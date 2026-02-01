#!/usr/bin/env python3
"""
Merge DBLP data from faculty_dblp_matched.json into faculty_data.json
Makes faculty_data.json the single source of truth with complete DBLP information.
"""

import json
from pathlib import Path

def normalize_name(name):
    """Normalize name for matching"""
    return name.strip().lower()

def merge_dblp_data():
    """Merge DBLP names and URLs into faculty_data.json"""
    
    # Load both JSON files
    base_dir = Path(__file__).parent
    faculty_data_path = base_dir / 'faculty_data.json'
    dblp_matched_path = base_dir / 'dblp' / 'faculty_dblp_matched.json'
    
    with open(faculty_data_path, 'r') as f:
        faculty_data = json.load(f)
    
    with open(dblp_matched_path, 'r') as f:
        dblp_matched = json.load(f)
    
    # Create lookup dict by normalized name
    dblp_lookup = {}
    for entry in dblp_matched:
        key = normalize_name(entry['faculty_name'])
        if key not in dblp_lookup:
            dblp_lookup[key] = []
        dblp_lookup[key].append(entry)
    
    # Update faculty_data with DBLP information
    updated_count = 0
    
    for faculty in faculty_data:
        faculty_name = faculty['name']
        normalized_name = normalize_name(faculty_name)
        
        # Find matching DBLP entry
        if normalized_name in dblp_lookup:
            # Take the first match (they should all have the same DBLP data)
            dblp_entry = dblp_lookup[normalized_name][0]
            
            # Extract all DBLP names from all_matches
            dblp_names = []
            dblp_pids = set()
            
            if dblp_entry.get('all_matches'):
                for match in dblp_entry['all_matches']:
                    if match.get('dblp_name'):
                        dblp_names.append(match['dblp_name'])
                    if match.get('dblp_pid'):
                        dblp_pids.add(match['dblp_pid'])
            
            # If no all_matches, use the primary dblp_name and dblp_pid
            if not dblp_names and dblp_entry.get('dblp_name'):
                dblp_names.append(dblp_entry['dblp_name'])
            
            if not dblp_pids and dblp_entry.get('dblp_pid'):
                dblp_pids.add(dblp_entry['dblp_pid'])
            
            # Construct DBLP URLs from PIDs
            dblp_urls = [f"https://dblp.org/pid/{pid}.html" for pid in sorted(dblp_pids)]
            
            # Update faculty record
            faculty['dblp_names'] = dblp_names if dblp_names else [""]
            faculty['dblp_urls'] = dblp_urls if dblp_urls else [""]
            faculty['dblp_pid'] = dblp_entry.get('dblp_pid', '')
            faculty['dblp_matched'] = dblp_entry.get('dblp_matched', False)
            
            # Update designation if it's more specific in dblp_matched
            if dblp_entry.get('designation') and dblp_entry['designation'] != 'Unknown':
                faculty['designation'] = dblp_entry['designation']
            
            updated_count += 1
            print(f"✓ Updated {faculty_name}: {len(dblp_names)} names, {len(dblp_urls)} URLs")
        else:
            # No DBLP match found
            if 'dblp_names' not in faculty:
                faculty['dblp_names'] = [""]
            if 'dblp_urls' not in faculty:
                faculty['dblp_urls'] = [""]
            if 'dblp_pid' not in faculty:
                faculty['dblp_pid'] = ''
            if 'dblp_matched' not in faculty:
                faculty['dblp_matched'] = False
            
            print(f"⚠ No DBLP match for {faculty_name}")
    
    # Write updated data back to faculty_data.json
    with open(faculty_data_path, 'w') as f:
        json.dump(faculty_data, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Successfully updated {updated_count}/{len(faculty_data)} faculty records")
    print(f"Output: {faculty_data_path}")
    print(f"{'='*80}")

if __name__ == '__main__':
    merge_dblp_data()
