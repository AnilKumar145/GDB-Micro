#!/usr/bin/env python3
"""
PostgreSQL Diagnostics and Database Setup Script

This script helps diagnose and resolve PostgreSQL connection issues,
and creates the database if it doesn't exist.

Usage:
    python setup_postgres.py
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings


async def test_postgres_connection():
    """Test connection to PostgreSQL server."""
    print("\n" + "="*70)
    print("🔍 STEP 1: Testing PostgreSQL Server Connection")
    print("="*70)
    
    try:
        # Try connecting to 'postgres' database with postgres user
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user="postgres",
            password="postgres",  # Default password
            database="postgres"
        )
        await conn.close()
        print("✅ PostgreSQL server is running!")
        print(f"   Host: {settings.DB_HOST}:{settings.DB_PORT}")
        return True
    except asyncpg.InvalidPasswordError:
        print("⚠️  PostgreSQL server is running but password is incorrect")
        print("   Default password 'postgres' is wrong")
        return None
    except asyncpg.PostgresError as e:
        print(f"❌ Cannot connect to PostgreSQL: {str(e)}")
        print("\n   Troubleshooting:")
        print("   1. Is PostgreSQL installed?")
        print("   2. Is PostgreSQL service running?")
        print("      - Windows: Check Services app for 'PostgreSQL'")
        print("      - Run: sc query PostgreSQL14")
        print("   3. Is it listening on port 5432?")
        print("      - Run: netstat -an | findstr 5432")
        return False


async def test_database_exists():
    """Check if transactions database exists."""
    print("\n" + "="*70)
    print("🔍 STEP 2: Checking if Database Exists")
    print("="*70)
    
    try:
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        await conn.close()
        print(f"✅ Database '{settings.DB_NAME}' exists and is accessible!")
        return True
    except asyncpg.InvalidPasswordError:
        print(f"❌ Wrong password for user '{settings.DB_USER}'")
        print(f"   Database: {settings.DB_NAME}")
        print(f"   User: {settings.DB_USER}")
        print(f"   Password in .env might be incorrect")
        return False
    except asyncpg.PostgresError as e:
        if "does not exist" in str(e):
            print(f"⚠️  Database '{settings.DB_NAME}' does not exist")
            print("   Need to create it...")
            return None
        else:
            print(f"❌ Error: {str(e)}")
            return False


async def create_database():
    """Create the transactions database."""
    print("\n" + "="*70)
    print("🔨 STEP 3: Creating Database")
    print("="*70)
    
    try:
        # Connect to postgres database
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database="postgres"
        )
        
        # Check if database already exists
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.DB_NAME
        )
        
        if db_exists:
            print(f"✅ Database '{settings.DB_NAME}' already exists")
            await conn.close()
            return True
        
        # Create database
        print(f"📦 Creating database '{settings.DB_NAME}'...")
        await conn.execute(f"CREATE DATABASE {settings.DB_NAME}")
        print(f"✅ Database '{settings.DB_NAME}' created successfully!")
        
        await conn.close()
        return True
        
    except asyncpg.InvalidPasswordError:
        print(f"❌ Wrong password for user '{settings.DB_USER}'")
        print("\n   Solutions:")
        print("   1. Reset PostgreSQL password:")
        print("      - Windows: Use pgAdmin or psql")
        print(f"      - psql -U postgres -c \"ALTER USER {settings.DB_USER} WITH PASSWORD 'anil';\"")
        return False
    except asyncpg.PostgresError as e:
        print(f"❌ Error creating database: {str(e)}")
        return False


async def test_final_connection():
    """Test final connection to newly created database."""
    print("\n" + "="*70)
    print("✅ STEP 4: Verifying Final Connection")
    print("="*70)
    
    try:
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        # Get server info
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Successfully connected to '{settings.DB_NAME}'!")
        print(f"\nPostgreSQL Version:")
        print(f"   {version}")
        
        await conn.close()
        return True
        
    except asyncpg.PostgresError as e:
        print(f"❌ Final connection failed: {str(e)}")
        return False


async def show_connection_details():
    """Show current connection configuration."""
    print("\n" + "="*70)
    print("📋 Connection Configuration")
    print("="*70)
    print(f"Host:     {settings.DB_HOST}")
    print(f"Port:     {settings.DB_PORT}")
    print(f"User:     {settings.DB_USER}")
    print(f"Password: {'*' * len(settings.DB_PASSWORD)}")
    print(f"Database: {settings.DB_NAME}")
    print(f"URL:      postgresql://{settings.DB_USER}:***@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")


async def main():
    """Main diagnostic flow."""
    print("\n" + "="*70)
    print("🚀 PostgreSQL Diagnostics and Database Setup")
    print("="*70)
    
    await show_connection_details()
    
    # Step 1: Test PostgreSQL server
    server_ok = await test_postgres_connection()
    
    if server_ok is False:
        print("\n❌ PostgreSQL server is not accessible")
        print("\nPlease start PostgreSQL:")
        print("  1. Windows Services: Start PostgreSQL service")
        print("  2. Or run: net start PostgreSQL14")
        sys.exit(1)
    
    # Step 2: Check database exists
    db_ok = await test_database_exists()
    
    if db_ok is None or db_ok is False:
        # Step 3: Create database if needed
        if not await create_database():
            print("\n❌ Failed to create database")
            print("\nTroubleshooting:")
            print("  1. Verify PostgreSQL user password in .env")
            print("  2. Try resetting password:")
            print(f"     psql -U postgres -c \"ALTER USER {settings.DB_USER} WITH PASSWORD 'anil';\"")
            print("  3. Run this script again")
            sys.exit(1)
    
    # Step 4: Verify final connection
    if not await test_final_connection():
        sys.exit(1)
    
    # Success!
    print("\n" + "="*70)
    print("🎉 PostgreSQL Setup Complete!")
    print("="*70)
    print(f"\nDatabase '{settings.DB_NAME}' is ready!")
    print(f"\nNext step: Run 'python setup_db.py' to create tables")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
