# Accounts Service - Code Analysis

## Overview
The Accounts Service is a FastAPI microservice for managing bank accounts (Savings and Current) with comprehensive validation, encryption, and database operations.

---

## Architecture Layers

### 1. **API Layer** (`app/api/`)
- **accounts.py**: External API endpoints (FastAPI routers)
  - Create savings/current accounts
  - Get account details, balance
  - Update account info
  - Manage account status (activate/inactivate/close)
  
- **internal_accounts.py**: Internal service-to-service API
  - Debit account (withdraw/transfer from)
  - Credit account (deposit/transfer to)
  - Verify PIN
  - Get account details

### 2. **Services Layer** (`app/services/`)
- **account_service.py**: High-level business logic
  - Orchestrates validation + repository
  - Implements business rules
  - Exception handling
  - Logging

**Key Methods:**
```
- create_savings_account(account) → account_number
- create_current_account(account) → account_number
- get_account_details(account_number) → AccountDetailsResponse
- get_balance(account_number) → float
- verify_pin(account_number, pin) → bool
- debit_account(account_number, amount, description) → bool
- credit_account(account_number, amount, description) → bool
- update_account(account_number, update) → bool
- activate_account(account_number) → bool
- inactivate_account(account_number) → bool
- close_account(account_number) → bool
```

### 3. **Repository Layer** (`app/repositories/`)
- **account_repo.py**: Data access (asyncpg - raw SQL, no ORM)
  - CRUD operations on accounts table
  - Debit/credit transactions
  - PIN hash retrieval
  - Account lookups

**Database Tables:**
```
- accounts (main table)
  - account_number (PK, from sequence)
  - account_type (SAVINGS | CURRENT)
  - name, pin_hash, balance, privilege
  - is_active, activated_date, closed_date
  
- savings_account_details
  - account_number (FK to accounts)
  - date_of_birth, gender, phone_no
  
- current_account_details
  - account_number (FK to accounts)
  - company_name, website, registration_no
```

### 4. **Models Layer** (`app/models/`)
- **account.py**: Pydantic models for request/response
  - `SavingsAccountCreate`: Request to create savings account
  - `CurrentAccountCreate`: Request to create current account
  - `AccountUpdate`: Update request
  - `AccountResponse`, `SavingsAccountResponse`, `CurrentAccountResponse`
  - `AccountDetailsResponse`: For service-to-service communication
  - `DebitRequest`, `CreditRequest`: Transaction requests

### 5. **Utils Layer** (`app/utils/`)
- **validators.py**: Business validation rules
  - `validate_age()`: Check age >= 18
  - `validate_pin()`: Check PIN format (4-6 digits, not sequential, not all same)
  - `validate_phone_number()`: Phone number validation
  - `validate_name()`: Name validation
  - `validate_company_name()`: Company name validation
  - `validate_registration_number()`: Registration number validation
  - `validate_privilege()`: Privilege level (PREMIUM, GOLD, SILVER)

- **encryption.py**: PIN/password hashing
  - Uses bcrypt with 12 salt rounds
  - `hash_pin()`, `verify_pin()`
  - `hash_password()`, `verify_password()`

- **helpers.py**: Utility functions
  - `AccountNumberGenerator`: Generates/validates account numbers
  - `mask_account_number()`: Masks account for display

### 6. **Exceptions** (`app/exceptions/`)
- Custom exception hierarchy:
  - `AccountNotFoundError`
  - `AccountInactiveError`, `AccountClosedError`
  - `InsufficientFundsError`
  - `InvalidPinError`
  - `AgeRestrictionError`
  - `DuplicateConstraintError`
  - `DatabaseError`
  - etc.

### 7. **Database** (`app/database/`)
- **db.py**: AsyncPG connection pooling
  - `DatabaseManager` class
  - Async context managers for transactions
  - Connection pool management (min=5, max=20)

### 8. **Config** (`app/config/`)
- **settings.py**: Environment configuration (Pydantic Settings v2)
  - Database URL, credentials
  - JWT config
  - API prefix, host, port
  - Debug mode, log level

- **logging.py**: Logging setup

---

## Business Logic Rules

### Account Creation
**Savings Account:**
- Age must be >= 18 (validated from DOB)
- PIN: 4-6 digits, not all same, not sequential
- Phone number: 10-20 digits
- Name + DOB must be unique
- Initial balance: 0

**Current Account:**
- PIN: 4-6 digits validation
- Registration number must be unique
- Privilege levels: PREMIUM, GOLD, SILVER
- Initial balance: 0

### Account Operations
- **Debit**: Check if account active and not closed, sufficient balance
- **Credit**: Check if account active and not closed
- **PIN Verification**: Compare against bcrypt hash
- **Status Change**: Activate/inactivate only if different state
- **Close**: Can close account regardless of balance (warning if balance > 0)

### Validation Rules
- **Age**: DOB format YYYY-MM-DD, must be >= 18
- **PIN**: 4-6 chars, numeric only, no sequential patterns
- **Phone**: 10-20 digits, numeric only
- **Name**: 1-255 chars
- **Privilege**: PREMIUM | GOLD | SILVER
- **Account Type**: SAVINGS | CURRENT

---

## Data Flow Example: Create Savings Account

```
1. API receives request (accounts.py)
2. Validate request with Pydantic (SavingsAccountCreate)
3. Call service.create_savings_account(account)
   - Validate age (>= 18)
   - Validate PIN format
   - Validate phone number
   - Validate name
   - Hash PIN with bcrypt
4. Call repo.create_savings_account(account, pin_hash)
   - Generate account_number from sequence
   - Insert into accounts table
   - Insert into savings_account_details table
   - Transaction handling
5. Return account_number
```

---

## Console Application Design

### Structure (Proposed)
```
account_service_console_application/
├── main.py (Entry point, CLI menu)
├── app/
│   ├── __init__.py
│   ├── models/
│   │   └── account.py (Same Pydantic models)
│   ├── services/
│   │   └── account_service.py (Same business logic)
│   ├── repositories/
│   │   └── account_repo.py (Modified for sync asyncpg → sqlite3)
│   ├── database/
│   │   └── db.py (SQLite connection management)
│   ├── exceptions/
│   │   └── account_exceptions.py (Same exceptions)
│   ├── utils/
│   │   ├── validators.py (Same validators)
│   │   ├── encryption.py (Same encryption)
│   │   └── helpers.py (Same helpers)
│   └── config/
│       └── settings.py (Same config, modified for SQLite)
├── database/
│   ├── init_db.py (Initialize SQLite schema)
│   └── schema.sql (SQLite schema - adapted from PostgreSQL)
├── ui/
│   ├── __init__.py
│   ├── menu.py (CLI menu system)
│   └── formatter.py (Output formatting)
├── requirements.txt
└── README.md
```

### Key Changes from FastAPI to Console:
1. **Database**: PostgreSQL asyncpg → SQLite3 (sync)
2. **Async**: Remove async/await (use sync SQLite)
3. **API Routes**: Replace with CLI menu system
4. **Request Handling**: Replace HTTP with console input/output
5. **Authentication**: Remove JWT (console is local)
6. **Logging**: Console output instead of logs

### Menu Structure:
```
=== Account Service Console ===

1. Create Account
   1.1 Create Savings Account
   1.2 Create Current Account
   
2. Account Operations
   2.1 View Account Details
   2.2 Check Balance
   2.3 Debit Account
   2.4 Credit Account
   2.5 Update Account
   
3. Account Management
   3.1 Activate Account
   3.2 Inactivate Account
   3.3 Close Account
   
4. PIN Management
   4.1 Verify PIN
   4.2 Update PIN
   
5. Reports
   5.1 List All Accounts
   5.2 Search Accounts
   5.3 Account Statement (by type)
   
6. Exit
```

---

## Code Reusability
- ✅ **100% of business logic** can be reused (services, validators, exceptions)
- ✅ **95% of models** can be reused (Pydantic models work in console)
- ⚠️ **Repository pattern** needs adapter (async → sync, asyncpg → sqlite3)
- ⚠️ **Encryption/Hashing** fully reusable (bcrypt works same way)
- ✅ **Helpers & Utils** fully reusable
- ✅ **Logging** can be reused with console handler

---

## Technology Stack for Console App
- **Language**: Python 3.9+
- **Database**: SQLite3 (built-in, no external dependency)
- **Validation**: Pydantic v2 (same as FastAPI version)
- **Hashing**: bcrypt (same)
- **CLI**: Built-in input/print + colorama (for colored output)
- **Testing**: pytest (same test framework)

---

## Benefits of Reusing Architecture
1. **Code Reusability**: 70-80% of code can be directly reused
2. **Consistency**: Same business logic, validation, error handling
3. **Maintainability**: Single source of truth for rules
4. **Testing**: Same test suite can work for both versions
5. **Quick Development**: Proven patterns and structures
6. **Scalability**: Can sync console app with FastAPI service
