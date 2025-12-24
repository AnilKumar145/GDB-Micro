# Account Activation Status Exceptions

## Overview

Added custom exceptions to handle account activation status checks. These exceptions are raised when attempting to activate or inactivate an account that is already in the desired state.

## Exceptions

### 1. AccountAlreadyActiveError

**Error Code**: `ACCOUNT_ALREADY_ACTIVE`

**HTTP Status Code**: `409 Conflict`

**Raised When**: Attempting to activate an account that is already active.

**Exception Definition**:
```python
class AccountAlreadyActiveError(AccountException):
    """Raised when account is already active."""
    
    def __init__(self, account_number: int):
        super().__init__(
            error_code="ACCOUNT_ALREADY_ACTIVE",
            message=f"Account {account_number} is already active"
        )
```

**Example**:
```python
# This will raise AccountAlreadyActiveError
await account_service.activate_account(1000)  # if 1000 is already active
```

### 2. AccountAlreadyInactiveError

**Error Code**: `ACCOUNT_ALREADY_INACTIVE`

**HTTP Status Code**: `409 Conflict`

**Raised When**: Attempting to inactivate an account that is already inactive.

**Exception Definition**:
```python
class AccountAlreadyInactiveError(AccountException):
    """Raised when account is already inactive."""
    
    def __init__(self, account_number: int):
        super().__init__(
            error_code="ACCOUNT_ALREADY_INACTIVE",
            message=f"Account {account_number} is already inactive"
        )
```

**Example**:
```python
# This will raise AccountAlreadyInactiveError
await account_service.inactivate_account(1001)  # if 1001 is already inactive
```

## API Endpoints

### Activate Account Endpoint

**Route**: `POST /api/v1/accounts/{account_number}/activate`

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Account activated successfully",
  "account_number": 1000
}
```

**Error Responses**:

#### Already Active (409 Conflict)
```json
{
  "error_code": "ACCOUNT_ALREADY_ACTIVE",
  "message": "Account 1000 is already active"
}
```

#### Account Not Found (404 Not Found)
```json
{
  "error_code": "ACCOUNT_NOT_FOUND",
  "message": "Account 1000 not found"
}
```

#### Server Error (500 Internal Server Error)
```json
{
  "error_code": "INTERNAL_ERROR",
  "message": "Internal server error"
}
```

### Inactivate Account Endpoint

**Route**: `POST /api/v1/accounts/{account_number}/inactivate`

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Account inactivated successfully",
  "account_number": 1000
}
```

**Error Responses**:

#### Already Inactive (409 Conflict)
```json
{
  "error_code": "ACCOUNT_ALREADY_INACTIVE",
  "message": "Account 1000 is already inactive"
}
```

#### Account Not Found (404 Not Found)
```json
{
  "error_code": "ACCOUNT_NOT_FOUND",
  "message": "Account 1000 not found"
}
```

#### Server Error (500 Internal Server Error)
```json
{
  "error_code": "INTERNAL_ERROR",
  "message": "Internal server error"
}
```

## Implementation Details

### Service Layer Logic

**File**: `app/services/account_service.py`

```python
async def activate_account(self, account_number: int) -> bool:
    """
    Activate an account.
    
    Checks if account exists and is not already active.
    Raises AccountAlreadyActiveError if account is already active.
    """
    account = await self.repo.get_account(account_number)
    
    if not account:
        raise AccountNotFoundError(account_number)
    
    # Check if account is already active
    if account.is_active:
        raise AccountAlreadyActiveError(account_number)
    
    success = await self.repo.activate_account(account_number)
    
    if not success:
        raise AccountNotFoundError(account_number)
    
    logger.info(f"✅ Account activated: {account_number}")
    return True

async def inactivate_account(self, account_number: int) -> bool:
    """
    Inactivate an account.
    
    Checks if account exists and is not already inactive.
    Raises AccountAlreadyInactiveError if account is already inactive.
    """
    account = await self.repo.get_account(account_number)
    
    if not account:
        raise AccountNotFoundError(account_number)
    
    # Check if account is already inactive
    if not account.is_active:
        raise AccountAlreadyInactiveError(account_number)
    
    success = await self.repo.inactivate_account(account_number)
    
    if not success:
        raise AccountNotFoundError(account_number)
    
    logger.info(f"✅ Account inactivated: {account_number}")
    return True
```

### API Layer Error Handling

**File**: `app/api/accounts.py`

```python
@router.post("/accounts/{account_number}/activate")
async def activate_account(
    account_number: int,
    account_service: AccountService = Depends(get_account_service)
):
    try:
        success = await account_service.activate_account(account_number)
        
        return {
            "success": success,
            "message": "Account activated successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Activate account failed: {e.error_code}")
        
        # Map error codes to appropriate HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if "NOT_FOUND" in e.error_code:
            status_code = status.HTTP_404_NOT_FOUND
        elif "ALREADY_ACTIVE" in e.error_code:
            status_code = status.HTTP_409_CONFLICT
        
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )
```

## Testing

### Test Case 1: Activate an Inactive Account

**Scenario**: Create an account, inactivate it, then activate it again

**Steps**:
1. Create a savings account (account is active by default)
2. Inactivate the account using `POST /api/v1/accounts/{account_number}/inactivate`
3. Activate the account using `POST /api/v1/accounts/{account_number}/activate`

**Expected Result**:
```
Step 1: Account created with account_number = 1000 (is_active = true)
Step 2: Account inactivated (is_active = false) → 200 OK
Step 3: Account activated (is_active = true) → 200 OK
```

### Test Case 2: Activate Already Active Account

**Scenario**: Try to activate an account that is already active

**Steps**:
1. Create a savings account (is_active = true by default)
2. Attempt to activate it again using `POST /api/v1/accounts/{account_number}/activate`

**Expected Result**: 
```json
{
  "status_code": 409,
  "error_code": "ACCOUNT_ALREADY_ACTIVE",
  "message": "Account 1000 is already active"
}
```

**Log Output**:
```
2025-12-24 13:35:22 - app.api.accounts - ERROR - ❌ Activate account failed: ACCOUNT_ALREADY_ACTIVE
```

### Test Case 3: Inactivate Already Inactive Account

**Scenario**: Try to inactivate an account that is already inactive

**Steps**:
1. Create a savings account
2. Inactivate the account using `POST /api/v1/accounts/{account_number}/inactivate`
3. Attempt to inactivate it again

**Expected Result**:
```json
{
  "status_code": 409,
  "error_code": "ACCOUNT_ALREADY_INACTIVE",
  "message": "Account 1000 is already inactive"
}
```

**Log Output**:
```
2025-12-24 13:35:25 - app.api.accounts - ERROR - ❌ Inactivate account failed: ACCOUNT_ALREADY_INACTIVE
```

### Test Case 4: Activate Non-Existent Account

**Scenario**: Try to activate an account that doesn't exist

**Steps**:
1. Call `POST /api/v1/accounts/9999/activate` (account doesn't exist)

**Expected Result**:
```json
{
  "status_code": 404,
  "error_code": "ACCOUNT_NOT_FOUND",
  "message": "Account 9999 not found"
}
```

## cURL Examples

### Activate Account
```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate \
  -H "Content-Type: application/json"
```

**Success Response**:
```json
{
  "success": true,
  "message": "Account activated successfully",
  "account_number": 1000
}
```

**Error Response** (Already Active):
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_ACTIVE",
    "message": "Account 1000 is already active"
  }
}
```

### Inactivate Account
```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate \
  -H "Content-Type: application/json"
```

**Success Response**:
```json
{
  "success": true,
  "message": "Account inactivated successfully",
  "account_number": 1000
}
```

**Error Response** (Already Inactive):
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_INACTIVE",
    "message": "Account 1000 is already inactive"
  }
}
```

## Exception Hierarchy

```
AccountException (Base)
├── AccountNotFoundError
├── AccountInactiveError
├── AccountClosedError
├── InsufficientFundsError
├── InvalidPinError
├── AccountAlreadyActiveError      ← NEW
└── AccountAlreadyInactiveError    ← NEW
```

## Files Modified

| File | Changes |
|------|---------|
| `app/exceptions/account_exceptions.py` | Added `AccountAlreadyActiveError` and `AccountAlreadyInactiveError` classes |
| `app/services/account_service.py` | Updated `activate_account()` and `inactivate_account()` to check status and raise new exceptions |
| `app/api/accounts.py` | Added error handling for new exceptions with 409 Conflict status code |

## Key Features

✅ **Status Validation**: Checks account status before activation/inactivation
✅ **Clear Error Messages**: User-friendly error messages with account number
✅ **HTTP 409 Conflict**: Proper HTTP status code for idempotency conflicts
✅ **Logging**: All events logged with emoji indicators
✅ **Backward Compatible**: Existing error handling still works
✅ **Type-Safe**: Uses Pydantic model attributes instead of dictionary `.get()`

## Migration Notes

If upgrading from previous version:
- No database schema changes required
- No breaking API changes
- New exceptions provide better error feedback
- Activation endpoints now properly validate account state

---

**Status**: ✅ Complete
**Date**: December 24, 2025
**Version**: 1.0.0
