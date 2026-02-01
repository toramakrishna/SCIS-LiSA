"""
Faculty API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from config.db_config import get_db
from models.db_models import Author, Publication, Collaboration, publication_authors
from api.schemas import (
    FacultySchema,
    PublicationSchema,
    PaginatedResponse,
    FacultyStatsSchema
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[FacultySchema])
async def list_faculty(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    designation: Optional[str] = Query(None, description="Filter by designation"),
    db: Session = Depends(get_db)
):
    """
    List all faculty members with pagination and filters.
    
    **Filters:**
    - designation: Filter by designation (Professor, Associate Professor, etc.)
    
    **Pagination:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    """
    # Query only faculty members
    query = db.query(Author).filter(Author.is_faculty == True)
    
    # Apply filters
    if designation:
        query = query.filter(Author.designation.ilike(f"%{designation}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    faculty_members = query.offset(offset).limit(page_size).all()
    
    return PaginatedResponse(
        items=faculty_members,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{faculty_id}", response_model=FacultySchema)
async def get_faculty(
    faculty_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific faculty member.
    """
    faculty = db.query(Author).filter(
        Author.id == faculty_id,
        Author.is_faculty == True
    ).first()
    
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    
    return faculty


@router.get("/{faculty_id}/publications", response_model=PaginatedResponse[PublicationSchema])
async def get_faculty_publications(
    faculty_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    year: Optional[int] = Query(None, description="Filter by year"),
    publication_type: Optional[str] = Query(None, description="Filter by publication type"),
    db: Session = Depends(get_db)
):
    """
    Get all publications for a specific faculty member.
    
    **Filters:**
    - year: Filter by publication year
    - publication_type: Filter by type (article, inproceedings, etc.)
    """
    # Verify faculty exists
    faculty = db.query(Author).filter(
        Author.id == faculty_id,
        Author.is_faculty == True
    ).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    
    # Build query for publications by this faculty member
    # Join through the publication_authors association table
    query = db.query(Publication).join(
        publication_authors,
        Publication.id == publication_authors.c.publication_id
    ).filter(
        publication_authors.c.author_id == faculty_id
    )
    
    # Apply filters
    if year:
        query = query.filter(Publication.year == year)
    
    if publication_type:
        query = query.filter(Publication.type == publication_type)
    
    # Order by year descending
    query = query.order_by(desc(Publication.year))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    publications = query.offset(offset).limit(page_size).all()
    
    return PaginatedResponse(
        items=publications,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{faculty_id}/collaborations")
async def get_faculty_collaborations(
    faculty_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get collaboration network for a faculty member.
    
    Returns list of co-authors with collaboration counts.
    """
    # Verify faculty exists
    from sqlalchemy import or_, case
    faculty = db.query(Author).filter(
        Author.id == faculty_id,
        Author.is_faculty == True
    ).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    
    # Query collaborations from both directions
    # Get the collaborator ID and name (handling bidirectional relationships)
    query = db.query(
        case(
            (Collaboration.author1_id == faculty_id, Collaboration.author2_id),
            else_=Collaboration.author1_id
        ).label('collaborator_id'),
        func.sum(Collaboration.collaboration_count).label('collaboration_count')
    ).filter(
        or_(
            Collaboration.author1_id == faculty_id,
            Collaboration.author2_id == faculty_id
        )
    ).group_by(
        'collaborator_id'
    ).order_by(
        desc('collaboration_count')
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    collaborations = query.offset(offset).limit(page_size).all()
    
    # Get author names for collaborators
    items = []
    for collab in collaborations:
        collaborator = db.query(Author).filter(Author.id == collab.collaborator_id).first()
        if collaborator:
            items.append({
                "collaborator_id": collab.collaborator_id,
                "collaborator_name": collaborator.name,
                "collaboration_count": collab.collaboration_count
            })
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{faculty_id}/stats", response_model=FacultyStatsSchema)
async def get_faculty_stats(
    faculty_id: int,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific faculty member.
    
    Includes:
    - Total publications
    - Publications by type
    - Publications by year
    - Total collaborators
    - H-index (if available)
    """
    # Verify faculty exists
    faculty = db.query(Author).filter(
        Author.id == faculty_id,
        Author.is_faculty == True
    ).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    
    # Total publications
    total_pubs = db.query(func.count(func.distinct(Publication.id))).join(
        publication_authors,
        Publication.id == publication_authors.c.publication_id
    ).filter(
        publication_authors.c.author_id == faculty_id
    ).scalar()
    
    # Publications by type
    pubs_by_type = db.query(
        Publication.type,
        func.count(func.distinct(Publication.id)).label('count')
    ).join(
        publication_authors,
        Publication.id == publication_authors.c.publication_id
    ).filter(
        publication_authors.c.author_id == faculty_id
    ).group_by(
        Publication.type
    ).all()
    
    # Publications by year
    pubs_by_year = db.query(
        Publication.year,
        func.count(func.distinct(Publication.id)).label('count')
    ).join(
        publication_authors,
        Publication.id == publication_authors.c.publication_id
    ).filter(
        publication_authors.c.author_id == faculty_id
    ).group_by(
        Publication.year
    ).order_by(
        desc(Publication.year)
    ).limit(10).all()
    
    # Total collaborators - count distinct co-authors from both directions
    from sqlalchemy import or_
    total_collaborators = db.query(
        func.count(func.distinct(
            func.case(
                (Collaboration.author1_id == faculty_id, Collaboration.author2_id),
                else_=Collaboration.author1_id
            )
        ))
    ).filter(
        or_(
            Collaboration.author1_id == faculty_id,
            Collaboration.author2_id == faculty_id
        )
    ).scalar()
    
    return FacultyStatsSchema(
        total_publications=total_pubs or 0,
        publications_by_type={pt.type: pt.count for pt in pubs_by_type},
        publications_by_year={py.year: py.count for py in pubs_by_year},
        total_collaborators=total_collaborators or 0,
        h_index=None  # To be calculated if needed
    )
