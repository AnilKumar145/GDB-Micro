#!/usr/bin/env python3
"""
Migration Script: Add account_number column to transaction_logging table

This script adds the missing account_number column to the existing transaction_logging table
without dropping data.

Usage:
    python migrate_add_account_number.py
"""

import asyncio
import asyncpg
import logging
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


async def migrate():
    """Add account_number column to transaction_logging table."""
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_name = os.getenv("DB_NAME", "gdb_transactions_db")
    
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
        # Check if column already exists
        check_column = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'transaction_logging' 
            AND column_name = 'account_number'
        """
        result = await connection.fetchval(check_column)
        
        if result:
            logger.info("✅ Column account_number already exists")
            return
        
        logger.info("📋 Adding account_number column to transaction_logging table...")
        
        # Add the column with a default value of 0
        add_column = """
            ALTER TABLE transaction_logging
            ADD COLUMN account_number BIGINT NOT NULL DEFAULT 0
        """
        await connection.execute(add_column)
        logger.info("  ✓ Added account_number column with default value 0")
        
        # Add index for the new column
        add_index = """
            CREATE INDEX IF NOT EXISTS idx_transaction_logging_account 
            ON transaction_logging(account_number)
        """
        await connection.execute(add_index)
        logger.info("  ✓ Added index on account_number")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("✅ transaction_logging table now has account_number column")
        logger.info("\nNote: Existing logs have account_number = 0")
        logger.info("New transactions will have proper account_number values")
        logger.info("="*60)
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        await connection.close()
        logger.info("🔌 Database connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)
