# Accounts Service - Logging Strategy

## Overview
Removed database audit_logs table. Instead, implementing comprehensive application-level logging for all account operations.

## Logging Architecture

### 1. Application-Level Logging
All account operations are logged to files and console using Python's `logging` module with structured logging.

### 2. Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical failures

### 3. Log Format
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Example:
```
2025-12-24 13:15:53,590 - app.repositories.account_repo - INFO - ✅ Savings account created: 1000
2025-12-24 13:15:53,593 - app.services.account_service - INFO - ✅ Savings account service created: 1000
```

## Events to Log

### Account Creation
```
Event: Account Creation
Logger: app.services.account_service or app.repositories.account_repo
Level: INFO
Message Format: "✅ {ACCOUNT_TYPE} account created: {ACCOUNT_NUMBER}"
Data Logged:
  - Account Number (masked: XXXX1000)
  - Account Type (SAVINGS/CURRENT)
  - Account Name
  - Privilege Level
  - Timestamp
```

Example Log:
```
2025-12-24 13:15:53,590 - app.repositories.account_repo - INFO - ✅ Savings account created: 1000
```

### Account Debit/Credit
```
Event: Fund Transfer (Debit/Credit)
Logger: app.repositories.account_repo
Level: INFO
Message Format: "✅ {DEBIT|CREDIT} successful: {ACCOUNT_NUMBER}, Amount: ₹{AMOUNT}"
Data Logged:
  - Account Number (masked)
  - Amount
  - Transaction Type
  - Idempotency Key (if provided)
  - New Balance
  - Timestamp
```

Example Logs:
```
app.repositories.account_repo - INFO - ✅ Debit successful: 1000, Amount: ₹5000.00
app.repositories.account_repo - INFO - ✅ Credit successful: 1001, Amount: ₹5000.00
```

### Account Status Changes
```
Event: Account Activation/Inactivation/Closure
Logger: app.repositories.account_repo
Level: INFO
Message Format: "✅ Account {ACTIVATED|INACTIVATED|CLOSED}: {ACCOUNT_NUMBER}"
Data Logged:
  - Account Number (masked)
  - Previous Status
  - New Status
  - Reason (if applicable)
  - Timestamp
```

### PIN Verification
```
Event: PIN Verification
Logger: app.services.account_service
Level: INFO (success) or WARNING (failure)
Message Format: "✅ PIN verified for account: {ACCOUNT_NUMBER}" or "❌ PIN verification failed"
Data Logged:
  - Account Number (masked)
  - Verification Result
  - Timestamp
Note: Never log actual PIN
```

### Validation Errors
```
Event: Validation Failure
Logger: app.services.account_service or app.utils.validators
Level: ERROR
Message Format: "❌ Validation failed: {ERROR_CODE} - {MESSAGE}"
Data Logged:
  - Error Code (INVALID_PIN, AGE_RESTRICTION, etc.)
  - Error Message
  - Field Name
  - Timestamp
```

Example Logs:
```
app.api.accounts - ERROR - ❌ Account creation failed: INVALID_PIN
app.services.account_service - ERROR - ❌ Validation failed: AGE_RESTRICTION
```

### Database Errors
```
Event: Database Operation Error
Logger: app.repositories.account_repo
Level: ERROR
Message Format: "❌ Error {OPERATION} account {ACCOUNT_NUMBER}: {ERROR_MESSAGE}"
Data Logged:
  - Account Number (masked)
  - Operation (creating, updating, deleting)
  - Error Message
  - Exception Type
  - Timestamp
```

### Idempotency Checks
```
Event: Idempotent Operation
Logger: app.repositories.account_repo
Level: WARNING
Message Format: "⚠️ {OPERATION} already processed: {IDEMPOTENCY_KEY}"
Data Logged:
  - Operation Type
  - Idempotency Key
  - Previous Result
  - Timestamp
```

## Log Locations

### Configuration
```python
# app/config/settings.py
log_level: str = "INFO"
log_file: Optional[str] = "logs/accounts_service.log"
```

### Directory Structure
```
accounts_service/
├── logs/
│   ├── accounts_service.log         # Main application log
│   ├── accounts_service.log.1       # Rotated log files
│   └── accounts_service.log.2
├── app/
│   ├── repositories/                # Data access logs
│   ├── services/                    # Business logic logs
│   ├── api/                         # API endpoint logs
│   └── utils/                       # Utility function logs
```

## Log Samples

### Successful Account Creation
```
2025-12-24 13:15:53,590 - app.repositories.account_repo - INFO - ✅ Savings account created: 1000
2025-12-24 13:15:53,591 - app.services.account_service - INFO - ✅ Savings account service created: 1000
2025-12-24 13:15:53,592 - app.api.accounts - INFO - Account creation successful
127.0.0.1:64300 - "POST /api/v1/accounts/savings HTTP/1.1" 201 Created
```

### PIN Validation Error
```
2025-12-24 13:14:18,706 - app.services.account_service - ERROR - ❌ Validation failed: INVALID_PIN - PIN cannot be purely sequential
2025-12-24 13:14:18,707 - app.api.accounts - ERROR - ❌ Account creation failed: INVALID_PIN
127.0.0.1:51946 - "POST /api/v1/accounts/savings HTTP/1.1" 400 Bad Request
```

### Account Debit/Credit
```
2025-12-24 13:20:45,123 - app.repositories.account_repo - INFO - ✅ Debit successful: 1000, Amount: ₹5000.00
2025-12-24 13:20:45,456 - app.repositories.account_repo - INFO - ✅ Credit successful: 1001, Amount: ₹5000.00
2025-12-24 13:20:45,789 - app.services.internal_service - INFO - Transfer completed successfully
```

## Sensitive Data Masking

### Account Number
```python
mask_account_number(1000)  # Returns "XXXX1000"
mask_account_number(1234567)  # Returns "XXXX1234567"
```

### Phone Number
```python
mask_phone_number("9876543210")  # Returns "XXXXXX3210"
```

### PIN
```python
mask_pin("9640")  # Returns "XXXX"
```

Never log in code:
- ❌ Raw PIN values
- ❌ PIN hashes
- ❌ Credit card numbers
- ❌ Full phone numbers (masked instead)

## Log Rotation

Implement log rotation using Python's `RotatingFileHandler`:
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    filename="logs/accounts_service.log",
    maxBytes=10485760,  # 10MB
    backupCount=5       # Keep 5 old files
)
```

## Log Analysis

### Common Patterns to Monitor

#### 1. Account Creation Success Rate
```
Filter: "✅ account created"
Expected: High success rate, low errors
```

#### 2. PIN Validation Failures
```
Filter: "INVALID_PIN"
Alert if: High frequency of PIN validation failures
```

#### 3. Insufficient Funds
```
Filter: "INSUFFICIENT_FUNDS"
Alert if: Abnormal patterns
```

#### 4. Database Errors
```
Filter: "DatabaseError"
Alert if: Any database errors occur
```

## Implementation Checklist

- ✅ Removed `account_audit_logs` table from schema
- ✅ Application-level logging configured in `app/main.py`
- ✅ Logging configured for all layers:
  - API layer (`app/api/`)
  - Service layer (`app/services/`)
  - Repository layer (`app/repositories/`)
  - Utils (`app/utils/`)
- ✅ Sensitive data masking functions in `app/utils/helpers.py`
- 📋 TODO: Add structured logging (JSON format)
- 📋 TODO: Add log aggregation (ELK, Splunk)
- 📋 TODO: Add monitoring/alerting

## File Changes

### Removed:
- `account_audit_logs` table from `database_schemas/accounts_schema.sql`

### Configuration:
- `app/config/settings.py` - Logging configuration
- `app/main.py` - Logger initialization

### Logging in Code:
- `app/repositories/account_repo.py` - Data layer logs
- `app/services/account_service.py` - Service layer logs
- `app/services/internal_service.py` - Internal service logs
- `app/api/accounts.py` - API endpoint logs
- `app/api/internal_accounts.py` - Internal API logs
- `app/utils/validators.py` - Validation logs

## Example: Adding a Log Entry

```python
# In repository or service
import logging

logger = logging.getLogger(__name__)

# Success
logger.info(f"✅ Account created: {mask_account_number(account_number)}")

# Warning
logger.warning(f"⚠️ Debit failed for {mask_account_number(account_number)}: insufficient balance")

# Error
logger.error(f"❌ Error creating account: {str(e)}")

# Debug
logger.debug(f"Debit transaction: {transaction_id}, Amount: ₹{amount}")
```

## Migration from Database Logs to File Logs

### Old Approach (Removed):
```sql
INSERT INTO account_audit_logs 
(account_number, action, old_data, new_data, performed_at)
VALUES (1000, 'CREATE', NULL, {...}, NOW());
```

### New Approach (Active):
```python
logger.info(f"✅ Savings account created: 1000")
# Output: 2025-12-24 13:15:53,590 - app.repositories.account_repo - INFO - ✅ Savings account created: 1000
```

---

**Status**: ✅ Implementation Complete
**Date**: December 24, 2025
**Version**: 1.0.0

