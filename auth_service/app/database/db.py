"""
Database Connection Management

Handles connection pooling and initialization for gdb_auth_db.
Uses asyncpg for high-performance async PostgreSQL access.

Author: GDB Architecture Team
"""

import asyncpg
import logging
from typing import Optional
from app.config.settings import settings


logger = logging.getLogger(__name__)


class Database:
    """AsyncPG database connection pool manager."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """
        Initialize database connection pool.
        
        Called during application startup.
        """
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                min_size=settings.MIN_DB_POOL_SIZE,
                max_size=settings.MAX_DB_POOL_SIZE,
            )
            logger.info(
                f"Connected to database: {settings.DATABASE_NAME} "
                f"at {settings.DATABASE_HOST}:{settings.DATABASE_PORT}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close database connection pool.
        
        Called during application shutdown.
        """
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def execute(
        self,
        query: str,
        *args,
        timeout: float = 10.0,
    ) -> None:
        """
        Execute a query that doesn't return rows (INSERT, UPDATE, DELETE, etc).
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
        
        Raises:
            Exception: If query fails
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args, timeout=timeout)
    
    async def fetch(
        self,
        query: str,
        *args,
        timeout: float = 10.0,
    ) -> list:
        """
        Fetch multiple rows from query result.
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
        
        Returns:
            List of asyncpg.Record objects
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args, timeout=timeout)
    
    async def fetchrow(
        self,
        query: str,
        *args,
        timeout: float = 10.0,
    ) -> Optional[dict]:
        """
        Fetch single row from query result.
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
        
        Returns:
            Single row as dict-like object or None if no rows
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args, timeout=timeout)
            return row
    
    async def fetchval(
        self,
        query: str,
        *args,
        timeout: float = 10.0,
    ) -> Optional[any]:
        """
        Fetch single value from query result.
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
        
        Returns:
            Single scalar value or None
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args, timeout=timeout)


# Global database instance
db = Database()
