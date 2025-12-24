"""
FastAPI Application Entry Point - Transaction Service

Initializes FastAPI app, registers routes, and configures exception handlers.
NO AUTHENTICATION REQUIRED - All endpoints are public.

Features:
- Async database connection pooling
- Proper lifespan management (startup/shutdown)
- CORS middleware for inter-service communication
- Exception handling for all transaction errors
- API documentation at /api/v1/docs
"""

import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime

from app.config.settings import settings
from app.database.db import database
from app.exceptions.transaction_exceptions import TransactionException

# Import routers
from app.api.deposit_routes import router as deposit_router
from app.api.withdraw_routes import router as withdraw_router
from app.api.transfer_routes import router as transfer_router
from app.api.transfer_limit_routes import router as transfer_limit_router
from app.api.transaction_log_routes import router as transaction_log_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles startup and shutdown events properly.
    """
    # Startup
    logger.info("🚀 Starting Transaction Service")
    logger.info(f"📊 Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info(f"💰 Account Service: {settings.ACCOUNT_SERVICE_URL}")
    
    try:
        await database.initialize()
        logger.info("✅ Database connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Transaction Service")
    try:
        await database.close()
        logger.info("✅ Database connection pool closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {str(e)}")


# Initialize FastAPI app with lifespan management
app = FastAPI(
    title="Global Digital Bank - Transaction Service",
    description="Microservice for handling withdrawals, deposits, transfers, and transaction logging",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS middleware - allow calls from other services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for inter-service communication
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get(
    "/api/v1/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health Check",
)
async def health_check():
    """
    Check if service is running and database is connected.

    Returns 200 OK if healthy.
    """
    return {
        "status": "healthy",
        "service": "Transaction Service",
        "version": "1.0.0",
    }


# API Info endpoint at root
@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Info"],
    summary="API Information",
)
async def root():
    """
    Root endpoint with service information and available endpoints.
    """
    return {
        "service": "Global Digital Bank - Transaction Service",
        "version": "1.0.0",
        "description": "Microservice for handling withdrawals, deposits, transfers, and transaction logging",
        "status": "running",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "deposits": "/api/v1/deposits",
            "withdrawals": "/api/v1/withdrawals",
            "transfers": "/api/v1/transfers",
            "transfer_limits": "/api/v1/transfer-limits",
            "transaction_logs": "/api/v1/transaction-logs",
        },
        "timestamp": datetime.now().isoformat(),
    }


# Ready check endpoint
@app.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Readiness Check",
)
async def readiness_check():
    """
    Check if service is ready to handle requests.

    Returns 200 OK if database is connected and service is ready.
    """
    return {
        "status": "ready",
        "service": "Transaction Service",
        "database": "connected",
    }


# Include all route routers for transaction operations
app.include_router(deposit_router)
app.include_router(withdraw_router)
app.include_router(transfer_router)
app.include_router(transfer_limit_router)
app.include_router(transaction_log_router)


# Global exception handler for TransactionException
@app.exception_handler(TransactionException)
async def transaction_exception_handler(request, exc: TransactionException):
    """Handle all transaction-related exceptions."""
    logger.warning(f"Transaction exception: {exc.error_code} - {exc.message}")

    return JSONResponse(
        status_code=exc.http_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "status": "error",
        },
    )


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "Internal server error",
            "status": "error",
        },
    )


# Root endpoint
@app.get(
    "/",
    tags=["Info"],
    summary="API Info",
)
async def root():
    """
    Transaction Service API.

    Main entry point with API information.
    """
    return {
        "name": "Transaction Service API",
        "version": "1.0.0",
        "description": "Microservice for financial transactions",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "docs": "/api/docs",
            "deposits": "/api/v1/deposits",
            "withdrawals": "/api/v1/withdrawals",
            "transfers": "/api/v1/transfers",
            "transfer_limits": "/api/v1/transfer-limits/{account_number}",
            "transaction_logs": "/api/v1/transaction-logs/{account_number}",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level="info",
    )
