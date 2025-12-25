"""
Authentication API Routes

Single public endpoint for user login.
All other services handle their own authorization using tokens.

Author: GDB Architecture Team
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from app.models.models import LoginRequest, TokenResponse, ErrorResponse
from app.services.auth_service import AuthService
from app.exceptions.auth_exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
    UserInactiveException,
    UserNotFoundException,
    ServiceUnavailableException,
)


logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["authentication"],
)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    if request.client:
        return request.client.host
    return None


def get_user_agent(request: Request) -> str:
    """Extract user agent from request."""
    return request.headers.get("user-agent", "")


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request format",
        },
        401: {
            "model": ErrorResponse,
            "description": "Invalid credentials or user inactive",
        },
        404: {
            "model": ErrorResponse,
            "description": "User not found",
        },
        503: {
            "model": ErrorResponse,
            "description": "User service unavailable",
        },
    },
)
async def login(request: Request, login_request: LoginRequest) -> TokenResponse:
    """
    Authenticate user and return JWT token.
    
    This is the ONLY public authentication endpoint.
    All other microservices use the returned JWT token for requests.
    
    **Login Flow:**
    1. User submits login_id and password
    2. Auth Service fetches user from User Service
    3. Auth Service verifies password against bcrypt hash
    4. Auth Service generates JWT token (HS256, 30 min expiry)
    5. JWT token contains claims: sub (user_id), login_id, role, iat, exp, jti
    6. Token is stored in auth_tokens table
    7. Client uses token in Authorization header: "Bearer <token>"
    
    **Response:**
    - access_token: JWT token for use in Authorization header
    - token_type: Always "Bearer"
    - expires_in: Token expiry time in seconds
    - user_id: User UUID
    - login_id: User login identifier
    - role: User role (ADMIN, TELLER, CUSTOMER)
    
    **Usage:**
    - Call /api/v1/auth/login with login_id and password
    - Use returned access_token in other services:
      Authorization: Bearer <access_token>
    
    Args:
        request: FastAPI request object
        login_request: LoginRequest with login_id and password
    
    Returns:
        TokenResponse with JWT token and user info
    
    Raises:
        HTTPException(401): Invalid credentials or user inactive
        HTTPException(404): User not found
        HTTPException(503): User service unavailable
    """
    
    # Get client context
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    logger.info(f"Login attempt for {login_request.login_id} from {ip_address}")
    
    try:
        # Call authentication service
        token_data = await AuthService.login(
            login_id=login_request.login_id,
            password=login_request.password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        # Return response
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user_id=token_data["user_id"],
            login_id=token_data["login_id"],
            role=token_data["role"],
        )
    
    except UserNotFoundException as e:
        logger.warning(
            f"Login failed - user not found: {login_request.login_id}"
        )
        raise HTTPException(
            status_code=404,
            detail={"error": "user_not_found", "message": e.message},
        )
    
    except UserInactiveException as e:
        logger.warning(
            f"Login failed - user inactive: {login_request.login_id}"
        )
        raise HTTPException(
            status_code=401,
            detail={"error": "user_inactive", "message": e.message},
        )
    
    except InvalidCredentialsException as e:
        logger.warning(
            f"Login failed - invalid credentials: {login_request.login_id}"
        )
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_credentials", "message": e.message},
        )
    
    except ServiceUnavailableException as e:
        logger.error(f"Login failed - user service unavailable: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "User service is unavailable",
            },
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
            },
        )


@router.get(
    "/health",
    status_code=200,
)
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns:
        Status dict
    """
    return {
        "status": "ok",
        "service": "auth-service",
    }
