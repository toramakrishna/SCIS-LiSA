"""
Admin API Endpoints
Handles system administration tasks including DBLP data extraction, ingestion, and configuration
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
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

from config.db_config import get_db, engine
from services.ingestion_service import DatabaseIngestionService
from parsers.bibtex_parser import BibTeXParser
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Store background task status
task_status = {
    "fetch": {"status": "idle", "progress": 0, "message": "", "total": 0, "current": 0},
    "ingest": {"status": "idle", "progress": 0, "message": "", "stats": {}}
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
    """
    try:
        # Test with a known PID
        test_pid = "31/566"  # Example PID
        url = f"https://dblp.org/pid/{test_pid}.bib"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return {
            "status": "success",
            "message": "DBLP API is accessible",
            "test_url": url,
            "response_size": len(response.text),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"DBLP API test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"DBLP API test failed: {str(e)}"
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
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Save to file - use index as ID
                output_path = output_dir / f"{idx:02d}_{sanitized_pid}.bib"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                success_count += 1
                logger.info(f"✅ Fetched {faculty['faculty_name']} ({idx}/{total})")
                
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
