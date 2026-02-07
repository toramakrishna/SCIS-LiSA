#!/usr/bin/env python3
"""
Extract IRINS profile IDs and photos from HTML and add to faculty_data.json
"""
import json
import re
import os
import urllib.request
from bs4 import BeautifulSoup

# Create images directory if it doesn't exist
os.makedirs('../../dataset/images/faculty', exist_ok=True)

# Read HTML file
with open('references/scis_irins_faculty_details.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Extract faculty data from HTML
faculty_html_data = []
for item in soup.find_all('div', class_='cbp-item'):
    h3 = item.find('h3')
    designation_span = item.find('span', class_='color-lightYellow')
    profile_link = item.find('a', href=re.compile(r'profile/\d+'))
    img_tag = item.find('img', class_='rounded-x')
    
    if h3 and designation_span and profile_link:
        name = h3.text.strip()
        designation = designation_span.text.strip()
        profile_url = profile_link['href']
        profile_id = profile_url.split('/')[-1]
        
        # Extract photo URL
        photo_url = None
        local_photo_path = None
        if img_tag and 'src' in img_tag.attrs:
            photo_url = img_tag['src']
            # Extract filename from URL
            if 'profile_images' in photo_url:
                filename = photo_url.split('/')[-1]
                local_photo_path = f'dataset/images/faculty/{filename}'
        
        faculty_html_data.append({
            'name': name,
            'designation': designation,
            'irins_profile': profile_id,
            'irins_url': profile_url,
            'irins_photo_url': photo_url,
            'local_photo_path': local_photo_path
        })

print(f"Found {len(faculty_html_data)} faculty in HTML")
print("\nFaculty from HTML:")
for f in faculty_html_data:
    print(f"  {f['name']} - Profile: {f['irins_profile']} - Photo: {f['irins_photo_url']}")

# Read existing JSON file
with open('references/faculty_data.json', 'r', encoding='utf-8') as f:
    faculty_json = json.load(f)

print(f"\nFound {len(faculty_json)} faculty in JSON")

# Manual name mappings for difficult matches
# HTML name -> JSON name
MANUAL_NAME_MAPPINGS = {
    'Prof Girija Panati N': 'Girija P.N.',
    'Dr Nagender Suryadevara': 'Nagender Kumar S.',
    'Dr Naga Mani M': 'Nagamani M.',
    'Dr Saifullah M.A': 'Saifulla Md. Abdul',
}

# Name normalization function
def normalize_name(name):
    """Normalize name for matching"""
    # Remove titles
    name = re.sub(r'^(Prof|Dr|Mr|Ms|Mrs)\.?\s+', '', name, flags=re.IGNORECASE)
    # Remove extra spaces
    name = ' '.join(name.split())
    # Convert to lowercase for comparison
    return name.lower().strip()

def are_names_similar(name1, name2):
    """Check if two names are similar"""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    # Direct match
    if norm1 == norm2:
        return True
    
    # Check if one is contained in the other
    if norm1 in norm2 or norm2 in norm1:
        return True
    
    # Split into parts and check overlap
    parts1 = set(norm1.split())
    parts2 = set(norm2.split())
    
    # Check if they share significant parts (at least 2 parts or >60% overlap)
    common = parts1 & parts2
    if len(common) >= 2:
        return True
    
    # Check percentage overlap
    if len(parts1) > 0 and len(parts2) > 0:
        overlap = len(common) / min(len(parts1), len(parts2))
        if overlap >= 0.6:
            return True
    
    return False

# Match and update
matched = 0
unmatched_html = []
unmatched_json = []
downloaded_photos = 0
failed_downloads = []

for html_fac in faculty_html_data:
    html_name = html_fac['name']
    found = False
    
    for json_fac in faculty_json:
        json_name = json_fac['name']
        
        # First check manual mappings
        is_match = False
        if html_name in MANUAL_NAME_MAPPINGS:
            is_match = (json_name == MANUAL_NAME_MAPPINGS[html_name])
            if is_match:
                print(f"\n✓ Manual mapping: '{html_name}' → '{json_name}'")
        else:
            # Use similarity matching
            is_match = are_names_similar(html_name, json_name)
        
        if is_match:
            # Add IRINS profile info
            json_fac['irins_profile'] = html_fac['irins_profile']
            json_fac['irins_url'] = html_fac['irins_url']
            
            # Add photo information
            if html_fac['irins_photo_url']:
                json_fac['irins_photo_url'] = html_fac['irins_photo_url']
                
                # Download photo
                if html_fac['local_photo_path']:
                    local_path = os.path.join('../..', html_fac['local_photo_path'])
                    try:
                        if html_name not in MANUAL_NAME_MAPPINGS:
                            print(f"\n✓ Matched: '{html_name}' → '{json_name}'")
                        print(f"  IRINS Profile: {html_fac['irins_profile']}")
                        print(f"  Downloading photo: {html_fac['irins_photo_url']}")
                        
                        urllib.request.urlretrieve(html_fac['irins_photo_url'], local_path)
                        json_fac['photo_path'] = html_fac['local_photo_path']
                        print(f"  ✓ Photo saved to: {html_fac['local_photo_path']}")
                        downloaded_photos += 1
                    except Exception as e:
                        print(f"  ✗ Failed to download photo: {e}")
                        failed_downloads.append((html_name, str(e)))
            else:
                if html_name not in MANUAL_NAME_MAPPINGS:
                    print(f"\n✓ Matched: '{html_name}' → '{json_name}'")
                print(f"  IRINS Profile: {html_fac['irins_profile']}")
                print(f"  No profile photo available")
            
            matched += 1
            found = True
            break
    
    if not found:
        unmatched_html.append(html_name)

# Check for JSON entries without IRINS profile
for json_fac in faculty_json:
    if 'irins_profile' not in json_fac:
        unmatched_json.append(json_fac['name'])

# Write updated JSON
with open('references/faculty_data.json', 'w', encoding='utf-8') as f:
    json.dump(faculty_json, f, indent=2, ensure_ascii=False)

print(f"\n\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total HTML entries: {len(faculty_html_data)}")
print(f"Total JSON entries: {len(faculty_json)}")
print(f"Matched: {matched}")
print(f"Photos downloaded: {downloaded_photos}")
print(f"Unmatched HTML: {len(unmatched_html)}")
print(f"Unmatched JSON: {len(unmatched_json)}")
print(f"Failed photo downloads: {len(failed_downloads)}")

if failed_downloads:
    print(f"\nFailed photo downloads:")
    for name, error in failed_downloads:
        print(f"  - {name}: {error}")

if unmatched_html:
    print(f"\nUnmatched HTML entries:")
    for name in unmatched_html:
        print(f"  - {name}")

if unmatched_json:
    print(f"\nUnmatched JSON entries:")
    for name in unmatched_json:
        print(f"  - {name}")

print(f"\n✓ Updated faculty_data.json with IRINS profile IDs and photos")
