# Account Activation Status Exceptions - Testing Guide

## Quick Test Commands

### Prerequisites
```bash
# Make sure server is running
python -m uvicorn app.main:app --reload --port 8001

# In another terminal, navigate to accounts service
cd accounts_service
```

---

## Scenario 1: Activate Account Twice

### Step 1: Create an Account

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

**Expected Response**:
```json
{
  "account_number": 1000,
  "name": "John Doe",
  "is_active": false
}
```

### Step 2: Activate Account (First Time)

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate
```

**Expected Response (200 OK)**:
```json
{
  "success": true,
  "message": "Account activated successfully",
  "account_number": 1000
}
```

### Step 3: Activate Again (Should Fail)

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/activate
```

**Expected Response (409 Conflict)**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_ACTIVE",
    "message": "Account 1000 is already active"
  }
}
```

✅ **Success**: Got 409 Conflict with `ACCOUNT_ALREADY_ACTIVE` error

---

## Scenario 2: Inactivate Account Twice

### Step 1: Inactivate Account (First Time)

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate
```

**Expected Response (200 OK)**:
```json
{
  "success": true,
  "message": "Account inactivated successfully",
  "account_number": 1000
}
```

### Step 2: Inactivate Again (Should Fail)

```bash
curl -X POST http://localhost:8001/api/v1/accounts/1000/inactivate
```

**Expected Response (409 Conflict)**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_INACTIVE",
    "message": "Account 1000 is already inactive"
  }
}
```

✅ **Success**: Got 409 Conflict with `ACCOUNT_ALREADY_INACTIVE` error

---

## Scenario 3: Activate Non-existent Account

```bash
curl -X POST http://localhost:8001/api/v1/accounts/9999/activate
```

**Expected Response (404 Not Found)**:
```json
{
  "detail": {
    "error_code": "ACCOUNT_NOT_FOUND",
    "message": "Account 9999 not found"
  }
}
```

✅ **Success**: Got 404 Not Found with `ACCOUNT_NOT_FOUND` error

---

## Scenario 4: Account State Transition Flow

```
Create Account
   ↓
[Account 1000: is_active = false]
   ↓
Activate Account
   ↓
[Account 1000: is_active = true]
   ├─→ Try Activate Again → 409 ALREADY_ACTIVE ✓
   │
   ↓
Inactivate Account
   ↓
[Account 1000: is_active = false]
   ├─→ Try Inactivate Again → 409 ALREADY_INACTIVE ✓
   │
   ↓
Activate Again (Works)
   ↓
[Account 1000: is_active = true]
```

---

## Using Python (Recommended for Automation)

### Test Script

```python
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_activation_exceptions():
    """Test account activation state exceptions."""
    
    # Step 1: Create account
    print("1️⃣  Creating account...")
    response = requests.post(
        f"{BASE_URL}/accounts/savings",
        json={
            "name": "Test User",
            "date_of_birth": "1990-01-15",
            "phone_number": "9876543210",
            "email": "test@example.com",
            "gender": "Male",
            "address": "123 Test St",
            "pin": "9640",
            "initial_balance": 5000.00
        }
    )
    account = response.json()
    account_num = account["account_number"]
    print(f"✅ Account created: {account_num}")
    print(f"   is_active: {account['is_active']}\n")
    
    # Step 2: Activate (first time - should succeed)
    print("2️⃣  Activating account (first time)...")
    response = requests.post(f"{BASE_URL}/accounts/{account_num}/activate")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   Message: {result['message']}\n")
    
    # Step 3: Activate again (should fail with 409)
    print("3️⃣  Activating account again (should fail)...")
    response = requests.post(f"{BASE_URL}/accounts/{account_num}/activate")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    error = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   Error Code: {error['detail']['error_code']}")
    print(f"   Message: {error['detail']['message']}\n")
    
    # Step 4: Inactivate (should succeed)
    print("4️⃣  Inactivating account...")
    response = requests.post(f"{BASE_URL}/accounts/{account_num}/inactivate")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   Message: {result['message']}\n")
    
    # Step 5: Inactivate again (should fail with 409)
    print("5️⃣  Inactivating account again (should fail)...")
    response = requests.post(f"{BASE_URL}/accounts/{account_num}/inactivate")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    error = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   Error Code: {error['detail']['error_code']}")
    print(f"   Message: {error['detail']['message']}\n")
    
    # Step 6: Non-existent account
    print("6️⃣  Activating non-existent account...")
    response = requests.post(f"{BASE_URL}/accounts/9999/activate")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    error = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   Error Code: {error['detail']['error_code']}")
    print(f"   Message: {error['detail']['message']}\n")
    
    print("=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_activation_exceptions()
```

### Run Test

```bash
python test_activation.py
```

**Expected Output**:
```
1️⃣  Creating account...
✅ Account created: 1000
   is_active: false

2️⃣  Activating account (first time)...
✅ Status: 200
   Message: Account activated successfully

3️⃣  Activating account again (should fail)...
✅ Status: 409
   Error Code: ACCOUNT_ALREADY_ACTIVE
   Message: Account 1000 is already active

4️⃣  Inactivating account...
✅ Status: 200
   Message: Account inactivated successfully

5️⃣  Inactivating account again (should fail)...
✅ Status: 409
   Error Code: ACCOUNT_ALREADY_INACTIVE
   Message: Account 1000 is already inactive

6️⃣  Activating non-existent account...
✅ Status: 404
   Error Code: ACCOUNT_NOT_FOUND
   Message: Account 9999 not found

============================================================
🎉 All tests passed!
============================================================
```

---

## Check Logs

While testing, monitor logs in real-time:

### Windows (PowerShell)
```powershell
Get-Content logs/accounts_service.log -Wait
```

### Linux/Mac
```bash
tail -f logs/accounts_service.log
```

**Expected Log Entries**:
```
2025-12-24 13:31:26 - app.repositories.account_repo - INFO - ✅ Savings account created: 1000
2025-12-24 13:31:26 - app.services.account_service - INFO - ✅ Account activated: 1000
2025-12-24 13:31:32 - app.api.accounts - ERROR - ❌ Activate account failed: ACCOUNT_ALREADY_ACTIVE
2025-12-24 13:31:38 - app.services.account_service - INFO - ✅ Account inactivated: 1000
2025-12-24 13:31:44 - app.api.accounts - ERROR - ❌ Inactivate account failed: ACCOUNT_ALREADY_INACTIVE
```

---

## Error Response Format Reference

### 409 Conflict (Already Active)
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_ACTIVE",
    "message": "Account 1000 is already active"
  }
}
```

### 409 Conflict (Already Inactive)
```json
{
  "detail": {
    "error_code": "ACCOUNT_ALREADY_INACTIVE",
    "message": "Account 1000 is already inactive"
  }
}
```

### 404 Not Found
```json
{
  "detail": {
    "error_code": "ACCOUNT_NOT_FOUND",
    "message": "Account 9999 not found"
  }
}
```

---

## Troubleshooting

### Server Not Running
```
Error: Connection refused
Solution: Run uvicorn in another terminal
$ python -m uvicorn app.main:app --reload --port 8001
```

### Database Connection Error
```
Error: could not connect to server
Solution: Verify PostgreSQL is running and .env file has correct credentials
```

### Invalid Account Number
```
Error: must be >= 1000
Solution: Account numbers must be >= 1000 (generated starting from 1000)
```

### Wrong HTTP Status
```
Expected: 409, Got: 400
Solution: Check server logs - may be a different validation error
```

---

## Quick Checklist

- [ ] Server is running on port 8001
- [ ] Database is initialized (ran reset_db.py)
- [ ] .env file has correct PostgreSQL credentials
- [ ] Create an account first (get account_number)
- [ ] Test activate (first time) → should be 200
- [ ] Test activate (second time) → should be 409 ALREADY_ACTIVE
- [ ] Test inactivate (first time) → should be 200
- [ ] Test inactivate (second time) → should be 409 ALREADY_INACTIVE
- [ ] Test with non-existent account → should be 404 NOT_FOUND
- [ ] Check logs for error messages

---

**Status**: ✅ Testing Guide Complete
**Date**: December 24, 2025
**Version**: 1.0.0
