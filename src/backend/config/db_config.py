"""
Database configuration for SCISLiSA
Supports both PostgreSQL (local) and MongoDB (cloud)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from typing import Generator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "scislisa-service")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# PostgreSQL connection string
POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLAlchemy setup
engine = create_engine(POSTGRES_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB Configuration
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "drtorkrishna_db_user")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "<password>")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER", "cluster0.mongodb.net")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "scislisa")

# MongoDB connection string
MONGODB_URL = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority"

# MongoDB client (lazy initialization)
_mongo_client = None
_mongo_db = None


def get_postgres_db() -> Generator:
    """
    Dependency for getting PostgreSQL database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo_db():
    """
    Get MongoDB database instance (lazy initialization)
    """
    global _mongo_client, _mongo_db
    
    if _mongo_db is None:
        try:
            _mongo_client = MongoClient(MONGODB_URL)
            _mongo_db = _mongo_client[MONGODB_DATABASE]
            # Test connection
            _mongo_client.server_info()
            logger.info(f"Connected to MongoDB database: {MONGODB_DATABASE}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    return _mongo_db


def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global _mongo_client, _mongo_db
    
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        logger.info("MongoDB connection closed")


def init_postgres_db():
    """
    Initialize PostgreSQL database tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("PostgreSQL database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL database: {e}")
        raise


def test_connections():
    """
    Test both database connections
    """
    # Test PostgreSQL
    try:
        with engine.connect() as conn:
            logger.info("✓ PostgreSQL connection successful")
            return True
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test connections when run directly
    print("Testing database connections...")
    test_connections()
