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
    data: List[Dict[str, Any]]
    visualization: Dict[str, Any]
    row_count: int
    confidence: Optional[float] = None
    error: Optional[str] = None


# Initialize agent (will be created per request to allow model selection)
def get_agent(model: str = "llama3.2") -> OllamaAgent:
    """Get or create Ollama agent instance"""
    return OllamaAgent(model=model)


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
        # Initialize agent
        agent = get_agent(request.model)
        
        # Generate SQL from natural language
        logger.info(f"Processing question: {request.question}")
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
        
        return QueryResponse(
            question=request.question,
            sql=sql,
            explanation=generation_result['explanation'],
            data=data,
            visualization=viz_config,
            row_count=len(data),
            confidence=generation_result.get('confidence')
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
