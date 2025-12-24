# Account Number Generation Implementation

## Summary

Successfully implemented account number generation with the following features:

### 1. **Database Schema Updates**
- ✅ Added `id` column (BIGSERIAL PRIMARY KEY) to all tables
  - `accounts` table
  - `savings_account_details` table
  - `current_account_details` table
  - `account_audit_logs` table

- ✅ Added Gender ENUM type
  - Values: `Male`, `Female`, `Others`
  - Replaces old VARCHAR(10) with CHECK constraint

- ✅ Account Number Generation
  - Sequence: `account_number_seq` starting from 1000
  - Increment by 1: 1000, 1001, 1002, etc.
  - BIGSERIAL UNIQUE column to prevent duplicates

### 2. **New Utility Module: `helpers.py`**

Created `app/utils/helpers.py` with the following utilities:

#### `AccountNumberGenerator` Class
```python
class AccountNumberGenerator:
    START_NUMBER = 1000
    
    @staticmethod
    def format_account_number(seq_value: int) -> int
        # Format sequence value to account number
    
    @staticmethod
    def is_valid_account_number(account_number: int) -> bool
        # Validate account number is >= 1000
```

#### Helper Functions
- `generate_idempotency_key()` - UUID v4 for transaction retry safety
- `get_transaction_id()` - Unique transaction ID (timestamp + UUID)
- `mask_account_number()` - Mask account for logging (XXXX1234)
- `mask_phone_number()` - Mask phone for logging (XXXXXX1234)
- `mask_pin()` - Mask PIN for logging (XXXX)

#### `ResponseFormatter` Class
- `success_response()` - Consistent success response format
- `error_response()` - Consistent error response format

### 3. **Updated Components**

#### `account_repo.py`
- ✅ Added import: `from app.utils.helpers import AccountNumberGenerator`
- ✅ Added validation in `create_savings_account()`:
  ```python
  if not AccountNumberGenerator.is_valid_account_number(account_number):
      raise DatabaseError(f"Invalid account number generated: {account_number}")
  ```
- ✅ Added same validation in `create_current_account()`

#### `account_service.py`
- ✅ Added imports:
  ```python
  from app.utils.helpers import mask_account_number, generate_idempotency_key
  ```
- Ready to use helpers for logging and transaction management

#### `internal_service.py`
- ✅ Added import: `from app.utils.helpers import mask_account_number`
- Ready to mask account numbers in logs

### 4. **Account Number Flow**

```
create_savings_account() / create_current_account()
    ↓
    Database Transaction
    ↓
    SELECT nextval('account_number_seq')  -- Gets 1000, 1001, 1002...
    ↓
    AccountNumberGenerator.is_valid_account_number()  -- Validates >= 1000
    ↓
    INSERT INTO accounts (account_number, ...)
    ↓
    Account Created with number 1000, 1001, 1002, etc.
```

### 5. **Benefits**

✅ **Centralized Generation** - Single source of truth for account numbers
✅ **Type Safety** - Integer account numbers starting from 1000
✅ **Validation** - Ensures all account numbers are valid
✅ **Idempotency** - Helper methods for transaction retry safety
✅ **Security** - Helper functions to mask sensitive data in logs
✅ **Consistency** - Response formatter for consistent API responses
✅ **Scalability** - Sequence-based generation scales to billions

### 6. **Database Tables Structure**

```sql
-- accounts table
id (BIGSERIAL PK) | account_number (BIGSERIAL UNIQUE) | account_type | name | ...

-- savings_account_details table
id (BIGSERIAL PK) | account_number (BIGINT UNIQUE FK) | date_of_birth | gender (ENUM) | ...

-- current_account_details table
id (BIGSERIAL PK) | account_number (BIGINT UNIQUE FK) | company_name | ...

-- account_audit_logs table
log_id (BIGSERIAL PK) | account_number (BIGINT FK) | action | ...
```

### 7. **Example Usage in Code**

```python
# In Repository
account_number = await conn.fetchval("SELECT nextval('account_number_seq')")
if not AccountNumberGenerator.is_valid_account_number(account_number):
    raise DatabaseError(f"Invalid account number: {account_number}")

# In Service/API
idempotency_key = generate_idempotency_key()
transaction_id = get_transaction_id()

# For Logging
masked_account = mask_account_number(1000)  # Returns "XXXX1000"
masked_phone = mask_phone_number("9876543210")  # Returns "XXXXXX3210"

# For API Responses
return ResponseFormatter.success_response({
    "account_number": 1000,
    "balance": 0.00
}, "Account created successfully")
```

## Next Steps

1. Run database reset: `python reset_db.py`
2. Test account creation with the new schema
3. Verify account numbers start from 1000 and increment properly
4. Use helper functions for logging and transaction management

## Files Modified

- `database_schemas/accounts_schema.sql` - Updated schema with id columns and gender enum
- `app/utils/helpers.py` - **NEW** - Account number generation and helper utilities
- `app/models/account.py` - Updated gender field to use Literal["Male", "Female", "Others"]
- `app/repositories/account_repo.py` - Added account number validation
- `app/services/account_service.py` - Added helper imports
- `app/services/internal_service.py` - Added helper imports

---

**Status**: ✅ Implementation Complete
**Date**: December 24, 2025
