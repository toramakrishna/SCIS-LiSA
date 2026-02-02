# SCISLiSA API - Quick Start Guide

## ✅ Step 1: Install FastAPI Dependencies

```bash
cd /Users/othadem/go/src/github.com/drtoramakrishna/SCISLiSA/src/backend
pip install fastapi uvicorn[standard] pydantic pydantic-settings python-multipart
```

## ✅ Step 2: Create Environment File

Create `.env` file in `src/backend/`:

```bash
cat > .env << 'EOF'
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=scislisa-service

# Application
DEBUG=True
LOG_LEVEL=INFO

# API
API_V1_PREFIX=/api/v1

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
EOF
```

## ✅ Step 3: Start the API Server

```bash
cd /Users/othadem/go/src/github.com/drtoramakrishna/SCISLiSA/src/backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## ✅ Step 4: Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **API Root**: http://localhost:8000/api/v1

## 📚 Available Endpoints

### Publications
- `GET /api/v1/publications` - List publications
- `GET /api/v1/publications/{id}` - Get publication details
- `GET /api/v1/publications/search/?q={query}` - Search publications
- `GET /api/v1/publications/stats/` - Publication statistics

### Faculty
- `GET /api/v1/faculty` - List faculty members
- `GET /api/v1/faculty/{id}` - Get faculty details
- `GET /api/v1/faculty/{id}/publications` - Faculty publications
- `GET /api/v1/faculty/{id}/stats` - Faculty statistics

### Authors
- `GET /api/v1/authors` - List all authors
- `GET /api/v1/authors?is_faculty=true` - List only faculty

### Venues
- `GET /api/v1/venues` - List venues

### Analytics
- `GET /api/v1/analytics/overview` - System overview

## 🧪 Test the API

```bash
# Health check
curl http://localhost:8000/health

# List publications
curl "http://localhost:8000/api/v1/publications?page=1&page_size=5"

# Search publications
curl "http://localhost:8000/api/v1/publications/search/?q=machine+learning"

# List faculty
curl http://localhost:8000/api/v1/faculty

# Get analytics overview
curl http://localhost:8000/api/v1/analytics/overview
```

## 📊 Example Response

```json
{
  "items": [
    {
      "id": 1,
      "title": "Sample Publication",
      "year": 2024,
      "publication_type": "article",
      "venue": "Computing",
      "doi": "10.1007/..."
    }
  ],
  "total": 1301,
  "page": 1,
  "page_size": 20,
  "total_pages": 66,
  "has_next": true,
  "has_prev": false
}
```

## 🎯 Next Steps

1. ✅ **API is Running** - All core endpoints implemented
2. **Phase 2**: Implement MCP Agent with Ollama
3. **Phase 3**: Add advanced features (caching, full-text search)
4. **Phase 4**: Deployment and monitoring

## 🔧 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running: `docker ps`
- Check database exists: `docker exec postgres psql -U postgres -l | grep postgres`

### Import Errors
- Install missing packages: `pip install -r requirements.txt`
- Check Python path: `echo $PYTHONPATH`

### Port Already in Use
- Change port: `uvicorn api.main:app --port 8001`
- Or kill process: `lsof -ti:8000 | xargs kill -9`

## 📝 Notes

- The API auto-generates interactive documentation at `/docs`
- All responses include pagination metadata
- Booktitle/journal formatting is automatically cleaned
- Faculty filter available on most endpoints
