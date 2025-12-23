# 🏦 GDB-Micro: Global Digital Bank - Microservices Backend

**Enterprise-Grade FastAPI Microservices Backend for Global Digital Bank**

![Architecture: Microservices](https://img.shields.io/badge/Architecture-Microservices-blue)
![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776ab)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Microservices](#microservices)
- [Quick Start](#quick-start)
- [Database Setup](#database-setup)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Production Deployment](#production-deployment)

---

## 🎯 Overview

**GDB-Micro** is a production-ready microservices backend for the **Global Digital Bank**, implementing:

✅ **True Microservices Architecture**
- 4 independent services with separate databases
- Database-per-service principle
- REST API inter-service communication

✅ **Enterprise-Grade Implementation**
- Raw SQL with asyncpg (no ORM)
- Async/await throughout (FastAPI + asyncpg)
- Proper transaction handling with rollback
- Idempotency keys for at-most-once semantics
- Comprehensive error handling

✅ **Banking Features**
- Account management (Savings/Current)
- Fund transfers with privilege-based limits
- Transaction logging and audit trails
- User management with role-based access
- JWT-based authentication

✅ **Security & Compliance**
- Bcrypt password/PIN hashing
- JWT token management
- Role-based authorization
- GDPR-compliant audit logs
- Secure inter-service communication

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         GDB-Micro Backend                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  REST API Layer (FastAPI)                              │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  /api/v1/accounts/*  |  /api/v1/transactions/*         │   │
│  │  /api/v1/users/*     |  /api/v1/auth/*                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────┐        │
│  │  Accounts    │  │  Transactions   │  │    Users     │        │
│  │   Service    │  │    Service      │  │   Service    │        │
│  │  (Port 8001) │  │  (Port 8002)    │  │ (Port 8003)  │        │
│  └──────────────┘  └─────────────────┘  └──────────────┘        │
│                                                                   │
│  ┌──────────────────┐                                            │
│  │   Auth Service   │                                            │
│  │  (Port 8004)     │                                            │
│  └──────────────────┘                                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Database Layer (PostgreSQL)                      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  gdb_accounts_db  │  gdb_transactions_db                │   │
│  │  gdb_users_db     │  gdb_auth_db                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Service Communication

```
┌──────────────────┐
│  Transactions    │
│    Service       │──→ (HTTP REST) → Accounts Service
│                  │──→ (HTTP REST) → Auth Service
└──────────────────┘
```

Services communicate exclusively via **REST APIs** - no direct database access.

---

## 🔧 Microservices

### 1️⃣ **Accounts Service** (Port 8001)

**Responsibility:** Account creation, management, and balance operations

**Database:** `gdb_accounts_db`

**Key Features:**
- Create Savings/Current accounts
- Manage account lifecycle (activate, inactivate, close)
- Balance management
- PIN verification
- Account privilege enforcement

**Tables:**
- `accounts` - Core account data
- `savings_account_details` - Savings-specific fields
- `current_account_details` - Business account fields
- `account_audit_logs` - Audit trail

**Internal APIs:**
- `GET /internal/accounts/{account_number}` - Fetch account details
- `POST /internal/accounts/{account_number}/debit` - Debit funds
- `POST /internal/accounts/{account_number}/credit` - Credit funds
- `POST /internal/accounts/{account_number}/verify-pin` - Verify PIN

[Detailed Docs →](./accounts_service/README.md)

---

### 2️⃣ **Transactions Service** (Port 8002)

**Responsibility:** Fund transfers, deposits, withdrawals, and transaction logging

**Database:** `gdb_transactions_db`

**Key Features:**
- Withdraw, Deposit, Transfer operations
- Daily transfer limits per privilege level
- Transaction logging and audit
- Inter-service debit/credit coordination

**Privilege-Based Limits:**
- **PREMIUM**: ₹100,000/day, 50 transactions/day
- **GOLD**: ₹50,000/day, 30 transactions/day
- **SILVER**: ₹25,000/day, 20 transactions/day

**Tables:**
- `transactions` - Transaction records
- `daily_transfer_limits` - Per-account daily aggregate
- `transaction_logs` - Audit logs
- `transfer_rules` - Privilege limits

**Public APIs:**
- `POST /api/v1/transactions/withdraw` - Withdraw funds
- `POST /api/v1/transactions/deposit` - Deposit funds
- `POST /api/v1/transactions/transfer` - Transfer between accounts
- `GET /api/v1/transactions/logs/{account_number}` - Transaction history

[Detailed Docs →](./transactions_service/README.md)

---

### 3️⃣ **Users Service** (Port 8003)

**Responsibility:** User management and CRUD operations

**Database:** `gdb_users_db`

**Key Features:**
- User creation and management
- Role-based access control
- Permission management
- User lifecycle management

**Tables:**
- `users` - User accounts
- `user_roles` - Role definitions
- `user_role_mapping` - User-role assignments
- `permissions` - Permission definitions
- `role_permission_mapping` - Role-permission mappings
- `user_audit_logs` - Audit trail

**Public APIs:**
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user details
- `PATCH /api/v1/users/{user_id}` - Update user
- `POST /api/v1/users/{user_id}/inactivate` - Inactivate user

[Detailed Docs →](./users_service/README.md)

---

### 4️⃣ **Auth Service** (Port 8004)

**Responsibility:** Authentication, authorization, and token management

**Database:** `gdb_auth_db`

**Key Features:**
- User authentication
- JWT token issuance and validation
- Token lifecycle management
- Session management
- Login attempt tracking

**Tables:**
- `auth_tokens` - Issued JWT tokens
- `refresh_tokens` - Refresh token storage
- `auth_sessions` - Active sessions
- `login_attempts` - Login audit log
- `token_blacklist` - Revoked tokens
- `password_resets` - Password reset tokens

**Public APIs:**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/verify` - Token verification

[Detailed Docs →](./auth_service/README.md)

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.10+** (for local development)
- **PostgreSQL 14+** (if not using Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd GDB-Micro

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f accounts_service
```

All services will start automatically with databases initialized.

### Option 2: Local Development

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r accounts_service/requirements.txt
pip install -r transactions_service/requirements.txt
pip install -r users_service/requirements.txt
pip install -r auth_service/requirements.txt

# 3. Create PostgreSQL databases
psql -U postgres -c "CREATE DATABASE gdb_accounts_db;"
psql -U postgres -c "CREATE DATABASE gdb_transactions_db;"
psql -U postgres -c "CREATE DATABASE gdb_users_db;"
psql -U postgres -c "CREATE DATABASE gdb_auth_db;"

# 4. Initialize schemas
psql -U postgres gdb_accounts_db < database_schemas/accounts_schema.sql
psql -U postgres gdb_transactions_db < database_schemas/transactions_schema.sql
psql -U postgres gdb_users_db < database_schemas/users_schema.sql
psql -U postgres gdb_auth_db < database_schemas/auth_schema.sql

# 5. Start each service (in separate terminals)
# Terminal 1:
cd accounts_service && python -m uvicorn app.main:app --reload --port 8001

# Terminal 2:
cd transactions_service && python -m uvicorn app.main:app --reload --port 8002

# Terminal 3:
cd users_service && python -m uvicorn app.main:app --reload --port 8003

# Terminal 4:
cd auth_service && python -m uvicorn app.main:app --reload --port 8004
```

---

## 🗄️ Database Setup

### Schema Initialization

All database schemas are in `database_schemas/`:

- `accounts_schema.sql` - Accounts Service schema
- `transactions_schema.sql` - Transactions Service schema
- `users_schema.sql` - Users Service schema
- `auth_schema.sql` - Auth Service schema

**With Docker Compose:** Schemas auto-initialize on startup

**Manual:**
```bash
psql -U gdb_user gdb_accounts_db < database_schemas/accounts_schema.sql
```

### Database URLs

| Service | URL | Port |
|---------|-----|------|
| Accounts | `postgresql://gdb_user:gdb_password@localhost:5432/gdb_accounts_db` | 5432 |
| Transactions | `postgresql://gdb_user:gdb_password@localhost:5433/gdb_transactions_db` | 5433 |
| Users | `postgresql://gdb_user:gdb_password@localhost:5434/gdb_users_db` | 5434 |
| Auth | `postgresql://gdb_user:gdb_password@localhost:5435/gdb_auth_db` | 5435 |

---

## 📚 API Documentation

### Interactive API Docs

Each service provides interactive documentation:

| Service | Swagger UI | ReDoc |
|---------|-----------|-------|
| Accounts | http://localhost:8001/api/v1/docs | http://localhost:8001/api/v1/redoc |
| Transactions | http://localhost:8002/api/v1/docs | http://localhost:8002/api/v1/redoc |
| Users | http://localhost:8003/api/v1/docs | http://localhost:8003/api/v1/redoc |
| Auth | http://localhost:8004/api/v1/docs | http://localhost:8004/api/v1/redoc |

### Health Checks

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

### Example API Calls

#### Create Savings Account
```bash
curl -X POST http://localhost:8001/api/v1/accounts/savings \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "pin": "1234",
    "date_of_birth": "1990-01-15",
    "gender": "M",
    "phone_no": "9876543210",
    "privilege": "GOLD"
  }'
```

#### Create Current Account
```bash
curl -X POST http://localhost:8001/api/v1/accounts/current \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ABC Corporation",
    "pin": "5678",
    "company_name": "ABC Corp Ltd",
    "registration_no": "CIN123456",
    "privilege": "PREMIUM"
  }'
```

#### Get Account Balance
```bash
curl http://localhost:8001/api/v1/accounts/1000/balance
```

#### Transfer Funds
```bash
curl -X POST http://localhost:8002/api/v1/transactions/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_account": 1000,
    "to_account": 1001,
    "amount": 5000.00,
    "pin": "1234",
    "transfer_mode": "NEFT",
    "idempotency_key": "uuid-here"
  }'
```

---

## 💻 Development

### Project Structure

```
GDB-Micro/
├── accounts_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config/
│   │   ├── models/
│   │   ├── api/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── exceptions/
│   │   ├── utils/
│   │   └── database/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── transactions_service/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── users_service/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── auth_service/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── database_schemas/
│   ├── accounts_schema.sql
│   ├── transactions_schema.sql
│   ├── users_schema.sql
│   └── auth_schema.sql
│
├── docker-compose.yml
└── README.md
```

### Code Style

**Format Code:**
```bash
black accounts_service/app transactions_service/app users_service/app auth_service/app
isort accounts_service/app transactions_service/app users_service/app auth_service/app
```

**Lint Code:**
```bash
flake8 accounts_service/app --max-line-length=120
mypy accounts_service/app --ignore-missing-imports
```

### Running Tests

```bash
# Install pytest
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run specific service tests
pytest accounts_service/tests/

# Run with coverage
pytest --cov=app --cov-report=html
```

### Database Migrations

Since we use raw SQL (no ORM):

1. **Create new migration file:**
   ```bash
   # database_schemas/accounts_v2.sql
   ALTER TABLE accounts ADD COLUMN new_column VARCHAR(255);
   ```

2. **Test in development:**
   ```bash
   psql -U gdb_user gdb_accounts_db < database_schemas/accounts_v2.sql
   ```

3. **Deploy to production:**
   - Execute migration script during maintenance window
   - Keep migration history for rollback

---

## 🔐 Security Best Practices

### Environment Variables

**Never commit sensitive data!**

```bash
# .gitignore should contain:
.env
*.log
__pycache__/
.pytest_cache/
```

**Production secrets:**
```bash
# Use environment variables, not .env files
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql://...
export PIN_ENCRYPTION_KEY=$(openssl rand -hex 32)
```

### Pin & Password Hashing

- Uses **bcrypt** with 12 salt rounds
- Time-constant verification (protected against timing attacks)
- Never log or return hashes

### JWT Tokens

- Signed with strong secret key
- Configurable expiration (default: 30 minutes)
- Blacklist mechanism for revocation

### Inter-Service Communication

**Idempotency Keys:**
```python
# Prevents duplicate operations on network retry
idempotency_key = str(uuid.uuid4())  # Unique per request
```

**Service URLs:**
```python
# Use internal docker network names
ACCOUNTS_SERVICE_URL = "http://accounts_service:8001"
```

---

## 📦 Production Deployment

### Docker Image Building

```dockerfile
# Dockerfile for each service
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

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
              name: gdb-secrets
              key: accounts-db-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Environment Configuration

**Development:**
```bash
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
```

**Production:**
```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# Use strong keys
JWT_SECRET_KEY=$(openssl rand -hex 32)
PIN_ENCRYPTION_KEY=$(openssl rand -hex 32)

# Use external database
DATABASE_URL=postgresql://user:pass@prod-db-server:5432/gdb_accounts_db
```

### Monitoring & Logging

**Structured JSON Logging:**
```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
```

**Health Check Endpoints:**
- All services expose `/health` endpoint
- Docker/K8s can monitor service health

### Backup & Recovery

**Database Backups:**
```bash
# Backup
pg_dump -U gdb_user gdb_accounts_db > accounts_backup.sql

# Restore
psql -U gdb_user gdb_accounts_db < accounts_backup.sql
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs accounts_service

# Verify database connection
docker-compose exec accounts_db psql -U gdb_user -d gdb_accounts_db -c "SELECT 1;"

# Restart services
docker-compose restart accounts_service
```

### Database Connection Issues

```bash
# Check if database is healthy
docker-compose ps

# Manually test connection
psql postgresql://gdb_user:gdb_password@localhost:5432/gdb_accounts_db

# Check network
docker network ls
docker network inspect gdb-network
```

### Port Conflicts

```bash
# Check if port is in use
lsof -i :8001

# Use different ports in docker-compose.yml
ports:
  - "9001:8001"  # Changed from 8001
```

---

## 📖 API Reference

See individual service READMEs for detailed API documentation:

- [Accounts Service API](./accounts_service/README.md#api-endpoints)
- [Transactions Service API](./transactions_service/README.md#api-endpoints)
- [Users Service API](./users_service/README.md#api-endpoints)
- [Auth Service API](./auth_service/README.md#api-endpoints)

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push branch: `git push origin feature/amazing-feature`
4. Open Pull Request

### Code Review Checklist

- [ ] Code follows style guide (black, isort)
- [ ] Tests pass (`pytest`)
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No secrets committed

---

## 📝 License

MIT License - See LICENSE file for details

---

## 📞 Support

For questions or issues:

1. Check service-specific README
2. Review API documentation at `/api/v1/docs`
3. Check application logs: `docker-compose logs service-name`
4. Open an issue with error details

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **asyncpg**: https://magicstack.github.io/asyncpg
- **PostgreSQL**: https://www.postgresql.org/docs
- **Docker Compose**: https://docs.docker.com/compose
- **Microservices**: https://microservices.io

---

**Last Updated:** December 20, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
