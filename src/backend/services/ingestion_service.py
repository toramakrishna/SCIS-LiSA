"""
Database Ingestion Service
Loads parsed BibTeX data into PostgreSQL with duplicate prevention
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db_config import SessionLocal, init_postgres_db, engine
from models.db_models import Author, Publication, Collaboration, Venue, DataSource, publication_authors
from parsers.bibtex_parser import BibTeXParser
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseIngestionService:
    """
    Service for ingesting publications into database with duplicate prevention
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.author_cache = {}  # Cache for author lookups {normalized_name: Author}
        self.venue_cache = {}   # Cache for venue lookups {name: Venue}
        self.stats = {
            'publications_added': 0,
            'publications_skipped': 0,
            'authors_added': 0,
            'authors_updated': 0,
            'collaborations_added': 0,
            'venues_added': 0,
            'errors': 0
        }
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize author name for consistent matching"""
        if not name:
            return ""
        # Remove extra whitespace
        name = ' '.join(name.split())
        # Convert to lowercase
        name = name.lower()
        # Remove dots and commas
        name = name.replace('.', '').replace(',', '')
        return name.strip()
    
    def get_or_create_author(self, author_name: str, is_faculty: bool = False,
                            dblp_pid: Optional[str] = None,
                            faculty_data: Optional[Dict] = None) -> Author:
        """
        Get existing author or create new one
        """
        normalized = self.normalize_name(author_name)
        
        # Check cache first
        cache_key = f"{normalized}_{dblp_pid or ''}"
        if cache_key in self.author_cache:
            return self.author_cache[cache_key]
        
        # Try to find existing author by normalized name or PID
        query = self.db.query(Author)
        if dblp_pid:
            author = query.filter(Author.dblp_pid == dblp_pid).first()
        else:
            author = query.filter(Author.normalized_name == normalized).first()
        
        if author:
            # Update if it's faculty
            if is_faculty and not author.is_faculty:
                author.is_faculty = True
                if faculty_data:
                    author.email = faculty_data.get('email') or author.email
                    author.phone = faculty_data.get('phone') or author.phone
                    author.designation = faculty_data.get('designation') or author.designation
                self.stats['authors_updated'] += 1
        else:
            # Create new author
            author = Author(
                name=author_name,
                normalized_name=normalized,
                dblp_pid=dblp_pid,
                is_faculty=is_faculty,
                email=faculty_data.get('email') if faculty_data else None,
                phone=faculty_data.get('phone') if faculty_data else None,
                designation=faculty_data.get('designation') if faculty_data else None,
                department='SCIS' if is_faculty else None
            )
            self.db.add(author)
            self.db.flush()  # Get the ID
            self.stats['authors_added'] += 1
            logger.debug(f"Created new author: {author_name} (faculty={is_faculty})")
        
        # Cache the author
        self.author_cache[cache_key] = author
        return author
    
    def get_or_create_venue(self, venue_name: str, venue_type: str,
                           publisher: Optional[str] = None) -> Optional[Venue]:
        """
        Get existing venue or create new one
        """
        if not venue_name:
            return None
        
        # Check cache
        if venue_name in self.venue_cache:
            return self.venue_cache[venue_name]
        
        # Try to find existing
        venue = self.db.query(Venue).filter(Venue.name == venue_name).first()
        
        if not venue:
            venue = Venue(
                name=venue_name,
                venue_type=venue_type,
                publisher=publisher
            )
            self.db.add(venue)
            self.db.flush()
            self.stats['venues_added'] += 1
            logger.debug(f"Created new venue: {venue_name}")
        
        self.venue_cache[venue_name] = venue
        return venue
    
    def create_publication(self, pub_data: Dict, faculty_mapping: Dict[str, Dict]) -> bool:
        """
        Create publication and associate with authors
        Returns True if created, False if skipped (duplicate)
        """
        try:
            dblp_key = pub_data['dblp_key']
            
            # Check if publication already exists
            existing = self.db.query(Publication).filter(
                Publication.dblp_key == dblp_key
            ).first()
            
            if existing:
                self.stats['publications_skipped'] += 1
                logger.debug(f"Skipping duplicate publication: {dblp_key}")
                return False
            
            # Determine venue
            venue = None
            if pub_data['journal']:
                venue = self.get_or_create_venue(pub_data['journal'], 'journal', pub_data.get('publisher'))
            elif pub_data['booktitle']:
                venue = self.get_or_create_venue(pub_data['booktitle'], 'conference', pub_data.get('publisher'))
            
            # Create publication
            publication = Publication(
                title=pub_data['title'],
                normalized_title=pub_data['normalized_title'],
                dblp_key=dblp_key,
                publication_type=pub_data['publication_type'],
                year=pub_data['year'],
                journal=pub_data['journal'],
                booktitle=pub_data['booktitle'],
                volume=pub_data['volume'],
                number=pub_data['number'],
                pages=pub_data['pages'],
                publisher=pub_data['publisher'],
                series=pub_data['series'],
                editor=', '.join(pub_data['editors']) if pub_data['editors'] else None,
                url=pub_data['url'],
                doi=pub_data['doi'],
                ee=pub_data['ee'],
                biburl=pub_data['biburl'],
                bibsource=pub_data['bibsource'],
                timestamp=pub_data['timestamp'],
                abstract=pub_data['abstract'],
                keywords=pub_data['keywords'],
                author_count=len(pub_data['authors']),
                has_faculty_author=False,  # Will update below
                source_pid=pub_data.get('source_pid'),  # Primary source PID
                source_pids=pub_data.get('source_pids', [])  # All faculty PIDs
            )
            
            self.db.add(publication)
            self.db.flush()  # Get the ID
            
            # Process authors and create associations
            authors_in_pub = []
            has_faculty = False
            
            # Get PID mapping for faculty identification
            pid_mapping = faculty_mapping.get('by_pid', {})
            source_pids = pub_data.get('source_pids', [])
            
            # Check if ANY of the source PIDs belong to faculty members
            faculty_pids_in_pub = set(source_pids) & set(pid_mapping.keys())
            
            if faculty_pids_in_pub:
                has_faculty = True
            
            for position, author_name in enumerate(pub_data['authors'], 1):
                # CORRECTED APPROACH: Only mark an author as faculty if we can match them
                # by name with a faculty member in this publication's source PIDs
                is_faculty = False
                dblp_pid = None
                faculty_data = None
                
                # Normalize author name for matching
                normalized_author = self.normalize_name(author_name)
                
                # Check each faculty PID in this publication
                for fac_pid in faculty_pids_in_pub:
                    fac_info = pid_mapping[fac_pid]
                    fac_name = fac_info.get('faculty_name', '')
                    normalized_fac_name = self.normalize_name(fac_name)
                    
                    # If this author's name matches this faculty member's name,
                    # assign the faculty data
                    if normalized_author == normalized_fac_name:
                        is_faculty = True
                        dblp_pid = fac_pid
                        faculty_data = fac_info
                        break  # Found the match, stop checking
                
                # Get or create author
                author = self.get_or_create_author(
                    author_name,
                    is_faculty=is_faculty,
                    dblp_pid=dblp_pid,
                    faculty_data=faculty_data
                )
                
                # Skip if this author is already in this publication (duplicate author entry)
                if author in authors_in_pub:
                    logger.debug(f"Skipping duplicate author '{author_name}' in publication {pub_data.get('dblp_key')}")
                    continue
                    
                authors_in_pub.append(author)
                
                # Create publication-author association
                self.db.execute(
                    publication_authors.insert().values(
                        publication_id=publication.id,
                        author_id=author.id,
                        author_position=position
                    )
                )
            
            # Update publication faculty flag
            publication.has_faculty_author = has_faculty
            
            # Update venue statistics
            if venue:
                venue.total_publications += 1
                if has_faculty:
                    venue.faculty_publications += 1
            
            # Create collaborations
            self._create_collaborations(authors_in_pub, pub_data['year'])
            
            # Update author statistics
            for author in authors_in_pub:
                author.total_publications = self.db.query(Publication).join(
                    publication_authors
                ).filter(publication_authors.c.author_id == author.id).count()
            
            self.stats['publications_added'] += 1
            logger.debug(f"Added publication: {pub_data['title'][:50]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating publication {pub_data.get('dblp_key')}: {e}")
            self.stats['errors'] += 1
            return False
    
    def _create_collaborations(self, authors: List[Author], year: Optional[int]):
        """
        Create or update collaboration records for co-authors
        """
        if len(authors) < 2:
            return
        
        for i, author1 in enumerate(authors):
            for author2 in authors[i+1:]:
                # Ensure consistent ordering (smaller ID first)
                a1_id, a2_id = (author1.id, author2.id) if author1.id < author2.id else (author2.id, author1.id)
                
                # Check if collaboration exists
                collab = self.db.query(Collaboration).filter(
                    and_(
                        Collaboration.author1_id == a1_id,
                        Collaboration.author2_id == a2_id
                    )
                ).first()
                
                if collab:
                    # Update existing
                    collab.collaboration_count += 1
                    if year:
                        if not collab.first_collaboration_year or year < collab.first_collaboration_year:
                            collab.first_collaboration_year = year
                        if not collab.last_collaboration_year or year > collab.last_collaboration_year:
                            collab.last_collaboration_year = year
                else:
                    # Create new - wrap in try/except to handle race conditions
                    try:
                        collab = Collaboration(
                            author1_id=a1_id,
                            author2_id=a2_id,
                            collaboration_count=1,
                            first_collaboration_year=year,
                            last_collaboration_year=year
                        )
                        self.db.add(collab)
                        self.db.flush()  # Flush immediately
                        self.stats['collaborations_added'] += 1
                    except Exception as e:
                        # Handle duplicate - query again
                        self.db.rollback()
                        collab = self.db.query(Collaboration).filter(
                            and_(
                                Collaboration.author1_id == a1_id,
                                Collaboration.author2_id == a2_id
                            )
                        ).first()
                        if collab:
                            collab.collaboration_count += 1
                            if year:
                                if not collab.first_collaboration_year or year < collab.first_collaboration_year:
                                    collab.first_collaboration_year = year
                                if not collab.last_collaboration_year or year > collab.last_collaboration_year:
                                    collab.last_collaboration_year = year
                
                # Update author collaboration counts
                author1.total_collaborations = self.db.query(Collaboration).filter(
                    or_(Collaboration.author1_id == author1.id, Collaboration.author2_id == author1.id)
                ).count()
                author2.total_collaborations = self.db.query(Collaboration).filter(
                    or_(Collaboration.author1_id == author2.id, Collaboration.author2_id == author2.id)
                ).count()
    
    def load_faculty_mapping(self, json_path: str) -> Dict[str, Dict]:
        """
        Load faculty mapping from JSON file
        Returns both name-to-data and PID-to-faculty mappings
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            faculty_list = json.load(f)
        
        name_mapping = {}
        pid_mapping = {}  # PID -> faculty info
        
        for faculty in faculty_list:
            if faculty.get('dblp_matched'):
                faculty_info = {
                    'faculty_name': faculty['faculty_name'],
                    'dblp_pid': faculty.get('dblp_pid'),
                    'email': faculty.get('email'),
                    'phone': faculty.get('phone'),
                    'designation': faculty.get('designation'),
                    'department': faculty.get('department')
                }
                
                name_mapping[faculty['faculty_name']] = faculty_info
                
                # Map PID to faculty (handle multiple PIDs per faculty)
                pid = faculty.get('dblp_pid')
                if pid:
                    pid_mapping[pid] = faculty_info
        
        return {'by_name': name_mapping, 'by_pid': pid_mapping}
    
    def ingest_publications(self, publications: List[Dict], faculty_mapping: Dict[str, Dict]):
        """
        Ingest all publications into database
        """
        total = len(publications)
        logger.info(f"Starting ingestion of {total} publications...")
        
        for i, pub_data in enumerate(publications, 1):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{total} publications processed")
                try:
                    self.db.commit()  # Periodic commits
                except Exception as e:
                    logger.error(f"Error during commit at publication {i}: {e}")
                    self.db.rollback()
            
            self.create_publication(pub_data, faculty_mapping)
        
        # Final commit
        try:
            self.db.commit()
            logger.info("Final commit successful")
        except Exception as e:
            logger.error(f"Error during final commit: {e}")
            self.db.rollback()
        
        logger.info("Ingestion complete!")
    
    def update_data_source(self, source_name: str = 'DBLP'):
        """
        Update data source sync record
        """
        data_source = self.db.query(DataSource).filter(
            DataSource.source_name == source_name
        ).first()
        
        if data_source:
            data_source.last_sync = datetime.utcnow()
            data_source.total_records = self.stats['publications_added']
            data_source.status = 'active'
        else:
            data_source = DataSource(
                source_name=source_name,
                last_sync=datetime.utcnow(),
                total_records=self.stats['publications_added'],
                status='active'
            )
            self.db.add(data_source)
        
        self.db.commit()
    
    def print_stats(self):
        """Print ingestion statistics"""
        print(f"\n{'='*80}")
        print(f"INGESTION STATISTICS")
        print(f"{'='*80}")
        print(f"Publications Added: {self.stats['publications_added']}")
        print(f"Publications Skipped (Duplicates): {self.stats['publications_skipped']}")
        print(f"Authors Added: {self.stats['authors_added']}")
        print(f"Authors Updated: {self.stats['authors_updated']}")
        print(f"Venues Added: {self.stats['venues_added']}")
        print(f"Collaborations Created: {self.stats['collaborations_added']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"{'='*80}\n")


def main():
    """Main ingestion process"""
    # Paths
    current_dir = Path(__file__).parent.parent
    project_root = current_dir.parent.parent
    bib_directory = project_root / 'src' / 'dataset' / 'dblp'
    faculty_json = current_dir / 'references' / 'dblp' / 'faculty_dblp_matched.json'
    
    logger.info("="*80)
    logger.info("DBLP DATA INGESTION PROCESS")
    logger.info("="*80)
    
    # Step 1: Initialize database
    logger.info("Step 1: Initializing database schema...")
    init_postgres_db()
    logger.info("✓ Database schema initialized")
    
    # Step 2: Parse BibTeX files
    logger.info("Step 2: Parsing BibTeX files...")
    parser = BibTeXParser()
    results = parser.parse_all_bib_files(str(bib_directory))
    publications = results['publications']
    stats = results['stats']
    
    logger.info(f"✓ Parsed {stats['unique_publications']} unique publications from {stats['successful_files']} files")
    logger.info(f"  Removed {stats['duplicates_removed']} duplicates")
    
    # Step 3: Load faculty mapping
    logger.info("Step 3: Loading faculty mapping...")
    db = SessionLocal()
    service = DatabaseIngestionService(db)
    faculty_mapping = service.load_faculty_mapping(str(faculty_json))
    logger.info(f"✓ Loaded {len(faculty_mapping['by_name'])} faculty members")
    
    # Step 4: Ingest data
    logger.info("Step 4: Ingesting data into PostgreSQL...")
    service.ingest_publications(publications, faculty_mapping)
    logger.info("✓ Data ingestion complete")
    
    # Step 5: Update data source
    logger.info("Step 5: Updating data source record...")
    service.update_data_source('DBLP')
    logger.info("✓ Data source updated")
    
    # Print final statistics
    service.print_stats()
    
    db.close()
    logger.info("Database connection closed")


if __name__ == "__main__":
    main()
