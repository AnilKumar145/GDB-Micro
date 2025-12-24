# Account Activation Status Exceptions

## Overview

Two new custom exceptions have been added to prevent invalid account state transitions. These exceptions ensure that accounts cannot be activated if already active, or deactivated if already inactive.

## New Exceptions

### 1. `AccountAlreadyActiveError`

**Purpose**: Raised when attempting to activate an account that is already active.

**Error Code**: `ACCOUNT_ALREADY_ACTIVE`

**HTTP Status Code**: `409 Conflict`

**Example**:
```python
from app.exceptions.account_exceptions import AccountAlreadyActiveError

raise AccountAlreadyActiveError(account_number=1000)
# Message: "Account 1000 is already active"
```

**When it's raised**:
```python
# In AccountService.activate_account()
account = await self.repo.get_account(account_number)

if account.get('is_active', False):  # Account is already active
    raise AccountAlreadyActiveError(account_number)
```

**API Response**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_ACTIVE",
    "message": "Account 1000 is already active"
  }
}
```

---

### 2. `AccountAlreadyInactiveError`

**Purpose**: Raised when attempting to inactivate an account that is already inactive.

**Error Code**: `ACCOUNT_ALREADY_INACTIVE`

**HTTP Status Code**: `409 Conflict`

**Example**:
```python
from app.exceptions.account_exceptions import AccountAlreadyInactiveError

raise AccountAlreadyInactiveError(account_number=1000)
# Message: "Account 1000 is already inactive"
```

**When it's raised**:
```python
# In AccountService.inactivate_account()
account = await self.repo.get_account(account_number)

if not account.get('is_active', False):  # Account is already inactive
    raise AccountAlreadyInactiveError(account_number)
```

**API Response**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_INACTIVE",
    "message": "Account 1000 is already inactive"
  }
}
```

---

## Implementation Details

### Service Layer Logic

**AccountService.activate_account()**:
```python
async def activate_account(self, account_number: int) -> bool:
    """Activate an account."""
    account = await self.repo.get_account(account_number)
    
    if not account:
        raise AccountNotFoundError(account_number)  # 404
    
    if account.get('is_active', False):
        raise AccountAlreadyActiveError(account_number)  # 409
    
    success = await self.repo.activate_account(account_number)
    if not success:
        raise AccountNotFoundError(account_number)  # 404
    
    logger.info(f"✅ Account activated: {account_number}")
    return True
```

**AccountService.inactivate_account()**:
```python
async def inactivate_account(self, account_number: int) -> bool:
    """Inactivate an account."""
    account = await self.repo.get_account(account_number)
    
    if not account:
        raise AccountNotFoundError(account_number)  # 404
    
    if not account.get('is_active', False):
        raise AccountAlreadyInactiveError(account_number)  # 409
    
    success = await self.repo.inactivate_account(account_number)
    if not success:
        raise AccountNotFoundError(account_number)  # 404
    
    logger.info(f"✅ Account inactivated: {account_number}")
    return True
```

### API Layer Handling

**Endpoints**: `POST /api/v1/accounts/{account_number}/activate`

**Status Code Mapping**:
- `404 Not Found`: Account doesn't exist (`ACCOUNT_NOT_FOUND`)
- `409 Conflict`: Account is already in the desired state (`ACCOUNT_ALREADY_ACTIVE` or `ACCOUNT_ALREADY_INACTIVE`)
- `500 Internal Server Error`: Unexpected errors

**Exception Handler**:
```python
except AccountException as e:
    logger.error(f"❌ Activate account failed: {e.error_code}")
    
    status_code = status.HTTP_400_BAD_REQUEST
    if "NOT_FOUND" in e.error_code:
        status_code = status.HTTP_404_NOT_FOUND
    elif "ALREADY_ACTIVE" in e.error_code:
        status_code = status.HTTP_409_CONFLICT
    
    raise HTTPException(
        status_code=status_code,
        detail={"error_code": e.error_code, "message": e.message}
    )
```

---

## API Usage Examples

### Activate an Account

**Request**:
```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Account activated successfully",
  "account_number": 1000
}
```

**Error - Already Active (409)**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_ACTIVE",
    "message": "Account 1000 is already active"
  }
}
```

**Error - Not Found (404)**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_NOT_FOUND",
    "message": "Account 9999 not found"
  }
}
```

---

### Inactivate an Account

**Request**:
```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Account inactivated successfully",
  "account_number": 1000
}
```

**Error - Already Inactive (409)**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_INACTIVE",
    "message": "Account 1000 is already inactive"
  }
}
```

**Error - Not Found (404)**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_NOT_FOUND",
    "message": "Account 9999 not found"
  }
}
```

---

## State Transition Diagram

```
Account Lifecycle:
┌─────────────┐
│  Created    │
│ (inactive)  │
└──────┬──────┘
       │ activate
       ▼
┌─────────────┐
│    Active   │ ◄──── Cannot activate (ALREADY_ACTIVE)
│             │ ──┐
└──────┬──────┘   │
       │          │ Cannot inactivate twice
       │          │ (ALREADY_INACTIVE)
       │ inactivate
       ▼
┌─────────────┐
│  Inactive   │ ◄──── Cannot inactivate (ALREADY_INACTIVE)
│             │
└──────┬──────┘
       │ activate
       ▼
    Back to Active
```

---

## Error Handling Best Practices

### ✅ Correct Usage

```python
try:
    await account_service.activate_account(account_number)
except AccountAlreadyActiveError as e:
    # Account is already active - skip or inform user
    logger.warning(f"Account {account_number} already active")
except AccountNotFoundError as e:
    # Account doesn't exist - handle appropriately
    logger.error(f"Account not found: {account_number}")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
```

### ❌ Incorrect Usage

```python
# Don't ignore the error
result = await account_service.activate_account(account_number)  # May raise!
if result:
    # This block might not execute if exception is raised
    process_account()

# Don't catch generic Exception only
except Exception as e:
    # Loses specific error code information
    raise Exception("Something went wrong")
```

---

## Testing Examples

### Test Already Active Error

```python
import pytest
from app.exceptions.account_exceptions import AccountAlreadyActiveError

@pytest.mark.asyncio
async def test_activate_already_active_account():
    """Test activating an already active account raises exception."""
    account_number = 1000
    
    # Create an active account
    await account_service.activate_account(account_number)
    
    # Try to activate again - should raise
    with pytest.raises(AccountAlreadyActiveError):
        await account_service.activate_account(account_number)
```

### Test Already Inactive Error

```python
@pytest.mark.asyncio
async def test_inactivate_already_inactive_account():
    """Test inactivating an already inactive account raises exception."""
    account_number = 1000
    
    # Account starts as inactive
    
    # Try to inactivate - should raise
    with pytest.raises(AccountAlreadyInactiveError):
        await account_service.inactivate_account(account_number)
```

---

## Files Modified

- ✅ `app/exceptions/account_exceptions.py` - Added 2 new exceptions
- ✅ `app/services/account_service.py` - Updated activate/inactivate logic
- ✅ `app/api/accounts.py` - Enhanced error handling with 409 Conflict status

---

## Summary of Changes

| Component | Change | Purpose |
|-----------|--------|---------|
| Exceptions | +2 new exceptions | Prevent invalid state transitions |
| Service | Status validation | Check `is_active` before operations |
| API | Status code mapping | Return 409 for duplicate operations |
| Logging | Error logging | Log when state conflicts occur |

---

**Status**: ✅ Account Activation Status Exceptions Implemented
**Date**: December 24, 2025
**Version**: 1.0.0
