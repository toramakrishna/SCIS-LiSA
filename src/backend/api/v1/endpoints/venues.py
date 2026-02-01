"""
Venues API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import re

from config.db_config import get_db
from models.db_models import Venue, Publication
from api.schemas import VenueSchema, PaginatedResponse, PublicationSchema

router = APIRouter()


def clean_venue_name(venue_name: str) -> str:
    """Clean venue name by removing BibTeX continuation markers and normalizing whitespace."""
    if not venue_name:
        return venue_name
    # Remove + continuation markers and newlines
    cleaned = re.sub(r'\+\s*\n\s*', ' ', venue_name)
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


@router.get("/", response_model=PaginatedResponse[VenueSchema])
async def list_venues(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    venue_type: Optional[str] = Query(None, description="Filter by venue type (journal/conference)"),
    db: Session = Depends(get_db)
):
    """
    List all publication venues with pagination.
    
    **Filters:**
    - venue_type: Filter by type (journal, conference, etc.)
    
    **Pagination:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    
    Returns venues sorted by publication count (descending).
    """
    query = db.query(
        Venue,
        func.count(Publication.id).label('publication_count')
    ).outerjoin(
        Publication, Venue.id == Publication.venue_id
    ).group_by(
        Venue.id
    )
    
    # Apply filters
    if venue_type:
        query = query.filter(Venue.type.ilike(f"%{venue_type}%"))
    
    # Order by publication count
    query = query.order_by(desc('publication_count'))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()
    
    # Format response with cleaned names
    items = []
    for venue, pub_count in results:
        venue_dict = {
            "id": venue.id,
            "name": clean_venue_name(venue.name),
            "type": venue.type,
            "dblp_venue_id": venue.dblp_venue_id,
            "publication_count": pub_count
        }
        items.append(venue_dict)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/search/")
async def search_venues(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for venues by name.
    
    **Parameters:**
    - q: Search query (searches in venue name)
    - page: Page number
    - page_size: Items per page
    """
    search_pattern = f"%{q}%"
    
    query = db.query(
        Venue,
        func.count(Publication.id).label('publication_count')
    ).outerjoin(
        Publication, Venue.id == Publication.venue_id
    ).filter(
        Venue.name.ilike(search_pattern)
    ).group_by(
        Venue.id
    ).order_by(
        desc('publication_count')
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()
    
    # Format response with cleaned names
    items = []
    for venue, pub_count in results:
        venue_dict = {
            "id": venue.id,
            "name": clean_venue_name(venue.name),
            "type": venue.type,
            "dblp_venue_id": venue.dblp_venue_id,
            "publication_count": pub_count
        }
        items.append(venue_dict)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{venue_id}")
async def get_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific venue.
    
    Includes venue details and publication count.
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Get publication count
    pub_count = db.query(func.count(Publication.id)).filter(
        Publication.venue_id == venue_id
    ).scalar()
    
    return {
        "id": venue.id,
        "name": clean_venue_name(venue.name),
        "type": venue.type,
        "dblp_venue_id": venue.dblp_venue_id,
        "publication_count": pub_count or 0
    }


@router.get("/{venue_id}/publications", response_model=PaginatedResponse[PublicationSchema])
async def get_venue_publications(
    venue_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db)
):
    """
    Get all publications from a specific venue.
    
    **Parameters:**
    - venue_id: Venue ID
    - year: Optional year filter
    - page: Page number
    - page_size: Items per page
    """
    # Verify venue exists
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Build query
    query = db.query(Publication).filter(Publication.venue_id == venue_id)
    
    # Apply year filter
    if year:
        query = query.filter(Publication.year == year)
    
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


@router.get("/top/")
async def get_top_venues(
    limit: int = Query(10, ge=1, le=100, description="Number of top venues to return"),
    venue_type: Optional[str] = Query(None, description="Filter by venue type"),
    db: Session = Depends(get_db)
):
    """
    Get top venues by publication count.
    
    **Parameters:**
    - limit: Number of venues to return (default: 10, max: 100)
    - venue_type: Filter by type (journal, conference, etc.)
    """
    query = db.query(
        Venue,
        func.count(Publication.id).label('publication_count')
    ).join(
        Publication, Venue.id == Publication.venue_id
    ).group_by(
        Venue.id
    )
    
    # Apply type filter
    if venue_type:
        query = query.filter(Venue.type.ilike(f"%{venue_type}%"))
    
    # Order by publication count and apply limit
    results = query.order_by(desc('publication_count')).limit(limit).all()
    
    return {
        "top_venues": [
            {
                "id": venue.id,
                "name": clean_venue_name(venue.name),
                "type": venue.type,
                "dblp_venue_id": venue.dblp_venue_id,
                "publication_count": pub_count
            }
            for venue, pub_count in results
        ],
        "limit": limit
    }
