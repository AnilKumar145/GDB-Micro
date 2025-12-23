#!/usr/bin/env python3
"""
Users Service Database Setup Script
Purpose: Create database tables and schema
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
os.chdir(current_dir)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_database():
    """Create database tables and schema"""
    try:
        import asyncpg
        
        # Load database config from .env
        db_host = os.getenv('DATABASE_HOST', 'localhost')
        db_port = int(os.getenv('DATABASE_PORT', 5432))
        db_name = os.getenv('DATABASE_NAME', 'gdb_users_db')
        db_user = os.getenv('DATABASE_USER', 'postgres')
        db_password = os.getenv('DATABASE_PASSWORD', '')
        
        logger.info("=" * 70)
        logger.info("🚀 SETTING UP DATABASE SCHEMA")
        logger.info("=" * 70)
        logger.info(f"\nTarget database: {db_name}")
        logger.info(f"Host: {db_host}:{db_port}")
        
        # Connect to the target database
        logger.info("\n1. Connecting to database...")
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        
        try:
            # Create users table
            logger.info("\n2. Creating users table...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGSERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    login_id VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER', 'TELLER', 'ADMIN')),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("✓ Users table created successfully")
            
            # Create indexes on users table
            logger.info("\n3. Creating indexes on users table...")
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_login_id ON users(login_id);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);"
            )
            logger.info("✓ Indexes created successfully")
            
            # Create user_audit_logs table
            logger.info("\n4. Creating user_audit_logs table...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_audit_logs (
                    log_id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    action VARCHAR(50) NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'INACTIVATE', 'REACTIVATE', 'PASSWORD_CHANGE')),
                    old_data JSONB,
                    new_data JSONB,
                    performed_by VARCHAR(255),
                    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("✓ Audit logs table created successfully")
            
            # Create indexes on audit_logs table
            logger.info("\n5. Creating indexes on user_audit_logs table...")
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_user_id ON user_audit_logs(user_id);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_action ON user_audit_logs(action);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_performed_at ON user_audit_logs(performed_at DESC);"
            )
            logger.info("✓ Audit logs indexes created successfully")
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            return True
            
        finally:
            await conn.close()
        
    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error("❌ DATABASE SETUP FAILED!")
        logger.error("=" * 70)
        logger.error(f"Error: {str(e)}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Ensure PostgreSQL is running")
        logger.error("2. Verify credentials in .env file")
        logger.error("3. Verify that the database exists")
        logger.error("=" * 70)
        return False


async def main():
    """Main entry point"""
    try:
        success = await setup_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
