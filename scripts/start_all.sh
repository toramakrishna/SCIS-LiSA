#!/bin/bash

# SCISLiSA Quick Start Script
# Starts both backend and frontend services
# Compatible with both Codespaces and local environments

set -e

echo "🚀 SCISLiSA Quick Start"
echo "======================="
echo ""

# Detect environment
if [ -d "/workspaces/SCISLiSA" ]; then
    ENV_TYPE="codespaces"
    echo "🌐 Environment: GitHub Codespaces"
else
    ENV_TYPE="local"
    echo "💻 Environment: Local"
fi
echo ""

# Check Python
echo "🔍 Checking Python..."
python3 --version || { echo "❌ Python3 not found"; exit 1; }

# Check Node
echo "🔍 Checking Node.js..."
node --version || { echo "❌ Node.js not found"; exit 1; }

# Check PostgreSQL (client)
echo "🔍 Checking PostgreSQL client..."
psql --version || { echo "❌ PostgreSQL client not found"; exit 1; }

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "📂 Project root: $PROJECT_ROOT"

echo "📂 Project root: $PROJECT_ROOT"

# Determine Python command based on environment
if [ "$ENV_TYPE" = "local" ]; then
    # Check for virtual environment
    if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
        PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
        echo "🐍 Using virtual environment: .venv"
    else
        PYTHON_CMD="python3"
        echo "🐍 Using system Python"
    fi
else
    PYTHON_CMD="python3"
    echo "🐍 Using Python: python3"
fi

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src/backend:$PYTHONPATH"

# Initialize database if needed
echo ""
echo "📦 Initializing database..."
cd "$PROJECT_ROOT/src/backend"
$PYTHON_CMD << EOF
from config.db_config import Base, engine
from models.db_models import Author, Publication, Collaboration, DataSource, Venue
Base.metadata.create_all(bind=engine)
print("✅ Database tables ready")
EOF

# Start Backend
echo ""
echo "🔥 Starting Backend API (Port 8000)..."
cd "$PROJECT_ROOT/src/backend"
nohup $PYTHON_CMD -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ Backend failed to start"
    cat /tmp/backend.log | tail -20
    exit 1
  fi
  sleep 1
done

# Start Frontend
echo ""
echo "🔥 Starting Frontend (Port 5173)..."
cd "$PROJECT_ROOT/src/frontend"
npm install > /dev/null 2>&1
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 5

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID  # Backend"
echo "   kill $FRONTEND_PID # Frontend"
echo ""
