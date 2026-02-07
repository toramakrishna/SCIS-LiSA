"""
Database Migration: Add Scopus URL
Adds scopus_url column and populates it for all faculty with Scopus Author IDs
"""

import json
import sys
from pathlib import Path
from sqlalchemy import text, inspect

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from config.db_config import engine, SessionLocal

def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_scopus_url_column():
    """Add scopus_url column to authors table if it doesn't exist"""
    
    if column_exists('authors', 'scopus_url'):
        print("✓ Column 'scopus_url' already exists")
        return
    
    print("Adding column: scopus_url")
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE authors 
            ADD COLUMN scopus_url VARCHAR(500);
        """))
        conn.commit()
    print("✓ Column 'scopus_url' added successfully")

def update_faculty_scopus_urls():
    """Update faculty records with Scopus URLs from JSON"""
    
    # Name mappings: JSON name -> Database name
    name_mappings = {
        "Durga Bhavani S.": "S. Durga Bhavani",
        "Nagamani M.": "M. Nagamani",
        "Nagender Kumar S.": "Nagender Kumar Suryadevara",
        "Naveen Nekuri": "Nekuri Naveen",
        "Rukma Rekha N.": "N. Rukma Rekha",
        "Sai Prasad P.S.V.S.": "P. S. V. S. Sai Prasad",
        "Subba Rao Y.V.": "Y. V. Subba Rao",
        "Swarupa Rani K.": "K. Swarupa Rani",
        "Vineet C. P. Nair": "Vineet Padmanabhan",
        "Arun K Pujari": "Arun K. Pujari",
        "Bapi Raju S.": "Bapi Raju Surampudi",
        "Girija P.N.": "P. N. Girija",
        "Narayana Murthy K.": "Narayana Murthy Kavi",
        "Sobha Rani T.": "T. Sobha Rani",
        "Srinivasa Rao Battula": "Battula Srinivasa Rao",
        "Raghavendra Rao C.": "C. Raghavendra Rao",
        "Venkaiah V.C.": "V. Ch. Venkaiah",
    }
    
    # Load faculty data from JSON
    json_path = Path(__file__).parent.parent / 'references' / 'faculty_data.json'
    print(f"\nLoading faculty data from: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        faculty_data = json.load(f)
    
    print(f"Found {len(faculty_data)} faculty members in JSON\n")
    
    session = SessionLocal()
    updated_count = 0
    
    try:
        for faculty in faculty_data:
            json_name = faculty['name']
            # Apply name mapping if exists, otherwise use JSON name
            db_name = name_mappings.get(json_name, json_name)
            scopus_url = faculty.get('scopus_url')
            
            if scopus_url:
                update_query = """
                    UPDATE authors 
                    SET scopus_url = :scopus_url
                    WHERE name = :name AND is_faculty = true
                """
                
                result = session.execute(text(update_query), {
                    'name': db_name, 
                    'scopus_url': scopus_url
                })
                
                if result.rowcount > 0:
                    updated_count += 1
                    display_name = db_name if json_name == db_name else f"{json_name} → {db_name}"
                    print(f"✓ Updated {display_name}")
                else:
                    print(f"⚠ Faculty not found in database: {json_name} (searched as: {db_name})")
        
        session.commit()
        
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total faculty in JSON: {len(faculty_data)}")
        print(f"Faculty updated with Scopus URLs: {updated_count}")
        print("="*60)
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Error updating Scopus URLs: {e}")
        raise
    finally:
        session.close()

def main():
    """Run migration"""
    print("="*60)
    print("DATABASE MIGRATION: Add Scopus URLs")
    print("="*60)
    print()
    
    try:
        # Step 1: Add scopus_url column
        add_scopus_url_column()
        
        # Step 2: Update faculty records
        update_faculty_scopus_urls()
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
