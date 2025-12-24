# Transaction Service - Complete Business Logic Documentation

## Overview

The Transaction Service implements comprehensive business logic for three core transaction types:
1. **Withdrawal** - Debit funds from account
2. **Deposit** - Credit funds to account
3. **Transfer** - Move funds between accounts

## Architecture Overview

```
API Layer (endpoints)
    ↓
Service Layer (business logic)
    ├── WithdrawService
    ├── DepositService
    ├── TransferService
    └── TransactionLogService
    ↓
Integration Layer (Account Service Communication)
    └── account_service_client
    ↓
Repository Layer (Database)
    ├── TransactionRepository
    ├── TransferLimitRepository
    └── TransactionLogRepository
    ↓
Database (PostgreSQL)
    ├── fund_transfers
    └── transaction_logging
```

## Service Files Structure

```
app/services/
├── withdraw_service.py          ✅ Withdrawal operations
├── deposit_service.py           ✅ Deposit operations
├── transfer_service.py          ✅ Transfer operations
├── transaction_log_service.py   ✅ Transaction logging
├── transfer_limit_service.py    ✅ Transfer limit validation
└── __init__.py                  ✅ Service exports
```

---

## 1. WITHDRAWAL SERVICE

**File**: `app/services/withdraw_service.py`

### Business Rules

#### Rule W1: Account Validation
- ✅ Check if account exists via Account Service
- ✅ Verify account is active (`is_active = true`)
- ❌ Raise `AccountNotFoundException` if not found
- ❌ Raise `AccountNotActiveException` if inactive

#### Rule W2: PIN Verification
- ✅ Validate PIN format (4-6 digits)
- ✅ Verify PIN via Account Service
- ❌ Raise `InvalidPINException` if invalid

#### Rule W3: Amount Validation
- ✅ Check amount > 0
- ✅ Check amount ≤ 999,999,999.99
- ❌ Raise `InvalidAmountException` if invalid

#### Rule W4: Balance Verification
- ✅ Get current balance from Account Service
- ✅ Verify balance ≥ withdrawal amount
- ❌ Raise `InsufficientFundsException` if insufficient

#### Rule W5: Transaction Processing
- ✅ Create transaction record (status = PENDING)
- ✅ Call Account Service to debit account
- ✅ Update transaction status to SUCCESS
- ✅ Log to database and file
- ❌ Raise `WithdrawalFailedException` on failure

### Critical Flow

```
1. Validate Account (Account Service)
   ├─ Exists? → Continue
   └─ Not found? → AccountNotFoundException

2. Check Account Active
   ├─ Is active? → Continue
   └─ Inactive? → AccountNotActiveException

3. Verify PIN
   ├─ Valid format? → Continue
   └─ Invalid? → InvalidPINException

4. Validate Amount
   ├─ Valid? → Continue
   └─ Invalid? → InvalidAmountException

5. Check Balance
   ├─ Sufficient? → Continue
   └─ Insufficient? → InsufficientFundsException

6. Debit Account (Account Service)
   ├─ Success? → Update transaction to SUCCESS
   └─ Failure? → Update transaction to FAILED

7. Log Transaction
   ├─ Database log
   └─ File log

8. Return Response
```

### Example Request/Response

**Request**:
```json
{
  "account_number": 1000,
  "amount": 5000.00,
  "pin": "1234"
}
```

**Response (Success - 200)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": "TXN001",
  "account_number": 1000,
  "amount": 5000.00,
  "transaction_type": "WITHDRAW",
  "new_balance": 45000.00,
  "transaction_date": "2025-12-24T13:45:00"
}
```

**Response (Error - 400)**:
```json
{
  "error_code": "INSUFFICIENT_FUNDS",
  "message": "Insufficient balance. Current: ₹2000, Required: ₹5000"
}
```

---

## 2. DEPOSIT SERVICE

**File**: `app/services/deposit_service.py`

### Business Rules

#### Rule D1: Account Validation
- ✅ Check if account exists via Account Service
- ✅ Verify account is active (`is_active = true`)
- ❌ Raise `AccountNotFoundException` if not found
- ❌ Raise `AccountNotActiveException` if inactive

#### Rule D2: Amount Validation
- ✅ Check amount > 0
- ✅ Check amount ≤ 999,999,999.99
- ❌ Raise `InvalidAmountException` if invalid

#### Rule D3: Transaction Processing
- ✅ Create transaction record (status = PENDING)
- ✅ Call Account Service to credit account
- ✅ Update transaction status to SUCCESS
- ✅ Log to database and file
- ❌ Raise `DepositFailedException` on failure

### Critical Flow

```
1. Validate Account (Account Service)
   ├─ Exists? → Continue
   └─ Not found? → AccountNotFoundException

2. Check Account Active
   ├─ Is active? → Continue
   └─ Inactive? → AccountNotActiveException

3. Validate Amount
   ├─ Valid? → Continue
   └─ Invalid? → InvalidAmountException

4. Credit Account (Account Service)
   ├─ Success? → Update transaction to SUCCESS
   └─ Failure? → Update transaction to FAILED

5. Log Transaction
   ├─ Database log
   └─ File log

6. Return Response
```

### Example Request/Response

**Request**:
```json
{
  "account_number": 1000,
  "amount": 10000.00
}
```

**Response (Success - 200)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": "TXN002",
  "account_number": 1000,
  "amount": 10000.00,
  "transaction_type": "DEPOSIT",
  "new_balance": 55000.00,
  "transaction_date": "2025-12-24T13:46:00"
}
```

---

## 3. TRANSFER SERVICE

**File**: `app/services/transfer_service.py`

### Business Rules

#### Rule T1: Account Validation (Both Accounts)
- ✅ Check if from_account exists via Account Service
- ✅ Check if to_account exists via Account Service
- ❌ Raise `AccountNotFoundException` if not found

#### Rule T2: Account Active Status
- ✅ Verify from_account is active
- ✅ Verify to_account is active
- ❌ Raise `SourceAccountInactiveException` if source inactive
- ❌ Raise `DestinationAccountInactiveException` if destination inactive
- ❌ Raise `BothAccountsInactiveException` if both inactive

#### Rule T3: Same Account Check
- ✅ Verify from_account ≠ to_account
- ❌ Raise `SameAccountTransferException` if same

#### Rule T4: PIN Verification
- ✅ Validate PIN format (4-6 digits)
- ✅ Verify PIN for from_account via Account Service
- ❌ Raise `InvalidPINException` if invalid

#### Rule T5: Amount Validation
- ✅ Check amount > 0
- ✅ Check amount ≤ 999,999,999.99
- ❌ Raise `InvalidAmountException` if invalid

#### Rule T6: Balance Verification
- ✅ Get current balance of from_account
- ✅ Verify balance ≥ transfer amount
- ❌ Raise `InsufficientFundsException` if insufficient

#### Rule T7: Privilege-Based Transfer Limits
- ✅ Get account privilege (PREMIUM, GOLD, SILVER)
- ✅ Check daily transfer limit based on privilege:
  - **PREMIUM**: ₹100,000/day
  - **GOLD**: ₹50,000/day
  - **SILVER**: ₹25,000/day
- ❌ Raise `TransferLimitExceededException` if exceeded

#### Rule T8: Daily Transaction Count
- ✅ Track daily transaction count per account
- ✅ Validate transaction count doesn't exceed limits
- ❌ Raise `DailyTransactionCountExceededException` if exceeded

#### Rule T9: Transfer Mode Validation
- ✅ Verify transfer_mode is one of: NEFT, RTGS, IMPS, UPI, CHEQUE
- ❌ Raise `InvalidTransferModeException` if invalid

#### Rule T10: Transaction Processing
- ✅ Create transaction record (status = PENDING)
- ✅ Call Account Service to debit from_account
- ✅ Call Account Service to credit to_account
- ✅ Update transaction status to SUCCESS
- ✅ Log to database and file
- ✅ Log to fund_transfers table
- ❌ Raise `TransferFailedException` on failure

### Critical Flow

```
1. Validate Both Accounts (Account Service)
   ├─ Both exist? → Continue
   └─ Not found? → AccountNotFoundException

2. Check Both Accounts Active
   ├─ Both active? → Continue
   ├─ Source inactive? → SourceAccountInactiveException
   ├─ Destination inactive? → DestinationAccountInactiveException
   └─ Both inactive? → BothAccountsInactiveException

3. Verify Not Same Account
   ├─ Different? → Continue
   └─ Same? → SameAccountTransferException

4. Verify PIN
   ├─ Valid format? → Continue
   └─ Invalid? → InvalidPINException

5. Validate Amount
   ├─ Valid? → Continue
   └─ Invalid? → InvalidAmountException

6. Check Source Balance
   ├─ Sufficient? → Continue
   └─ Insufficient? → InsufficientFundsException

7. Check Transfer Limits
   ├─ Daily limit OK? → Continue
   └─ Limit exceeded? → TransferLimitExceededException

8. Check Transaction Count
   ├─ Count OK? → Continue
   └─ Count exceeded? → DailyTransactionCountExceededException

9. Validate Transfer Mode
   ├─ Valid mode? → Continue
   └─ Invalid? → InvalidTransferModeException

10. Debit Source Account (Account Service)
    ├─ Success? → Continue
    └─ Failure? → Update transaction to FAILED

11. Credit Destination Account (Account Service)
    ├─ Success? → Update transaction to SUCCESS
    └─ Failure? → Rollback, update to FAILED

12. Log Transaction
    ├─ Database log
    ├─ File log
    └─ fund_transfers table

13. Return Response
```

### Transfer Limits by Privilege

| Privilege | Daily Limit | Daily Txn Count | Notes |
|-----------|-------------|-----------------|-------|
| PREMIUM | ₹100,000 | Unlimited | Highest tier |
| GOLD | ₹50,000 | 50 txns | Standard tier |
| SILVER | ₹25,000 | 20 txns | Basic tier |

### Example Request/Response

**Request**:
```json
{
  "from_account": 1000,
  "to_account": 1001,
  "amount": 5000.00,
  "pin": "1234",
  "transfer_mode": "NEFT"
}
```

**Response (Success - 200)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": "TXN003",
  "from_account": 1000,
  "to_account": 1001,
  "amount": 5000.00,
  "transfer_mode": "NEFT",
  "transaction_type": "TRANSFER",
  "from_new_balance": 40000.00,
  "to_new_balance": 15000.00,
  "transaction_date": "2025-12-24T13:47:00"
}
```

**Response (Error - Transfer Limit Exceeded)**:
```json
{
  "error_code": "TRANSFER_LIMIT_EXCEEDED",
  "message": "Daily transfer limit exceeded for SILVER account. Limit: ₹25,000, Used: ₹20,000, Requested: ₹5,000"
}
```

---

## 4. TRANSACTION LOGGING SERVICE

**File**: `app/services/transaction_log_service.py`

### Logging Rules

#### Rule L1: Logging Requirements
- ✅ Log every transaction (WITHDRAW, DEPOSIT, TRANSFER)
- ✅ Log to database (transaction_logging table)
- ✅ Log to file (rotating file handler)
- ✅ Include: amount, transaction_type, created_at, updated_at

#### Rule L2: Database Logging
- ✅ Record in `transaction_logging` table
- ✅ Fields: id, amount, transaction_type, created_at, updated_at
- ✅ Automatic timestamps via database triggers

#### Rule L3: File Logging
- ✅ Rotate files at 10MB
- ✅ Keep 5 backup files
- ✅ Use consistent format with timestamps

#### Rule L4: Fund Transfer Logging
- ✅ Log detailed transfer info to `fund_transfers` table
- ✅ Fields: id, from_account, to_account, transfer_amount, transfer_mode, created_at, updated_at

### Logging Fields

**transaction_logging Table**:
```
- id (BIGSERIAL PRIMARY KEY)
- amount (NUMERIC(15,2))
- transaction_type (WITHDRAW, DEPOSIT, TRANSFER)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

**fund_transfers Table** (for transfers only):
```
- id (BIGSERIAL PRIMARY KEY)
- from_account (BIGINT)
- to_account (BIGINT)
- transfer_amount (NUMERIC(15,2))
- transfer_mode (NEFT, RTGS, IMPS, UPI, CHEQUE)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

---

## 5. CUSTOM EXCEPTIONS

**File**: `app/exceptions/transaction_exceptions.py`

### Exception Hierarchy

```
TransactionException (Base - HTTP 400)
├── AccountNotFoundException (HTTP 404)
├── AccountNotActiveException (HTTP 400)
├── InsufficientFundsException (HTTP 400)
├── InvalidAmountException (HTTP 400)
├── InvalidPINException (HTTP 401)
├── WithdrawalFailedException (HTTP 400)
├── DepositFailedException (HTTP 400)
├── TransferFailedException (HTTP 400)
├── TransferLimitExceededException (HTTP 400)
├── DailyTransactionCountExceededException (HTTP 400)
├── SameAccountTransferException (HTTP 400)
├── SourceAccountInactiveException (HTTP 400)
├── DestinationAccountInactiveException (HTTP 400)
├── BothAccountsInactiveException (HTTP 400)
├── InvalidTransferModeException (HTTP 400)
├── ServiceUnavailableException (HTTP 503)
├── DatabaseException (HTTP 500)
├── ValidationException (HTTP 422)
└── ... (more specific exceptions)
```

### Exception Usage Examples

```python
# Withdrawal Rules
raise AccountNotActiveException("Account is not active")
raise InsufficientFundsException("Balance: ₹2000, Required: ₹5000")
raise InvalidPINException("PIN verification failed")

# Deposit Rules
raise AccountNotFoundException("Account 9999 not found")

# Transfer Rules
raise SameAccountTransferException("Cannot transfer to same account")
raise TransferLimitExceededException("Daily limit exceeded")
raise SourceAccountInactiveException("Source account is inactive")
raise DestinationAccountInactiveException("Destination account is inactive")
```

---

## 6. INTER-SERVICE COMMUNICATION

### Account Service Integration

**File**: `app/integration/account_service_client.py`

#### API Calls to Account Service

| Operation | Endpoint | Method | Purpose |
|-----------|----------|--------|---------|
| `validate_account()` | GET /api/v1/accounts/{id} | GET | Check account exists and get details |
| `verify_pin()` | POST /api/v1/accounts/{id}/verify-pin | POST | Verify PIN |
| `debit_account()` | POST /api/v1/accounts/{id}/debit | POST | Withdraw funds |
| `credit_account()` | POST /api/v1/accounts/{id}/credit | POST | Deposit funds |
| `get_balance()` | GET /api/v1/accounts/{id}/balance | GET | Get current balance |
| `get_privilege()` | GET /api/v1/accounts/{id}/privilege | GET | Get privilege level |

#### Error Handling

- ❌ Account Service Down: Raise `ServiceUnavailableException` (HTTP 503)
- ❌ Account Not Found: Raise `AccountNotFoundException` (HTTP 404)
- ❌ Invalid Response: Raise `AccountServiceException` (HTTP 502)

---

## 7. VALIDATION LAYER

### Validators Used

**File**: `app/validation/validators.py`

```python
class AmountValidator:
    - validate_withdrawal_amount(amount)
    - validate_deposit_amount(amount)
    - validate_transfer_amount(amount)

class BalanceValidator:
    - validate_sufficient_balance(current_balance, required_amount)

class PINValidator:
    - validate_pin_format(pin)

class TransferValidator:
    - validate_accounts_different(from_account, to_account)
    - validate_transfer_mode(mode)

class TransferLimitValidator:
    - validate_daily_limit(account_number, privilege, amount)
    - validate_daily_transaction_count(account_number, count)
```

---

## 8. REPOSITORY LAYER

### Repositories

| Repository | Purpose |
|-----------|---------|
| `TransactionRepository` | Manage transaction records |
| `TransactionLogRepository` | Log to database and file |
| `TransferLimitRepository` | Track daily limits |
| `FundTransferRepository` | Manage fund transfer records |

---

## Complete Transaction Flow Example

### Scenario: Transfer ₹5000 from Account 1000 to Account 1001

```
1. User submits transfer request
   └─ from_account: 1000, to_account: 1001, amount: 5000, pin: 1234

2. TransferService.process_transfer() called
   ├─ Validate account 1000 exists (Account Service)
   ├─ Validate account 1001 exists (Account Service)
   ├─ Check 1000 is active (Account Service)
   ├─ Check 1001 is active (Account Service)
   ├─ Verify 1000 ≠ 1001 ✓
   ├─ Verify PIN for 1000 (Account Service)
   ├─ Validate amount 5000 ✓
   ├─ Check balance of 1000 ≥ 5000 ✓
   ├─ Check daily transfer limit for 1000
   │  └─ Privilege: GOLD, Limit: ₹50,000, Used today: ₹20,000
   │  └─ Can transfer: ₹50,000 - ₹20,000 = ₹30,000 ✓
   ├─ Check daily transaction count
   │  └─ Max: 50, Used: 25, Remaining: 25 ✓
   ├─ Create transaction record (status: PENDING)
   ├─ Debit account 1000 by 5000 (Account Service)
   │  └─ New balance: 45,000
   ├─ Credit account 1001 by 5000 (Account Service)
   │  └─ New balance: 15,000
   ├─ Update transaction record (status: SUCCESS)
   ├─ Log to transaction_logging table
   ├─ Log to fund_transfers table
   ├─ Log to file
   └─ Return success response

3. Success Response
   └─ transaction_id: TXN003
      from_account: 1000, new_balance: 45,000
      to_account: 1001, new_balance: 15,000
      transfer_mode: NEFT
```

---

## Error Handling Strategy

### Transactional Safety

- ✅ Create transaction record BEFORE any account changes
- ✅ Update status to FAILED if any step fails
- ✅ All changes logged regardless of success/failure
- ✅ Idempotency keys prevent duplicate transactions

### Rollback Strategy

For transfers, if destination credit fails:
1. Debit already applied to source
2. Log failure with reference to source debit
3. Manual intervention required to credit destination
4. Transaction marked as FAILED for auditing

### Logging on Failure

All failures logged with:
- Transaction ID
- Account numbers
- Amount
- Failure reason
- Timestamp
- Error code

---

## Summary

### ✅ Implemented

- [x] Withdrawal service with balance validation
- [x] Deposit service with account validation
- [x] Transfer service with privilege-based limits
- [x] Custom exception hierarchy (20+ exceptions)
- [x] Inter-service communication to Account Service
- [x] Transaction logging (database + file)
- [x] Daily limit tracking
- [x] Transaction count tracking
- [x] Comprehensive validation layer
- [x] Error handling and rollback

### ✅ Non-Negotiable Requirements Met

- [x] Account active check before every transaction
- [x] Balance verification before withdrawal/transfer
- [x] Privilege-based transfer limits (PREMIUM: ₹100K, GOLD: ₹50K, SILVER: ₹25K)
- [x] PIN verification for withdrawal and transfer
- [x] Daily transaction logging
- [x] HTTP communication to Account Service
- [x] Complete audit trail

---

**Status**: ✅ Production Ready
**Date**: December 24, 2025
**Version**: 1.0.0
