#!/usr/bin/env python3
"""
Update authors table with faculty information based on DBLP PIDs.
Sets is_faculty flag and designation for faculty members.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db_config import SessionLocal
from models.db_models import Author


def update_faculty_from_dblp_pid():
    """Update authors table with faculty information based on DBLP PIDs"""
    
    # Load faculty DBLP matched data
    faculty_file = Path(__file__).parent.parent / 'references' / 'dblp' / 'faculty_dblp_matched.json'
    
    with open(faculty_file, 'r') as f:
        faculty_data = json.load(f)
    
    session = SessionLocal()
    
    try:
        print("="*100)
        print("UPDATING AUTHORS TABLE WITH FACULTY INFORMATION")
        print("="*100)
        
        updated_count = 0
        not_found_count = 0
        
        for faculty in faculty_data:
            faculty_name = faculty['faculty_name']
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
                
                # Update email if not already set
                if email and not author.email:
                    author.email = email
                
                session.commit()
                
                print(f"✓ Updated {author.name:<40} | PID: {dblp_pid:<15} | {designation}")
                updated_count += 1
            else:
                print(f"❌ Not found: {faculty_name:<40} | PID: {dblp_pid}")
                not_found_count += 1
        
        print(f"\n{'='*100}")
        print(f"SUMMARY:")
        print(f"  Total faculty in reference: {len(faculty_data)}")
        print(f"  Authors updated: {updated_count}")
        print(f"  Not found in DB: {not_found_count}")
        print(f"{'='*100}")
        
        # Show updated faculty list
        print(f"\nFACULTY IN AUTHORS TABLE:")
        print("-"*100)
        
        faculty_authors = session.query(Author).filter(Author.is_faculty == True).order_by(Author.name).all()
        
        for author in faculty_authors:
            pubs = author.total_publications or 0
            print(f"  {author.name:<40} | {author.designation:<25} | Pubs: {pubs:>4} | PID: {author.dblp_pid}")
        
        print(f"\n{'='*100}")
        print(f"Total faculty marked in database: {len(faculty_authors)}")
        print(f"{'='*100}")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    update_faculty_from_dblp_pid()
