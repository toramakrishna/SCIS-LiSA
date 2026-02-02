# SCISLiSA - GitHub Codespaces Setup

This repository is configured to run seamlessly in GitHub Codespaces with all dependencies pre-installed.

## 🚀 Quick Start in Codespaces

1. **Create Codespace**:
   - Click the green "Code" button on GitHub
   - Select "Codespaces" tab
   - Click "Create codespace on backend"
   - ✅ **Works on free 2-core machine** (Ollama optional)

2. **Wait for Setup** (2-3 minutes):
   - The devcontainer will automatically:
     - Install Python and Node.js dependencies
     - Start PostgreSQL database
     - Create environment files
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
- **VS Code Extensions**:
  - Python, Pylance, Debugger
  - ESLint, Prettier
  - Tailwind CSS
  - PostgreSQL SQLTools
  - Docker

## 🎯 Available Features (Without Ollama)

- ✅ **Faculty Dashboard** - View faculty profiles, publications, h-index
- ✅ **Publications Browser** - Browse, search, and filter publications
- ✅ **Analytics Dashboard** - Charts and statistics
- ✅ **Collaboration Networks** - View co-author relationships
- ⚠️ **Natural Language Query** - Requires Ollama (see optional setup below)

## 🔧 Configuration

### Database
- Host: `localhost`
- Port: `5432`
- Database: `scislisa-service`
- User: `postgres`
- Password: `postgres`

## 🔧 Optional: Enable Natural Language Query (Ollama)

The Natural Language Query feature is **optional** and requires additional resources.

**To enable Ollama**:

1. **Edit `.devcontainer/docker-compose.yml`**:
   - Uncomment the `ollama` service section
   - Uncomment `- ollama` in the app's `depends_on`
   - Uncomment `ollama-data` in volumes

2. **Upgrade Codespace** (if needed):
   - Requires **4-core or 8-core machine**
   - Go to Codespace settings → Change machine type

3. **Rebuild Container**:
   - Press `F1` → "Dev Containers: Rebuild Container"
   - Wait 5-10 minutes for Ollama model download

4. **Update backend config**:
   - Uncomment `OLLAMA_URL` in `src/backend/.env`

### Ollama Configuration (when enabled)
- URL: `http://localhost:11434`
- Model: `llama3.2`
- Required RAM: 4GB+

## ⚠️ Performance Notes

**Default Setup (2-core)**:
- ✅ Works perfectly for all features except Natural Language Query
- ✅ Fast startup (2-3 minutes)
- ✅ Suitable for development and testing

**With Ollama Enabled**:
- Requires 4-core or 8-core machine
- Slower startup (5-10 minutes for model download)
- Higher memory usage (4GB+ RAM)

**Alternatives to Local Ollama**:

1. **Use Remote Ollama**:
   - Host Ollama on a separate server
   - Update `OLLAMA_URL` in `.env` to remote URL

2. **Switch to Cloud API**:
   - Replace Ollama with OpenAI/Anthropic
   - Modify `src/backend/mcp/agent.py`

## 🐛 Troubleshooting

### Natural Language Query not working
- This feature requires Ollama (see Optional Setup section above)
- Without Ollama, all other features work normally
- Error message will indicate if Ollama is not available

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
