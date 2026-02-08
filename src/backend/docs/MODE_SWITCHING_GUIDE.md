# Quick Mode Switching Demo

## Current Setup: ✅ Working

Your SCISLiSA backend now supports **flexible Ollama configuration** based on environment mode.

### 🎯 Quick Switch Commands

#### Switch to Cloud Mode (Codespaces/Production)
```bash
# Edit .env file
OLLAMA_MODE=cloud
```

#### Switch to Local Mode (Local Development)
```bash
# Edit .env file
OLLAMA_MODE=local
```

### 🧪 Testing

After changing the mode, test the connection:

```bash
cd /workspaces/SCIS-LiSA/src/backend
python test_ollama_cloud.py
```

**Expected Output (Cloud Mode):**
```
🌩️  OLLAMA CLOUD CONNECTION TEST
======================================================================
Mode: cloud
Host: https://ollama.com
Model: qwen3-coder-next
API Key: ✓ Configured
======================================================================
✓ Client initialized
✓ Found 30 models available
✓ Model responded successfully!
✓ ALL TESTS PASSED!
```

**Expected Output (Local Mode):**
```
🖥️  OLLAMA LOCAL CONNECTION TEST
======================================================================
Mode: local
Host: http://localhost:11434
Model: llama3.2
API Key: ✗ Not configured (local mode)
======================================================================
✓ Client initialized
...
```

### 📋 Current Configuration

Your `.env` file now has separate sections:

```env
# Ollama Configuration
OLLAMA_MODE=cloud   # ← Change this to 'local' or 'cloud'

# Cloud Ollama Configuration
OLLAMA_CLOUD_HOST=https://ollama.com
OLLAMA_CLOUD_MODEL=qwen3-coder-next
OLLAMA_API_KEY=637b244a7004433cb01341143ac267f9.Sa5tTopeE4SxWpNCx2Cjwe6g

# Local Ollama Configuration  
OLLAMA_LOCAL_HOST=http://localhost:11434
OLLAMA_LOCAL_MODEL=llama3.2
```

### 🔧 What Happens Automatically

When you change `OLLAMA_MODE`:

1. **Agent Initialization** - Automatically configures:
   - ✅ Correct host URL (cloud vs local)
   - ✅ Appropriate model selection
   - ✅ API key authentication (cloud only)
   - ✅ Client initialization

2. **Error Messages** - Context-aware guidance:
   - Cloud mode: "Check OLLAMA_CLOUD_HOST and OLLAMA_API_KEY"
   - Local mode: "Make sure Ollama is running at localhost:11434"

3. **Logging** - Clear mode indicators:
   - `🌩️  Using CLOUD Ollama mode`
   - `🖥️  Using LOCAL Ollama mode`

### ✅ Verified Working

**Cloud Mode** (Current):
```bash
$ curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"question": "how many faculty"}'

{
  "sql": "SELECT COUNT(*) FROM authors WHERE is_faculty = true;",
  "data": [{"faculty_count": 34}],
  "row_count": 1
}
```

**Test Script**:
```bash
$ python test_ollama_cloud.py
🌩️  OLLAMA CLOUD CONNECTION TEST
✓ ALL TESTS PASSED!
```

### 🚀 For Your Local Testing

When you want to test locally:

1. **Install Ollama** (if not already):
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull a model**:
   ```bash
   ollama pull llama3.2
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

4. **Switch mode in .env**:
   ```env
   OLLAMA_MODE=local
   ```

5. **Restart backend** (auto-reload will pick up the change)

6. **Test**:
   ```bash
   python test_ollama_cloud.py
   ```

### 📖 Full Documentation

See [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) for complete documentation including:
- Available models for each mode
- Troubleshooting guide
- Environment variables reference
- Architecture details

---

**Status**: ✅ Cloud Ollama integration working perfectly!  
**Current Mode**: 🌩️ Cloud (Codespaces)  
**Ready for**: 🖥️ Local testing when needed
