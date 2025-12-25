#!/usr/bin/env python3
"""
Authentication Service - Database Setup Script

Creates the gdb_auth_db database and runs the schema.
Run this once before starting the service.

Usage:
    python setup_db.py

Author: GDB Architecture Team
"""

import asyncio
import asyncpg
import logging
from datetime import datetime
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# SQL Schema for Auth Service
CREATE_AUTH_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    login_id VARCHAR(255) NOT NULL,
    token_jti VARCHAR(255) NOT NULL UNIQUE,
    issued_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_expiry CHECK (expires_at > issued_at)
);

-- Indexes for auth_tokens
CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_token_jti ON auth_tokens(token_jti);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_expires_at ON auth_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_is_revoked ON auth_tokens(is_revoked);
"""

CREATE_AUTH_AUDIT_LOGS_TABLE = """
CREATE TYPE auth_action_enum AS ENUM ('LOGIN_SUCCESS', 'LOGIN_FAILURE', 'TOKEN_REVOKED');

CREATE TABLE IF NOT EXISTS auth_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login_id VARCHAR(255) NOT NULL,
    user_id BIGINT,
    action auth_action_enum NOT NULL,
    reason VARCHAR(500),
    ip_address INET,
    user_agent VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for auth_audit_logs
CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_user_id ON auth_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_login_id ON auth_audit_logs(login_id);
CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_action ON auth_audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_created_at ON auth_audit_logs(created_at);
"""

CREATE_VIEWS = """
-- Active Tokens View
CREATE OR REPLACE VIEW active_auth_tokens AS
SELECT
    id,
    user_id,
    login_id,
    token_jti,
    issued_at,
    expires_at
FROM auth_tokens
WHERE is_revoked = FALSE
    AND expires_at > CURRENT_TIMESTAMP;

-- Recent Logins View
CREATE OR REPLACE VIEW recent_auth_logins AS
SELECT
    id,
    login_id,
    user_id,
    action,
    reason,
    ip_address,
    created_at
FROM auth_audit_logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY created_at DESC;

-- Failed Logins View
CREATE OR REPLACE VIEW failed_auth_logins AS
SELECT
    id,
    login_id,
    user_id,
    reason,
    ip_address,
    created_at
FROM auth_audit_logs
WHERE action = 'LOGIN_FAILURE'
ORDER BY created_at DESC;
"""

CREATE_CLEANUP_FUNCTION = """
-- Function to revoke expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS TABLE(revoked_count INTEGER) AS $$
DECLARE
    revoked_count INTEGER;
BEGIN
    UPDATE auth_tokens
    SET is_revoked = TRUE
    WHERE expires_at <= CURRENT_TIMESTAMP
        AND is_revoked = FALSE;
    
    GET DIAGNOSTICS revoked_count = ROW_COUNT;
    RETURN QUERY SELECT revoked_count;
END;
$$ LANGUAGE plpgsql;
"""


async def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = int(os.getenv("DATABASE_PORT", 5432))
    db_user = os.getenv("DATABASE_USER", "postgres")
    db_password = os.getenv("DATABASE_PASSWORD", "")
    db_name = os.getenv("DATABASE_NAME", "gdb_auth_db")
    
    try:
        # First, connect to the postgres database to check/create target database
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres",
        )
        
        # Check if database exists
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name
        )
        
        if not db_exists:
            logger.info(f"📦 Creating database: {db_name}")
            await conn.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ Database created: {db_name}")
        else:
            logger.info(f"✅ Database already exists: {db_name}")
        
        await conn.close()
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Failed to create database: {str(e)}")
        raise


async def create_tables():
    """Create all required tables in the database."""
    
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = int(os.getenv("DATABASE_PORT", 5432))
    db_user = os.getenv("DATABASE_USER", "postgres")
    db_password = os.getenv("DATABASE_PASSWORD", "")
    db_name = os.getenv("DATABASE_NAME", "gdb_auth_db")
    
    # First ensure database exists
    await create_database_if_not_exists()
    
    # Connect to database
    try:
        connection = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        logger.info(f"✅ Connected to database: {db_name}")
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Failed to connect to database: {str(e)}")
        raise
    
    try:
        # Create auth_tokens table
        logger.info("📋 Creating auth_tokens table...")
        await connection.execute(CREATE_AUTH_TOKENS_TABLE)
        logger.info("✅ auth_tokens table created successfully")
        
        # Create auth_audit_logs table
        logger.info("📋 Creating auth_audit_logs table...")
        await connection.execute(CREATE_AUTH_AUDIT_LOGS_TABLE)
        logger.info("✅ auth_audit_logs table created successfully")
        
        # Create views
        logger.info("📋 Creating views...")
        await connection.execute(CREATE_VIEWS)
        logger.info("✅ Views created successfully")
        
        # Create cleanup function
        logger.info("📋 Creating cleanup function...")
        await connection.execute(CREATE_CLEANUP_FUNCTION)
        logger.info("✅ Cleanup function created successfully")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 All tables created successfully!")
        logger.info("="*60)
        logger.info(f"Database: {db_name}")
        logger.info(f"Host: {db_host}:{db_port}")
        logger.info(f"User: {db_user}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("="*60)
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        raise
    finally:
        await connection.close()
        logger.info("🔌 Database connection closed")


async def verify_tables():
    """Verify that all tables were created successfully."""
    
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = int(os.getenv("DATABASE_PORT", 5432))
    db_user = os.getenv("DATABASE_USER", "postgres")
    db_password = os.getenv("DATABASE_PASSWORD", "")
    db_name = os.getenv("DATABASE_NAME", "gdb_auth_db")
    
    connection = await asyncpg.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
    )
    
    try:
        # Get list of tables
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        """
        tables = await connection.fetch(query)
        
        if tables:
            logger.info("\n📊 Tables in database:")
            for table in tables:
                table_name = table['table_name']
                # Get row count
                count_query = f"SELECT COUNT(*) as cnt FROM {table_name}"
                count_result = await connection.fetchrow(count_query)
                row_count = count_result['cnt']
                logger.info(f"  ✓ {table_name}: {row_count} rows")
        else:
            logger.warning("No tables found in database")
            
        # Check views
        logger.info("\n📊 Views in database:")
        views_query = """
        SELECT viewname FROM pg_views 
        WHERE schemaname = 'public' 
        ORDER BY viewname
        """
        views = await connection.fetch(views_query)
        if views:
            for view in views:
                logger.info(f"  ✓ {view['viewname']}")
        
    finally:
        await connection.close()


async def main():
    """Main entry point."""
    try:
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = int(os.getenv("DATABASE_PORT", 5432))
        db_user = os.getenv("DATABASE_USER", "postgres")
        db_name = os.getenv("DATABASE_NAME", "gdb_auth_db")
        
        logger.info("🚀 Starting authentication database setup...")
        logger.info(f"Database configuration:")
        logger.info(f"  Host: {db_host}")
        logger.info(f"  Port: {db_port}")
        logger.info(f"  Database: {db_name}")
        logger.info(f"  User: {db_user}\n")
        
        # Create tables
        await create_tables()
        
        # Verify tables
        await verify_tables()
        
        logger.info("\n" + "="*60)
        logger.info("✅ DATABASE SETUP COMPLETE!")
        logger.info("="*60)
        logger.info("\nNext steps:")
        logger.info("  1. Verify .env configuration")
        logger.info("  2. Run: python -m uvicorn app.main:app --reload")
        logger.info("  3. Test: curl http://localhost:8004/health")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
