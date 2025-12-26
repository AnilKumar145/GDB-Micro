"""
Database Reset Script

Drops and recreates the GDB-GDB database to start fresh.

Usage:
    python reset_database.py
"""

import subprocess
import sys
import os

def reset_database():
    """Reset the PostgreSQL database."""
    
    # PostgreSQL credentials
    user = "postgres"
    password = "anil"
    host = "localhost"
    database = "GDB-GDB"
    
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print()
    
    # Set PGPASSWORD environment variable for non-interactive password entry
    os.environ['PGPASSWORD'] = password
    
    try:
        # Step 1: Drop the database
        print(f"Dropping database: {database}")
        drop_cmd = [
            "psql",
            "-U", user,
            "-h", host,
            "-d", "postgres",
            "-c", f"DROP DATABASE IF EXISTS \"{database}\" WITH (FORCE);"
        ]
        result = subprocess.run(drop_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error dropping database: {result.stderr}")
            return False
        print("✅ Database dropped")
        print()
        
        # Step 2: Create the database
        print(f"Creating database: {database}")
        create_cmd = [
            "psql",
            "-U", user,
            "-h", host,
            "-d", "postgres",
            "-c", f"CREATE DATABASE \"{database}\";"
        ]
        result = subprocess.run(create_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error creating database: {result.stderr}")
            return False
        print("✅ Database created")
        print()
        
        # Step 3: Initialize schema
        print("Initializing database schema...")
        print("Run: python database/init_db.py")
        print()
        
        print("=" * 60)
        print("✅ DATABASE RESET COMPLETE")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. python database/init_db.py")
        print("2. python main.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Clean up environment variable
        if 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD']


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
