"""
MCP Agent - Natural Language to SQL Query Generator
Uses Ollama LLM to convert natural language questions to SQL queries
"""

import json
import re
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from ollama import Client
from dotenv import load_dotenv

# Load .env file at module import time
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from mcp.schema_context import get_schema_context, get_example_queries

logger = logging.getLogger(__name__)

# Load publication report prompt template
REPORT_PROMPT_PATH = Path(__file__).parent.parent / 'references' / 'publication_report_prompt.md'


class OllamaAgent:
    """Ollama-based agent for NL-to-SQL conversion"""
    
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None):
        # Determine mode: cloud or local
        ollama_mode = os.getenv("OLLAMA_MODE", "local").lower()
        
        if ollama_mode == "cloud":
            # Cloud Ollama configuration
            default_host = os.getenv("OLLAMA_CLOUD_HOST", "https://ollama.com")
            default_model = os.getenv("OLLAMA_CLOUD_MODEL", "qwen3-coder-next")
            self.api_key = os.getenv("OLLAMA_API_KEY")
            
            logger.info(f"🌩️  Using CLOUD Ollama mode")
        else:
            # Local Ollama configuration
            default_host = os.getenv("OLLAMA_LOCAL_HOST", "http://localhost:11434")
            default_model = os.getenv("OLLAMA_LOCAL_MODEL", "llama3.2")
            self.api_key = None
            
            logger.info(f"🖥️  Using LOCAL Ollama mode")
        
        # Allow override via parameters
        self.model = model or default_model
        self.base_url = base_url or default_host
        
        logger.info(f"Initializing OllamaAgent - Mode: {ollama_mode}, Model: '{self.model}', Host: '{self.base_url}', API Key: {'✓ set' if self.api_key else '✗ not set'}")
        
        # Initialize Ollama client with or without API key
        if self.api_key:
            # Cloud Ollama with API key authentication
            self.client = Client(
                host=self.base_url,
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            logger.info("✓ Client initialized with API key authentication")
        else:
            # Local Ollama without API key
            self.client = Client(host=self.base_url)
            logger.info("✓ Client initialized for local connection")
        
        self.schema_context = get_schema_context()
        self.examples = get_example_queries()
        self.report_template = self._load_report_template()
    
    def _load_report_template(self) -> str:
        """Load the publication report prompt template"""
        try:
            if REPORT_PROMPT_PATH.exists():
                with open(REPORT_PROMPT_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract the main prompt section from the markdown
                    prompt_match = re.search(r'## Prompt for Report Generation\s*```(.*?)```', content, re.DOTALL)
                    if prompt_match:
                        return prompt_match.group(1).strip()
                logger.info(f"✓ Loaded publication report template from {REPORT_PROMPT_PATH}")
                return content
        except Exception as e:
            logger.warning(f"Could not load report template: {e}")
        return ""
    
    async def generate_sql(self, question: str, conversation_history: Optional[List] = None) -> Dict:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            conversation_history: Optional list of previous messages for context
                                 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        
        Returns:
            {
                "sql": "SELECT ...",
                "visualization": "line_chart|bar_chart|pie_chart|table|network_graph",
                "explanation": "What this query does",
                "confidence": 0.95
            }
        """
        # Build prompt with schema context, examples, and conversation history
        prompt = self._build_prompt(question, conversation_history)
        
        try:
            # Use Ollama client to generate response
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                format='json',  # Request JSON format explicitly
                options={
                    'temperature': 0.1,  # Low temperature for more deterministic SQL
                    'top_p': 0.9,
                    'num_predict': 1000  # Allow longer responses for complex queries
                }
            )
            
            # Parse the LLM response
            return self._parse_llm_response(response['response'], question)
                
        except Exception as e:
            # Provide context-specific error guidance
            ollama_mode = os.getenv("OLLAMA_MODE", "local").lower()
            
            if ollama_mode == "cloud":
                guidance = "Check OLLAMA_CLOUD_HOST, OLLAMA_CLOUD_MODEL, and OLLAMA_API_KEY in .env"
            else:
                guidance = f"Make sure Ollama is running locally at {self.base_url} and model '{self.model}' is pulled"
            
            return {
                "error": f"Ollama API error: {str(e)}",
                "sql": None,
                "visualization": "table",
                "explanation": "Failed to connect to LLM service",
                "note": f"Mode: {ollama_mode}. {guidance}"
            }
    
    def _build_prompt(self, question: str, conversation_history: Optional[List] = None) -> str:
        """Build comprehensive prompt with schema, examples, and conversation history"""
        
        # Detect if user wants a formatted publication report
        is_report_request = self._is_report_request(question)
        
        if is_report_request and self.report_template:
            logger.info("🎯 Detected publication report request - using specialized template")
            return self._build_report_prompt(question, conversation_history)
        
        # Find most relevant example
        relevant_example = self._find_similar_example(question)
        
        # Build conversation context section if history provided
        context_section = ""
        last_user_question = None
        last_sql_query = None
        last_visualization_type = None
        
        if conversation_history and len(conversation_history) > 0:
            context_section = "\n## Previous Conversation Context\n"
            
            # Include up to last 4 messages (2 exchanges) to avoid overwhelming the prompt
            recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
            
            for msg in recent_history:
                # Handle both Pydantic objects and dictionaries
                if hasattr(msg, 'role'):
                    # Pydantic Message object
                    role = msg.role
                    content = msg.content
                else:
                    # Dictionary
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                
                if role == "user":
                    last_user_question = content
                    context_section += f"Previous question: \"{content}\"\n"
                elif role == "assistant":
                    # Extract SQL and visualization type from assistant response
                    if "SELECT" in content.upper():
                        # This is likely SQL
                        sql_match = re.search(r'(SELECT.*?;)', content, re.IGNORECASE | re.DOTALL)
                        if sql_match:
                            last_sql_query = sql_match.group(1)
                            context_section += f"Previous query: {sql_match.group(1)[:300]}...\n"
                        
                        # Extract visualization type if present
                        viz_match = re.search(r'\[VISUALIZATION:\s*(\w+)\]', content, re.IGNORECASE)
                        if viz_match:
                            last_visualization_type = viz_match.group(1)
                            context_section += f"Previous visualization format: {last_visualization_type}\n"
            
            # Detect if current question is a follow-up
            follow_up_indicators = ['also', 'what about', 'how about', 'and for', 'show for', 'same for', 'for']
            is_follow_up = any(indicator in question.lower() for indicator in follow_up_indicators)
            
            if is_follow_up and last_user_question and last_sql_query:
                context_section += f"\n🔄 **FOLLOW-UP DETECTED**:\n"
                context_section += f"The current question appears to be a follow-up asking the same thing about a different entity/filter.\n"
                context_section += f"Previous question was: \"{last_user_question}\"\n"
                context_section += f"Current question is: \"{question}\"\n\n"
                context_section += f"**CRITICAL INSTRUCTION**: Generate the EXACT SAME type of query AND visualization:\n"
                context_section += f"- Keep the same SELECT columns\n"
                context_section += f"- Keep the same JOINs\n"
                context_section += f"- Keep the same query structure\n"
                if last_visualization_type:
                    context_section += f"- **MUST use the same visualization type: \"{last_visualization_type}\" (DO NOT CHANGE THIS)**\n"
                context_section += f"- ONLY change the filter condition (e.g., name, year, category) to match: \"{question}\"\n"
                context_section += f"- Extract the new filter value from the current question and apply it in the WHERE clause\n\n"
            else:
                context_section += "\nThis appears to be a new question (not a follow-up).\n\n"
        
        prompt = f"""You are an expert SQL query generator for a faculty publication analytics database.

{self.schema_context}
{context_section}
## Your Task
Convert this natural language question into a SQL query:
"{question}"

## Example Query for Reference
{json.dumps(relevant_example, indent=2)}

## Instructions
1. Generate a valid PostgreSQL query using the schema above
2. Always include appropriate JOINs when querying across tables
3. Use proper WHERE clauses for filtering
4. Include GROUP BY ONLY when using aggregate functions (COUNT, SUM, AVG, etc.)
5. IMPORTANT: If selecting a column, either include it in GROUP BY or use an aggregate function
6. The collaborations table already has pre-computed collaboration_count - no GROUP BY needed
7. Add ORDER BY for sorted results
8. **ALWAYS add LIMIT clause (EXCEPT when user says "all")**:
   - If user says "all" or "show all" → **DO NOT add LIMIT** (return all matching records)
   - If user specifies a number (e.g., "5 recent", "top 10") → use that limit
   - If NO limit specified and NOT asking for "all" → DEFAULT to LIMIT 5
   - Examples: 
     * "recent publications" → LIMIT 5
     * "top publications" → LIMIT 5
     * "show all faculty with h-index > 10" → NO LIMIT (return all 8 faculty)
     * "list all publications by X" → NO LIMIT (return all publications)
   - Only omit LIMIT for: time series/trend data, queries with "all", or full dataset requests

## Understanding User Questions - CRITICAL
- **"Who" questions** = ALWAYS include author/faculty names in SELECT and GROUP BY
  * "Who published the most?" → SELECT a.name, COUNT(*) ... GROUP BY a.name
  * "Who has the highest h-index?" → SELECT a.name, a.h_index ...
  * "Who collaborated with X?" → SELECT collaborator names
- **"What" questions about counts** = May or may not need names
  * "What is the total count?" → Just COUNT(*)
  * "What are the top venues?" → SELECT venue names
- **"How many" questions** = Usually just COUNT, no names needed unless asking "how many per person"

## Name Matching Rules - CRITICAL
9. **Faculty/Author Names - SEARCH IN THE AUTHORS TABLE**:
   - To find publications by a specific author: JOIN with authors table and filter on authors.name
   - NEVER search for author names in publications.title or publications.dblp_key
   - Use ILIKE with flexible patterns to handle name variations
   - Names may include periods, middle initials, and different orderings:
     * "S Durga Bhavani" might be stored as "S. Durga Bhavani" (with period)
     * "Durga Bhavani" might be stored as "Durga Bhavani S." or "S. Durga Bhavani"
     * Use patterns like '%Durga%Bhavani%' to catch all variations
   - For single-letter initials, use patterns that work with or without periods:
     * Instead of ILIKE '%S Durga Bhavani%', use ILIKE '%Durga%Bhavani%'
     * Or use: (a2.name ILIKE '%S.%Durga%Bhavani%' OR a2.name ILIKE '%S %Durga%Bhavani%')
   
   CORRECT way to find publications by author:
   ```sql
   WHERE EXISTS (
       SELECT 1 FROM publication_authors pa2
       JOIN authors a2 ON pa2.author_id = a2.id
       WHERE pa2.publication_id = p.id 
       AND a2.name ILIKE '%Durga%Bhavani%'  -- Flexible pattern
   )
   ```
   
   WRONG (DO NOT DO THIS):
   ```sql
   WHERE p.title ILIKE '%Durga Bhavani%'  -- DON'T search in title
   WHERE p.dblp_key ILIKE '%Durga Bhavani%'  -- DON'T search in dblp_key
   WHERE a2.name ILIKE '%S Durga Bhavani%'  -- Too specific, won't match "S. Durga Bhavani"
   ```

9b. **CRITICAL: Displaying Publications WITH Authors (No Duplicates)**:
   - When listing publications, ALWAYS show author names using STRING_AGG with DISTINCT
   - This combines all unique authors into one comma-separated string per publication
   - Results: Each publication appears ONCE with ALL unique authors shown
   
   CORRECT - shows each publication ONCE with unique authors only:
   ```sql
   SELECT 
       p.title,
       STRING_AGG(DISTINCT a.name, ', ') as authors,
       p.year,
       p.publication_type,
       COALESCE(NULLIF(p.journal, ''), p.booktitle) as venue
   FROM publications p
   JOIN publication_authors pa ON p.id = pa.publication_id
   JOIN authors a ON pa.author_id = a.id
   WHERE EXISTS (
       SELECT 1 FROM publication_authors pa2
       JOIN authors a2 ON pa2.author_id = a2.id
       WHERE pa2.publication_id = p.id AND a2.name ILIKE '%Durga%Bhavani%'
   )
   GROUP BY p.id, p.title, p.year, p.publication_type, p.journal, p.booktitle
   ORDER BY p.year DESC
   LIMIT 5;
   ```
   
   NOTE: Use STRING_AGG(DISTINCT a.name, ', ') to avoid duplicate author names
   Do NOT use ORDER BY inside STRING_AGG when using DISTINCT (not compatible)
   
   WRONG - creates duplicate rows (one per co-author):
   ```sql
   SELECT p.title, a.name as author_name, p.year
   FROM publications p
   JOIN publication_authors pa ON p.id = pa.publication_id
   JOIN authors a ON pa.author_id = a.id
   WHERE a.name ILIKE '%Durga%Bhavani%'
   -- This returns one row per author per publication - BAD!
   ```
   
   **Column Selection Rules**:
   - **WHEN LISTING/SEARCHING PUBLICATIONS - ALWAYS INCLUDE THESE 5 COLUMNS**:
     1. p.title
     2. STRING_AGG(DISTINCT a.name, ', ') as authors  -- NEVER omit this!
     3. p.year
     4. p.publication_type
     5. COALESCE(NULLIF(p.journal, ''), p.booktitle) as venue
   - This applies to ALL publication queries: searching by title, by author, by venue, by year, etc.
   - **Even if user doesn't ask for authors, INCLUDE THEM** - they are essential context
   - NEVER include: volume, number, pages (too detailed, clutters display)
   - Use NULLIF to convert empty strings to NULL so conferences show booktitle properly

9c. **CRITICAL: ALWAYS Include JOINs When Showing Authors**:
   - **IF you use STRING_AGG(DISTINCT a.name, ', ') or reference authors table 'a'**:
   - **THEN you MUST include these JOINs in your FROM clause**:
     ```sql
     FROM publications p
     LEFT JOIN publication_authors pa ON p.id = pa.publication_id
     LEFT JOIN authors a ON pa.author_id = a.id
     ```
   - This applies to ALL queries that display authors, including:
     * Searching publications by title
     * Listing all publications
     * Filtering by venue, year, type, etc.
   - **WITHOUT these JOINs, you will get SQL error: "missing FROM-clause entry for table 'a'"**
   
   **Example - Searching publication by title with authors**:
   ```sql
   SELECT 
       p.title,
       STRING_AGG(DISTINCT a.name, ', ') as authors,
       p.year,
       p.publication_type,
       COALESCE(NULLIF(p.journal, ''), p.booktitle) as venue
   FROM publications p
   LEFT JOIN publication_authors pa ON p.id = pa.publication_id  -- REQUIRED!
   LEFT JOIN authors a ON pa.author_id = a.id                     -- REQUIRED!
   WHERE p.title ILIKE '%searched title%'
   GROUP BY p.id, p.title, p.year, p.publication_type, p.journal, p.booktitle
   ORDER BY p.year DESC
   LIMIT 5;
   ```

10. **Collaboration Network Queries - CRITICAL**:
   - When asked for "collaboration network" or "collaborations between faculty":
   - **IMPORTANT**: Faculty typically collaborate with external researchers, not with each other
   - Use: WHERE a1.is_faculty = true (only require one author to be faculty)
   - Do NOT use: WHERE a1.is_faculty = true AND a2.is_faculty = true (too restrictive, returns 0 results)
   - Query pattern:
   ```sql
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
   ```
   - Use visualization: "network_graph"
   - Add note: "Showing faculty members and their top collaborators (including external researchers)"

11. **When using partial matching, ALWAYS add a note**:
   - Example: "Note: Using flexible name matching to handle variations like 'S. Durga Bhavani', 'Durga Bhavani S.', etc."
   - Mention if multiple matches might be found

12. **SQL Syntax - CRITICAL**:
   - ALWAYS close ALL string literals with matching quotes
   - Check: every ILIKE '%text%' must have closing quote
   - Use parentheses for complex WHERE conditions with AND/OR
   - Example: WHERE (condition1 OR condition2) AND condition3

## Visualization Selection - CRITICAL
13. **For Simple/Single-Value Answers - Use "none" visualization**:
   - When the query returns a SINGLE number, count, or simple fact
   - Examples requiring NO visualization:
     * "How many publications does X have?" → single count
     * "What is the h-index of Y?" → single number
     * "When was the first publication?" → single year
     * "What is the total count of...?" → single number
   - For these, set: "visualization": "none"
   - Provide a conversational explanation that includes the actual answer
   - Example: "explanation": "Satish Srirama has published 78 papers in total."

14. **CRITICAL: Keywords Determine Format - Report vs List vs Visualize**:
   
   A. **Use "report" Format (Text/Paragraph)** when question contains:
      - "in the format" → user specifies custom format
      - "in the below format" → user wants specific layout
      - "report" → user wants report-style output
      - "format as" → user wants custom formatting
      - Key indicators:
        * Question includes line breaks or formatting instructions
        * Question mentions specific fields to display
        * User wants downloadable text format for official use
      - Examples:
        * "list all publications of X in the format:\nTitle\nAuthors\nDetails" → report
        * "generate report for faculty Y" → report
        * "show publications in the below format..." → report
      - For report format:
        * Still generate normal SQL query
        * Set visualization type to "report"
        * Frontend will format as text with download option
   
   B. **Use Table Format (No Chart)** when question contains:
      - "list" → user wants tabular list
      - "enumerate" → user wants enumerated table
      - Examples:
        * "list the number of publications..." → table
        * "list faculty publications..." → table
        * "enumerate the top authors..." → table
   
   C. **Use Visualization (Chart/Graph)** when question contains:
      - "show" → user wants visual chart
      - "display" → user wants visual representation
      - "visualize" → user wants chart
      - Examples:
        * "show publication trends..." → line_chart/bar_chart
        * "display faculty comparison..." → bar_chart
        * "show distribution of..." → pie_chart

15. **For Data that NEEDS Visualization (Charts/Graphs)**:
   Choose from these types:
   - line_chart: for time series trends (multiple data points over time)
   - bar_chart: for comparisons and rankings (multiple items to compare)
   - pie_chart: for distribution/proportions (multiple categories)
   - table: for detailed listings with multiple rows (when user says "list" or "enumerate")
   - network_graph: for relationships/collaborations
   - multi_line_chart: for comparing multiple series over time

16. **Decision Rule Priority**:
   1. If user says "list" or "enumerate" → ALWAYS use "table"
   2. If user says "show" or "display" → use appropriate chart (bar/line/pie)
   3. If query result is 1 row with 1-2 columns → visualization: "none"
   4. If query asks for trends/over time → use "line_chart" or "multi_line_chart"
   5. If query asks for comparison/ranking → use "bar_chart"
   6. If query result is multiple rows and no keyword → use "table" as default

## Response Format (JSON)
CRITICAL: You MUST generate actual, complete, executable SQL - NOT placeholders like "SELECT ..." or "..." 
The SQL must be ready to run in PostgreSQL immediately without any modifications.

{{
    "sql": "SELECT actual_column FROM actual_table WHERE actual_condition ORDER BY actual_order LIMIT 10",
    "visualization": "chart_type",
    "explanation": "Brief explanation of what the query returns",
    "note": "Any assumptions made (e.g., partial name matching used, date range assumed, etc.) - INCLUDE THIS if using ILIKE or making assumptions",
    "x_axis": "column name for x-axis (if applicable)",
    "y_axis": "column name for y-axis (if applicable)",
    "series": "column name for series grouping (if multi-line)",
    "report_format": "template string for report output (only if visualization=report, e.g., 'Title: {{title}}\nAuthors: {{authors}}\nYear: {{year}}')"
}}

Visualization types:
- "report" = Text/paragraph format with download option (use when user specifies format or wants report)
- "table" = Data table (use for lists and searches)
- "bar_chart", "pie_chart", "line_chart", "multi_line_chart" = Charts
- "network_graph" = Network visualization
- "none" = No visualization (simple text answer)

IMPORTANT: 
- The "sql" field must contain a COMPLETE, EXECUTABLE PostgreSQL query
- Do NOT use placeholders like "...", "SELECT ...", or "actual_column"  
- Use real table and column names from the schema provided above
- Always include the "note" field when:
  * Using ILIKE for partial name matching
  * Making assumptions about date ranges
  * Interpreting ambiguous terms
  * Handling potential variations in data

Generate the JSON response now:"""
        
        return prompt
    
    def _is_report_request(self, question: str) -> bool:
        """Detect if user is requesting a formatted publication report"""
        question_lower = question.lower()
        
        # Strong indicators for publication report
        report_indicators = [
            'generate report',
            'create report', 
            'publication report',
            'faculty report'
        ]
        
        # Check if question contains any report indicators
        has_indicator = any(indicator in question_lower for indicator in report_indicators)
        
        # Check if question mentions categorization (A, B, C format)
        has_categories = any(term in question_lower for term in ['category a', 'category b', 'category c', 'categorized', 'categories'])
        
        return has_indicator or has_categories
    
    def _build_report_prompt(self, question: str, conversation_history: Optional[List] = None) -> str:
        """Build specialized prompt for publication report generation"""
        
        # Extract faculty name from question
        faculty_name = self._extract_faculty_name(question)
        
        prompt = f"""You are an expert SQL query generator for generating standardized faculty publication reports.

{self.schema_context}

## TASK: Generate Publication Report in SCIS Standard Format

User Question: "{question}"
Detected Faculty: {faculty_name if faculty_name else "Not specified - will return all"}

## CRITICAL: Report Format Requirements

The output MUST follow the SCIS publication format structure:

**Category A: Books (Authored/Edited/Chapters)**
- Books Authored
- Books Edited  
- Books Chapter (Authorship)

**Category B: Research Papers** (Journal Publications)

**Category C: Conference Proceedings**

## Report Format Template (from scis_publications.md)

For each publication, format as:
[Category] [Number]. [Publication Type]: [Authors], [Author Role], [Title], [Indexing], [Volume], [Journal/Venue], [Pages], [Date].

### Examples from SCIS Format:

**Category A - Books:**
```
A 1. Books Authored: R. Buyya, C. Vecchiola, S. T. Selvi, S. Poojara, S. N. Srirama, Corresponding Author, Mastering Cloud Computing: Powering AI, Big Data, and IoT Applications, 2nd Edition, Mc Graw Hill, India, ISBN-13: 978-93-5532-950-9. ISBN-10: 93-5532-950-4., 01/07/2024.

A 2. Books Edited: Anirban Dasgupta, Rage Uday Kiran, Radwa El Shawi, Satish Srirama, Mainak Adhikari, Big Data and Artificial Intelligence: 12th International Conference, BDA 2024, Hyderabad, India,December 17–20, 2024, Proceedings, Springer, India, International, eBook ISBN: 978-3-031-81821-9, 01/03/2025.

A 3. Books Chapter (Authorship): Maria R. Read, C. K. Dehury, S. N. Srirama, R. Buyya, Deep Reinforcement Learning (DRL) -Based Methods for Serverless Stream Processing Engines: A Vision, Architectural Elements, and Future Directions in Book title: Resource Management in Distributed Systems (ISBN: 978-981-97-2643-1), Editor(s): A. Mukherjee, D. De, R. Buyya, Springer, -, 01/11/2024, pp. 285-314.
```

**Category B - Research Papers:**
```
B 1. Research Papers: T. R. Chhetri, C. K. Dehury, B. Varghese, Anna Fensel, S. N. Srirama, Rance J. DeLong, Co Author, Enabling privacy-aware interoperable and quality IoT data sharing with context, Web of Science, 157, Future Generation Computer Systems - Journal, 164-179, 01/08/2024.

B 2. Research Papers: Sucharitha Isukapalli, S. N. Srirama, Corresponding Author, A Systematic Survey on Fault-Tolerant Solutions for Distributed Data Analytics: Taxonomy, Comparison, and Future Directions, Web of Science, 53, Computer Science Review, 100660, 01/08/2024.
```

**Category C - Conference Proceedings:**
```
C 1. Conference Proceedings: Chinmaya Kumar Dehury, Satish Narayana Srirama, Integrating Serverless and DRL for Infrastructure Management in Streaming Data Processing across Edge-Cloud Continuum,Workshop on Engineering techniques for Distributed Computing Continuum Systems @ 44th IEEE International Conference on Distributed Computing Systems, 93-101, New Jersey, USA, 23/07/2024.
```

## SQL Query Requirements

1. **Query ALL publications for the faculty member**
2. **Group by publication_type to separate categories:**
   - 'book' → Category A (Books Authored)
   - 'proceedings', 'edited' → Category A (Books Edited)
   - 'incollection' → Category A (Books Chapter)
   - 'article' → Category B (Research Papers)
   - 'inproceedings' → Category C (Conference Proceedings)

3. **Required fields to SELECT:**
   - p.title
   - STRING_AGG(a.name, ', ' ORDER BY pa.author_position) as authors
   - p.year
   - p.publication_type
   - p.journal (for articles)
   - p.booktitle (for conferences)
   - p.publisher
   - p.volume
   - p.number
   - p.pages
   - p.doi
   - COALESCE(p.journal, p.booktitle) as venue

4. **Order by:** publication_type (to group categories), then year DESC (most recent first)

5. **Faculty Name Matching:** Use flexible ILIKE pattern: `a.name ILIKE '%{faculty_name}%'`

## Example SQL Query Structure:

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
    p.doi,
    TO_CHAR(p.year || '-01-01'::date, 'DD/MM/YYYY') as formatted_date
FROM publications p
JOIN publication_authors pa ON p.id = pa.publication_id
JOIN authors a ON pa.author_id = a.id
WHERE EXISTS (
    SELECT 1 FROM publication_authors pa2
    JOIN authors a2 ON pa2.author_id = a2.id
    WHERE pa2.publication_id = p.id 
    AND a2.name ILIKE '%{faculty_name if faculty_name else ""}%'
)
GROUP BY p.id, p.publication_type, p.title, p.year, p.journal, p.booktitle, p.publisher, p.volume, p.number, p.pages, p.doi
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

## Response JSON Format

{{
    "sql": "SELECT ... (complete executable SQL as shown above)",
    "visualization": "report",
    "explanation": "This report lists all publications by [Faculty Name] organized by category (A: Books, B: Research Papers, C: Conference Proceedings) as per SCIS standard format.",
    "report_format": "{{category}} {{number}}. {{publication_type_label}}: {{authors}}, {{author_role}}, {{title}}, {{indexing}}, {{volume}}, {{venue}}, {{pages}}, {{formatted_date}}.",
    "note": "Report generated in SCIS standard publication format with categories A (Books), B (Research Papers), and C (Conference Proceedings)",
    "categorization": {{
        "A": ["book", "proceedings", "incollection"],
        "B": ["article"],
        "C": ["inproceedings"]
    }}
}}

## Important Instructions:

1. **ALWAYS set visualization to "report"** for formatted publication reports
2. **Include ALL publications** - do NOT add LIMIT clause
3. **Use STRING_AGG(DISTINCT a.name, ', ')** to show all unique authors
4. **Order by category first, then year DESC** within each category
5. **Include report_format field** with template for frontend formatting
6. **Include categorization mapping** to help frontend organize output
7. **Extract faculty name** flexibly using ILIKE patterns
8. **Date format:** DD/MM/YYYY (e.g., 01/07/2024)

Generate the JSON response now:"""
        
        return prompt
    
    def _extract_faculty_name(self, question: str) -> Optional[str]:
        """Extract faculty name from question"""
        question_lower = question.lower()
        
        # Common patterns for faculty name extraction
        patterns = [
            r'publications? (?:by|of|from) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'(?:professor|dr\.?|faculty) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'for ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'report (?:on|for|of) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?: [A-Z][a-z]+)*?)\'s publications?',
        ]
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                name = match.group(1).strip()
                # Validate it looks like a name (2-4 words, each capitalized)
                name_parts = name.split()
                if 1 <= len(name_parts) <= 4 and all(part[0].isupper() for part in name_parts):
                    logger.info(f"📝 Extracted faculty name: {name}")
                    return name
        
        logger.info("📝 No specific faculty name detected - will query all publications")
        return None
    
    def _find_similar_example(self, question: str) -> Dict:
        """Find the most relevant example query based on question keywords"""
        question_lower = question.lower()
        
        # Check for report format requests - highest priority
        report_patterns = [
            'in the format', 'in the below format', 'report', 'format as',
            'in this format', 'generate report', 'publications report', 'publication report',
            'scis format', 'standard format', 'academic report'
        ]
        if any(pattern in question_lower for pattern in report_patterns):
            # User wants a formatted report - use publication_report example
            return self.examples.get('publication_report', self.examples.get('faculty_member_publications', {}))
        
        # Check for simple count/number queries - should use "none" visualization
        simple_query_patterns = [
            'how many', 'count', 'total number', 'what is the', 'h-index', 
            'h index', 'when was', 'what year', 'which year'
        ]
        if any(pattern in question_lower for pattern in simple_query_patterns):
            # This is likely a simple count/fact query
            return self.examples.get('simple_count', {})
        
        # Check if searching for a specific publication by title
        publication_search_patterns = ['who published', 'who wrote', 'who authored', 'paper titled', 
                                       'publication titled', 'article titled', 'find paper', 
                                       'find publication', 'search for paper']
        if any(pattern in question_lower for pattern in publication_search_patterns):
            return self.examples.get('publication_by_title', {})
        
        # Check if asking about a specific person (contains a name-like pattern)
        # Look for common faculty name patterns or words like "by", "from", "done by"
        person_indicators = ['by ', 'from ', 'done by', 'published by', 'written by', 'authored by']
        if any(indicator in question_lower for indicator in person_indicators):
            # Likely asking about a specific faculty member's publications
            return self.examples.get('faculty_member_publications', {})
        
        # Keyword matching
        if any(word in question_lower for word in ['trend', 'over time', 'year', 'timeline']):
            return self.examples.get('publications_by_year', {})
        elif any(word in question_lower for word in ['top', 'most', 'best', 'ranking', 'productive']):
            if 'venue' in question_lower or 'journal' in question_lower or 'conference' in question_lower:
                return self.examples.get('top_venues', {})
            else:
                return self.examples.get('top_faculty', {})
        elif any(word in question_lower for word in ['type', 'distribution', 'breakdown']):
            return self.examples.get('publication_types', {})
        elif any(word in question_lower for word in ['collaboration', 'co-author', 'work with', 'together']):
            return self.examples.get('collaborations', {})
        elif any(word in question_lower for word in ['recent', 'latest', 'new']):
            # If mentions a name AND "recent", use faculty_member_publications example
            if any(indicator in question_lower for indicator in ['by', 'from', 'of']):
                return self.examples.get('faculty_member_publications', {})
            return self.examples.get('recent_publications', {})
        elif any(word in question_lower for word in ['growth', 'change', 'compare']):
            return self.examples.get('faculty_growth', {})
        else:
            return self.examples.get('top_faculty', {})
    
    def _parse_llm_response(self, response: str, original_question: str) -> Dict:
        """Parse LLM response and extract JSON"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                
                # Validate SQL
                if 'sql' in result and result['sql']:
                    # Basic SQL validation
                    sql = result['sql'].strip()
                    if not sql.upper().startswith(('SELECT', 'WITH')):
                        raise ValueError("Invalid SQL: must start with SELECT or WITH")
                    
                    # Check for placeholder SQL
                    if '...' in sql or 'actual_column' in sql.lower() or 'actual_table' in sql.lower():
                        raise ValueError("Invalid SQL: contains placeholders instead of real SQL")
                    
                    # Check if SQL is suspiciously short (likely incomplete)
                    if len(sql) < 20:
                        raise ValueError("Invalid SQL: query too short, likely incomplete")
                    
                    # Check for unterminated strings
                    # Count single quotes - must be even
                    single_quotes = sql.count("'")
                    if single_quotes % 2 != 0:
                        raise ValueError("Invalid SQL: unterminated string literal (missing closing quote)")
                    
                    # Check for common syntax issues
                    if 'ILIKE' in sql.upper():
                        # Make sure ILIKE patterns are properly quoted
                        if "ILIKE '" in sql and sql.count("ILIKE '") != sql.count("ILIKE '%"):
                            # This is a heuristic check
                            pass
                    
                    # Ensure required fields
                    result['visualization'] = result.get('visualization', 'table')
                    result['explanation'] = result.get('explanation', 'Query results')
                    result['confidence'] = 0.85  # Default confidence
                    
                    return result
            
            # Fallback: try to extract SQL directly
            sql_match = re.search(r'SELECT[\s\S]+?(?:;|$)', response, re.IGNORECASE)
            if sql_match:
                return {
                    'sql': sql_match.group().strip(';').strip(),
                    'visualization': 'table',
                    'explanation': f'Results for: {original_question}',
                    'confidence': 0.6
                }
            
            raise ValueError("Could not parse SQL from response")
            
        except (json.JSONDecodeError, ValueError) as e:
            return {
                'error': f'Failed to generate valid SQL query: {str(e)}. Please try rephrasing your question or make it more specific.',
                'sql': None,
                'visualization': 'table',
                'explanation': 'Could not generate a valid query. The LLM may need a clearer question.',
                'note': 'Try asking in a different way, for example: "Show publications by [author name] from the last 5 years" or "List top 10 faculty by publication count"',
                'raw_response': response[:500] if 'response' in locals() else None
            }
    
    async def execute_query(self, sql: str, db: Session) -> List[Dict]:
        """Execute SQL query safely and return results"""
        try:
            # Basic SQL injection prevention
            if any(dangerous in sql.upper() for dangerous in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']):
                raise ValueError("Only SELECT queries are allowed")
            
            # Execute query
            result = db.execute(text(sql))
            
            # Convert to list of dicts
            columns = result.keys()
            rows = []
            for row in result:
                rows.append({col: self._serialize_value(val) for col, val in zip(columns, row)})
            
            return rows
            
        except Exception as e:
            raise ValueError(f"Query execution failed: {str(e)}")
    
    def _serialize_value(self, value):
        """Serialize SQL result values for JSON"""
        if value is None:
            return None
        elif isinstance(value, (int, float, str, bool)):
            return value
        elif isinstance(value, list):
            return value
        else:
            return str(value)
    
    def suggest_visualization(self, data: List[Dict], viz_type: str) -> Dict:
        """Generate visualization configuration based on data and type"""
        if not data:
            return {"type": "empty", "message": "No data to visualize"}
        
        columns = list(data[0].keys())
        
        viz_config = {
            "type": viz_type,
            "columns": columns
        }
        
        # Add type-specific configuration
        if viz_type == "line_chart":
            # Find x-axis (usually year or date) and y-axis (numeric)
            x_col = next((c for c in columns if 'year' in c.lower() or 'date' in c.lower()), columns[0])
            y_col = next((c for c in columns if isinstance(data[0].get(c), (int, float)) and c != x_col), columns[-1])
            viz_config.update({
                "x_axis": x_col,
                "y_axis": y_col,
                "title": f"{y_col.replace('_', ' ').title()} over {x_col.replace('_', ' ').title()}"
            })
        
        elif viz_type == "bar_chart":
            x_col = columns[0]
            y_col = next((c for c in columns if isinstance(data[0].get(c), (int, float))), columns[-1])
            viz_config.update({
                "x_axis": x_col,
                "y_axis": y_col,
                "title": f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}"
            })
        
        elif viz_type == "pie_chart":
            label_col = columns[0]
            value_col = next((c for c in columns if isinstance(data[0].get(c), (int, float))), columns[-1])
            viz_config.update({
                "label": label_col,
                "value": value_col,
                "title": f"Distribution of {label_col.replace('_', ' ').title()}"
            })
        
        elif viz_type == "table":
            viz_config.update({
                "title": "Query Results",
                "sortable": True,
                "searchable": True
            })
        
        elif viz_type == "network_graph":
            # For collaboration networks
            if len(columns) >= 3:
                viz_config.update({
                    "node1": columns[0],
                    "node2": columns[1],
                    "edge_weight": columns[2],
                    "title": "Collaboration Network"
                })
        
        return viz_config


async def test_agent():
    """Test the agent with sample questions"""
    agent = OllamaAgent()
    
    test_questions = [
        "Show publication trends over the last 10 years",
        "Who are the top 10 most productive faculty members?",
        "What are the most popular publication venues?",
        "Show collaborations between faculty members",
        "What types of publications do we have?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*80}")
        print(f"Q: {question}")
        print(f"{'='*80}")
        
        result = await agent.generate_sql(question)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())
