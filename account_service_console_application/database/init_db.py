"""
Database Schema Initialization

PostgreSQL schema initialization script.
Use this script to initialize the database for the console application.

Note: This creates the same schema as the FastAPI accounts_service.
Run this script ONCE when first setting up the console application.

Author: GDB Architecture Team
"""

import asyncio
import asyncpg
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def init_schema(database_url: str, min_size: int = 2, max_size: int = 10) -> None:
    """
    Initialize database schema.
    
    Creates all required tables and sequences.
    
    Args:
        database_url: PostgreSQL connection URL
        min_size: Minimum pool size (ignored, for compatibility)
        max_size: Maximum pool size (ignored, for compatibility)
    """
    # Connect to database
    conn = await asyncpg.connect(database_url)
    
    try:
        # Drop existing tables to start fresh
        await conn.execute("""
            DROP TABLE IF EXISTS current_account_details CASCADE;
            DROP TABLE IF EXISTS savings_account_details CASCADE;
            DROP TABLE IF EXISTS accounts CASCADE;
            DROP SEQUENCE IF EXISTS account_number_seq CASCADE;
        """)
        logger.info("✅ Dropped existing tables and sequences")
        
        # Create account_number sequence - starts at 1000
        await conn.execute("""
            CREATE SEQUENCE account_number_seq START WITH 1000 INCREMENT BY 1;
        """)
        logger.info("✅ Created account_number_seq sequence (START 1000)")
        
        # Create accounts table - NO DEFAULT for account_number, must be explicit
        await conn.execute("""
            CREATE TABLE accounts (
                id SERIAL PRIMARY KEY,
                account_number INTEGER UNIQUE NOT NULL,
                account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('SAVINGS', 'CURRENT')),
                name VARCHAR(255) NOT NULL,
                pin_hash VARCHAR(255) NOT NULL,
                balance NUMERIC(15,2) NOT NULL DEFAULT 0.00,
                privilege VARCHAR(20) NOT NULL DEFAULT 'SILVER' CHECK (privilege IN ('PREMIUM', 'GOLD', 'SILVER')),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                activated_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                closed_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.info("✅ Created accounts table (no DEFAULT for account_number)")
        
        # Create savings_account_details table
        await conn.execute("""
            CREATE TABLE savings_account_details (
                id SERIAL PRIMARY KEY,
                account_number INTEGER UNIQUE NOT NULL,
                date_of_birth DATE NOT NULL,
                gender VARCHAR(20) NOT NULL CHECK (gender IN ('Male', 'Female', 'Others')),
                phone_no VARCHAR(20) NOT NULL,
                CONSTRAINT fk_savings_account FOREIGN KEY (account_number) 
                    REFERENCES accounts(account_number) ON DELETE CASCADE
            );
        """)
        logger.info("✅ Created savings_account_details table")
        
        # Create current_account_details table
        await conn.execute("""
            CREATE TABLE current_account_details (
                id SERIAL PRIMARY KEY,
                account_number INTEGER UNIQUE NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                website VARCHAR(255),
                registration_no VARCHAR(50) NOT NULL UNIQUE,
                CONSTRAINT fk_current_account FOREIGN KEY (account_number) 
                    REFERENCES accounts(account_number) ON DELETE CASCADE
            );
        """)
        logger.info("✅ Created current_account_details table")
        
        # Create indexes for better performance
        await conn.execute("""
            CREATE INDEX idx_account_type ON accounts(account_type);
        """)
        
        await conn.execute("""
            CREATE INDEX idx_account_name ON accounts(name);
        """)
        
        await conn.execute("""
            CREATE INDEX idx_account_active ON accounts(is_active);
        """)
        
        await conn.execute("""
            CREATE INDEX idx_savings_phone ON savings_account_details(phone_no);
        """)
        
        await conn.execute("""
            CREATE INDEX idx_current_registration ON current_account_details(registration_no);
        """)
        
        logger.info("✅ Created indexes")
        logger.info("✅ Database schema initialized successfully")
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error initializing schema: {e}")
        raise
    finally:
        await conn.close()


def main() -> None:
    """Run database initialization."""
    import os
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get database URL
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:anil@localhost:5432/GDB-GDB"
    )
    
    print(f"Initializing database: {db_url}")
    print()
    
    # Run initialization
    asyncio.run(init_schema(db_url))
    print("\n✅ Database initialization complete!")


if __name__ == "__main__":
    main()

