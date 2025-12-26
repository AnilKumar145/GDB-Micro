"""
Reset Sequence Script

Resets the account_number_seq sequence to the correct next value.

Usage:
    python reset_sequence.py
"""

import asyncpg
import asyncio
import sys

async def reset_sequence():
    """Reset the sequence to the next available value."""
    
    database_url = "postgresql://postgres:anil@localhost:5432/GDB-GDB"
    
    try:
        conn = await asyncpg.connect(database_url)
        
        print("=" * 60)
        print("SEQUENCE RESET SCRIPT")
        print("=" * 60)
        print()
        
        # Get the maximum account_number
        max_account = await conn.fetchval("""
            SELECT COALESCE(MAX(account_number), 999) 
            FROM accounts
        """)
        
        print(f"Current maximum account_number in database: {max_account}")
        
        # Reset sequence to next value
        next_value = max_account + 1
        await conn.execute(f"""
            ALTER SEQUENCE account_number_seq RESTART WITH {next_value}
        """)
        
        print(f"Sequence reset to start at: {next_value}")
        
        # Verify
        current_seq = await conn.fetchval("""
            SELECT last_value FROM account_number_seq
        """)
        
        print(f"Verified sequence last_value: {current_seq}")
        print()
        
        print("=" * 60)
        print("SEQUENCE RESET COMPLETE")
        print("=" * 60)
        print()
        print("Next account numbers will be:")
        print(f"  - {next_value} (next account)")
        print(f"  - {next_value + 1}")
        print(f"  - {next_value + 2}")
        print(f"  - etc...")
        print()
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(reset_sequence())
    print("Ready to create accounts!")
