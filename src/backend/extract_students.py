#!/usr/bin/env python3
"""
Script to extract student data from PDF and ingest into database
"""
import pdfplumber
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from config.db_config import SessionLocal, init_postgres_db, engine
from models.db_models import Student, Base

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PDF_PATH = "/workspaces/SCIS-LiSA/dataset/students/uoh_students.pdf"


def normalize_program_name(program: str) -> str:
    """
    Normalize program name to fix common inconsistencies
    - Adds space before parenthesis if missing
    - Fixes case inconsistencies
    - Removes newlines and extra spaces
    """
    if not program or program == 'None':
        return None
    
    # Remove newlines and extra spaces
    program = ' '.join(program.split())
    
    # Fix missing space before parenthesis
    program = program.replace('Technology(', 'Technology (')
    program = program.replace('Application(', 'Application (')
    program = program.replace('Philosophy(', 'Philosophy (')
    
    # Standardize case for "Computer science" -> "Computer Science"
    program = program.replace('Computer science', 'Computer Science')
    
    return program


def create_students_table():
    """Create students table if it doesn't exist"""
    try:
        Base.metadata.create_all(bind=engine, tables=[Student.__table__])
        logger.info("Students table created or already exists")
    except Exception as e:
        logger.error(f"Error creating students table: {e}")
        raise


def extract_students_from_pdf(pdf_path: str) -> list:
    """
    Extract student data from PDF file
    
    Returns:
        List of student dictionaries
    """
    students = []
    
    # Column indices (will be determined from first page header)
    reg_no_idx = 1  # Default based on observed structure
    name_idx = 2
    semester_idx = 3
    program_idx = 4
    school_idx = 5
    prog_type_idx = 6
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Processing {len(pdf.pages)} pages from {pdf_path}")
            
            # First, find column indices from first page header
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0]
                tables = first_page.extract_tables()
                if tables and len(tables[0]) > 1:
                    table = tables[0]
                    # Find header row
                    for idx, row in enumerate(table):
                        if row and len(row) > 1 and row[1] and 'Reg No' in str(row[1]):
                            headers = row
                            try:
                                reg_no_idx = next(i for i, h in enumerate(headers) if h and 'Reg No' in str(h))
                                name_idx = next(i for i, h in enumerate(headers) if h and 'Name' in str(h) and 'School' not in str(h))
                                semester_idx = next(i for i, h in enumerate(headers) if h and 'Semester' in str(h))
                                program_idx = next(i for i, h in enumerate(headers) if h and 'Program' in str(h) and 'Type' not in str(h))
                                school_idx = next(i for i, h in enumerate(headers) if h and 'School Name' in str(h))
                                prog_type_idx = next(i for i, h in enumerate(headers) if h and 'Programme-Type' in str(h))
                                logger.info(f"Column indices: RegNo={reg_no_idx}, Name={name_idx}, Semester={semester_idx}, Program={program_idx}, School={school_idx}, ProgType={prog_type_idx}")
                                break
                            except StopIteration:
                                logger.warning("Could not find all required columns in header")
            
            # Process all pages
            for page_num, page in enumerate(pdf.pages, 1):
                if page_num % 10 == 0:
                    logger.info(f"Processing page {page_num}/{len(pdf.pages)}")
                
                # Extract tables from the page
                tables = page.extract_tables()
                
                if not tables:
                    continue
                
                # Process first table on the page
                table = tables[0]
                
                # Find where to start processing (skip header rows if present)
                start_row = 0
                for idx, row in enumerate(table):
                    if row and len(row) > 1:
                        # Skip title rows and header rows
                        cell_text = str(row[1]) if row[1] else ""
                        if 'ELECTORAL' in cell_text or 'Reg No' in cell_text or 'SNo' in cell_text:
                            start_row = idx + 1
                            continue
                        break
                
                # Process data rows
                for row_idx in range(start_row, len(table)):
                    row = table[row_idx]
                    
                    # Skip empty or invalid rows
                    if not row or len(row) <= max(reg_no_idx, name_idx, semester_idx, program_idx, school_idx, prog_type_idx):
                        continue
                    
                    # Extract student data
                    reg_no = str(row[reg_no_idx]).strip() if row[reg_no_idx] else None
                    name = str(row[name_idx]).strip() if row[name_idx] else None
                    semester_str = str(row[semester_idx]).strip() if row[semester_idx] else None
                    program = str(row[program_idx]).strip() if row[program_idx] else None
                    school_name = str(row[school_idx]).strip() if row[school_idx] else None
                    prog_type = str(row[prog_type_idx]).strip() if row[prog_type_idx] else None
                    
                    # Skip rows with missing critical data or invalid entries
                    if not reg_no or not name or reg_no == 'None' or name == 'None':
                        continue
                    
                    # Skip header repetitions
                    if 'Reg No' in reg_no or 'SNo' in reg_no:
                        continue
                    
                    # Parse semester as integer
                    try:
                        semester = int(semester_str) if semester_str and semester_str != 'None' else None
                    except ValueError:
                        semester = None
                    
                    # Normalize program name
                    normalized_program = normalize_program_name(program)
                    
                    student_data = {
                        'registration_number': reg_no,
                        'name': name,
                        'semester': semester,
                        'program': normalized_program,
                        'school_name': school_name if school_name != 'None' else None,
                        'programme_type': prog_type if prog_type != 'None' else None
                    }
                    
                    students.append(student_data)
                    
        logger.info(f"Extracted {len(students)} students from PDF")
        return students
        
    except Exception as e:
        logger.error(f"Error extracting students from PDF: {e}")
        raise


def ingest_students_to_db(students: list, db: Session) -> dict:
    """
    Ingest students into database
    
    Returns:
        Dictionary with statistics (inserted, duplicates, errors)
    """
    stats = {
        'inserted': 0,
        'duplicates': 0,
        'errors': 0
    }
    
    for student_data in students:
        try:
            # Check if student already exists
            existing = db.query(Student).filter(
                Student.registration_number == student_data['registration_number']
            ).first()
            
            if existing:
                stats['duplicates'] += 1
                logger.debug(f"Student {student_data['registration_number']} already exists")
                continue
            
            # Create new student
            student = Student(**student_data)
            db.add(student)
            db.commit()
            stats['inserted'] += 1
            
            if stats['inserted'] % 100 == 0:
                logger.info(f"Inserted {stats['inserted']} students...")
                
        except IntegrityError as e:
            db.rollback()
            stats['duplicates'] += 1
            logger.warning(f"Duplicate student {student_data['registration_number']}: {e}")
        except Exception as e:
            db.rollback()
            stats['errors'] += 1
            logger.error(f"Error inserting student {student_data.get('registration_number', 'unknown')}: {e}")
    
    return stats


def main():
    """Main execution function"""
    logger.info("Starting student data extraction and ingestion")
    
    try:
        # Create students table
        logger.info("Creating students table...")
        create_students_table()
        
        # Extract students from PDF
        logger.info(f"Extracting students from {PDF_PATH}...")
        students = extract_students_from_pdf(PDF_PATH)
        
        if not students:
            logger.error("No students extracted from PDF")
            return
        
        # Ingest to database
        logger.info("Ingesting students to database...")
        db = SessionLocal()
        try:
            stats = ingest_students_to_db(students, db)
            
            logger.info("=" * 60)
            logger.info("EXTRACTION AND INGESTION COMPLETE")
            logger.info(f"Total students extracted: {len(students)}")
            logger.info(f"Successfully inserted: {stats['inserted']}")
            logger.info(f"Duplicates skipped: {stats['duplicates']}")
            logger.info(f"Errors: {stats['errors']}")
            logger.info("=" * 60)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
