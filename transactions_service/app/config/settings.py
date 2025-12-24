"""
Configuration Module for Transaction Service

Handles:
- Database connection settings
- Account Service URL
- JWT configuration
- Logging paths
- Service ports
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application configuration settings."""

    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "gdb_transactions_db")
    
    # Connection pool settings
    DB_POOL_MIN_SIZE: int = int(os.getenv("DB_POOL_MIN_SIZE", 5))
    DB_POOL_MAX_SIZE: int = int(os.getenv("DB_POOL_MAX_SIZE", 20))
    DB_TIMEOUT: int = int(os.getenv("DB_TIMEOUT", 30))

    # ========================================================================
    # SERVICE CONFIGURATION
    # ========================================================================
    SERVICE_NAME: str = "Transaction Service"
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", 8002))
    SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # ========================================================================
    # INTER-SERVICE COMMUNICATION
    # ========================================================================
    ACCOUNT_SERVICE_URL: str = os.getenv(
        "ACCOUNT_SERVICE_URL", 
        "http://localhost:8001"
    )
    ACCOUNT_SERVICE_TIMEOUT: int = int(
        os.getenv("ACCOUNT_SERVICE_TIMEOUT", 10)
    )

    # ========================================================================
    # JWT & SECURITY
    # ========================================================================
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", 
        "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
    
    # RBAC Roles
    ALLOWED_ROLES: dict = {
        "WITHDRAW": ["CUSTOMER", "TELLER"],
        "DEPOSIT": ["CUSTOMER", "TELLER"],
        "TRANSFER": ["CUSTOMER", "TELLER"],
        "VIEW_LOGS": ["ADMIN"],
        "MANAGE_LIMITS": ["ADMIN"],
    }

    # ========================================================================
    # TRANSFER LIMITS BY PRIVILEGE
    # ========================================================================
    TRANSFER_LIMITS: dict = {
        "PREMIUM": {
            "daily_limit": 100000.00,
            "daily_transaction_count": 50,
        },
        "GOLD": {
            "daily_limit": 50000.00,
            "daily_transaction_count": 25,
        },
        "SILVER": {
            "daily_limit": 25000.00,
            "daily_transaction_count": 10,
        },
        "BASIC": {
            "daily_limit": 10000.00,
            "daily_transaction_count": 5,
        },
    }

    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs/transactions")
    LOG_FILE_FORMAT: str = "%Y-%m-%d"  # Daily log file format
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Ensure log directory exists
    @staticmethod
    def ensure_log_dir() -> None:
        """Create log directory if it doesn't exist."""
        if not os.path.exists(Settings.LOG_DIR):
            os.makedirs(Settings.LOG_DIR, exist_ok=True)

    # ========================================================================
    # BUSINESS RULES
    # ========================================================================
    MINIMUM_DEPOSIT_AMOUNT: float = 1.00
    MINIMUM_WITHDRAWAL_AMOUNT: float = 1.00
    MINIMUM_TRANSFER_AMOUNT: float = 1.00
    
    # Maximum amounts
    MAXIMUM_TRANSACTION_AMOUNT: float = 999999999.99
    
    # PIN settings
    PIN_LENGTH: int = 4
    MAX_PIN_ATTEMPTS: int = 3

    # ========================================================================
    # API CONFIGURATION
    # ========================================================================
    API_VERSION: str = "v1"
    API_BASE_URL: str = f"/api/{API_VERSION}"
    
    # Swagger docs
    TITLE: str = "Global Digital Bank - Transaction Service"
    DESCRIPTION: str = "Microservice for handling withdrawals, deposits, transfers, and transaction logging"
    VERSION: str = "1.0.0"

    # ========================================================================
    # DATABASE URL (for connection)
    # ========================================================================
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL for PostgreSQL connection."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ========================================================================
    # CORS CONFIGURATION
    # ========================================================================
    CORS_ALLOWED_ORIGINS: list = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # ========================================================================
    # IDEMPOTENCY
    # ========================================================================
    IDEMPOTENCY_HEADER_NAME: str = "Idempotency-Key"
    IDEMPOTENCY_TTL_HOURS: int = 24


# Create settings instance
settings = Settings()

# Ensure log directory exists on module load
settings.ensure_log_dir()
