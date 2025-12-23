"""
Main FastAPI application for User Management Service.
Entry point for the service.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import database and configuration
from .database.connection import init_db, close_db
from .config.settings import settings
from .api.add_user_routes import router as add_user_router
from .api.edit_user_routes import router as edit_user_router
from .api.view_user_routes import router as view_user_router
from .api.inactivate_user_routes import router as inactivate_user_router
from .api.activate_user_routes import router as activate_user_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting User Management Service...")
    await init_db()
    logger.info("✅ Service started successfully")
    yield

    # Shutdown
    logger.info("⏹️ Shutting down User Management Service...")
    await close_db()
    logger.info("✅ Service shut down successfully")


# Create FastAPI app with docs at /api/v1/docs
app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Include all route routers
app.include_router(add_user_router)
app.include_router(edit_user_router)
app.include_router(view_user_router)
app.include_router(inactivate_user_router)
app.include_router(activate_user_router)


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status.
    """
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "docs": "/api/v1/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8003,
        reload=settings.DEBUG,
    )
