"""
Students API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from config.db_config import get_db
from models.db_models import Student
from api.schemas import StudentSchema, StudentCreate, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[StudentSchema])
async def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=5000, description="Items per page"),
    school: Optional[str] = Query(None, description="Filter by school name"),
    program: Optional[str] = Query(None, description="Filter by program"),
    programme_type: Optional[str] = Query(None, description="Filter by programme type"),
    search: Optional[str] = Query(None, description="Search by name or registration number"),
    sort_by: str = Query("name", description="Sort by: name, registration_number, semester"),
    db: Session = Depends(get_db)
):
    """
    List all students with pagination and filters.
    
    **Filters:**
    - school: Filter by school name
    - program: Filter by program
    - programme_type: Filter by programme type
    - search: Search by name or registration number
    - sort_by: Sort by name, registration_number, or semester
    
    **Pagination:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 5000)
    """
    # Base query
    query = db.query(Student)
    
    # Apply filters
    if school:
        query = query.filter(Student.school_name.ilike(f"%{school}%"))
    
    if program:
        query = query.filter(Student.program.ilike(f"%{program}%"))
    
    if programme_type:
        query = query.filter(Student.programme_type.ilike(f"%{programme_type}%"))
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Student.name.ilike(search_pattern),
                Student.registration_number.ilike(search_pattern)
            )
        )
    
    # Apply sorting
    if sort_by == "registration_number":
        query = query.order_by(Student.registration_number)
    elif sort_by == "semester":
        query = query.order_by(Student.semester.desc().nullslast())
    else:  # default: name
        query = query.order_by(Student.name)
    
    # Get total count (before pagination)
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    students = query.offset(offset).limit(page_size).all()
    
    return PaginatedResponse(
        items=students,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{student_id}", response_model=StudentSchema)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific student.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.get("/by-registration/{registration_number}", response_model=StudentSchema)
async def get_student_by_registration(
    registration_number: str,
    db: Session = Depends(get_db)
):
    """
    Get student information by registration number.
    """
    student = db.query(Student).filter(
        Student.registration_number == registration_number
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.get("/stats/summary")
async def get_student_stats(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics about students.
    """
    # Total students
    total = db.query(func.count(Student.id)).scalar()
    
    # Students by school
    by_school = db.query(
        Student.school_name,
        func.count(Student.id).label('count')
    ).group_by(Student.school_name).order_by(func.count(Student.id).desc()).all()
    
    # Students by programme type
    by_programme = db.query(
        Student.programme_type,
        func.count(Student.id).label('count')
    ).group_by(Student.programme_type).order_by(func.count(Student.id).desc()).all()
    
    # Students by semester
    by_semester = db.query(
        Student.semester,
        func.count(Student.id).label('count')
    ).filter(Student.semester.isnot(None)).group_by(Student.semester).order_by(Student.semester).all()
    
    return {
        "total_students": total,
        "by_school": [{"school": s, "count": c} for s, c in by_school],
        "by_programme_type": [{"programme_type": p, "count": c} for p, c in by_programme],
        "by_semester": [{"semester": s, "count": c} for s, c in by_semester]
    }


@router.post("/", response_model=StudentSchema, status_code=201)
async def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new student.
    
    **Required fields:**
    - registration_number: Unique student registration number
    - name: Student's full name
    
    **Optional fields:**
    - semester: Current semester (integer)
    - program: Academic program name
    - school_name: School/department name
    - programme_type: Type of programme (e.g., Full Time, Part Time)
    - email: Student's email address
    - phone: Student's phone number
    """
    # Check if registration number already exists
    existing = db.query(Student).filter(
        Student.registration_number == student.registration_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Student with registration number '{student.registration_number}' already exists"
        )
    
    try:
        # Create new student
        db_student = Student(**student.model_dump())
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create student: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
