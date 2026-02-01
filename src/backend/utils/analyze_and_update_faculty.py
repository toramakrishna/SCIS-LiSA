#!/usr/bin/env python3
"""
Analyze faculty coverage in the dataset and update authors table.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db_config import SessionLocal
from models.db_models import Author


def analyze_faculty_coverage():
    """Analyze which faculty have BibTeX files in the dataset"""
    
    # Load faculty data
    faculty_file = Path(__file__).parent.parent / 'references' / 'dblp' / 'faculty_dblp_matched.json'
    with open(faculty_file) as f:
        faculty_data = json.load(f)
    
    # Get list of BibTeX files
    dataset_dir = Path(__file__).parent.parent.parent / 'dataset' / 'dblp'
    bib_files = list(dataset_dir.glob('*.bib'))
    
    print('='*100)
    print('FACULTY COVERAGE ANALYSIS')
    print('='*100)
    
    found_in_dataset = []
    not_in_dataset = []
    
    for faculty in faculty_data:
        pid = faculty.get('dblp_pid', '')
        name = faculty['faculty_name']
        
        # Normalize PID for comparison (e.g., "04/3517" -> "04_3517")
        pid_normalized = pid.replace('/', '_')
        
        # Check if any bib file matches this PID
        has_bib = any(pid_normalized in f.stem for f in bib_files)
        
        if has_bib:
            found_in_dataset.append((name, pid, faculty.get('designation', '')))
        else:
            not_in_dataset.append((name, pid, faculty.get('designation', '')))
    
    print(f'\nFaculty WITH BibTeX files in dataset ({len(found_in_dataset)}):')
    print('-'*100)
    for name, pid, designation in sorted(found_in_dataset):
        print(f'  ✓ {name:<45} | PID: {pid:<15} | {designation}')
    
    print(f'\nFaculty WITHOUT BibTeX files in dataset ({len(not_in_dataset)}):')
    print('-'*100)
    for name, pid, designation in sorted(not_in_dataset):
        print(f'  ✗ {name:<45} | PID: {pid:<15} | {designation}')
    
    print('\n' + '='*100)
    print('SUMMARY:')
    print(f'  Total faculty: {len(faculty_data)}')
    print(f'  With BibTeX data: {len(found_in_dataset)}')
    print(f'  Missing BibTeX data: {len(not_in_dataset)}')
    print('='*100)
    
    return found_in_dataset, not_in_dataset


def update_faculty_in_database():
    """Update authors table with faculty information based on DBLP PIDs"""
    
    # Load faculty DBLP matched data
    faculty_file = Path(__file__).parent.parent / 'references' / 'dblp' / 'faculty_dblp_matched.json'
    
    with open(faculty_file, 'r') as f:
        faculty_data = json.load(f)
    
    session = SessionLocal()
    
    try:
        print('\n' + '='*100)
        print("UPDATING AUTHORS TABLE WITH FACULTY INFORMATION")
        print('='*100)
        
        updated_count = 0
        not_found_count = 0
        not_found_list = []
        
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
                
                # Update designation if not "Unknown"
                if designation and designation != 'Unknown':
                    author.designation = designation
                
                # Update email if provided and not already set
                if email and not author.email:
                    author.email = email
                
                session.commit()
                
                print(f"✓ Updated {author.name:<40} | PID: {dblp_pid:<15} | {designation}")
                updated_count += 1
            else:
                not_found_list.append((faculty_name, dblp_pid, designation))
                not_found_count += 1
        
        print('\n' + '='*100)
        print("UPDATE SUMMARY:")
        print(f"  Total faculty in reference: {len(faculty_data)}")
        print(f"  Authors updated: {updated_count}")
        print(f"  Not found in DB: {not_found_count}")
        print("  (Not found = faculty whose publications are not in the dataset)")
        print('='*100)
        
        if not_found_list:
            print(f"\nFaculty NOT FOUND in database (no BibTeX files ingested):")
            print('-'*100)
            for name, pid, designation in not_found_list:
                print(f"  ✗ {name:<40} | PID: {pid:<15} | {designation}")
        
        # Show updated faculty list
        print('\n' + '='*100)
        print("FACULTY IN AUTHORS TABLE (UPDATED):")
        print('-'*100)
        
        faculty_authors = session.query(Author).filter(
            Author.is_faculty == True
        ).order_by(Author.total_publications.desc()).all()
        
        for author in faculty_authors:
            pubs = author.total_publications or 0
            desig = author.designation or 'N/A'
            print(f"  {author.name:<40} | {desig:<25} | Pubs: {pubs:>4} | PID: {author.dblp_pid}")
        
        print('\n' + '='*100)
        print("FINAL STATISTICS:")
        print(f"  Total faculty marked in database: {len(faculty_authors)}")
        print(f"  Total publications by faculty: {sum(a.total_publications or 0 for a in faculty_authors)}")
        print('='*100)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    # First analyze coverage
    analyze_faculty_coverage()
    
    # Then update database
    update_faculty_in_database()
