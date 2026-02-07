"""
Migration: Add extended faculty information fields
Adds education, areas_of_interest, profile_page, and status columns to authors table
Then populates them from faculty_data.json
"""
import sys
import json
from pathlib import Path
from sqlalchemy import text
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db_config import engine, SessionLocal
from models.db_models import Author


def add_columns():
    """Add new columns to authors table"""
    print("Adding new columns to authors table...")
    
    with engine.connect() as conn:
        # Check if columns exist before adding
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'authors' AND column_name IN ('education', 'areas_of_interest', 'profile_page', 'status')
        """))
        existing_columns = [row[0] for row in result]
        
        columns_to_add = {
            'education': 'ALTER TABLE authors ADD COLUMN IF NOT EXISTS education TEXT',
            'areas_of_interest': 'ALTER TABLE authors ADD COLUMN IF NOT EXISTS areas_of_interest TEXT',
            'profile_page': 'ALTER TABLE authors ADD COLUMN IF NOT EXISTS profile_page VARCHAR(500)',
            'status': 'ALTER TABLE authors ADD COLUMN IF NOT EXISTS status VARCHAR(100)'
        }
        
        for col_name, sql in columns_to_add.items():
            if col_name not in existing_columns:
                print(f"  Adding column: {col_name}")
                conn.execute(text(sql))
            else:
                print(f"  Column '{col_name}' already exists, skipping")
        
        conn.commit()
    
    print("✓ Columns added successfully")


def populate_from_json():
    """Populate new fields from faculty_data.json"""
    print("\nPopulating faculty data from JSON...")
    
    # Load faculty data
    json_path = Path(__file__).parent.parent / 'references' / 'faculty_data.json'
    with open(json_path, 'r') as f:
        faculty_data = json.load(f)
    
    db = SessionLocal()
    try:
        updated_count = 0
        not_found = []
        
        for faculty in faculty_data:
            name = faculty.get('name')
            dblp_pid = faculty.get('dblp_pid')
            
            # Try to find faculty by DBLP PID first (more reliable), then by name
            author = None
            if dblp_pid:
                author = db.query(Author).filter(
                    Author.dblp_pid == dblp_pid,
                    Author.is_faculty == True
                ).first()
            
            if not author:
                # Fallback to name matching
                author = db.query(Author).filter(
                    Author.name == name,
                    Author.is_faculty == True
                ).first()
            
            if author:
                # Update fields
                author.education = faculty.get('education')
                author.areas_of_interest = faculty.get('areas_of_interest')
                author.profile_page = faculty.get('profile_page')
                author.status = faculty.get('status')  # Will be None for current faculty
                
                # Also update other fields if they're missing
                if not author.phone and faculty.get('phone'):
                    author.phone = faculty.get('phone')
                if not author.homepage and faculty.get('homepage'):
                    author.homepage = faculty.get('homepage')
                if not author.designation and faculty.get('designation'):
                    author.designation = faculty.get('designation')
                if not author.email and faculty.get('email'):
                    author.email = faculty.get('email')
                
                author.updated_at = datetime.utcnow()
                updated_count += 1
                print(f"  ✓ Updated: {name} (DB name: {author.name})")
            else:
                not_found.append(f"{name} (PID: {dblp_pid})")
                print(f"  ✗ Not found in database: {name} (PID: {dblp_pid})")
        
        db.commit()
        print(f"\n✓ Updated {updated_count} faculty records")
        
        if not_found:
            print(f"\n⚠ {len(not_found)} faculty not found in database:")
            for name in not_found[:5]:  # Show first 5
                print(f"  - {name}")
            if len(not_found) > 5:
                print(f"  ... and {len(not_found) - 5} more")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Run migration"""
    print("=" * 60)
    print("MIGRATION: Add Extended Faculty Information")
    print("=" * 60)
    
    try:
        add_columns()
        populate_from_json()
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
