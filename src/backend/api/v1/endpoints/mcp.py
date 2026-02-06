"""
MCP Analytics Endpoint
Natural Language Query Interface for Faculty Publications
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import logging

from config.db_config import get_db
from mcp.agent import OllamaAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["MCP Analytics"])

# Pydantic models
class QueryRequest(BaseModel):
    """Natural language query request"""
    question: str = Field(..., description="Natural language question about faculty publications")
    model: Optional[str] = Field("llama3.2", description="Ollama model to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show publication trends over the last 10 years",
                "model": "llama3.2"
            }
        }


class QueryResponse(BaseModel):
    """Query response with SQL, data, and visualization config"""
    question: str
    sql: Optional[str]
    explanation: str
    note: Optional[str] = None  # Assumptions or context about the query
    data: List[Dict[str, Any]]
    visualization: Dict[str, Any]
    row_count: int
    confidence: Optional[float] = None
    error: Optional[str] = None
    suggested_questions: List[str] = []


# Initialize agent (will be created per request to allow model selection)
def get_agent(model: str = "llama3.2") -> OllamaAgent:
    """Get or create Ollama agent instance"""
    return OllamaAgent(model=model)


def generate_follow_up_questions(question: str, data: List[Dict[str, Any]], sql: str) -> List[str]:
    """
    Generate contextual follow-up questions based on the query and results.
    
    Args:
        question: Original user question
        data: Query results
        sql: Generated SQL query
        
    Returns:
        List of suggested follow-up questions
    """
    suggestions = []
    
    # Analyze the question type and results
    question_lower = question.lower()
    has_data = len(data) > 0
    
    # Check what was asked about
    is_trend = any(word in question_lower for word in ['trend', 'over time', 'years', 'timeline'])
    is_top = any(word in question_lower for word in ['top', 'best', 'most', 'highest'])
    is_faculty = any(word in question_lower for word in ['faculty', 'professor', 'researcher'])
    is_venue = any(word in question_lower for word in ['venue', 'journal', 'conference'])
    is_collaboration = any(word in question_lower for word in ['collaboration', 'coauthor', 'together'])
    is_count = any(word in question_lower for word in ['how many', 'count', 'number of'])
    
    if has_data:
        # Get column names from first row
        columns = list(data[0].keys()) if data else []
        
        # Extract specific names/values from results for context
        first_row = data[0] if data else {}
        top_name = first_row.get('name', None)
        
        # For faculty queries with top results
        if is_faculty and is_top and 'name' in columns:
            # Get top 3 faculty names
            faculty_names = [row.get('name') for row in data[:3] if row.get('name')]
            if len(faculty_names) >= 2:
                name_list = f"{faculty_names[0]}, {faculty_names[1]}"
                if len(faculty_names) > 2:
                    name_list += f", and {faculty_names[2]}"
                suggestions.append(f"Show publication trends for {name_list} over the last 5 years")
                suggestions.append(f"What are the top venues where {faculty_names[0]} publishes?")
                suggestions.append(f"Show collaborations between {faculty_names[0]} and {faculty_names[1]}")
            elif len(faculty_names) == 1:
                suggestions.append(f"Show publication trends for {faculty_names[0]} over the last 5 years")
                suggestions.append(f"What are the top venues where {faculty_names[0]} publishes?")
                suggestions.append(f"Who are {faculty_names[0]}'s main collaborators?")
        elif is_faculty and not is_trend and top_name:
            suggestions.append(f"Show publication trends for {top_name} over time")
            suggestions.append(f"What are {top_name}'s most cited publications?")
            
        # For trend queries
        if is_trend:
            suggestions.append("Which faculty contributed most to publications in recent years?")
            suggestions.append("Break down publication trends by type")
            suggestions.append("Show the top publication venues for recent years")
            
        # For venue queries
        if is_venue and 'venue' in columns:
            venue_names = [row.get('venue') for row in data[:2] if row.get('venue')]
            if venue_names:
                suggestions.append(f"Which faculty publish most in {venue_names[0]}?")
                suggestions.append("Show publication trends in top venues over time")
            else:
                suggestions.append("Which faculty publish most in these venues?")
                suggestions.append("Show publication trends in these venues over time")
            
        # For collaboration queries
        if is_collaboration:
            suggestions.append("Show the most productive faculty collaborations")
            suggestions.append("Which faculty have the most diverse collaboration networks?")
            suggestions.append("Show publication counts for collaborative work")
            
        # Generic follow-ups based on result structure
        if 'name' in columns and 'publication_count' in columns and not suggestions:
            if top_name:
                suggestions.append(f"Show publication trends for {top_name}")
                suggestions.append(f"What venues does {top_name} publish in?")
        
        if 'year' in columns and not suggestions:
            suggestions.append("What are the top publication venues in recent years?")
            suggestions.append("Which faculty are most productive in recent years?")
            
    else:
        # No data returned
        suggestions.append("Show top 10 faculty by publication count")
        suggestions.append("Show publication trends over the last 10 years")
        suggestions.append("What are the most popular publication venues?")
        
    # Limit to 3 suggestions and make them unique
    return list(dict.fromkeys(suggestions))[:3]


# Pattern-based query handler - works without Ollama for common queries
async def handle_predefined_query(question: str, db: Session) -> Optional[QueryResponse]:
    """
    Handle common predefined queries without needing LLM/Ollama.
    Returns None if question doesn't match any pattern.
    """
    from sqlalchemy import text
    
    question_lower = question.lower()
    
    # Pattern 1: Top faculty by publication count
    if any(p in question_lower for p in ['top', 'most productive', 'most published']) and \
       any(p in question_lower for p in ['faculty', 'professor', 'researcher']):
        limit = 10
        # Try to extract number
        import re
        match = re.search(r'(\d+)', question)
        if match:
            limit = min(int(match.group(1)), 50)
        
        sql = f"""
        SELECT 
            f.id,
            f.name,
            COUNT(pa.publication_id) as publication_count
        FROM authors f
        LEFT JOIN publication_authors pa ON f.id = pa.author_id
        WHERE f.is_faculty = true
        GROUP BY f.id, f.name
        ORDER BY publication_count DESC
        LIMIT {limit}
        """
        
        try:
            result = db.execute(text(sql)).fetchall()
            data = [dict(row._mapping) for row in result]
            return QueryResponse(
                question=question,
                sql=sql,
                explanation=f"Top {limit} faculty by publication count",
                data=data,
                visualization={
                    "type": "bar_chart",
                    "title": f"Top {limit} Faculty by Publication Count",
                    "x_axis": "name",
                    "y_axis": "publication_count"
                },
                row_count=len(data),
                suggested_questions=["Show publication trends for " + (data[0]['name'] if data else 'faculty') + " over time"]
            )
        except Exception as e:
            logger.error(f"Error executing predefined query: {e}")
            return None
    
    # Pattern 2: Publications by year/trends
    if any(p in question_lower for p in ['trend', 'over time', 'by year', 'timeline', 'history', 'publication count', 'count by year']):
        # Group publications by year
        sql = """
        SELECT 
            COALESCE(year, 2023) as year,
            COUNT(*) as publication_count
        FROM publications
        GROUP BY COALESCE(year, 2023)
        ORDER BY year DESC
        LIMIT 20
        """
        
        try:
            result = db.execute(text(sql)).fetchall()
            data = [dict(row._mapping) for row in result]
            if data:  # Return if we have any data
                return QueryResponse(
                    question=question,
                    sql=sql,
                    explanation="Publication trends over time",
                    data=data,
                    visualization={
                        "type": "line_chart" if len(data) > 1 else "bar_chart",
                        "title": "Publication Trends Over Time",
                        "x_axis": "year",
                        "y_axis": "publication_count"
                    },
                    row_count=len(data),
                    suggested_questions=["Which faculty contributed most in recent years?"]
                )
        except Exception as e:
            logger.error(f"Error executing trends query: {e}")
            pass  # Continue to try next if this fails
    
    # Pattern 3: Top publication venues
    if any(p in question_lower for p in ['venue', 'journal', 'conference', 'published in']):
        # Get top venues from publication journal/booktitle fields
        sql = """
        SELECT 
            COALESCE(journal, booktitle, 'Unknown Venue') as venue,
            publication_type as venue_type,
            COUNT(id) as publication_count
        FROM publications
        WHERE journal IS NOT NULL OR booktitle IS NOT NULL
        GROUP BY COALESCE(journal, booktitle, 'Unknown Venue'), publication_type
        ORDER BY publication_count DESC
        LIMIT 15
        """
        
        try:
            result = db.execute(text(sql)).fetchall()
            data = [dict(row._mapping) for row in result]
            return QueryResponse(
                question=question,
                sql=sql,
                explanation="Top publication venues by count",
                data=data,
                visualization={
                    "type": "bar_chart",
                    "title": "Top Publication Venues",
                    "x_axis": "venue",
                    "y_axis": "publication_count"
                },
                row_count=len(data),
                suggested_questions=["Which faculty publish most in " + (data[0]['venue'] if data else 'these venues') + "?"]
            )
        except Exception as e:
            logger.error(f"Error executing venue query: {e}")
            return None
    
    return None


@router.post("/query", response_model=QueryResponse)
async def natural_language_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Convert natural language question to SQL and execute it.
    
    **Supported Question Types:**
    - Publication trends over time
    - Faculty rankings and statistics
    - Venue analysis (top journals/conferences)
    - Collaboration patterns
    - Publication type distributions
    - Recent publications
    - Comparative analysis
    
    **Examples:**
    - "Show publication trends over the last 10 years"
    - "Who are the top 10 most productive faculty members?"
    - "What are the most popular publication venues?"
    - "Show me collaborations between faculty members"
    - "How many publications did Satish Srirama publish in 2023?"
    - "Compare publication output of different faculty over time"
    
    **Returns:**
    - SQL query generated
    - Query results as JSON
    - Visualization configuration (chart type, axes, etc.)
    """
    try:
        # First, try predefined queries that don't require Ollama
        logger.info(f"Processing question: {request.question}")
        predefined_response = await handle_predefined_query(request.question, db)
        if predefined_response:
            logger.info("Using predefined query handler")
            return predefined_response
        
        # Fall back to LLM-based query
        logger.info("Attempting LLM-based query generation")
        agent = get_agent(request.model)
        
        # Generate SQL from natural language
        generation_result = await agent.generate_sql(request.question)
        
        if 'error' in generation_result:
            return QueryResponse(
                question=request.question,
                sql=None,
                explanation=generation_result.get('explanation', 'Failed to generate query'),
                data=[],
                visualization={"type": "error"},
                row_count=0,
                error=generation_result['error']
            )
        
        sql = generation_result['sql']
        logger.info(f"Generated SQL: {sql}")
        
        # Execute query
        try:
            data = await agent.execute_query(sql, db)
            logger.info(f"Query returned {len(data)} rows")
        except ValueError as e:
            return QueryResponse(
                question=request.question,
                sql=sql,
                explanation=generation_result['explanation'],
                data=[],
                visualization={"type": "error"},
                row_count=0,
                error=str(e)
            )
        
        # Generate visualization config
        viz_type = generation_result.get('visualization', 'table')
        viz_config = agent.suggest_visualization(data, viz_type)
        
        # Add metadata from generation
        if 'x_axis' in generation_result:
            viz_config['x_axis'] = generation_result['x_axis']
        if 'y_axis' in generation_result:
            viz_config['y_axis'] = generation_result['y_axis']
        if 'series' in generation_result:
            viz_config['series'] = generation_result['series']
        
        # Generate follow-up questions
        suggested_questions = generate_follow_up_questions(request.question, data, sql)
        
        return QueryResponse(
            question=request.question,
            sql=sql,
            explanation=generation_result['explanation'],
            note=generation_result.get('note'),  # Include the note if present
            data=data,
            visualization=viz_config,
            row_count=len(data),
            confidence=generation_result.get('confidence'),
            suggested_questions=suggested_questions
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/examples")
async def get_example_queries():
    """
    Get example natural language queries with expected outputs.
    
    **Returns:**
    List of example queries showing different question types and patterns.
    """
    from mcp.schema_context import get_example_queries
    
    examples = get_example_queries()
    
    return {
        "examples": [
            {
                "category": key,
                "question": example['question'],
                "visualization": example['visualization'],
                "sql_preview": example['sql'][:200] + "..." if len(example['sql']) > 200 else example['sql']
            }
            for key, example in examples.items()
        ]
    }


@router.get("/schema")
async def get_database_schema():
    """
    Get database schema information for understanding available data.
    
    **Returns:**
    Comprehensive schema documentation with tables, columns, and relationships.
    """
    from mcp.schema_context import get_schema_context
    
    return {
        "schema": get_schema_context(),
        "tables": ["authors", "publications", "publication_authors", "venues", "collaborations"],
        "description": "SCISLiSA faculty publication analytics database schema"
    }


@router.post("/validate-sql")
async def validate_sql_query(
    sql: str = Query(..., description="SQL query to validate"),
    db: Session = Depends(get_db)
):
    """
    Validate SQL query syntax and safety without executing it.
    
    **Parameters:**
    - sql: SQL query string
    
    **Returns:**
    Validation result with any errors or warnings.
    """
    try:
        agent = get_agent()
        
        # Check for dangerous operations
        sql_upper = sql.upper()
        dangerous_ops = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        found_dangerous = [op for op in dangerous_ops if op in sql_upper]
        
        if found_dangerous:
            return {
                "valid": False,
                "error": f"Dangerous operations not allowed: {', '.join(found_dangerous)}",
                "sql": sql
            }
        
        # Try to explain the query (doesn't execute it)
        from sqlalchemy import text
        db.execute(text(f"EXPLAIN {sql}"))
        
        return {
            "valid": True,
            "sql": sql,
            "message": "SQL query is valid"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "sql": sql
        }
