# Ollama Configuration Guide

This guide explains how to configure the SCISLiSA backend to work with either local or cloud Ollama instances.

## Configuration Modes

The system supports two modes controlled by the `OLLAMA_MODE` environment variable in `.env`:

### 🌩️ Cloud Mode (Default)
Uses cloud Ollama service with API key authentication.

**When to use:**
- Running in GitHub Codespaces or cloud environments
- Cannot install Ollama locally
- Want to use cloud-hosted models

**Configuration in `.env`:**
```env
OLLAMA_MODE=cloud
OLLAMA_CLOUD_HOST=https://ollama.com
OLLAMA_CLOUD_MODEL=qwen3-coder-next
OLLAMA_API_KEY=your_api_key_here
```

### 🖥️ Local Mode
Uses local Ollama instance without API key.

**When to use:**
- Running on your local development machine
- Have Ollama installed locally
- Testing with local models

**Configuration in `.env`:**
```env
OLLAMA_MODE=local
OLLAMA_LOCAL_HOST=http://localhost:11434
OLLAMA_LOCAL_MODEL=llama3.2
```

## Quick Start

### For Cloud Ollama

1. Get your Ollama API key from https://ollama.com
2. Update `.env`:
   ```env
   OLLAMA_MODE=cloud
   OLLAMA_API_KEY=your_api_key_here
   ```
3. Test connection:
   ```bash
   python test_ollama_cloud.py
   ```

### For Local Ollama

1. Install Ollama: https://ollama.com/download
2. Pull required model:
   ```bash
   ollama pull llama3.2
   ```
3. Update `.env`:
   ```env
   OLLAMA_MODE=local
   ```
4. Start Ollama service:
   ```bash
   ollama serve
   ```
5. Test connection:
   ```bash
   python test_ollama_cloud.py
   ```

## Available Models

### Cloud Ollama Models
- `qwen3-coder-next` (recommended for SQL generation)
- `deepseek-v3.2` (strong reasoning)
- `mistral-large-3:675b` (very capable)
- `gemma3:27b` (Google's model)

Run `python test_ollama_cloud.py` in cloud mode to see all available models.

### Local Ollama Models
Common models available locally:
- `llama3.2` (default, good for general tasks)
- `codellama` (optimized for code)
- `mistral` (fast and efficient)

Pull models with: `ollama pull <model-name>`

## Switching Between Modes

Simply change `OLLAMA_MODE` in `.env` and restart the backend:

```bash
# Switch to local
OLLAMA_MODE=local

# Switch to cloud
OLLAMA_MODE=cloud
```

The system automatically:
- ✅ Configures the correct host URL
- ✅ Selects the appropriate model
- ✅ Enables/disables API key authentication
- ✅ Provides mode-specific error messages

## Testing Your Configuration

Run the test script to verify connectivity:

```bash
cd /workspaces/SCIS-LiSA/src/backend
python test_ollama_cloud.py
```

Expected output for working connection:
```
🌩️  OLLAMA CLOUD CONNECTION TEST  (or 🖥️  LOCAL)
======================================================================
✓ Client initialized
✓ Found X models available
✓ Model responded successfully!
✓ ALL TESTS PASSED!
```

## Troubleshooting

### Cloud Mode Issues
- **404 Not Found**: Model not available on cloud instance
  - Check available models with test script
  - Update `OLLAMA_CLOUD_MODEL` in `.env`
- **401 Unauthorized**: Invalid API key
  - Verify `OLLAMA_API_KEY` in `.env`

### Local Mode Issues
- **Connection Refused**: Ollama not running
  - Start Ollama: `ollama serve`
- **Model Not Found**: Model not pulled
  - Pull model: `ollama pull llama3.2`

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OLLAMA_MODE` | No | `local` | Mode: `cloud` or `local` |
| `OLLAMA_CLOUD_HOST` | Cloud only | `https://ollama.com` | Cloud Ollama endpoint |
| `OLLAMA_CLOUD_MODEL` | Cloud only | `qwen3-coder-next` | Cloud model name |
| `OLLAMA_API_KEY` | Cloud only | - | API key for authentication |
| `OLLAMA_LOCAL_HOST` | Local only | `http://localhost:11434` | Local Ollama endpoint |
| `OLLAMA_LOCAL_MODEL` | Local only | `llama3.2` | Local model name |

## Architecture

The system uses conditional initialization based on `OLLAMA_MODE`:

```python
# Cloud mode
if OLLAMA_MODE == "cloud":
    client = Client(
        host=OLLAMA_CLOUD_HOST,
        headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
    )

# Local mode
else:
    client = Client(host=OLLAMA_LOCAL_HOST)
```

This allows seamless switching without code changes.
