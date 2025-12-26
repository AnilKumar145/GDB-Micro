# Account Service Console Application

A professional console-based account management system for Global Digital Bank. Built with the same business logic, validation rules, and architecture as the FastAPI microservice, but optimized for local CLI usage.

## Features

### Account Creation
- **Savings Account**: Age verification (18+), PIN validation, phone number validation
- **Current Account**: Company registration validation, unique registration number
- Support for multiple privilege levels (PREMIUM, GOLD, SILVER)

### Account Operations
- View account details (balance, status, privilege level, etc.)
- Check account balance
- Debit account (Withdraw with PIN verification)
- Credit account (Deposit funds)
- Update account information
- PIN verification

### Account Management
- Activate/Inactivate accounts
- Close accounts
- Account status management

### Reporting & Analytics
- List all accounts with pagination
- Search accounts by name or account number
- Account statistics (total balance, active accounts, account type breakdown)

### Security Features
- PIN hashing with bcrypt (12 salt rounds)
- PIN validation rules (4-6 digits, not sequential, not all same)
- Age validation for savings accounts
- Account status checks for transactions

## Architecture

### Layers

#### 1. **Models** (`app/models/`)
- Pydantic-like data classes for requests and responses
- Account models for Savings and Current accounts
- Transaction request/response models

#### 2. **Services** (`app/services/`)
- `AccountService`: High-level business logic
  - Account creation with validation
  - Account operations (debit, credit, balance check)
  - Account management (activate, inactivate, close)
  - Account queries and searches

#### 3. **Repository** (`app/repositories/`)
- `AccountRepository`: Data access layer
  - SQLite operations (CRUD)
  - Transaction management
  - Account lookups and searches

#### 4. **Database** (`app/database/`)
- PostgreSQL connection management using asyncpg
- Async/sync bridge for console compatibility
- Transaction support with context managers
- Connection pooling simulation

#### 5. **Utils** (`app/utils/`)
- **validators.py**: Business validation rules
  - Age validation, PIN validation, phone validation
  - Name, company name, registration number validation
  - Privilege level validation
  
- **encryption.py**: PIN/Password hashing
  - bcrypt-based hashing and verification
  
- **helpers.py**: Utility functions
  - Account number generation/validation
  - Currency formatting
  - Date/time formatting
  - Account number masking

#### 6. **Exceptions** (`app/exceptions/`)
- Custom exception hierarchy
- Banking-specific error codes
- Detailed error messages

#### 7. **UI** (`ui/`)
- **formatter.py**: Console output formatting
  - Colored output support
  - Account/transaction formatting
  - Receipt generation
  
- **menu.py**: Interactive CLI menu system
  - Main menu navigation
  - Input validation
  - Error handling

### Database Schema

**SQLite Tables:**

```sql
-- Accounts table
CREATE TABLE accounts (
    account_number INTEGER PRIMARY KEY,
    account_type TEXT CHECK (account_type IN ('SAVINGS', 'CURRENT')),
    name TEXT NOT NULL,
    pin_hash TEXT NOT NULL,
    balance REAL DEFAULT 0.0,
    privilege TEXT CHECK (privilege IN ('PREMIUM', 'GOLD', 'SILVER')),
    is_active INTEGER DEFAULT 1,
    activated_date TEXT,
    closed_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Savings account details
CREATE TABLE savings_account_details (
    account_number INTEGER PRIMARY KEY,
    date_of_birth TEXT NOT NULL,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Others')),
    phone_no TEXT NOT NULL,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);

-- Current account details
CREATE TABLE current_account_details (
    account_number INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    website TEXT,
    registration_no TEXT NOT NULL UNIQUE,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone/Navigate to project directory:**
   ```bash
   cd account_service_console_application
   ```

2. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

The application will automatically create the SQLite database (`accounts.db`) and initialize the schema on first run.

## Usage

### Main Menu Options

```
1. CREATE ACCOUNT
   ├── Create Savings Account
   └── Create Current Account

2. ACCOUNT OPERATIONS
   ├── View Account Details
   ├── Check Balance
   ├── Debit Account (Withdrawal)
   ├── Credit Account (Deposit)
   └── Update Account

3. ACCOUNT MANAGEMENT
   ├── Activate Account
   ├── Inactivate Account
   └── Close Account

4. PIN MANAGEMENT
   └── Verify PIN

5. REPORTS & SEARCH
   ├── List All Accounts
   ├── Search Accounts
   └── Account Statistics

6. EXIT
```

### Example Workflows

#### Create a Savings Account
```
1. Select "Create Account" → "Create Savings Account"
2. Enter:
   - Name: John Doe
   - DOB: 1995-05-15 (must be 18+)
   - Gender: Male
   - Phone: 9876543210
   - PIN: 1234 (4-6 digits, not sequential)
   - Privilege: GOLD
3. Account created successfully with auto-generated account number
```

#### Debit Account
```
1. Select "Account Operations" → "Debit Account"
2. Enter:
   - Account Number: 1000
   - Amount: 5000
   - PIN: 1234 (verification)
3. Transaction succeeds, new balance shown
```

#### Search Accounts
```
1. Select "Reports & Search" → "Search Accounts"
2. Enter search term:
   - By name: "John" (case-insensitive)
   - By account number: "1000"
3. Matching accounts displayed
```

## Validation Rules

### PIN
- Length: 4-6 digits
- Must be numeric only
- Cannot be all same digits (1111, 2222)
- Cannot be sequential (1234, 4321, 0123)

### Phone Number (Savings Accounts)
- Length: 10-20 digits
- Must be numeric only

### Age (Savings Accounts)
- Minimum: 18 years old
- Format: YYYY-MM-DD

### Privilege Levels
- PREMIUM, GOLD, SILVER

### Account Types
- SAVINGS: Individual savings accounts
- CURRENT: Business current accounts

## Business Logic

### Account Creation Validation
- **Savings**: Age ≥ 18, valid DOB, unique name+DOB combination
- **Current**: Valid registration number (must be unique)

### Transaction Validation
- Account must be active
- Account must not be closed
- Debit: Sufficient balance required
- Credit: Only requires active account

### Account Status
- **Active**: Can perform transactions
- **Inactive**: Cannot debit/credit
- **Closed**: Cannot perform any transactions

## Configuration

Settings can be configured via environment variables in `.env` file:

```env
APP_NAME=Account Service Console
APP_VERSION=1.0.0
ENVIRONMENT=development
DATABASE_PATH=accounts.db
BCRYPT_ROUNDS=12
LOG_LEVEL=INFO
ENABLE_COLORS=true
```

## Logging

Application logs are written to:
- **File**: `console_app.log`
- **Console**: Standard output with configured log level

Log format: `timestamp - logger_name - level - message`

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_account_service.py

# Verbose output
pytest -v
```

## Code Structure Comparison

### FastAPI Version vs Console Version

| Aspect | FastAPI | Console |
|--------|---------|---------|
| Framework | FastAPI | Stdlib only |
| Database | asyncpg + PostgreSQL | sqlite3 |
| Async | Full async/await | Sync operations |
| API | HTTP REST endpoints | CLI menu system |
| Authentication | JWT tokens | None (local app) |
| Input validation | Pydantic | Custom validators |
| HTTP Middleware | CORS, TrustedHost | N/A |

### Code Reusability

- ✅ **100%** Business logic (services, validation rules)
- ✅ **95%** Models (converted to simple classes)
- ✅ **90%** Exceptions (same hierarchy, same error codes)
- ✅ **85%** Utils (validators, encryption, helpers)
- ⚠️ **50%** Repository (adapted from async asyncpg to sync sqlite3)
- ❌ **0%** API layer (CLI replaces HTTP)

## Future Enhancements

- [ ] Transaction history/audit log
- [ ] Export accounts to CSV
- [ ] Batch account operations
- [ ] Interest calculation for savings accounts
- [ ] Monthly statement generation
- [ ] PIN change functionality
- [ ] Database backup/restore utilities
- [ ] Performance analytics
- [ ] Concurrent account access (threading)
- [ ] Web-based console (Flask/FastAPI wrapper)

## Troubleshooting

### Database Lock
If you get "database is locked" error:
1. Close all other instances of the application
2. Delete `accounts.db` and restart (will recreate schema)

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### PIN Verification Fails
- Check PIN hasn't changed
- Ensure bcrypt is installed: `pip install bcrypt`
- Verify account number is correct

## Contributing

Follow the existing code structure and patterns when adding features:
1. Add business logic to `AccountService`
2. Add repository methods to `AccountRepository`
3. Add menu options to `Menu` class
4. Add validators if needed
5. Write tests in `tests/` directory

## License

© 2024 Global Digital Bank. All rights reserved.

## Support

For issues or questions, contact the development team.

---

**Built with ❤️ by GDB Architecture Team**
