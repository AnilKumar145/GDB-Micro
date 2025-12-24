# Accounts Service - Global Digital Bank (GDB)

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Requirements](#requirements)
4. [Features](#features)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [API Endpoints](#api-endpoints)
8. [Database Schema](#database-schema)
9. [Data Models](#data-models)
10. [Error Handling](#error-handling)
11. [Testing](#testing)
12. [Deployment](#deployment)

---

## 📌 Overview

The **Accounts Service** is a microservice within the Global Digital Bank (GDB) ecosystem, responsible for managing all account-related operations. It provides core banking functionalities including:

- **Account Management**: Create and manage savings and current accounts
- **Account Activation**: Activate accounts with PIN verification
- **Balance Management**: Track account balances with precision
- **Inter-service Communication**: Debit/credit operations for transactions
- **Pin Verification**: Secure PIN-based authentication
- **Account Status Management**: Activate, deactivate, and close accounts

**Service Port**: `8001`
**API Prefix**: `/api/v1`

---

## 🏗️ Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT / API GATEWAY                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌────▼────┐  ┌───▼──────┐
   │ Accounts │  │  Trx    │  │  Users   │
   │ Service  │  │ Service │  │ Service  │
   │ (8001)   │  │ (8002)  │  │ (8003)   │
   └────┬────┘  └────┬────┘  └───┬──────┘
        │            │            │
   ┌────▼────────────▼────────────▼────┐
   │      PostgreSQL Database           │
   │  ┌─────────────────────────────┐   │
   │  │  accounts_db                │   │
   │  │  transactions_db            │   │
   │  │  users_db                   │   │
   │  └─────────────────────────────┘   │
   └────────────────────────────────────┘
```

### Microservice Architecture - Accounts Service

```
┌──────────────────────────────────────────────────────────────────┐
│                      ACCOUNTS SERVICE (8001)                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 🌐 API Layer (FastAPI)                                      │  │
│  │  ├─ POST   /api/v1/accounts/savings          (Create)       │  │
│  │  ├─ POST   /api/v1/accounts/current          (Create)       │  │
│  │  ├─ GET    /api/v1/accounts/{account_no}     (Fetch)        │  │
│  │  ├─ POST   /api/v1/accounts/{account_no}/activate (Activate)│  │
│  │  ├─ POST   /api/v1/accounts/{account_no}/deactivate         │  │
│  │  ├─ POST   /api/v1/accounts/{account_no}/close             │  │
│  │  ├─ POST   /api/v1/accounts/{account_no}/pin/verify         │  │
│  │  ├─ GET    /api/v1/accounts/{account_no}/balance            │  │
│  │  └─ Internal APIs (Service-to-Service)                       │  │
│  │     ├─ GET    /api/v1/internal/accounts/validate             │  │
│  │     ├─ POST   /api/v1/internal/accounts/debit                │  │
│  │     ├─ POST   /api/v1/internal/accounts/credit               │  │
│  │     └─ POST   /api/v1/internal/accounts/transfer-debit/credit│  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────▼────────────────────────────────┐  │
│  │ 🔧 Service Layer (Business Logic)                           │  │
│  │  ├─ AccountService (account_service.py)                    │  │
│  │  │  ├─ create_savings_account()                            │  │
│  │  │  ├─ create_current_account()                            │  │
│  │  │  ├─ activate_account()                                  │  │
│  │  │  ├─ deactivate_account()                                │  │
│  │  │  ├─ close_account()                                     │  │
│  │  │  ├─ debit_account()                                     │  │
│  │  │  ├─ credit_account()                                    │  │
│  │  │  └─ verify_pin()                                        │  │
│  │  │                                                          │  │
│  │  └─ InternalAccountService (internal_service.py)           │  │
│  │     ├─ get_account_details()                               │  │
│  │     ├─ debit_for_transfer()                                │  │
│  │     ├─ credit_for_transfer()                               │  │
│  │     └─ verify_account_pin()                                │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 📦 Repository Layer (Data Access)                           │  │
│  │  └─ AccountRepository (account_repo.py)                    │  │
│  │     ├─ create_savings_account()                            │  │
│  │     ├─ create_current_account()                            │  │
│  │     ├─ get_account()                                       │  │
│  │     ├─ get_account_balance()                               │  │
│  │     ├─ activate_account()                                  │  │
│  │     ├─ deactivate_account()                                │  │
│  │     ├─ close_account()                                     │  │
│  │     ├─ debit_account()                                     │  │
│  │     └─ credit_account()                                    │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 🔐 Utilities & Validators                                   │  │
│  │  ├─ encryption.py          (PIN hashing)                    │  │
│  │  ├─ validators.py          (Input validation)               │  │
│  │  └─ helpers.py             (Utilities)                      │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 💾 Database Layer (asyncpg)                                 │  │
│  │  ├─ Connection Pooling                                      │  │
│  │  ├─ Transaction Management                                  │  │
│  │  └─ Query Execution                                         │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PostgreSQL DB    │
                    │  (accounts_db)     │
                    └────────────────────┘
```

### Layered Architecture Details

#### 1. **API Layer** (`app/api/`)
- **Public API** (`accounts.py`): REST endpoints for external clients
- **Internal API** (`internal_accounts.py`): Endpoints for inter-service communication
- Framework: FastAPI with dependency injection
- Middleware: CORS, TrustedHost, error handling

#### 2. **Service Layer** (`app/services/`)
- **AccountService**: High-level business logic
  - Account creation with validation
  - Account lifecycle management (activate/deactivate/close)
  - Debit/credit operations with idempotency
  - PIN verification
  
- **InternalAccountService**: Inter-service communication layer
  - Called by Transactions Service for debit/credit
  - Provides account validation and details
  - Implements idempotency keys

#### 3. **Repository Layer** (`app/repositories/`)
- **AccountRepository**: Data access abstraction
- Raw SQL with asyncpg (no ORM)
- Implements CRUD operations
- Type-safe database interactions
- Connection pool management

#### 4. **Data Models** (`app/models/`)
- Pydantic v2 models for request/response validation
- Type safety with Field descriptors
- Custom validators for business rules

#### 5. **Exception Layer** (`app/exceptions/`)
- Custom exception hierarchy
- Error codes for external communication
- Detailed error messages

#### 6. **Utilities** (`app/utils/`)
- **encryption.py**: PIN hashing with bcrypt
- **validators.py**: Input validation (age, PIN, phone, etc.)
- **helpers.py**: Account number generation, utilities

#### 7. **Configuration** (`app/config/`)
- **settings.py**: Environment-based configuration
- **logging.py**: Structured logging setup
- Support for development/staging/production

#### 8. **Database** (`app/database/`)
- **db.py**: asyncpg connection pool management
- Lifecycle management (init/close)
- Query execution helpers

---

## 📦 Requirements

### System Requirements
- **Python**: 3.9+
- **PostgreSQL**: 12.0+
- **asyncpg**: For async PostgreSQL driver
- **FastAPI**: 0.104.1+
- **uvicorn**: ASGI server

### Python Dependencies

```
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3

# Database
asyncpg==0.29.0
sqlalchemy==2.0.23  # For async utilities

# Security & Encryption
bcrypt==4.1.1
python-jose[cryptography]==3.3.0
cryptography==41.0.7

# HTTP Client (Inter-service communication)
httpx==0.25.1
aiohttp==3.9.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Logging & Monitoring
python-json-logger==2.0.7

# Development & Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.12.1
flake8==6.1.0
isort==5.13.2
mypy==1.7.1

# Environment Management
python-dotenv==1.0.0
```

### Database Requirements
- PostgreSQL database with the following tables:
  - `accounts`: Main account table
  - `savings_account_details`: Savings-specific details
  - `current_account_details`: Current account-specific details
  - `account_pins`: PIN storage (hashed)

---

## ✨ Features

### 1. Account Creation
- **Savings Accounts**: For individuals (age >= 18)
  - Name, DOB, Gender, Phone, Privilege level
  - Unique constraint on name + DOB
  - Auto-generated account number starting from 1000
  
- **Current Accounts**: For businesses/organizations
  - Company name, registration number, website
  - Unique registration number constraint
  - Similar privilege levels as savings

### 2. Account Management
- **Activation**: Verify PIN before account activation
- **Deactivation**: Prevent operations on inactive accounts
- **Closure**: Permanently close accounts
- **Status Tracking**: Active/Inactive/Closed states

### 3. Balance Operations
- **Debit**: Withdraw or transfer funds with sufficient balance check
- **Credit**: Deposit or receive transferred funds
- **Balance Query**: Get current balance in real-time
- **Type Safety**: Decimal precision for currency (₹)

### 4. Security
- **PIN Hashing**: bcrypt with salt
- **PIN Format Validation**: 4-6 digits, no sequential/repeated digits
- **Privilege Levels**: SILVER, GOLD, PREMIUM
- **Account Verification**: Ensure account existence and status

### 5. Inter-service Communication
- **Idempotency Keys**: At-most-once semantics for retry safety
- **Internal APIs**: Service-to-service endpoints
- **Transactions Service Integration**: For debit/credit operations
- **Error Propagation**: Consistent error codes across services

### 6. Logging & Monitoring
- Structured JSON logging
- Transaction audit trail
- Comprehensive error tracking
- Request/response logging

---

## 🚀 Installation & Setup

### 1. Prerequisites
```bash
# Verify Python version
python --version  # Should be 3.9+

# Verify PostgreSQL
psql --version  # Should be 12+
```

### 2. Clone & Navigate
```bash
cd accounts_service
```

### 3. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Database
```bash
# Initialize database
python setup_db.py

# Or manually:
# 1. Create PostgreSQL database: gdb_accounts_db
# 2. Run: database_schemas/accounts_schema.sql
```

### 6. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings:
DATABASE_URL=postgresql://user:password@localhost:5432/gdb_accounts_db
PIN_ENCRYPTION_KEY=your-secret-key
LOG_LEVEL=INFO
```

### 7. Run Application
```bash
# Development
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Production
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8001 app.main:app
```

### 8. Verify Service
```bash
# Health check
curl http://localhost:8001/health

# API docs
open http://localhost:8001/api/v1/docs
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Application
APP_NAME=GDB-Accounts-Service
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8001

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gdb_accounts_db
MIN_DB_POOL_SIZE=5
MAX_DB_POOL_SIZE=20

# Security
PIN_ENCRYPTION_KEY=your-secret-encryption-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/accounts_service.log

# Inter-service URLs
AUTH_SERVICE_URL=http://localhost:8004
TRANSACTIONS_SERVICE_URL=http://localhost:8002
USERS_SERVICE_URL=http://localhost:8003

# API
API_PREFIX=/api/v1
```

---

## 📡 API Endpoints

### Account Creation

#### Create Savings Account
```http
POST /api/v1/accounts/savings
Content-Type: application/json

{
  "name": "John Doe",
  "pin": "1234",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "phone_no": "9876543210",
  "privilege": "GOLD"
}
```

**Response (201 Created)**:
```json
{
  "account_number": 1001,
  "account_type": "SAVINGS",
  "name": "John Doe",
  "balance": 0.00,
  "privilege": "GOLD",
  "is_active": true,
  "activated_date": "2024-12-24T10:00:00",
  "closed_date": null
}
```

#### Create Current Account
```http
POST /api/v1/accounts/current
Content-Type: application/json

{
  "name": "Tech Company Ltd",
  "pin": "5678",
  "company_name": "Tech Company Ltd",
  "website": "https://techcompany.com",
  "registration_no": "REG123456",
  "privilege": "PREMIUM"
}
```

### Account Operations

#### Get Account Details
```http
GET /api/v1/accounts/1001
```

**Response (200 OK)**:
```json
{
  "account_number": 1001,
  "account_type": "SAVINGS",
  "name": "John Doe",
  "balance": 50000.00,
  "privilege": "GOLD",
  "is_active": true,
  "activated_date": "2024-12-24T10:00:00",
  "closed_date": null
}
```

#### Activate Account
```http
POST /api/v1/accounts/1001/activate
Content-Type: application/json

{
  "pin": "1234"
}
```

#### Get Account Balance
```http
GET /api/v1/accounts/1001/balance
```

**Response**:
```json
{
  "account_number": 1001,
  "balance": 50000.00,
  "currency": "INR"
}
```

### Internal APIs (Service-to-Service)

#### Validate Account
```http
GET /api/v1/internal/accounts/validate?account_number=1001
```

#### Debit Account
```http
POST /api/v1/internal/accounts/debit
Content-Type: application/json

{
  "account_number": 1001,
  "amount": 1000.00,
  "description": "Fund Transfer",
  "idempotency_key": "uuid-string"
}
```

#### Credit Account
```http
POST /api/v1/internal/accounts/credit
Content-Type: application/json

{
  "account_number": 1001,
  "amount": 5000.00,
  "description": "Fund Deposit",
  "idempotency_key": "uuid-string"
}
```

---

## 💾 Database Schema

### Accounts Table
```sql
CREATE TABLE accounts (
  account_number INT PRIMARY KEY,
  account_type VARCHAR(20) NOT NULL,  -- SAVINGS or CURRENT
  name VARCHAR(255) NOT NULL,
  balance NUMERIC(15, 2) DEFAULT 0.00,
  privilege VARCHAR(20) DEFAULT 'SILVER',  -- SILVER, GOLD, PREMIUM
  is_active BOOLEAN DEFAULT TRUE,
  activated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  closed_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Savings Account Details Table
```sql
CREATE TABLE savings_account_details (
  id SERIAL PRIMARY KEY,
  account_number INT UNIQUE,
  date_of_birth DATE NOT NULL,
  gender VARCHAR(20) NOT NULL,
  phone_no VARCHAR(20) NOT NULL,
  FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);
```

### Current Account Details Table
```sql
CREATE TABLE current_account_details (
  id SERIAL PRIMARY KEY,
  account_number INT UNIQUE,
  company_name VARCHAR(255) NOT NULL,
  website VARCHAR(255),
  registration_no VARCHAR(50) UNIQUE NOT NULL,
  FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);
```

### Account PINs Table
```sql
CREATE TABLE account_pins (
  id SERIAL PRIMARY KEY,
  account_number INT UNIQUE,
  pin_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);
```

---

## 🔍 Data Models

### Request Models

#### SavingsAccountCreate
```python
{
  "name": str (1-255 chars),
  "pin": str (4-6 digits),
  "date_of_birth": str (YYYY-MM-DD),
  "gender": "Male" | "Female" | "Others",
  "phone_no": str (10-20 digits),
  "privilege": "SILVER" | "GOLD" | "PREMIUM" (default: SILVER)
}
```

#### CurrentAccountCreate
```python
{
  "name": str (1-255 chars),
  "pin": str (4-6 digits),
  "company_name": str (1-255 chars),
  "website": str (optional),
  "registration_no": str (1-50 chars, unique),
  "privilege": "SILVER" | "GOLD" | "PREMIUM" (default: SILVER)
}
```

### Response Models

#### AccountResponse
```python
{
  "account_number": int,
  "account_type": "SAVINGS" | "CURRENT",
  "name": str,
  "balance": float,
  "privilege": "SILVER" | "GOLD" | "PREMIUM",
  "is_active": bool,
  "activated_date": datetime,
  "closed_date": datetime | null
}
```

---

## ⚠️ Error Handling

### Error Response Format
```json
{
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message"
}
```

### Common Error Codes

| Error Code | Status | Meaning |
|---|---|---|
| `ACCOUNT_NOT_FOUND` | 404 | Account does not exist |
| `ACCOUNT_ALREADY_EXISTS` | 400 | Account with name+DOB exists |
| `ACCOUNT_INACTIVE` | 400 | Account is not active |
| `ACCOUNT_CLOSED` | 400 | Account is closed |
| `INSUFFICIENT_FUNDS` | 400 | Balance insufficient for transaction |
| `INVALID_PIN` | 400 | PIN is invalid or incorrect |
| `INVALID_AGE` | 400 | Age must be >= 18 |
| `INVALID_PRIVILEGE` | 400 | Invalid privilege level |
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Files
- **test_api.py**: API endpoint tests
- **test_basic.py**: Basic functionality tests
- **test_services.py**: Business logic tests
- **test_repository.py**: Data access layer tests
- **test_models_validators.py**: Model validation tests
- **test_integration.py**: End-to-end integration tests

### Test Coverage
- ✅ 169+ automated tests
- ✅ Unit tests for all layers
- ✅ Integration tests
- ✅ Error scenario testing
- ✅ Edge case coverage

---

## 📦 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: accounts-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: accounts-service
  template:
    metadata:
      labels:
        app: accounts-service
    spec:
      containers:
      - name: accounts-service
        image: gdb/accounts-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: accounts-db-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Environment-specific Deployment

**Development**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Staging**:
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8001 app.main:app
```

**Production**:
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8001 \
  --access-logfile - --error-logfile - app.main:app
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8001/api/v1/docs
- **ReDoc**: http://localhost:8001/api/v1/redoc
- **Health Check**: http://localhost:8001/health
- **Database Schema**: `database_schemas/accounts_schema.sql`
- **Configuration Template**: `.env.example`

---

## 🤝 Contributing

### Code Style
- Use Black for formatting: `black app/`
- Use isort for imports: `isort app/`
- Run linting: `flake8 app/`

### Before Committing
```bash
black app/
isort app/
flake8 app/
pytest tests/
```

---

## 📝 License

Copyright © 2024 Global Digital Bank (GDB). All rights reserved.

---

## 📞 Support

For issues, questions, or support:
- Create an issue in the repository
- Contact: support@gdb.local
- Documentation: Check docs/ folder

---

**Last Updated**: December 24, 2024
**Version**: 1.0.0
**Maintainer**: GDB Architecture Team
