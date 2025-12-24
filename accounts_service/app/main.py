"""
Accounts Service - Main Application

FastAPI application for Global Digital Bank Accounts Service.

Author: GDB Architecture Team
Version: 1.0.0
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config.settings import settings
from app.config.logging import setup_logging
from app.database.db import initialize_db, close_db
from app.api import accounts, internal_accounts

# Configure logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Accounts Service...")
    await initialize_db(
        str(settings.database_url),
        min_size=settings.min_db_pool_size,
        max_size=settings.max_db_pool_size
    )
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Accounts Service...")
    await close_db()
    logger.info("✅ Accounts Service stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Microservice for managing bank accounts",
    version=settings.app_version,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.gdb.local"]
)


# Include routers
app.include_router(
    accounts.router,
    prefix=settings.api_prefix,
    tags=["accounts"]
)

app.include_router(
    internal_accounts.router,
    prefix=f"{settings.api_prefix}/internal",
    tags=["internal"]
)


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: Service information
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": f"http://localhost:{settings.port}{settings.api_prefix}/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
