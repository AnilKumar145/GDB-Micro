"""
Internal User Routes for User Management Service.
These endpoints are for inter-microservice communication only (NOT exposed publicly).
Used for user validation, role checking, and authentication by other services.

Endpoints:
- GET /internal/v1/users/{login_id} - Get user details by login_id
- POST /internal/v1/users/verify - Verify user credentials
- POST /internal/v1/users/validate-role - Validate user role
- GET /internal/v1/users/{user_id}/role - Get user role by user_id
- GET /internal/v1/users/{login_id}/status - Get user active status
- POST /internal/v1/users/bulk-validate - Validate multiple users
- GET /internal/v1/users/search - Search users by criteria
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
import logging
from ..models.response_models import UserResponse, ErrorResponse
from ..models.request_models import AddUserRequest
from ..repositories.user_repository import UserRepository
from ..exceptions.user_management_exception import UserNotFoundException
import bcrypt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/v1", tags=["Internal User Management"])

# Lazy initialization - service created on first request
_internal_service = None


def get_internal_service() -> "InternalUserService":
    """Get or create the internal service (lazy initialization)."""
    global _internal_service
    if _internal_service is None:
        _internal_service = InternalUserService()
    return _internal_service


class InternalUserService:
    """Internal service for inter-microservice user operations."""
    
    def __init__(self):
        """Initialize with repository."""
        self.repo = UserRepository()
    
    async def get_user_details(self, login_id: str) -> Optional[dict]:
        """Get user details by login_id for internal use."""
        return await self.repo.get_user_by_login_id(login_id)
    
    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by user_id for internal use."""
        return await self.repo.get_user_by_id(user_id)
    
    async def verify_user_credentials(self, login_id: str, password: str) -> bool:
        """Verify user credentials for authentication."""
        user = await self.repo.get_user_by_login_id(login_id)
        if not user:
            return False
        
        # Verify password
        try:
            return bcrypt.checkpw(password.encode(), user["password"].encode())
        except Exception:
            return False
    
    async def validate_user_role(self, login_id: str, required_role: str) -> bool:
        """Validate if user has the required role."""
        user = await self.repo.get_user_by_login_id(login_id)
        if not user:
            return False
        
        return user["role"] == required_role
    
    async def get_user_role(self, user_id: int) -> Optional[str]:
        """Get user role by user_id."""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            return None
        
        return user["role"]
    
    async def check_user_active_status(self, login_id: str) -> Optional[bool]:
        """Check if user is active."""
        user = await self.repo.get_user_by_login_id(login_id)
        if not user:
            return None
        
        return user["is_active"]


@router.get(
    "/users/{login_id}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def get_user_internal(login_id: str):
    """
    Get user details by login_id for internal microservice use.
    
    **Internal Use Only** - Not exposed in public API
    
    Args:
        login_id: User's login identifier
    
    Returns:
        UserResponse: Complete user details
    
    Raises:
        404: User not found
    """
    try:
        logger.info(f"[INTERNAL] Fetching user: {login_id}")
        
        service = get_internal_service()
        user = await service.get_user_details(login_id)
        if not user:
            raise UserNotFoundException(login_id)
        
        logger.info(f"[INTERNAL] User fetched: {login_id}")
        
        return UserResponse(
            user_id=user["user_id"],
            username=user["username"],
            login_id=user["login_id"],
            role=user["role"],
            created_at=user["created_at"],
            is_active=user["is_active"]
        )
    
    except UserNotFoundException as e:
        logger.error(f"[INTERNAL] User not found: {login_id}")
        raise HTTPException(status_code=404, detail=e.detail)
    
    except Exception as e:
        logger.error(f"[INTERNAL] Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/users/verify",
    response_model=dict,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials"},
        401: {"model": ErrorResponse, "description": "Authentication failed"},
    },
)
async def verify_user_credentials(
    login_id: str = Query(..., description="User login_id"),
    password: str = Query(..., description="User password")
):
    """
    Verify user credentials for authentication.
    
    **Internal Use Only** - For Auth Service
    
    Args:
        login_id: User login identifier
        password: User password (will be verified against hash)
    
    Returns:
        dict: {
            "is_valid": bool,
            "user_id": int (if valid),
            "role": str (if valid)
        }
    
    Raises:
        401: Invalid credentials
    """
    try:
        logger.info(f"[INTERNAL] Verifying credentials for: {login_id}")
        
        if not login_id or not password:
            raise HTTPException(status_code=400, detail="Missing credentials")
        
        service = get_internal_service()
        # Verify credentials
        is_valid = await service.verify_user_credentials(login_id, password)
        
        if not is_valid:
            logger.warning(f"[INTERNAL] Invalid credentials for: {login_id}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get user details for response
        user = await service.get_user_details(login_id)
        
        logger.info(f"[INTERNAL] Credentials verified for: {login_id}")
        
        return {
            "is_valid": True,
            "user_id": user["user_id"],
            "login_id": user["login_id"],
            "role": user["role"],
            "is_active": user["is_active"]
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"[INTERNAL] Error verifying credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/users/validate-role",
    response_model=dict,
)
async def validate_user_role(
    login_id: str = Query(..., description="User login_id"),
    required_role: str = Query(..., description="Required role to validate against")
):
    """
    Validate if user has a specific role.
    
    **Internal Use Only** - For authorization checks
    
    Args:
        login_id: User login identifier
        required_role: Role to validate (CUSTOMER, TELLER, ADMIN)
    
    Returns:
        dict: {
            "has_role": bool,
            "user_role": str,
            "required_role": str
        }
    """
    try:
        logger.info(f"[INTERNAL] Validating role for {login_id}: {required_role}")
        
        service = get_internal_service()
        user = await service.get_user_details(login_id)
        if not user:
            raise UserNotFoundException(login_id)
        
        has_role = user["role"] == required_role
        
        logger.info(f"[INTERNAL] Role validation result: {has_role}")
        
        return {
            "has_role": has_role,
            "user_role": user["role"],
            "required_role": required_role,
            "user_id": user["user_id"]
        }
    
    except UserNotFoundException as e:
        logger.error(f"[INTERNAL] User not found: {login_id}")
        raise HTTPException(status_code=404, detail=e.detail)
    
    except Exception as e:
        logger.error(f"[INTERNAL] Error validating role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/users/{user_id}/role",
    response_model=dict,
)
async def get_user_role(user_id: int):
    """
    Get user role by user_id.
    
    **Internal Use Only** - For role-based authorization
    
    Args:
        user_id: User identifier
    
    Returns:
        dict: {
            "user_id": int,
            "role": str,
            "is_active": bool
        }
    """
    try:
        logger.info(f"[INTERNAL] Fetching role for user_id: {user_id}")
        
        service = get_internal_service()
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user["user_id"],
            "role": user["role"],
            "is_active": user["is_active"],
            "login_id": user["login_id"]
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"[INTERNAL] Error fetching role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/users/{login_id}/status",
    response_model=dict,
)
async def get_user_status(login_id: str):
    """
    Get user active status.
    
    **Internal Use Only** - For status validation
    
    Args:
        login_id: User login identifier
    
    Returns:
        dict: {
            "user_id": int,
            "login_id": str,
            "is_active": bool,
            "role": str
        }
    """
    try:
        logger.info(f"[INTERNAL] Checking status for: {login_id}")
        
        service = get_internal_service()
        user = await service.get_user_details(login_id)
        if not user:
            raise UserNotFoundException(login_id)
        
        return {
            "user_id": user["user_id"],
            "login_id": user["login_id"],
            "is_active": user["is_active"],
            "role": user["role"]
        }
    
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.detail)
    
    except Exception as e:
        logger.error(f"[INTERNAL] Error checking status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/users/bulk-validate",
    response_model=dict,
)
async def bulk_validate_users(
    login_ids: List[str] = Body(..., description="List of login_ids to validate")
):
    """
    Validate multiple users exist and are active.
    
    **Internal Use Only** - For batch operations
    
    Args:
        login_ids: List of login identifiers
    
    Returns:
        dict: {
            "valid_users": List[dict],
            "invalid_users": List[str],
            "total_valid": int,
            "total_invalid": int
        }
    """
    try:
        logger.info(f"[INTERNAL] Bulk validating {len(login_ids)} users")
        
        valid_users = []
        invalid_users = []
        
        for login_id in login_ids:
            user = await internal_service.get_user_details(login_id)
            
            if user and user["is_active"]:
                valid_users.append({
                    "user_id": user["user_id"],
                    "login_id": user["login_id"],
                    "role": user["role"]
                })
            else:
                invalid_users.append(login_id)
        
        logger.info(f"[INTERNAL] Bulk validation: {len(valid_users)} valid, {len(invalid_users)} invalid")
        
        return {
            "valid_users": valid_users,
            "invalid_users": invalid_users,
            "total_valid": len(valid_users),
            "total_invalid": len(invalid_users)
        }
    
    except Exception as e:
        logger.error(f"[INTERNAL] Error in bulk validation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/users",
    response_model=dict,
)
async def search_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
):
    """
    Search users by criteria.
    
    **Internal Use Only** - For service-to-service queries
    
    Args:
        role: Filter by role (CUSTOMER, TELLER, ADMIN)
        is_active: Filter by active status
        limit: Maximum number of results
    
    Returns:
        dict: {
            "users": List[dict],
            "total_count": int,
            "filters": dict
        }
    """
    try:
        logger.info(f"[INTERNAL] Searching users with filters - role: {role}, active: {is_active}")
        
        # Get all users
        all_users = await internal_service.repo.get_all_users()
        
        # Apply filters
        filtered_users = all_users
        
        if role:
            filtered_users = [u for u in filtered_users if u["role"] == role]
        
        if is_active is not None:
            filtered_users = [u for u in filtered_users if u["is_active"] == is_active]
        
        # Apply limit
        filtered_users = filtered_users[:limit]
        
        # Format response
        users_data = [
            {
                "user_id": u["user_id"],
                "login_id": u["login_id"],
                "username": u["username"],
                "role": u["role"],
                "is_active": u["is_active"]
            }
            for u in filtered_users
        ]
        
        logger.info(f"[INTERNAL] Search returned {len(users_data)} results")
        
        return {
            "users": users_data,
            "total_count": len(users_data),
            "filters": {
                "role": role,
                "is_active": is_active,
                "limit": limit
            }
        }
    
    except Exception as e:
        logger.error(f"[INTERNAL] Error searching users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/health",
    response_model=dict,
)
async def health_check():
    """
    Health check endpoint for internal services.
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": "user-management",
        "version": "1.0.0"
    }
