"""
Analytics API endpoints for system-wide statistics and trends.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract

from config.db_config import get_db
from models.db_models import (
    Publication, Author, Venue, Collaboration
)

router = APIRouter()


@router.get("/overview")
async def get_system_overview(db: Session = Depends(get_db)):
    """
    Get comprehensive system overview with key statistics.
    
    Returns:
    - Total counts for publications, authors, faculty, venues, collaborations
    - Publication distribution by type
    - Recent activity metrics
    """
    # Total counts
    total_publications = db.query(func.count(Publication.id)).scalar()
    total_authors = db.query(func.count(func.distinct(Author.name))).scalar()
    total_faculty = db.query(func.count(Author.id)).filter(Author.is_faculty == True).scalar()
    total_venues = db.query(func.count(Venue.id)).scalar()
    total_collaborations = db.query(func.count(Collaboration.id)).scalar()
    
    # Publications by type
    pubs_by_type = db.query(
        Publication.publication_type,
        func.count(Publication.id).label('count')
    ).group_by(Publication.publication_type).all()
    
    # Publications by year (last 10 years)
    pubs_by_year = db.query(
        Publication.year,
        func.count(Publication.id).label('count')
    ).group_by(
        Publication.year
    ).order_by(
        desc(Publication.year)
    ).limit(10).all()
    
    # Faculty with most publications
    from models.db_models import publication_authors
    top_faculty = db.query(
        Author.name,
        func.count(func.distinct(publication_authors.c.publication_id)).label('publication_count')
    ).join(
        publication_authors,
        Author.id == publication_authors.c.author_id
    ).filter(
        Author.is_faculty == True
    ).group_by(
        Author.id, Author.name
    ).order_by(
        desc('publication_count')
    ).limit(10).all()
    
    # Most active venues (from journal and booktitle fields)
    # Get journals
    top_journals = db.query(
        Publication.journal.label('venue'),
        func.count(Publication.id).label('publication_count')
    ).filter(
        Publication.journal.isnot(None),
        Publication.journal != ''
    ).group_by(
        Publication.journal
    ).order_by(
        desc('publication_count')
    ).limit(5).all()
    
    # Get conference venues (booktitle)
    top_conferences = db.query(
        Publication.booktitle.label('venue'),
        func.count(Publication.id).label('publication_count')
    ).filter(
        Publication.booktitle.isnot(None),
        Publication.booktitle != ''
    ).group_by(
        Publication.booktitle
    ).order_by(
        desc('publication_count')
    ).limit(5).all()
    
    # Combine top venues
    top_venues = []
    for venue in list(top_journals) + list(top_conferences):
        top_venues.append({
            "name": venue.venue[:100] if venue.venue else "Unknown",
            "publication_count": venue.publication_count
        })
    
    # Sort by count and take top 10
    top_venues = sorted(top_venues, key=lambda x: x['publication_count'], reverse=True)[:10]
    
    return {
        "totals": {
            "publications": total_publications or 0,
            "authors": total_authors or 0,
            "faculty": total_faculty or 0,
            "venues": total_venues or 0,
            "collaborations": total_collaborations or 0
        },
        "publications_by_type": {
            pub_type.publication_type: pub_type.count for pub_type in pubs_by_type
        },
        "publications_by_year": {
            year.year: year.count for year in pubs_by_year
        },
        "top_faculty": [
            {
                "name": faculty.name,
                "publication_count": faculty.publication_count
            }
            for faculty in top_faculty
        ],
        "top_venues": top_venues
    }


@router.get("/trends")
async def get_publication_trends(
    start_year: Optional[int] = Query(None, description="Start year for analysis"),
    end_year: Optional[int] = Query(None, description="End year for analysis"),
    db: Session = Depends(get_db)
):
    """
    Get publication trends over time.
    
    **Parameters:**
    - start_year: Start year (optional)
    - end_year: End year (optional)
    
    Returns yearly trends with:
    - Publications per year
    - Publications by type per year
    - Average authors per publication
    """
    query = db.query(Publication)
    
    # Apply year filters
    if start_year:
        query = query.filter(Publication.year >= start_year)
    if end_year:
        query = query.filter(Publication.year <= end_year)
    
    # Publications per year
    pubs_per_year = db.query(
        Publication.year,
        func.count(Publication.id).label('count')
    )
    if start_year:
        pubs_per_year = pubs_per_year.filter(Publication.year >= start_year)
    if end_year:
        pubs_per_year = pubs_per_year.filter(Publication.year <= end_year)
    
    pubs_per_year = pubs_per_year.group_by(
        Publication.year
    ).order_by(
        Publication.year
    ).all()
    
    # Publications by type per year
    pubs_by_type_year = db.query(
        Publication.year,
        Publication.publication_type,
        func.count(Publication.id).label('count')
    )
    if start_year:
        pubs_by_type_year = pubs_by_type_year.filter(Publication.year >= start_year)
    if end_year:
        pubs_by_type_year = pubs_by_type_year.filter(Publication.year <= end_year)
    
    pubs_by_type_year = pubs_by_type_year.group_by(
        Publication.year,
        Publication.publication_type
    ).order_by(
        Publication.year,
        Publication.publication_type
    ).all()
    
    # Average authors per publication per year
    avg_authors = db.query(
        Publication.year,
        func.avg(
            db.query(func.count(Author.id))
            .filter(Author.publication_id == Publication.id)
            .correlate(Publication)
            .scalar_subquery()
        ).label('avg_authors')
    )
    if start_year:
        avg_authors = avg_authors.filter(Publication.year >= start_year)
    if end_year:
        avg_authors = avg_authors.filter(Publication.year <= end_year)
    
    avg_authors = avg_authors.group_by(
        Publication.year
    ).order_by(
        Publication.year
    ).all()
    
    # Format response
    yearly_trends = {}
    for year, count in pubs_per_year:
        if year not in yearly_trends:
            yearly_trends[year] = {
                "total": count,
                "by_type": {},
                "avg_authors": 0.0
            }
        yearly_trends[year]["total"] = count
    
    for year, pub_type, count in pubs_by_type_year:
        if year in yearly_trends:
            yearly_trends[year]["by_type"][pub_type] = count
    
    for year, avg in avg_authors:
        if year in yearly_trends:
            yearly_trends[year]["avg_authors"] = round(float(avg) if avg else 0.0, 2)
    
    return {
        "trends": yearly_trends,
        "year_range": {
            "start": start_year or min(yearly_trends.keys()) if yearly_trends else None,
            "end": end_year or max(yearly_trends.keys()) if yearly_trends else None
        }
    }


@router.get("/collaboration-network")
async def get_collaboration_network(
    faculty_id: Optional[int] = Query(None, description="Filter by specific faculty member"),
    min_collaborations: int = Query(1, ge=1, description="Minimum collaboration count"),
    limit: int = Query(50, ge=1, le=500, description="Maximum nodes to return"),
    db: Session = Depends(get_db)
):
    """
    Get collaboration network data.
    
    **Parameters:**
    - faculty_id: Focus on specific faculty member (optional)
    - min_collaborations: Minimum number of collaborations (default: 1)
    - limit: Maximum nodes to return (default: 50, max: 500)
    
    Returns network nodes and edges for visualization.
    """
    query = db.query(
        Collaboration.faculty_id,
        Faculty.name.label('faculty_name'),
        Collaboration.collaborator_id,
        Collaboration.collaborator_name,
        func.count(Collaboration.id).label('collaboration_count')
    ).join(
        Faculty, Collaboration.faculty_id == Faculty.id
    ).group_by(
        Collaboration.faculty_id,
        Faculty.name,
        Collaboration.collaborator_id,
        Collaboration.collaborator_name
    )
    
    # Filter by faculty if specified
    if faculty_id:
        query = query.filter(Collaboration.faculty_id == faculty_id)
    
    # Filter by minimum collaborations
    query = query.having(func.count(Collaboration.id) >= min_collaborations)
    
    # Order by collaboration count and limit
    collaborations = query.order_by(
        desc('collaboration_count')
    ).limit(limit).all()
    
    # Build nodes and edges
    nodes = {}
    edges = []
    
    for collab in collaborations:
        # Add faculty node
        if collab.faculty_id not in nodes:
            nodes[collab.faculty_id] = {
                "id": collab.faculty_id,
                "name": collab.faculty_name,
                "type": "faculty"
            }
        
        # Add collaborator node
        collab_node_id = f"collab_{collab.collaborator_id}"
        if collab_node_id not in nodes:
            nodes[collab_node_id] = {
                "id": collab_node_id,
                "name": collab.collaborator_name,
                "type": "collaborator"
            }
        
        # Add edge
        edges.append({
            "source": collab.faculty_id,
            "target": collab_node_id,
            "weight": collab.collaboration_count
        })
    
    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "faculty_id": faculty_id,
            "min_collaborations": min_collaborations
        }
    }


@router.get("/research-areas")
async def get_research_areas(
    limit: int = Query(20, ge=1, le=100, description="Number of top keywords to return"),
    db: Session = Depends(get_db)
):
    """
    Identify top research areas based on publication keywords.
    
    **Parameters:**
    - limit: Number of top keywords to return (default: 20, max: 100)
    
    **Note:** This is a placeholder for future implementation.
    Currently returns basic type distribution as research categories.
    """
    # For now, return publication types as research categories
    # In future, this can be enhanced with actual keyword extraction
    research_categories = db.query(
        Publication.publication_type,
        func.count(Publication.id).label('count')
    ).group_by(
        Publication.publication_type
    ).order_by(
        desc('count')
    ).all()
    
    return {
        "research_categories": [
            {
                "category": cat.publication_type,
                "publication_count": cat.count
            }
            for cat in research_categories
        ],
        "note": "Enhanced keyword-based research area analysis will be implemented in future versions"
    }
