"""
FastAPI Authorization Dependencies

Reusable FastAPI dependencies for JWT validation and role-based access control.
Services can inject these into their route handlers for automatic authorization.

Author: GDB Architecture Team
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, Header, status, HTTPException

from .jwt_validation import JWTValidator, RoleChecker

logger = logging.getLogger(__name__)


# Configuration object (should be set by the service at startup)
_jwt_config = None


def set_jwt_config(secret_key: str, algorithm: str = "HS256"):
    """
    Set the JWT configuration for the service.
    Call this during service initialization.
    
    Args:
        secret_key: Secret key for JWT validation
        algorithm: JWT algorithm (default: HS256)
    """
    global _jwt_config
    _jwt_config = {
        "secret_key": secret_key,
        "algorithm": algorithm,
    }


def get_jwt_config() -> Dict[str, Any]:
    """Get the current JWT configuration."""
    if not _jwt_config:
        raise RuntimeError(
            "JWT config not initialized. Call set_jwt_config() during startup."
        )
    return _jwt_config


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Extract and validate JWT from Authorization header.
    Returns JWT claims.
    
    Usage in route:
    ```python
    @router.get("/protected")
    async def protected_route(claims: Dict = Depends(get_current_user)):
        user_id = claims["user_id"]
        login_id = claims["login_id"]
        role = claims["role"]
    ```
    
    Args:
        authorization: Authorization header value
    
    Returns:
        Dictionary of JWT claims (user_id, login_id, role, etc.)
    
    Raises:
        HTTPException(401): If token is missing or invalid
    """
    config = get_jwt_config()
    
    # Extract token from header
    token = JWTValidator.extract_token_from_header(authorization)
    
    # Validate token
    claims = JWTValidator.validate_token(
        token=token,
        secret_key=config["secret_key"],
        algorithm=config["algorithm"],
    )
    
    return claims


async def get_current_user_id(
    claims: Dict[str, Any] = Depends(get_current_user),
) -> int:
    """
    Extract user_id from JWT claims.
    
    Usage in route:
    ```python
    @router.get("/profile")
    async def get_profile(user_id: int = Depends(get_current_user_id)):
        # user_id is already extracted and validated
    ```
    
    Args:
        claims: JWT claims from get_current_user dependency
    
    Returns:
        User ID (integer)
    
    Raises:
        HTTPException(401): If user_id is missing or invalid
    """
    return JWTValidator.get_user_id(claims)


async def get_current_user_role(
    claims: Dict[str, Any] = Depends(get_current_user),
) -> str:
    """
    Extract user role from JWT claims.
    
    Usage in route:
    ```python
    @router.get("/admin-only")
    async def admin_endpoint(role: str = Depends(get_current_user_role)):
        if role != "ADMIN":
            raise HTTPException(403, "Admin access required")
    ```
    
    Args:
        claims: JWT claims from get_current_user dependency
    
    Returns:
        User role (ADMIN, TELLER, or CUSTOMER)
    
    Raises:
        HTTPException(401): If role is missing or invalid
    """
    return JWTValidator.get_role(claims)


def require_role(*allowed_roles: str):
    """
    Create a dependency that requires the user to have one of the specified roles.
    
    Usage in route:
    ```python
    @router.post("/admin-action")
    async def admin_action(
        claims: Dict = Depends(require_role("ADMIN"))
    ):
        # Only ADMIN users can access this endpoint
    ```
    
    Args:
        allowed_roles: Variable number of allowed role strings
    
    Returns:
        Dependency function
    
    Raises:
        HTTPException(403): If user role not in allowed_roles
    """
    async def check_role(
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """Check if user role is in allowed roles."""
        user_role = JWTValidator.get_role(claims)
        RoleChecker.require_role(user_role, list(allowed_roles))
        return claims
    
    return check_role


def require_admin():
    """
    Create a dependency that requires ADMIN role.
    
    Usage in route:
    ```python
    @router.delete("/users/{user_id}")
    async def delete_user(
        user_id: int,
        claims: Dict = Depends(require_admin())
    ):
        # Only ADMIN users can delete users
    ```
    
    Returns:
        Dependency function that returns JWT claims if authorized
    
    Raises:
        HTTPException(403): If user is not ADMIN
    """
    return require_role("ADMIN")


def require_admin_or_teller():
    """
    Create a dependency that requires ADMIN or TELLER role.
    
    Usage in route:
    ```python
    @router.post("/accounts")
    async def create_account(
        request: AccountCreate,
        claims: Dict = Depends(require_admin_or_teller())
    ):
        # Only ADMIN or TELLER can create accounts
    ```
    
    Returns:
        Dependency function that returns JWT claims if authorized
    
    Raises:
        HTTPException(403): If user is not ADMIN or TELLER
    """
    return require_role("ADMIN", "TELLER")


def require_customer_or_teller():
    """
    Create a dependency that requires CUSTOMER or TELLER role.
    
    Returns:
        Dependency function that returns JWT claims if authorized
    
    Raises:
        HTTPException(403): If user is not CUSTOMER or TELLER
    """
    return require_role("CUSTOMER", "TELLER")


# Pre-created dependencies for common role requirements  
require_admin_dependency = require_role("ADMIN")
require_teller_dependency = require_role("TELLER")
require_customer_dependency = require_role("CUSTOMER")
require_admin_or_teller_dependency = require_role("ADMIN", "TELLER")
require_customer_or_teller_dependency = require_role("CUSTOMER", "TELLER")
