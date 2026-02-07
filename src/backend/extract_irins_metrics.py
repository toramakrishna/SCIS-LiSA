"""
Script to extract Scopus Author ID and h-index from IRINS profile pages
and update faculty_data.json
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

def extract_scopus_and_hindex(irins_url):
    """
    Extract Scopus Author ID and h-index from IRINS profile page
    
    Args:
        irins_url: URL of the IRINS profile page
        
    Returns:
        tuple: (scopus_author_id, h_index)
    """
    try:
        print(f"  Fetching: {irins_url}")
        response = requests.get(irins_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract Scopus Author ID
        scopus_author_id = None
        scopus_link = soup.find('a', href=lambda x: x and 'scopus.com/authid/detail.url?authorId=' in x)
        if scopus_link:
            href = scopus_link['href']
            # Extract authorId from URL
            if 'authorId=' in href:
                scopus_author_id = href.split('authorId=')[1].split('&')[0]
                print(f"  ✓ Found Scopus Author ID: {scopus_author_id}")
        else:
            print(f"  ✗ Scopus Author ID not found")
        
        # Extract h-index
        h_index = None
        # Look for h-index image followed by counter span
        h_index_img = soup.find('img', src=lambda x: x and 'h_index.png' in x)
        if h_index_img:
            # Find the counter span that follows the h-index image
            parent = h_index_img.parent
            if parent:
                counter_span = parent.find('span', class_='counter')
                if counter_span:
                    try:
                        h_index = int(counter_span.text.strip())
                        print(f"  ✓ Found h-index: {h_index}")
                    except ValueError:
                        print(f"  ✗ Could not parse h-index value: {counter_span.text}")
        
        if not h_index:
            print(f"  ✗ h-index not found")
        
        return scopus_author_id, h_index
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {irins_url}: {e}")
        return None, None
    except Exception as e:
        print(f"  ✗ Error parsing {irins_url}: {e}")
        return None, None


def main():
    # Load faculty data
    json_path = Path(__file__).parent / 'references' / 'faculty_data.json'
    
    print(f"Loading faculty data from: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        faculty_data = json.load(f)
    
    print(f"Found {len(faculty_data)} faculty members\n")
    
    # Track statistics
    total_with_irins = 0
    scopus_found = 0
    hindex_found = 0
    
    # Process each faculty member
    for i, faculty in enumerate(faculty_data, 1):
        name = faculty['name']
        irins_url = faculty.get('irins_url')
        
        if not irins_url:
            print(f"{i}. {name}: No IRINS URL available")
            continue
        
        total_with_irins += 1
        print(f"{i}. {name}")
        
        # Extract data
        scopus_author_id, h_index = extract_scopus_and_hindex(irins_url)
        
        # Update faculty data
        if scopus_author_id:
            faculty['scopus_author_id'] = scopus_author_id
            scopus_found += 1
        
        if h_index is not None:
            faculty['h_index'] = h_index
            hindex_found += 1
        
        print()  # Blank line between faculty
        
        # Be respectful with requests - add delay
        time.sleep(1)
    
    # Save updated data
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total faculty: {len(faculty_data)}")
    print(f"Faculty with IRINS profiles: {total_with_irins}")
    print(f"Scopus Author IDs found: {scopus_found}")
    print(f"h-index values found: {hindex_found}")
    print("="*60)
    
    print(f"\nSaving updated data to: {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(faculty_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Faculty data updated successfully!")


if __name__ == '__main__':
    main()
