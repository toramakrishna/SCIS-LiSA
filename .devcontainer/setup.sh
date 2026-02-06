#!/bin/bash
set -e

echo "🚀 Setting up SCISLiSA Development Environment..."

# Navigate to workspace root
cd /workspaces/SCISLiSA

# ============================================
# 1. Install Backend Dependencies
# ============================================
echo "📦 Installing Python backend dependencies..."
cd src/backend
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Backend dependencies installed"
else
    echo "⚠️  requirements.txt not found in src/backend"
fi

# ============================================
# 2. Install Frontend Dependencies
# ============================================
echo "📦 Installing Node.js frontend dependencies..."
cd ../frontend
if [ -f "package.json" ]; then
    npm install
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  package.json not found in src/frontend"
fi

# ============================================
# 3. Wait for PostgreSQL to be ready
# ============================================
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h localhost -p 5432 -U scislisa > /dev/null 2>&1; do
    echo "   PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "✅ PostgreSQL is ready"

# ============================================
# 3.5. Create additional databases
# ============================================
echo "🗄️  Creating additional databases..."
psql -h localhost -U postgres -d postgres -c "SELECT 1 FROM pg_database WHERE datname = 'certification_service'" | grep -q 1 || \
    psql -h localhost -U postgres -d postgres -c "CREATE DATABASE certification_service"
echo "✅ Additional databases ready"

# ============================================
# 4. Set up database (create tables, etc.)
# ============================================
echo "🗄️  Setting up database..."
cd /workspaces/SCISLiSA/src/backend
# You may need to run migrations or setup scripts here
# Example:
# python -c "from models.db_models import Base; from config.db_config import engine; Base.metadata.create_all(engine)"

# ============================================
# 5. Create environment files if needed
# ============================================
echo "📝 Creating environment configuration..."
cd /workspaces/SCISLiSA/src/backend

if [ ! -f ".env" ]; then
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/scislisa-service
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=scislisa-service

# Ollama Configuration
OLLAMA_URL=http://localhost:11434

# Application Settings
ENVIRONMENT=development
DEBUG=True
EOF
    echo "✅ Created .env file"
fi

# ============================================
# 7. Success Message
# ============================================
echo ""
echo "✨ Setup Complete! ✨"
echo ""
echo "📝 Quick Start Commands:"
echo "   Backend:  cd src/backend && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo "   Frontend: cd src/frontend && npm run dev"
echo ""
echo "🌐 Access URLs (after starting services):"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "ℹ️  Available Features:"
echo "   ✅ Faculty Dashboard - View faculty profiles and publications"
echo "   ✅ Publications - Browse and filter publications"
echo "   ✅ Analytics - Publication trends and statistics"
echo "   ⚠️  Natural Language Query - Requires Ollama (not included by default)"
echo ""
echo "💡 To enable Natural Language Query:"
echo "   1. Uncomment Ollama service in .devcontainer/docker-compose.yml"
echo "   2. Rebuild container (requires 4-core or 8-core Codespace)"
echo "   3. Update OLLAMA_URL in src/backend/.env"
echo ""
