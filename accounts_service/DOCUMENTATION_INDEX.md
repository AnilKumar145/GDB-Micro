# Documentation Index - Accounts Service

## Complete Setup & Configuration Documentation

### Database & Infrastructure

| Document | Purpose | Status |
|----------|---------|--------|
| **DATABASE_SCRIPTS_UPDATE.md** | Updates to setup_db.py and reset_db.py with logging | ✅ |
| **LOGGING_IMPLEMENTATION.md** | File-based logging setup with rotation | ✅ |
| **QUICK_REFERENCE.md** | Quick start guide for database operations | ✅ |
| **.gitignore** | Git configuration excluding logs, env, cache | ✅ |
| **logs/** | Directory for application logs (auto-created) | ✅ |

### Feature Implementation

| Document | Purpose | Status |
|----------|---------|--------|
| **ACCOUNT_ACTIVATION_EXCEPTIONS.md** | Custom exceptions for account status checks | ✅ |
| **ACTIVATION_FIX_SUMMARY.md** | Quick summary of the activation status fix | ✅ |
| **ACTIVATION_TEST_GUIDE.md** | Comprehensive testing scenarios | ✅ |
| **ACTIVATION_STATUS_SUMMARY.md** | Complete implementation summary | ✅ |

### Reference Documents (Previously Created)

| Document | Purpose |
|----------|---------|
| CODEBASE_ANALYSIS.md | Complete codebase architecture analysis |
| PIN_VALIDATION_RULES.md | PIN validation logic and test cases |
| ACCOUNT_NUMBER_GENERATION.md | Account number generation strategy |
| INTER_SERVICE_COMMUNICATION_ANALYSIS.md | Service communication patterns |

---

## Getting Started Quick Guide

### 1. Initial Setup (First Time)

```bash
# 1. Navigate to accounts service
cd accounts_service

# 2. Create/reset database
python reset_db.py

# 3. Start the server
python -m uvicorn app.main:app --reload --port 8001

# 4. Access API docs
# Browser: http://localhost:8001/api/v1/docs
```

### 2. Create an Account

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

**Response** (Account number = 1000):
```json
{
  "account_number": 1000,
  "is_active": true,
  "balance": 5000.00
}
```

### 3. Test Activation Status

```bash
# Try to activate already active account (should fail)
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate

# Inactivate account
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate

# Try to inactivate already inactive account (should fail)
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate
```

### 4. Monitor Logs

```powershell
# Windows PowerShell - Real-time logs
Get-Content logs/accounts_service.log -Wait
```

```bash
# Linux/Mac - Real-time logs
tail -f logs/accounts_service.log
```

---

## File Structure

```
accounts_service/
├── Documentation (You are here)
│   ├── DOCUMENTATION_INDEX.md          ← This file
│   ├── DATABASE_SCRIPTS_UPDATE.md
│   ├── LOGGING_IMPLEMENTATION.md
│   ├── QUICK_REFERENCE.md
│   ├── ACCOUNT_ACTIVATION_EXCEPTIONS.md
│   ├── ACTIVATION_FIX_SUMMARY.md
│   ├── ACTIVATION_TEST_GUIDE.md
│   └── ACTIVATION_STATUS_SUMMARY.md
├── Scripts
│   ├── setup_db.py                    ← Create database (updated with logging)
│   ├── reset_db.py                    ← Reset database (updated with logging)
│   └── run_tests.py
├── logs/                               ← Application logs (auto-created)
│   └── accounts_service.log
├── app/
│   ├── main.py                         ← FastAPI entry point
│   ├── config/
│   │   ├── logging.py                  ← Logging configuration (NEW)
│   │   └── settings.py
│   ├── api/
│   │   ├── accounts.py                 ← Account endpoints
│   │   └── internal_accounts.py
│   ├── services/
│   │   ├── account_service.py          ← Fixed activation methods
│   │   └── internal_service.py
│   ├── repositories/
│   │   └── account_repo.py
│   ├── models/
│   │   └── account.py
│   ├── exceptions/
│   │   └── account_exceptions.py       ← Custom exceptions
│   ├── database/
│   │   └── db.py
│   └── utils/
│       ├── helpers.py                  ← Account number generation (NEW)
│       └── validators.py
├── database_schemas/
│   └── accounts_schema.sql             ← Updated with gender enum
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_services.py
│   └── ... (other test files)
├── .env                                ← Environment config (NEW)
├── .gitignore                          ← Git configuration (NEW)
└── requirements.txt

```

---

## Documentation Navigation

### For Database Operations
→ Start with **QUICK_REFERENCE.md** for quick start
→ Then read **DATABASE_SCRIPTS_UPDATE.md** for details
→ See **LOGGING_IMPLEMENTATION.md** for logging setup

### For Account Activation Feature
→ Start with **ACTIVATION_FIX_SUMMARY.md** for overview
→ Read **ACCOUNT_ACTIVATION_EXCEPTIONS.md** for exception details
→ Use **ACTIVATION_TEST_GUIDE.md** for testing scenarios
→ See **ACTIVATION_STATUS_SUMMARY.md** for complete details

### For Development
→ Read **CODEBASE_ANALYSIS.md** for architecture
→ Check **PIN_VALIDATION_RULES.md** for PIN validation
→ See **ACCOUNT_NUMBER_GENERATION.md** for number generation

### For API Usage
→ Use Swagger UI: http://localhost:8001/api/v1/docs
→ Use ReDoc: http://localhost:8001/api/v1/redoc
→ Reference **QUICK_REFERENCE.md** for cURL examples

---

## Key Features Implemented

### ✅ Database & Logging
- [x] File-based logging with automatic rotation (10MB per file)
- [x] Setup and reset scripts with logging integration
- [x] Comprehensive database schema with enums and sequences
- [x] Account number generation starting from 1000

### ✅ Account Management
- [x] Create savings and current accounts
- [x] Activate/inactivate accounts with status validation
- [x] Get account details and balance
- [x] Update account information

### ✅ Validation & Error Handling
- [x] PIN validation (no sequential patterns)
- [x] Age restriction (must be >= 18)
- [x] Gender enum (Male, Female, Others)
- [x] Custom exception hierarchy with proper HTTP status codes
- [x] Account status validation (already active/inactive checks)

### ✅ Error Codes
```
ACCOUNT_NOT_FOUND         → 404 Not Found
ACCOUNT_ALREADY_ACTIVE    → 409 Conflict
ACCOUNT_ALREADY_INACTIVE  → 409 Conflict
ACCOUNT_INACTIVE          → 400 Bad Request
INVALID_PIN               → 400 Bad Request
AGE_RESTRICTION           → 400 Bad Request
INTERNAL_ERROR            → 500 Server Error
```

---

## Recent Fixes & Updates

### December 24, 2025

**Fixed**: Account Activation 500 Error
- Problem: Pydantic model treated as dictionary
- Solution: Changed `.get('is_active')` to `account.is_active`
- Files: `app/services/account_service.py` (2 methods)
- Result: Proper HTTP 409 responses for status conflicts

**Added**: Logging Integration
- Updated `setup_db.py` with logging
- Updated `reset_db.py` with logging
- Created `app/config/logging.py`
- Created `.gitignore`
- Created `logs/` directory

**Created**: Comprehensive Documentation
- 8 documentation files
- Test guide with Python script
- Quick reference guide
- Complete implementation summaries

---

## Testing Checklist

### ✅ Completed Tests
- [x] Database setup/reset with new schema
- [x] Account creation (savings and current)
- [x] Account number generation (starts from 1000)
- [x] PIN validation rules
- [x] Account activation status checks
- [x] Proper error codes and HTTP status
- [x] Logging to file with rotation
- [x] Gender enum validation

### 📋 Recommended Additional Tests
- [ ] End-to-end API test suite
- [ ] Load testing with concurrent requests
- [ ] Database backup/restore procedures
- [ ] Security testing (PIN hashing, SQL injection)
- [ ] Performance testing (query optimization)

---

## Common Commands

```bash
# Setup/Reset Database
python setup_db.py              # Create fresh database
python reset_db.py              # Drop and recreate

# Start Server
python -m uvicorn app.main:app --reload --port 8001

# View Logs
Get-Content logs/accounts_service.log -Wait    # Windows
tail -f logs/accounts_service.log              # Linux/Mac

# Run Tests
python -m pytest tests/

# Check Errors
python -m pylint app/
python -m flake8 app/
```

---

## Performance Notes

### Log Rotation
- Max file size: 10 MB
- Backup files: 5
- Total capacity: ~60 MB
- Automatic cleanup of oldest logs

### Database
- Connection pool: 5-20 connections
- Async operations with asyncpg
- Transaction support with rollback

### Account Numbers
- Sequence starts: 1000
- Increment: 1 per account
- Max accounts: Theoretical max of BIGINT

---

## Support & Troubleshooting

### Database Won't Connect
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Check credentials: postgres:anil@localhost:5432

### Logs Not Appearing
1. Check LOG_LEVEL in .env (should be INFO or DEBUG)
2. Verify logs/ directory exists
3. Check file permissions: `chmod 755 logs/`

### Account Activation Fails
1. Check account exists: GET /api/v1/accounts/{number}
2. Verify account status in response
3. Check logs for error details

### Pin Validation Fails
1. PIN must be 4-6 digits
2. Can't use sequential patterns (1234, 4321)
3. Valid examples: 9640, 2468, 1357

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-24 | Initial release with logging & activation exceptions |
| 0.9.0 | 2025-12-23 | Helper utilities and PIN validation |
| 0.8.0 | 2025-12-22 | Dependency injection fixes |
| 0.7.0 | 2025-12-21 | Database schema with enums |

---

## Contact & Support

For issues or questions:
1. Check relevant documentation file above
2. Review error messages in logs/accounts_service.log
3. Check API response error codes
4. Refer to test guide for scenario examples

---

**Last Updated**: December 24, 2025
**Status**: ✅ Production Ready
**Maintained By**: GDB Architecture Team
