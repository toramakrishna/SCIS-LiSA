"""
Database Migration: Add Scopus Author ID and update h-index
Adds scopus_author_id column and updates academic metrics for all faculty
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

def add_scopus_author_id_column():
    """Add scopus_author_id column to authors table if it doesn't exist"""
    
    if column_exists('authors', 'scopus_author_id'):
        print("✓ Column 'scopus_author_id' already exists")
        return
    
    print("Adding column: scopus_author_id")
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE authors 
            ADD COLUMN scopus_author_id VARCHAR(100);
        """))
        conn.commit()
    print("✓ Column 'scopus_author_id' added successfully")

def update_faculty_metrics():
    """Update faculty records with Scopus Author ID and h-index from JSON"""
    
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
    scopus_updated = 0
    hindex_updated = 0
    
    try:
        for faculty in faculty_data:
            json_name = faculty['name']
            # Apply name mapping if exists, otherwise use JSON name
            db_name = name_mappings.get(json_name, json_name)
            scopus_author_id = faculty.get('scopus_author_id')
            h_index = faculty.get('h_index')
            
            # Build update query dynamically based on available data
            update_fields = []
            params = {'name': db_name}
            
            if scopus_author_id:
                update_fields.append("scopus_author_id = :scopus_author_id")
                params['scopus_author_id'] = scopus_author_id
                scopus_updated += 1
            
            if h_index is not None:
                update_fields.append("h_index = :h_index")
                params['h_index'] = h_index
                hindex_updated += 1
            
            if update_fields:
                update_query = f"""
                    UPDATE authors 
                    SET {', '.join(update_fields)}
                    WHERE name = :name AND is_faculty = true
                """
                
                result = session.execute(text(update_query), params)
                
                if result.rowcount > 0:
                    updated_count += 1
                    updates = []
                    if scopus_author_id:
                        updates.append(f"Scopus ID: {scopus_author_id}")
                    if h_index is not None:
                        updates.append(f"h-index: {h_index}")
                    display_name = db_name if json_name == db_name else f"{json_name} → {db_name}"
                    print(f"✓ Updated {display_name}: {', '.join(updates)}")
                else:
                    print(f"⚠ Faculty not found in database: {json_name} (searched as: {db_name})")
        
        session.commit()
        
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total faculty in JSON: {len(faculty_data)}")
        print(f"Faculty updated in database: {updated_count}")
        print(f"  - Scopus Author IDs updated: {scopus_updated}")
        print(f"  - h-index values updated: {hindex_updated}")
        print("="*60)
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Error updating faculty metrics: {e}")
        raise
    finally:
        session.close()

def main():
    """Run migration"""
    print("="*60)
    print("DATABASE MIGRATION: Add Scopus Author ID and Update Metrics")
    print("="*60)
    print()
    
    try:
        # Step 1: Add scopus_author_id column
        add_scopus_author_id_column()
        
        # Step 2: Update faculty records
        update_faculty_metrics()
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
