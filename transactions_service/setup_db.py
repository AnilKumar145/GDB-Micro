#!/usr/bin/env python3
"""
Database Setup Script

Creates all necessary tables in the PostgreSQL database for the Transactions Service.
Run this script once to initialize the database schema.

Usage:
    python setup_db.py
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


# SQL Schemas - Simplified for transaction tracking
CREATE_FUND_TRANSFERS_TABLE = """
CREATE TABLE IF NOT EXISTS fund_transfers (
    id BIGSERIAL PRIMARY KEY,
    from_account BIGINT NOT NULL,
    to_account BIGINT NOT NULL,
    transfer_amount NUMERIC(15, 2) NOT NULL,
    transfer_mode VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_transfer_amount CHECK (transfer_amount > 0),
    CONSTRAINT chk_from_not_equal_to CHECK (from_account <> to_account),
    CONSTRAINT chk_transfer_mode CHECK (
        transfer_mode IN ('NEFT', 'RTGS', 'IMPS', 'UPI')
    )
);

-- Indexes for fund_transfers
CREATE INDEX IF NOT EXISTS idx_fund_transfers_from_account ON fund_transfers(from_account);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_to_account ON fund_transfers(to_account);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_created_at ON fund_transfers(created_at);
"""

CREATE_TRANSACTION_LOGGING_TABLE = """
CREATE TABLE IF NOT EXISTS transaction_logging (
    id BIGSERIAL PRIMARY KEY,
    account_number BIGINT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_transaction_amount CHECK (amount > 0),
    CONSTRAINT chk_transaction_type CHECK (
        transaction_type IN ('WITHDRAW', 'DEPOSIT', 'TRANSFER')
    )
);

-- Indexes for transaction_logging
CREATE INDEX IF NOT EXISTS idx_transaction_logging_account ON transaction_logging(account_number);
CREATE INDEX IF NOT EXISTS idx_transaction_logging_type ON transaction_logging(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transaction_logging_created_at ON transaction_logging(created_at);
"""


async def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "gdb_transactions_db")
    
    try:
        # First, try to connect to the postgres database to check/create target database
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
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "gdb_transactions_db")
    
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
        # Create fund_transfers table
        logger.info("📋 Creating fund_transfers table...")
        await connection.execute(CREATE_FUND_TRANSFERS_TABLE)
        logger.info("✅ fund_transfers table created successfully")
        
        # Create transaction_logging table
        logger.info("📋 Creating transaction_logging table...")
        await connection.execute(CREATE_TRANSACTION_LOGGING_TABLE)
        logger.info("✅ transaction_logging table created successfully")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 All tables created successfully!")
        logger.info("="*60)
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", 5432))
        db_name = os.getenv("DB_NAME", "gdb_transactions_db")
        logger.info(f"Database: {db_name}")
        logger.info(f"Host: {db_host}:{db_port}")
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
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "gdb_transactions_db")
    
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
            
    finally:
        await connection.close()


async def main():
    """Main entry point."""
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", 5432))
        db_user = os.getenv("DB_USER", "postgres")
        db_name = os.getenv("DB_NAME", "gdb_transactions_db")
        
        logger.info("🚀 Starting database setup...")
        logger.info(f"Database configuration:")
        logger.info(f"  Host: {db_host}")
        logger.info(f"  Port: {db_port}")
        logger.info(f"  Database: {db_name}")
        logger.info(f"  User: {db_user}\n")
        
        # Create tables
        await create_tables()
        
        # Verify tables
        await verify_tables()
        
    except Exception as e:
        logger.error(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
