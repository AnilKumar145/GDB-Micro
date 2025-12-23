"""
Accounts Service - Custom Exceptions

Defines all account-specific exceptions following banking standards.

Author: GDB Architecture Team
"""


class AccountException(Exception):
    """Base exception for all account-related errors."""
    
    def __init__(self, message: str, error_code: str = "ACCOUNT_ERROR"):
        """
        Initialize account exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
        """
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


class AccountAlreadyExistsError(AccountException):
    """Raised when account already exists."""
    
    def __init__(self, name: str, dob: str = None):
        msg = f"Account with name '{name}'"
        if dob:
            msg += f" and DOB '{dob}'"
        msg += " already exists"
        super().__init__(msg, "ACCOUNT_ALREADY_EXISTS")


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
            f"Insufficient funds. Balance: ₹{balance}, Required: ₹{required}",
            "INSUFFICIENT_FUNDS"
        )


class InvalidBalanceError(AccountException):
    """Raised when balance operation is invalid."""
    
    def __init__(self, message: str = "Invalid balance operation"):
        super().__init__(message, "INVALID_BALANCE")


class InvalidAccountTypeError(AccountException):
    """Raised when account type is invalid."""
    
    def __init__(self, account_type: str):
        super().__init__(
            f"Invalid account type: {account_type}. Must be SAVINGS or CURRENT",
            "INVALID_ACCOUNT_TYPE"
        )


class InvalidPrivilegeError(AccountException):
    """Raised when privilege level is invalid."""
    
    def __init__(self, privilege: str):
        super().__init__(
            f"Invalid privilege: {privilege}. Must be PREMIUM, GOLD, or SILVER",
            "INVALID_PRIVILEGE"
        )


class InvalidPinError(AccountException):
    """Raised when PIN is invalid."""
    
    def __init__(self, message: str = "PIN verification failed"):
        super().__init__(message, "INVALID_PIN")


class AgeRestrictionError(AccountException):
    """Raised when account holder is underage."""
    
    def __init__(self, age: int):
        super().__init__(
            f"Account holder must be at least 18 years old (Current age: {age})",
            "AGE_RESTRICTION"
        )


class ValidationError(AccountException):
    """Raised when validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            f"Validation error in {field}: {message}",
            "VALIDATION_ERROR"
        )


class OperationNotAllowedError(AccountException):
    """Raised when operation is not allowed on account."""
    
    def __init__(self, account_number: int, reason: str):
        super().__init__(
            f"Operation not allowed on account {account_number}: {reason}",
            "OPERATION_NOT_ALLOWED"
        )


class DatabaseError(AccountException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            f"Database error: {message}",
            "DATABASE_ERROR"
        )


class ConcurrencyError(AccountException):
    """Raised when concurrent operation causes conflict."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Concurrent operation on account {account_number}. Please retry",
            "CONCURRENCY_ERROR"
        )


class DuplicateConstraintError(AccountException):
    """Raised when unique constraint is violated."""
    
    def __init__(self, constraint: str):
        super().__init__(
            f"Duplicate value violates constraint: {constraint}",
            "DUPLICATE_CONSTRAINT"
        )
