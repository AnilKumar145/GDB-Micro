# Account Activation Status Exceptions - Implementation Summary

## What Was Added

Two new custom exceptions to prevent invalid account state transitions:

### 1. **AccountAlreadyActiveError**
- Raised when trying to activate an already active account
- Error Code: `ACCOUNT_ALREADY_ACTIVE`
- HTTP Status: `409 Conflict`

### 2. **AccountAlreadyInactiveError**
- Raised when trying to deactivate an already inactive account
- Error Code: `ACCOUNT_ALREADY_INACTIVE`
- HTTP Status: `409 Conflict`

---

## Files Modified

### 1. `app/exceptions/account_exceptions.py`

**Added** (after line 169):
```python
class AccountAlreadyActiveError(AccountException):
    """Raised when trying to activate an already active account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is already active",
            "ACCOUNT_ALREADY_ACTIVE"
        )


class AccountAlreadyInactiveError(AccountException):
    """Raised when trying to deactivate an already inactive account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is already inactive",
            "ACCOUNT_ALREADY_INACTIVE"
        )
```

---

### 2. `app/services/account_service.py`

**Updated Imports** (lines 23-29):
```python
from app.exceptions.account_exceptions import (
    AccountNotFoundError,
    AccountInactiveError,
    AccountClosedError,
    InsufficientFundsError,
    InvalidPinError,
    AccountAlreadyActiveError,          # ← NEW
    AccountAlreadyInactiveError         # ← NEW
)
```

**Updated Method: `activate_account()`** (lines 359-388):
```python
async def activate_account(self, account_number: int) -> bool:
    """
    Activate an account.
    
    Args:
        account_number: Account to activate
        
    Returns:
        True if activated
        
    Raises:
        AccountNotFoundError: If account doesn't exist
        AccountAlreadyActiveError: If account is already active
    """
    account = await self.repo.get_account(account_number)
    
    if not account:
        raise AccountNotFoundError(account_number)
    
    # Check if account is already active
    if account.get('is_active', False):
        raise AccountAlreadyActiveError(account_number)  # ← NEW
    
    success = await self.repo.activate_account(account_number)
    
    if not success:
        raise AccountNotFoundError(account_number)
    
    logger.info(f"✅ Account activated: {account_number}")
    return True
```

**Updated Method: `inactivate_account()`** (lines 390-418):
```python
async def inactivate_account(self, account_number: int) -> bool:
    """
    Inactivate an account.
    
    Args:
        account_number: Account to inactivate
        
    Returns:
        True if inactivated
        
    Raises:
        AccountNotFoundError: If account doesn't exist
        AccountAlreadyInactiveError: If account is already inactive
    """
    account = await self.repo.get_account(account_number)
    
    if not account:
        raise AccountNotFoundError(account_number)
    
    # Check if account is already inactive
    if not account.get('is_active', False):
        raise AccountAlreadyInactiveError(account_number)  # ← NEW
    
    success = await self.repo.inactivate_account(account_number)
    
    if not success:
        raise AccountNotFoundError(account_number)
    
    logger.info(f"✅ Account inactivated: {account_number}")
    return True
```

---

### 3. `app/api/accounts.py`

**Updated: `activate_account()` endpoint error handler** (lines 385-397):
```python
except AccountException as e:
    logger.error(f"❌ Activate account failed: {e.error_code}")
    # Map error codes to appropriate HTTP status codes
    status_code = status.HTTP_400_BAD_REQUEST
    if "NOT_FOUND" in e.error_code:
        status_code = status.HTTP_404_NOT_FOUND
    elif "ALREADY_ACTIVE" in e.error_code:              # ← NEW
        status_code = status.HTTP_409_CONFLICT          # ← NEW
    
    raise HTTPException(
        status_code=status_code,
        detail={"error_code": e.error_code, "message": e.message}
    )
```

**Updated: `inactivate_account()` endpoint error handler** (lines 432-444):
```python
except AccountException as e:
    logger.error(f"❌ Inactivate account failed: {e.error_code}")
    # Map error codes to appropriate HTTP status codes
    status_code = status.HTTP_400_BAD_REQUEST
    if "NOT_FOUND" in e.error_code:
        status_code = status.HTTP_404_NOT_FOUND
    elif "ALREADY_INACTIVE" in e.error_code:            # ← NEW
        status_code = status.HTTP_409_CONFLICT          # ← NEW
    
    raise HTTPException(
        status_code=status_code,
        detail={"error_code": e.error_code, "message": e.message}
    )
```

---

## How It Works

### Activation Flow

1. **User calls**: `POST /api/v1/accounts/1000/activate`
2. **API endpoint** calls: `account_service.activate_account(1000)`
3. **Service layer**:
   - Fetches account from database
   - Checks if `is_active == False` (inactive)
   - ✅ If inactive → activates it
   - ❌ If already active → raises `AccountAlreadyActiveError`
   - ❌ If not found → raises `AccountNotFoundError`
4. **API layer** catches exception:
   - Maps error code to HTTP status
   - Returns JSON response with error details
5. **Client receives**:
   - `200 OK` if successful
   - `404 Not Found` if account doesn't exist
   - `409 Conflict` if already in desired state

---

## Testing the Feature

### Test 1: Activate Account Twice

```bash
# First activation - Success
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate

# Response: 200 OK
{
  "success": true,
  "message": "Account activated successfully",
  "account_number": 1000
}

# Second activation - Conflict
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate

# Response: 409 Conflict
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_ACTIVE",
    "message": "Account 1000 is already active"
  }
}
```

### Test 2: Inactivate Account Twice

```bash
# First inactivation - Success
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate

# Response: 200 OK
{
  "success": true,
  "message": "Account inactivated successfully",
  "account_number": 1000
}

# Second inactivation - Conflict
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate

# Response: 409 Conflict
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_INACTIVE",
    "message": "Account 1000 is already inactive"
  }
}
```

### Test 3: Activate Non-existent Account

```bash
# Try to activate account that doesn't exist
curl -X POST http://localhost:8001/api/v1/accounts/9999/activate

# Response: 404 Not Found
{
  "detail": {
    "error_code": "ACCOUNT_NOT_FOUND",
    "message": "Account 9999 not found"
  }
}
```

---

## Benefits

### ✅ Data Integrity
- Prevents invalid state transitions
- Ensures consistent account status
- No silent failures

### ✅ Better Error Handling
- Clear, specific error messages
- Proper HTTP status codes (409 Conflict)
- Distinguishes between "not found" and "already in state"

### ✅ User Experience
- Users understand why operation failed
- Clear distinction between error types
- Can provide appropriate feedback

### ✅ Debugging
- Logging captures state conflicts
- Error codes aid troubleshooting
- Audit trail of state change attempts

---

## Logging

All operations are logged to `logs/accounts_service.log`:

```
2025-12-24 13:31:26 - app.services.account_service - INFO - ✅ Account activated: 1000
2025-12-24 13:31:32 - app.services.account_service - ERROR - Account 1000 is already active
2025-12-24 13:31:32 - app.api.accounts - ERROR - ❌ Activate account failed: ACCOUNT_ALREADY_ACTIVE
```

---

## Related Documentation

- 📄 `ACTIVATION_STATUS_EXCEPTIONS.md` - Comprehensive exception documentation
- 📄 `LOGGING_IMPLEMENTATION.md` - Logging strategy and usage
- 📄 `QUICK_REFERENCE.md` - Quick start guide

---

## Summary

✅ Added 2 new custom exceptions
✅ Updated service layer with status validation  
✅ Enhanced API error handling with proper status codes
✅ All changes logged and documented
✅ Ready for production use

---

**Status**: ✅ Complete
**Date**: December 24, 2025
**Version**: 1.0.0
