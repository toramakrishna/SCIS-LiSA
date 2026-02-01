"""
Authors API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from config.db_config import get_db
from models.db_models import Author, Publication
from api.schemas import AuthorSchema, PaginatedResponse, PublicationSchema

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[AuthorSchema])
async def list_authors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_faculty: Optional[bool] = Query(None, description="Filter by faculty status"),
    db: Session = Depends(get_db)
):
    """
    List all unique authors with pagination.
    
    **Filters:**
    - is_faculty: Filter by faculty status (true shows only faculty authors)
    
    **Pagination:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    
    **Note:** Returns authors with publication counts.
    """
    from models.db_models import publication_authors
    
    # Query authors with publication counts
    subquery = db.query(
        publication_authors.c.author_id,
        func.count(publication_authors.c.publication_id).label('pub_count')
    ).group_by(publication_authors.c.author_id).subquery()
    
    query = db.query(
        Author,
        func.coalesce(subquery.c.pub_count, 0).label('publication_count')
    ).outerjoin(subquery, Author.id == subquery.c.author_id)
    
    # Apply filters
    if is_faculty is not None:
        query = query.filter(Author.is_faculty == is_faculty)
    
    # Order by publication count descending
    query = query.order_by(desc('publication_count'))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    authors = query.offset(offset).limit(page_size).all()
    
    # Format response
    items = [
        {
            "id": author[0].id,
            "name": author[0].name,
            "is_faculty": author[0].is_faculty,
            "dblp_pid": author[0].dblp_pid,
            "publication_count": author[1]
        }
        for author in authors
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/search/")
async def search_authors(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for authors by name.
    
    **Parameters:**
    - q: Search query (searches in author name)
    - page: Page number
    - page_size: Items per page
    
    Returns authors matching the search query with publication counts.
    """
    from models.db_models import publication_authors
    
    # Search in author names
    search_pattern = f"%{q}%"
    
    # Subquery for publication counts
    subquery = db.query(
        publication_authors.c.author_id,
        func.count(publication_authors.c.publication_id).label('pub_count')
    ).group_by(publication_authors.c.author_id).subquery()
    
    query = db.query(
        Author,
        func.coalesce(subquery.c.pub_count, 0).label('publication_count')
    ).outerjoin(subquery, Author.id == subquery.c.author_id).filter(
        Author.name.ilike(search_pattern)
    ).order_by(
        desc('publication_count')
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    authors = query.offset(offset).limit(page_size).all()
    
    # Format response
    items = [
        {
            "id": author[0].id,
            "name": author[0].name,
            "is_faculty": author[0].is_faculty,
            "dblp_pid": author[0].dblp_pid,
            "publication_count": author[1]
        }
        for author in authors
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{author_name}/publications", response_model=PaginatedResponse[PublicationSchema])
async def get_author_publications(
    author_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db)
):
    """
    Get all publications for a specific author by name.
    
    **Parameters:**
    - author_name: Exact author name
    - year: Optional year filter
    - page: Page number
    - page_size: Items per page
    """
    from models.db_models import publication_authors
    
    # Build query - join through publication_authors association table
    query = db.query(Publication).join(
        publication_authors, Publication.id == publication_authors.c.publication_id
    ).join(
        Author, Author.id == publication_authors.c.author_id
    ).filter(
        Author.name == author_name
    )
    
    # Apply year filter
    if year:
        query = query.filter(Publication.year == year)
    
    # Order by year descending
    query = query.order_by(desc(Publication.year))
    
    # Get total count
    total = query.count()
    
    if total == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No publications found for author: {author_name}"
        )
    
    # Apply pagination
    offset = (page - 1) * page_size
    publications = query.offset(offset).limit(page_size).all()
    
    return PaginatedResponse(
        items=publications,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/top/")
async def get_top_authors(
    limit: int = Query(10, ge=1, le=100, description="Number of top authors to return"),
    is_faculty: Optional[bool] = Query(None, description="Filter by faculty status"),
    db: Session = Depends(get_db)
):
    """
    Get top authors by publication count.
    
    **Parameters:**
    - limit: Number of authors to return (default: 10, max: 100)
    - is_faculty: Filter by faculty status
    
    Returns authors sorted by publication count (descending).
    """
    query = db.query(
        Author.name,
        Author.faculty_id,
        func.count(func.distinct(Author.publication_id)).label('publication_count')
    ).group_by(
        Author.name,
        Author.faculty_id
    )
    
    # Apply faculty filter
    if is_faculty is not None:
        if is_faculty:
            query = query.filter(Author.faculty_id.isnot(None))
        else:
            query = query.filter(Author.faculty_id.is_(None))
    
    # Order by publication count and apply limit
    authors = query.order_by(desc('publication_count')).limit(limit).all()
    
    return {
        "top_authors": [
            {
                "name": author.name,
                "faculty_id": author.faculty_id,
                "publication_count": author.publication_count
            }
            for author in authors
        ],
        "limit": limit
    }
