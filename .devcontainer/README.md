# SCISLiSA - GitHub Codespaces Setup

This repository is configured to run seamlessly in GitHub Codespaces with all dependencies pre-installed.

## 🚀 Quick Start in Codespaces

1. **Create Codespace**:
   - Click the green "Code" button on GitHub
   - Select "Codespaces" tab
   - Click "Create codespace on backend"
   - ⚠️ **Recommended**: Choose a **4-core or 8-core machine** for better Ollama performance

2. **Wait for Setup**:
   - The devcontainer will automatically:
     - Install Python and Node.js dependencies
     - Start PostgreSQL database
     - Start Ollama service
     - Pull the llama3.2 model (takes 5-10 minutes)
   - Check the terminal for setup progress

3. **Start the Application**:

   Open two terminals in Codespaces:

   **Terminal 1 - Backend**:
   ```bash
   cd src/backend
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   **Terminal 2 - Frontend**:
   ```bash
   cd src/frontend
   npm run dev
   ```

4. **Access the Application**:
   - Frontend: Click the "Open in Browser" notification for port 5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📦 What's Included

- **Python 3.11** with FastAPI and all backend dependencies
- **Node.js 20** with Vite and React
- **PostgreSQL 15** database
- **Ollama** with llama3.2 model
- **VS Code Extensions**:
  - Python, Pylance, Debugger
  - ESLint, Prettier
  - Tailwind CSS
  - PostgreSQL SQLTools
  - Docker

## 🔧 Configuration

### Database
- Host: `localhost`
- Port: `5432`
- Database: `scislisa_db`
- User: `scislisa`
- Password: `scislisa_pass`

### Ollama
- URL: `http://localhost:11434`
- Model: `llama3.2`

## ⚠️ Performance Notes

**Ollama Resource Requirements**:
- Minimum: 4GB RAM
- Recommended: 8GB+ RAM
- The free 2-core Codespace may struggle with Ollama

**If Ollama is too slow**:

1. **Upgrade Codespace Machine**:
   - Click the Codespace name > Change machine type
   - Select 4-core or 8-core

2. **Use Remote Ollama** (Alternative):
   - Host Ollama on a separate server
   - Update `OLLAMA_URL` in `.env`

3. **Switch to Cloud API** (Alternative):
   - Replace Ollama with OpenAI/Anthropic
   - Modify `src/backend/mcp/agent.py`

## 🐛 Troubleshooting

### Ollama model not downloading
```bash
# Manually pull the model
curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3.2"}'
```

### Database connection issues
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432 -U scislisa

# Restart PostgreSQL (if needed)
# In .devcontainer terminal, rebuild container
```

### Port forwarding issues
- Go to "Ports" tab in VS Code
- Make sure ports 5173, 8000 are set to "Public"

## 📝 Manual Setup (if auto-setup fails)

```bash
# Backend
cd src/backend
pip install -r requirements.txt

# Frontend
cd src/frontend
npm install

# Database (if tables don't exist)
cd src/backend
python -c "from models.db_models import Base; from config.db_config import engine; Base.metadata.create_all(engine)"
```

## 🔄 Rebuilding Container

If you need to rebuild the devcontainer:
1. Press `F1` or `Cmd+Shift+P`
2. Type "Rebuild Container"
3. Select "Dev Containers: Rebuild Container"

## 📚 Additional Resources

- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [Dev Container Spec](https://containers.dev/)
- [Ollama Documentation](https://ollama.ai/docs)
