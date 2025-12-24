# 📝 Logging Strategy - Accounts Service

## Overview

The Accounts Service uses **file-based logging** to track all operations. Logs are stored in the `logs/` directory with automatic rotation to prevent disk space issues.

## Logging Configuration

### Log Levels

| Level | Purpose | Example |
|-------|---------|---------|
| **DEBUG** | Detailed diagnostic information | Database queries, internal operations |
| **INFO** | General informational messages | Account created, database connected |
| **WARNING** | Warning messages | Retry attempts, inactive accounts |
| **ERROR** | Error messages | Failed operations, exceptions |
| **CRITICAL** | Critical errors | System failures |

### Log Destinations

```
Console Output (INFO level and above)
    ↓
    └─→ Shows in terminal during development/production

File Output (DEBUG level and above)
    ↓
    └─→ logs/accounts_service.log (rotates at 10MB)
    └─→ logs/accounts_service.log.1
    └─→ logs/accounts_service.log.2
    └─→ logs/accounts_service.log.3
    └─→ logs/accounts_service.log.4
    └─→ logs/accounts_service.log.5 (oldest)
```

## Log File Configuration

### Location
```
accounts_service/
└── logs/
    ├── accounts_service.log      (Current log file)
    ├── accounts_service.log.1    (Backup 1)
    ├── accounts_service.log.2    (Backup 2)
    ├── accounts_service.log.3    (Backup 3)
    ├── accounts_service.log.4    (Backup 4)
    └── accounts_service.log.5    (Backup 5 - oldest)
```

### Rotation Policy
- **Max File Size**: 10 MB per log file
- **Backup Count**: 5 previous logs retained
- **Total Capacity**: ~60 MB maximum
- **Encoding**: UTF-8

### File Format
```
2025-12-24 13:15:50,046 - app.main - INFO - 🚀 Starting Accounts Service...
2025-12-24 13:15:50,558 - app.database.db - INFO - ✅ Database connection pool established
2025-12-24 13:15:53,590 - app.repositories.account_repo - INFO - ✅ Savings account created: 1000
```

## Logging Events

### Account Creation
```
✅ Savings account created: 1000
✅ Current account created: 1001
✅ Savings account service created: 1000
```

### Database Operations
```
✅ Database initialized
✅ Database connection pool established
✅ Database connection pool closed
```

### Transaction Operations
```
✅ Debit successful: 1000, Amount: ₹500.00
✅ Credit successful: 1001, Amount: ₹500.00
⚠️ Debit already processed: <idempotency-key>
⚠️ Credit already processed: <idempotency-key>
❌ Account not found: 9999
❌ Insufficient funds. Balance: ₹100, Required: ₹500
```

### Errors
```
❌ Database connection failed: <error>
❌ Account creation failed: INVALID_PIN
❌ Get account details failed: ACCOUNT_NOT_FOUND
❌ Error creating savings account: <error>
```

## Log Levels by Module

| Module | Level | Purpose |
|--------|-------|---------|
| `app.main` | INFO | Application startup/shutdown |
| `app.api.*` | ERROR | API endpoint errors |
| `app.services.*` | INFO | Service operations |
| `app.repositories.*` | INFO | Database operations |
| `app.database.db` | INFO | Connection pool events |
| `app.exceptions.*` | ERROR | Custom exceptions |

## Code Examples

### Using Logger in Code

```python
import logging

logger = logging.getLogger(__name__)

# INFO level
logger.info(f"✅ Account created: {account_number}")

# WARNING level
logger.warning(f"⚠️ Retry attempt for transaction: {idempotency_key}")

# ERROR level
logger.error(f"❌ Account creation failed: {error_code}")

# DEBUG level
logger.debug(f"📊 Account balance updated: {account_number} -> ₹{new_balance}")
```

### Using Helper for Sensitive Data

```python
from app.utils.helpers import mask_account_number, mask_phone_number, mask_pin

# Log without exposing sensitive data
logger.info(f"Account {mask_account_number(1000)} created")  # "XXX1000"
logger.info(f"Phone {mask_phone_number('9876543210')} verified")  # "XXXXXX3210"
logger.info(f"PIN {mask_pin('9640')} verified")  # "XXXX"
```

## Viewing Logs

### Real-time Logs (Linux/Mac)
```bash
tail -f logs/accounts_service.log
```

### Real-time Logs (Windows)
```powershell
Get-Content logs/accounts_service.log -Wait
```

### Search Logs
```bash
# Find all errors
grep "ERROR" logs/accounts_service.log

# Find account creation logs
grep "account created" logs/accounts_service.log

# Find specific account
grep "account_number: 1000" logs/accounts_service.log

# Count errors by date
grep "2025-12-24" logs/accounts_service.log | grep "ERROR" | wc -l
```

### View Recent Logs
```bash
# Last 50 lines
tail -50 logs/accounts_service.log

# Last 100 lines with timestamps
tail -100 logs/accounts_service.log | grep "✅\|❌\|⚠️"
```

## Log Rotation Example

When `accounts_service.log` reaches 10 MB:
1. `accounts_service.log` → `accounts_service.log.1`
2. `accounts_service.log.1` → `accounts_service.log.2`
3. `accounts_service.log.2` → `accounts_service.log.3`
4. `accounts_service.log.3` → `accounts_service.log.4`
5. `accounts_service.log.4` → `accounts_service.log.5` (deleted after 5th rotation)
6. New `accounts_service.log` created

## Environment Variables

Configure logging in `.env`:

```env
# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log file path
LOG_FILE=logs/accounts_service.log

# Debug mode
DEBUG=False

# Environment
ENVIRONMENT=development  # or production
```

## Best Practices

✅ **DO:**
- Use appropriate log levels (INFO for normal, ERROR for failures)
- Include relevant context (account numbers, amounts, user actions)
- Use emojis for quick visual scanning (✅ ❌ ⚠️ 📊)
- Mask sensitive data (PINs, passwords, full phone numbers)
- Log at function boundaries (entry/exit for critical operations)

❌ **DON'T:**
- Log sensitive data like full PINs or passwords
- Log at DEBUG level for production (use INFO instead)
- Include large data structures in logs
- Log within tight loops
- Use print() instead of logger

## Troubleshooting

### Logs Not Appearing
1. Check `LOG_LEVEL` in `.env` is set to `DEBUG` or `INFO`
2. Verify `logs/` directory exists and is writable
3. Check file permissions: `chmod 755 logs/`
4. Check disk space: `df -h`

### Log File Growing Too Large
- Logs are automatically rotated at 10 MB
- Old logs are kept for up to 5 rotations (~60 MB total)
- Older logs are automatically deleted

### Cannot Write to Log File
```bash
# Fix permissions
chmod 666 logs/accounts_service.log

# Or create directory if missing
mkdir -p logs
chmod 755 logs
```

## Files Changed

- ✅ `app/config/logging.py` - NEW - Logging configuration
- ✅ `app/main.py` - Updated to use new logging
- ✅ `.gitignore` - NEW - Exclude logs from git
- ✅ `logs/` - NEW - Directory for log files (gitignored)

---

**Status**: ✅ File-based Logging Implemented
**Date**: December 24, 2025
**Version**: 1.0.0
