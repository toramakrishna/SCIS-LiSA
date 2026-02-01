"""
Faculty data extraction from HTML
Extracts faculty names and details from scis_uoh_faculty_details.html
"""
import re
from bs4 import BeautifulSoup
from typing import List, Dict
import json
import os


def extract_faculty_details(html_file_path: str) -> List[Dict[str, str]]:
    """
    Extract faculty details from the HTML file
    
    Args:
        html_file_path: Path to the HTML file
        
    Returns:
        List of dictionaries containing faculty details
    """
    with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    faculty_list = []
    
    # Find all faculty entries (they are in tr elements with class 'td_faculty')
    faculty_rows = soup.find_all('tr', class_='td_faculty')
    
    for row in faculty_rows:
        try:
            # Get the name and designation from the first td
            td_elements = row.find_all('td')
            if not td_elements:
                continue
            
            first_td = td_elements[0]
            name_tag = first_td.find('b')
            
            if not name_tag:
                continue
            
            full_text = name_tag.get_text(strip=True)
            
            # Extract name and designation using regex
            # Pattern: "Name (Designation)"
            match = re.match(r'(.+?)\s*\((.+?)\)', full_text)
            
            if match:
                name = match.group(1).strip()
                designation = match.group(2).strip()
            else:
                # If pattern doesn't match, use the whole text as name
                name = full_text.strip()
                designation = "Unknown"
            
            # Get email and phone from next row
            next_row = row.find_next_sibling('tr')
            email = ""
            phone = ""
            
            if next_row:
                tds = next_row.find_all('td')
                for td in tds:
                    # Find email
                    email_tag = td.find('font', color=lambda c: c and 'F14E23' in c)
                    if email_tag:
                        email = email_tag.get_text(strip=True)
                    
                    # Find phone
                    phone_match = re.search(r'Phone:\s*([0-9\-+]+)', td.get_text())
                    if phone_match:
                        phone = phone_match.group(1).strip()
            
            faculty_data = {
                'name': name,
                'designation': designation,
                'email': email,
                'phone': phone,
                'department': 'SCIS'
            }
            
            faculty_list.append(faculty_data)
            
        except Exception as e:
            print(f"Error processing row: {e}")
            continue
    
    return faculty_list


def save_faculty_data(faculty_list: List[Dict], output_file: str):
    """
    Save faculty data to JSON file
    
    Args:
        faculty_list: List of faculty dictionaries
        output_file: Path to output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(faculty_list, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(faculty_list)} faculty records to {output_file}")


if __name__ == "__main__":
    # Get the path to the HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, 'scis_uoh_faculty_details.html')
    output_file = os.path.join(current_dir, 'faculty_data.json')
    
    # Extract faculty details
    faculty_list = extract_faculty_details(html_file)
    
    # Print extracted data
    print(f"\nExtracted {len(faculty_list)} faculty members:\n")
    for i, faculty in enumerate(faculty_list, 1):
        print(f"{i}. {faculty['name']} ({faculty['designation']})")
        if faculty['email']:
            print(f"   Email: {faculty['email']}")
    
    # Save to JSON
    save_faculty_data(faculty_list, output_file)
