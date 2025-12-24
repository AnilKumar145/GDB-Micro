#!/usr/bin/env python3
"""
PostgreSQL Password Reset Script

This script resets the PostgreSQL 'postgres' user password to 'anil'.
Run this if you get "password authentication failed" errors.

Prerequisites:
- PostgreSQL must be installed and running
- You must be able to connect without a password (peer authentication)
  OR you know the current postgres password

Usage:
    python reset_postgres_password.py

The script will:
1. Try to connect with 'trust' authentication (local connections)
2. Set postgres user password to 'anil'
3. Verify the new password works
"""

import subprocess
import sys
import asyncio
import asyncpg
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings


def run_psql_command(command: str, use_password: bool = False, password: str = None) -> tuple[bool, str]:
    """
    Execute a psql command.
    
    Args:
        command: SQL command to execute
        use_password: Whether to use password authentication
        password: Password to use if use_password is True
        
    Returns:
        (success, output_message)
    """
    try:
        # Build the psql command
        if use_password and password:
            # Use PGPASSWORD environment variable
            import os
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            psql_cmd = [
                'psql',
                '-U', 'postgres',
                '-h', 'localhost',
                '-d', 'postgres',
                '-c', command
            ]
            result = subprocess.run(psql_cmd, capture_output=True, text=True, env=env)
        else:
            # Try without password (peer authentication)
            psql_cmd = [
                'psql',
                '-U', 'postgres',
                '-h', 'localhost',
                '-d', 'postgres',
                '-c', command
            ]
            result = subprocess.run(psql_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except FileNotFoundError:
        return False, "psql command not found. Make sure PostgreSQL is installed and in PATH."
    except Exception as e:
        return False, str(e)


def reset_password_via_psql() -> bool:
    """Try to reset password using psql command line."""
    print("\n" + "="*70)
    print("🔧 Method 1: Reset PostgreSQL Password via psql")
    print("="*70)
    
    # First, try without password (peer authentication for local Unix socket)
    print("\nAttempting to connect to PostgreSQL without password...")
    print("(This works if PostgreSQL uses 'trust' or 'peer' authentication)")
    
    sql_command = "ALTER USER postgres WITH PASSWORD 'anil';"
    success, output = run_psql_command(sql_command)
    
    if success:
        print("✅ Password reset successful!")
        print(f"   Output: {output}")
        return True
    else:
        print("⚠️  Could not connect without password")
        print(f"   Error: {output}")
        
        # Try with empty password
        print("\nTrying with empty password...")
        success, output = run_psql_command(sql_command, use_password=True, password="")
        
        if success:
            print("✅ Password reset successful!")
            return True
        else:
            print("❌ Failed to reset password via psql")
            return False


async def verify_password() -> bool:
    """Verify that the new password works."""
    print("\n" + "="*70)
    print("✅ Verifying New Password")
    print("="*70)
    
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='anil',
            database='postgres'
        )
        
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        
        print("✅ Successfully connected with password 'anil'!")
        print(f"\nPostgreSQL Version:")
        print(f"   {version[:50]}...")
        
        return True
    except asyncpg.PostgresError as e:
        print(f"❌ Failed to connect with new password: {str(e)}")
        return False


async def main():
    """Main function."""
    print("\n" + "="*70)
    print("🚀 PostgreSQL Password Reset Tool")
    print("="*70)
    print(f"\nTarget User: postgres")
    print(f"New Password: anil")
    print(f"Host: localhost")
    print(f"Port: 5432")
    
    # Check if psql is available
    print("\n🔍 Checking if psql is installed...")
    success, output = run_psql_command("SELECT version();")
    
    if success:
        print("✅ psql found! Proceeding with password reset...")
        
        # Reset password
        if not reset_password_via_psql():
            print("\n❌ Failed to reset password via psql")
            print("\nAlternative methods:")
            print("1. Use pgAdmin GUI tool")
            print("2. Reinstall PostgreSQL with 'anil' password")
            print("3. Check PostgreSQL documentation for your version")
            sys.exit(1)
        
        # Verify
        if not await verify_password():
            print("\n⚠️  Password may not have been set correctly")
            sys.exit(1)
        
        print("\n" + "="*70)
        print("🎉 PostgreSQL Password Reset Complete!")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: python setup_postgres.py")
        print("2. Then: python setup_db.py")
        print("3. Start the application: uvicorn app.main:app --port 8002")
        print("="*70 + "\n")
        
    else:
        print("❌ psql not found in PATH")
        print("\nInstallation instructions for Windows:")
        print("1. Download PostgreSQL from: https://www.postgresql.org/download/")
        print("2. Run installer with these settings:")
        print("   - Installation Directory: C:\\Program Files\\PostgreSQL\\14")
        print("   - Password: anil (for postgres user)")
        print("   - Port: 5432")
        print("3. Add PostgreSQL bin to PATH:")
        print("   - C:\\Program Files\\PostgreSQL\\14\\bin")
        print("4. Restart terminal and try again")
        print("\nOr manually reset password:")
        print("1. Open pgAdmin (comes with PostgreSQL)")
        print("2. Right-click 'postgres' user under 'Roles'")
        print("3. Select 'Properties'")
        print("4. Go to 'Definition' tab")
        print("5. Set password to: anil")
        print("6. Click 'Save'")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
