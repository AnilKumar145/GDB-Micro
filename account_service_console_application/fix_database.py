"""
Database Fix Script - Reset Sequence and Verify

This script:
1. Connects to PostgreSQL
2. Checks current accounts
3. Resets the sequence to proper value
4. Verifies everything is working

Usage:
    python fix_database.py
"""

import asyncpg
import asyncio
import sys
import os

async def fix_database():
    """Fix the database sequence."""
    
    # Get credentials from environment or use defaults
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "anil")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "GDB-GDB")
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        print("=" * 70)
        print("DATABASE FIX SCRIPT - SEQUENCE RESET")
        print("=" * 70)
        print()
        
        conn = await asyncpg.connect(database_url)
        print(f"Connected to: {db_name}")
        print()
        
        # Step 1: Show current accounts
        print("Step 1: Current accounts in database")
        print("-" * 70)
        accounts = await conn.fetch("""
            SELECT id, account_number, account_type, name 
            FROM accounts 
            ORDER BY account_number
        """)
        
        if accounts:
            for acc in accounts:
                print(f"  ID: {acc['id']}, Account #: {acc['account_number']}, Type: {acc['account_type']}, Name: {acc['name']}")
        else:
            print("  No accounts found")
        
        print()
        
        # Step 2: Check current sequence value
        print("Step 2: Check sequence status")
        print("-" * 70)
        seq_last_value = await conn.fetchval("""
            SELECT last_value FROM account_number_seq
        """)
        
        if seq_last_value:
            print(f"  Sequence last_value: {seq_last_value}")
        
        print()
        
        # Step 3: Get max account number
        print("Step 3: Calculate next sequence value")
        print("-" * 70)
        max_account = await conn.fetchval("""
            SELECT COALESCE(MAX(account_number), 999) 
            FROM accounts
        """)
        
        next_value = max_account + 1
        print(f"  Max account_number: {max_account}")
        print(f"  Next value should be: {next_value}")
        print()
        
        # Step 4: Reset sequence
        print("Step 4: Resetting sequence")
        print("-" * 70)
        
        # Method 1: Using setval with is_called=true
        result = await conn.fetchval(f"""
            SELECT setval('account_number_seq', {max_account}, true)
        """)
        print(f"  setval result: {result}")
        print()
        
        # Step 5: Verify reset
        print("Step 5: Verify sequence reset")
        print("-" * 70)
        next_seq = await conn.fetchval("""
            SELECT nextval('account_number_seq')
        """)
        print(f"  Next sequence value: {next_seq}")
        
        if next_seq == next_value:
            print(f"  SUCCESS: Sequence will generate {next_value} for next account!")
        else:
            print(f"  WARNING: Expected {next_value}, got {next_seq}")
        
        print()
        
        # Step 6: Reset sequence back to generate next_value
        print("Step 6: Final sequence setup")
        print("-" * 70)
        await conn.execute(f"""
            ALTER SEQUENCE account_number_seq RESTART WITH {next_value}
        """)
        print(f"  Sequence restarted with: {next_value}")
        
        # Verify final state
        final_next = await conn.fetchval("""
            SELECT nextval('account_number_seq')
        """)
        print(f"  Final next value: {final_next}")
        
        if final_next == next_value:
            print()
            print("=" * 70)
            print("SUCCESS: Database is fixed!")
            print("=" * 70)
            print()
            print(f"Next 5 account numbers will be:")
            print(f"  {final_next}, {final_next+1}, {final_next+2}, {final_next+3}, {final_next+4}")
            print()
            return True
        else:
            print()
            print("WARNING: Sequence may not be properly configured")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    success = asyncio.run(fix_database())
    sys.exit(0 if success else 1)
