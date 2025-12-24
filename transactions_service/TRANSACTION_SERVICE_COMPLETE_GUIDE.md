# Transaction Service - Complete Business Logic & Architecture

## Overview

Transaction Service handles all financial transactions (withdrawals, deposits, transfers) with comprehensive business logic, validation, and inter-service communication with the Account Service.

## Architecture

### Layers

```
API Routes (withdraw_routes.py, deposit_routes.py, transfer_routes.py)
         ↓
Service Layer (withdraw_service.py, deposit_service.py, transfer_service.py)
         ↓
Account Service Client (Inter-service HTTP calls)
         ↓
Repository Layer (transaction_repository.py, transaction_log_repository.py)
         ↓
Database & Logging
```

## Business Rules & Validations

### 1. WITHDRAWAL RULES (FE010)

#### Data Elements Required
- `account_number` - Account to withdraw from
- `amount` - Withdrawal amount
- `pin` - Account PIN for verification
- `description` - Optional transaction description

#### Business Logic Flow

```
┌─ Validate Account Exists (via Account Service)
│  └─ GET /api/v1/accounts/{account_number}
│     • Check account exists
│     • Get current balance
│     • Verify account is active (is_active = true)
│
├─ Validate PIN Format
│  └─ Check PIN is 4-6 digits, numeric only
│
├─ Verify PIN (via Account Service)
│  └─ POST /api/v1/accounts/{account_number}/verify-pin
│     • Validate PIN matches stored hash
│
├─ Validate Amount
│  └─ Check amount > 0
│  └─ Check amount ≤ 10,00,000
│
├─ Check Sufficient Balance
│  └─ Verify: current_balance >= amount
│  └─ Raise InsufficientFundsException if insufficient
│
├─ Create Transaction Record (PENDING status)
│  └─ INSERT into fund_transfers with PENDING status
│
├─ Debit Account (via Account Service)
│  └─ POST /api/v1/accounts/{account_number}/debit
│     • Deduct amount from balance
│     • Update last_transaction_date
│
├─ Update Transaction Status (SUCCESS)
│  └─ UPDATE fund_transfers SET status = 'SUCCESS'
│
├─ Log Transaction to Database
│  └─ INSERT into transaction_logging
│
└─ Log to File (rotating logs)
   └─ Write to logs/transactions.log
```

#### Exceptions Raised

| Exception | HTTP Code | Condition |
|-----------|-----------|-----------|
| `AccountNotFoundException` | 404 | Account doesn't exist |
| `AccountNotActiveException` | 400 | Account is inactive (is_active = false) |
| `InvalidPINException` | 401 | PIN format invalid or verification failed |
| `InvalidAmountException` | 400 | Amount invalid (≤0 or >limit) |
| `InsufficientFundsException` | 400 | Balance < withdrawal amount |
| `WithdrawalFailedException` | 500 | Unexpected withdrawal failure |
| `ServiceUnavailableException` | 503 | Account Service unreachable |

#### Example Request/Response

**Request**:
```json
{
  "account_number": 1000,
  "amount": 5000.00,
  "pin": "9640",
  "description": "ATM withdrawal"
}
```

**Success Response (201)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": 1,
  "account_number": 1000,
  "amount": 5000.00,
  "new_balance": 10000.00,
  "transaction_date": "2025-12-24T14:30:00",
  "description": "ATM withdrawal"
}
```

**Error Response (400)**:
```json
{
  "error_code": "INSUFFICIENT_FUNDS",
  "message": "Insufficient balance. Available: ₹3000, Required: ₹5000"
}
```

---

### 2. DEPOSIT RULES (FE011)

#### Data Elements Required
- `account_number` - Account to deposit to
- `amount` - Deposit amount
- `description` - Optional transaction description

#### Business Logic Flow

```
┌─ Validate Account Exists (via Account Service)
│  └─ GET /api/v1/accounts/{account_number}
│     • Check account exists
│     • Get current balance
│     • Verify account is active (is_active = true)
│
├─ Validate Amount
│  └─ Check amount > 0
│  └─ Check amount ≤ 10,00,000
│
├─ Create Transaction Record (PENDING status)
│  └─ INSERT into fund_transfers with PENDING status
│
├─ Credit Account (via Account Service)
│  └─ POST /api/v1/accounts/{account_number}/credit
│     • Add amount to balance
│     • Update last_transaction_date
│
├─ Update Transaction Status (SUCCESS)
│  └─ UPDATE fund_transfers SET status = 'SUCCESS'
│
├─ Log Transaction to Database
│  └─ INSERT into transaction_logging
│
└─ Log to File (rotating logs)
   └─ Write to logs/transactions.log
```

#### Exceptions Raised

| Exception | HTTP Code | Condition |
|-----------|-----------|-----------|
| `AccountNotFoundException` | 404 | Account doesn't exist |
| `AccountNotActiveException` | 400 | Account is inactive |
| `InvalidAmountException` | 400 | Amount invalid |
| `DepositFailedException` | 500 | Unexpected deposit failure |
| `ServiceUnavailableException` | 503 | Account Service unreachable |

#### Example Request/Response

**Request**:
```json
{
  "account_number": 1000,
  "amount": 10000.00,
  "description": "Salary deposit"
}
```

**Success Response (201)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": 2,
  "account_number": 1000,
  "amount": 10000.00,
  "new_balance": 25000.00,
  "transaction_date": "2025-12-24T14:35:00",
  "description": "Salary deposit"
}
```

---

### 3. FUND TRANSFER RULES (FE012)

#### Data Elements Required
- `from_account` - Source account
- `to_account` - Destination account
- `amount` - Transfer amount
- `pin` - Source account PIN
- `transfer_mode` - Transfer mode (NEFT, RTGS, IMPS, UPI, CHEQUE)
- `description` - Optional description

#### Business Logic Flow

```
┌─ Validate Both Accounts Exist (via Account Service)
│  ├─ GET /api/v1/accounts/{from_account}
│  └─ GET /api/v1/accounts/{to_account}
│
├─ Verify Both Accounts Are Active
│  ├─ Check from_account.is_active = true
│  └─ Check to_account.is_active = true
│     └─ Raise AccountNotActiveException if either inactive
│
├─ Validate Accounts Are Different
│  └─ Check from_account ≠ to_account
│     └─ Raise InvalidAmountException if same
│
├─ Validate PIN Format & Verify
│  └─ POST /api/v1/accounts/{from_account}/verify-pin
│
├─ Validate Amount
│  └─ Check amount > 0 and ≤ 10,00,000
│
├─ Check Sufficient Balance
│  └─ Verify: from_account.balance >= amount
│
├─ VALIDATE TRANSFER LIMITS (Per Privilege)
│  ├─ Get from_account.privilege
│  ├─ Apply daily limit:
│  │  ├─ PREMIUM: ₹100,000/day
│  │  ├─ GOLD: ₹50,000/day
│  │  └─ SILVER: ₹25,000/day
│  ├─ Get today's transfers total
│  └─ Raise TransferLimitExceededException if exceeded
│
├─ VALIDATE TRANSACTION COUNT
│  ├─ Get transaction count for today
│  ├─ Check against privilege limit:
│  │  ├─ PREMIUM: 50 txns/day
│  │  ├─ GOLD: 30 txns/day
│  │  └─ SILVER: 20 txns/day
│  └─ Raise TransactionLimitExceededException if exceeded
│
├─ Create Transfer Record (PENDING)
│  └─ INSERT into fund_transfers with PENDING status
│
├─ Debit Source Account (via Account Service)
│  └─ POST /api/v1/accounts/{from_account}/debit
│
├─ Credit Destination Account (via Account Service)
│  └─ POST /api/v1/accounts/{to_account}/credit
│
├─ Update Transfer Status (SUCCESS)
│  └─ UPDATE fund_transfers SET status = 'SUCCESS'
│
├─ Log Transfer to Database
│  └─ INSERT into transaction_logging
│
└─ Log to File
   └─ Write to logs/transactions.log
```

#### Transfer Limits by Privilege

| Privilege | Daily Limit | Txn Limit | Per Txn Max |
|-----------|-------------|-----------|-------------|
| PREMIUM | ₹100,000 | 50 txns | ₹10,00,000 |
| GOLD | ₹50,000 | 30 txns | ₹10,00,000 |
| SILVER | ₹25,000 | 20 txns | ₹10,00,000 |

#### Exceptions Raised

| Exception | HTTP Code | Condition |
|-----------|-----------|-----------|
| `AccountNotFoundException` | 404 | Either account doesn't exist |
| `AccountNotActiveException` | 400 | Either account is inactive |
| `InvalidPINException` | 401 | PIN invalid/verification failed |
| `InvalidAmountException` | 400 | Same account or invalid amount |
| `InsufficientFundsException` | 400 | Balance insufficient |
| `TransferLimitExceededException` | 400 | Daily limit exceeded |
| `TransactionLimitExceededException` | 400 | Transaction count exceeded |
| `TransferFailedException` | 500 | Unexpected failure |
| `ServiceUnavailableException` | 503 | Account Service down |

#### Example Request/Response

**Request**:
```json
{
  "from_account": 1000,
  "to_account": 1001,
  "amount": 5000.00,
  "pin": "9640",
  "transfer_mode": "NEFT",
  "description": "Payment for invoice"
}
```

**Success Response (201)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": 3,
  "from_account": 1000,
  "to_account": 1001,
  "amount": 5000.00,
  "transfer_mode": "NEFT",
  "from_account_new_balance": 5000.00,
  "to_account_new_balance": 15000.00,
  "transaction_date": "2025-12-24T14:40:00"
}
```

**Error Response - Limit Exceeded (400)**:
```json
{
  "error_code": "TRANSFER_LIMIT_EXCEEDED",
  "message": "Daily transfer limit exceeded. Limit: ₹25000, Used: ₹20000, Requested: ₹5000"
}
```

---

## Inter-Service Communication (HTTP Calls to Account Service)

### Account Service Integration

All inter-service calls are made via `account_service_client` to ensure consistency:

#### 1. Get Account Details
```
GET /api/v1/accounts/{account_number}

Response:
{
  "account_number": 1000,
  "name": "John Doe",
  "balance": 15000.00,
  "is_active": true,
  "privilege": "GOLD"
}

Raises:
- 404: Account not found
- 503: Service unavailable
```

#### 2. Verify PIN
```
POST /api/v1/accounts/{account_number}/verify-pin

Request:
{
  "pin": "9640"
}

Response:
{
  "valid": true
}

Raises:
- 400: Invalid PIN
- 401: PIN mismatch
- 404: Account not found
```

#### 3. Debit Account
```
POST /api/v1/accounts/{account_number}/debit

Request:
{
  "amount": 5000.00,
  "description": "Withdrawal"
}

Response:
{
  "new_balance": 10000.00,
  "transaction_date": "2025-12-24T14:30:00"
}

Raises:
- 400: Invalid amount or insufficient balance
- 404: Account not found
```

#### 4. Credit Account
```
POST /api/v1/accounts/{account_number}/credit

Request:
{
  "amount": 5000.00,
  "description": "Deposit"
}

Response:
{
  "new_balance": 20000.00,
  "transaction_date": "2025-12-24T14:35:00"
}

Raises:
- 400: Invalid amount
- 404: Account not found
```

---

## Transaction Logging Rules

### Transaction Log Structure

Every transaction must log these fields:
- `id` - Primary key (BIGSERIAL)
- `amount` - Transaction amount
- `transaction_type` - WITHDRAW, DEPOSIT, or TRANSFER
- `created_at` - Timestamp
- `updated_at` - Timestamp

### Logging Strategy

#### 1. Database Logging
```sql
INSERT INTO transaction_logging (amount, transaction_type, created_at, updated_at)
VALUES (5000.00, 'WITHDRAW', NOW(), NOW());
```

#### 2. File-Based Logging
```
logs/transactions.log
2025-12-24 14:30:00,123 - app.services.withdraw_service - INFO - ✅ Withdrawal successful for account 1000
2025-12-24 14:30:00,124 - app.repositories.transaction_log_repository - INFO - 📝 Transaction logged: WITHDRAW, ₹5000
```

---

## Custom Exceptions

### Exception Hierarchy

```
TransactionException (Base)
├── AccountNotFoundException
├── AccountNotActiveException
├── InvalidAmountException
├── InvalidPINException
├── InsufficientFundsException
├── WithdrawalFailedException
├── DepositFailedException
├── TransferFailedException
├── TransferLimitExceededException
├── TransactionLimitExceededException
└── ServiceUnavailableException
```

### Exception Details

Each exception includes:
- `error_code` - Unique error identifier
- `message` - User-friendly error message
- `http_code` - HTTP status code (400, 401, 404, 500, 503)

---

## Validation Layer

### AmountValidator
- Validates withdrawal/deposit amounts (1 to 10,00,000)
- Ensures decimal precision (2 decimal places max)

### BalanceValidator
- Checks sufficient balance for withdrawal/transfer
- Validates balance doesn't exceed max value

### PINValidator
- Checks PIN format (4-6 digits, numeric)
- Validates PIN structure

### LimitValidator
- Validates daily transfer limits per privilege
- Checks transaction count limits
- Tracks daily totals

---

## Repository Layer

### TransactionRepository
- `create_transaction()` - Create new transaction record
- `update_transaction_status()` - Update transaction status
- `get_transaction()` - Retrieve transaction details
- `get_daily_transfers()` - Get today's transfers for limit check
- `get_today_transaction_count()` - Count transactions for today

### TransactionLogRepository
- `log_to_database()` - Write to transaction_logging table
- `log_to_file()` - Write to rotating log file
- `get_transaction_logs()` - Query transaction history

---

## Error Handling

### Graceful Degradation
1. Validates all inputs before making external calls
2. Catches service-level exceptions
3. Logs all errors with context
4. Returns meaningful error messages

### Retry Strategy
- Implements idempotency keys for failed transactions
- Allows safe retry without duplicate processing
- Tracks idempotency keys in transaction_logging

### Circuit Breaker Pattern
- Detects Account Service unavailability
- Returns 503 Service Unavailable
- Allows clients to handle gracefully

---

## Files Structure

```
app/
├── api/
│   ├── withdraw_routes.py      - Withdrawal endpoints
│   ├── deposit_routes.py       - Deposit endpoints
│   └── transfer_routes.py      - Transfer endpoints
├── services/
│   ├── withdraw_service.py     - Withdrawal business logic
│   ├── deposit_service.py      - Deposit business logic
│   └── transfer_service.py     - Transfer business logic
├── repositories/
│   ├── transaction_repository.py    - Fund transfer DB ops
│   └── transaction_log_repository.py - Logging ops
├── exceptions/
│   └── transaction_exceptions.py    - Custom exceptions
├── integration/
│   └── account_service_client.py    - Inter-service calls
├── validation/
│   └── validators.py           - Business logic validators
└── models/
    ├── enums.py               - TransactionType, TransferMode, PrivilegeLevel
    ├── transaction.py         - FundTransfer models
    ├── request_models.py      - API request models
    └── response_models.py     - API response models
```

---

## Testing Scenarios

### Withdrawal Tests
- ✅ Successful withdrawal with valid PIN
- ✅ Fail with account inactive
- ✅ Fail with insufficient funds
- ✅ Fail with invalid PIN
- ✅ Fail with invalid amount

### Deposit Tests
- ✅ Successful deposit
- ✅ Fail with account inactive
- ✅ Fail with invalid amount

### Transfer Tests
- ✅ Successful transfer with valid privilege
- ✅ Fail when daily limit exceeded
- ✅ Fail when transaction count exceeded
- ✅ Fail with insufficient balance
- ✅ Fail with same source/destination
- ✅ Fail with inactive account

---

**Status**: ✅ Complete Architecture
**Date**: December 24, 2025
**Version**: 1.0.0
