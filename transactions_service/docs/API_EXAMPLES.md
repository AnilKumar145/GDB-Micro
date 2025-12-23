# 🔗 Transaction Service - API Examples

**Base URL:** `http://localhost:8002`

---

## 📌 Quick Reference

All endpoints are now **accessible without authentication** (for initial version).

---

## 💸 Withdrawals (FE010)

### Endpoint
```
POST /withdrawals
Content-Type: application/json
```

### Request Example
```json
{
  "account_number": 1001,
  "amount": 5000.00,
  "pin": "1234",
  "description": "ATM Withdrawal"
}
```

### Success Response (200)
```json
{
  "transaction_id": 1,
  "account_number": 1001,
  "amount": 5000.00,
  "status": "SUCCESS",
  "message": "Withdrawal successful",
  "transaction_date": "2025-12-22T10:30:00"
}
```

### Error Response (400)
```json
{
  "detail": "Insufficient funds"
}
```

---

## 💰 Deposits (FE011)

### Endpoint
```
POST /deposits
Content-Type: application/json
```

### Request Example
```json
{
  "account_number": 1001,
  "amount": 10000.00,
  "description": "Salary Deposit"
}
```

### Success Response (200)
```json
{
  "transaction_id": 2,
  "account_number": 1001,
  "amount": 10000.00,
  "status": "SUCCESS",
  "message": "Deposit successful",
  "transaction_date": "2025-12-22T10:35:00"
}
```

---

## 🔄 Transfers (FE012)

### Endpoint
```
POST /transfers
Content-Type: application/json
```

### Request Example
```json
{
  "from_account": 1001,
  "to_account": 1002,
  "amount": 25000.00,
  "transfer_mode": "NEFT",
  "pin": "1234",
  "description": "Payment to vendor"
}
```

### Transfer Modes Supported
- `NEFT` - National Electronic Funds Transfer
- `RTGS` - Real Time Gross Settlement
- `IMPS` - Immediate Payment Service
- `UPI` - Unified Payments Interface
- `CHEQUE` - Cheque-based transfer
- `INTERNAL` - Internal bank transfer

### Success Response (200)
```json
{
  "transaction_id": 3,
  "from_account": 1001,
  "to_account": 1002,
  "amount": 25000.00,
  "transfer_mode": "NEFT",
  "status": "SUCCESS",
  "message": "Transfer successful",
  "daily_limit_remaining": 25000.00
}
```

### Transfer Limits by Privilege
- **PREMIUM:** ₹100,000 per day
- **GOLD:** ₹50,000 per day
- **SILVER:** ₹25,000 per day

---

## 💼 Transfer Limits (FE013)

### Get Account Transfer Limit
```
GET /transfer-limits/{account_number}
```

### Example Request
```
GET /transfer-limits/1001
```

### Success Response (200)
```json
{
  "account_number": 1001,
  "privilege": "GOLD",
  "daily_limit": 50000.00,
  "daily_transaction_count_limit": 30,
  "message": "Transfer limit retrieved successfully"
}
```

---

## 📊 Remaining Daily Limit (FE013)

### Get Remaining Daily Limit
```
GET /transfer-limits/{account_number}/remaining
```

### Example Request
```
GET /transfer-limits/1001/remaining
```

### Success Response (200)
```json
{
  "account_number": 1001,
  "privilege": "GOLD",
  "daily_limit": 50000.00,
  "daily_used": 15000.00,
  "remaining": 35000.00,
  "transaction_count_today": 2,
  "transaction_count_limit": 30,
  "message": "Remaining daily limit retrieved"
}
```

---

## 📋 All Transfer Rules (FE014)

### Get All Transfer Rules
```
GET /transfer-limits/rules/all
```

### Success Response (200)
```json
{
  "rules": [
    {
      "privilege": "PREMIUM",
      "daily_limit": 100000.00,
      "daily_transaction_count_limit": 50
    },
    {
      "privilege": "GOLD",
      "daily_limit": 50000.00,
      "daily_transaction_count_limit": 30
    },
    {
      "privilege": "SILVER",
      "daily_limit": 25000.00,
      "daily_transaction_count_limit": 20
    }
  ],
  "message": "All transfer rules retrieved successfully"
}
```

---

## 📝 Transaction Logs (FE015)

### Get Logs for Specific Transaction
```
GET /transaction-logs/transaction/{transaction_id}
```

### Example Request
```
GET /transaction-logs/transaction/1
```

### Success Response (200)
```json
{
  "transaction_id": 1,
  "logs": [
    {
      "log_id": 1,
      "from_account": 1001,
      "to_account": null,
      "amount": "5000.00",
      "transaction_type": "WITHDRAW",
      "status": "SUCCESS",
      "log_message": "Withdrawal successful",
      "log_file_path": "./logs/transactions/2025-12-22.log",
      "log_date": "2025-12-22T10:30:00"
    }
  ]
}
```

---

## 👤 Account Transaction Logs (FE017)

### Get Paginated Account Logs
```
GET /transaction-logs/account/{account_number}?skip=0&limit=20
```

### Example Request
```
GET /transaction-logs/account/1001?skip=0&limit=10
```

### Success Response (200)
```json
{
  "account_number": 1001,
  "logs": [
    {
      "log_id": 1,
      "transaction_id": 1,
      "from_account": 1001,
      "to_account": null,
      "amount": "5000.00",
      "transaction_type": "WITHDRAW",
      "status": "SUCCESS",
      "log_message": "Withdrawal successful",
      "log_file_path": "./logs/transactions/2025-12-22.log",
      "log_date": "2025-12-22T10:30:00"
    }
  ],
  "total_count": 150,
  "page": 1,
  "page_size": 10,
  "total_pages": 15
}
```

---

## ✅ Successful Transaction Logs (FE019)

### Get Successful Logs
```
GET /transaction-logs/successful?skip=0&limit=20
```

### Example Request
```
GET /transaction-logs/successful?skip=0&limit=10
```

### Success Response (200)
```json
{
  "logs": [
    {
      "log_id": 1,
      "transaction_id": 1,
      "from_account": 1001,
      "to_account": null,
      "amount": "5000.00",
      "transaction_type": "WITHDRAW",
      "status": "SUCCESS",
      "log_message": "Withdrawal successful",
      "log_date": "2025-12-22T10:30:00"
    }
  ],
  "total_count": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

---

## ❌ Failed Transaction Logs

### Get Failed Logs
```
GET /transaction-logs/failed?skip=0&limit=20
```

### Example Request
```
GET /transaction-logs/failed?skip=0&limit=10
```

### Success Response (200)
```json
{
  "logs": [
    {
      "log_id": 5,
      "transaction_id": 5,
      "from_account": 1003,
      "to_account": null,
      "amount": "10000.00",
      "transaction_type": "WITHDRAW",
      "status": "FAILED",
      "log_message": "Insufficient funds",
      "log_date": "2025-12-22T11:15:00"
    }
  ],
  "total_count": 5,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

## 🏥 Health Check

### Endpoint
```
GET /health
```

### Success Response (200)
```json
{
  "status": "healthy",
  "service": "Transaction Service",
  "version": "1.0.0",
  "database": "connected"
}
```

---

## 🔍 Error Responses

### Account Not Found (404)
```json
{
  "detail": "Account not found"
}
```

### Insufficient Funds (400)
```json
{
  "detail": "Insufficient funds in account"
}
```

### Invalid PIN (403)
```json
{
  "detail": "Invalid PIN"
}
```

### Transfer Limit Exceeded (400)
```json
{
  "detail": "Transfer amount exceeds daily limit"
}
```

### Daily Limit Exceeded (400)
```json
{
  "detail": "Daily transfer limit exceeded"
}
```

### Invalid Amount (400)
```json
{
  "detail": "Amount must be greater than 0"
}
```

### Same Account Transfer (400)
```json
{
  "detail": "Cannot transfer to the same account"
}
```

---

## 🧪 cURL Examples

### Health Check
```bash
curl http://localhost:8002/health
```

### Get Transfer Limit
```bash
curl http://localhost:8002/transfer-limits/1001
```

### Withdraw Funds
```bash
curl -X POST http://localhost:8002/withdrawals \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": 1001,
    "amount": 5000.00,
    "pin": "1234",
    "description": "ATM Withdrawal"
  }'
```

### Deposit Funds
```bash
curl -X POST http://localhost:8002/deposits \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": 1001,
    "amount": 10000.00,
    "description": "Salary Deposit"
  }'
```

### Transfer Funds
```bash
curl -X POST http://localhost:8002/transfers \
  -H "Content-Type: application/json" \
  -d '{
    "from_account": 1001,
    "to_account": 1002,
    "amount": 25000.00,
    "transfer_mode": "NEFT",
    "pin": "1234",
    "description": "Payment to vendor"
  }'
```

### Get Account Logs
```bash
curl "http://localhost:8002/transaction-logs/account/1001?skip=0&limit=10"
```

---

## 📊 Pagination

All list endpoints support pagination:

### Parameters
- `skip` (query): Number of records to skip (default: 0)
- `limit` (query): Maximum records to return (default: 20, max: 100)

### Example
```
GET /transaction-logs/account/1001?skip=20&limit=50
```

### Response Structure
```json
{
  "logs": [...],
  "total_count": 150,
  "page": 2,
  "page_size": 50,
  "total_pages": 3
}
```

---

## ⏰ Timestamps

All timestamps are in ISO 8601 format:
```
2025-12-22T10:30:00
```

---

## 📱 Content-Type

All requests must include:
```
Content-Type: application/json
```

---

## 🎯 Rate Limiting

No rate limiting in initial version. To be added in production.

---

## 📞 For More Information

- **Service Documentation:** README.md
- **Setup Guide:** SETUP_COMPLETE.md
- **Implementation Summary:** IMPLEMENTATION_SUMMARY.md
- **Swagger UI:** http://localhost:8002/api/docs
- **ReDoc:** http://localhost:8002/api/redoc

---

**Last Updated:** December 22, 2025  
**Status:** ✅ Ready for Testing
