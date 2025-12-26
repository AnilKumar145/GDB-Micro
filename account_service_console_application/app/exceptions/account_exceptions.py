"""
Account Service - Custom Exceptions

Defines all account-specific exceptions.

Author: GDB Architecture Team
"""


class AccountException(Exception):
    """Base exception for all account-related errors."""
    
    def __init__(self, message: str, error_code: str = "ACCOUNT_ERROR"):
        """Initialize account exception."""
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AccountNotFoundError(AccountException):
    """Raised when account does not exist."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} not found",
            "ACCOUNT_NOT_FOUND"
        )


class AccountInactiveError(AccountException):
    """Raised when trying to operate on inactive account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is inactive",
            "ACCOUNT_INACTIVE"
        )


class AccountClosedError(AccountException):
    """Raised when trying to operate on closed account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is closed",
            "ACCOUNT_CLOSED"
        )


class InsufficientFundsError(AccountException):
    """Raised when account balance is insufficient for transaction."""
    
    def __init__(self, balance: float, required: float):
        super().__init__(
            f"Insufficient funds. Balance: ₹{balance:.2f}, Required: ₹{required:.2f}",
            "INSUFFICIENT_FUNDS"
        )


class InvalidPinError(AccountException):
    """Raised when PIN is invalid."""
    
    def __init__(self, message: str = "Invalid PIN"):
        super().__init__(message, "INVALID_PIN")


class AgeRestrictionError(AccountException):
    """Raised when age is below minimum requirement."""
    
    def __init__(self, age: int, min_age: int = 18):
        super().__init__(
            f"Age restriction failed. You are {age} years old, minimum required is {min_age}",
            "AGE_RESTRICTION"
        )


class ValidationError(AccountException):
    """Raised when validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            f"Validation failed for {field}: {message}",
            "VALIDATION_ERROR"
        )


class DuplicateConstraintError(AccountException):
    """Raised when unique constraint is violated."""
    
    def __init__(self, field: str):
        super().__init__(
            f"Duplicate value for {field}",
            "DUPLICATE_CONSTRAINT"
        )


class DatabaseError(AccountException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            f"Database error: {message}",
            "DATABASE_ERROR"
        )


class AccountAlreadyActiveError(AccountException):
    """Raised when trying to activate an already active account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is already active",
            "ACCOUNT_ALREADY_ACTIVE"
        )


class AccountAlreadyInactiveError(AccountException):
    """Raised when trying to inactivate an already inactive account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is already inactive",
            "ACCOUNT_ALREADY_INACTIVE"
        )
