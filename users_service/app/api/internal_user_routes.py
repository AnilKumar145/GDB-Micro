"""
Internal User Routes for User Management Service

INTERNAL API ENDPOINTS (Simplified - 6 endpoints)

CORE ENDPOINTS (3 - Required for Auth Service):
- POST /internal/v1/users/verify - Verify user credentials (login_id + password)
- GET /internal/v1/users/{login_id}/status - Get user status and role
- GET /internal/v1/users/{login_id}/role - Get user role only

OPTIONAL ENDPOINTS (2 - Advanced Features):
- POST /internal/v1/users/validate-role - Validate if user has required role
- POST /internal/v1/users/bulk-validate - Bulk validate multiple users

UTILITY ENDPOINTS (1):
- GET /internal/v1/health - Health check with endpoint listing

DEPRECATED/REMOVED ENDPOINTS (3):
- Removed: GET /internal/v1/users/{user_id} (redundant, use status endpoint)
- Removed: GET /internal/v1/users (search functionality - moved to public API)
- Removed: GET /internal/v1/users/{user_id}/role (replaced with login_id version)

Design Philosophy:
- Minimal surface area: Only endpoints needed for Auth Service integration
- Security first: All endpoints validate credentials/permissions before returning data
- Audit ready: All operations are logged for compliance
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel
import bcrypt
import logging

from ..models.response_models import ErrorResponse
from ..repositories.user_repository import UserRepository
from ..exceptions.user_management_exception import (
    UserManagementException,
    UserNotFoundException,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/v1", tags=["Internal User APIs"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class BulkValidateRequest(BaseModel):
    """Request model for bulk user validation endpoint."""
    login_ids: List[str]


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class VerifyCredentialsResponse(BaseModel):
    """Response model for verify user credentials endpoint."""
    is_valid: bool
    user_id: Optional[int] = None
    role: Optional[str] = None
    is_active: bool = False


# ============================================================================
# SERVICE CLASS
# ============================================================================

class InternalUserService:
    """Service class for internal user operations."""
    
    def __init__(self, repo: UserRepository):
        """
        Initialize service with repository.
        
        Args:
            repo: UserRepository instance
        """
        self.repo = repo
        self.logger = logging.getLogger(__name__)
    
    async def verify_user_credentials(self, login_id: str, password: str) -> dict:
        """
        Verify user credentials (login_id + password).
        
        Args:
            login_id: User's login identifier
            password: User's plaintext password
        
        Returns:
            Dictionary with:
            - is_valid: bool - Whether credentials are correct
            - user_id: int - User ID (if valid)
            - role: str - User role (if valid)
            - is_active: bool - User active status
        
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        try:
            user = await self.repo.get_user_by_login_id(login_id)
            
            if not user:
                return {
                    "is_valid": False,
                    "user_id": None,
                    "role": None,
                    "is_active": False
                }
            
            # Verify password
            is_password_valid = await self._verify_password(password, user.get("password"))
            
            # Always return actual is_active status from database, regardless of password
            is_active_value = user.get("is_active", False)
            self.logger.info(f"DEBUG: User {login_id} is_active from DB: {is_active_value}, type: {type(is_active_value)}")
            
            return {
                "is_valid": is_password_valid,
                "user_id": user.get("user_id") if is_password_valid else None,
                "role": user.get("role") if is_password_valid else None,
                "is_active": is_active_value  # Always return actual status, not conditional on password
            }
        
        except Exception as e:
            self.logger.error(f"Error verifying credentials for {login_id}: {str(e)}")
            raise
    
    async def get_user_status(self, login_id: str) -> Optional[dict]:
        """
        Get user status and role by login_id.
        
        Args:
            login_id: User's login identifier
        
        Returns:
            Dictionary with:
            - user_id: int
            - login_id: str
            - is_active: bool
            - role: str
        
        Returns None if user doesn't exist.
        """
        try:
            user = await self.repo.get_user_by_login_id(login_id)
            
            if not user:
                return None
            
            return {
                "user_id": user.get("user_id"),
                "login_id": user.get("login_id"),
                "is_active": user.get("is_active", False),
                "role": user.get("role")
            }
        
        except Exception as e:
            self.logger.error(f"Error getting user status for {login_id}: {str(e)}")
            raise
    
    async def get_user_role(self, login_id: str) -> Optional[dict]:
        """
        Get user role by login_id.
        
        Args:
            login_id: User's login identifier
        
        Returns:
            Dictionary with:
            - user_id: int
            - login_id: str
            - role: str
        
        Returns None if user doesn't exist.
        """
        try:
            user = await self.repo.get_user_by_login_id(login_id)
            
            if not user:
                return None
            
            return {
                "user_id": user.get("user_id"),
                "login_id": user.get("login_id"),
                "role": user.get("role")
            }
        
        except Exception as e:
            self.logger.error(f"Error getting user role for {login_id}: {str(e)}")
            raise
    
    async def validate_user_role(self, login_id: str, required_role: str) -> Optional[dict]:
        """
        Validate if user has required role.
        
        Args:
            login_id: User's login identifier
            required_role: Role to validate against
        
        Returns:
            Dictionary with:
            - has_role: bool - Whether user has required role
            - user_role: str - User's actual role
            - is_active: bool - User active status
        
        Returns None if user doesn't exist.
        """
        try:
            user = await self.repo.get_user_by_login_id(login_id)
            
            if not user:
                return None
            
            user_role = user.get("role")
            has_role = user_role == required_role
            
            return {
                "has_role": has_role,
                "user_role": user_role,
                "is_active": user.get("is_active", False)
            }
        
        except Exception as e:
            self.logger.error(f"Error validating role for {login_id}: {str(e)}")
            raise
    
    async def bulk_validate_users(self, login_ids: List[str]) -> dict:
        """
        Bulk validate multiple users.
        
        Args:
            login_ids: List of login IDs to validate
        
        Returns:
            Dictionary with:
            - valid_users: List[dict] - Valid users found
            - invalid_users: List[str] - Login IDs not found
            - total_valid: int - Count of valid users
            - total_invalid: int - Count of invalid users
        """
        try:
            valid_users = []
            invalid_users = []
            
            for login_id in login_ids:
                user = await self.repo.get_user_by_login_id(login_id)
                
                if user:
                    valid_users.append({
                        "user_id": user.get("user_id"),
                        "login_id": user.get("login_id"),
                        "role": user.get("role"),
                        "is_active": user.get("is_active", False)
                    })
                else:
                    invalid_users.append(login_id)
            
            return {
                "valid_users": valid_users,
                "invalid_users": invalid_users,
                "total_valid": len(valid_users),
                "total_invalid": len(invalid_users)
            }
        
        except Exception as e:
            self.logger.error(f"Error in bulk validate: {str(e)}")
            raise
    
    @staticmethod
    async def _verify_password(plaintext: str, hashed: str) -> bool:
        """
        Verify plaintext password against bcrypt hash.
        
        Args:
            plaintext: Plaintext password
            hashed: Hashed password from database
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            # bcrypt.checkpw expects bytes for both arguments
            # hashed password from DB is typically a string
            if isinstance(hashed, str):
                hashed = hashed.encode("utf-8")
            return bcrypt.checkpw(plaintext.encode("utf-8"), hashed)
        except Exception:
            return False


# ============================================================================
# CORE ENDPOINTS (3)
# ============================================================================

@router.post(
    "/users/verify",
    status_code=200,
    response_model=VerifyCredentialsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def verify_user_credentials(
    login_id: str = Body(..., embed=True),
    password: str = Body(..., embed=True)
) -> VerifyCredentialsResponse:
    """
    Verify user credentials (CORE - Required for Auth Service).
    
    **Endpoint:** POST /internal/v1/users/verify
    
    **Purpose:** Authenticate user by login_id and password
    
    **Request Body:**
    ```json
    {
        "login_id": "user.name",
        "password": "SecurePass123"
    }
    ```
    
    **Success Response (200 - Valid Credentials):**
    ```json
    {
        "is_valid": true,
        "user_id": 123,
        "role": "CUSTOMER",
        "is_active": true
    }
    ```
    
    **Error Response (200 - Invalid Credentials or User Not Found):**
    ```json
    {
        "is_valid": false,
        "user_id": null,
        "role": null,
        "is_active": false
    }
    ```
    
    **Response Fields:**
    - `is_valid`: Boolean indicating if credentials are correct
    - `user_id`: User ID if credentials valid, null otherwise
    - `role`: User role (CUSTOMER/TELLER/ADMIN) if credentials valid, null otherwise
    - `is_active`: User active status if credentials valid, false otherwise
    """
    try:
        repo = UserRepository()
        service = InternalUserService(repo)
        result = await service.verify_user_credentials(login_id, password)
        return VerifyCredentialsResponse(**result)
    
    except Exception as e:
        logger.error(f"Error verifying credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/users/{login_id}/status",
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def get_user_status(login_id: str):
    """
    Get user status and role (CORE - Required for Auth Service).
    
    **Endpoint:** GET /internal/v1/users/{login_id}/status
    
    **Purpose:** Get user's active status and role for authorization
    
    **Path Parameters:**
    - login_id: User's login identifier
    
    **Success Response (200):**
    ```json
    {
        "user_id": 123,
        "login_id": "user.name",
        "is_active": true,
        "role": "CUSTOMER"
    }
    ```
    
    **Error Response (404):**
    ```json
    {
        "detail": "User not found"
    }
    ```
    """
    try:
        repo = UserRepository()
        service = InternalUserService(repo)
        result = await service.get_user_status(login_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/users/{login_id}/role",
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def get_user_role(login_id: str):
    """
    Get user role only (CORE - Required for Auth Service).
    
    **Endpoint:** GET /internal/v1/users/{login_id}/role
    
    **Purpose:** Quick role lookup for authorization checks
    
    **Path Parameters:**
    - login_id: User's login identifier
    
    **Success Response (200):**
    ```json
    {
        "user_id": 123,
        "login_id": "user.name",
        "role": "CUSTOMER"
    }
    ```
    
    **Error Response (404):**
    ```json
    {
        "detail": "User not found"
    }
    ```
    """
    try:
        repo = UserRepository()
        service = InternalUserService(repo)
        result = await service.get_user_role(login_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# OPTIONAL ENDPOINTS (2)
# ============================================================================

@router.post(
    "/users/validate-role",
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def validate_user_role(
    login_id: str = Body(..., embed=True),
    required_role: str = Body(..., embed=True)
):
    """
    Validate if user has required role (OPTIONAL - Advanced feature).
    
    **Endpoint:** POST /internal/v1/users/validate-role
    
    **Purpose:** Check if user has specific role for authorization
    
    **Request Body:**
    ```json
    {
        "login_id": "user.name",
        "required_role": "TELLER"
    }
    ```
    
    **Success Response (200):**
    ```json
    {
        "has_role": true,
        "user_role": "TELLER",
        "is_active": true
    }
    ```
    
    **Error Response (404):**
    ```json
    {
        "detail": "User not found"
    }
    ```
    """
    try:
        repo = UserRepository()
        service = InternalUserService(repo)
        result = await service.validate_user_role(login_id, required_role)
        
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating user role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/users/bulk-validate",
    status_code=200,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def bulk_validate_users(request: BulkValidateRequest):
    """
    Bulk validate multiple users (OPTIONAL - Batch processing).
    
    **Endpoint:** POST /internal/v1/users/bulk-validate
    
    **Purpose:** Validate multiple users in single request
    
    **Request Body:**
    ```json
    {
        "login_ids": ["user1.name", "user2.name", "user3.name"]
    }
    ```
    
    **Success Response (200):**
    ```json
    {
        "valid_users": [
            {
                "user_id": 123,
                "login_id": "user1.name",
                "role": "CUSTOMER",
                "is_active": true
            },
            {
                "user_id": 124,
                "login_id": "user2.name",
                "role": "TELLER",
                "is_active": true
            }
        ],
        "invalid_users": ["user3.name"],
        "total_valid": 2,
        "total_invalid": 1
    }
    ```
    """
    try:
        if not request.login_ids:
            raise HTTPException(status_code=400, detail="login_ids cannot be empty")
        
        repo = UserRepository()
        service = InternalUserService(repo)
        result = await service.bulk_validate_users(request.login_ids)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk validate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# UTILITY ENDPOINTS (1)
# ============================================================================

@router.get(
    "/health",
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Service unhealthy"},
    },
)
async def health_check():
    """
    Health check endpoint with endpoint listing (UTILITY).
    
    **Endpoint:** GET /internal/v1/health
    
    **Purpose:** Check service health and list available endpoints
    
    **Success Response (200):**
    ```json
    {
        "status": "healthy",
        "service": "User Management Service",
        "version": "1.0.0",
        "endpoints": {
            "core": [
                "POST /internal/v1/users/verify",
                "GET /internal/v1/users/{login_id}/status",
                "GET /internal/v1/users/{login_id}/role"
            ],
            "optional": [
                "POST /internal/v1/users/validate-role",
                "POST /internal/v1/users/bulk-validate"
            ],
            "utility": [
                "GET /internal/v1/health"
            ]
        }
    }
    ```
    """
    try:
        return {
            "status": "healthy",
            "service": "User Management Service - Internal APIs",
            "version": "1.0.0",
            "endpoints": {
                "core": [
                    "POST /internal/v1/users/verify",
                    "GET /internal/v1/users/{login_id}/status",
                    "GET /internal/v1/users/{login_id}/role"
                ],
                "optional": [
                    "POST /internal/v1/users/validate-role",
                    "POST /internal/v1/users/bulk-validate"
                ],
                "utility": [
                    "GET /internal/v1/health"
                ]
            }
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")
