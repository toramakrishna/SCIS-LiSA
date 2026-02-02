#!/bin/bash

# SCISLiSA Quick Start Script
# Starts both backend and frontend services

set -e

echo "🚀 SCISLiSA Quick Start"
echo "======================="
echo ""

# Check Python
echo "🔍 Checking Python..."
python3 --version || { echo "❌ Python3 not found"; exit 1; }

# Check Node
echo "🔍 Checking Node.js..."
node --version || { echo "❌ Node.js not found"; exit 1; }

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
psql --version || { echo "❌ PostgreSQL not found"; exit 1; }

# Initialize database if needed
echo ""
echo "📦 Initializing database..."
cd /workspaces/SCISLiSA/src/backend
python3 << EOF
from config.db_config import Base, engine
from models.db_models import Author, Publication, Collaboration, DataSource, Venue
Base.metadata.create_all(bind=engine)
print("✅ Database tables ready")
EOF

# Start Backend
echo ""
echo "🔥 Starting Backend API (Port 8000)..."
cd /workspaces/SCISLiSA/src/backend
nohup .venv/bin/python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    cat /tmp/backend.log
    exit 1
fi

# Start Frontend
echo ""
echo "🔥 Starting Frontend (Port 5173)..."
cd /workspaces/SCISLiSA/src/frontend
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
