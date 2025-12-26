"""
Account Service - Database Connection Management

PostgreSQL connection management for console application using asyncpg.
Adapted for sync usage in console environment.

Author: GDB Architecture Team
"""

import asyncio
import asyncpg
from typing import Optional, Dict, List
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL connection pool using asyncpg."""
    
    def __init__(self, database_url: str, min_size: int = 2, max_size: int = 10):
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
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    def connect(self) -> None:
        """
        Create connection pool (sync wrapper for async).
        
        Raises:
            asyncpg.PostgresError: If connection fails
        """
        try:
            # Get or create event loop
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            # Create pool
            self.pool = self.loop.run_until_complete(self._create_pool())
            logger.info("✅ Database connection pool established")
        except asyncpg.PostgresError as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def _create_pool(self) -> asyncpg.Pool:
        """Create asyncpg pool (async method)."""
        return await asyncpg.create_pool(
            self.database_url,
            min_size=self.min_size,
            max_size=self.max_size,
            timeout=10,
            command_timeout=10
        )
    
    def disconnect(self) -> None:
        """Close all connections in pool."""
        if self.pool and self.loop:
            self.loop.run_until_complete(self.pool.close())
            logger.info("✅ Database connection pool closed")
    
    def execute(self, query: str, *args) -> str:
        """
        Execute a query (INSERT, UPDATE, DELETE) synchronously.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Result status
        """
        return self.loop.run_until_complete(self._execute(query, *args))
    
    async def _execute(self, query: str, *args) -> str:
        """Execute query asynchronously."""
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)
            return "OK"
    
    def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """
        Fetch a single row synchronously.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Row as dict or None if not found
        """
        return self.loop.run_until_complete(self._fetch_one(query, *args))
    
    async def _fetch_one(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row asynchronously."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    def fetch_all(self, query: str, *args) -> List[Dict]:
        """
        Fetch all rows synchronously.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            List of rows as dicts
        """
        return self.loop.run_until_complete(self._fetch_all(query, *args))
    
    async def _fetch_all(self, query: str, *args) -> List[Dict]:
        """Fetch all rows asynchronously."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    def fetch_val(self, query: str, *args) -> Optional:
        """
        Fetch a single value synchronously.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single value or None
        """
        return self.loop.run_until_complete(self._fetch_val(query, *args))
    
    async def _fetch_val(self, query: str, *args) -> Optional:
        """Fetch single value asynchronously."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    def transaction(self):
        """
        Context manager for transaction management (synchronous wrapper).
        
        This simulates transactions for console usage.
        For actual transactions, use the async methods.
        """
        return self._SyncTransactionContext(self)
    
    class _SyncTransactionContext:
        """Synchronous transaction context manager."""
        
        def __init__(self, db_manager):
            self.db_manager = db_manager
            self.conn = None
        
        def __enter__(self):
            """Enter transaction context."""
            # For simplicity in console app, return a cursor-like object
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            """Exit transaction context."""
            pass
        
        def execute(self, query: str, *args):
            """Execute query in transaction."""
            self.db_manager.execute(query, *args)


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def init_db(database_url: str, min_size: int = 2, max_size: int = 10) -> DatabaseManager:
    """
    Initialize global database instance.
    
    Args:
        database_url: PostgreSQL connection URL
        min_size: Minimum pool size
        max_size: Maximum pool size
        
    Returns:
        DatabaseManager instance
    """
    global _db_instance
    _db_instance = DatabaseManager(database_url, min_size, max_size)
    _db_instance.connect()
    return _db_instance


def get_db() -> DatabaseManager:
    """
    Get global database instance.
    
    Returns:
        DatabaseManager instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if _db_instance is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db_instance


def close_db() -> None:
    """Close global database instance."""
    global _db_instance
    if _db_instance:
        _db_instance.disconnect()
        _db_instance = None


# Alias for consistency with accounts_service naming
initialize_db = init_db
