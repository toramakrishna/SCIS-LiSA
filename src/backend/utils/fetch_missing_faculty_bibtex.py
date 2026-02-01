#!/usr/bin/env python3
"""
Fetch missing DBLP BibTeX files and ingest all faculty publications.
Downloads BibTeX files for faculty PIDs that are missing from the dataset.
"""

import json
import requests
from pathlib import Path
import time
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def fetch_dblp_bibtex(dblp_pid, output_dir):
    """
    Fetch BibTeX file from DBLP for a given PID
    
    Args:
        dblp_pid: DBLP PID (e.g., '09/1571')
        output_dir: Directory to save the BibTeX file
    
    Returns:
        Path to saved file or None if failed
    """
    # Normalize PID for filename
    pid_normalized = dblp_pid.replace('/', '_')
    output_file = output_dir / f"{pid_normalized}.bib"
    
    # Check if file already exists
    if output_file.exists():
        print(f"  ✓ Already exists: {output_file.name}")
        return output_file
    
    # DBLP BibTeX URL
    url = f"https://dblp.org/pid/{dblp_pid}.bib"
    
    try:
        print(f"  Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  ✓ Saved: {output_file.name} ({len(response.text)} bytes)")
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to download {dblp_pid}: {e}")
        return None


def fetch_missing_faculty_data():
    """Fetch BibTeX files for all faculty from faculty_data.json"""
    
    # Load faculty data
    faculty_file = Path(__file__).parent.parent / 'references' / 'faculty_data.json'
    with open(faculty_file, 'r') as f:
        faculty_data = json.load(f)
    
    # Dataset directory
    dataset_dir = Path(__file__).parent.parent.parent / 'dataset' / 'dblp'
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Get existing BibTeX files
    existing_files = list(dataset_dir.glob('*.bib'))
    existing_pids = {f.stem.replace('_', '/').replace('-', '/') for f in existing_files}
    
    print("="*100)
    print("FETCHING MISSING DBLP BIBTEX FILES")
    print("="*100)
    print(f"\nFaculty data source: {faculty_file}")
    print(f"Dataset directory: {dataset_dir}")
    print(f"Existing BibTeX files: {len(existing_files)}")
    print(f"\nTotal faculty: {len(faculty_data)}")
    
    # Track downloads
    to_download = []
    already_exist = []
    failed = []
    
    # Check which faculty need downloads
    for faculty in faculty_data:
        name = faculty['name']
        pid = faculty.get('dblp_pid')
        
        if not pid:
            print(f"\n⚠️  {name}: No DBLP PID")
            continue
        
        # Normalize PID for comparison
        pid_normalized = pid.replace('/', '_')
        
        # Check if any bib file matches this PID
        has_bib = any(pid_normalized in f.stem for f in existing_files)
        
        if has_bib:
            already_exist.append((name, pid))
        else:
            to_download.append((name, pid))
    
    print(f"\n{'='*100}")
    print(f"STATUS:")
    print(f"  Already have BibTeX: {len(already_exist)}")
    print(f"  Need to download: {len(to_download)}")
    print(f"{'='*100}")
    
    if not to_download:
        print("\n✓ All faculty BibTeX files are already present!")
        return True
    
    # Download missing files
    print(f"\nDOWNLOADING {len(to_download)} MISSING BIBTEX FILES:")
    print("-"*100)
    
    for name, pid in to_download:
        print(f"\n{name} (PID: {pid}):")
        result = fetch_dblp_bibtex(pid, dataset_dir)
        
        if result:
            print(f"  ✓ Success")
        else:
            failed.append((name, pid))
            print(f"  ✗ Failed")
        
        # Be respectful to DBLP servers
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*100}")
    print(f"DOWNLOAD SUMMARY:")
    print(f"  Attempted: {len(to_download)}")
    print(f"  Successful: {len(to_download) - len(failed)}")
    print(f"  Failed: {len(failed)}")
    
    if failed:
        print(f"\nFailed downloads:")
        for name, pid in failed:
            print(f"  ✗ {name} (PID: {pid})")
    
    print(f"{'='*100}")
    
    return len(failed) == 0


if __name__ == '__main__':
    success = fetch_missing_faculty_data()
    
    if success:
        print("\n✓ All faculty BibTeX files are ready for ingestion!")
        print("\nNext step: Run the ingestion service")
        print("  cd /Users/othadem/go/src/github.com/drtoramakrishna/SCISLiSA/src/backend")
        print("  python3 services/ingestion_service.py")
    else:
        print("\n⚠️  Some downloads failed. Check the errors above.")
        sys.exit(1)
