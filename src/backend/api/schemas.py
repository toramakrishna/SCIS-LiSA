"""
Pydantic Schemas for API Request/Response Models
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from enum import Enum

# Type variable for generic pagination
T = TypeVar('T')


# Enums
class PublicationType(str, Enum):
    """Publication types"""
    ARTICLE = "article"
    CONFERENCE = "conference"
    BOOK = "book"
    INPROCEEDINGS = "inproceedings"
    INCOLLECTION = "incollection"
    PHDTHESIS = "phdthesis"
    MASTERSTHESIS = "mastersthesis"
    OTHER = "other"


class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"


# Base schemas
class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Author schemas
class AuthorBase(BaseModel):
    """Base author schema"""
    name: str
    is_faculty: bool = False
    dblp_pid: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None


class AuthorCreate(AuthorBase):
    """Schema for creating an author"""
    pass


class AuthorUpdate(BaseModel):
    """Schema for updating an author"""
    name: Optional[str] = None
    is_faculty: Optional[bool] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None


class AuthorSchema(AuthorBase, TimestampMixin):
    """Author response schema"""
    id: int
    faculty_id: Optional[int] = None
    publication_count: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)


# Keep Author as alias for backward compatibility
Author = AuthorSchema


class AuthorDetail(AuthorSchema):
    """Detailed author schema with additional info"""
    collaborator_count: Optional[int] = 0
    first_publication_year: Optional[int] = None
    last_publication_year: Optional[int] = None


# Publication schemas
class PublicationBase(BaseModel):
    """Base publication schema"""
    title: str
    publication_type: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    booktitle: Optional[str] = None
    volume: Optional[str] = None
    number: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None


class PublicationSchema(PublicationBase, TimestampMixin):
    """Publication response schema"""
    id: int
    type: Optional[str] = None
    dblp_key: Optional[str] = None
    author_count: Optional[int] = 0
    has_faculty_author: bool = False
    source_pids: Optional[List[str]] = []
    authors: Optional[List[str]] = []  # List of author names for DBLP format
    editor: Optional[str] = None
    series: Optional[str] = None
    ee: Optional[str] = None
    is_verified: Optional[bool] = None  # Verification status for current faculty
    
    model_config = ConfigDict(from_attributes=True)


class PublicationDetail(PublicationSchema):
    """Detailed publication with authors"""
    author_objects: List[AuthorSchema] = []
    venue_name: Optional[str] = None


# Keep Publication as alias for backward compatibility
Publication = PublicationSchema


# Faculty schemas
class FacultyBase(BaseModel):
    """Base faculty schema"""
    name: str
    designation: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    dblp_pid: Optional[str] = None
    is_faculty: bool = True
    education: Optional[str] = None
    areas_of_interest: Optional[str] = None
    profile_page: Optional[str] = None
    status: Optional[str] = None


class FacultySchema(FacultyBase, TimestampMixin):
    """Faculty response schema"""
    id: int
    dblp_names: Optional[List[str]] = []
    dblp_urls: Optional[List[str]] = []
    publication_count: Optional[int] = 0
    total_publications: Optional[int] = 0
    h_index: Optional[int] = None
    scopus_author_id: Optional[str] = None
    scopus_url: Optional[str] = None
    homepage: Optional[str] = None
    research_interests: Optional[str] = None
    irins_profile: Optional[str] = None
    irins_url: Optional[str] = None
    irins_photo_url: Optional[str] = None
    photo_path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FacultyStatsSchema(BaseModel):
    """Faculty member statistics"""
    total_publications: int
    publications_by_type: dict[str, int]
    publications_by_year: dict[int, int]
    total_collaborators: int
    h_index: Optional[int] = None


# Venue schemas
class VenueBase(BaseModel):
    """Base venue schema"""
    name: str
    venue_type: str  # 'journal' or 'conference'
    publisher: Optional[str] = None


class VenueSchema(VenueBase, TimestampMixin):
    """Venue response schema"""
    id: int
    type: Optional[str] = None
    dblp_venue_id: Optional[str] = None
    publication_count: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)


# Collaboration schemas
class Collaboration(BaseModel):
    """Collaboration between authors"""
    id: int
    author1_id: int
    author2_id: int
    author1_name: str
    author2_name: str
    collaboration_count: int
    first_collaboration_year: Optional[int] = None
    last_collaboration_year: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# Statistics schemas
class PublicationStats(BaseModel):
    """Publication statistics"""
    total_publications: int
    publications_by_type: dict[str, int]
    publications_by_year: dict[int, int]
    average_authors_per_publication: float
    faculty_publications: int


class FacultyStats(BaseModel):
    """Faculty statistics"""
    total_faculty: int
    publications_per_faculty: dict[str, int]
    average_publications_per_faculty: float
    top_publishers: List[dict]


class AuthorStats(BaseModel):
    """Author statistics"""
    name: str
    publication_count: int
    collaboration_count: int
    first_publication_year: Optional[int] = None
    last_publication_year: Optional[int] = None
    active_years: int = 0
    publications_by_type: dict[str, int] = {}
    top_venues: List[dict] = []


# Pagination schemas
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        """Calculate total pages"""
        return (self.total + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1
    
    model_config = ConfigDict(from_attributes=True)


# Search schemas
class SearchParams(BaseModel):
    """Search parameters"""
    query: str = Field(..., min_length=1, description="Search query")
    fields: Optional[List[str]] = Field(None, description="Fields to search in")
    year_from: Optional[int] = Field(None, ge=1900, description="Start year")
    year_to: Optional[int] = Field(None, le=2100, description="End year")
    publication_type: Optional[str] = None
    is_faculty: Optional[bool] = None
    
    
class FilterParams(BaseModel):
    """Filter parameters for publications"""
    year: Optional[int] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    publication_type: Optional[str] = None
    has_faculty_author: Optional[bool] = None
    author_id: Optional[int] = None
    venue_id: Optional[int] = None


# Publication Attribution Verification
class AttributionVerificationRequest(BaseModel):
    """Request to verify/reject a publication attribution"""
    publication_id: int
    faculty_id: int
    is_verified: bool  # True = accept, False = reject
    verified_by: Optional[str] = None  # Email or identifier of verifier


class AttributionVerificationResponse(BaseModel):
    """Response after verifying attribution"""
    success: bool
    message: str
    publication_id: int
    faculty_id: int
    is_verified: bool
    journal: Optional[str] = None
    booktitle: Optional[str] = None


# Student schemas
class StudentBase(BaseModel):
    """Base student schema"""
    registration_number: str
    name: str
    semester: Optional[int] = None
    program: Optional[str] = None
    school_name: Optional[str] = None
    programme_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class StudentCreate(StudentBase):
    """Schema for creating a student"""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating a student"""
    name: Optional[str] = None
    semester: Optional[int] = None
    program: Optional[str] = None
    school_name: Optional[str] = None
    programme_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class StudentSchema(StudentBase, TimestampMixin):
    """Student response schema"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# Keep Student as alias
Student = StudentSchema

