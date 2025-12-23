"""
User Management Service - Configuration Settings

This module provides environment-based configuration for the User Management Service.
Follows 12-factor app principles with environment variables.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Attributes:
        SERVICE_NAME: Name of the service
        SERVICE_VERSION: Version of the service
        DEBUG: Debug mode flag
        ENVIRONMENT: Environment (development, staging, production)
        
        DATABASE_HOST: PostgreSQL host
        DATABASE_PORT: PostgreSQL port
        DATABASE_NAME: PostgreSQL database name
        DATABASE_USER: PostgreSQL user
        DATABASE_PASSWORD: PostgreSQL password
        
        LOG_LEVEL: Logging level
        
        CORS_ORIGINS: List of allowed CORS origins
        CORS_CREDENTIALS: Allow credentials in CORS
        CORS_METHODS: Allowed HTTP methods for CORS
        CORS_HEADERS: Allowed headers for CORS
    """
    
    # Application Settings
    SERVICE_NAME: str = "GDB-User-Management-Service"
    TITLE: str = "User Management Service"
    DESCRIPTION: str = "FastAPI service for user management with role-based access control"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    # Database Settings
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "gdb_users_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    
    # Security Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/users_service.log"
    
    # Service URLs (for inter-service communication)
    AUTH_SERVICE_URL: str = "http://localhost:8004"
    TRANSACTIONS_SERVICE_URL: str = "http://localhost:8002"
    ACCOUNTS_SERVICE_URL: str = "http://localhost:8001"
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:8004",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


# Load settings from environment
settings = Settings()
