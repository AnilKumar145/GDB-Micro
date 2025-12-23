# 🏦 Transaction Service - Database Initialization Guide

## Overview

This guide explains how to initialize the Transaction Service database with all necessary tables, indexes, and default data.

---

## 📋 Tables to be Created

### 1. **transactions** table
Stores all withdrawal, deposit, and transfer operations.

**Columns:**
- `transaction_id` (BIGSERIAL) - Primary key
- `from_account` (BIGINT) - Source account
- `to_account` (BIGINT) - Destination account
- `amount` (NUMERIC) - Transaction amount
- `transaction_type` (VARCHAR) - WITHDRAW, DEPOSIT, or TRANSFER
- `transfer_mode` (VARCHAR) - NEFT, RTGS, IMPS, UPI, CHEQUE, INTERNAL
- `status` (VARCHAR) - PENDING, SUCCESS, FAILED, or REVERSED
- `idempotency_key` (VARCHAR) - Unique transaction identifier
- `transaction_date` (TIMESTAMP) - When transaction occurred
- `description` (TEXT) - Transaction description
- `error_message` (TEXT) - Error details if failed
- `created_at` (TIMESTAMP) - Record creation time
- `updated_at` (TIMESTAMP) - Record update time

### 2. **daily_transfer_limits** table
Tracks daily transfer amounts and counts per account.

**Columns:**
- `limit_id` (BIGSERIAL) - Primary key
- `account_number` (BIGINT) - Account number
- `transfer_date` (DATE) - Date of transfers
- `total_amount` (NUMERIC) - Total transferred today
- `transaction_count` (INT) - Number of transfers today
- `created_at` (TIMESTAMP) - Record creation time
- `updated_at` (TIMESTAMP) - Record update time

### 3. **transaction_logs** table
Complete audit trail for all transactions.

**Columns:**
- `log_id` (BIGSERIAL) - Primary key
- `transaction_id` (BIGINT) - Foreign key to transactions
- `from_account` (BIGINT) - Source account
- `to_account` (BIGINT) - Destination account
- `amount` (NUMERIC) - Transaction amount
- `transaction_type` (VARCHAR) - Type of transaction
- `status` (VARCHAR) - Final status
- `log_message` (TEXT) - Log message
- `log_file_path` (TEXT) - Path to file log
- `log_date` (TIMESTAMP) - Log timestamp
- `created_at` (TIMESTAMP) - Record creation time

### 4. **transfer_rules** table
Privilege-based transfer limits.

**Columns:**
- `rule_id` (BIGSERIAL) - Primary key
- `privilege` (VARCHAR) - PREMIUM, GOLD, or SILVER
- `daily_limit` (NUMERIC) - Daily transfer limit amount
- `daily_transaction_count` (INT) - Daily transaction count limit
- `description` (TEXT) - Rule description
- `created_at` (TIMESTAMP) - Record creation time
- `updated_at` (TIMESTAMP) - Record update time

---

## 🚀 Two Ways to Initialize

### Method 1: Using Python Script (Recommended)

**Step 1: Ensure dependencies are installed**
```bash
pip install asyncpg python-dotenv
```

**Step 2: Configure environment**
Make sure `.env` file has:
```env
DATABASE_URL=postgresql://gdb_user:gdb_password@localhost:5432/gdb_transactions_db
```

**Step 3: Run the initialization script**
```bash
python init_database.py
```

**Output:**
```
✅ DATABASE INITIALIZATION COMPLETE
=====================================================================

Tables created:
  1. transactions - Main transaction records
  2. daily_transfer_limits - Daily transfer tracking
  3. transaction_logs - Audit trail
  4. transfer_rules - Privilege-based limits

Default transfer rules inserted:
  • PREMIUM: ₹100,000 daily limit, 50 transactions/day
  • GOLD: ₹50,000 daily limit, 30 transactions/day
  • SILVER: ₹25,000 daily limit, 20 transactions/day
```

**To reset database (careful!):**
```bash
python init_database.py reset
```

---

### Method 2: Using SQL Script (Manual)

**Step 1: Connect to PostgreSQL**
```bash
psql -U gdb_user -d gdb_transactions_db
```

**Step 2: Run the SQL script**
```sql
\i transactions_init.sql
```

Or execute directly:
```bash
psql -U gdb_user -d gdb_transactions_db -f transactions_init.sql
```

---

## 📊 Default Transfer Rules

The following default rules are automatically inserted:

| Privilege | Daily Limit | Daily Tx Count | Description |
|-----------|------------|-----------------|------------|
| PREMIUM   | ₹100,000   | 50             | Premium privilege - highest limits |
| GOLD      | ₹50,000    | 30             | Gold privilege - medium limits |
| SILVER    | ₹25,000    | 20             | Silver privilege - basic limits |

---

## 🔍 Verify Database Setup

### Using Python
```python
import asyncpg
import asyncio

async def verify():
    conn = await asyncpg.connect("postgresql://gdb_user:gdb_password@localhost:5432/gdb_transactions_db")
    
    # Check tables
    tables = await conn.fetch("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    print("Tables:", [t['table_name'] for t in tables])
    
    # Check rules
    rules = await conn.fetch("SELECT * FROM transfer_rules")
    for rule in rules:
        print(f"  {rule['privilege']}: {rule['daily_limit']} limit, {rule['daily_transaction_count']} tx/day")
    
    await conn.close()

asyncio.run(verify())
```

### Using SQL
```sql
-- List all tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Check transfer rules
SELECT privilege, daily_limit, daily_transaction_count FROM transfer_rules;

-- Check indexes
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';

-- Count records in each table
SELECT 'transactions' as table_name, COUNT(*) as record_count FROM transactions
UNION ALL
SELECT 'daily_transfer_limits', COUNT(*) FROM daily_transfer_limits
UNION ALL
SELECT 'transaction_logs', COUNT(*) FROM transaction_logs
UNION ALL
SELECT 'transfer_rules', COUNT(*) FROM transfer_rules;
```

---

## 📝 Database Indexes

The following indexes are created for performance:

**transactions table:**
- `idx_transactions_from_account` - Lookup by source account
- `idx_transactions_to_account` - Lookup by destination account
- `idx_transactions_transaction_date` - Sort by date (DESC)
- `idx_transactions_status` - Filter by status
- `idx_transactions_idempotency_key` - Unique constraint

**daily_transfer_limits table:**
- `idx_daily_limits_account_date` - Composite index for account + date lookup

**transaction_logs table:**
- `idx_logs_transaction_id` - Lookup logs by transaction
- `idx_logs_log_date` - Sort by date (DESC)
- `idx_logs_account` - Composite index for account lookups

---

## 🛡️ Constraints

All tables have the following constraints:

**transactions table:**
- Amount must be > 0
- transaction_type must be WITHDRAW, DEPOSIT, or TRANSFER
- transfer_mode must be NEFT, RTGS, IMPS, UPI, CHEQUE, or INTERNAL
- status must be PENDING, SUCCESS, FAILED, or REVERSED
- idempotency_key must be unique (prevents duplicate transactions)

**transfer_rules table:**
- privilege must be PREMIUM, GOLD, or SILVER (unique)
- daily_limit must be > 0
- daily_transaction_count must be > 0

**daily_transfer_limits table:**
- Composite unique constraint on (account_number, transfer_date)

---

## 🔄 Database Lifecycle

### Startup (Application)
The application automatically initializes the database on startup:
```python
@app.on_event("startup")
async def startup_event():
    await init_db()
    print("✅ Database initialized")
```

### Manual Reset
```bash
python init_database.py reset
```

This will:
1. Drop all tables (including data)
2. Recreate all tables
3. Re-insert default rules
4. Verify tables are created

---

## ⚠️ Important Notes

1. **One-time Setup**: Run initialization script only once
2. **Idempotent**: Script uses `IF NOT EXISTS` and `ON CONFLICT` - safe to run multiple times
3. **Cascade Delete**: Deleting a transaction automatically deletes its logs
4. **Timestamps**: All tables have `created_at` and `updated_at` timestamps
5. **Indexes**: All indexes are created for optimal query performance

---

## 🐛 Troubleshooting

### Connection refused
```
Error: could not connect to server: Connection refused
```
**Solution:** Make sure PostgreSQL is running and credentials are correct in `.env`

### Database does not exist
```
Error: database "gdb_transactions_db" does not exist
```
**Solution:** Create the database first:
```sql
CREATE DATABASE gdb_transactions_db OWNER gdb_user;
```

### Permission denied
```
Error: permission denied for schema public
```
**Solution:** Grant permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE gdb_transactions_db TO gdb_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO gdb_user;
```

### Table already exists
If you see "Table already exists" warning, it's normal - the script handles existing tables.

---

## 📚 Sample Queries

### Insert a transaction
```sql
INSERT INTO transactions (from_account, to_account, amount, transaction_type, status)
VALUES (1001, 1002, 5000.00, 'TRANSFER', 'SUCCESS');
```

### Query transfer history
```sql
SELECT * FROM transactions 
WHERE from_account = 1001 
ORDER BY transaction_date DESC 
LIMIT 20;
```

### Check daily limit usage
```sql
SELECT * FROM daily_transfer_limits 
WHERE account_number = 1001 
AND transfer_date = CURRENT_DATE;
```

### View transaction logs
```sql
SELECT * FROM transaction_logs 
WHERE transaction_id = 1 
ORDER BY log_date DESC;
```

---

## ✅ Checklist

- [ ] PostgreSQL is running
- [ ] Database `gdb_transactions_db` exists
- [ ] User `gdb_user` has permissions
- [ ] `.env` file has correct DATABASE_URL
- [ ] Run `python init_database.py` successfully
- [ ] Verify all 4 tables are created
- [ ] Verify 3 default transfer rules are inserted
- [ ] Application starts without database errors

---

**Last Updated:** December 22, 2025  
**Status:** ✅ Ready for use
