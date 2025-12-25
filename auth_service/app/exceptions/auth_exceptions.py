"""
Custom Exception Classes for Authentication Service

Specific exceptions for auth-related errors.

Author: GDB Architecture Team
"""


class AuthenticationException(Exception):
    """Base exception for authentication errors."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid."""
    
    def __init__(self, message: str = "Invalid login credentials"):
        super().__init__(message, status_code=401)


class UserInactiveException(AuthenticationException):
    """Raised when user account is inactive."""
    
    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message, status_code=403)


class UserNotFoundException(AuthenticationException):
    """Raised when user does not exist."""
    
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token is expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, status_code=401)


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, status_code=401)


class TokenRevokedException(AuthenticationException):
    """Raised when JWT token has been revoked."""
    
    def __init__(self, message: str = "Token has been revoked"):
        super().__init__(message, status_code=401)


class ServiceUnavailableException(AuthenticationException):
    """Raised when dependent service (User Service) is unavailable."""
    
    def __init__(self, message: str = "User service is unavailable"):
        super().__init__(message, status_code=503)


class DatabaseException(AuthenticationException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class InternalServerException(AuthenticationException):
    """Raised for unexpected internal errors."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)
