"""
Merge Duplicate Faculty Author Records
Handles name variations where faculty members exist as both faculty and co-authors
"""
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db_config import SessionLocal
from models.db_models import Author, Publication, Collaboration, publication_authors
from sqlalchemy import and_, or_, text
import json

def normalize_name_for_matching(name: str) -> str:
    """Normalize name by removing dots, commas, and extra spaces"""
    if not name:
        return ""
    name = name.lower()
    name = name.replace('.', '').replace(',', '')
    name = ' '.join(name.split())
    return name

def get_name_variations(name: str) -> List[str]:
    """Generate common name variations"""
    variations = []
    parts = name.split()
    
    if len(parts) >= 2:
        # Original
        variations.append(name)
        
        # Handle "FirstName MiddleName LastName" -> "FirstName LastName"
        if len(parts) > 2:
            variations.append(f"{parts[0]} {parts[-1]}")
        
        # Handle "FirstName LastName" -> "LastName FirstName"
        if len(parts) == 2:
            variations.append(f"{parts[1]} {parts[0]}")
        
        # Handle "FirstName LastName Suffix" -> "Suffix FirstName LastName"
        if len(parts) == 3:
            variations.append(f"{parts[2]} {parts[0]} {parts[1]}")
            variations.append(f"{parts[2]}. {parts[0]} {parts[1]}")
        
        # Handle initials
        # "S. Durga Bhavani" <-> "Durga Bhavani S."
        if len(parts[0]) <= 2:  # First part is initial
            rest = ' '.join(parts[1:])
            variations.append(f"{rest} {parts[0]}")
            variations.append(f"{rest} {parts[0].replace('.', '')}")
        
        if len(parts[-1]) <= 2:  # Last part is initial
            rest = ' '.join(parts[:-1])
            variations.append(f"{parts[-1]} {rest}")
            variations.append(f"{parts[-1].replace('.', '')} {rest}")
    
    # Normalize all variations
    normalized = []
    for v in variations:
        norm = normalize_name_for_matching(v)
        if norm and norm not in normalized:
            normalized.append(norm)
    
    return normalized

def find_duplicate_authors(db, faculty_author: Author) -> List[Author]:
    """Find potential duplicate non-faculty authors for a faculty member"""
    variations = get_name_variations(faculty_author.name)
    
    duplicates = []
    for variation in variations:
        candidates = db.query(Author).filter(
            Author.is_faculty == False,
            Author.normalized_name == variation
        ).all()
        
        for candidate in candidates:
            if candidate not in duplicates:
                duplicates.append(candidate)
    
    return duplicates

def merge_authors(db, faculty_author: Author, duplicate_author: Author) -> Dict:
    """Merge duplicate author into faculty author"""
    stats = {
        'publications_transferred': 0,
        'collaborations_updated': 0
    }
    
    print(f"\n  Merging '{duplicate_author.name}' into '{faculty_author.name}'...")
    
    # 1. Transfer all publications from duplicate to faculty
    duplicate_pubs = db.query(publication_authors).filter(
        publication_authors.c.author_id == duplicate_author.id
    ).all()
    
    for pub_assoc in duplicate_pubs:
        # Check if faculty author already has this publication
        existing = db.query(publication_authors).filter(
            and_(
                publication_authors.c.publication_id == pub_assoc.publication_id,
                publication_authors.c.author_id == faculty_author.id
            )
        ).first()
        
        if not existing:
            # Transfer the publication to faculty author
            db.execute(
                publication_authors.update().where(
                    and_(
                        publication_authors.c.publication_id == pub_assoc.publication_id,
                        publication_authors.c.author_id == duplicate_author.id
                    )
                ).values(author_id=faculty_author.id)
            )
            stats['publications_transferred'] += 1
    
    # 2. Handle collaborations - delete all involving duplicate, then recreate as needed
    # Just delete all collaborations involving the duplicate author
    # They'll be recreated if needed during future ingestions
    db.execute(
        text("""
            DELETE FROM collaborations 
            WHERE author1_id = :duplicate_id OR author2_id = :duplicate_id
        """),
        {'duplicate_id': duplicate_author.id}
    )
    
    # 3. Delete the duplicate author
    db.delete(duplicate_author)
    
    # 4. Update faculty author statistics
    total_pubs = db.query(publication_authors).filter(
        publication_authors.c.author_id == faculty_author.id
    ).count()
    
    faculty_author.total_publications = total_pubs
    
    print(f"    ✓ Transferred {stats['publications_transferred']} publications")
    print(f"    ✓ New total: {total_pubs} publications")
    
    return stats

def main():
    db = SessionLocal()
    
    print("="*100)
    print("FACULTY DUPLICATE AUTHOR MERGE UTILITY")
    print("="*100)
    
    # Load faculty mapping
    current_dir = Path(__file__).parent.parent
    faculty_json = current_dir / 'references' / 'dblp' / 'faculty_dblp_matched.json'
    
    with open(faculty_json, 'r') as f:
        source_faculty = json.load(f)
    
    faculty_by_pid = {f['dblp_pid']: f for f in source_faculty if f.get('dblp_matched')}
    
    # Get all faculty authors
    faculty_authors = db.query(Author).filter(Author.is_faculty == True).all()
    
    print(f"\nFound {len(faculty_authors)} faculty members in database")
    print(f"Checking for duplicate non-faculty records...\n")
    
    total_stats = {
        'faculty_checked': 0,
        'duplicates_found': 0,
        'publications_transferred': 0,
        'merges_performed': 0
    }
    
    merge_log = []
    
    for faculty in faculty_authors:
        total_stats['faculty_checked'] += 1
        
        # Find duplicates
        duplicates = find_duplicate_authors(db, faculty)
        
        if duplicates:
            print(f"\n{faculty.name} (PID: {faculty.dblp_pid}):")
            print(f"  Current publications: {faculty.total_publications}")
            print(f"  Found {len(duplicates)} duplicate(s):")
            
            for dup in duplicates:
                dup_pubs = db.query(publication_authors).filter(
                    publication_authors.c.author_id == dup.id
                ).count()
                print(f"    • '{dup.name}' - {dup_pubs} publications")
                total_stats['duplicates_found'] += 1
            
            # Merge each duplicate
            for dup in duplicates:
                stats = merge_authors(db, faculty, dup)
                total_stats['publications_transferred'] += stats['publications_transferred']
                total_stats['merges_performed'] += 1
                
                merge_log.append({
                    'faculty_name': faculty.name,
                    'faculty_pid': faculty.dblp_pid,
                    'duplicate_name': dup.name,
                    'publications_transferred': stats['publications_transferred']
                })
    
    # Commit all changes
    try:
        db.commit()
        print("\n" + "="*100)
        print("MERGE COMPLETE - Changes committed successfully")
        print("="*100)
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during commit: {e}")
        print("All changes have been rolled back")
        db.close()
        return
    
    # Print summary
    print(f"\nSUMMARY:")
    print(f"  Faculty Checked: {total_stats['faculty_checked']}")
    print(f"  Duplicates Found: {total_stats['duplicates_found']}")
    print(f"  Merges Performed: {total_stats['merges_performed']}")
    print(f"  Publications Transferred: {total_stats['publications_transferred']}")
    
    if merge_log:
        print(f"\nDETAILED MERGE LOG:")
        print("-"*100)
        for entry in merge_log:
            print(f"  {entry['faculty_name']} (PID: {entry['faculty_pid']})")
            print(f"    Merged: '{entry['duplicate_name']}' ({entry['publications_transferred']} publications)")
    
    # Verify final state
    print(f"\n" + "="*100)
    print("VERIFICATION - Faculty Publication Counts:")
    print("="*100)
    
    faculty_authors = db.query(Author).filter(Author.is_faculty == True).order_by(Author.name).all()
    
    for faculty in faculty_authors:
        actual_count = db.query(publication_authors).filter(
            publication_authors.c.author_id == faculty.id
        ).count()
        
        faculty_info = faculty_by_pid.get(faculty.dblp_pid, {})
        expected_name = faculty_info.get('faculty_name', 'Unknown')
        
        status = "✓" if actual_count > 10 else "⚠"
        print(f"  {status} {faculty.name:<30} PID: {faculty.dblp_pid:<15} Pubs: {actual_count:>3}")
    
    db.close()
    
    print("\n" + "="*100)
    print("Done! Re-run verification scripts to confirm all counts are correct.")
    print("="*100)

if __name__ == "__main__":
    main()
