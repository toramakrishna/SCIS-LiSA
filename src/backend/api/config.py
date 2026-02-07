"""
SCISLiSA API Configuration
Handles environment variables and application settings
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import Optional, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "SCISLiSA API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "School of Computer and Information Sciences Library and Scholarly Activity API"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "scislisa-service"
    
    # CORS
    CORS_ORIGINS: Union[list[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000"
    ]
    CORS_CREDENTIALS: bool = False
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list[str] = ["*"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting (requests per minute)
    RATE_LIMIT: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def database_url(self) -> str:
        """Construct database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        # Point to .env file in the backend directory (one level up from api/config.py)
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables without validation errors


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
