"""
Pydantic Models for Authentication Service

Request/Response models with strict validation.

Author: GDB Architecture Team
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    login_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User login identifier (username or ID)",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User password",
    )


class TokenResponse(BaseModel):
    """Response model for successful login (JWT token)."""
    
    access_token: str = Field(
        ...,
        description="JWT access token",
    )
    token_type: str = Field(
        "Bearer",
        description="Token type (always 'Bearer')",
    )
    expires_in: int = Field(
        ...,
        description="Token expiry time in seconds",
    )
    user_id: int = Field(
        ...,
        description="User ID (from User Service)",
    )
    login_id: str = Field(
        ...,
        description="User login identifier",
    )
    role: str = Field(
        ...,
        description="User role (ADMIN, TELLER, CUSTOMER)",
    )


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    error: str = Field(
        ...,
        description="Error code or type",
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
    )
    status_code: int = Field(
        ...,
        description="HTTP status code",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error timestamp",
    )


class AuthToken(BaseModel):
    """Internal model for auth token data in database."""
    
    id: str  # UUID
    user_id: int  # BIGINT from User Service
    login_id: str
    token_jti: str  # JWT ID from token
    issued_at: datetime
    expires_at: datetime
    is_revoked: bool = False


class AuthAuditLog(BaseModel):
    """Internal model for audit log entries."""
    
    id: str  # UUID
    login_id: str
    user_id: Optional[int] = None  # BIGINT from User Service (None if user not found)
    action: str  # LOGIN_SUCCESS, LOGIN_FAILURE, TOKEN_REVOKED
    reason: Optional[str] = None  # Error reason if failure
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
