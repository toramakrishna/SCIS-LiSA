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
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for more deterministic SQL
                            "top_p": 0.9
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse the LLM response
                return self._parse_llm_response(result["response"], question)
                
        except httpx.HTTPError as e:
            return {
                "error": f"Ollama API error: {str(e)}",
                "sql": None,
                "visualization": "table",
                "explanation": "Failed to generate SQL query"
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
9. Choose the most appropriate visualization type:
   - line_chart: for time series trends
   - bar_chart: for comparisons and rankings
   - pie_chart: for distribution/proportions
   - table: for detailed listings
   - network_graph: for relationships/collaborations
   - multi_line_chart: for comparing multiple series over time

## Response Format (JSON)
{{
    "sql": "Your SQL query here",
    "visualization": "chart_type",
    "explanation": "Brief explanation of what the query returns",
    "x_axis": "column name for x-axis (if applicable)",
    "y_axis": "column name for y-axis (if applicable)",
    "series": "column name for series grouping (if multi-line)"
}}

Generate the JSON response now:"""
        
        return prompt
    
    def _find_similar_example(self, question: str) -> Dict:
        """Find the most relevant example query based on question keywords"""
        question_lower = question.lower()
        
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
                'error': f'Failed to parse LLM response: {str(e)}',
                'sql': None,
                'visualization': 'table',
                'explanation': 'Could not generate query',
                'raw_response': response[:500]
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
