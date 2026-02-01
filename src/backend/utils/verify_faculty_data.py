"""
Faculty Data Verification Script
Cross-checks database records against source faculty data
"""
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db_config import SessionLocal
from models.db_models import Author
from sqlalchemy import and_

def normalize_name(name):
    """Normalize name for comparison"""
    if not name:
        return ""
    return ' '.join(name.lower().split()).replace('.', '').replace(',', '')

def main():
    # Load source data
    current_dir = Path(__file__).parent.parent
    faculty_json = current_dir / 'references' / 'dblp' / 'faculty_dblp_matched.json'
    
    with open(faculty_json, 'r') as f:
        source_faculty = json.load(f)
    
    # Filter to only matched faculty
    source_faculty = [f for f in source_faculty if f.get('dblp_matched')]
    
    # Get database data
    db = SessionLocal()
    db_faculty = db.query(Author).filter(Author.is_faculty == True).all()
    
    print("="*100)
    print("FACULTY DATA VERIFICATION REPORT")
    print("="*100)
    print(f"\nSource Faculty Count: {len(source_faculty)}")
    print(f"Database Faculty Count: {len(db_faculty)}")
    
    # Create mappings
    source_by_pid = {f['dblp_pid']: f for f in source_faculty}
    db_by_pid = {a.dblp_pid: a for a in db_faculty if a.dblp_pid}
    
    # Check for missing faculty
    source_pids = set(source_by_pid.keys())
    db_pids = set(db_by_pid.keys())
    
    missing_from_db = source_pids - db_pids
    extra_in_db = db_pids - source_pids
    
    if missing_from_db:
        print(f"\n⚠️  MISSING FROM DATABASE ({len(missing_from_db)}):")
        print("-"*100)
        for pid in sorted(missing_from_db):
            fac = source_by_pid[pid]
            print(f"  PID: {pid:<15} Name: {fac['faculty_name']:<30} Email: {fac['email']}")
    
    if extra_in_db:
        print(f"\n⚠️  EXTRA IN DATABASE ({len(extra_in_db)}):")
        print("-"*100)
        for pid in sorted(extra_in_db):
            author = db_by_pid[pid]
            print(f"  PID: {pid:<15} Name: {author.name:<30} Email: {author.email}")
    
    # Detailed comparison for matching PIDs
    matching_pids = source_pids & db_pids
    print(f"\n✓ MATCHED FACULTY ({len(matching_pids)}):")
    print("-"*100)
    
    mismatches = []
    for pid in sorted(matching_pids):
        source = source_by_pid[pid]
        db_author = db_by_pid[pid]
        
        issues = []
        
        # Check name match
        source_name_norm = normalize_name(source['faculty_name'])
        db_name_norm = normalize_name(db_author.name)
        if source_name_norm != db_name_norm:
            issues.append(f"NAME: '{source['faculty_name']}' vs '{db_author.name}'")
        
        # Check email
        if source['email'] != db_author.email:
            issues.append(f"EMAIL: '{source['email']}' vs '{db_author.email}'")
        
        # Check designation
        if source['designation'] != db_author.designation:
            issues.append(f"DESIGNATION: '{source['designation']}' vs '{db_author.designation}'")
        
        if issues:
            mismatches.append({
                'pid': pid,
                'name': source['faculty_name'],
                'issues': issues
            })
        else:
            print(f"  ✓ {pid:<15} {source['faculty_name']:<30} - All fields match")
    
    if mismatches:
        print(f"\n❌ DATA MISMATCHES FOUND ({len(mismatches)}):")
        print("="*100)
        for m in mismatches:
            print(f"\nPID: {m['pid']} - {m['name']}")
            for issue in m['issues']:
                print(f"  • {issue}")
    else:
        print(f"\n✅ ALL MATCHED FACULTY HAVE CORRECT DATA!")
    
    # Check co-authors not marked as faculty
    print(f"\n\nCO-AUTHOR VERIFICATION:")
    print("-"*100)
    
    # Get some co-authors from publications with faculty
    non_faculty = db.query(Author).filter(Author.is_faculty == False).limit(10).all()
    
    print(f"Sample non-faculty authors (checking they don't have faculty emails):")
    for author in non_faculty:
        if author.email and '@uohyd.ac.in' in author.email:
            print(f"  ⚠️  {author.name:<30} has faculty email: {author.email}")
        else:
            print(f"  ✓ {author.name:<30} - Correctly marked as non-faculty")
    
    db.close()
    
    print("\n" + "="*100)
    print("VERIFICATION COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()
