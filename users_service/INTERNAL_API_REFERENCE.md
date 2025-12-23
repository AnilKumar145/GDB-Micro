# Internal User Service APIs - Complete Reference

## Overview

The Internal User Service provides protected endpoints for inter-microservice communication. These endpoints are **NOT exposed in the public API** and should only be accessed by authenticated internal services.

**Base URL:** `http://localhost:8003/internal/v1`

## Authentication

All internal endpoints require:
- Service-to-service authentication (to be implemented with JWT/API Key)
- Requests from authorized microservices only
- All requests logged for audit purposes

## Endpoints

### 1. Get User Details
**Endpoint:** `GET /internal/v1/users/{login_id}`

Retrieve complete user information by login_id.

**Parameters:**
- `login_id` (path, required): User's login identifier

**Response (200 OK):**
```json
{
  "user_id": 1,
  "username": "John Doe",
  "login_id": "john.doe",
  "role": "CUSTOMER",
  "created_at": "2025-12-22T10:30:00",
  "is_active": true
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

**Use Cases:**
- Auth Service: Get user info during login
- Accounts Service: Verify user exists before creating account
- Transactions Service: Get user role for transaction validation

---

### 2. Verify User Credentials
**Endpoint:** `POST /internal/v1/users/verify`

Verify user login credentials for authentication.

**Parameters:**
- `login_id` (query, required): User login identifier
- `password` (query, required): User password (plain text)

**Response (200 OK):**
```json
{
  "is_valid": true,
  "user_id": 1,
  "login_id": "john.doe",
  "role": "CUSTOMER",
  "is_active": true
}
```

**Error Responses:**
- `400 Bad Request`: Missing credentials
- `401 Unauthorized`: Invalid credentials
- `500 Internal Server Error`: Server error

**Use Cases:**
- Auth Service: Authenticate user login
- API Gateway: Validate credentials before issuing JWT

**Security Notes:**
- Password is hashed and verified using bcrypt
- Never return password in response
- Log failed attempts for security

---

### 3. Validate User Role
**Endpoint:** `POST /internal/v1/users/validate-role`

Check if a user has a specific role.

**Parameters:**
- `login_id` (query, required): User login identifier
- `required_role` (query, required): Role to validate (CUSTOMER, TELLER, ADMIN)

**Response (200 OK):**
```json
{
  "has_role": true,
  "user_role": "TELLER",
  "required_role": "TELLER",
  "user_id": 2
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

**Use Cases:**
- Transactions Service: Verify user is TELLER before allowing transfer
- Accounts Service: Verify ADMIN role for account modifications
- Authorization Service: Role-based access control

---

### 4. Get User Role by ID
**Endpoint:** `GET /internal/v1/users/{user_id}/role`

Get user role by user_id (faster than login_id lookup).

**Parameters:**
- `user_id` (path, required): User identifier

**Response (200 OK):**
```json
{
  "user_id": 3,
  "role": "ADMIN",
  "is_active": true,
  "login_id": "admin.user"
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

**Use Cases:**
- Cached lookup: Services maintaining user_id cache
- Quick role verification for transactions
- Audit logging with user_id references

---

### 5. Check User Active Status
**Endpoint:** `GET /internal/v1/users/{login_id}/status`

Check if user is active (can perform operations).

**Parameters:**
- `login_id` (path, required): User login identifier

**Response (200 OK):**
```json
{
  "user_id": 1,
  "login_id": "john.doe",
  "is_active": true,
  "role": "CUSTOMER"
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

**Use Cases:**
- Transactions Service: Prevent inactive users from transactions
- Accounts Service: Block operations on inactive accounts
- Business Rules Engine: Check user eligibility

---

### 6. Bulk Validate Users
**Endpoint:** `POST /internal/v1/users/bulk-validate`

Validate multiple users exist and are active (batch operation).

**Request Body:**
```json
{
  "login_ids": ["john.doe", "jane.smith", "nonexistent.user"]
}
```

**Response (200 OK):**
```json
{
  "valid_users": [
    {
      "user_id": 1,
      "login_id": "john.doe",
      "role": "CUSTOMER"
    },
    {
      "user_id": 2,
      "login_id": "jane.smith",
      "role": "TELLER"
    }
  ],
  "invalid_users": ["nonexistent.user"],
  "total_valid": 2,
  "total_invalid": 1
}
```

**Error Responses:**
- `500 Internal Server Error`: Server error

**Use Cases:**
- Batch processing: Validate recipients before fund transfer
- Bulk operations: Check multiple users for group operations
- Data migration: Verify user lists from external sources

---

### 7. Search Users
**Endpoint:** `GET /internal/v1/users`

Search users by criteria (role, active status).

**Parameters:**
- `role` (query, optional): Filter by role (CUSTOMER, TELLER, ADMIN)
- `is_active` (query, optional): Filter by active status (true/false)
- `limit` (query, optional): Maximum results (default: 100, max: 1000)

**Response (200 OK):**
```json
{
  "users": [
    {
      "user_id": 1,
      "login_id": "john.doe",
      "username": "John Doe",
      "role": "CUSTOMER",
      "is_active": true
    },
    {
      "user_id": 2,
      "login_id": "jane.smith",
      "username": "Jane Smith",
      "role": "TELLER",
      "is_active": true
    }
  ],
  "total_count": 2,
  "filters": {
    "role": "CUSTOMER",
    "is_active": true,
    "limit": 100
  }
}
```

**Error Responses:**
- `500 Internal Server Error`: Server error

**Use Cases:**
- Admin Dashboard: List all TELLER users
- Reporting: Get active CUSTOMER count
- Analytics: Filter users by role for statistics

---

### 8. Health Check
**Endpoint:** `GET /internal/v1/health`

Service health status endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "user-management",
  "version": "1.0.0"
}
```

**Use Cases:**
- Service discovery: Check if User Service is running
- Load balancer: Monitor service availability
- Orchestration: Health check for deployment

---

## Request Examples

### Example 1: Auth Service - Verify Login
```bash
curl -X POST "http://localhost:8003/internal/v1/users/verify" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SERVICE_TOKEN>" \
  -d '{"login_id": "john.doe", "password": "password123"}'
```

### Example 2: Transactions Service - Validate User Role
```bash
curl -X POST "http://localhost:8003/internal/v1/users/validate-role" \
  -H "Authorization: Bearer <SERVICE_TOKEN>" \
  -d '{
    "login_id": "jane.smith",
    "required_role": "TELLER"
  }'
```

### Example 3: Accounts Service - Get User Details
```bash
curl -X GET "http://localhost:8003/internal/v1/users/john.doe" \
  -H "Authorization: Bearer <SERVICE_TOKEN>"
```

### Example 4: Bulk Validation - Fund Transfer
```bash
curl -X POST "http://localhost:8003/internal/v1/users/bulk-validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SERVICE_TOKEN>" \
  -d '{
    "login_ids": ["sender.user", "recipient.user"]
  }'
```

### Example 5: Search Tellers
```bash
curl -X GET "http://localhost:8003/internal/v1/users?role=TELLER&is_active=true&limit=50" \
  -H "Authorization: Bearer <SERVICE_TOKEN>"
```

---

## Integration Guide

### For Auth Service

```python
import httpx

async def authenticate_user(login_id: str, password: str):
    """Authenticate user against User Service."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://user-service:8003/internal/v1/users/verify",
            params={
                "login_id": login_id,
                "password": password
            },
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "authenticated": True,
                "user_id": data["user_id"],
                "role": data["role"]
            }
        else:
            return {"authenticated": False}
```

### For Transactions Service

```python
async def validate_transaction_user(login_id: str, required_role: str):
    """Validate user can perform transaction."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://user-service:8003/internal/v1/users/validate-role",
            params={
                "login_id": login_id,
                "required_role": required_role
            },
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )
        
        if response.status_code == 200:
            return response.json()["has_role"]
        return False
```

### For Accounts Service

```python
async def get_account_user_info(user_id: int):
    """Get user info for account operations."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://user-service:8003/internal/v1/users/{user_id}/role",
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
```

---

## Error Handling

All endpoints follow standard HTTP status codes:

| Status | Meaning | Handling |
|--------|---------|----------|
| 200 | Success | Process response data |
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Invalid credentials or expired token |
| 404 | Not Found | User does not exist |
| 500 | Server Error | Retry with exponential backoff |

---

## Security Considerations

1. **Service Authentication:** All requests must include valid service-to-service auth token
2. **Rate Limiting:** Implement rate limits per service (e.g., 1000 req/min)
3. **Logging:** All internal API calls logged with timestamp, service, and action
4. **Password Handling:** Never log or expose user passwords
5. **SSL/TLS:** All internal communication should use HTTPS in production
6. **Network Isolation:** Internal APIs should only be accessible within service mesh
7. **Audit Trail:** Maintain audit logs of all user validations and role checks

---

## Monitoring & Metrics

Track these metrics for each endpoint:

- **Response Time:** P50, P95, P99 latencies
- **Error Rate:** 4xx and 5xx response counts
- **Throughput:** Requests per second
- **Cache Hit Rate:** If implementing caching
- **Failed Authentications:** Count of failed verify attempts

---

## Future Enhancements

- [ ] Implement service-to-service JWT authentication
- [ ] Add response caching (Redis) for frequently accessed users
- [ ] Implement rate limiting per service
- [ ] Add GraphQL endpoint for complex queries
- [ ] Implement webhooks for user state changes
- [ ] Add batch export functionality
- [ ] Implement user activity tracking
- [ ] Add advanced search with Elasticsearch

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-23 | Initial release with 8 core endpoints |

---

**Last Updated:** 2025-12-23  
**Maintained by:** Global Digital Banking Team
