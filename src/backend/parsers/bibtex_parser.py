"""
BibTeX Parser for DBLP Publications
Parses .bib files and extracts structured data with duplicate detection
"""
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import os
import re
from typing import Dict, List, Set, Tuple, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BibTeXParser:
    """
    Parser for BibTeX files with duplicate detection
    """
    
    def __init__(self):
        self.seen_keys = set()  # Track DBLP keys for deduplication
        self.seen_dois = set()  # Track DOIs for deduplication
        self.seen_titles = set()  # Track normalized titles for deduplication
        
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison (remove extra spaces, lowercase, etc.)
        """
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.strip()
    
    @staticmethod
    def normalize_author_name(name: str) -> str:
        """
        Normalize author name for consistent matching
        """
        if not name:
            return ""
        # Remove extra whitespace
        name = ' '.join(name.split())
        # Convert to lowercase for comparison
        name = name.lower()
        # Remove dots and common titles
        name = name.replace('.', '').replace(',', '')
        titles = ['dr', 'prof', 'mr', 'ms', 'mrs']
        for title in titles:
            name = name.replace(title + ' ', '')
        return name.strip()
    
    @staticmethod
    def parse_authors(author_str: str) -> List[str]:
        """
        Parse author string and return list of author names
        """
        if not author_str:
            return []
        
        # Replace newlines with spaces first
        author_str = author_str.replace('\n', ' ')
        
        # Split by 'and' (case-insensitive, with word boundaries)
        import re
        authors = re.split(r'\s+and\s+', author_str, flags=re.IGNORECASE)
        
        # Clean up each author name
        cleaned_authors = []
        for author in authors:
            author = ' '.join(author.split())  # Remove extra whitespace
            if author:
                cleaned_authors.append(author)
        
        return cleaned_authors
    
    @staticmethod
    def extract_publication_type(entry_type: str) -> str:
        """
        Map BibTeX entry type to our publication type
        """
        type_mapping = {
            'article': 'article',
            'inproceedings': 'conference',
            'proceedings': 'proceedings',
            'book': 'book',
            'incollection': 'book_chapter',
            'phdthesis': 'thesis',
            'mastersthesis': 'thesis',
            'techreport': 'technical_report',
            'misc': 'misc'
        }
        return type_mapping.get(entry_type.lower(), 'unknown')
    
    def parse_bib_file(self, file_path: str) -> Tuple[List[Dict], int, int]:
        """
        Parse a single .bib file and return extracted publications
        Uses LOCAL duplicate detection for within-file duplicates only
        
        Args:
            file_path: Path to .bib file
            
        Returns:
            Tuple of (publications list, total_count, duplicate_count)
        """
        publications = []
        total_count = 0
        duplicate_count = 0
        
        # LOCAL seen trackers for this file only (not global)
        # Only track DBLP keys and DOIs - NOT titles (titles can have minor variations)
        local_seen_keys = set()
        local_seen_dois = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as bibfile:
                parser = BibTexParser(common_strings=True)
                parser.customization = convert_to_unicode
                bib_database = bibtexparser.load(bibfile, parser=parser)
                
                for entry in bib_database.entries:
                    total_count += 1
                    
                    # Extract DBLP key (primary identifier)
                    dblp_key = entry.get('ID', '').strip()
                    if not dblp_key:
                        logger.warning(f"Entry without ID found in {file_path}")
                        duplicate_count += 1
                        continue
                    
                    # Check for duplicate by DBLP key WITHIN THIS FILE
                    if dblp_key in local_seen_keys:
                        duplicate_count += 1
                        logger.debug(f"Duplicate DBLP key found: {dblp_key}")
                        continue
                    
                    # Extract DOI
                    doi = entry.get('doi', '').strip().upper()
                    
                    # Check for duplicate by DOI WITHIN THIS FILE (only if DOI exists)
                    if doi and doi in local_seen_dois:
                        duplicate_count += 1
                        logger.debug(f"Duplicate DOI found: {doi}")
                        continue
                    
                    # Mark as seen IN THIS FILE
                    local_seen_keys.add(dblp_key)
                    if doi:
                        local_seen_dois.add(doi)
                    
                    # Extract and normalize title (for display, not deduplication)
                    title = entry.get('title', '').strip()
                    normalized_title = self.normalize_text(title)
                    
                    # Parse authors
                    author_str = entry.get('author', '')
                    authors = self.parse_authors(author_str)
                    
                    # Parse editors
                    editor_str = entry.get('editor', '')
                    editors = self.parse_authors(editor_str)
                    
                    # Extract publication data
                    publication = {
                        'dblp_key': dblp_key,
                        'title': title,
                        'normalized_title': normalized_title,
                        'publication_type': self.extract_publication_type(entry.get('ENTRYTYPE', 'misc')),
                        'year': self._safe_int(entry.get('year')),
                        'authors': authors,
                        'editors': editors,
                        'journal': entry.get('journal', '').strip(),
                        'booktitle': entry.get('booktitle', '').strip(),
                        'volume': entry.get('volume', '').strip(),
                        'number': entry.get('number', '').strip(),
                        'pages': entry.get('pages', '').strip(),
                        'publisher': entry.get('publisher', '').strip(),
                        'series': entry.get('series', '').strip(),
                        'url': entry.get('url', '').strip(),
                        'doi': doi,
                        'ee': entry.get('ee', '').strip(),
                        'biburl': entry.get('biburl', '').strip(),
                        'bibsource': entry.get('bibsource', '').strip(),
                        'timestamp': entry.get('timestamp', '').strip(),
                        'abstract': entry.get('abstract', '').strip(),
                        'keywords': entry.get('keywords', '').strip(),
                    }
                    
                    publications.append(publication)
                    
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return publications, total_count, duplicate_count
    
    @staticmethod
    def _safe_int(value: str) -> Optional[int]:
        """Safely convert string to integer"""
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None
    
    def parse_all_bib_files(self, directory: str) -> Dict:
        """
        Parse all .bib files in a directory
        Track multiple source PIDs for publications that appear in multiple faculty files
        
        Args:
            directory: Directory containing .bib files
            
        Returns:
            Dictionary with parsing results
        """
        all_publications = []
        publication_index = {}  # Map dblp_key -> publication dict to track duplicates
        stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_entries': 0,
            'unique_publications': 0,
            'duplicates_removed': 0,
            'files_processed': []
        }
        
        # Get all .bib files
        bib_files = list(Path(directory).glob('*.bib'))
        stats['total_files'] = len(bib_files)
        
        logger.info(f"Found {len(bib_files)} .bib files to process")
        
        for bib_file in sorted(bib_files):
            try:
                publications, total, duplicates = self.parse_bib_file(str(bib_file))
                
                # Extract PID from filename (e.g., "94_4013.bib" -> "94/4013")
                # Or "01_1744-1_alok.bib" -> "01/1744-1"
                filename = bib_file.stem  # Get filename without .bib extension
                
                # Remove faculty name suffix (e.g., "_alok", "_udgata") if present
                # Faculty names are typically alphabetic suffixes after the PID
                parts = filename.split('_')
                if len(parts) >= 3:  # e.g., ["01", "1744-1", "alok"]
                    # Check if last part is alphabetic (faculty name)
                    if parts[-1].replace('-', '').isalpha():
                        # Remove the faculty name suffix
                        parts = parts[:-1]
                
                # Check if last part is a single digit (duplicate marker like _1, _2)
                if len(parts) >= 2 and parts[-1].isdigit() and len(parts[-1]) == 1:
                    # Remove duplicate marker
                    parts = parts[:-1]
                
                # Reconstruct PID: "01_1744-1" -> "01/1744-1"
                base_filename = '_'.join(parts)
                source_pid = base_filename.replace('_', '/', 1)  # Replace first underscore with /
                
                # Add or update publications with source PID tracking
                for pub in publications:
                    dblp_key = pub['dblp_key']
                    
                    if dblp_key in publication_index:
                        # Publication already exists - add this PID to source_pids list
                        existing_pub = publication_index[dblp_key]
                        if 'source_pids' not in existing_pub:
                            # Convert old source_pid to list
                            existing_pub['source_pids'] = [existing_pub.get('source_pid', source_pid)]
                        if source_pid not in existing_pub['source_pids']:
                            existing_pub['source_pids'].append(source_pid)
                        duplicates += 1
                    else:
                        # New publication - initialize with single source PID
                        pub['source_pid'] = source_pid
                        pub['source_pids'] = [source_pid]
                        publication_index[dblp_key] = pub
                
                stats['total_entries'] += total
                stats['duplicates_removed'] += duplicates
                stats['successful_files'] += 1
                stats['files_processed'].append({
                    'filename': bib_file.name,
                    'publications': len(publications),
                    'duplicates': duplicates,
                    'source_pid': source_pid
                })
                
                logger.info(f"Processed {bib_file.name}: {len(publications)} unique publications, {duplicates} duplicates")
                
            except Exception as e:
                logger.error(f"Failed to process {bib_file.name}: {e}")
                stats['failed_files'] += 1
        
        # Convert publication_index to list
        all_publications = list(publication_index.values())
        stats['unique_publications'] = len(all_publications)
        
        return {
            'publications': all_publications,
            'stats': stats
        }


if __name__ == "__main__":
    # Test the parser
    parser = BibTeXParser()
    
    # Get dataset directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    bib_directory = os.path.join(project_root, 'dataset', 'dblp')
    
    logger.info(f"Parsing BibTeX files from: {bib_directory}")
    
    # Parse all files
    results = parser.parse_all_bib_files(bib_directory)
    
    # Print statistics
    stats = results['stats']
    print(f"\n{'='*80}")
    print(f"PARSING STATISTICS")
    print(f"{'='*80}")
    print(f"Total Files: {stats['total_files']}")
    print(f"Successfully Processed: {stats['successful_files']}")
    print(f"Failed: {stats['failed_files']}")
    print(f"Total Entries Parsed: {stats['total_entries']}")
    print(f"Unique Publications: {stats['unique_publications']}")
    print(f"Duplicates Removed: {stats['duplicates_removed']}")
    print(f"{'='*80}\n")
    
    # Sample publications
    if results['publications']:
        print(f"\nSample Publications (first 3):")
        print(f"{'-'*80}")
        for i, pub in enumerate(results['publications'][:3], 1):
            print(f"\n{i}. {pub['title']}")
            print(f"   Authors: {', '.join(pub['authors'][:5])}")
            print(f"   Year: {pub['year']}, Type: {pub['publication_type']}")
            if pub['journal']:
                print(f"   Journal: {pub['journal']}")
            if pub['booktitle']:
                print(f"   Conference: {pub['booktitle']}")
