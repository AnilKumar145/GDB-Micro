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


# SQL Schemas
CREATE_FUND_TRANSFERS_TABLE = """
CREATE TABLE IF NOT EXISTS fund_transfers (
    id SERIAL PRIMARY KEY,
    transaction_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    account_number VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    balance_after DECIMAL(15, 2),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    description VARCHAR(500),
    reference_number VARCHAR(100),
    from_account VARCHAR(50),
    to_account VARCHAR(50),
    transfer_mode VARCHAR(20),
    encrypted_pin VARCHAR(255),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    idempotency_key VARCHAR(255) UNIQUE,
    
    -- Indexes for common queries
    CONSTRAINT chk_transaction_type CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAW', 'TRANSFER')),
    CONSTRAINT chk_status CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    CONSTRAINT chk_transfer_mode CHECK (transfer_mode IS NULL OR transfer_mode IN ('NEFT', 'RTGS', 'IMPS', 'UPI'))
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_fund_transfers_account_number ON fund_transfers(account_number);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_transaction_type ON fund_transfers(transaction_type);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_status ON fund_transfers(status);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_created_at ON fund_transfers(created_at);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_transaction_id ON fund_transfers(transaction_id);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_idempotency_key ON fund_transfers(idempotency_key);
"""

CREATE_TRANSACTION_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS transaction_logs (
    id SERIAL PRIMARY KEY,
    fund_transfer_id INTEGER NOT NULL REFERENCES fund_transfers(id) ON DELETE CASCADE,
    account_number VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    log_type VARCHAR(50) NOT NULL,
    log_message TEXT,
    error_code VARCHAR(50),
    error_message TEXT,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for better query performance
    CONSTRAINT chk_log_type CHECK (log_type IN ('INFO', 'WARNING', 'ERROR', 'DEBUG', 'AUDIT'))
);

-- Create indexes for transaction logs
CREATE INDEX IF NOT EXISTS idx_transaction_logs_fund_transfer_id ON transaction_logs(fund_transfer_id);
CREATE INDEX IF NOT EXISTS idx_transaction_logs_account_number ON transaction_logs(account_number);
CREATE INDEX IF NOT EXISTS idx_transaction_logs_created_at ON transaction_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_transaction_logs_log_type ON transaction_logs(log_type);
"""

CREATE_TRANSFER_LIMITS_TABLE = """
CREATE TABLE IF NOT EXISTS transfer_limits (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(50) NOT NULL UNIQUE,
    privilege_level VARCHAR(20) NOT NULL,
    daily_limit DECIMAL(15, 2) NOT NULL,
    daily_transaction_count INTEGER NOT NULL,
    current_day_amount DECIMAL(15, 2) DEFAULT 0,
    current_day_transaction_count INTEGER DEFAULT 0,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_privilege_level CHECK (privilege_level IN ('PREMIUM', 'GOLD', 'SILVER', 'BASIC')),
    CONSTRAINT chk_amounts_positive CHECK (daily_limit > 0 AND current_day_amount >= 0)
);

-- Create indexes for transfer limits
CREATE INDEX IF NOT EXISTS idx_transfer_limits_account_number ON transfer_limits(account_number);
CREATE INDEX IF NOT EXISTS idx_transfer_limits_privilege_level ON transfer_limits(privilege_level);
CREATE INDEX IF NOT EXISTS idx_transfer_limits_last_reset_date ON transfer_limits(last_reset_date);
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
        
        # Create transaction_logs table
        logger.info("📋 Creating transaction_logs table...")
        await connection.execute(CREATE_TRANSACTION_LOGS_TABLE)
        logger.info("✅ transaction_logs table created successfully")
        
        # Create transfer_limits table
        logger.info("📋 Creating transfer_limits table...")
        await connection.execute(CREATE_TRANSFER_LIMITS_TABLE)
        logger.info("✅ transfer_limits table created successfully")
        
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
