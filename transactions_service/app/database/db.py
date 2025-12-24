"""
Database Connection Module

Manages PostgreSQL connection pool using asyncpg.
Handles initialization, cleanup, and connection operations.
"""

import asyncpg
from typing import Optional
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """PostgreSQL connection pool manager."""

    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def initialize(cls) -> asyncpg.Pool:
        """
        Initialize and return PostgreSQL connection pool.
        
        Returns:
            asyncpg.Pool: Connection pool instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if cls._pool is not None:
            return cls._pool

        try:
            cls._pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_TIMEOUT,
            )
            logger.info("✅ Database connection pool initialized successfully")
            return cls._pool
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {str(e)}")
            raise ConnectionError(f"Database connection failed: {str(e)}")

    @classmethod
    async def close(cls) -> None:
        """
        Close database connection pool.
        """
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logger.info("✅ Database connection pool closed")

    @classmethod
    async def get_connection(cls) -> asyncpg.Connection:
        """
        Get a connection from the pool.
        
        Returns:
            asyncpg.Connection: A database connection
        """
        if cls._pool is None:
            await cls.initialize()
        return await cls._pool.acquire()

    @classmethod
    async def execute(
        cls,
        query: str,
        *args,
        fetch: bool = False,
        fetch_one: bool = False
    ) -> any:
        """
        Execute a query.
        
        Args:
            query: SQL query string
            args: Query parameters
            fetch: Return all rows
            fetch_one: Return single row
            
        Returns:
            Query result (list of dicts or single dict)
        """
        conn = await cls.get_connection()
        try:
            if fetch:
                return await conn.fetch(query, *args)
            elif fetch_one:
                return await conn.fetchrow(query, *args)
            else:
                return await conn.execute(query, *args)
        finally:
            await cls._pool.release(conn)

    @classmethod
    async def transaction(cls):
        """
        Get transaction context manager.
        
        Usage:
            async with database.transaction():
                # Transaction operations
        """
        conn = await cls.get_connection()
        return conn.transaction()


# Singleton instance
database = DatabaseConnection()
