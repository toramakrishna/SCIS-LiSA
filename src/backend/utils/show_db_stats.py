#!/usr/bin/env python3
"""Show current database statistics"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db_config import get_postgres_db
from models.db_models import Author, Publication, Collaboration, Venue
from sqlalchemy import func

def main():
    db = next(get_postgres_db())

    print("\n" + "="*80)
    print("CURRENT DATABASE STATISTICS")
    print("="*80)

    total_pubs = db.query(Publication).count()
    total_authors = db.query(Author).count()
    total_collabs = db.query(Collaboration).count()
    total_venues = db.query(Venue).count()
    faculty_count = db.query(Author).filter(Author.is_faculty == True).count()

    print(f"\n  Publications:     {total_pubs:,}")
    print(f"  Authors:          {total_authors:,}")
    print(f"  Collaborations:   {total_collabs:,}")
    print(f"  Venues:           {total_venues:,}")
    print(f"  Faculty Members:  {faculty_count:,}")

    # Faculty with publications
    faculty_with_pubs = db.query(Author).filter(
        Author.is_faculty == True
    ).all()

    faculty_pub_counts = []
    for faculty in faculty_with_pubs:
        count = faculty.publications.count()
        if count > 0:
            faculty_pub_counts.append((faculty.name, count))

    faculty_pub_counts.sort(key=lambda x: x[1], reverse=True)

    print(f"\n  Faculty with publications: {len(faculty_pub_counts)}")
    print(f"  Faculty with zero publications: {faculty_count - len(faculty_pub_counts)}")

    if faculty_pub_counts:
        print(f"\n  Top 5 researchers:")
        for i, (name, count) in enumerate(faculty_pub_counts[:5], 1):
            print(f"    {i}. {name:<40} {count:>4} publications")

    print("\n" + "="*80 + "\n")

    db.close()

if __name__ == '__main__':
    main()
