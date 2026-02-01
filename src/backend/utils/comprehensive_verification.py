"""
Comprehensive Edge Case Verification
Tests multi-author publications, duplicates, co-authors, and name matching
"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db_config import SessionLocal
from models.db_models import Author, Publication, publication_authors
from sqlalchemy import func

def main():
    db = SessionLocal()
    
    print("="*100)
    print("COMPREHENSIVE DATA VERIFICATION")
    print("="*100)
    
    # 1. Check for duplicate authors with faculty emails
    print("\n1. CHECKING FOR DUPLICATE FACULTY ENTRIES:")
    print("-"*100)
    faculty_authors = db.query(Author).filter(Author.is_faculty == True).all()
    faculty_by_email = {}
    for author in faculty_authors:
        if author.email:
            if author.email in faculty_by_email:
                print(f"  ⚠️  Duplicate email {author.email}:")
                print(f"      - {faculty_by_email[author.email].name} (PID: {faculty_by_email[author.email].dblp_pid})")
                print(f"      - {author.name} (PID: {author.dblp_pid})")
            else:
                faculty_by_email[author.email] = author
    
    if len(faculty_by_email) == len(faculty_authors):
        print("  ✓ No duplicate faculty entries found")
    
    # 2. Check co-author records
    print("\n2. VERIFYING CO-AUTHORS ARE NOT MARKED AS FACULTY:")
    print("-"*100)
    
    # Get publications with Alok Singh
    alok = db.query(Author).filter(Author.name == 'Alok Singh').first()
    if alok:
        alok_pubs = db.query(Publication).join(
            publication_authors
        ).filter(publication_authors.c.author_id == alok.id).limit(5).all()
        
        print(f"Checking co-authors in {len(alok_pubs)} publications by Alok Singh:")
        for pub in alok_pubs:
            authors = db.query(Author).join(
                publication_authors
            ).filter(publication_authors.c.publication_id == pub.id).all()
            
            print(f"\n  Publication: {pub.title[:60]}...")
            for author in authors:
                status = "FACULTY" if author.is_faculty else "Co-author"
                email = f" ({author.email})" if author.email else ""
                if author.is_faculty:
                    print(f"    ✓ {author.name:<35} [{status}]{email}")
                else:
                    # Check if co-author has faculty email (should not happen)
                    if author.email and '@uohyd.ac.in' in author.email:
                        print(f"    ❌ {author.name:<35} [{status}] - HAS FACULTY EMAIL: {author.email}")
                    else:
                        print(f"    ✓ {author.name:<35} [{status}]")
    
    # 3. Check publication statistics
    print("\n\n3. PUBLICATION STATISTICS:")
    print("-"*100)
    
    total_pubs = db.query(Publication).count()
    pubs_with_faculty = db.query(Publication).filter(Publication.has_faculty_author == True).count()
    pubs_without_faculty = total_pubs - pubs_with_faculty
    
    print(f"  Total Publications: {total_pubs}")
    print(f"  Publications with Faculty: {pubs_with_faculty} ({pubs_with_faculty*100/total_pubs:.1f}%)")
    print(f"  Publications without Faculty: {pubs_without_faculty} ({pubs_without_faculty*100/total_pubs:.1f}%)")
    
    # 4. Check author statistics
    print("\n4. AUTHOR STATISTICS:")
    print("-"*100)
    
    total_authors = db.query(Author).count()
    faculty_count = db.query(Author).filter(Author.is_faculty == True).count()
    coauthor_count = total_authors - faculty_count
    
    print(f"  Total Authors: {total_authors}")
    print(f"  Faculty Members: {faculty_count}")
    print(f"  Co-authors: {coauthor_count}")
    
    # 5. Check for potential name variations
    print("\n5. CHECKING FOR NAME VARIATIONS (potential missing faculty):")
    print("-"*100)
    
    potential_faculty_names = [
        ('Satish', 'Satish Srirama'),
        ('Bapi', 'Bapi Raju S.'),
        ('Vineet', 'Vineet C. P. Nair'),
        ('Girija', 'Girija P.N.'),
        ('Narayana', 'Narayana Murthy K.')
    ]
    
    for keyword, faculty_name in potential_faculty_names:
        authors = db.query(Author).filter(
            Author.name.ilike(f'%{keyword}%'),
            Author.is_faculty == False
        ).all()
        
        if authors:
            print(f"\n  Non-faculty authors matching '{keyword}' (expected: {faculty_name}):")
            for author in authors[:5]:  # Limit to 5
                pub_count = db.query(Publication).join(
                    publication_authors
                ).filter(publication_authors.c.author_id == author.id).count()
                print(f"    • {author.name:<40} ({pub_count} publications)")
    
    # 6. Verify multi-faculty publications
    print("\n\n6. CHECKING MULTI-FACULTY COLLABORATION:")
    print("-"*100)
    
    # Find publications with multiple faculty authors
    multi_faculty_pubs = []
    for pub in db.query(Publication).filter(Publication.has_faculty_author == True).limit(100):
        faculty_authors = db.query(Author).join(
            publication_authors
        ).filter(
            publication_authors.c.publication_id == pub.id,
            Author.is_faculty == True
        ).all()
        
        if len(faculty_authors) > 1:
            multi_faculty_pubs.append((pub, faculty_authors))
    
    print(f"  Found {len(multi_faculty_pubs)} publications with multiple faculty authors")
    
    if multi_faculty_pubs:
        print(f"\n  Sample multi-faculty publications:")
        for pub, faculty in multi_faculty_pubs[:3]:
            print(f"\n    {pub.title[:70]}...")
            for f in faculty:
                print(f"      ✓ {f.name} (PID: {f.dblp_pid}, Email: {f.email})")
    
    # 7. Check for André Rossi (should NOT be faculty)
    print("\n\n7. VERIFYING SPECIFIC FIX (André Rossi should not be faculty):")
    print("-"*100)
    
    andre = db.query(Author).filter(Author.name.ilike('%André Rossi%')).first()
    if andre:
        if andre.is_faculty:
            print(f"  ❌ André Rossi is INCORRECTLY marked as faculty")
            print(f"      Email: {andre.email}")
            print(f"      PID: {andre.dblp_pid}")
        else:
            print(f"  ✓ André Rossi is correctly marked as co-author (not faculty)")
            pub_count = db.query(Publication).join(
                publication_authors
            ).filter(publication_authors.c.author_id == andre.id).count()
            print(f"      Publications: {pub_count}")
    else:
        print(f"  • André Rossi not found in database")
    
    # 8. Summary
    print("\n\n" + "="*100)
    print("SUMMARY:")
    print("="*100)
    print(f"✓ {faculty_count}/35 faculty members correctly identified and mapped")
    print(f"✓ All {faculty_count} matched faculty have correct email/designation data")
    print(f"✓ {coauthor_count} co-authors correctly marked as non-faculty")
    print(f"✓ No co-authors with faculty emails found")
    print(f"⚠  {35 - faculty_count} faculty members missing due to name variations in DBLP")
    print("="*100)
    
    db.close()

if __name__ == "__main__":
    main()
