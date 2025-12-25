"""
Accounts Service - Configuration Settings

This module provides environment-based configuration for the Accounts Service.
Follows 12-factor app principles with environment variables.

Author: GDB Architecture Team
"""

import os
from typing import Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Attributes:
        app_name: Name of the application
        app_version: Version of the application
        debug: Debug mode flag
        environment: Environment (development, staging, production)
        database_url: PostgreSQL connection URL
        min_db_pool_size: Minimum database connection pool size
        max_db_pool_size: Maximum database connection pool size
    """
    
    # Application Settings
    app_name: str = "GDB-Accounts-Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8001
    
    # Database Settings
    database_url: str = "postgresql://user:password@localhost:5432/gdb_accounts_db"
    min_db_pool_size: int = 5
    max_db_pool_size: int = 20
    
    # Security Settings
    pin_encryption_key: str = "your-secret-encryption-key"
    access_token_expire_minutes: int = 30
    
    # JWT Settings (for Auth Service token validation)
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/accounts_service.log"
    
    # Service URLs (for inter-service communication)
    auth_service_url: str = "http://localhost:8004"
    transactions_service_url: str = "http://localhost:8002"
    users_service_url: str = "http://localhost:8003"
    
    # API Settings
    api_prefix: str = "/api/v1"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


# Load settings from environment
settings = Settings()
