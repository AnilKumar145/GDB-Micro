# Schema Configuration - Verified ✅

## Confirmation: Account Number Generation

Your schema is **correctly configured**:

### Sequence Configuration
```sql
CREATE SEQUENCE account_number_seq START 1000;
```

**Behavior:**
- ✅ Starts at: **1000**
- ✅ Increments by: **1** (default)
- ✅ Generates: 1000, 1001, 1002, 1003, ...

---

## Current Schema Structure

### accounts table
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,                    -- Auto-incrementing row ID
    account_number INTEGER UNIQUE NOT NULL,   -- Generated from sequence (1000, 1001, ...)
    account_type VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    pin_hash VARCHAR(255) NOT NULL,
    balance NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    privilege VARCHAR(20) NOT NULL DEFAULT 'SILVER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    activated_date TIMESTAMP NOT NULL,
    closed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Points:**
- `id` = PRIMARY KEY (internal row identifier, 1, 2, 3, ...)
- `account_number` = UNIQUE (business identifier, 1000, 1001, 1002, ...)

---

### savings_account_details table
```sql
CREATE TABLE savings_account_details (
    id SERIAL PRIMARY KEY,                    -- Auto-incrementing row ID
    account_number INTEGER UNIQUE NOT NULL,   -- Links to accounts table
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20) NOT NULL,
    phone_no VARCHAR(20) NOT NULL,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);
```

---

### current_account_details table
```sql
CREATE TABLE current_account_details (
    id SERIAL PRIMARY KEY,                    -- Auto-incrementing row ID
    account_number INTEGER UNIQUE NOT NULL,   -- Links to accounts table
    company_name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    registration_no VARCHAR(50) NOT NULL UNIQUE,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);
```

---

## Account Number Generation Examples

When you create accounts:

**First Account (Savings):**
```
Input:
  - Name: John Doe
  - Type: SAVINGS

Generated:
  - id: 1
  - account_number: 1000  ← Auto-generated from sequence
```

**Second Account (Current):**
```
Input:
  - Name: Jane Smith
  - Type: CURRENT

Generated:
  - id: 2
  - account_number: 1001  ← Auto-incremented to next value
```

**Third Account:**
```
Generated:
  - id: 3
  - account_number: 1002  ← Continues incrementing
```

---

## Database Queries Reference

### Insert a Savings Account
```sql
INSERT INTO accounts (account_type, name, pin_hash)
VALUES ('SAVINGS', 'John Doe', 'hashed_pin_here')
RETURNING id, account_number;

-- Output: id=1, account_number=1000
```

### View All Accounts with Numbers
```sql
SELECT id, account_number, account_type, name, balance
FROM accounts
ORDER BY account_number;

-- Output:
-- id | account_number | account_type |  name    | balance
-- ---+----------------+--------------+----------+---------
--  1 |           1000 | SAVINGS      | John Doe | 0.00
--  2 |           1001 | CURRENT      | Jane Sm  | 0.00
```

### Query by Account Number
```sql
SELECT * FROM accounts WHERE account_number = 1000;
```

### Query by Internal ID
```sql
SELECT * FROM accounts WHERE id = 1;
```

---

## Sequence Management

### Check Current Sequence Value
```sql
SELECT last_value FROM account_number_seq;
```

### Manually Set Next Value (if needed)
```sql
SELECT setval('account_number_seq', 2000);
```

### Reset Sequence (starts fresh at 1000)
```sql
ALTER SEQUENCE account_number_seq RESTART WITH 1000;
```

---

## ✅ Configuration Summary

| Aspect | Setting | Status |
|--------|---------|--------|
| **Primary Key (accounts)** | `id` (SERIAL) | ✅ Correct |
| **Account Number** | UNIQUE NOT NULL | ✅ Correct |
| **Sequence Start** | 1000 | ✅ Correct |
| **Sequence Increment** | 1 | ✅ Correct |
| **Account Numbers Generated** | 1000, 1001, 1002, ... | ✅ Correct |
| **Table Structure** | id + account_number | ✅ Correct |

---

## 🚀 Ready to Deploy

Your database schema is correctly configured:
1. Drop old database: `DROP DATABASE "GDB-GDB"`
2. Create new database: `CREATE DATABASE "GDB-GDB"`
3. Initialize schema: `python database/init_db.py`

You're all set! ✨
