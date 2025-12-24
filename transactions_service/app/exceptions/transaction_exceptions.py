"""
Custom Exceptions for Transaction Service

All exceptions with HTTP status codes and descriptive messages.
"""

from typing import Optional


class TransactionException(Exception):
    """Base exception for transaction service."""
    
    http_code: int = 400
    error_code: str = "TRANSACTION_ERROR"
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize transaction exception.
        
        Args:
            message: Human-readable error message
            error_code: Error code for categorization
        """
        super().__init__(message)
        self.message = message
        if error_code:
            self.error_code = error_code


class AccountNotFoundException(TransactionException):
    """Account does not exist."""
    
    http_code = 404
    error_code = "ACCOUNT_NOT_FOUND"


class AccountNotActiveException(TransactionException):
    """Account is not active."""
    
    http_code = 400
    error_code = "ACCOUNT_NOT_ACTIVE"


class InsufficientFundsException(TransactionException):
    """Insufficient balance for transaction."""
    
    http_code = 400
    error_code = "INSUFFICIENT_FUNDS"


class InvalidAmountException(TransactionException):
    """Invalid transaction amount."""
    
    http_code = 400
    error_code = "INVALID_AMOUNT"


class InvalidPINException(TransactionException):
    """PIN is invalid or incorrect."""
    
    http_code = 401
    error_code = "INVALID_PIN"


class InvalidAccountException(TransactionException):
    """Account is invalid or malformed."""
    
    http_code = 400
    error_code = "INVALID_ACCOUNT"


class TransferLimitExceededException(TransactionException):
    """Daily transfer limit exceeded."""
    
    http_code = 400
    error_code = "TRANSFER_LIMIT_EXCEEDED"


class DailyTransactionCountExceededException(TransactionException):
    """Daily transaction count limit exceeded."""
    
    http_code = 400
    error_code = "DAILY_TRANSACTION_COUNT_EXCEEDED"


class SameAccountTransferException(TransactionException):
    """Cannot transfer to the same account."""
    
    http_code = 400
    error_code = "SAME_ACCOUNT_TRANSFER"


class WithdrawalFailedException(TransactionException):
    """Withdrawal operation failed."""
    
    http_code = 400
    error_code = "WITHDRAWAL_FAILED"


class DepositFailedException(TransactionException):
    """Deposit operation failed."""
    
    http_code = 400
    error_code = "DEPOSIT_FAILED"


class TransferFailedException(TransactionException):
    """Transfer operation failed."""
    
    http_code = 400
    error_code = "TRANSFER_FAILED"


class TransferLimitNotFoundException(TransactionException):
    """Transfer limit not found for account."""
    
    http_code = 404
    error_code = "TRANSFER_LIMIT_NOT_FOUND"


class ServiceUnavailableException(TransactionException):
    """External service (e.g., Account Service) is unavailable."""
    
    http_code = 503
    error_code = "SERVICE_UNAVAILABLE"


class DatabaseException(TransactionException):
    """Database operation failed."""
    
    http_code = 500
    error_code = "DATABASE_ERROR"


class ValidationException(TransactionException):
    """Input validation failed."""
    
    http_code = 422
    error_code = "VALIDATION_ERROR"


class UnauthorizedException(TransactionException):
    """User is not authorized for this operation."""
    
    http_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenException(TransactionException):
    """User does not have permission for this operation."""
    
    http_code = 403
    error_code = "FORBIDDEN"


class IdempotencyException(TransactionException):
    """Idempotency key violation."""
    
    http_code = 409
    error_code = "IDEMPOTENCY_CONFLICT"


class LoggingException(TransactionException):
    """Transaction logging failed."""
    
    http_code = 500
    error_code = "LOGGING_ERROR"


class TransactionLogNotFoundException(TransactionException):
    """Transaction log not found."""
    
    http_code = 404
    error_code = "TRANSACTION_LOG_NOT_FOUND"


class AccountServiceException(TransactionException):
    """Account Service returned an error."""
    
    http_code = 502
    error_code = "ACCOUNT_SERVICE_ERROR"


# ========================================
# ADDITIONAL SPECIFIC EXCEPTIONS
# ========================================

class InvalidTransferModeException(TransactionException):
    """Invalid transfer mode specified."""
    
    http_code = 400
    error_code = "INVALID_TRANSFER_MODE"


class DailyAmountLimitException(TransactionException):
    """Daily amount limit exceeded."""
    
    http_code = 400
    error_code = "DAILY_AMOUNT_LIMIT_EXCEEDED"


class InvalidTransactionException(TransactionException):
    """Invalid transaction parameters."""
    
    http_code = 400
    error_code = "INVALID_TRANSACTION"


class TransactionLoggingException(TransactionException):
    """Transaction logging operation failed."""
    
    http_code = 500
    error_code = "TRANSACTION_LOGGING_ERROR"


class SourceAccountInactiveException(TransactionException):
    """Source account is inactive."""
    
    http_code = 400
    error_code = "SOURCE_ACCOUNT_INACTIVE"


class DestinationAccountInactiveException(TransactionException):
    """Destination account is inactive."""
    
    http_code = 400
    error_code = "DESTINATION_ACCOUNT_INACTIVE"


class BothAccountsInactiveException(TransactionException):
    """Both source and destination accounts are inactive."""
    
    http_code = 400
    error_code = "BOTH_ACCOUNTS_INACTIVE"
