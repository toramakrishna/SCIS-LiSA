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
# 4. Set up database (create tables, etc.)
# ============================================
echo "🗄️  Setting up database..."
cd /workspaces/SCISLiSA/src/backend
# You may need to run migrations or setup scripts here
# Example:
# python -c "from models.db_models import Base; from config.db_config import engine; Base.metadata.create_all(engine)"

# ============================================
# 5. Pull Ollama model
# ============================================
echo "🤖 Setting up Ollama..."
# Wait for Ollama service to be ready
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "   Waiting for Ollama service..."
    sleep 3
done

echo "📥 Pulling llama3.2 model (this may take several minutes)..."
curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3.2"}' || echo "⚠️  Failed to pull Ollama model. You may need to do this manually."

# ============================================
# 6. Create environment files if needed
# ============================================
echo "📝 Creating environment configuration..."
cd /workspaces/SCISLiSA/src/backend

if [ ! -f ".env" ]; then
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://scislisa:scislisa_pass@localhost:5432/scislisa_db
POSTGRES_USER=scislisa
POSTGRES_PASSWORD=scislisa_pass
POSTGRES_DB=scislisa_db

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
echo "⚠️  Note: Ollama requires 4GB+ RAM. If you encounter issues, consider:"
echo "   - Using a larger Codespaces machine (4-core or 8-core)"
echo "   - Using a remote Ollama instance"
echo "   - Switching to OpenAI/Anthropic API"
echo ""
