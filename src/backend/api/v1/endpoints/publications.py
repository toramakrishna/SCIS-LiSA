"""
Publications API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from typing import List, Optional
import re

from config.db_config import SessionLocal, get_db
from models.db_models import Publication, Author, Venue
from api import schemas

router = APIRouter()


# Static routes MUST come before parameterized routes
@router.get("/stats", response_model=dict)
async def get_publication_stats(
    db: Session = Depends(get_db)
):
    """
    Get publication statistics
    """
    # Total publications
    total = db.query(Publication).count()
    
    # By type
    by_type = db.query(
        Publication.publication_type,
        func.count(Publication.id).label('count')
    ).group_by(Publication.publication_type).all()
    
    # By year
    by_year = db.query(
        Publication.year,
        func.count(Publication.id).label('count')
    ).group_by(Publication.year).order_by(Publication.year.desc()).limit(10).all()
    
    # Faculty publications
    faculty_pubs = db.query(Publication).filter(
        Publication.has_faculty_author == True
    ).count()
    
    # Average authors per publication
    avg_authors = db.query(func.avg(Publication.author_count)).scalar() or 0
    
    return {
        "total_publications": total,
        "faculty_publications": faculty_pubs,
        "average_authors_per_publication": round(float(avg_authors), 2),
        "publications_by_type": {
            pub_type: count for pub_type, count in by_type
        },
        "publications_by_year": {
            year: count for year, count in by_year
        }
    }


@router.get("/search", response_model=schemas.PaginatedResponse)
async def search_publications(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search publications by title, abstract, or keywords
    """
    # Use PostgreSQL full-text search or ILIKE for simple search
    search_term = f"%{q}%"
    
    query = db.query(Publication).filter(
        or_(
            Publication.title.ilike(search_term),
            Publication.abstract.ilike(search_term),
            Publication.keywords.ilike(search_term)
        )
    )
    
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    publications = query.order_by(Publication.year.desc()).offset(offset).limit(page_size).all()
    
    # Calculate metadata
    total_pages = (total + page_size - 1) // page_size
    
    items = [
        {
            "id": pub.id,
            "title": pub.title,
            "year": pub.year,
            "publication_type": pub.publication_type,
            "venue": pub.journal or pub.booktitle,
            "doi": pub.doi,
            "relevance_score": 1.0  # Can implement tf-idf later
        }
        for pub in publications
    ]
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/", response_model=schemas.PaginatedResponse)
async def list_publications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    year: Optional[int] = Query(None, description="Filter by year"),
    year_from: Optional[int] = Query(None, description="Filter from year"),
    year_to: Optional[int] = Query(None, description="Filter to year"),
    publication_type: Optional[str] = Query(None, description="Filter by type"),
    has_faculty: Optional[bool] = Query(None, description="Filter by faculty author"),
    sort_by: str = Query("year", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """
    List publications with pagination and filters
    """
    # Build query
    query = db.query(Publication)
    
    # Apply filters
    if year:
        query = query.filter(Publication.year == year)
    if year_from:
        query = query.filter(Publication.year >= year_from)
    if year_to:
        query = query.filter(Publication.year <= year_to)
    if publication_type:
        query = query.filter(Publication.publication_type == publication_type)
    if has_faculty is not None:
        query = query.filter(Publication.has_faculty_author == has_faculty)
    
    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(Publication, sort_by, Publication.year)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    publications = query.offset(offset).limit(page_size).all()
    
    # Calculate pagination metadata
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1
    
    # Convert to dict
    items = [
        {
            "id": pub.id,
            "title": pub.title,
            "year": pub.year,
            "publication_type": pub.publication_type,
            "venue": pub.journal or pub.booktitle,
            "doi": pub.doi,
            "author_count": pub.author_count,
            "has_faculty_author": pub.has_faculty_author
        }
        for pub in publications
    ]
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev
    }


@router.get("/{publication_id}", response_model=dict)
async def get_publication(
    publication_id: int,
    db: Session = Depends(get_db)
):
    """
    Get publication details by ID
    """
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with ID {publication_id} not found"
        )
    
    # Get authors
    authors = db.query(Author).join(
        PublicationAuthor,
        Author.id == PublicationAuthor.author_id
    ).filter(
        PublicationAuthor.publication_id == publication_id
    ).order_by(PublicationAuthor.author_position).all()
    
    # Clean booktitle/journal (remove + and newlines)
    venue = publication.journal or publication.booktitle
    if venue:
        venue = re.sub(r'\+\s*\n\s*', ' ', venue)  # Remove + and newlines
        venue = re.sub(r'\s+', ' ', venue).strip()  # Normalize whitespace
    
    return {
        "id": publication.id,
        "title": publication.title,
        "dblp_key": publication.dblp_key,
        "publication_type": publication.publication_type,
        "year": publication.year,
        "venue": venue,
        "journal": publication.journal,
        "booktitle": publication.booktitle,
        "volume": publication.volume,
        "number": publication.number,
        "pages": publication.pages,
        "publisher": publication.publisher,
        "doi": publication.doi,
        "url": publication.url,
        "abstract": publication.abstract,
        "author_count": publication.author_count,
        "has_faculty_author": publication.has_faculty_author,
        "source_pids": publication.source_pids,
        "authors": [
            {
                "id": author.id,
                "name": author.name,
                "is_faculty": author.is_faculty,
                "dblp_pid": author.dblp_pid,
                "designation": author.designation
            }
            for author in authors
        ],
        "created_at": publication.created_at,
        "updated_at": publication.updated_at
    }
