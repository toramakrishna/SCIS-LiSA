"""
MCP Module Initialization
"""

from .agent import OllamaAgent
from .schema_context import get_schema_context, get_example_queries

__all__ = [
    'OllamaAgent',
    'get_schema_context',
    'get_example_queries'
]
