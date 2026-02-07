#!/usr/bin/env python3
"""
Manually add remaining IRINS profile IDs that couldn't be auto-matched
"""
import json

# Read the JSON file
with open('references/faculty_data.json', 'r', encoding='utf-8') as f:
    faculty_json = json.load(f)

# Manual mappings based on careful name analysis
manual_mappings = {
    'Girija P.N.': {'irins_profile': '71067', 'irins_url': 'https://uohyd.irins.org/profile/71067'},
    'Nagender Kumar S.': {'irins_profile': '71041', 'irins_url': 'https://uohyd.irins.org/profile/71041'},
    'Nagamani M.': {'irins_profile': '112626', 'irins_url': 'https://uohyd.irins.org/profile/112626'},
    'Saifulla Md. Abdul': {'irins_profile': '112629', 'irins_url': 'https://uohyd.irins.org/profile/112629'},
}

# Apply manual mappings
for faculty in faculty_json:
    name = faculty['name']
    if name in manual_mappings and 'irins_profile' not in faculty:
        faculty['irins_profile'] = manual_mappings[name]['irins_profile']
        faculty['irins_url'] = manual_mappings[name]['irins_url']
        print(f"✓ Manually added IRINS profile for: {name} → {manual_mappings[name]['irins_profile']}")

# Note: Some faculty may not have IRINS profiles (new hires, etc.)
faculty_without_irins = []
for faculty in faculty_json:
    if 'irins_profile' not in faculty:
        faculty_without_irins.append(faculty['name'])

# Write updated JSON
with open('references/faculty_data.json', 'w', encoding='utf-8') as f:
    json.dump(faculty_json, f, indent=2, ensure_ascii=False)

print(f"\n✓ Updated faculty_data.json with manual IRINS profile mappings")

if faculty_without_irins:
    print(f"\nFaculty without IRINS profiles (may be newer faculty or not in IRINS system):")
    for name in faculty_without_irins:
        print(f"  - {name}")
