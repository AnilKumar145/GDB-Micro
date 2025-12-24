#!/usr/bin/env python3
"""
Database Reset Script

Drops and recreates all tables in the PostgreSQL database for the Transactions Service.
This is useful for development and testing to reset the database to a clean state.

⚠️  WARNING: This will delete ALL data in the database. Use with caution!

Usage:
    python reset_db.py
"""

import asyncio
import asyncpg
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# SQL for dropping tables
DROP_TRANSACTION_LOGS_TABLE = """
DROP TABLE IF EXISTS transaction_logs CASCADE;
"""

DROP_TRANSFER_LIMITS_TABLE = """
DROP TABLE IF EXISTS transfer_limits CASCADE;
"""

DROP_FUND_TRANSFERS_TABLE = """
DROP TABLE IF EXISTS fund_transfers CASCADE;
"""

# SQL Schemas for creating tables
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
    
    -- Constraints
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
    
    -- Constraints
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


async def confirm_reset():
    """Ask user for confirmation before resetting database."""
    
    print("\n" + "="*70)
    print("⚠️  WARNING: DATABASE RESET")
    print("="*70)
    print(f"\nDatabase: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print("\nThis operation will:")
    print("  1. DROP all existing tables (transaction_logs, fund_transfers, transfer_limits)")
    print("  2. DELETE all data permanently")
    print("  3. Recreate empty tables with proper schema")
    print("\n⚠️  THIS CANNOT BE UNDONE!")
    print("="*70)
    
    confirmation = input("\nType 'yes' to proceed with database reset: ").strip().lower()
    
    if confirmation != 'yes':
        logger.info("❌ Reset cancelled by user")
        return False
    
    return True


async def drop_tables(connection):
    """Drop all existing tables."""
    
    logger.info("\n📋 Dropping existing tables...")
    
    try:
        # Drop in correct order (dependent tables first)
        await connection.execute(DROP_TRANSACTION_LOGS_TABLE)
        logger.info("  ✓ Dropped transaction_logs table")
        
        await connection.execute(DROP_TRANSFER_LIMITS_TABLE)
        logger.info("  ✓ Dropped transfer_limits table")
        
        await connection.execute(DROP_FUND_TRANSFERS_TABLE)
        logger.info("  ✓ Dropped fund_transfers table")
        
        logger.info("✅ All tables dropped successfully")
        return True
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error dropping tables: {str(e)}")
        raise


async def create_tables(connection):
    """Create all required tables."""
    
    logger.info("\n📋 Creating tables...")
    
    try:
        # Create in correct order (independent tables first)
        await connection.execute(CREATE_FUND_TRANSFERS_TABLE)
        logger.info("  ✓ Created fund_transfers table")
        
        await connection.execute(CREATE_TRANSACTION_LOGS_TABLE)
        logger.info("  ✓ Created transaction_logs table")
        
        await connection.execute(CREATE_TRANSFER_LIMITS_TABLE)
        logger.info("  ✓ Created transfer_limits table")
        
        logger.info("✅ All tables created successfully")
        return True
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        raise


async def verify_tables(connection):
    """Verify that all tables exist and show their structure."""
    
    logger.info("\n📊 Verifying tables...")
    
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
            logger.info("  Tables created:")
            for table in tables:
                table_name = table['table_name']
                # Get column count
                col_query = f"""
                SELECT COUNT(*) as cnt 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                """
                col_result = await connection.fetchrow(col_query)
                col_count = col_result['cnt']
                logger.info(f"    ✓ {table_name}: {col_count} columns, 0 rows")
        else:
            logger.warning("  No tables found!")
            return False
        
        logger.info("✅ All tables verified successfully")
        return True
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error verifying tables: {str(e)}")
        raise


async def reset_database():
    """Main function to reset the database."""
    
    # Connect to database
    try:
        connection = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
        )
        logger.info(f"✅ Connected to database: {settings.DB_NAME}")
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Failed to connect to database: {str(e)}")
        raise
    
    try:
        # Drop existing tables
        await drop_tables(connection)
        
        # Create fresh tables
        await create_tables(connection)
        
        # Verify tables
        await verify_tables(connection)
        
        logger.info("\n" + "="*70)
        logger.info("🎉 DATABASE RESET COMPLETED SUCCESSFULLY!")
        logger.info("="*70)
        logger.info(f"Database: {settings.DB_NAME}")
        logger.info(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"\n❌ Reset failed: {str(e)}")
        raise
    finally:
        await connection.close()
        logger.info("\n🔌 Database connection closed")


async def main():
    """Main entry point."""
    try:
        # Confirm before proceeding
        if not await confirm_reset():
            sys.exit(0)
        
        logger.info("\n🚀 Starting database reset...")
        logger.info(f"Database configuration:")
        logger.info(f"  Host: {settings.DB_HOST}")
        logger.info(f"  Port: {settings.DB_PORT}")
        logger.info(f"  Database: {settings.DB_NAME}")
        logger.info(f"  User: {settings.DB_USER}\n")
        
        # Reset database
        await reset_database()
        
    except Exception as e:
        logger.error(f"\n❌ Reset failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
