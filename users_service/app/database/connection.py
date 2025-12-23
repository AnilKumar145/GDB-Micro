"""
User Management Service - Database Connection Management

This module provides async database connection pooling using asyncpg.
Raw SQL operations only - no ORM.
"""

import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages asyncpg connection pool for PostgreSQL.
    
    Provides async context managers for database operations.
    Ensures proper resource cleanup and connection pooling.
    """
    
    def __init__(self, database_url: str, min_size: int = 5, max_size: int = 20):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL
            min_size: Minimum pool size
            max_size: Maximum pool size
        """
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """
        Create connection pool.
        
        Raises:
            asyncpg.PostgresError: If connection fails
        """
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=self.min_size,
                max_size=self.max_size,
                timeout=10,
                command_timeout=10
            )
            logger.info("✅ Database connection pool established")
        except asyncpg.PostgresError as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close all connections in pool.
        """
        if self.pool:
            await self.pool.close()
            logger.info("✅ Database connection pool closed")
    
    @asynccontextmanager
    async def transaction(self):
        """
        Async context manager for transaction management.
        
        Yields:
            asyncpg.Connection: Database connection with active transaction
            
        Usage:
            async with db_manager.transaction() as conn:
                await conn.execute("INSERT INTO ...")
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a single connection from pool.
        
        Yields:
            asyncpg.Connection: Database connection
            
        Usage:
            async with db_manager.get_connection() as conn:
                result = await conn.fetch("SELECT ...")
        """
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args):
        """
        Execute a query that doesn't return results.
        
        Args:
            query: SQL query string
            *args: Query parameters
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """
        Fetch multiple rows from database.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            List of records as dictionaries
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """
        Fetch a single row from database.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single record as dictionary or None
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """
        Fetch a single value from database.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single value or None
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


async def init_db():
    """
    Initialize database connection pool.
    Called during application startup.
    """
    global db_manager
    
    # Build database URL from environment variables
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', 'gdb_users_db')
    db_user = os.getenv('DATABASE_USER', 'postgres')
    db_password = os.getenv('DATABASE_PASSWORD', '')
    
    if db_password:
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        database_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    logger.info(f"🚀 Initializing database connection to {db_name}@{db_host}:{db_port}")
    
    db_manager = DatabaseManager(database_url)
    await db_manager.connect()
    logger.info("✅ Database initialized successfully")


async def close_db():
    """
    Close database connection pool.
    Called during application shutdown.
    """
    global db_manager
    
    if db_manager:
        await db_manager.disconnect()
        db_manager = None
        logger.info("✅ Database closed successfully")


def get_db() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: The active database manager
        
    Raises:
        RuntimeError: If database manager is not initialized
    """
    if db_manager is None:
        raise RuntimeError("Database manager is not initialized. Call init_db() first.")
    return db_manager
