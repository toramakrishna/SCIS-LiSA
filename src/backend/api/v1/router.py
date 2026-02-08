"""
API v1 Main Router
Combines all API endpoint routers
"""

from fastapi import APIRouter
from api.v1.endpoints import publications, faculty, authors, venues, analytics, mcp, admin, students

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    publications.router,
    prefix="/publications",
    tags=["Publications"]
)

api_router.include_router(
    faculty.router,
    prefix="/faculty",
    tags=["Faculty"]
)

api_router.include_router(
    authors.router,
    prefix="/authors",
    tags=["Authors"]
)

api_router.include_router(
    venues.router,
    prefix="/venues",
    tags=["Venues"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    students.router,
    prefix="/students",
    tags=["Students"]
)

api_router.include_router(
    mcp.router,
    tags=["MCP Analytics"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)
