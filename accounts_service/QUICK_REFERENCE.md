# Database Operations Quick Reference

## First-Time Setup (New Database)

```bash
# 1. Navigate to accounts service
cd accounts_service

# 2. Run setup script
python setup_db.py

# 3. Logs will be written to logs/accounts_service.log
# 4. Check console for success message
```

**Expected Output:**
- ✅ Database 'gdb_accounts_db' created
- ✅ All tables created successfully!
- ✅ Database setup completed successfully!

---

## Fresh Start (Reset Everything)

```bash
# 1. Navigate to accounts service
cd accounts_service

# 2. Run reset script
python reset_db.py

# 3. Confirm with "YES" when prompted
# 4. Wait for completion
```

**Expected Output:**
- ✅ Database dropped
- ✅ Database created
- ✅ All tables created successfully!
- ✅ Database reset completed successfully!

---

## Start the Server

```bash
# After successful setup/reset
python -m uvicorn app.main:app --reload --port 8001
```

**Server Ready:**
- Console: `Uvicorn running on http://127.0.0.1:8001`
- API Docs: http://localhost:8001/api/v1/docs

---

## Monitor Logs

### Windows PowerShell
```powershell
# Real-time logs
Get-Content logs/accounts_service.log -Wait

# Search for errors
Select-String "ERROR" logs/accounts_service.log

# Last 20 lines
Get-Content logs/accounts_service.log -Tail 20
```

### Linux/Mac
```bash
# Real-time logs
tail -f logs/accounts_service.log

# Search for errors
grep "ERROR" logs/accounts_service.log

# Last 20 lines
tail -20 logs/accounts_service.log
```

---

## Test Account Creation

### Using cURL
```bash
curl -X POST http://localhost:8001/api/v1/accounts/savings \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1990-01-15",
    "phone_number": "9876543210",
    "email": "john@example.com",
    "gender": "Male",
    "address": "123 Main St",
    "pin": "9640",
    "initial_balance": 5000.00
  }'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8001/api/v1/accounts/savings",
    json={
        "name": "John Doe",
        "date_of_birth": "1990-01-15",
        "phone_number": "9876543210",
        "email": "john@example.com",
        "gender": "Male",
        "address": "123 Main St",
        "pin": "9640",
        "initial_balance": 5000.00
    }
)

print(response.json())
# Output: {"account_number": 1000, ...}
```

---

## Verify Everything

### Check Logs for Account Creation
```bash
# Windows
Select-String "account created" logs/accounts_service.log

# Linux/Mac
grep "account created" logs/accounts_service.log
```

### Expected Log Output
```
2025-12-24 13:30:45,250 - app.repositories.account_repo - INFO - ✅ Savings account created: 1000
2025-12-24 13:30:45,251 - app.services.account_service - INFO - ✅ Savings account service created: 1000
```

---

## Troubleshooting

### "Database not initialized"
- ✅ Fixed - Run `python setup_db.py` first

### "PostgreSQL connection refused"
- Check if PostgreSQL is running
- Verify DATABASE_URL in .env file
- Check username/password: `postgresql://postgres:anil@localhost:5432/gdb_accounts_db`

### "Schema file not found"
- Verify file exists: `database_schemas/accounts_schema.sql`
- Check file path is correct

### "Database being accessed by other users"
- Stop the FastAPI server
- Close any psql or pgAdmin connections
- Try reset_db.py again

### "Permission denied for logs directory"
```bash
# Windows
mkdir logs
icacls logs /grant %username%:F

# Linux/Mac
mkdir -p logs
chmod 755 logs
```

---

## What Gets Logged

### INFO Level (Console & File)
- ✅ Database connections
- ✅ Database created/dropped
- ✅ Schema execution
- ✅ Tables created
- ✅ Account creation
- ✅ Successful operations

### DEBUG Level (File Only)
- Database query details
- Internal operations
- Detailed state changes

### ERROR Level (Console & File)
- ❌ Connection failures
- ❌ Schema errors
- ❌ Missing files
- ❌ Validation errors

### WARNING Level (Console & File)
- ⚠️ Database drop warnings
- ⚠️ Connection issues
- ⚠️ Retry attempts

---

## File Structure

```
accounts_service/
├── setup_db.py                    ← Run for first-time setup
├── reset_db.py                    ← Run for complete reset
├── logs/                           ← Stores application logs
│   ├── accounts_service.log        ← Current log file
│   ├── accounts_service.log.1      ← Previous logs (auto-rotated)
│   └── accounts_service.log.5      ← Oldest backup
├── app/
│   ├── main.py                     ← FastAPI entry point
│   ├── config/
│   │   ├── logging.py              ← Logging configuration
│   │   └── settings.py             ← Database settings
│   └── ...
└── database_schemas/
    └── accounts_schema.sql         ← Database schema
```

---

## Log Rotation

- **Max File Size**: 10 MB
- **Backup Count**: 5 previous logs
- **Automatic**: Triggered when file reaches 10 MB
- **Total Capacity**: ~60 MB

When rotation occurs:
```
accounts_service.log   → accounts_service.log.1
accounts_service.log.1 → accounts_service.log.2
accounts_service.log.2 → accounts_service.log.3
accounts_service.log.3 → accounts_service.log.4
accounts_service.log.4 → accounts_service.log.5
accounts_service.log.5 → DELETED
New accounts_service.log created
```

---

**Last Updated**: December 24, 2025
**Version**: 1.0.0
