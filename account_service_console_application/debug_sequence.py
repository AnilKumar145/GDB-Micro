"""
Debug script to check sequence and database state
"""

import asyncpg
import asyncio
import os

async def debug():
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "anil")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "GDB-GDB")
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    conn = await asyncpg.connect(database_url)
    
    print("=" * 70)
    print("DEBUG: SEQUENCE AND DATABASE STATE")
    print("=" * 70)
    print()
    
    # Check sequence last_value
    print("1. Current sequence state:")
    last_val = await conn.fetchval("SELECT last_value FROM account_number_seq")
    print(f"   last_value: {last_val}")
    print()
    
    # Check max account number
    print("2. Accounts in database:")
    accounts = await conn.fetch("SELECT id, account_number, name FROM accounts ORDER BY account_number")
    for acc in accounts:
        print(f"   ID: {acc['id']}, Account#: {acc['account_number']}, Name: {acc['name']}")
    print()
    
    # Try nextval 5 times to see what happens
    print("3. Testing nextval() calls:")
    for i in range(5):
        next_num = await conn.fetchval("SELECT nextval('account_number_seq')")
        print(f"   Call {i+1}: {next_num}")
    print()
    
    # Check sequence again
    print("4. Sequence after nextval() calls:")
    last_val_after = await conn.fetchval("SELECT last_value FROM account_number_seq")
    print(f"   last_value: {last_val_after}")
    print()
    
    # RESET IT BACK
    print("5. Resetting sequence back to 1001:")
    await conn.execute("ALTER SEQUENCE account_number_seq RESTART WITH 1001")
    print("   Done")
    print()
    
    # Verify
    print("6. Verify reset:")
    last_val_reset = await conn.fetchval("SELECT last_value FROM account_number_seq")
    next_after_reset = await conn.fetchval("SELECT nextval('account_number_seq')")
    print(f"   last_value: {last_val_reset}")
    print(f"   nextval(): {next_after_reset}")
    
    await conn.close()

asyncio.run(debug())
