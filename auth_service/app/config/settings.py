"""
Authentication Service - Configuration Settings

Environment-based configuration following 12-factor principles.

Author: GDB Architecture Team
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    JWT secrets MUST be identical across all GDB microservices.
    Database credentials are service-specific.
    """
    
    # ================================================================
    # APPLICATION SETTINGS
    # ================================================================
    APP_NAME: str = "GDB-Authentication-Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # ================================================================
    # SERVER SETTINGS
    # ================================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    
    # ================================================================
    # DATABASE SETTINGS (gdb_auth_db - Auth-only data)
    # ================================================================
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "gdb_auth_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    
    # Connection pooling
    MIN_DB_POOL_SIZE: int = 5
    MAX_DB_POOL_SIZE: int = 20
    
    # ================================================================
    # JWT SECURITY SETTINGS (SHARED ACROSS ALL SERVICES)
    # ================================================================
    
    # Secret key for JWT signing and verification
    # ⚠️ MUST BE IDENTICAL in all microservices (Account, Transaction, User, Auth)
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    
    # JWT Algorithm (HS256 - HMAC SHA-256)
    JWT_ALGORITHM: str = "HS256"
    
    # JWT Token expiry in minutes (15-30 min recommended)
    JWT_EXPIRY_MINUTES: int = 30
    
    # ================================================================
    # INTER-SERVICE COMMUNICATION
    # ================================================================
    
    # User Service URL (for credential verification)
    USER_SERVICE_URL: str = "http://localhost:8003"
    
    # Timeout for user service calls (seconds)
    USER_SERVICE_TIMEOUT: int = 10
    
    # Account Service URL (for reference)
    ACCOUNT_SERVICE_URL: str = "http://localhost:8001"
    
    # Transaction Service URL (for reference)
    TRANSACTION_SERVICE_URL: str = "http://localhost:8002"
    
    # ================================================================
    # LOGGING SETTINGS
    # ================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/auth_service.log"
    
    # ================================================================
    # CORS SETTINGS
    # ================================================================
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:8000",
            "http://localhost:8001",
            "http://localhost:8002",
            "http://localhost:8003",
            "http://localhost:8004",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ]
    )
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = Field(default=["*"])
    CORS_HEADERS: List[str] = Field(default=["*"])
    
    # ================================================================
    # API SETTINGS
    # ================================================================
    API_PREFIX: str = "/api/v1"
    
    # ================================================================
    # PYDANTIC CONFIGURATION
    # ================================================================
    class Config:
        env_file = ".env"
        case_sensitive = False


# Load settings from environment
settings = Settings()
