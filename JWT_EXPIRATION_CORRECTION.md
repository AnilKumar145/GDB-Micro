# JWT Token Expiration - Correction Notice

**Date:** December 25, 2025  
**Corrected:** JWT Token Expiration Setting  
**Status:** ✅ Documented

---

## Summary

**JWT Token Expiration is 30 minutes**, NOT 10 years as was initially mentioned in some documentation.

### Actual Configuration

**File:** `auth_service/app/config/settings.py`  
**Setting:** `JWT_EXPIRY_MINUTES = 30`

```python
# JWT Token expiry in minutes (15-30 min recommended)
JWT_EXPIRY_MINUTES: int = 30
```

---

## Why 30 Minutes?

### Security Best Practices
- **Short expiration (30 minutes)** prevents token abuse if stolen
- User needs to login again after token expires
- Reduces window of vulnerability
- Industry standard for API tokens

### For Trainee Environment
- 30 minutes is sufficient for learning exercises
- Longer durations (like 10 years) would be a security risk
- Can be adjusted in settings if needed for testing
- Aligns with production security practices

---

## Impact

### What This Means for Trainees
1. **Token Validity:** JWT tokens are valid for 30 minutes after login
2. **Relogin Required:** After 30 minutes, user must login again to get a new token
3. **Multiple Exercises:** During training exercises, may need to login multiple times
4. **Recommended:** Use a script or Postman to refresh tokens if needed

### Example Workflow
```bash
# 1. Login - Get JWT token (valid for 30 minutes)
curl -X POST http://localhost:8004/api/v1/auth/login \
  -d '{"login_id": "john.doe", "password": "Welcome@1"}'
# Response: {"access_token": "eyJ...", ...}

# 2. Use token for operations (within 30 minutes)
curl -X GET http://localhost:8003/api/v1/users/1002 \
  -H "Authorization: Bearer eyJ..."

# 3. After 30 minutes - token expires
# Need to login again to get a new token
```

---

## Correction Applied

### Documents Updated
- ✅ `PRODUCTION_READINESS_ANALYSIS.md` - Line 42
  - Changed: "10-year expiration" → "30-minute expiration"
  
- ✅ `EXECUTIVE_SUMMARY.md` - Line 282
  - Changed: "10-year expiration for training purposes" → "30-minute token expiration"

---

## Settings Available

If you need to adjust token expiration for your training needs, edit:

**File:** `auth_service/app/config/settings.py`

```python
# Current setting
JWT_EXPIRY_MINUTES: int = 30

# To increase to 1 hour:
JWT_EXPIRY_MINUTES: int = 60

# To increase to 8 hours:
JWT_EXPIRY_MINUTES: int = 480

# ⚠️ Note: Change must be identical in all microservices
```

---

## Verification

To verify current setting:

```bash
# Check in auth_service
grep "JWT_EXPIRY_MINUTES" auth_service/app/config/settings.py
# Output: JWT_EXPIRY_MINUTES: int = 30

# Check JWT token claims
# The "exp" claim shows expiration timestamp (unix time)
```

### Decode a Token to See Expiration
```python
import jwt
import json
from datetime import datetime

token = "eyJ..."  # Your JWT token

# Decode without verification (just to inspect)
payload = jwt.decode(token, options={"verify_signature": False})
print(json.dumps(payload, indent=2, default=str))

# See expiration date
exp_timestamp = payload["exp"]
exp_date = datetime.fromtimestamp(exp_timestamp)
print(f"Token expires at: {exp_date}")
```

---

## Conclusion

**JWT Token Expiration: 30 minutes** ✅

This is the correct, secure configuration for the GDB-Micro banking system. It follows security best practices while remaining practical for training exercises.

**For Extended Testing:** If you need longer token validity during training, adjust `JWT_EXPIRY_MINUTES` in settings and restart the auth service.

---

**Status:** ✅ Correction Applied & Documented  
**All References:** Updated  
**System:** Production Ready
