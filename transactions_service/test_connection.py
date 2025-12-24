#!/usr/bin/env python3
"""
Simple PostgreSQL Connection Tester

Tests various connection methods to diagnose the issue.
"""

import asyncpg
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings


async def test_connection(description, host, port, user, password, database):
    """Test a specific connection."""
    print(f"\n🔍 Testing: {description}")
    print(f"   Connection: {user}@{host}:{port}/{database}")
    
    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"   ✅ SUCCESS!")
        print(f"   Version: {version[:60]}...")
        return True
    except asyncpg.InvalidPasswordError:
        print(f"   ❌ INVALID PASSWORD")
        return False
    except asyncpg.PostgresError as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        return False


async def main():
    """Main function."""
    print("\n" + "="*70)
    print("🧪 PostgreSQL Connection Diagnostics")
    print("="*70)
    
    print(f"\n📋 Settings from .env:")
    print(f"   Host:     {settings.DB_HOST}")
    print(f"   Port:     {settings.DB_PORT}")
    print(f"   User:     {settings.DB_USER}")
    print(f"   Password: {'*' * len(settings.DB_PASSWORD)}")
    print(f"   Database: {settings.DB_NAME}")
    
    # Test 1: Connect to postgres database
    result1 = await test_connection(
        "Connect to 'postgres' database (server check)",
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_USER,
        settings.DB_PASSWORD,
        "postgres"
    )
    
    # Test 2: Connect to target database
    result2 = await test_connection(
        f"Connect to '{settings.DB_NAME}' database",
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_USER,
        settings.DB_PASSWORD,
        settings.DB_NAME
    )
    
    # Summary
    print("\n" + "="*70)
    print("📊 Results Summary")
    print("="*70)
    
    if result1:
        print(f"✅ Can connect to 'postgres' database")
    else:
        print(f"❌ Cannot connect to 'postgres' database")
    
    if result2:
        print(f"✅ Can connect to '{settings.DB_NAME}' database")
    else:
        print(f"❌ Cannot connect to '{settings.DB_NAME}' database")
    
    print("\n" + "="*70)
    
    if result1 and result2:
        print("🎉 All connections successful!")
        print("\nNext step: python setup_db.py")
        print("="*70 + "\n")
        return 0
    elif result1 and not result2:
        print("⚠️  Server is OK, but database may not exist")
        print("\nNext step: python setup_postgres.py")
        print("="*70 + "\n")
        return 1
    else:
        print("❌ Cannot connect to PostgreSQL server")
        print("\nCheck:")
        print("1. Is PostgreSQL running? (net start PostgreSQL14)")
        print("2. Is password 'anil' correct?")
        print("3. Is host 'localhost' and port 5432 correct?")
        print("="*70 + "\n")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
