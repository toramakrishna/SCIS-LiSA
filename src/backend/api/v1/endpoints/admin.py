"""
Admin API Endpoints
Handles system administration tasks including DBLP data extraction, ingestion, and configuration
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import requests
import logging
from datetime import datetime
from pathlib import Path
import tempfile
import pdfplumber
from sqlalchemy.exc import IntegrityError

from config.db_config import get_db, engine
from services.ingestion_service import DatabaseIngestionService
from parsers.bibtex_parser import BibTeXParser
from models.db_models import Student
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Store background task status
task_status = {
    "fetch": {"status": "idle", "progress": 0, "message": "", "total": 0, "current": 0},
    "ingest": {"status": "idle", "progress": 0, "message": "", "stats": {}},
    "students": {"status": "idle", "progress": 0, "message": "", "stats": {}}
}


class DBConnectionTest(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str


class FacultyMember(BaseModel):
    id: int
    name: str
    dblp_pid: str


class IngestionConfig(BaseModel):
    dataset_path: str
    source_name: str = "DBLP"


class FetchConfig(BaseModel):
    output_directory: str = "dataset/dblp"
    faculty_json_path: str = "references/dblp/faculty_dblp_matched.json"


# =====================================================
# Configuration & Testing Endpoints
# =====================================================

@router.get("/health")
async def health_check():
    """Check if the API is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SCISLiSA Admin API"
    }


@router.post("/test-db-connection")
async def test_database_connection(config: DBConnectionTest):
    """
    Test database connection with provided credentials
    """
    try:
        from sqlalchemy import create_engine
        
        # Build connection string
        db_url = f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"
        
        # Attempt to connect
        test_engine = create_engine(db_url)
        
        with test_engine.connect() as conn:
            # Run a simple query
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
        test_engine.dispose()
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_version": version,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Database connection failed: {str(e)}"
        )


@router.get("/test-current-db")
async def test_current_database(db: Session = Depends(get_db)):
    """
    Test the currently configured database connection
    """
    try:
        # Test connection
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        
        # Get table counts
        tables_query = text("""
            SELECT 
                schemaname,
                tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables_result = db.execute(tables_query)
        tables = [{"schema": row[0], "name": row[1]} for row in tables_result]
        
        # Get record counts
        counts = {}
        for table in ['authors', 'publications', 'collaborations', 'venues']:
            try:
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = count_result.fetchone()[0]
            except:
                counts[table] = 0
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_version": version,
            "tables": tables,
            "record_counts": counts,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database test failed: {str(e)}"
        )


@router.get("/test-dblp-api")
async def test_dblp_api():
    """
    Test DBLP API connectivity
    Note: This may timeout in containerized environments (e.g., Codespaces)
    """
    try:
        # Test with a known PID
        test_pid = "31/566"  # Example PID
        url = f"https://dblp.org/pid/{test_pid}.bib"
        
        response = requests.get(url, timeout=30)  # Increased timeout for containers
        response.raise_for_status()
        
        return {
            "status": "success",
            "message": "DBLP API is accessible",
            "test_url": url,
            "response_size": len(response.text),
            "timestamp": datetime.now().isoformat()
        }
        
    except requests.exceptions.Timeout as e:
        # Handle timeout gracefully - this is expected in some environments
        logger.warning(f"DBLP API timeout (expected in containerized environments): {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "timeout",
                "message": "DBLP API connection timed out. This is common in containerized environments (Codespaces, Docker). The application will work fine with existing data.",
                "test_url": url,
                "note": "DBLP access is only needed for fetching new data. Existing data and all features will work normally.",
                "timestamp": datetime.now().isoformat()
            }
        )
    except requests.exceptions.RequestException as e:
        # Handle other network errors gracefully
        logger.warning(f"DBLP API connection issue: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Could not connect to DBLP API: {str(e)}",
                "note": "This doesn't affect the application functionality with existing data.",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"DBLP API test failed: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"DBLP API test failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )


# =====================================================
# DBLP Data Fetching Endpoints
# =====================================================

@router.get("/faculty-list")
async def get_faculty_list():
    """
    Get list of faculty members from the matched JSON file
    """
    try:
        # Get absolute path relative to this file's location
        current_file = Path(__file__)
        backend_dir = current_file.parent.parent.parent.parent  # Navigate to backend dir
        json_path = backend_dir / "references" / "dblp" / "faculty_dblp_matched.json"
        
        if not json_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Faculty JSON file not found at {json_path}"
            )
        
        with open(json_path, 'r', encoding='utf-8') as f:
            faculty_data = json.load(f)
        
        return {
            "status": "success",
            "total_faculty": len(faculty_data),
            "faculty": faculty_data
        }
        
    except Exception as e:
        logger.error(f"Failed to load faculty list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load faculty list: {str(e)}"
        )


def fetch_dblp_data_background(config: FetchConfig):
    """Background task to fetch DBLP data"""
    try:
        task_status["fetch"]["status"] = "running"
        task_status["fetch"]["message"] = "Loading faculty list..."
        
        # Get absolute path for faculty JSON
        current_file = Path(__file__)
        backend_dir = current_file.parent.parent.parent.parent
        faculty_json_path = backend_dir / config.faculty_json_path.replace('src/backend/', '')
        
        # Load faculty list
        with open(faculty_json_path, 'r', encoding='utf-8') as f:
            faculty_data = json.load(f)
        
        total = len(faculty_data)
        task_status["fetch"]["total"] = total
        
        # Create output directory (relative to backend dir)
        output_dir = backend_dir.parent.parent / config.output_directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        error_count = 0
        
        for idx, faculty in enumerate(faculty_data, 1):
            task_status["fetch"]["current"] = idx
            task_status["fetch"]["progress"] = int((idx / total) * 100)
            task_status["fetch"]["message"] = f"Fetching data for {faculty['faculty_name']}..."
            
            pid = faculty['dblp_pid']
            sanitized_pid = pid.replace('/', '_')
            
            try:
                # Fetch BibTeX
                url = f"https://dblp.org/pid/{pid}.bib"
                response = requests.get(url, timeout=60)  # Increased timeout for containers
                response.raise_for_status()
                
                # Save to file - use index as ID
                output_path = output_dir / f"{idx:02d}_{sanitized_pid}.bib"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                success_count += 1
                logger.info(f"✅ Fetched {faculty['faculty_name']} ({idx}/{total})")
                
            except requests.exceptions.Timeout:
                error_count += 1
                logger.warning(f"⏱️ Timeout fetching {faculty['faculty_name']} - skipping")
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Failed to fetch {faculty['faculty_name']}: {str(e)}")
        
        task_status["fetch"]["status"] = "completed"
        task_status["fetch"]["message"] = f"Completed: {success_count} successful, {error_count} errors"
        task_status["fetch"]["progress"] = 100
        
    except Exception as e:
        task_status["fetch"]["status"] = "error"
        task_status["fetch"]["message"] = f"Error: {str(e)}"
        logger.error(f"Fetch task failed: {str(e)}")


@router.post("/fetch-dblp-data")
async def fetch_dblp_data(
    config: FetchConfig,
    background_tasks: BackgroundTasks
):
    """
    Fetch BibTeX data from DBLP for all faculty members (async)
    """
    if task_status["fetch"]["status"] == "running":
        raise HTTPException(
            status_code=409,
            detail="Fetch operation already in progress"
        )
    
    # Reset status
    task_status["fetch"] = {
        "status": "starting",
        "progress": 0,
        "message": "Initializing...",
        "total": 0,
        "current": 0
    }
    
    # Start background task
    background_tasks.add_task(fetch_dblp_data_background, config)
    
    return {
        "status": "started",
        "message": "DBLP data fetch started in background"
    }


@router.get("/fetch-status")
async def get_fetch_status():
    """Get status of DBLP fetch operation"""
    return task_status["fetch"]


# =====================================================
# Data Ingestion Endpoints
# =====================================================

def ingest_data_background(config: IngestionConfig):
    """Background task to ingest BibTeX files into database"""
    try:
        task_status["ingest"]["status"] = "running"
        
        # Ensure database tables exist
        from config.db_config import Base, engine
        task_status["ingest"]["message"] = "Initializing database tables..."
        Base.metadata.create_all(bind=engine)
        
        task_status["ingest"]["message"] = "Scanning BibTeX files..."
        
        # Get absolute path for dataset
        current_file = Path(__file__)
        backend_dir = current_file.parent.parent.parent.parent
        
        # If path starts with 'dataset/', it's relative to project root
        if config.dataset_path.startswith('dataset/'):
            dataset_path = backend_dir.parent.parent / config.dataset_path
        else:
            dataset_path = Path(config.dataset_path)
        
        if not dataset_path.exists():
            raise ValueError(f"Dataset path not found: {dataset_path}")
        
        # Get all .bib files
        bib_files = list(dataset_path.glob("*.bib"))
        total = len(bib_files)
        
        if total == 0:
            raise ValueError(f"No .bib files found in {dataset_path}")
        
        task_status["ingest"]["total"] = total
        task_status["ingest"]["message"] = f"Found {total} BibTeX files"
        
        # Create database session
        from config.db_config import SessionLocal
        db = SessionLocal()
        
        try:
            service = DatabaseIngestionService(db)
            parser = BibTeXParser()
            
            # Load faculty mapping
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent.parent.parent  # Go up to src/backend
            faculty_json_path = backend_dir / 'references' / 'faculty_data.json'
            
            if not faculty_json_path.exists():
                raise ValueError(f"Faculty data not found at {faculty_json_path}")
            
            faculty_mapping = service.load_faculty_mapping(str(faculty_json_path))
            
            for idx, bib_file in enumerate(bib_files, 1):
                task_status["ingest"]["current"] = idx
                task_status["ingest"]["progress"] = int((idx / total) * 100)
                task_status["ingest"]["message"] = f"Processing {bib_file.name}..."
                
                try:
                    # Parse BibTeX file
                    publications, _, _ = parser.parse_bib_file(str(bib_file))
                    
                    # Extract source_pid from filename
                    # Filename format: XX_YYYY-Z_name.bib -> XX/YYYY-Z
                    filename = bib_file.stem  # Remove .bib extension
                    parts = filename.split('_')
                    
                    # Remove faculty name suffix if present (alphabetic)
                    if len(parts) >= 3 and parts[-1].replace('-', '').isalpha():
                        parts = parts[:-1]
                    
                    # Remove duplicate marker if present (single digit)
                    if len(parts) >= 2 and parts[-1].isdigit() and len(parts[-1]) == 1:
                        parts = parts[:-1]
                    
                    # Reconstruct PID
                    base_filename = '_'.join(parts)
                    source_pid = base_filename.replace('_', '/', 1)
                    
                    # Add source_pid to each publication
                    for pub in publications:
                        pub['source_pid'] = source_pid
                        pub['source_pids'] = [source_pid]
                    
                    # Ingest into database
                    service.ingest_publications(publications, faculty_mapping)
                    
                    logger.info(f"✅ Processed {bib_file.name} ({idx}/{total})")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process {bib_file.name}: {str(e)}")
            
            # Commit final changes
            db.commit()
            
            # Update data source tracking
            service.update_data_source('DBLP')
            
            task_status["ingest"]["status"] = "completed"
            task_status["ingest"]["message"] = "Ingestion completed successfully"
            task_status["ingest"]["progress"] = 100
            task_status["ingest"]["stats"] = service.stats
            
        finally:
            db.close()
            
    except Exception as e:
        task_status["ingest"]["status"] = "error"
        task_status["ingest"]["message"] = f"Error: {str(e)}"
        logger.error(f"Ingestion task failed: {str(e)}")


@router.post("/ingest-data")
async def ingest_data(
    config: IngestionConfig,
    background_tasks: BackgroundTasks
):
    """
    Ingest BibTeX files into database (async)
    """
    if task_status["ingest"]["status"] == "running":
        raise HTTPException(
            status_code=409,
            detail="Ingestion operation already in progress"
        )
    
    # Reset status
    task_status["ingest"] = {
        "status": "starting",
        "progress": 0,
        "message": "Initializing...",
        "total": 0,
        "current": 0,
        "stats": {}
    }
    
    # Start background task
    background_tasks.add_task(ingest_data_background, config)
    
    return {
        "status": "started",
        "message": "Data ingestion started in background"
    }


@router.get("/ingest-status")
async def get_ingest_status():
    """Get status of data ingestion operation"""
    return task_status["ingest"]


@router.get("/database-stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Get current database statistics
    """
    try:
        stats = {}
        
        # Get counts
        for table in ['authors', 'publications', 'collaborations', 'venues', 'data_sources']:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                stats[table] = result.fetchone()[0]
            except:
                stats[table] = 0
        
        # Get faculty count
        result = db.execute(text("SELECT COUNT(*) FROM authors WHERE is_faculty = true"))
        stats['faculty'] = result.fetchone()[0]
        
        # Get students count
        try:
            result = db.execute(text("SELECT COUNT(*) FROM students"))
            stats['students'] = result.fetchone()[0]
        except:
            stats['students'] = 0
        
        # Get SCIS students count
        try:
            result = db.execute(text("""
                SELECT COUNT(*) FROM students 
                WHERE school_name LIKE '%Computer%Information%'
            """))
            stats['scis_students'] = result.fetchone()[0]
        except:
            stats['scis_students'] = 0
        
        # Get recent publications
        result = db.execute(text("""
            SELECT year, COUNT(*) as count
            FROM publications
            WHERE year >= 2020
            GROUP BY year
            ORDER BY year DESC
            LIMIT 5
        """))
        stats['recent_by_year'] = [{"year": row[0], "count": row[1]} for row in result]
        
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database stats: {str(e)}"
        )


# =====================================================
# Data Quality Validation Endpoints
# =====================================================

@router.get("/data-quality-check")
async def data_quality_check(db: Session = Depends(get_db)):
    """
    Perform comprehensive data quality validation by comparing actual database counts
    with expected counts from faculty_data.json
    
    Returns:
    - Perfect matches (exact count match)
    - Close matches (within 5% tolerance)
    - Mismatches (>5% difference)
    - Overall statistics and accuracy metrics
    """
    try:
        # Load faculty data (expected counts)
        current_file = Path(__file__)
        backend_dir = current_file.parent.parent.parent.parent
        faculty_json_path = backend_dir / 'references' / 'faculty_data.json'
        
        with open(faculty_json_path, 'r') as f:
            faculty_data = json.load(f)
        
        # Get actual publication counts from database
        from models.db_models import publication_authors
        query = text("""
            SELECT 
                a.dblp_pid,
                a.name,
                COUNT(DISTINCT pa.publication_id) as pub_count
            FROM authors a
            LEFT JOIN publication_authors pa ON a.id = pa.author_id
            WHERE a.is_faculty = true
            GROUP BY a.id, a.dblp_pid, a.name
            ORDER BY a.name
        """)
        
        result = db.execute(query)
        db_counts = {row.dblp_pid: {"name": row.name, "count": row.pub_count} for row in result}
        
        # Perform validation
        perfect_matches = []
        close_matches = []
        mismatches = []
        
        for faculty in faculty_data:
            pid = faculty['dblp_pid']
            expected = faculty['dblp_count']
            faculty_name = faculty['name']
            
            # Get actual count from database
            db_info = db_counts.get(pid, {"name": faculty_name, "count": 0})
            actual = db_info['count']
            db_name = db_info['name']
            
            diff = actual - expected
            pct_diff = abs(diff) / expected * 100 if expected > 0 else (0 if diff == 0 else 100)
            
            item = {
                "faculty_name": faculty_name,
                "db_name": db_name,
                "dblp_pid": pid,
                "expected": expected,
                "actual": actual,
                "difference": diff,
                "pct_difference": round(pct_diff, 2)
            }
            
            if diff == 0:
                perfect_matches.append(item)
            elif pct_diff <= 5:
                close_matches.append(item)
            else:
                mismatches.append(item)
        
        # Calculate overall statistics
        total_expected = sum(f['dblp_count'] for f in faculty_data)
        total_actual = sum(db_counts[f['dblp_pid']]['count'] if f['dblp_pid'] in db_counts else 0 for f in faculty_data)
        overall_diff = total_actual - total_expected
        overall_accuracy = (total_actual / total_expected * 100) if total_expected > 0 else 0
        
        total_faculty = len(faculty_data)
        accuracy_rate = (len(perfect_matches) + len(close_matches)) / total_faculty * 100 if total_faculty > 0 else 0
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_faculty": total_faculty,
                "perfect_matches": len(perfect_matches),
                "close_matches": len(close_matches),
                "mismatches": len(mismatches),
                "accuracy_rate": round(accuracy_rate, 1),
                "perfect_match_rate": round(len(perfect_matches) / total_faculty * 100, 1) if total_faculty > 0 else 0
            },
            "overall_stats": {
                "total_expected_publications": total_expected,
                "total_actual_publications": total_actual,
                "overall_difference": overall_diff,
                "overall_accuracy": round(overall_accuracy, 1)
            },
            "perfect_matches": perfect_matches,
            "close_matches": close_matches,
            "mismatches": mismatches
        }
        
    except Exception as e:
        logger.error(f"Data quality check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Data quality check failed: {str(e)}"
        )


# ========== Ollama Configuration Endpoints ==========

class OllamaSettings(BaseModel):
    """Ollama configuration settings"""
    mode: str  # 'cloud' or 'local'
    cloud_host: str = "https://ollama.com"
    cloud_model: str = "qwen3-coder-next"
    cloud_api_key: Optional[str] = None
    local_host: str = "http://localhost:11434"
    local_model: str = "llama3.2"


class TestConnectionRequest(BaseModel):
    """Request to test Ollama connection"""
    mode: str
    host: str
    model: str
    api_key: Optional[str] = None


class TestConnectionResponse(BaseModel):
    """Response from connection test"""
    success: bool
    message: str
    model_count: Optional[int] = None
    available_models: Optional[List[str]] = None


# Path to .env file
ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"


@router.get("/settings/ollama")
async def get_ollama_settings() -> OllamaSettings:
    """Get current Ollama settings from environment"""
    try:
        # Load current settings from .env file
        settings = {}
        if ENV_FILE_PATH.exists():
            with open(ENV_FILE_PATH, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        settings[key.strip()] = value.strip()
        
        # Mask the API key for security - only show first 8 and last 4 characters
        api_key = settings.get('OLLAMA_API_KEY', '')
        masked_key = ''
        if api_key:
            if len(api_key) > 12:
                masked_key = api_key[:8] + '...' + api_key[-4:]
            else:
                masked_key = '***********'
        
        return OllamaSettings(
            mode=settings.get('OLLAMA_MODE', 'local'),
            cloud_host=settings.get('OLLAMA_CLOUD_HOST', 'https://ollama.com'),
            cloud_model=settings.get('OLLAMA_CLOUD_MODEL', 'qwen3-coder-next'),
            cloud_api_key=masked_key,
            local_host=settings.get('OLLAMA_LOCAL_HOST', 'http://localhost:11434'),
            local_model=settings.get('OLLAMA_LOCAL_MODEL', 'llama3.2')
        )
    except Exception as e:
        logger.error(f"Error loading Ollama settings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load settings: {str(e)}"
        )


@router.post("/settings/ollama/test")
async def test_ollama_connection(request: TestConnectionRequest) -> TestConnectionResponse:
    """Test Ollama connection with provided settings"""
    try:
        from ollama import Client
        
        # Initialize client
        if request.api_key:
            client = Client(host=request.host, headers={'Authorization': f'Bearer {request.api_key}'})
        else:
            client = Client(host=request.host)
        
        # Try to list models
        try:
            models_response = client.list()
            models = [model['name'] for model in models_response.get('models', [])]
            
            # Test if the specified model exists
            if request.model not in models:
                return TestConnectionResponse(
                    success=False,
                    message=f"Model '{request.model}' not found. Available models: {', '.join(models[:5])}...",
                    model_count=len(models),
                    available_models=models[:10]
                )
            
            # Try a simple generate request
            response = client.generate(
                model=request.model,
                prompt="Hello",
                options={"num_predict": 10}
            )
            
            return TestConnectionResponse(
                success=True,
                message=f"Successfully connected to {request.mode} Ollama! Found {len(models)} models.",
                model_count=len(models),
                available_models=models[:10]
            )
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return TestConnectionResponse(
                success=False,
                message=f"Connection failed: {str(e)}"
            )
            
    except Exception as e:
        logger.error(f"Error initializing client: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize client: {str(e)}"
        )


@router.post("/settings/ollama")
async def save_ollama_settings(settings: OllamaSettings) -> Dict:
    """Save Ollama settings to .env file"""
    try:
        if not ENV_FILE_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail=".env file not found"
            )
        
        # Read current .env file
        with open(ENV_FILE_PATH, 'r') as f:
            lines = f.readlines()
        
        # Load existing settings to preserve API key if not being updated
        existing_api_key = ''
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#') and '=' in line_stripped:
                key, value = line_stripped.split('=', 1)
                if key.strip() == 'OLLAMA_API_KEY':
                    existing_api_key = value.strip()
                    break
        
        # Update the relevant settings
        # If API key is empty string, preserve the existing one (don't overwrite)
        api_key_to_save = settings.cloud_api_key if settings.cloud_api_key else existing_api_key
        
        updated_lines = []
        settings_to_update = {
            'OLLAMA_MODE': settings.mode,
            'OLLAMA_CLOUD_HOST': settings.cloud_host,
            'OLLAMA_CLOUD_MODEL': settings.cloud_model,
            'OLLAMA_API_KEY': api_key_to_save,
            'OLLAMA_LOCAL_HOST': settings.local_host,
            'OLLAMA_LOCAL_MODEL': settings.local_model
        }
        
        updated_keys = set()
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#') and '=' in line_stripped:
                key = line_stripped.split('=', 1)[0].strip()
                if key in settings_to_update:
                    updated_lines.append(f"{key}={settings_to_update[key]}\n")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Add any missing keys
        for key, value in settings_to_update.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}\n")
        
        # Write back to .env file
        with open(ENV_FILE_PATH, 'w') as f:
            f.writelines(updated_lines)
        
        logger.info(f"Successfully updated Ollama settings to {settings.mode} mode")
        
        return {
            "success": True,
            "message": f"Settings saved successfully. Mode set to: {settings.mode}",
            "settings": settings.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving Ollama settings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save settings: {str(e)}"
        )


# =====================================================
# Students PDF Upload & Ingestion
# =====================================================

def normalize_program_name(program: str) -> str:
    """
    Normalize program name to fix common inconsistencies
    - Adds space before parenthesis if missing
    - Fixes case inconsistencies
    - Removes newlines and extra spaces
    """
    if not program or program == 'None':
        return None
    
    # Remove newlines and extra spaces
    program = ' '.join(program.split())
    
    # Fix missing space before parenthesis
    program = program.replace('Technology(', 'Technology (')
    program = program.replace('Application(', 'Application (')
    program = program.replace('Philosophy(', 'Philosophy (')
    
    # Standardize case for "Computer science" -> "Computer Science"
    program = program.replace('Computer science', 'Computer Science')
    
    return program


def extract_students_from_pdf_content(pdf_file) -> list:
    """
    Extract student data from PDF file content
    Returns list of student dictionaries
    """
    students = []
    
    # Column indices (based on observed structure)
    reg_no_idx = 1
    name_idx = 2
    semester_idx = 3
    program_idx = 4
    school_idx = 5
    prog_type_idx = 6
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            logger.info(f"Processing {len(pdf.pages)} pages from uploaded PDF")
            
            # First, find column indices from first page header
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0]
                tables = first_page.extract_tables()
                if tables and len(tables[0]) > 1:
                    table = tables[0]
                    for idx, row in enumerate(table):
                        if row and len(row) > 1 and row[1] and 'Reg No' in str(row[1]):
                            headers = row
                            try:
                                reg_no_idx = next(i for i, h in enumerate(headers) if h and 'Reg No' in str(h))
                                name_idx = next(i for i, h in enumerate(headers) if h and 'Name' in str(h) and 'School' not in str(h))
                                semester_idx = next(i for i, h in enumerate(headers) if h and 'Semester' in str(h))
                                program_idx = next(i for i, h in enumerate(headers) if h and 'Program' in str(h) and 'Type' not in str(h))
                                school_idx = next(i for i, h in enumerate(headers) if h and 'School Name' in str(h))
                                prog_type_idx = next(i for i, h in enumerate(headers) if h and 'Programme-Type' in str(h))
                                logger.info(f"Column indices found: RegNo={reg_no_idx}, Name={name_idx}")
                                break
                            except StopIteration:
                                logger.warning("Could not find all required columns in header")
            
            # Process all pages
            for page_num, page in enumerate(pdf.pages, 1):
                if page_num % 10 == 0:
                    logger.info(f"Processing page {page_num}/{len(pdf.pages)}")
                
                tables = page.extract_tables()
                if not tables:
                    continue
                
                table = tables[0]
                
                # Find where to start processing (skip header rows)
                start_row = 0
                for idx, row in enumerate(table):
                    if row and len(row) > 1:
                        cell_text = str(row[1]) if row[1] else ""
                        if 'ELECTORAL' in cell_text or 'Reg No' in cell_text or 'SNo' in cell_text:
                            start_row = idx + 1
                            continue
                        break
                
                # Process data rows
                for row_idx in range(start_row, len(table)):
                    row = table[row_idx]
                    
                    if not row or len(row) <= max(reg_no_idx, name_idx, semester_idx, program_idx, school_idx, prog_type_idx):
                        continue
                    
                    reg_no = str(row[reg_no_idx]).strip() if row[reg_no_idx] else None
                    name = str(row[name_idx]).strip() if row[name_idx] else None
                    semester_str = str(row[semester_idx]).strip() if row[semester_idx] else None
                    program = str(row[program_idx]).strip() if row[program_idx] else None
                    school_name = str(row[school_idx]).strip() if row[school_idx] else None
                    prog_type = str(row[prog_type_idx]).strip() if row[prog_type_idx] else None
                    
                    if not reg_no or not name or reg_no == 'None' or name == 'None':
                        continue
                    
                    if 'Reg No' in reg_no or 'SNo' in reg_no:
                        continue
                    
                    try:
                        semester = int(semester_str) if semester_str and semester_str != 'None' else None
                    except ValueError:
                        semester = None
                    
                    # Normalize program name
                    normalized_program = normalize_program_name(program)
                    
                    students.append({
                        'registration_number': reg_no,
                        'name': name,
                        'semester': semester,
                        'program': normalized_program,
                        'school_name': school_name if school_name != 'None' else None,
                        'programme_type': prog_type if prog_type != 'None' else None
                    })
                    
        logger.info(f"Extracted {len(students)} students from PDF")
        return students
        
    except Exception as e:
        logger.error(f"Error extracting students from PDF: {e}")
        raise


def ingest_students_to_db_task(students: list, db: Session) -> dict:
    """
    Ingest students into database
    Returns dictionary with statistics
    """
    stats = {
        'inserted': 0,
        'duplicates': 0,
        'errors': 0
    }
    
    for student_data in students:
        try:
            existing = db.query(Student).filter(
                Student.registration_number == student_data['registration_number']
            ).first()
            
            if existing:
                stats['duplicates'] += 1
                continue
            
            student = Student(**student_data)
            db.add(student)
            db.commit()
            stats['inserted'] += 1
            
            if stats['inserted'] % 100 == 0:
                logger.info(f"Inserted {stats['inserted']} students...")
                task_status["students"]["progress"] = int((stats['inserted'] / len(students)) * 100)
                task_status["students"]["message"] = f"Inserted {stats['inserted']}/{len(students)} students"
                
        except IntegrityError:
            db.rollback()
            stats['duplicates'] += 1
        except Exception as e:
            db.rollback()
            stats['errors'] += 1
            logger.error(f"Error inserting student {student_data.get('registration_number', 'unknown')}: {e}")
    
    return stats


@router.post("/students/upload")
async def upload_students_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a students PDF file and ingest the data into the database
    """
    if task_status["students"]["status"] == "running":
        raise HTTPException(
            status_code=400,
            detail="A student ingestion task is already running"
        )
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Update task status
        task_status["students"]["status"] = "running"
        task_status["students"]["progress"] = 0
        task_status["students"]["message"] = "Reading PDF file..."
        task_status["students"]["stats"] = {}
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        logger.info(f"Processing uploaded PDF: {file.filename} ({len(content)} bytes)")
        
        # Extract students from PDF
        task_status["students"]["message"] = "Extracting student data from PDF..."
        task_status["students"]["progress"] = 10
        
        students = extract_students_from_pdf_content(tmp_file_path)
        
        if not students:
            task_status["students"]["status"] = "error"
            task_status["students"]["message"] = "No students found in PDF"
            os.unlink(tmp_file_path)
            raise HTTPException(status_code=400, detail="No students found in PDF")
        
        # Ingest to database
        task_status["students"]["message"] = f"Ingesting {len(students)} students to database..."
        task_status["students"]["progress"] = 50
        
        stats = ingest_students_to_db_task(students, db)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        # Update final status
        task_status["students"]["status"] = "completed"
        task_status["students"]["progress"] = 100
        task_status["students"]["message"] = f"Successfully processed {len(students)} students"
        task_status["students"]["stats"] = stats
        
        logger.info(f"Student ingestion completed: {stats}")
        
        return {
            "status": "success",
            "message": f"Successfully processed {file.filename}",
            "total_extracted": len(students),
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing student PDF: {e}")
        task_status["students"]["status"] = "error"
        task_status["students"]["message"] = f"Error: {str(e)}"
        
        # Clean up temp file if it exists
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )


@router.get("/students/upload/status")
async def get_students_upload_status():
    """
    Get the current status of the students upload task
    """
    return task_status["students"]


