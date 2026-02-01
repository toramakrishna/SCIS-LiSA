#!/usr/bin/env python3
"""
Update authors table with faculty information from faculty_data.json (SSOT).
Sets is_faculty flag and designation for all faculty members based on DBLP PID.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db_config import SessionLocal
from models.db_models import Author


def update_faculty_from_ssot():
    """Update authors table with faculty information from faculty_data.json"""
    
    # Load faculty data from SSOT
    faculty_file = Path(__file__).parent.parent / 'references' / 'faculty_data.json'
    
    with open(faculty_file, 'r') as f:
        faculty_data = json.load(f)
    
    session = SessionLocal()
    
    try:
        print("="*100)
        print("UPDATING AUTHORS TABLE FROM FACULTY_DATA.JSON (SSOT)")
        print("="*100)
        
        updated_count = 0
        not_found_count = 0
        not_found_list = []
        
        for faculty in faculty_data:
            faculty_name = faculty['name']
            dblp_pid = faculty.get('dblp_pid')
            designation = faculty.get('designation', '')
            email = faculty.get('email', '')
            
            if not dblp_pid:
                print(f"⚠️  No DBLP PID for {faculty_name}, skipping")
                continue
            
            # Find author by dblp_pid
            author = session.query(Author).filter(Author.dblp_pid == dblp_pid).first()
            
            if author:
                # Update faculty information
                author.is_faculty = True
                author.designation = designation
                
                # Update email if provided and not already set
                if email and not author.email:
                    author.email = email
                
                session.commit()
                
                pubs = author.total_publications or 0
                print(f"✓ Updated {author.name:<40} | {designation:<25} | Pubs: {pubs:>3} | PID: {dblp_pid}")
                updated_count += 1
            else:
                not_found_list.append((faculty_name, dblp_pid, designation))
                not_found_count += 1
        
        print(f"\n{'='*100}")
        print(f"UPDATE SUMMARY:")
        print(f"  Total faculty in SSOT (faculty_data.json): {len(faculty_data)}")
        print(f"  Authors updated in database: {updated_count}")
        print(f"  Not found in database: {not_found_count}")
        print(f"  (Not found = faculty whose publications haven't been ingested yet)")
        print("="*100)
        
        if not_found_list:
            print(f"\nFaculty NOT FOUND in database (publications not yet ingested):")
            print('-'*100)
            for name, pid, designation in sorted(not_found_list):
                print(f"  ✗ {name:<45} | PID: {pid:<15} | {designation}")
        
        # Show updated faculty list
        print(f"\n{'='*100}")
        print(f"ALL FACULTY IN AUTHORS TABLE:")
        print('-'*100)
        print(f"{'Rank':<6} {'Name':<40} {'Designation':<25} {'Pubs':>5} {'DBLP PID':<15}")
        print('-'*100)
        
        faculty_authors = session.query(Author).filter(
            Author.is_faculty == True
        ).order_by(Author.total_publications.desc()).all()
        
        for idx, author in enumerate(faculty_authors, 1):
            pubs = author.total_publications or 0
            desig = author.designation or 'N/A'
            print(f"{idx:<6} {author.name:<40} {desig:<25} {pubs:>5} {author.dblp_pid:<15}")
        
        print(f"\n{'='*100}")
        print(f"FINAL STATISTICS:")
        print(f"  Total faculty marked in database: {len(faculty_authors)}")
        print(f"  Total publications by faculty: {sum(a.total_publications or 0 for a in faculty_authors)}")
        print(f"  Average publications per faculty: {sum(a.total_publications or 0 for a in faculty_authors) / len(faculty_authors):.1f}")
        print("="*100)
        
        return updated_count, not_found_count
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    update_faculty_from_ssot()
