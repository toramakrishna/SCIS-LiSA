#!/bin/bash

# Quick Start Script for MCP Agent Testing

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       SCISLiSA MCP Agent - Quick Start & Test Guide           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Ollama is running
echo "🔍 Checking Ollama service..."
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not running!"
    echo ""
    echo "Please start Ollama:"
    echo "  Terminal 1: ollama serve"
    echo ""
    echo "Then pull the model:"
    echo "  Terminal 2: ollama pull llama3.2"
    echo ""
    exit 1
fi

# Check if model is available
echo ""
echo "🔍 Checking for llama3.2 model..."
if ollama list | grep -q "llama3.2"; then
    echo "✅ llama3.2 model found"
else
    echo "⚠️  llama3.2 model not found"
    echo "Downloading model (this may take a few minutes)..."
    ollama pull llama3.2
fi

# Check database connection
echo ""
echo "🔍 Checking database connection..."
if docker ps | grep -q postgres; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL is not running!"
    echo "Please start PostgreSQL first"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  All Prerequisites Met!                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Offer to run tests
read -p "Would you like to run the MCP agent tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧪 Running MCP Agent Tests..."
    echo ""
    .venv/bin/python test_mcp.py
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    How to Use MCP Agent                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Start FastAPI server (if not already running):"
echo "   .venv/bin/python -m uvicorn api.main:app --reload --port 8000"
echo ""
echo "2. Test with curl:"
echo "   curl -X POST http://localhost:8000/api/v1/mcp/query \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"question\": \"Show top 10 faculty by publications\"}'"
echo ""
echo "3. View API documentation:"
echo "   http://localhost:8000/docs#/MCP%20Analytics"
echo ""
echo "4. See example queries:"
echo "   curl http://localhost:8000/api/v1/mcp/examples | jq"
echo ""
echo "5. Read full documentation:"
echo "   cat MCP_GUIDE.md"
echo ""
