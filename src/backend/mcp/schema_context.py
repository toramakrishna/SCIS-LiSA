"""
Database Schema Context for NL-to-SQL Agent
Provides comprehensive schema information for LLM to generate accurate SQL queries
"""

DATABASE_SCHEMA = """
# SCISLiSA Database Schema

## Tables and Relationships

### 1. authors
Stores faculty members and co-authors with their information and statistics.

Columns:
- id (INTEGER, PRIMARY KEY): Unique author identifier
- name (STRING): Author's full name (indexed)
- normalized_name (STRING): Normalized version for deduplication
- dblp_pid (STRING): DBLP person ID (e.g., '09/1571')
- dblp_urlpt (STRING): DBLP URL part
- is_faculty (BOOLEAN): True if this is a faculty member (indexed)
- email (STRING): Email address
- department (STRING): Department name (default: 'SCIS')
- designation (STRING): Academic position (Professor, Assistant Professor, etc.)
- phone (STRING): Contact number
- total_publications (INTEGER): Cached count of publications
- total_collaborations (INTEGER): Count of unique collaborators
- h_index (INTEGER): H-index metric
- created_at (TIMESTAMP): Record creation time
- updated_at (TIMESTAMP): Last update time

Indexes:
- idx_author_name_faculty (name, is_faculty)

### 2. publications
Stores research publications with complete metadata.

Columns:
- id (INTEGER, PRIMARY KEY): Unique publication identifier
- title (TEXT): Publication title (indexed)
- publication_type (STRING): Type: 'article', 'inproceedings', 'book', 'incollection', etc.
- year (INTEGER): Publication year (indexed)
- journal (STRING): Journal name (if article)
- booktitle (STRING): Conference/book title (if inproceedings/incollection)
- volume (STRING): Volume number
- number (STRING): Issue number
- pages (STRING): Page range
- publisher (STRING): Publisher name
- doi (STRING): Digital Object Identifier
- url (TEXT): Publication URL
- abstract (TEXT): Abstract text
- dblp_key (STRING): Unique DBLP identifier (e.g., 'DBLP:journals/tocs/Smith20')
- author_count (INTEGER): Number of authors
- has_faculty_author (BOOLEAN): True if any author is faculty
- source_pids (ARRAY): List of faculty DBLP PIDs who authored this
- created_at (TIMESTAMP): Record creation time
- updated_at (TIMESTAMP): Last update time

Indexes:
- idx_pub_year (year)
- idx_pub_type (publication_type)
- idx_pub_dblp_key (dblp_key, UNIQUE)
- idx_pub_faculty (has_faculty_author, year)

### 3. publication_authors (Association Table)
Many-to-many relationship between publications and authors.

Columns:
- id (INTEGER, PRIMARY KEY): Unique identifier
- publication_id (INTEGER, FOREIGN KEY → publications.id): Publication reference
- author_id (INTEGER, FOREIGN KEY → authors.id): Author reference
- author_position (INTEGER): Position in author list (1st, 2nd, etc.)
- created_at (TIMESTAMP): Record creation time

Indexes:
- idx_pub_authors_pub (publication_id)
- idx_pub_authors_author (author_id)
- UNIQUE CONSTRAINT: (publication_id, author_id)

### 4. venues
Stores journals and conferences.

Columns:
- id (INTEGER, PRIMARY KEY): Unique venue identifier
- name (STRING): Venue full name (indexed)
- short_name (STRING): Abbreviation
- venue_type (STRING): 'journal' or 'conference'
- publisher (STRING): Publisher name
- issn (STRING): ISSN for journals
- total_publications (INTEGER): Count of publications
- created_at (TIMESTAMP): Record creation time
- updated_at (TIMESTAMP): Last update time

### 5. collaborations
Stores co-authorship relationships between authors.

Columns:
- id (INTEGER, PRIMARY KEY): Unique identifier
- author1_id (INTEGER, FOREIGN KEY → authors.id): First author
- author2_id (INTEGER, FOREIGN KEY → authors.id): Second author
- collaboration_count (INTEGER): Number of joint publications
- first_collaboration_year (INTEGER): Year of first joint paper
- last_collaboration_year (INTEGER): Year of most recent joint paper
- created_at (TIMESTAMP): Record creation time
- updated_at (TIMESTAMP): Last update time

Indexes:
- idx_collab_authors (author1_id, author2_id)

## Common Query Patterns

### Faculty Publications by Year
```sql
SELECT a.name, p.year, COUNT(*) as pub_count
FROM authors a
JOIN publication_authors pa ON a.id = pa.author_id
JOIN publications p ON pa.publication_id = p.id
WHERE a.is_faculty = true
GROUP BY a.name, p.year
ORDER BY p.year DESC, pub_count DESC;
```

### Top Collaborators for a Faculty Member
Note: The collaborations table already contains pre-computed collaboration_count.
No GROUP BY needed - just filter and sort.
```sql
SELECT a2.name as collaborator, c.collaboration_count as joint_publications
FROM authors a1
JOIN collaborations c ON a1.id = c.author1_id
JOIN authors a2 ON c.author2_id = a2.id
WHERE a1.name = 'Satish Narayana Srirama'
ORDER BY c.collaboration_count DESC
LIMIT 10;
```

### Publication Type Distribution
```sql
SELECT publication_type, COUNT(*) as count
FROM publications
WHERE has_faculty_author = true
GROUP BY publication_type
ORDER BY count DESC;
```

### Publications per Year Trend
```sql
SELECT year, COUNT(*) as publications
FROM publications
WHERE has_faculty_author = true AND year >= 2020
GROUP BY year
ORDER BY year;
```

### Top Venues
```sql
SELECT journal as venue_name, COUNT(*) as pub_count
FROM publications
WHERE journal IS NOT NULL AND journal != ''
GROUP BY journal
ORDER BY pub_count DESC
LIMIT 10;
```

### Faculty Ranking by Publications
```sql
SELECT a.name, a.designation, COUNT(DISTINCT p.id) as publication_count
FROM authors a
JOIN publication_authors pa ON a.id = pa.author_id
JOIN publications p ON pa.publication_id = p.id
WHERE a.is_faculty = true
GROUP BY a.id, a.name, a.designation
ORDER BY publication_count DESC;
```

## Important Notes

1. **Faculty Identification**: Use `is_faculty = true` in authors table
2. **Publication Years**: Year column is indexed for efficient time-based queries
3. **Venue Names**: Stored in `journal` (for articles) or `booktitle` (for conferences)
4. **Author Position**: Available in publication_authors.author_position
5. **Collaboration Data**: Pre-computed in collaborations table
6. **DBLP Integration**: source_pids array contains faculty DBLP PIDs who authored the paper
"""

QUERY_EXAMPLES = {
    "simple_count": {
        "question": "How many publications does Satish Srirama have?",
        "sql": """
SELECT COUNT(DISTINCT p.id) as publication_count
FROM publications p
JOIN publication_authors pa ON p.id = pa.publication_id
JOIN authors a ON pa.author_id = a.id
WHERE a.name ILIKE '%Satish%Srirama%';
""",
        "visualization": "none",
        "explanation": "Satish Narayana Srirama has published 78 papers in total.",
        "note": "Using partial name matching to handle name variations. No chart needed for a single number."
    },
    "publications_by_year": {
        "question": "Show publication trends over the years",
        "sql": """
SELECT year, COUNT(*) as publications
FROM publications
WHERE has_faculty_author = true
GROUP BY year
ORDER BY year;
""",
        "visualization": "line_chart",
        "x_axis": "year",
        "y_axis": "publications"
    },
    "top_faculty": {
        "question": "Who are the most productive faculty members?",
        "sql": """
SELECT a.name, a.designation, COUNT(DISTINCT p.id) as publications
FROM authors a
JOIN publication_authors pa ON a.id = pa.author_id
JOIN publications p ON pa.publication_id = p.id
WHERE a.is_faculty = true
GROUP BY a.id, a.name, a.designation
ORDER BY publications DESC
LIMIT 10;
""",
        "visualization": "bar_chart",
        "x_axis": "name",
        "y_axis": "publications"
    },
    "top_faculty_by_year": {
        "question": "Who published the most in 2024?",
        "sql": """
SELECT a.name, COUNT(DISTINCT p.id) as publications
FROM authors a
JOIN publication_authors pa ON a.id = pa.author_id
JOIN publications p ON pa.publication_id = p.id
WHERE a.is_faculty = true AND p.year = 2024
GROUP BY a.id, a.name
ORDER BY publications DESC
LIMIT 1;
""",
        "visualization": "none",
        "explanation": "The most productive faculty member in 2024",
        "note": "Returns a single faculty member - no chart needed for simple answer"
    },
    "publication_types": {
        "question": "What types of publications do faculty produce?",
        "sql": """
SELECT publication_type, COUNT(*) as count
FROM publications
WHERE has_faculty_author = true
GROUP BY publication_type
ORDER BY count DESC;
""",
        "visualization": "pie_chart",
        "label": "publication_type",
        "value": "count"
    },
    "top_venues": {
        "question": "What are the top publication venues?",
        "sql": """
SELECT 
    COALESCE(journal, booktitle) as venue,
    COUNT(*) as publications
FROM publications
WHERE has_faculty_author = true
  AND (journal IS NOT NULL AND journal != '' OR booktitle IS NOT NULL AND booktitle != '')
GROUP BY COALESCE(journal, booktitle)
ORDER BY publications DESC
LIMIT 15;
""",
        "visualization": "bar_chart",
        "x_axis": "venue",
        "y_axis": "publications"
    },
    "collaborations": {
        "question": "Show collaboration network of faculty members",
        "sql": """
SELECT 
    a1.name as faculty_member,
    a2.name as collaborator,
    c.collaboration_count as joint_papers
FROM collaborations c
JOIN authors a1 ON c.author1_id = a1.id
JOIN authors a2 ON c.author2_id = a2.id
WHERE a1.is_faculty = true
ORDER BY c.collaboration_count DESC
LIMIT 30;
""",
        "visualization": "network_graph",
        "node1": "faculty_member",
        "node2": "collaborator",
        "edge_weight": "joint_papers",
        "note": "Shows faculty members and their top collaborators. Use WHERE a1.is_faculty = true (not requiring both to be faculty) since faculty typically collaborate with external researchers."
    },
    "recent_publications": {
        "question": "What are the most recent publications?",
        "sql": """
SELECT 
    p.title,
    STRING_AGG(DISTINCT a.name, ', ') as authors,
    p.year,
    p.publication_type,
    COALESCE(NULLIF(p.journal, ''), p.booktitle) as venue
FROM publications p
LEFT JOIN publication_authors pa ON p.id = pa.publication_id
LEFT JOIN authors a ON pa.author_id = a.id
WHERE p.has_faculty_author = true
GROUP BY p.id, p.title, p.year, p.publication_type, p.journal, p.booktitle
ORDER BY p.year DESC, p.title
LIMIT 20;
""",
        "visualization": "table",
        "columns": ["title", "authors", "year", "publication_type", "venue"]
    },
    "publication_by_title": {
        "question": "Who published the paper 'Interest maximization in social networks'?",
        "sql": """
SELECT 
    p.title,
    STRING_AGG(DISTINCT a.name, ', ') as authors,
    p.year,
    p.publication_type,
    COALESCE(NULLIF(p.journal, ''), p.booktitle) as venue
FROM publications p
LEFT JOIN publication_authors pa ON p.id = pa.publication_id
LEFT JOIN authors a ON pa.author_id = a.id
WHERE p.title ILIKE '%Interest maximization in social networks%'
GROUP BY p.id, p.title, p.year, p.publication_type, p.journal, p.booktitle
ORDER BY p.year DESC
LIMIT 5;
""",
        "visualization": "table",
        "columns": ["title", "authors", "year", "publication_type", "venue"],
        "note": "Searching by publication title. Use ILIKE with wildcards for flexible matching. MUST include LEFT JOINs to show authors."
    },
    "faculty_member_publications": {
        "question": "What are the recent publications by Satish Srirama?",
        "sql": """
SELECT 
    p.title,
    STRING_AGG(DISTINCT a.name, ', ') as authors,
    p.year,
    p.publication_type,
    COALESCE(NULLIF(p.journal, ''), p.booktitle) as venue
FROM publications p
LEFT JOIN publication_authors pa ON p.id = pa.publication_id
LEFT JOIN authors a ON pa.author_id = a.id
WHERE EXISTS (
    SELECT 1 FROM publication_authors pa2
    JOIN authors a2 ON pa2.author_id = a2.id
    WHERE pa2.publication_id = p.id 
    AND a2.name ILIKE '%Satish%Srirama%'
)
GROUP BY p.id, p.title, p.year, p.publication_type, p.journal, p.booktitle
ORDER BY p.year DESC, p.title
LIMIT 10;
""",
        "visualization": "table",
        "columns": ["title", "authors", "year", "publication_type", "venue"],
        "note": "Using partial name matching with ILIKE to handle name variations like 'Satish Narayana Srirama' or 'Satish N. Srirama'"
    },
    "faculty_growth": {
        "question": "How has faculty publication output changed over time?",
        "sql": """
SELECT 
    a.name,
    p.year,
    COUNT(*) as publications
FROM authors a
JOIN publication_authors pa ON a.id = pa.author_id
JOIN publications p ON pa.publication_id = p.id
WHERE a.is_faculty = true AND p.year >= 2015
GROUP BY a.name, p.year
ORDER BY a.name, p.year;
""",
        "visualization": "multi_line_chart",
        "x_axis": "year",
        "y_axis": "publications",
        "series": "name"
    }
}

def get_schema_context() -> str:
    """Get complete database schema context for LLM"""
    return DATABASE_SCHEMA

def get_example_queries() -> dict:
    """Get example query patterns"""
    return QUERY_EXAMPLES
