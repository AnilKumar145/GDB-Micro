"""
Reset Database and Fix Account Number Sequence

This script will:
1. Drop all existing tables
2. Recreate tables with correct sequence starting from 1000
3. Initialize the database fresh

Usage:
    python reset_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings
import asyncpg


async def reset_database():
    """Reset database and create tables with correct sequence."""
    
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
        print("❌ Invalid DATABASE_URL format")
        return False
    
    try:
        print(f"📡 Connecting to PostgreSQL at {host}:{port}...")
        
        # Connect to postgres database first
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        print(f"✅ Connected to PostgreSQL")
        
        # Drop the database if it exists
        print(f"🗑️  Dropping existing database '{database}'...")
        try:
            # Terminate all connections to the database
            await conn.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{database}'
                AND pid <> pg_backend_pid();
            """)
            
            await conn.execute(f"DROP DATABASE IF EXISTS {database}")
            print(f"✅ Database '{database}' dropped")
        except Exception as e:
            print(f"⚠️  Warning: Could not drop database: {e}")
        
        await conn.close()
        
        # Reconnect and create fresh database
        print(f"\n📡 Reconnecting to PostgreSQL...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        # Create fresh database
        print(f"📦 Creating database '{database}'...")
        await conn.execute(f"CREATE DATABASE {database}")
        print(f"✅ Database '{database}' created")
        
        await conn.close()
        
        # Now connect to gdb_accounts_db and create tables
        print(f"\n📡 Connecting to {database}...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        print(f"✅ Connected to {database}")
        
        # Read and execute schema
        schema_file = Path(__file__).parent.parent / "database_schemas" / "accounts_schema.sql"
        
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            await conn.close()
            return False
        
        print(f"\n📋 Reading schema from {schema_file.name}...")
        with open(schema_file, "r") as f:
            schema_sql = f.read()
        
        # Execute schema
        print("🔨 Creating tables and objects...")
        await conn.execute(schema_sql)
        
        # Verify the sequence was created correctly
        print("\n🔍 Verifying sequence...")
        seq_info = await conn.fetchrow(
            "SELECT last_value, is_called FROM account_number_seq"
        )
        
        if seq_info:
            print(f"✅ Sequence 'account_number_seq' created")
            print(f"   Last value: {seq_info['last_value']}")
            print(f"   Next value will be: {seq_info['last_value'] + 1}")
        
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
        for table in tables:
            print(f"   ✓ {table['table_name']}")
        
        await conn.close()
        return True
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    print("=" * 60)
    print("🏦 GDB Accounts Service - Database Reset")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DROP all existing data!")
    print("=" * 60)
    print()
    
    response = input("Type 'YES' to proceed with database reset: ")
    
    if response.upper() != "YES":
        print("❌ Reset cancelled.")
        sys.exit(0)
    
    print()
    success = await reset_database()
    
    print()
    if success:
        print("✅ Database reset completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Start the server: python -m uvicorn app.main:app --reload --port 8001")
        print("   2. Create a new account - it will have account_number 1000")
        print("   3. Each new account will increment: 1001, 1002, 1003...")
        sys.exit(0)
    else:
        print("❌ Database reset failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
