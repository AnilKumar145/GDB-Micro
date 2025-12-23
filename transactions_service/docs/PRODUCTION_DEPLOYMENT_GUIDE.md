# 🚀 Production Deployment Checklist & Configuration Guide

## Quick Start: What to Do NOW

```
⏱️ Estimated Time: 2-3 weeks to production
🎯 Critical Items: 7 (Must complete before deployment)
⚠️ High Priority Items: 8 (Should complete before deployment)
```

---

## CRITICAL ITEMS (DO FIRST ⚠️ REQUIRED)

### 1. Enable Authentication & Authorization

**File:** `transactions_service/app/main.py`

**Current Status:** Security code exists but is DISABLED

**Action:**

```python
# UNCOMMENT these imports at the top of main.py
from app.security.jwt_dependency import verify_token
from app.security.role_guard import require_role

# UNCOMMENT these dependencies on ALL endpoint functions:
@app.post("/api/v1/deposits")
async def deposit(
    account_number: int,
    amount: Decimal,
    description: str,
    current_user: dict = Depends(verify_token),  # ← UNCOMMENT THIS
    _: None = Depends(require_role(["CUSTOMER", "TELLER"]))  # ← UNCOMMENT THIS
):
    """Deposit funds (requires authentication)."""
    pass

# Repeat for ALL endpoints:
# - POST /api/v1/deposits
# - POST /api/v1/withdrawals
# - POST /api/v1/transfers
# - GET /transfer-limits/{privilege_level}
# - GET /transaction-logs/{account_number}
```

**Verification:**
```bash
# This should fail without valid token
curl -X POST http://localhost:8002/api/v1/deposits \
  -H "Content-Type: application/json" \
  -d '{"account_number": 1001, "amount": 100, "description": "test"}'
# Expected: 403 Unauthorized

# This should succeed with valid token
curl -X POST http://localhost:8002/api/v1/deposits \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"account_number": 1001, "amount": 100, "description": "test"}'
# Expected: 200 OK
```

**Estimated Time:** 30 minutes

---

### 2. Implement Rate Limiting

**File:** Create `transactions_service/app/middleware/rate_limiter.py`

**Step 1:** Install package
```bash
pip install slowapi
```

**Step 2:** Create rate limiter configuration
```python
# app/middleware/rate_limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

async def rate_limit_error_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "error_code": "RATE_LIMIT_EXCEEDED"
        }
    )
```

**Step 3:** Update `app/main.py`
```python
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)

# Apply limits to endpoints
@app.post("/api/v1/deposits")
@limiter.limit("50/hour")  # 50 deposits per hour per IP
async def deposit(...):
    pass

@app.post("/api/v1/withdrawals")
@limiter.limit("30/hour")  # 30 withdrawals per hour per IP
async def withdraw(...):
    pass

@app.post("/api/v1/transfers")
@limiter.limit("20/hour")  # 20 transfers per hour per IP
async def transfer(...):
    pass
```

**Testing:**
```bash
# Test rate limit by making 51 requests in quick succession
for i in {1..51}; do
  curl -X POST http://localhost:8002/api/v1/deposits \
    -H "Content-Type: application/json" \
    -d '{"account_number": 1001, "amount": 100, "description": "test"}'
done

# 51st request should return 429 Too Many Requests
```

**Estimated Time:** 45 minutes

---

### 3. Implement JSON Structured Logging

**File:** `transactions_service/app/utils/logging_config.py`

**Step 1:** Install package
```bash
pip install python-json-logger
```

**Step 2:** Create logging configuration
```python
# app/utils/logging_config.py
import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path

def setup_structured_logging(service_name: str, log_level: str = "INFO"):
    """Configure JSON structured logging."""
    
    # Create logs directory
    log_dir = Path("./logs/transactions")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # File handler for JSON logs
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_dict = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": service_name,
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            if record.exc_info:
                log_dict["exception"] = self.formatException(record.exc_info)
            
            # Add custom fields if present
            if hasattr(record, 'transaction_id'):
                log_dict['transaction_id'] = record.transaction_id
            if hasattr(record, 'account_number'):
                log_dict['account_number'] = record.account_number
            if hasattr(record, 'duration_ms'):
                log_dict['duration_ms'] = record.duration_ms
            
            return json.dumps(log_dict)
    
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.json.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger
```

**Step 3:** Update `app/main.py`
```python
import logging
from app.utils.logging_config import setup_structured_logging

# Configure logging at startup
logger = setup_structured_logging(
    service_name="transactions-service",
    log_level=os.getenv("LOG_LEVEL", "INFO")
)

@app.on_event("startup")
async def startup_event():
    logger.info("Transaction Service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Transaction Service shutting down")
```

**Verification:**
```bash
# Check logs directory
ls -la logs/transactions/

# View JSON logs
cat logs/transactions/app.json.log | jq '.'
```

**Estimated Time:** 1 hour

---

### 4. Enable HTTPS/TLS (Production Environment)

**Option A: Using Let's Encrypt with certbot**

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate for your domain
sudo certbot certonly --standalone -d api.yourdomain.com

# Update app to use SSL
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8002 \
  --ssl-keyfile /etc/letsencrypt/live/api.yourdomain.com/privkey.pem \
  --ssl-certfile /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
```

**Option B: Using self-signed certificate (Development)**

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem \
  -keyout key.pem \
  -days 365

# Start with SSL
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8002 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem
```

**Verification:**
```bash
# Test HTTPS
curl -k https://localhost:8002/health
# Should return health check status
```

**Estimated Time:** 30 minutes

---

### 5. Configure Security Headers Middleware

**File:** `transactions_service/app/middleware/security_headers.py`

**Create middleware:**
```python
# app/middleware/security_headers.py
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = "accelerometer=(), microphone=(), camera=()"
        
        return response
```

**Add to main.py:**
```python
from app.middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

**Verification:**
```bash
curl -I http://localhost:8002/health
# Should see security headers in response
```

**Estimated Time:** 30 minutes

---

### 6. Set Up Monitoring with Prometheus

**File:** Create `transactions_service/app/monitoring/metrics.py`

**Step 1:** Install packages
```bash
pip install prometheus-client
```

**Step 2:** Create metrics configuration
```python
# app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# Transaction metrics
transactions_total = Counter(
    'transactions_total',
    'Total transactions processed',
    ['type', 'status']
)

transaction_amount = Histogram(
    'transaction_amount_total',
    'Transaction amounts',
    ['type'],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000)
)

# Database metrics
db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Active database connections'
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type']
)
```

**Step 3:** Add metrics endpoint to main.py
```python
from prometheus_client import make_asgi_app
from starlette.routing import Mount

# Add Prometheus endpoint at /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", Mount(metrics_app, name="metrics"))
```

**Step 4:** Instrument endpoints
```python
from app.monitoring.metrics import transactions_total, transaction_amount
import time

@app.post("/api/v1/deposits")
async def deposit(account_number: int, amount: Decimal, description: str):
    """Deposit funds."""
    start_time = time.time()
    
    try:
        # Your deposit logic here
        result = await transfer_service.deposit(account_number, amount, description)
        
        # Record metrics
        transactions_total.labels(type="deposit", status="success").inc()
        transaction_amount.labels(type="deposit").observe(float(amount))
        
        return result
    except Exception as e:
        transactions_total.labels(type="deposit", status="error").inc()
        raise
    finally:
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method="POST",
            endpoint="/deposits"
        ).observe(duration)
```

**Verification:**
```bash
# Metrics should be available at /metrics endpoint
curl http://localhost:8002/metrics
```

**Estimated Time:** 1.5 hours

---

### 7. Database Backup & Recovery Procedures

**Step 1:** Automated backups (daily)
```bash
#!/bin/bash
# backup_postgres.sh

BACKUP_DIR="/backups/postgres"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="${DATABASE_NAME:-gdb_transactions}"

mkdir -p $BACKUP_DIR

# Full backup
pg_dump -h ${DB_HOST} -U ${DB_USER} ${DB_NAME} | \
  gzip > "${BACKUP_DIR}/backup_${BACKUP_DATE}.sql.gz"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_DIR}/backup_${BACKUP_DATE}.sql.gz"
```

**Step 2:** Configure automated backup (cron)
```bash
# Add to crontab
0 2 * * * /scripts/backup_postgres.sh >> /var/log/backup.log 2>&1
```

**Step 3:** Restore procedure
```bash
#!/bin/bash
# restore_postgres.sh

BACKUP_FILE=$1
DB_NAME="${DATABASE_NAME:-gdb_transactions}"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Decompress and restore
gunzip -c $BACKUP_FILE | psql -h ${DB_HOST} -U ${DB_USER} ${DB_NAME}

echo "Restore completed from: $BACKUP_FILE"
```

**Testing:**
```bash
# Test backup
./backup_postgres.sh

# Verify backup exists
ls -lh /backups/postgres/

# Test restore procedure (on test database)
createdb gdb_transactions_test
./restore_postgres.sh /backups/postgres/backup_latest.sql.gz
```

**Estimated Time:** 1 hour

---

## HIGH PRIORITY ITEMS (SHOULD DO)

### 8. Database Connection Pooling Optimization

**File:** `transactions_service/app/database/connection.py`

**Current Status:** Working with 5-20 connections

**Optimize for Production:**
```python
# Update connection pool settings
pool = await asyncpg.create_pool(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    min_size=10,        # Minimum connections (↑ from 5)
    max_size=50,        # Maximum connections (↑ from 20)
    command_timeout=30, # Add timeout
    max_cached_statement_lifetime=3600,  # Cache statements
    max_cacheable_statement_size=15000,  # Larger cache
)
```

**Estimated Time:** 30 minutes

---

### 9. Health Check Endpoint Enhancement

**File:** `transactions_service/app/main.py`

**Current:** Basic health check

**Enhanced:**
```python
@app.get("/health")
async def health_check():
    """Detailed health check."""
    
    # Check database connectivity
    try:
        async with pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Account Service connectivity
    try:
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost:8001/health", timeout=5)
        accounts_service_status = "healthy"
    except Exception as e:
        accounts_service_status = f"unhealthy: {str(e)}"
    
    all_healthy = db_status == "healthy" and accounts_service_status == "healthy"
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": db_status,
            "accounts_service": accounts_service_status,
            "version": "1.0.0"
        }
    }
```

**Estimated Time:** 30 minutes

---

### 10. Kubernetes Deployment Manifests

**File:** `transactions_service/k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transactions-service
  namespace: microservices
spec:
  replicas: 3
  selector:
    matchLabels:
      app: transactions-service
  template:
    metadata:
      labels:
        app: transactions-service
    spec:
      containers:
      - name: transactions-service
        image: your-registry/transactions-service:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8002
          name: http
        env:
        - name: DATABASE_HOST
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: host
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: user
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: transactions-service
  namespace: microservices
spec:
  type: ClusterIP
  selector:
    app: transactions-service
  ports:
  - port: 8002
    targetPort: 8002
    name: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: transactions-service-hpa
  namespace: microservices
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: transactions-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Estimated Time:** 1 hour

---

### 11. Load Testing Script

**File:** `transactions_service/load_tests/load_test.py`

```python
import asyncio
import httpx
import time
from statistics import mean, stdev

class LoadTester:
    def __init__(self, base_url: str, num_requests: int = 1000):
        self.base_url = base_url
        self.num_requests = num_requests
        self.results = []
    
    async def run_load_test(self):
        """Run load test against endpoints."""
        
        async with httpx.AsyncClient() as client:
            tasks = [
                self.test_deposit(client),
                self.test_withdrawal(client),
                self.test_transfer(client),
            ]
            
            await asyncio.gather(*tasks)
        
        self.print_results()
    
    async def test_deposit(self, client: httpx.AsyncClient):
        """Test deposit endpoint."""
        times = []
        
        for i in range(self.num_requests):
            start = time.time()
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/deposits",
                    json={
                        "account_number": 1001 + (i % 10),
                        "amount": 100.00,
                        "description": f"Load test {i}"
                    },
                    timeout=5
                )
                elapsed = (time.time() - start) * 1000  # milliseconds
                times.append(elapsed)
                
                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
            except Exception as e:
                print(f"Exception: {e}")
        
        self.print_endpoint_results("Deposit", times)
    
    async def test_withdrawal(self, client: httpx.AsyncClient):
        """Test withdrawal endpoint."""
        # Similar to test_deposit
        pass
    
    async def test_transfer(self, client: httpx.AsyncClient):
        """Test transfer endpoint."""
        # Similar to test_deposit
        pass
    
    def print_endpoint_results(self, endpoint: str, times: list):
        """Print results for an endpoint."""
        if not times:
            return
        
        print(f"\n{endpoint} Results:")
        print(f"  Total Requests: {len(times)}")
        print(f"  Avg Time: {mean(times):.2f}ms")
        print(f"  Min Time: {min(times):.2f}ms")
        print(f"  Max Time: {max(times):.2f}ms")
        print(f"  Std Dev: {stdev(times) if len(times) > 1 else 0:.2f}ms")
        print(f"  P95: {sorted(times)[int(len(times) * 0.95)]:.2f}ms")
        print(f"  P99: {sorted(times)[int(len(times) * 0.99)]:.2f}ms")

# Run load test
if __name__ == "__main__":
    tester = LoadTester("http://localhost:8002", num_requests=1000)
    asyncio.run(tester.run_load_test())
```

**Run test:**
```bash
python load_tests/load_test.py
```

**Estimated Time:** 1.5 hours

---

## DEPLOYMENT TIMELINE

```
Week 1 (Critical Items):
├─ Monday: Enable auth, implement rate limiting
├─ Tuesday: Setup structured logging, JSON logs
├─ Wednesday: HTTPS/TLS, security headers
├─ Thursday: Prometheus monitoring setup
└─ Friday: Backup procedures, testing

Week 2 (Infrastructure):
├─ Monday: Docker image creation
├─ Tuesday: Kubernetes manifests
├─ Wednesday: Load balancer setup
├─ Thursday: Auto-scaling configuration
└─ Friday: Disaster recovery testing

Week 3 (Testing):
├─ Monday-Tuesday: Load testing
├─ Wednesday: Security audit
├─ Thursday: Chaos engineering
└─ Friday: Production readiness review

Week 4 (Deployment):
├─ Monday: Staging environment validation
├─ Tuesday: Canary deployment (5% traffic)
├─ Wednesday: Monitor and validate
├─ Thursday: Full rollout (100% traffic)
└─ Friday: Post-deployment validation
```

---

## ROLLBACK PROCEDURE (If needed)

```bash
# Identify previous version
helm history transactions-service

# Rollback to previous version
helm rollback transactions-service <REVISION>

# Verify rollback
kubectl get pods -n microservices
kubectl logs -n microservices -l app=transactions-service

# Monitor metrics
# Check Grafana dashboard for health metrics
```

---

## SUCCESS CRITERIA

- [ ] 238/238 tests passing
- [ ] All endpoints require authentication
- [ ] Rate limiting prevents abuse
- [ ] Monitoring shows < 5% error rate
- [ ] P95 latency < 200ms
- [ ] Database backups automated and tested
- [ ] Load test: 5000 req/sec with P95 < 500ms
- [ ] Security audit passed
- [ ] Disaster recovery procedure tested

---

**Total Estimated Time:** 2-3 weeks  
**Deployment Date:** Target: End of month  
**Go-Live:** Post-successful staging validation
