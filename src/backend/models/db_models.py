"""
Enhanced Database Models for SCISLiSA
Optimized schema for efficient querying and analytics
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean, Index, UniqueConstraint, Float, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from config.db_config import Base

# Association table for many-to-many relationship between publications and authors
publication_authors = Table(
    'publication_authors',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('publication_id', Integer, ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
    Column('author_id', Integer, ForeignKey('authors.id', ondelete='CASCADE'), nullable=False),
    Column('author_position', Integer),  # Position in author list (1st, 2nd, etc.)
    Column('created_at', DateTime, default=datetime.utcnow),
    UniqueConstraint('publication_id', 'author_id', name='uq_pub_author'),
    Index('idx_pub_authors_pub', 'publication_id'),
    Index('idx_pub_authors_author', 'author_id')
)


class Author(Base):
    """
    Author model - represents faculty members and co-authors
    """
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)  # Increased from 255 to 500
    normalized_name = Column(String(500), index=True)  # For deduplication
    dblp_pid = Column(String(100), index=True)  # Not unique as same person may have multiple PIDs
    dblp_urlpt = Column(String(255))
    is_faculty = Column(Boolean, default=False, index=True)
    email = Column(String(255))
    department = Column(String(255), default='SCIS')
    designation = Column(String(255))
    phone = Column(String(50))
    
    # Statistics
    total_publications = Column(Integer, default=0)
    total_collaborations = Column(Integer, default=0)
    h_index = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    publications = relationship(
        'Publication',
        secondary=publication_authors,
        back_populates='authors',
        lazy='dynamic'
    )
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_author_name_faculty', 'name', 'is_faculty'),
        Index('idx_author_normalized', 'normalized_name'),
    )
    
    def __repr__(self):
        return f"<Author(name='{self.name}', dblp_pid='{self.dblp_pid}', is_faculty={self.is_faculty})>"


class Publication(Base):
    """
    Publication model - represents research papers, articles, etc.
    """
    __tablename__ = 'publications'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False, index=True)
    normalized_title = Column(Text)  # For deduplication
    dblp_key = Column(String(255), unique=True, index=True, nullable=False)  # Primary deduplication key
    publication_type = Column(String(50), index=True)  # article, inproceedings, book, etc.
    year = Column(Integer, index=True)
    
    # Publication venue details
    journal = Column(String(500))
    booktitle = Column(String(500))
    volume = Column(String(50))
    number = Column(String(50))
    pages = Column(String(100))
    publisher = Column(String(255))
    series = Column(String(255))
    
    # Editors (for proceedings)
    editor = Column(Text)
    
    # URLs and identifiers
    url = Column(Text)
    doi = Column(String(255), index=True)  # Also used for deduplication
    ee = Column(Text)
    biburl = Column(Text)
    bibsource = Column(String(255))
    
    # Additional metadata
    abstract = Column(Text)
    keywords = Column(Text)
    timestamp = Column(String(100))
    
    # Analytics fields
    citation_count = Column(Integer, default=0)
    has_faculty_author = Column(Boolean, default=False, index=True)
    author_count = Column(Integer, default=0)
    
    # Multi-PID tracking for co-authored papers between faculty
    source_pid = Column(String(100))  # Primary source PID (first file this appeared in)
    source_pids = Column(ARRAY(String))  # All faculty PIDs for this publication
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    authors = relationship(
        'Author',
        secondary=publication_authors,
        back_populates='publications',
        lazy='dynamic'
    )
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_pub_year_type', 'year', 'publication_type'),
        Index('idx_pub_faculty', 'has_faculty_author', 'year'),
        Index('idx_pub_journal', 'journal'),
        Index('idx_pub_doi', 'doi'),
    )
    
    def __repr__(self):
        return f"<Publication(title='{self.title[:50]}...', year={self.year}, type={self.publication_type})>"


class Collaboration(Base):
    """
    Collaboration network - represents co-authorship relationships
    Optimized for network analysis queries
    """
    __tablename__ = 'collaborations'
    
    id = Column(Integer, primary_key=True, index=True)
    author1_id = Column(Integer, ForeignKey('authors.id', ondelete='CASCADE'), nullable=False)
    author2_id = Column(Integer, ForeignKey('authors.id', ondelete='CASCADE'), nullable=False)
    collaboration_count = Column(Integer, default=1)
    first_collaboration_year = Column(Integer)
    last_collaboration_year = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique pairwise collaborations (bidirectional handled by constraint)
    __table_args__ = (
        UniqueConstraint('author1_id', 'author2_id', name='uq_collaboration'),
        Index('idx_collab_author1', 'author1_id'),
        Index('idx_collab_author2', 'author2_id'),
        Index('idx_collab_count', 'collaboration_count'),
    )
    
    def __repr__(self):
        return f"<Collaboration(author1={self.author1_id}, author2={self.author2_id}, count={self.collaboration_count})>"


class Venue(Base):
    """
    Publication venues (journals/conferences) for analytics
    """
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), unique=True, nullable=False, index=True)
    venue_type = Column(String(50), index=True)  # journal, conference
    abbreviation = Column(String(100))
    publisher = Column(String(255))
    
    # Statistics
    total_publications = Column(Integer, default=0)
    faculty_publications = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_venue_type_pubs', 'venue_type', 'total_publications'),
    )
    
    def __repr__(self):
        return f"<Venue(name='{self.name}', type={self.venue_type})>"


class DataSource(Base):
    """
    Track data sources and synchronization
    """
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), unique=True, nullable=False)  # DBLP, Scopus, etc.
    last_sync = Column(DateTime)
    total_records = Column(Integer, default=0)
    status = Column(String(50))  # active, inactive, error
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DataSource(name='{self.source_name}', last_sync={self.last_sync})>"


class PublicationStatistics(Base):
    """
    Pre-computed statistics for fast dashboard queries
    """
    __tablename__ = 'publication_statistics'
    
    id = Column(Integer, primary_key=True, index=True)
    stat_type = Column(String(100), nullable=False, index=True)  # yearly, by_venue, by_author, etc.
    stat_key = Column(String(255), nullable=False)  # year number, venue name, author id, etc.
    stat_value = Column(Float)
    additional_data = Column(Text)  # JSON for complex stats
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('stat_type', 'stat_key', name='uq_stat'),
        Index('idx_stat_type_key', 'stat_type', 'stat_key'),
    )
    
    def __repr__(self):
        return f"<PublicationStatistics(type='{self.stat_type}', key='{self.stat_key}', value={self.stat_value})>"
