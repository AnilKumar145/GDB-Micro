# Inter-Service Communication Analysis
## Accounts Service ↔ Transactions Service

**Status:** ⚠️  **PARTIALLY CONFIGURED** - Missing Endpoint

---

## Summary

✅ **Transactions Service (Client)** - Well configured  
⚠️  **Accounts Service (Server)** - Missing one endpoint

---

## Communication Flow

```
Transactions Service                    Accounts Service
    ↓                                        ↓
  Client                                   Server
    ↓                                        ↓
account_service_client.py            internal_accounts.py
    ↓                                        ↓
Makes HTTP calls to:                  Receives calls on:
/api/v1/internal/accounts/{id}        ✅ GET  /api/v1/internal/accounts/{id}
/api/v1/internal/accounts/{id}/...    ✅ GET  /api/v1/internal/accounts/{id}/...
```

---

## Endpoint Mapping

### Transaction Service Client (Expecting)
Located: `transactions_service/app/integration/account_service_client.py`

| Method | Client Endpoint | Purpose |
|--------|-----------------|---------|
| ✅ | `/api/v1/accounts/{account_number}` | Get account details |
| ⚠️  | `/api/v1/accounts/{account_number}/validation` | **MISSING IN ACCOUNTS SERVICE** |
| ✅ | `/api/v1/accounts/{account_number}/verify-pin` | Verify PIN |
| ✅ | `/api/v1/accounts/{account_number}/debit` | Debit amount |
| ✅ | `/api/v1/accounts/{account_number}/credit` | Credit amount |
| ✅ | `/api/v1/accounts/{account_number}/privilege` | Get privilege level |

### Accounts Service Server (Available)
Located: `accounts_service/app/api/internal_accounts.py`

| Method | Server Endpoint | Implementation |
|--------|-----------------|-----------------|
| ✅ | `GET /api/v1/internal/accounts/{account_number}` | `get_account_details_internal()` |
| ⚠️  | `GET /api/v1/internal/accounts/{account_number}/validation` | **NOT IMPLEMENTED** |
| ✅ | `GET /api/v1/internal/accounts/{account_number}/privilege` | `get_privilege_internal()` |
| ✅ | `GET /api/v1/internal/accounts/{account_number}/active` | `check_account_active_internal()` |
| ✅ | `POST /api/v1/internal/accounts/{account_number}/verify-pin` | `verify_pin_internal()` |
| ✅ | `POST /api/v1/internal/accounts/{account_number}/debit` | `debit_account_internal()` |
| ✅ | `POST /api/v1/internal/accounts/{account_number}/credit` | `credit_account_internal()` |

---

## Issues Found

### 🔴 **CRITICAL: Missing Endpoint**

**Problem:**
```python
# In transactions_service/app/integration/account_service_client.py, line 37
endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/validation"
```

The Transactions Service is calling:
```
GET /api/v1/accounts/{account_number}/validation
```

But Accounts Service doesn't have this endpoint!

**What it should call instead:**
```
GET /api/v1/internal/accounts/{account_number}  ← This endpoint exists
```

OR

```
GET /api/v1/internal/accounts/{account_number}/active  ← Also suitable
```

---

## Issues Analysis

### Issue #1: Wrong Endpoint Path

**Transactions Service Code (Line 37):**
```python
endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/validation"
```

**Problem:** 
- Uses `/api/v1/accounts/` but Accounts Service has `/api/v1/internal/accounts/`
- Endpoint name `/validation` doesn't exist in Accounts Service
- No `/validation` endpoint defined anywhere

**Accounts Service Available:**
```python
# From internal_accounts.py
@router.get("/accounts/{account_number}")
@router.get("/accounts/{account_number}/privilege")
@router.get("/accounts/{account_number}/active")
@router.post("/accounts/{account_number}/verify-pin")
@router.post("/accounts/{account_number}/debit")
@router.post("/accounts/{account_number}/credit")
```

**Note:** These are registered with prefix `/api/v1/internal/`

---

### Issue #2: Path Prefix Mismatch

**Transactions Service Expects:**
```
http://localhost:8001/api/v1/accounts/{account_number}/validation
```

**Accounts Service Has:**
```
http://localhost:8001/api/v1/internal/accounts/{account_number}
```

**The prefix includes `internal/`** - Transaction service is not including this!

---

## Configuration Status

### ✅ Configuration in Transactions Service

`.env` file has correct Account Service URL:
```properties
ACCOUNTS_SERVICE_URL=http://localhost:8001
ACCOUNT_SERVICE_TIMEOUT=10
```

Client is correctly configured:
```python
self.base_url = settings.ACCOUNT_SERVICE_URL  # http://localhost:8001
self.timeout = settings.ACCOUNT_SERVICE_TIMEOUT  # 10 seconds
```

### ✅ Configuration in Accounts Service

Routes are registered with correct prefix:
```python
app.include_router(
    internal_accounts.router,
    prefix=f"{settings.api_prefix}/internal",  # /api/v1/internal
    tags=["internal"]
)
```

---

## How to Fix

### Option 1: Update Transactions Service (RECOMMENDED)

Change the endpoint from `/api/v1/accounts/` to `/api/v1/internal/accounts/`

**File:** `transactions_service/app/integration/account_service_client.py`

**Current (Line 37):**
```python
endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/validation"
```

**Change to:**
```python
endpoint = f"{self.base_url}/api/v1/internal/accounts/{account_number}"
```

Then use either:
- Get account details directly, OR
- Check active status separately

**New Code:**
```python
async def validate_account(self, account_number: int) -> Dict[str, Any]:
    """Validate account exists and is active."""
    endpoint = f"{self.base_url}/api/v1/internal/accounts/{account_number}"
    
    try:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint)
            
            if response.status_code == 404:
                raise AccountNotFoundException(...)
            
            if response.status_code == 200:
                data = response.json()
                # Check if account is active
                if not data.get("is_active", False):
                    raise AccountNotActiveException(...)
                return data
```

---

### Option 2: Create Validation Endpoint in Accounts Service

Add new endpoint to Accounts Service that combines validation logic.

**New Endpoint** in `accounts_service/app/api/internal_accounts.py`:

```python
@router.get(
    "/accounts/{account_number}/validation",
    tags=["Internal - Validation"],
    summary="Validate Account (Internal)",
    description="Check if account exists and is active"
)
async def validate_account_internal(account_number: int):
    """
    Validate account for transaction processing.
    Returns account details only if active.
    """
    try:
        details = await internal_service.get_account_details(account_number)
        
        if not details.get("is_active", False):
            raise AccountNotActiveException(f"Account inactive")
        
        return {
            "account_number": account_number,
            "is_active": True,
            "balance": details.get("balance"),
            "privilege": details.get("privilege")
        }
    except Exception as e:
        raise HTTPException(...)
```

---

## Summary of Issues

| # | Issue | Severity | Location | Fix |
|---|-------|----------|----------|-----|
| 1 | Wrong endpoint path (`/api/v1/` vs `/api/v1/internal/`) | 🔴 CRITICAL | `account_service_client.py:37` | Update path |
| 2 | Missing `/validation` endpoint | 🔴 CRITICAL | `internal_accounts.py` | Add endpoint OR use existing |
| 3 | Service URL might have `/internal/` inconsistency | 🟡 WARNING | Both services | Verify routing |

---

## What Works

✅ **PIN Verification**
```python
async def verify_pin(self, account_number: int, pin: str) -> bool:
    endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/verify-pin"
```
Will work after fixing validation endpoint.

✅ **Debit/Credit Operations**
```python
async def debit_account(self, ...):
    endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/debit"
```
Will work after fixing base endpoint issue.

✅ **Privilege Level**
```python
async def get_account_privilege(self, account_number: int):
    endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/privilege"
```
Will work after fixing base endpoint issue.

---

## Testing the Communication

### Step 1: Test Accounts Service is Running

```bash
curl http://localhost:8001/health
# Should return: {"status": "healthy", "service": "...", ...}
```

### Step 2: Test Internal Endpoint

```bash
# Get account details
curl http://localhost:8001/api/v1/internal/accounts/1001

# Expected response (200):
{
  "account_number": 1001,
  "account_type": "SAVINGS",
  "name": "John Doe",
  "balance": 50000.00,
  "privilege": "GOLD",
  "is_active": true,
  "activated_date": "2023-01-15T...",
  "closed_date": null
}
```

### Step 3: Test Other Endpoints

```bash
# Get privilege
curl http://localhost:8001/api/v1/internal/accounts/1001/privilege

# Check if active
curl http://localhost:8001/api/v1/internal/accounts/1001/active

# Verify PIN
curl -X POST http://localhost:8001/api/v1/internal/accounts/1001/verify-pin \
  -H "Content-Type: application/json" \
  -d '{"pin": "1234"}'
```

---

## Recommended Fix Priority

### Phase 1: IMMEDIATE (Make services work)
1. Update `account_service_client.py` line 37
   - Change endpoint path from `/api/v1/accounts/` to `/api/v1/internal/accounts/`

### Phase 2: VERIFY
1. Test all endpoints between services
2. Test deposit/withdraw/transfer flows

### Phase 3: OPTIONAL (Better design)
1. Consider creating `/validation` endpoint in Accounts Service for cleaner API
2. Unify endpoint naming across both services

---

## Files Affected

**Need to Update:**
- ✏️  `transactions_service/app/integration/account_service_client.py` - Fix endpoint paths

**No Changes Needed:**
- ✅ `accounts_service/app/api/internal_accounts.py` - Already correct
- ✅ `accounts_service/app/main.py` - Already correct
- ✅ `transactions_service/.env` - Already correct

---

## Detailed Changes Required

### 1. Update account_service_client.py

```python
# BEFORE
endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/validation"

# AFTER  
endpoint = f"{self.base_url}/api/v1/internal/accounts/{account_number}"
```

Also update other endpoint calls to use `/internal/`:

```python
# BEFORE
endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/verify-pin"

# AFTER
endpoint = f"{self.base_url}/api/v1/internal/accounts/{account_number}/verify-pin"
```

All endpoints in `account_service_client.py` should use `/api/v1/internal/accounts/` prefix instead of `/api/v1/accounts/`.

---

## Checklist

- [ ] Accounts Service running on localhost:8001
- [ ] Transactions Service can reach Accounts Service
- [ ] Update endpoint paths in `account_service_client.py`
- [ ] Test validation endpoint call
- [ ] Test PIN verification
- [ ] Test debit/credit operations
- [ ] Test privilege level fetching
- [ ] Run integration tests

---

**Analysis Date:** 2025-12-24
**Status:** Ready for implementation
