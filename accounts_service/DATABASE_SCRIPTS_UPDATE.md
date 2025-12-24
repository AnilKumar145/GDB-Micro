# Database Scripts Update

## Overview

Updated `setup_db.py` and `reset_db.py` to integrate with the new file-based logging infrastructure. Both scripts now log all operations to `logs/accounts_service.log` while maintaining console output for real-time feedback.

## Changes Summary

### Files Updated
- ✅ `setup_db.py` - Added logging integration
- ✅ `reset_db.py` - Added logging integration

### What Was Added

#### Imports
```python
import logging
from app.config.logging import setup_logging

# Setup logging
logger = setup_logging()
```

#### Logging Throughout Scripts

**Connection & Database Creation:**
```python
logger.info(f"Connecting to PostgreSQL at {host}:{port}...")
logger.info(f"✅ Connected to PostgreSQL")
logger.info(f"Creating database '{database}'...")
logger.info(f"✅ Database '{database}' created")
```

**Schema Execution:**
```python
logger.info(f"Reading schema from {schema_file.name}...")
logger.info("Creating tables and objects...")
logger.info("✅ Schema executed successfully")
```

**Table Verification:**
```python
logger.info(f"Created {len(tables)} tables:")
for table in tables:
    logger.info(f"   ✓ {table['table_name']}")
```

**Error Handling:**
```python
logger.error(f"Database error: {e}")
logger.error(f"Schema file not found: {schema_file}")
```

**Reset-Specific:**
```python
logger.warning("=" * 60)
logger.warning("🏦 GDB Accounts Service - Database Reset")
logger.warning("⚠️  WARNING: This will DROP all existing data!")
logger.warning("=" * 60)
logger.info("Reset confirmed by user - proceeding...")
logger.info("Reset cancelled by user")
```

## Benefits

### ✅ Persistent Record
- All database operations are now logged to `logs/accounts_service.log`
- Useful for debugging and auditing database setup/reset operations
- Automatically rotates when file reaches 10MB

### ✅ Consistent Logging
- Uses same logging infrastructure as the FastAPI application
- All logs formatted consistently with timestamps and log levels
- Easy to correlate database setup logs with application logs

### ✅ Error Tracking
- Exceptions are logged with full context
- Helps diagnose database connectivity issues
- Enables troubleshooting of schema execution failures

### ✅ User Feedback
- Console output remains for immediate feedback
- Detailed logs available in files for later review
- Both console and file handlers work together

## Usage

### Setup Database (First Time)
```bash
# Create fresh database and tables
python setup_db.py
```

**Console Output:**
```
============================================================
🏦 GDB Accounts Service - Database Setup
============================================================

📡 Connecting to PostgreSQL at localhost:5432...
✅ Connected to PostgreSQL
📦 Creating database 'gdb_accounts_db'...
✅ Database 'gdb_accounts_db' created

📡 Connecting to gdb_accounts_db...
✅ Connected to gdb_accounts_db

📋 Reading schema from accounts_schema.sql...
🔨 Creating tables and objects...
✅ All tables created successfully!

📊 Created tables (7):
   ✓ accounts
   ✓ current_account_details
   ✓ savings_account_details
   ✓ account_number_seq

✅ Database setup completed successfully!

📝 Next steps:
   1. Start the server: python -m uvicorn app.main:app --reload --port 8001
   2. Access API docs: http://localhost:8001/api/v1/docs
```

**Log File Entry:**
```
2025-12-24 13:15:50,046 - root - INFO - 🔧 Starting database setup...
2025-12-24 13:15:50,156 - root - INFO - Connecting to PostgreSQL at localhost:5432...
2025-12-24 13:15:50,258 - root - INFO - ✅ Connected to PostgreSQL
...
```

### Reset Database (Complete Fresh Start)
```bash
# Drop existing database and recreate from scratch
python reset_db.py

# You will be prompted:
# ============================================================
# 🏦 GDB Accounts Service - Database Reset
# ============================================================
# 
# ⚠️  WARNING: This will DROP all existing data!
# ============================================================
# 
# Type 'YES' to proceed with database reset: YES
```

**Console Output:**
```
============================================================
🏦 GDB Accounts Service - Database Reset
============================================================

⚠️  WARNING: This will DROP all existing data!
============================================================

Type 'YES' to proceed with database reset: YES

📡 Connecting to PostgreSQL at localhost:5432...
✅ Connected to PostgreSQL
🗑️  Dropping existing database 'gdb_accounts_db'...
✅ Database 'gdb_accounts_db' dropped

📡 Reconnecting to PostgreSQL...
📦 Creating database 'gdb_accounts_db'...
✅ Database 'gdb_accounts_db' created

📡 Connecting to gdb_accounts_db...
✅ Connected to gdb_accounts_db

📋 Reading schema from accounts_schema.sql...
🔨 Creating tables and objects...
✅ All tables created successfully!

🔍 Verifying sequence...
✅ Sequence 'account_number_seq' created
   Last value: 999
   Next value will be: 1000

📊 Created tables (7):
   ✓ accounts
   ✓ current_account_details
   ✓ savings_account_details
   ✓ account_number_seq

✅ Database reset completed successfully!

📝 Next steps:
   1. Start the server: python -m uvicorn app.main:app --reload --port 8001
   2. Create a new account - it will have account_number 1000
   3. Each new account will increment: 1001, 1002, 1003...
```

## Log File Locations

- **Primary Log**: `logs/accounts_service.log` (10MB per file)
- **Rotation**: Automatic at 10MB with 5 backups
- **Format**: `TIMESTAMP - LOGGER_NAME - LEVEL - MESSAGE`

### View Logs

**Windows (PowerShell):**
```powershell
# Real-time logs
Get-Content logs/accounts_service.log -Wait

# Last 50 lines
Get-Content logs/accounts_service.log | Select-Object -Last 50

# Search for errors
Select-String "ERROR" logs/accounts_service.log
```

**Linux/Mac:**
```bash
# Real-time logs
tail -f logs/accounts_service.log

# Last 50 lines
tail -50 logs/accounts_service.log

# Search for errors
grep "ERROR" logs/accounts_service.log
```

## Error Scenarios

### Connection Failed
```
❌ Database error: could not connect to server: Connection refused
```

**Logged as:**
```
2025-12-24 13:15:50,258 - root - ERROR - Database error: could not connect to server: Connection refused
```

**Fix:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env file
- Check username/password credentials

### Schema File Not Found
```
❌ Schema file not found: .../database_schemas/accounts_schema.sql
```

**Logged as:**
```
2025-12-24 13:15:50,259 - root - ERROR - Schema file not found: .../database_schemas/accounts_schema.sql
```

**Fix:**
- Verify accounts_schema.sql exists in database_schemas/ directory
- Check file path is correct

### Drop Database Failed
```
⚠️  Warning: Could not drop database: ERROR: database "gdb_accounts_db" is being accessed by other users
```

**Logged as:**
```
2025-12-24 13:15:50,360 - root - WARNING - Could not drop database: ERROR: database "gdb_accounts_db" is being accessed by other users
```

**Fix:**
- Close any connections to the database (stop the app server)
- Close any psql/pgAdmin connections
- Try reset_db.py again

## Next Steps

1. **Run Database Setup/Reset:**
   ```bash
   python reset_db.py
   ```

2. **Start the Server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8001
   ```

3. **Monitor Logs:**
   ```bash
   Get-Content logs/accounts_service.log -Wait  # Windows
   tail -f logs/accounts_service.log              # Linux/Mac
   ```

4. **Create Test Accounts:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/accounts/savings \
     -H "Content-Type: application/json" \
     -d '{...}'
   ```

---

**Status**: ✅ Setup & Reset Scripts Updated with Logging
**Date**: December 24, 2025
**Version**: 1.0.0
