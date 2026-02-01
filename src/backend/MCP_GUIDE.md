# MCP Agent - Natural Language to SQL

## Overview

The MCP (Model Context Protocol) agent converts natural language questions about faculty publications into SQL queries, executes them, and returns results with appropriate visualization recommendations.

## Architecture

```
User Question (NL)
      ↓
  Ollama LLM (llama3.2)
      ↓
  SQL Generation (with schema context)
      ↓
  Query Execution (PostgreSQL)
      ↓
  Result Formatting + Visualization Config
      ↓
  JSON Response (data + chart metadata)
```

## Components

### 1. Schema Context (`mcp/schema_context.py`)
- Complete database schema documentation
- Table relationships and indexes
- Example query patterns for common questions
- Used as context for LLM prompt

### 2. Ollama Agent (`mcp/agent.py`)
- Connects to local Ollama instance (port 11434)
- Builds prompts with schema context
- Parses LLM responses to extract SQL
- Executes queries safely (read-only)
- Suggests appropriate visualizations

### 3. MCP Endpoints (`api/v1/endpoints/mcp.py`)
- **POST /api/v1/mcp/query** - Main NL query endpoint
- **GET /api/v1/mcp/examples** - Sample queries
- **GET /api/v1/mcp/schema** - Database schema info
- **POST /api/v1/mcp/validate-sql** - Validate SQL syntax

## Prerequisites

### Install Ollama

**macOS:**
```bash
brew install ollama
ollama serve
```

**Download Model:**
```bash
ollama pull llama3.2
```

**Verify:**
```bash
curl http://localhost:11434/api/version
```

## Usage

### 1. Start Services

**Terminal 1 - Ollama:**
```bash
ollama serve
```

**Terminal 2 - FastAPI:**
```bash
cd src/backend
.venv/bin/python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Natural Language Queries

**Example 1: Publication Trends**
```bash
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show publication trends over the last 10 years"
  }'
```

**Response:**
```json
{
  "question": "Show publication trends over the last 10 years",
  "sql": "SELECT year, COUNT(*) as publications FROM publications WHERE has_faculty_author = true AND year >= 2015 GROUP BY year ORDER BY year",
  "explanation": "Publication count by year for the last decade",
  "data": [
    {"year": 2015, "publications": 45},
    {"year": 2016, "publications": 52},
    ...
  ],
  "visualization": {
    "type": "line_chart",
    "x_axis": "year",
    "y_axis": "publications",
    "title": "Publications over Year"
  },
  "row_count": 10,
  "confidence": 0.95
}
```

**Example 2: Top Faculty**
```bash
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who are the top 10 most productive faculty members?"
  }'
```

**Example 3: Collaboration Network**
```bash
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me the top collaborations between faculty"
  }'
```

**Example 4: Specific Faculty**
```bash
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many publications did Satish Srirama publish in 2024?"
  }'
```

### 3. Get Example Queries

```bash
curl http://localhost:8000/api/v1/mcp/examples
```

### 4. View Database Schema

```bash
curl http://localhost:8000/api/v1/mcp/schema
```

### 5. Validate SQL

```bash
curl -X POST "http://localhost:8000/api/v1/mcp/validate-sql?sql=SELECT%20*%20FROM%20authors%20LIMIT%2010"
```

## Supported Question Types

### 1. Time Series / Trends
- "Show publication trends over the years"
- "How has publication output changed since 2020?"
- "Plot yearly publication counts"

**→ Visualization: Line Chart**

### 2. Rankings / Top Lists
- "Who are the most productive faculty?"
- "Top 10 publication venues"
- "Which faculty have the most collaborations?"

**→ Visualization: Bar Chart**

### 3. Distributions
- "What types of publications do we have?"
- "Distribution of publications by type"
- "Breakdown of articles vs conference papers"

**→ Visualization: Pie Chart**

### 4. Collaborations
- "Show collaborations between faculty"
- "Who does Satish Srirama collaborate with?"
- "Find co-authorship patterns"

**→ Visualization: Network Graph**

### 5. Detailed Listings
- "Show recent publications"
- "List all publications from 2024"
- "Get publications by Alok Singh"

**→ Visualization: Table**

### 6. Comparisons
- "Compare publication output of different faculty"
- "How do publication trends differ across faculty?"

**→ Visualization: Multi-line Chart**

## Visualization Types

### 1. Line Chart
```json
{
  "type": "line_chart",
  "x_axis": "year",
  "y_axis": "publications",
  "title": "Publications over Year",
  "data": [...]
}
```

### 2. Bar Chart
```json
{
  "type": "bar_chart",
  "x_axis": "name",
  "y_axis": "publications",
  "title": "Publications by Name",
  "data": [...]
}
```

### 3. Pie Chart
```json
{
  "type": "pie_chart",
  "label": "publication_type",
  "value": "count",
  "title": "Distribution of Publication Type",
  "data": [...]
}
```

### 4. Table
```json
{
  "type": "table",
  "columns": ["title", "year", "authors"],
  "sortable": true,
  "searchable": true,
  "data": [...]
}
```

### 5. Network Graph
```json
{
  "type": "network_graph",
  "node1": "faculty1",
  "node2": "faculty2",
  "edge_weight": "joint_papers",
  "title": "Collaboration Network",
  "data": [...]
}
```

## Advanced Features

### Custom Model Selection

Use different Ollama models:

```bash
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show top venues",
    "model": "llama3.1"
  }'
```

### Error Handling

The agent handles various error cases:

- **Invalid SQL**: Returns error with explanation
- **Dangerous operations**: Blocks DROP, DELETE, UPDATE, etc.
- **Ollama unavailable**: Returns helpful error message
- **Empty results**: Returns appropriate empty state

### SQL Validation

Validate queries before execution:

```python
{
  "valid": true,
  "sql": "SELECT * FROM authors LIMIT 10",
  "message": "SQL query is valid"
}
```

## Frontend Integration

### React Component Example

```jsx
import React, { useState } from 'react';
import { LineChart, BarChart, PieChart } from 'recharts';

function NLQueryInterface() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);

  const handleQuery = async () => {
    const response = await fetch('/api/v1/mcp/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    setResult(data);
  };

  const renderVisualization = () => {
    if (!result) return null;
    
    const { visualization, data } = result;
    
    switch (visualization.type) {
      case 'line_chart':
        return <LineChart data={data} />;
      case 'bar_chart':
        return <BarChart data={data} />;
      case 'pie_chart':
        return <PieChart data={data} />;
      case 'table':
        return <DataTable data={data} />;
      default:
        return <pre>{JSON.stringify(data, null, 2)}</pre>;
    }
  };

  return (
    <div>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleQuery}>Query</button>
      
      {result && (
        <div>
          <h3>{result.explanation}</h3>
          <details>
            <summary>SQL Query</summary>
            <code>{result.sql}</code>
          </details>
          {renderVisualization()}
        </div>
      )}
    </div>
  );
}
```

## Testing

### Run Agent Tests

```bash
cd src/backend
.venv/bin/python -m mcp.agent
```

This will test the agent with sample questions.

### Test All Endpoints

```bash
# Get examples
curl http://localhost:8000/api/v1/mcp/examples | jq

# Test query
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show top 5 faculty by publications"}' | jq

# Validate SQL
curl -X POST "http://localhost:8000/api/v1/mcp/validate-sql?sql=SELECT COUNT(*) FROM publications" | jq
```

## Troubleshooting

### Ollama Not Running

**Error:** `Ollama API error: Connection refused`

**Solution:**
```bash
ollama serve
```

### Model Not Found

**Error:** `Model llama3.2 not found`

**Solution:**
```bash
ollama pull llama3.2
```

### Slow Query Generation

- Reduce model temperature (already set to 0.1)
- Use smaller/faster model: `llama3.1` or `mistral`
- Consider query caching for repeated questions

### Invalid SQL Generated

- Check schema context accuracy
- Review example queries
- Adjust prompt engineering in `agent.py`

## Performance Optimization

1. **Query Caching**: Cache generated SQL for common questions
2. **Result Caching**: Cache query results with TTL
3. **Model Selection**: Use faster models for simple queries
4. **Connection Pooling**: Reuse database connections
5. **Async Processing**: Use async/await throughout

## Security

✅ **Read-only queries**: Only SELECT statements allowed  
✅ **SQL injection prevention**: Blocks dangerous keywords  
✅ **Query validation**: Syntax check before execution  
✅ **Error sanitization**: No raw database errors exposed  

## Next Steps

- [ ] Add query result caching (Redis)
- [ ] Implement query history tracking
- [ ] Add user authentication for queries
- [ ] Support multi-turn conversations
- [ ] Add query explanation feature
- [ ] Implement forecast/prediction queries
- [ ] Add export functionality (CSV, PDF)

## API Documentation

Full interactive API documentation available at:
**http://localhost:8000/docs#/MCP%20Analytics**
