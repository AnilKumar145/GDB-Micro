"""
Console Application - Settings Configuration

Environment configuration for PostgreSQL connection.

Author: GDB Architecture Team
"""

import os
from pathlib import Path


class Settings:
    """Application settings."""
    
    # Application info
    app_name: str = "Account Service Console"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # Database settings (PostgreSQL)
    database_url: str = "postgresql://postgres:anil@localhost:5432/GDB-GDB"
    db_min_size: int = 2
    db_max_size: int = 10
    
    # Encryption settings
    bcrypt_rounds: int = 12
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Console UI
    enable_colors: bool = True
    
    def __init__(self):
        """Initialize settings from environment variables."""
        self.app_name = os.getenv("APP_NAME", "Account Service Console")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # PostgreSQL connection
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:anil@localhost:5432/GDB-GDB"
        )
        self.db_min_size = int(os.getenv("DB_MIN_SIZE", "2"))
        self.db_max_size = int(os.getenv("DB_MAX_SIZE", "10"))
        
        self.bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.enable_colors = os.getenv("ENABLE_COLORS", "true").lower() == "true"


# Global settings instance
settings = Settings()
