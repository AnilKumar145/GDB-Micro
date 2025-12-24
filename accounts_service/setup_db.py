"""
Database Setup Script for Accounts Service

This script creates the database and tables from the schema file.
Run this ONCE before starting the application.

Usage:
    python setup_db.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings
from app.config.logging import setup_logging
import asyncpg

# Setup logging
logger = setup_logging()


async def setup_database():
    """Create database and tables from schema."""
    
    logger.info("🔧 Starting database setup...")
    
    # Connection string for postgres admin user
    db_url = str(settings.database_url)
    
    # Extract connection details
    if "postgresql://" in db_url:
        # Parse: postgresql://user:password@host:port/database
        parts = db_url.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        host_port = parts[1].split("/")
        host = host_port[0].split(":")[0]
        port = int(host_port[0].split(":")[1]) if ":" in host_port[0] else 5432
        database = host_port[1]
    else:
        logger.error("❌ Invalid DATABASE_URL format")
        print("❌ Invalid DATABASE_URL format")
        return False
    
    try:
        print(f"📡 Connecting to PostgreSQL at {host}:{port}...")
        logger.info(f"Connecting to PostgreSQL at {host}:{port}...")
        
        # Connect to postgres database first to create gdb_accounts_db
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        print(f"✅ Connected to PostgreSQL")
        logger.info(f"✅ Connected to PostgreSQL")
        
        # Check if database exists
        db_exists = await conn.fetchval(
            f"SELECT 1 FROM pg_database WHERE datname = $1",
            database
        )
        
        if not db_exists:
            print(f"📦 Creating database '{database}'...")
            logger.info(f"Creating database '{database}'...")
            await conn.execute(f"CREATE DATABASE {database}")
            print(f"✅ Database '{database}' created")
            logger.info(f"✅ Database '{database}' created")
        else:
            print(f"✅ Database '{database}' already exists")
            logger.info(f"Database '{database}' already exists")
        
        await conn.close()
        
        # Now connect to gdb_accounts_db and create tables
        print(f"\n📡 Connecting to {database}...")
        logger.info(f"Connecting to {database}...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        print(f"✅ Connected to {database}")
        logger.info(f"✅ Connected to {database}")
        
        # Read and execute schema
        schema_file = Path(__file__).parent.parent / "database_schemas" / "accounts_schema.sql"
        
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            logger.error(f"Schema file not found: {schema_file}")
            await conn.close()
            return False
        
        print(f"\n📋 Reading schema from {schema_file.name}...")
        logger.info(f"Reading schema from {schema_file.name}...")
        with open(schema_file, "r") as f:
            schema_sql = f.read()
        
        # Execute schema
        print("🔨 Creating tables and objects...")
        logger.info("Creating tables and objects...")
        await conn.execute(schema_sql)
        logger.info("✅ Schema executed successfully")
        
        print("✅ All tables created successfully!")
        logger.info("✅ All tables created successfully!")
        
        # List created tables
        tables = await conn.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        
        print(f"\n📊 Created tables ({len(tables)}):")
        logger.info(f"Created {len(tables)} tables:")
        for table in tables:
            print(f"   ✓ {table['table_name']}")
            logger.info(f"   ✓ {table['table_name']}")
        
        await conn.close()
        return True
        
    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"Database error: {e}")
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return False


async def main():
    """Main entry point."""
    print("=" * 60)
    print("🏦 GDB Accounts Service - Database Setup")
    print("=" * 60)
    print()
    
    logger.info("=" * 60)
    logger.info("🏦 GDB Accounts Service - Database Setup")
    logger.info("=" * 60)
    
    success = await setup_database()
    
    print()
    if success:
        print("✅ Database setup completed successfully!")
        logger.info("✅ Database setup completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Start the server: python -m uvicorn app.main:app --reload --port 8001")
        print("   2. Access API docs: http://localhost:8001/api/v1/docs")
        sys.exit(0)
    else:
        print("❌ Database setup failed. Check the errors above.")
        logger.error("❌ Database setup failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
