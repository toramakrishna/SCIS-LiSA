#!/usr/bin/env python3
"""
Verify publication counts by comparing database with DBLP website
Fetches counts directly from DBLP and compares with our database
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
import time
from bs4 import BeautifulSoup
from sqlalchemy import text
from config.db_config import SessionLocal
from services.ingestion_service import DatabaseIngestionService


def get_dblp_publication_count(pid: str) -> int:
    """
    Fetch publication count from DBLP website for a given PID
    
    Args:
        pid: DBLP PID (e.g., '50/971')
        
    Returns:
        Number of publications from DBLP
    """
    url = f"https://dblp.org/pid/{pid}.html"
    
    try:
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # DBLP shows publications in <li class="entry"> elements
        # Count all publication entries
        entries = soup.find_all('li', class_='entry')
        
        # Alternative: Look for the publication count in the header
        # DBLP sometimes shows "X publications" in the header
        header = soup.find('header')
        if header:
            # Try to find count in header text
            header_text = header.get_text()
            # Look for patterns like "123 publications"
            import re
            match = re.search(r'(\d+)\s+(?:publications?|entries)', header_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Count entry elements as fallback
        return len(entries)
        
    except requests.RequestException as e:
        print(f"  Error fetching DBLP data for PID {pid}: {e}")
        return -1
    except Exception as e:
        print(f"  Error parsing DBLP data for PID {pid}: {e}")
        return -1


def main():
    db = SessionLocal()
    service = DatabaseIngestionService(db)
    
    # Load faculty mapping from SSOT
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    faculty_json = os.path.join(current_dir, 'references', 'faculty_data.json')
    faculty_map_full = service.load_faculty_mapping(faculty_json)
    faculty_map = faculty_map_full['by_pid']
    
    print("\n" + "=" * 120)
    print(" " * 40 + "DBLP PUBLICATION COUNT VERIFICATION")
    print("=" * 120)
    print(f"{'Faculty Name':<35}{'DBLP PID':<20}{'DB Count':<12}{'DBLP Count':<12}{'Match':<10}{'Difference':<15}")
    print("-" * 120)
    
    verification_results = []
    total_matches = 0
    total_mismatches = 0
    
    for pid, info in sorted(faculty_map.items(), key=lambda x: x[1].get('faculty_name', '')):
        name = info.get('faculty_name')
        
        # Get count from our database
        db_count = db.execute(text("""
            SELECT COUNT(*) 
            FROM publications 
            WHERE :pid = ANY(source_pids)
        """), {'pid': pid}).scalar() or 0
        
        # Get count from DBLP website
        print(f"{name:<35}{pid:<20}{db_count:<12}", end='', flush=True)
        
        dblp_count = get_dblp_publication_count(pid)
        
        if dblp_count == -1:
            print(f"{'ERROR':<12}{'N/A':<10}{'N/A':<15}")
            verification_results.append({
                'name': name,
                'pid': pid,
                'db_count': db_count,
                'dblp_count': 'ERROR',
                'match': False,
                'difference': 'N/A'
            })
        else:
            match = db_count == dblp_count
            difference = db_count - dblp_count
            match_status = '✓ YES' if match else '✗ NO'
            
            if match:
                total_matches += 1
            else:
                total_mismatches += 1
            
            print(f"{dblp_count:<12}{match_status:<10}{difference:+d}")
            
            verification_results.append({
                'name': name,
                'pid': pid,
                'db_count': db_count,
                'dblp_count': dblp_count,
                'match': match,
                'difference': difference
            })
        
        # Be nice to DBLP servers - add a small delay
        time.sleep(0.5)
    
    print("-" * 120)
    print("\nSummary:")
    print(f"  Total Faculty: {len(faculty_map)}")
    print(f"  Exact Matches: {total_matches} ({total_matches/len(faculty_map)*100:.1f}%)")
    print(f"  Mismatches: {total_mismatches} ({total_mismatches/len(faculty_map)*100:.1f}%)")
    
    # Show detailed analysis of mismatches
    if total_mismatches > 0:
        print("\nDetailed Mismatch Analysis:")
        print("-" * 120)
        mismatches = [r for r in verification_results if not r['match'] and r['dblp_count'] != 'ERROR']
        
        # Group by type of difference
        db_higher = [r for r in mismatches if r['difference'] > 0]
        dblp_higher = [r for r in mismatches if r['difference'] < 0]
        
        if db_higher:
            print(f"\nDatabase has MORE publications than DBLP ({len(db_higher)} faculty):")
            for r in sorted(db_higher, key=lambda x: x['difference'], reverse=True):
                print(f"  {r['name']:<35} DB: {r['db_count']}, DBLP: {r['dblp_count']} (DB +{r['difference']})")
        
        if dblp_higher:
            print(f"\nDBLP has MORE publications than Database ({len(dblp_higher)} faculty):")
            for r in sorted(dblp_higher, key=lambda x: x['difference']):
                print(f"  {r['name']:<35} DB: {r['db_count']}, DBLP: {r['dblp_count']} (DBLP +{abs(r['difference'])})")
        
        print("\nPossible reasons for mismatches:")
        print("  • Our deduplication removed legitimate variations (arXiv preprints, different versions)")
        print("  • DBLP may include/exclude certain publication types")
        print("  • DBLP data may have been updated since we downloaded .bib files")
        print("  • Co-authored papers between faculty might be counted differently")
    
    print("=" * 120)
    
    db.close()


if __name__ == "__main__":
    main()
