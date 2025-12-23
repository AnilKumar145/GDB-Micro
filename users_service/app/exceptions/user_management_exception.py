"""
Custom exceptions for User Management Service.
All user-related errors inherit from UserManagementException.
"""

from fastapi import HTTPException
from typing import Optional


class UserManagementException(HTTPException):
    """
    Base exception for all user management operations.

    Attributes:
        status_code: HTTP status code
        detail: Error message
        error_code: Custom error code for client handling
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "USER_MANAGEMENT_ERROR",
    ):
        """Initialize UserManagementException."""
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class UserAlreadyExistsException(UserManagementException):
    """Raised when attempting to create a user with existing login_id."""

    def __init__(self, login_id: str):
        """Initialize UserAlreadyExistsException."""
        super().__init__(
            status_code=409,
            detail=f"User with login_id '{login_id}' already exists",
            error_code="USER_ALREADY_EXISTS",
        )


class UserNotFoundException(UserManagementException):
    """Raised when user is not found in database."""

    def __init__(self, login_id: str):
        """Initialize UserNotFoundException."""
        super().__init__(
            status_code=404,
            detail=f"User with login_id '{login_id}' not found",
            error_code="USER_NOT_FOUND",
        )


class UserInactiveException(UserManagementException):
    """Raised when attempting to edit an inactive user."""

    def __init__(self, login_id: str):
        """Initialize UserInactiveException."""
        super().__init__(
            status_code=403,
            detail=f"User with login_id '{login_id}' is inactive",
            error_code="USER_INACTIVE",
        )


class UserAlreadyInactiveException(UserManagementException):
    """Raised when attempting to inactivate an already inactive user."""

    def __init__(self, login_id: str):
        """Initialize UserAlreadyInactiveException."""
        super().__init__(
            status_code=400,
            detail=f"User with login_id '{login_id}' is already inactive",
            error_code="USER_ALREADY_INACTIVE",
        )


class InvalidUserInputException(UserManagementException):
    """Raised when user input validation fails."""

    def __init__(self, field: str, reason: str):
        """Initialize InvalidUserInputException."""
        super().__init__(
            status_code=400,
            detail=f"Invalid {field}: {reason}",
            error_code="INVALID_USER_INPUT",
        )


class DatabaseException(UserManagementException):
    """Raised when database operation fails."""

    def __init__(self, operation: str, reason: str):
        """Initialize DatabaseException."""
        super().__init__(
            status_code=500,
            detail=f"Database error during {operation}: {reason}",
            error_code="DATABASE_ERROR",
        )


class InvalidRoleException(UserManagementException):
    """Raised when an invalid role is provided."""

    def __init__(self, role: str, valid_roles: Optional[list] = None):
        """Initialize InvalidRoleException."""
        valid_roles_str = ", ".join(valid_roles) if valid_roles else "CUSTOMER, TELLER, ADMIN"
        super().__init__(
            status_code=400,
            detail=f"Invalid role '{role}'. Valid roles are: {valid_roles_str}",
            error_code="INVALID_ROLE",
        )


class UserAlreadyActiveException(UserManagementException):
    """Raised when attempting to activate an already active user."""

    def __init__(self, login_id: str):
        """Initialize UserAlreadyActiveException."""
        super().__init__(
            status_code=400,
            detail=f"User with login_id '{login_id}' is already active",
            error_code="USER_ALREADY_ACTIVE",
        )
