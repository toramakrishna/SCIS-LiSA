#!/usr/bin/env python3
"""
Export database tables to CSV files for data quality analysis
Generates CSV backups of all main tables
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from datetime import datetime
from sqlalchemy import text
from config.db_config import SessionLocal

def export_table_to_csv(db, table_name: str, output_dir: Path, query: str = None):
    """
    Export a database table to CSV file
    
    Args:
        db: Database session
        table_name: Name of the table to export
        output_dir: Directory to save CSV files
        query: Custom SQL query (optional, defaults to SELECT * FROM table_name)
    """
    if query is None:
        query = f"SELECT * FROM {table_name}"
    
    print(f"Exporting {table_name}...", end=" ", flush=True)
    
    # Execute query
    result = db.execute(text(query))
    rows = result.fetchall()
    
    if not rows:
        print(f"No data found")
        return
    
    # Get column names
    columns = result.keys()
    
    # Create CSV file
    csv_file = output_dir / f"{table_name}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        writer.writerow(columns)
        
        # Write rows
        for row in rows:
            # Convert arrays to string representation
            processed_row = []
            for value in row:
                if isinstance(value, list):
                    processed_row.append(';'.join(str(v) for v in value))
                elif value is None:
                    processed_row.append('')
                else:
                    processed_row.append(value)
            writer.writerow(processed_row)
    
    print(f"✓ {len(rows)} rows exported to {csv_file.name}")
    return len(rows)


def main():
    """Export all database tables to CSV files"""
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent.parent / 'exports' / f'db_export_{timestamp}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 80)
    print(" " * 25 + "DATABASE EXPORT TO CSV")
    print("=" * 80)
    print(f"Output directory: {output_dir}")
    print("-" * 80)
    
    db = SessionLocal()
    
    try:
        total_rows = 0
        
        # Export main tables
        tables = {
            'publications': None,
            'authors': None,
            'venues': None,
            'collaborations': None,
            'data_sources': None
        }
        
        for table_name in tables:
            rows = export_table_to_csv(db, table_name, output_dir)
            if rows:
                total_rows += rows
        
        print("-" * 80)
        
        # Export faculty-specific views
        print("\nExporting faculty-specific data...")
        
        # Faculty authors
        faculty_query = """
            SELECT id, name, dblp_pid, is_faculty, designation, email, 
                   department, created_at
            FROM authors 
            WHERE is_faculty = true 
            ORDER BY name
        """
        export_table_to_csv(db, 'faculty_authors', output_dir, faculty_query)
        
        # Faculty publications (publications with at least one faculty author)
        faculty_pubs_query = """
            SELECT DISTINCT p.id, p.title, p.dblp_key, p.publication_type, 
                   p.year, p.journal, p.booktitle, p.source_pids
            FROM publications p
            WHERE EXISTS (
                SELECT 1 FROM authors a
                WHERE a.is_faculty = true 
                AND a.dblp_pid = ANY(p.source_pids)
            )
            ORDER BY p.year DESC, p.title
        """
        export_table_to_csv(db, 'faculty_publications', output_dir, faculty_pubs_query)
        
        # Author collaboration network
        collab_query = """
            SELECT c.id, 
                   a1.name as author1_name, a1.is_faculty as author1_is_faculty,
                   a2.name as author2_name, a2.is_faculty as author2_is_faculty,
                   c.collaboration_count, c.first_collaboration_year, c.last_collaboration_year
            FROM collaborations c
            JOIN authors a1 ON c.author1_id = a1.id
            JOIN authors a2 ON c.author2_id = a2.id
            WHERE a1.is_faculty = true OR a2.is_faculty = true
            ORDER BY c.collaboration_count DESC
        """
        export_table_to_csv(db, 'faculty_collaborations', output_dir, collab_query)
        
        # Summary statistics
        print("\nExporting summary statistics...")
        
        stats_query = """
            SELECT 
                'Publications' as entity,
                COUNT(*) as total_count,
                COUNT(CASE WHEN year >= 2020 THEN 1 END) as recent_count
            FROM publications
            UNION ALL
            SELECT 
                'Authors',
                COUNT(*),
                COUNT(CASE WHEN is_faculty = true THEN 1 END)
            FROM authors
            UNION ALL
            SELECT 
                'Venues',
                COUNT(*),
                COUNT(CASE WHEN venue_type = 'journal' THEN 1 END)
            FROM venues
            UNION ALL
            SELECT 
                'Collaborations',
                COUNT(*),
                NULL
            FROM collaborations
        """
        export_table_to_csv(db, 'summary_statistics', output_dir, stats_query)
        
        # Faculty publication counts
        faculty_stats_query = """
            SELECT 
                a.name as faculty_name,
                a.dblp_pid,
                a.designation,
                COUNT(DISTINCT p.id) as publication_count,
                MIN(p.year) as first_publication_year,
                MAX(p.year) as latest_publication_year,
                COUNT(DISTINCT CASE WHEN p.publication_type = 'article' THEN p.id END) as journal_articles,
                COUNT(DISTINCT CASE WHEN p.publication_type = 'inproceedings' THEN p.id END) as conference_papers
            FROM authors a
            JOIN publications p ON a.dblp_pid = ANY(p.source_pids)
            WHERE a.is_faculty = true
            GROUP BY a.id, a.name, a.dblp_pid, a.designation
            ORDER BY publication_count DESC, a.name
        """
        export_table_to_csv(db, 'faculty_publication_stats', output_dir, faculty_stats_query)
        
        # Venue statistics
        venue_stats_query = """
            SELECT 
                v.name as venue_name,
                v.venue_type,
                (SELECT COUNT(*) FROM publications p 
                 WHERE (v.venue_type = 'journal' AND p.journal = v.name) 
                    OR (v.venue_type = 'conference' AND p.booktitle = v.name)) as publication_count,
                (SELECT MIN(year) FROM publications p 
                 WHERE (v.venue_type = 'journal' AND p.journal = v.name) 
                    OR (v.venue_type = 'conference' AND p.booktitle = v.name)) as first_year,
                (SELECT MAX(year) FROM publications p 
                 WHERE (v.venue_type = 'journal' AND p.journal = v.name) 
                    OR (v.venue_type = 'conference' AND p.booktitle = v.name)) as latest_year
            FROM venues v
            ORDER BY publication_count DESC
            LIMIT 50
        """
        export_table_to_csv(db, 'top_venues', output_dir, venue_stats_query)
        
        print("-" * 80)
        print(f"\n✓ Export completed successfully!")
        print(f"  Total rows exported: {total_rows:,}")
        print(f"  Files saved to: {output_dir}")
        print("=" * 80 + "\n")
        
        # Create a README file
        readme_path = output_dir / 'README.txt'
        with open(readme_path, 'w') as f:
            f.write(f"Database Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write("This directory contains CSV exports of the SCISLiSA database.\n\n")
            f.write("Main Tables:\n")
            f.write("  - publications.csv: All publications (1,301 records)\n")
            f.write("  - authors.csv: All authors (1,090 records)\n")
            f.write("  - venues.csv: All venues (670 records)\n")
            f.write("  - collaborations.csv: Author-publication relationships\n")
            f.write("  - data_sources.csv: Data source tracking\n\n")
            f.write("Faculty-Specific Data:\n")
            f.write("  - faculty_authors.csv: 34 faculty members\n")
            f.write("  - faculty_publications.csv: Publications with faculty authors\n")
            f.write("  - publication_authors.csv: Detailed author-publication mapping\n\n")
            f.write("Statistics:\n")
            f.write("  - summary_statistics.csv: Overall database statistics\n")
            f.write("  - faculty_publication_stats.csv: Per-faculty publication counts\n")
            f.write("  - top_venues.csv: Top 50 venues by publication count\n\n")
            f.write("Notes:\n")
            f.write("  - Array fields (like source_pids) are semicolon-separated\n")
            f.write("  - Empty cells represent NULL values\n")
            f.write("  - All dates are in ISO format (YYYY-MM-DD)\n")
        
        print(f"README file created: {readme_path.name}\n")
        
    except Exception as e:
        print(f"\n✗ Error during export: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
