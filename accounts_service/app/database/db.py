"""
Accounts Service - Database Connection Management

This module provides async database connection pooling using asyncpg.
Raw SQL operations only - no ORM.

Author: GDB Architecture Team
"""

import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
import logging

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
        Async context manager to get a single connection.
        
        Yields:
            asyncpg.Connection: Database connection
        """
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Command completion status
        """
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Fetch a single row.
        
        Args:
            query: SQL SELECT query
            *args: Query parameters
            
        Returns:
            Single row as asyncpg.Record or None
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetch_all(self, query: str, *args) -> list:
        """
        Fetch multiple rows.
        
        Args:
            query: SQL SELECT query
            *args: Query parameters
            
        Returns:
            List of asyncpg.Record objects
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_val(self, query: str, *args):
        """
        Fetch a single scalar value.
        
        Args:
            query: SQL query returning single value
            *args: Query parameters
            
        Returns:
            Single scalar value
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database manager instance
db: Optional[DatabaseManager] = None


async def initialize_db(database_url: str, min_size: int = 5, max_size: int = 20) -> DatabaseManager:
    """
    Initialize global database manager.
    
    Args:
        database_url: PostgreSQL connection URL
        min_size: Minimum pool size
        max_size: Maximum pool size
        
    Returns:
        DatabaseManager instance
    """
    global db
    db = DatabaseManager(database_url, min_size, max_size)
    await db.connect()
    return db


async def close_db() -> None:
    """Close database connections."""
    global db
    if db:
        await db.disconnect()
        db = None


def get_db() -> DatabaseManager:
    """
    Get current database manager instance.
    
    Returns:
        DatabaseManager instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call initialize_db() first.")
    return db
