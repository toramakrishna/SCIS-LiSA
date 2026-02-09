# Publication Report Generation Enhancement

## Overview

The MCP Agent (`agent.py`) has been enhanced to automatically detect and generate standardized faculty publication reports in the SCIS format when requested by users through the Query page.

## Changes Made

### 1. New Files Created

#### `/src/backend/references/publication_report_prompt.md`
- **Purpose**: Comprehensive template for generating publication reports
- **Content**: 
  - SCIS publication format specification
  - Category definitions (A: Books, B: Research Papers, C: Conferences)
  - Citation format examples
  - Prompt template for AI-based report generation
  - Quality assurance checklist

#### `/src/backend/references/scis_publications_analysis_2024-2025.md`
- **Purpose**: Complete analysis of SCIS faculty publications for 2024-2025
- **Content**:
  - Statistical breakdown by faculty
  - Publication distribution by category
  - Research themes and trends
  - Collaboration patterns
  - Recommendations for future growth

#### `/src/backend/test_report_generation.py`
- **Purpose**: Test script to verify report generation functionality
- **Usage**:
  ```bash
  python test_report_generation.py           # Run all tests
  python test_report_generation.py --detailed # Single detailed test
  ```

### 2. Enhanced Agent (`agent.py`)

#### New Methods

**`_load_report_template()`**
- Loads the publication report prompt template from markdown file
- Extracts the main prompt section for use in query generation
- Provides fallback if file not found

**`_is_report_request(question: str) -> bool`**
- Detects if user is requesting a formatted publication report
- Checks for keywords like:
  - "generate report"
  - "publication report"
  - "in the format"
  - "format as mentioned"
  - "category a/b/c"
- Returns `True` if report format is needed

**`_build_report_prompt(question: str, conversation_history: Optional[List]) -> str`**
- Builds specialized prompt for publication report generation
- Includes:
  - Schema context
  - SCIS format specifications with examples
  - Category mappings (A: Books, B: Papers, C: Conferences)
  - SQL query structure for report generation
  - Formatting templates
- Extracts faculty name from question
- Returns complete prompt optimized for report generation

**`_extract_faculty_name(question: str) -> Optional[str]`**
- Extracts faculty member name from user question
- Handles various patterns:
  - "publications by [Name]"
  - "report for [Name]"
  - "Professor [Name]"
  - "[Name]'s publications"
- Returns `None` if no specific faculty mentioned (generates report for all)

#### Modified Methods

**`_build_prompt(question: str, conversation_history: Optional[List]) -> str`**
- Now checks if request is for a report using `_is_report_request()`
- Routes to `_build_report_prompt()` if report detected
- Otherwise uses original prompt building logic
- Ensures seamless switching between normal queries and report generation

**`_find_similar_example(question: str) -> Dict`**
- Added priority check for report requests
- Uses new `publication_report` example when appropriate
- Maintains compatibility with existing example selection logic

### 3. Schema Context Updates (`schema_context.py`)

#### New Example Query: `publication_report`
```python
"publication_report": {
    "question": "Generate publication report for Satish Srirama in SCIS format",
    "sql": """...""",  # Complete SQL with category ordering
    "visualization": "report",
    "report_format": "...",
    "categorization": {
        "A": ["book", "proceedings", "incollection"],
        "B": ["article"],
        "C": ["inproceedings"]
    }
}
```

## How It Works

### User Request Flow

1. **User asks query** on Query page, e.g.:
   - "Generate publication report for Satish Srirama"
   - "List all publications of Udgata in SCIS format"
   - "Show Salman's publications in the below format..."

2. **Agent detects report request**:
   - `_is_report_request()` analyzes question keywords
   - Returns `True` if report format indicators found

3. **Agent builds specialized prompt**:
   - `_build_report_prompt()` creates report-specific prompt
   - Includes SCIS format examples and specifications
   - Extracts faculty name using `_extract_faculty_name()`

4. **LLM generates response**:
   - Receives specialized prompt with format guidelines
   - Generates SQL query to fetch all publications
   - Orders by category (A, B, C) and year
   - Sets `visualization: "report"` in response
   - Includes `report_format` template and `categorization` mapping

5. **Frontend renders report**:
   - Detects `visualization: "report"` 
   - Formats data according to SCIS standard
   - Groups by categories (A: Books, B: Papers, C: Conferences)
   - Numbers publications within each category
   - Provides download option for text format

### SQL Query Structure for Reports

```sql
SELECT 
    p.publication_type,
    p.title,
    STRING_AGG(DISTINCT a.name, ', ') as authors,
    p.year,
    COALESCE(NULLIF(p.journal, ''), p.booktitle) as venue,
    p.publisher,
    p.volume,
    p.number,
    p.pages,
    p.doi
FROM publications p
JOIN publication_authors pa ON p.id = pa.publication_id
JOIN authors a ON pa.author_id = a.id
WHERE EXISTS (
    SELECT 1 FROM publication_authors pa2
    JOIN authors a2 ON pa2.author_id = a2.id
    WHERE pa2.publication_id = p.id 
    AND a2.name ILIKE '%Faculty Name%'
)
GROUP BY p.id, p.publication_type, p.title, p.year, p.journal, p.booktitle, 
         p.publisher, p.volume, p.number, p.pages, p.doi
ORDER BY 
    CASE p.publication_type
        WHEN 'book' THEN 1
        WHEN 'proceedings' THEN 2
        WHEN 'incollection' THEN 3
        WHEN 'article' THEN 4
        WHEN 'inproceedings' THEN 5
        ELSE 6
    END,
    p.year DESC;
```

**Key Features:**
- **No LIMIT clause** - returns ALL publications
- **Category ordering** - groups by publication type
- **Year DESC** - most recent first within each category
- **All authors** - uses STRING_AGG to show all co-authors
- **Complete metadata** - includes volume, pages, DOI, etc.

## SCIS Format Specification

### Category Mapping

| Category | Publication Types | Description |
|----------|-------------------|-------------|
| **A** | book, proceedings, incollection | Books (Authored/Edited/Chapters) |
| **B** | article | Research Papers (Journal Publications) |
| **C** | inproceedings | Conference Proceedings |

### Citation Format

**Category A - Books:**
```
A 1. Books Authored: [Authors], [Role], [Title], [Edition], [Publisher], [Location], [ISBN], [Date].

A 2. Books Edited: [Editors], [Role], [Title], [Publisher], [Location], [ISBN], [Date].

A 3. Books Chapter (Authorship): [Authors], [Chapter Title] in [Book Title] (ISBN: [ISBN]), Editor(s): [Editors], [Publisher], [Location], [Date], pp. [Pages].
```

**Category B - Research Papers:**
```
B 1. Research Papers: [Authors], [Role], [Title], [Indexing], [Volume], [Journal], [Pages], [Date].
```

**Category C - Conference Proceedings:**
```
C 1. Conference Proceedings: [Authors], [Role], [Title], [Conference], [Volume], [ISBN], [Pages], [Location], [Date].
```

## Example Usage

### Query Examples

1. **Basic Report Request:**
   ```
   "Generate publication report for Satish Narayana Srirama"
   ```
   → Returns all publications in SCIS format

2. **With Format Specification:**
   ```
   "List all publications of Siba Kumar Udgata in SCIS format"
   ```
   → Returns categorized report with proper formatting

3. **Custom Format Request:**
   ```
   "Show publications by Salman Abdul Moiz in the below format:
   Category Number. Type: Authors, Title, Venue, Year"
   ```
   → Returns report with specified format template

4. **All Faculty Report:**
   ```
   "Generate publication report for all SCIS faculty members"
   ```
   → Returns comprehensive report for entire school

### Testing

Run the test script to verify functionality:

```bash
cd /home/24mcpc14/tork/github.com/toramakrishna/SCIS-LiSA/src/backend

# Test all report scenarios
python test_report_generation.py

# Detailed test with full JSON output
python test_report_generation.py --detailed
```

## Configuration

### Environment Variables

The agent respects existing Ollama configuration:

```env
# Local Ollama (default)
OLLAMA_MODE=local
OLLAMA_LOCAL_HOST=http://localhost:11434
OLLAMA_LOCAL_MODEL=llama3.2

# Cloud Ollama
OLLAMA_MODE=cloud
OLLAMA_CLOUD_HOST=https://ollama.com
OLLAMA_CLOUD_MODEL=qwen3-coder-next
OLLAMA_API_KEY=your_api_key_here
```

No additional configuration needed for report generation.

## Frontend Integration

The frontend should detect `visualization: "report"` in the response and:

1. **Parse categorization mapping** from response
2. **Group results** by publication_type according to categories
3. **Number sequentially** within each category
4. **Format citations** using report_format template
5. **Display sections**:
   - Category A: Books (Authored/Edited/Chapters)
   - Category B: Research Papers
   - Category C: Conference Proceedings
6. **Provide download** as .txt or .md file

### Expected Response Structure

```json
{
  "sql": "SELECT ...",
  "visualization": "report",
  "explanation": "Publication report for [Faculty Name]",
  "report_format": "{category} {number}. {type}: {authors}, {role}, {title}, ...",
  "note": "Report formatted according to SCIS standard",
  "categorization": {
    "A": ["book", "proceedings", "incollection"],
    "B": ["article"],
    "C": ["inproceedings"]
  }
}
```

## Benefits

1. **Automated Report Generation**: Faculty can generate publication reports instantly
2. **Standardized Format**: Ensures consistency with SCIS requirements
3. **Comprehensive Data**: Includes all metadata (authors, venue, volume, pages, etc.)
4. **Flexible**: Handles individual faculty or all faculty reports
5. **Maintainable**: Template-based approach allows easy format updates
6. **Backward Compatible**: Doesn't affect existing query functionality

## Future Enhancements

1. **Date Range Filtering**: "Publications from 2020-2024"
2. **Category Filtering**: "Only show research papers"
3. **Export Formats**: PDF, Word, LaTeX
4. **Multi-Faculty Reports**: Side-by-side comparison
5. **Impact Metrics**: Include h-index, citations, impact factors
6. **Custom Templates**: Allow users to define their own formats

## Maintenance

### Updating Format Specifications

To modify the SCIS format:

1. Edit `/src/backend/references/publication_report_prompt.md`
2. Update the format examples and templates
3. Restart the backend service
4. Changes are automatically picked up by agent

### Adding New Categories

To add new publication categories:

1. Update `categorization` mapping in schema_context.py
2. Add new category examples in publication_report_prompt.md
3. Update frontend category display logic
4. Test with `test_report_generation.py`

## Troubleshooting

### Report Not Generating

**Issue**: Agent returns table instead of report

**Solutions**:
- Check if question contains report keywords
- Add explicit "report" or "format" in query
- Try: "Generate publication report for [Name]"

### Missing Publications

**Issue**: Some publications not showing in report

**Solutions**:
- Verify faculty name spelling in database
- Check publication_authors table linkage
- Run: `SELECT * FROM authors WHERE name ILIKE '%Faculty Name%'`

### Format Issues

**Issue**: Citations not formatted correctly

**Solutions**:
- Review report_format template in response
- Check if all required fields present in SQL query
- Verify categorization mapping is correct

## Contact & Support

For issues or enhancements related to report generation:
- Check test results: `python test_report_generation.py`
- Review logs: Agent logs report mode activation
- Consult: `publication_report_prompt.md` for format specs
