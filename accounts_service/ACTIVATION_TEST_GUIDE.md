# Account Activation Test Guide

## Setup

Make sure the server is running:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

## Test Scenarios

### Scenario 1: Activate an Already Active Account

#### Step 1: Create a Savings Account

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

**Expected Response** (HTTP 201):
```json
{
  "account_number": 1000,
  "account_type": "SAVINGS",
  "name": "John Doe",
  "privilege": "SILVER",
  "balance": 5000.00,
  "is_active": true,
  "activated_date": "2025-12-24T13:35:00",
  "closed_date": null
}
```

#### Step 2: Try to Activate the Already Active Account

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate \
  -H "Content-Type: application/json"
```

**Expected Response** (HTTP 409 Conflict):
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_ACTIVE",
    "message": "Account 1000 is already active"
  }
}
```

**Server Log** (shows error logging):
```
2025-12-24 13:35:22 - app.api.accounts - ERROR - ❌ Activate account failed: ACCOUNT_ALREADY_ACTIVE
```

✅ **Test Passed** - Server correctly rejects activation of already active account

---

### Scenario 2: Inactivate and Then Try to Inactivate Again

#### Step 1: Inactivate the Account

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate \
  -H "Content-Type: application/json"
```

**Expected Response** (HTTP 200):
```json
{
  "success": true,
  "message": "Account inactivated successfully",
  "account_number": 1000
}
```

**Server Log**:
```
2025-12-24 13:35:25 - app.services.account_service - INFO - ✅ Account inactivated: 1000
```

#### Step 2: Try to Inactivate the Already Inactive Account

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate \
  -H "Content-Type: application/json"
```

**Expected Response** (HTTP 409 Conflict):
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_INACTIVE",
    "message": "Account 1000 is already inactive"
  }
}
```

**Server Log**:
```
2025-12-24 13:35:28 - app.api.accounts - ERROR - ❌ Inactivate account failed: ACCOUNT_ALREADY_INACTIVE
```

✅ **Test Passed** - Server correctly rejects inactivation of already inactive account

---

### Scenario 3: Activate an Inactivated Account

#### Step 1: Activate the Inactivated Account

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate \
  -H "Content-Type: application/json"
```

**Expected Response** (HTTP 200):
```json
{
  "success": true,
  "message": "Account activated successfully",
  "account_number": 1000
}
```

**Server Log**:
```
2025-12-24 13:35:31 - app.services.account_service - INFO - ✅ Account activated: 1000
```

✅ **Test Passed** - Activation of inactive account succeeds

---

### Scenario 4: Activate Non-Existent Account

```bash
curl -X POST http://localhost:8001/api/v1/accounts/9999/activate \
  -H "Content-Type: application/json"
```

**Expected Response** (HTTP 404):
```json
{
  "detail": {
    "error_code": "ACCOUNT_NOT_FOUND",
    "message": "Account 9999 not found"
  }
}
```

**Server Log**:
```
2025-12-24 13:35:34 - app.api.accounts - ERROR - ❌ Activate account failed: ACCOUNT_NOT_FOUND
```

✅ **Test Passed** - Proper error for non-existent account

---

## Python Test Script

Save this as `test_activation.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_account_activation():
    print("=" * 60)
    print("Account Activation Status Tests")
    print("=" * 60)
    
    # Test 1: Create account
    print("\n[Test 1] Create Savings Account")
    response = requests.post(
        f"{BASE_URL}/accounts/savings",
        json={
            "name": "Test User",
            "date_of_birth": "1990-05-20",
            "phone_number": "9876543210",
            "email": "test@example.com",
            "gender": "Male",
            "address": "123 Test St",
            "pin": "9640",
            "initial_balance": 1000.00
        }
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    account = response.json()
    account_number = account['account_number']
    print(f"✅ Account created: {account_number} (is_active: {account['is_active']})")
    
    # Test 2: Try to activate already active account
    print("\n[Test 2] Try to Activate Already Active Account")
    response = requests.post(
        f"{BASE_URL}/accounts/{account_number}/activate"
    )
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    error = response.json()
    assert error['detail']['error_code'] == "ACCOUNT_ALREADY_ACTIVE"
    print(f"✅ Correctly rejected: {error['detail']['message']}")
    
    # Test 3: Inactivate account
    print("\n[Test 3] Inactivate Account")
    response = requests.post(
        f"{BASE_URL}/accounts/{account_number}/inactivate"
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    print(f"✅ Account inactivated: {result['message']}")
    
    # Test 4: Try to inactivate already inactive account
    print("\n[Test 4] Try to Inactivate Already Inactive Account")
    response = requests.post(
        f"{BASE_URL}/accounts/{account_number}/inactivate"
    )
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    error = response.json()
    assert error['detail']['error_code'] == "ACCOUNT_ALREADY_INACTIVE"
    print(f"✅ Correctly rejected: {error['detail']['message']}")
    
    # Test 5: Activate inactivated account
    print("\n[Test 5] Activate Inactivated Account")
    response = requests.post(
        f"{BASE_URL}/accounts/{account_number}/activate"
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    print(f"✅ Account activated: {result['message']}")
    
    # Test 6: Try to activate non-existent account
    print("\n[Test 6] Try to Activate Non-Existent Account")
    response = requests.post(
        f"{BASE_URL}/accounts/9999/activate"
    )
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    error = response.json()
    assert error['detail']['error_code'] == "ACCOUNT_NOT_FOUND"
    print(f"✅ Correctly rejected: {error['detail']['message']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_account_activation()
```

Run the test:
```bash
python test_activation.py
```

---

## Expected Output

```
============================================================
Account Activation Status Tests
============================================================

[Test 1] Create Savings Account
✅ Account created: 1000 (is_active: True)

[Test 2] Try to Activate Already Active Account
✅ Correctly rejected: Account 1000 is already active

[Test 3] Inactivate Account
✅ Account inactivated: Account inactivated successfully

[Test 4] Try to Inactivate Already Inactive Account
✅ Correctly rejected: Account 1000 is already inactive

[Test 5] Activate Inactivated Account
✅ Account activated: Account activated successfully

[Test 6] Try to Activate Non-Existent Account
✅ Correctly rejected: Account 9999 not found

============================================================
✅ All tests passed!
============================================================
```

## Verification Checklist

- ✅ Create account succeeds (HTTP 201)
- ✅ Account is active by default (is_active = true)
- ✅ Activate already active account fails with 409
- ✅ Inactivate account succeeds (HTTP 200)
- ✅ Inactivate already inactive account fails with 409
- ✅ Activate inactivated account succeeds
- ✅ Activate non-existent account fails with 404
- ✅ Error messages are clear and descriptive
- ✅ Error codes are correct and standardized
- ✅ Logging shows proper error handling

---

**Status**: ✅ Ready for Testing
**Date**: December 24, 2025
