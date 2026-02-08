"""
Fix duplicate program names by standardizing formatting
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config.db_config import get_db, engine

def fix_program_names():
    """Standardize program names to fix duplicates"""
    
    # Mapping of incorrect names to correct standardized names
    fixes = {
        # Fix missing space before parenthesis
        "Master of Technology(Artificial Intelligence)": "Master of Technology (Artificial Intelligence)",
        "Master of Technology(Computer science)": "Master of Technology (Computer Science)",
        "Master of Technology(Information Technology)": "Master of Technology (Information Technology)",
        
        # Fix case inconsistency
        "Master of Technology (Computer science)": "Master of Technology (Computer Science)",
        
        # Fix newline issue in 5-year integrated program
        "Master of Technology (5 year Integrated) Computer Science and\nEngineering": "Master of Technology (5 year Integrated) Computer Science and Engineering"
    }
    
    db = next(get_db())
    
    try:
        for old_name, new_name in fixes.items():
            # Update students table
            result = db.execute(
                text("UPDATE students SET program = :new_name WHERE program = :old_name"),
                {"old_name": old_name, "new_name": new_name}
            )
            count = result.rowcount
            if count > 0:
                print(f"✓ Updated {count} records: '{old_name}' → '{new_name}'")
        
        db.commit()
        print("\n✓ All program names standardized successfully!")
        
        # Show final counts
        print("\nFinal program distribution:")
        result = db.execute(text("""
            SELECT program, COUNT(*) as count
            FROM students
            WHERE school_name LIKE '%Computer and Information%'
            AND program IS NOT NULL
            GROUP BY program
            ORDER BY program
        """))
        for row in result:
            print(f"  {row[0]}: {row[1]}")
            
    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    fix_program_names()
