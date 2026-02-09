#!/usr/bin/env python3
"""
Migration: Add IRINS profile fields to authors table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config.db_config import engine, SessionLocal

def add_irins_columns():
    """Add IRINS profile columns to authors table"""
    print("Adding IRINS profile columns to authors table...")
    
    with engine.connect() as conn:
        try:
            # Check if columns exist
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'authors' 
                AND column_name IN ('irins_profile', 'irins_url', 'irins_photo_url', 'photo_path')
            """)
            
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            # Add columns if they don't exist
            columns_to_add = {
                'irins_profile': 'VARCHAR(100)',
                'irins_url': 'VARCHAR(500)',
                'irins_photo_url': 'VARCHAR(500)',
                'photo_path': 'VARCHAR(500)'
            }
            
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_columns:
                    print(f"  Adding column: {col_name}")
                    alter_query = text(f"ALTER TABLE authors ADD COLUMN {col_name} {col_type}")
                    conn.execute(alter_query)
                else:
                    print(f"  Column {col_name} already exists")
            
            conn.commit()
            print("✓ Successfully added IRINS columns")
            
        except Exception as e:
            print(f"✗ Error adding columns: {e}")
            conn.rollback()
            raise

def update_faculty_irins_data():
    """Update faculty with IRINS and Scopus data from faculty_data.json"""
    print("\nUpdating faculty with IRINS and Scopus data from JSON...")
    
    import json
    
    # Load faculty data
    json_path = Path(__file__).parent.parent / 'references' / 'faculty_data.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        faculty_data = json.load(f)
    
    db = SessionLocal()
    try:
        from models.db_models import Author
        
        updated = 0
        for fac in faculty_data:
            # Find by DBLP PID
            dblp_pid = fac.get('dblp_pid')
            if not dblp_pid:
                continue
            
            author = db.query(Author).filter(Author.dblp_pid == dblp_pid).first()
            if author:
                # Update IRINS fields if they exist in JSON
                if 'irins_profile' in fac:
                    author.irins_profile = fac['irins_profile']
                if 'irins_url' in fac:
                    author.irins_url = fac['irins_url']
                if 'irins_photo_url' in fac:
                    author.irins_photo_url = fac['irins_photo_url']
                if 'photo_path' in fac:
                    author.photo_path = fac['photo_path']
                
                # Update Scopus fields if they exist in JSON
                if 'scopus_author_id' in fac:
                    author.scopus_author_id = fac['scopus_author_id']
                if 'scopus_url' in fac:
                    author.scopus_url = fac['scopus_url']
                if 'h_index' in fac:
                    author.h_index = fac['h_index']
                
                updated += 1
                print(f"  ✓ Updated: {fac['name']}")
        
        db.commit()
        print(f"\n✓ Updated {updated} faculty with IRINS and Scopus data")
        
    except Exception as e:
        print(f"✗ Error updating IRINS data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Run migration"""
    print("="*60)
    print("IRINS Profile Migration")
    print("="*60)
    
    try:
        add_irins_columns()
        update_faculty_irins_data()
        
        print("\n" + "="*60)
        print("Migration completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
