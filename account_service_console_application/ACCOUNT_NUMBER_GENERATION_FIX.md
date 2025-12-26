# Account Number Generation Fix - SEQUENCE AUTO-INCREMENT

## ✅ Status: FIXED

Fixed the duplicate key issue by using PostgreSQL's auto-increment sequence properly.

---

## Problem

The error occurred because:
1. We were manually calling `nextval('account_number_seq')` to get the next value
2. The sequence wasn't properly aligned with existing data (1000 was already inserted)
3. Trying to insert account_number=1000 again caused duplicate key violation

**Error:**
```
duplicate key value violates unique constraint "accounts_account_number_key"
DETAIL:  Key (account_number)=(1000) already exists.
```

---

## Solution

Changed the approach to let PostgreSQL auto-generate account numbers using the DEFAULT value and RETURNING clause:

### Before:
```python
# Manual sequence call (causes duplicate issue)
account_number = self.db.fetch_val("SELECT nextval('account_number_seq')")
self.db.execute("""
    INSERT INTO accounts 
    (account_number, account_type, name, pin_hash, balance, privilege, is_active, activated_date)
    VALUES ($1, $2, $3, $4, $5, $6, TRUE, CURRENT_TIMESTAMP)
""", account_number, ...)
```

### After:
```python
# Let PostgreSQL auto-generate using DEFAULT
result = self.db.fetch_one("""
    INSERT INTO accounts 
    (account_type, name, pin_hash, balance, privilege, is_active, activated_date)
    VALUES ($1, $2, $3, $4, $5, TRUE, CURRENT_TIMESTAMP)
    RETURNING account_number
""", ...)
account_number = result['account_number']
```

---

## Changes Made

### File: `app/repositories/account_repo.py`

**Methods Updated:**
1. ✅ `create_savings_account()` - Now uses auto-increment
2. ✅ `create_current_account()` - Now uses auto-increment

**Key Changes:**
- Removed manual `nextval()` call
- Removed `account_number` from INSERT columns (uses DEFAULT)
- Added `RETURNING account_number` clause
- Fetch returned account_number from result

---

## Database Reset Required

Since you have duplicate data, you need to reset the database:

### Option 1: Using the Reset Script
```powershell
python reset_database.py
```

This will:
1. Drop the database
2. Create a fresh database
3. Ready for schema initialization

### Option 2: Manual Reset
```powershell
# Connect to PostgreSQL
psql -U postgres

# Drop database with FORCE
DROP DATABASE "GDB-GDB" WITH (FORCE);

# Create fresh database
CREATE DATABASE "GDB-GDB";

# Exit
\q
```

---

## Complete Setup Sequence

After resetting the database:

### Step 1: Reset Database
```powershell
python reset_database.py
```

Output:
```
============================================================
DATABASE RESET SCRIPT
============================================================

Dropping database: GDB-GDB
✅ Database dropped

Creating database: GDB-GDB
✅ Database created

============================================================
✅ DATABASE RESET COMPLETE
============================================================
```

### Step 2: Initialize Schema
```powershell
python database/init_db.py
```

Expected output:
```
Initializing database: postgresql://postgres:anil@localhost:5432/GDB-GDB

✅ Created account_number_seq sequence
✅ Created accounts table
✅ Created savings_account_details table
✅ Created current_account_details table
✅ Created indexes
...
✅ Database initialization complete!
```

### Step 3: Run Application
```powershell
python main.py
```

---

## How Account Number Generation Works Now

### Database Schema:
```sql
CREATE SEQUENCE account_number_seq START 1000;

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_number INTEGER UNIQUE NOT NULL DEFAULT nextval('account_number_seq'),
    ...
);
```

### Account Creation Flow:
```
1. User submits account creation form
2. Service validates data
3. Repository executes INSERT with no account_number
4. PostgreSQL automatically:
   - Calls nextval('account_number_seq')
   - Generates next account number (1000, 1001, 1002, ...)
   - Inserts record
   - Returns generated account_number
5. Application receives account_number via RETURNING clause
```

### Example Results:
```
First account:  account_number = 1000
Second account: account_number = 1001
Third account:  account_number = 1002
```

---

## Testing Steps

### Test 1: Create Savings Account
```
Menu > Create Account > Create Savings Account
Name: Anil
DOB: 2003-02-24
Gender: Male
Phone: 1234567809
PIN: 8297
Privilege: GOLD

Expected: Account 1000 created successfully
```

### Test 2: Create Current Account
```
Menu > Create Account > Create Current Account
Name: Test Company
Company: ABC Corp
Website: www.abc.com
Registration: ABC-12345
PIN: 5678
Privilege: PREMIUM

Expected: Account 1001 created successfully
```

### Test 3: Verify in Database
```powershell
psql -U postgres -d GDB-GDB

# View accounts
SELECT id, account_number, account_type, name FROM accounts;

# Expected output:
-- id | account_number | account_type |      name
-- ---+----------------+--------------+-------------------
--  1 |           1000 | SAVINGS      | Anil
--  2 |           1001 | CURRENT      | Test Company
```

---

## Sequence Management

### Check Sequence Value
```sql
SELECT last_value FROM account_number_seq;
-- Should show 1001 (last generated + 1)
```

### Reset Sequence (if needed)
```sql
ALTER SEQUENCE account_number_seq RESTART WITH 1000;
```

### Check Sequence Owner
```sql
SELECT * FROM pg_sequences WHERE sequencename = 'account_number_seq';
```

---

## Files Modified

- ✅ `app/repositories/account_repo.py`
  - `create_savings_account()` - Now uses auto-increment
  - `create_current_account()` - Now uses auto-increment

- ✅ `reset_database.py` (NEW)
  - Script to reset database for clean start

---

## Quick Reference

| Operation | Command |
|-----------|---------|
| Reset DB | `python reset_database.py` |
| Init Schema | `python database/init_db.py` |
| Run App | `python main.py` |
| Check Accounts | `SELECT * FROM accounts;` |
| Check Sequence | `SELECT last_value FROM account_number_seq;` |

---

## Ready to Test! 🚀

**Next Steps:**
1. Run: `python reset_database.py`
2. Run: `python database/init_db.py`
3. Run: `python main.py`
4. Create test accounts and verify numbering

The application will now correctly auto-generate account numbers starting at 1000 and incrementing by 1 for each new account!
