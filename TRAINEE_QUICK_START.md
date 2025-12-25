# Quick Start Guide for GDB-Micro Banking System

## 🚀 Start Services (5 minutes)

### Step 1: Terminal 1 - Auth Service
```bash
cd auth_service
python setup_db.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004
```
✅ Output: "Uvicorn running on http://0.0.0.0:8004"

### Step 2: Terminal 2 - Users Service
```bash
cd users_service
python setup_db.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```
✅ Output: "Uvicorn running on http://0.0.0.0:8003"

### Step 3: Terminal 3 - Accounts Service
```bash
cd accounts_service
python setup_db.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```
✅ Output: "Uvicorn running on http://0.0.0.0:8001"

### Step 4: Terminal 4 - Transactions Service
```bash
cd transactions_service
python setup_db.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```
✅ Output: "Uvicorn running on http://0.0.0.0:8002"

---

## 📋 Test Services (2 minutes)

### Test All Services
```bash
# In auth_service
python -m pytest tests/ -v

# In users_service
python -m pytest tests/ -v

# In accounts_service
python -m pytest tests/ -v

# In transactions_service
python -m pytest tests/ -v
```

**Expected Result:** ✅ All tests pass (561+ tests)

---

## 🔐 Authentication Flow

### 1. Login to Get JWT Token
```bash
curl -X POST http://localhost:8004/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login_id": "john.doe", "password": "Welcome@1"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1002,
    "login_id": "john.doe",
    "role": "TELLER"
  }
}
```

### 2. Use Token for API Calls
```bash
curl -X GET http://localhost:8003/api/v1/users/1002 \
  -H "Authorization: Bearer <access_token>"
```

---

## 👥 Sample Users (Pre-Configured)

| User ID | Login ID | Password | Role | Privilege |
|---------|----------|----------|------|-----------|
| 1000 | admin.user | Welcome@1 | ADMIN | N/A |
| 1001 | john.teller | Welcome@1 | TELLER | N/A |
| 1002 | jane.smith | Welcome@1 | CUSTOMER | GOLD |
| 1003 | robert.johnson | Welcome@1 | CUSTOMER | SILVER |

---

## 💰 Sample Accounts (Pre-Configured)

| Account # | User | Type | Balance | Privilege | PIN |
|-----------|------|------|---------|-----------|-----|
| 1000 | john.doe | Savings | ₹10,000 | GOLD | 9640 |
| 1001 | jane.smith | Current | ₹50,000 | PREMIUM | 5837 |
| 1002 | admin.user | Savings | ₹1,00,000 | GOLD | 4682 |
| 1003 | robert.johnson | Current | ₹5,000 | SILVER | 1234 |

---

## 🏦 Key Operations

### Create User (ADMIN only)
```bash
curl -X POST http://localhost:8003/api/v1/users \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "login_id": "new.user",
    "username": "New User",
    "email": "new.user@gdb.com",
    "phone": "9876543210",
    "password": "SecurePass123!",
    "role": "CUSTOMER"
  }'
```

### Create Account
```bash
curl -X POST http://localhost:8001/api/v1/accounts/savings \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "account_type": "Savings",
    "user_id": 1004,
    "initial_balance": "25000",
    "pin": "9876"
  }'
```

### Deposit Money
```bash
curl -X POST "http://localhost:8002/api/v1/deposits?account_number=1000&amount=5000" \
  -H "Authorization: Bearer <customer_token>"
```

### Withdraw Money
```bash
curl -X POST "http://localhost:8002/api/v1/withdrawals?account_number=1000&amount=2000&pin=9640" \
  -H "Authorization: Bearer <customer_token>"
```

### Transfer Funds
```bash
curl -X POST "http://localhost:8002/api/v1/transfers?from_account=1000&to_account=1001&amount=5000&pin=9640" \
  -H "Authorization: Bearer <customer_token>"
```

### Check Transfer Limits
```bash
curl -X GET "http://localhost:8002/api/v1/transfer-limits/1000" \
  -H "Authorization: Bearer <customer_token>"
```

### Get Transaction History
```bash
curl -X GET "http://localhost:8002/api/v1/transaction-logs/1000" \
  -H "Authorization: Bearer <customer_token>"
```

---

## 📊 Daily Transaction Limits

| Privilege Level | Daily Limit | Max Transactions |
|-----------------|-------------|------------------|
| PREMIUM | ₹10,00,000 | 50 per day |
| GOLD | ₹5,00,000 | 20 per day |
| SILVER | ₹1,00,000 | 10 per day |

**Note:** Limits reset at 00:00 UTC daily

---

## 🚫 Common Errors & Fixes

### "JWT config not initialized"
✅ **Solution:** Start Auth Service FIRST before other services

### "Connection refused on port 8004"
✅ **Solution:** Check if Auth Service is running on Port 8004

### "Invalid PIN"
✅ **Solution:** PIN must be numeric, 4+ digits, not sequential (1234, 5678 rejected)

### "Insufficient funds"
✅ **Solution:** Account balance must be >= withdrawal amount

### "Daily limit exceeded"
✅ **Solution:** Wait until 00:00 UTC for limit reset, or use different account

### "Zero amount rejected"
✅ **Solution:** Deposit/withdrawal amount must be > 0

---

## 📚 API Documentation URLs

Open in browser:
- **Auth Service:** http://localhost:8004/api/v1/docs
- **Users Service:** http://localhost:8003/api/v1/docs
- **Accounts Service:** http://localhost:8001/api/v1/docs
- **Transactions Service:** http://localhost:8002/api/v1/docs

---

## ✅ Verify Everything is Working

### Health Check Script
```bash
#!/bin/bash

echo "Checking Auth Service..."
curl -s http://localhost:8004/api/v1/docs > /dev/null && echo "✅ Auth Service OK" || echo "❌ Auth Service DOWN"

echo "Checking Users Service..."
curl -s http://localhost:8003/api/v1/docs > /dev/null && echo "✅ Users Service OK" || echo "❌ Users Service DOWN"

echo "Checking Accounts Service..."
curl -s http://localhost:8001/api/v1/docs > /dev/null && echo "✅ Accounts Service OK" || echo "❌ Accounts Service DOWN"

echo "Checking Transactions Service..."
curl -s http://localhost:8002/api/v1/docs > /dev/null && echo "✅ Transactions Service OK" || echo "❌ Transactions Service DOWN"
```

---

## 🎯 Learning Path for Trainees

### Week 1: Setup & Basics
- [ ] Deploy all 4 services
- [ ] Run test suites
- [ ] Test login and token generation
- [ ] Review API documentation

### Week 2: Core Operations
- [ ] Create new users
- [ ] Create accounts
- [ ] Perform deposits/withdrawals
- [ ] Test transfer limits

### Week 3: Inter-Service Communication
- [ ] Study service dependencies
- [ ] Understand JWT flow
- [ ] Review database schemas
- [ ] Test role-based access control

### Week 4: Advanced Topics
- [ ] Implement new features
- [ ] Write custom tests
- [ ] Optimize database queries
- [ ] Add new validations

---

## 🆘 Getting Help

### Documentation Files
- `PRODUCTION_READINESS_ANALYSIS.md` - Comprehensive analysis
- `INTER_SERVICE_COMMUNICATION_ANALYSIS.md` - Service flow
- `accounts_service/docs/COMPREHENSIVE_TEST_SUMMARY.md` - Test details

### Test Files
- Study test files in `tests/` folder for code examples
- Each test file contains docstrings explaining expected behavior

### API Docs
- Interactive docs at `/api/v1/docs` (Swagger UI)
- Try endpoints directly in browser

---

**Status:** ✅ PRODUCTION READY FOR TRAINEES  
**Test Pass Rate:** 100% (561+ tests)  
**Deployment Time:** ~5 minutes  
**Training Duration:** 4 weeks recommended
