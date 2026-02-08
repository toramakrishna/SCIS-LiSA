# Connecting to Cloud Ollama

This guide explains how to configure SCISLiSA to use a cloud-based Ollama service instead of running Ollama locally.

## Configuration Steps

### 1. Update Environment Variables

Edit the `.env` file in the project root:

```bash
# Update OLLAMA_HOST with your cloud endpoint
OLLAMA_HOST=https://your-cloud-endpoint.com
OLLAMA_MODEL=llama3.2
```

### 2. Cloud Ollama Options

#### Option A: Ollama Cloud (Official)
If Ollama offers a cloud service:
```bash
OLLAMA_HOST=https://api.ollama.com  # Check official documentation
OLLAMA_MODEL=llama3.2
```

#### Option B: Self-Hosted Cloud Server
If you're running Ollama on a cloud server (AWS, Azure, GCP):
```bash
OLLAMA_HOST=https://your-server-ip:11434
OLLAMA_MODEL=llama3.2
```

#### Option C: Tunneling Service (Ngrok, Cloudflare Tunnel)
If you're tunneling a local Ollama instance:
```bash
OLLAMA_HOST=https://your-tunnel-url.ngrok.io
OLLAMA_MODEL=llama3.2
```

#### Option D: Alternative LLM Providers
If you want to use OpenAI or other providers, you'll need to modify the agent code (see below).

### 3. Restart Services

After updating `.env`, restart the backend:

```bash
# Stop current services
pkill -f uvicorn

# Start backend
cd /workspaces/SCIS-LiSA/src/backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Verify Connection

Test the connection:

```bash
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many faculty members are there?"}'
```

## Common Cloud Setups

### Running Ollama on a Cloud VM

1. **Install Ollama on cloud VM:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Configure Ollama to accept external connections:**
   ```bash
   # Set environment variable before starting
   export OLLAMA_HOST=0.0.0.0:11434
   ollama serve
   ```

3. **Pull your model:**
   ```bash
   ollama pull llama3.2
   ```

4. **Update SCISLiSA .env:**
   ```bash
   OLLAMA_HOST=http://your-vm-ip:11434
   OLLAMA_MODEL=llama3.2
   ```

### Using Ollama through Ngrok

1. **Run Ollama locally:**
   ```bash
   ollama serve
   ```

2. **Create Ngrok tunnel:**
   ```bash
   ngrok http 11434
   ```

3. **Update .env with Ngrok URL:**
   ```bash
   OLLAMA_HOST=https://abc123.ngrok.io
   OLLAMA_MODEL=llama3.2
   ```

## Troubleshooting

### Connection Refused
- Ensure your cloud endpoint is accessible
- Check firewall rules allow connections on port 11434
- Verify Ollama is running on the remote server

### Model Not Found
- Pull the model on the cloud instance: `ollama pull llama3.2`
- Verify model name matches exactly in `.env`

### Timeout Errors
- Increase timeout in the agent (already set to 60s)
- Check network latency to cloud endpoint
- Consider using a closer geographic region

### Authentication Errors
If your cloud service requires authentication, you may need to add API keys:

```python
# In mcp/agent.py, modify the request to include headers:
headers = {
    "Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"
}

response = await client.post(
    f"{self.base_url}/api/generate",
    json={...},
    headers=headers
)
```

## Alternative: Using OpenAI API

If you prefer to use OpenAI instead of Ollama:

1. **Install OpenAI SDK:**
   ```bash
   pip install openai
   ```

2. **Update agent code** (contact developer for complete implementation)

3. **Set environment variables:**
   ```bash
   OPENAI_API_KEY=your-api-key
   OPENAI_MODEL=gpt-4
   ```

## Support

For additional help or alternative configurations, please refer to:
- Ollama documentation: https://ollama.com/docs
- SCISLiSA backend README: `/src/backend/README.md`
