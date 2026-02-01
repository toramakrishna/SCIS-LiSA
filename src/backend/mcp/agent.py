"""
MCP Agent - Natural Language to SQL Query Generator
Uses Ollama LLM to convert natural language questions to SQL queries
"""

import json
import re
from typing import Dict, List, Optional, Tuple
import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from mcp.schema_context import get_schema_context, get_example_queries


class OllamaAgent:
    """Ollama-based agent for NL-to-SQL conversion"""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.schema_context = get_schema_context()
        self.examples = get_example_queries()
    
    async def generate_sql(self, question: str) -> Dict:
        """
        Generate SQL query from natural language question
        
        Returns:
            {
                "sql": "SELECT ...",
                "visualization": "line_chart|bar_chart|pie_chart|table|network_graph",
                "explanation": "What this query does",
                "confidence": 0.95
            }
        """
        # Build prompt with schema context and examples
        prompt = self._build_prompt(question)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:  # Increased timeout for complex queries
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",  # Request JSON format explicitly
                        "options": {
                            "temperature": 0.1,  # Low temperature for more deterministic SQL
                            "top_p": 0.9,
                            "num_predict": 1000  # Allow longer responses for complex queries
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse the LLM response
                return self._parse_llm_response(result["response"], question)
                
        except httpx.HTTPError as e:
            return {
                "error": f"Ollama API error: {str(e)}. Make sure Ollama is running and the model '{self.model}' is available.",
                "sql": None,
                "visualization": "table",
                "explanation": "Failed to connect to LLM service",
                "note": "Check if Ollama is running with: ollama list"
            }
    
    def _build_prompt(self, question: str) -> str:
        """Build comprehensive prompt with schema and examples"""
        
        # Find most relevant example
        relevant_example = self._find_similar_example(question)
        
        prompt = f"""You are an expert SQL query generator for a faculty publication analytics database.

{self.schema_context}

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
8. Limit results to reasonable numbers (10-50 for lists, no limit for time series)

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
   - Use ILIKE '%partial_name%' for partial, case-insensitive matching
   - Example: "Durga Bhavani" may be stored as "Durga Bhavani S." or "S. Durga Bhavani"
   
   CORRECT way to find publications by author:
   ```sql
   WHERE EXISTS (
       SELECT 1 FROM publication_authors pa2
       JOIN authors a2 ON pa2.author_id = a2.id
       WHERE pa2.publication_id = p.id 
       AND a2.name ILIKE '%Durga Bhavani%'
   )
   ```
   
   WRONG (DO NOT DO THIS):
   ```sql
   WHERE p.title ILIKE '%Durga Bhavani%'  -- DON'T search in title
   WHERE p.dblp_key ILIKE '%Durga Bhavani%'  -- DON'T search in dblp_key
   ```

10. **When using partial matching, ALWAYS add a note**:
   - Example: "Note: Using partial name matching for 'Durga Bhavani' to catch variations like 'Durga Bhavani S.'"
   - Mention if multiple matches might be found

11. **SQL Syntax - CRITICAL**:
   - ALWAYS close ALL string literals with matching quotes
   - Check: every ILIKE '%text%' must have closing quote
   - Use parentheses for complex WHERE conditions with AND/OR
   - Example: WHERE (condition1 OR condition2) AND condition3

## Visualization Selection - CRITICAL
12. **For Simple/Single-Value Answers - Use "none" visualization**:
   - When the query returns a SINGLE number, count, or simple fact
   - Examples requiring NO visualization:
     * "How many publications does X have?" → single count
     * "What is the h-index of Y?" → single number
     * "When was the first publication?" → single year
     * "What is the total count of...?" → single number
   - For these, set: "visualization": "none"
   - Provide a conversational explanation that includes the actual answer
   - Example: "explanation": "Satish Srirama has published 78 papers in total."

13. **For Data that NEEDS Visualization**:
   Choose from these types:
   - line_chart: for time series trends (multiple data points over time)
   - bar_chart: for comparisons and rankings (multiple items to compare)
   - pie_chart: for distribution/proportions (multiple categories)
   - table: for detailed listings with multiple rows
   - network_graph: for relationships/collaborations
   - multi_line_chart: for comparing multiple series over time

14. **Decision Rule**:
   - If query result is 1 row with 1-2 columns → visualization: "none"
   - If query result is multiple rows or complex data → use appropriate chart
   - If asking for a list (even if short) → use "table"
   - table: for detailed listings
   - network_graph: for relationships/collaborations
   - multi_line_chart: for comparing multiple series over time

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
    "series": "column name for series grouping (if multi-line)"
}}

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
    
    def _find_similar_example(self, question: str) -> Dict:
        """Find the most relevant example query based on question keywords"""
        question_lower = question.lower()
        
        # Check for simple count/number queries - should use "none" visualization
        simple_query_patterns = [
            'how many', 'count', 'total number', 'what is the', 'h-index', 
            'h index', 'when was', 'what year', 'which year'
        ]
        if any(pattern in question_lower for pattern in simple_query_patterns):
            # This is likely a simple count/fact query
            return self.examples.get('simple_count', {})
        
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
            "data": data,
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
