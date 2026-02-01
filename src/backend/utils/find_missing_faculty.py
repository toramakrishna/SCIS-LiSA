#!/usr/bin/env python3
"""Find missing faculty members from the database"""

import json
from pathlib import Path

# Load faculty data
faculty_json_path = Path(__file__).parent.parent / 'references' / 'faculty_data.json'
with open(faculty_json_path, 'r') as f:
    faculty_data = json.load(f)

# Extract all PIDs from faculty_data.json
all_pids = {}
for faculty in faculty_data:
    if faculty.get('dblp_pid'):
        all_pids[faculty['dblp_pid']] = faculty['name']

print(f'Total faculty in faculty_data.json: {len(all_pids)}')

# Faculty PIDs found in database
found_pids = {
    '01/1744-1', '138/0168', '16/5380', '97/3869', '95/6184', '263/4582-1',
    '73/4368', '06/10134', '50/1424', '338/9977', '91/1525', '07/5281-1',
    '327/2466', '74/5678', '77/10593', '21/10736', '94/4013', '55/8654',
    '83/9943', '10/2362', '23/2953', '31/566', '31/9532', '309/7711',
    '98/6017', '09/1571', '63/2890', '04/3517', '51/1349', '66/8044',
    '98/255', '05/2858', '50/971'
}

print(f'Faculty found in database: {len(found_pids)}')

# Find missing faculty
missing_pids = set(all_pids.keys()) - found_pids
print(f'\nMissing faculty PIDs ({len(missing_pids)}): {missing_pids}')

# Show details of missing faculty
for pid in missing_pids:
    for faculty in faculty_data:
        if faculty.get('dblp_pid') == pid:
            print(f'\nMissing faculty:')
            print(f'  Name: {faculty["name"]}')
            print(f'  PID: {faculty["dblp_pid"]}')
            print(f'  DBLP Names: {faculty.get("dblp_names", [])}')
            print(f'  Designation: {faculty.get("designation")}')
