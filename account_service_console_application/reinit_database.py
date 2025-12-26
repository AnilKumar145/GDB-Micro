"""
Reinitialize Database Script

This script will:
1. Drop the current GDB-GDB database
2. Create a fresh GDB-GDB database
3. Initialize the schema using init_db.py

Run this when you want a completely fresh start.
"""

import asyncio
import asyncpg
import subprocess
import sys
import os

async def reinit_database():
    """Reinitialize the database completely."""
    
    print("=" * 70)
    print("DATABASE REINITIALIZATION SCRIPT")
    print("=" * 70)
    print()
    
    # Database connection details
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "anil")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "GDB-GDB")
    
    # Connect to postgres (not to GDB-GDB)
    try:
        conn = await asyncpg.connect(
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
        )
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    
    try:
        # Terminate existing connections to the database
        print(f"\n1. Terminating existing connections to {db_name}...")
        try:
            await conn.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid();
            """)
            print(f"   ✅ Terminated existing connections")
        except Exception as e:
            print(f"   ⚠ {e}")
        
        # Drop database
        print(f"\n2. Dropping database {db_name}...")
        try:
            await conn.execute(f"DROP DATABASE IF EXISTS \"{db_name}\"")
            print(f"   ✅ Dropped database {db_name}")
        except Exception as e:
            print(f"   ❌ Error dropping database: {e}")
            await conn.close()
            return False
        
        # Create database
        print(f"\n3. Creating fresh database {db_name}...")
        try:
            await conn.execute(f"CREATE DATABASE \"{db_name}\"")
            print(f"   ✅ Created database {db_name}")
        except Exception as e:
            print(f"   ❌ Error creating database: {e}")
            await conn.close()
            return False
        
        await conn.close()
        
        # Now initialize schema
        print(f"\n4. Initializing schema...")
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Import and run init_schema
        from database.init_db import init_schema
        await init_schema(database_url)
        
        print()
        print("=" * 70)
        print("SUCCESS: Database reinitialized!")
        print("=" * 70)
        print()
        print("The database is now ready with:")
        print("  - accounts table (id, account_number, account_type, name, ...)")
        print("  - savings_account_details table")
        print("  - current_account_details table")
        print("  - account_number_seq sequence (starts at 1000)")
        print()
        print("Next steps:")
        print("  1. Run: python main.py")
        print("  2. Create accounts (account numbers will be 1000, 1001, 1002, ...)")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(reinit_database())
    sys.exit(0 if success else 1)
