#!/usr/bin/env python3
"""
Generate complete faculty publication report using source_pids
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from models.db_models import Publication
from config.db_config import SessionLocal
from services.ingestion_service import DatabaseIngestionService
from sqlalchemy import text

def main():
    db = SessionLocal()
    service = DatabaseIngestionService(db)
    
    # Load faculty mapping
    faculty_map_full = service.load_faculty_mapping('references/dblp/faculty_dblp_matched.json')
    faculty_map = faculty_map_full['by_name']  # Use the by_name mapping for iteration
    
    print("\n" + "=" * 100)
    print(" " * 30 + "COMPLETE FACULTY PUBLICATION REPORT")
    print("=" * 100)
    print(f"{'Rank':<6}{'Faculty Name':<35}{'Publications':<15}{'Collaborations':<18}{'DBLP PID':<20}")
    print("-" * 100)
    
    # Get all faculty data
    faculty_data = []
    for name, info in faculty_map.items():
        pid = info.get('dblp_pid')
        
        # Query publications directly using source_pids array
        # This gives us the accurate count of publications for this faculty PID
        pub_count = db.execute(text("""
            SELECT COUNT(*) 
            FROM publications 
            WHERE :pid = ANY(source_pids)
        """), {'pid': pid}).scalar() or 0
        
        # Count co-authored papers (publications with multiple faculty PIDs)
        collab_count = db.execute(text("""
            SELECT COUNT(*) 
            FROM publications 
            WHERE :pid = ANY(source_pids) 
            AND array_length(source_pids, 1) > 1
        """), {'pid': pid}).scalar() or 0
        
        faculty_data.append({
            'name': name,
            'publications': pub_count,
            'collaborations': collab_count,
            'pid': pid or 'N/A'
        })
    
    # Sort by publications descending
    faculty_data.sort(key=lambda x: x['publications'], reverse=True)
    
    # Print all faculty
    for rank, fac in enumerate(faculty_data, 1):
        print(f"{rank:<6}{fac['name']:<35}{fac['publications']:<15}{fac['collaborations']:<18}{fac['pid']:<20}")
    
    print("-" * 100)
    print(f"\nSummary Statistics:")
    print(f"  Total Faculty: {len(faculty_data)}")
    print(f"  Faculty with Publications: {sum(1 for f in faculty_data if f['publications'] > 0)}")
    print(f"  Faculty with 0 Publications: {sum(1 for f in faculty_data if f['publications'] == 0)}")
    print(f"  Total Publications: {sum(f['publications'] for f in faculty_data)}")
    print(f"  Total Co-authored Papers: {sum(f['collaborations'] for f in faculty_data)}")
    print(f"  Average Publications per Faculty: {sum(f['publications'] for f in faculty_data) / len(faculty_data):.1f}")
    print(f"  Average Publications (active only): {sum(f['publications'] for f in faculty_data if f['publications'] > 0) / sum(1 for f in faculty_data if f['publications'] > 0):.1f}")
    print("=" * 100)
    
    db.close()

if __name__ == "__main__":
    main()
