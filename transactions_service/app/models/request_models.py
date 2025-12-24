"""
Request Models for Transaction Service

Pydantic models for validating incoming API requests.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional
from decimal import Decimal
from app.models.enums import TransferMode


class DepositRequest(BaseModel):
    """Request model for deposit operations."""
    
    account_number: int = Field(..., gt=0, description="Account number")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Deposit amount")
    description: Optional[str] = Field(None, max_length=500, description="Deposit description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_number": 1001,
                "amount": "10000.00",
                "description": "Salary deposit"
            }
        }
    
    @validator("amount")
    def validate_amount(cls, v):
        """Validate amount is positive and within limits."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > Decimal("999999999.99"):
            raise ValueError("Amount exceeds maximum limit")
        return v


class WithdrawRequest(BaseModel):
    """Request model for withdrawal operations."""
    
    account_number: int = Field(..., gt=0, description="Account number")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Withdrawal amount")
    pin: str = Field(..., min_length=4, max_length=4, description="Account PIN")
    description: Optional[str] = Field(None, max_length=500, description="Withdrawal description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_number": 1001,
                "amount": "5000.00",
                "pin": "1234",
                "description": "ATM withdrawal"
            }
        }
    
    @validator("amount")
    def validate_amount(cls, v):
        """Validate amount."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > Decimal("999999999.99"):
            raise ValueError("Amount exceeds maximum limit")
        return v
    
    @validator("pin")
    def validate_pin(cls, v):
        """Validate PIN is numeric."""
        if not v.isdigit():
            raise ValueError("PIN must be numeric")
        return v


class TransferRequest(BaseModel):
    """Request model for transfer operations."""
    
    from_account: int = Field(..., gt=0, description="Source account number")
    to_account: int = Field(..., gt=0, description="Destination account number")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Transfer amount")
    pin: str = Field(..., min_length=4, max_length=4, description="Account PIN")
    transfer_mode: TransferMode = Field(
        default=TransferMode.INTERNAL,
        description="Transfer mode (NEFT, RTGS, IMPS, etc.)"
    )
    description: Optional[str] = Field(None, max_length=500, description="Transfer description")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key for retry safety")
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_account": 1001,
                "to_account": 1002,
                "amount": "5000.00",
                "pin": "1234",
                "transfer_mode": "INTERNAL",
                "description": "Payment to friend"
            }
        }
    
    @validator("amount")
    def validate_amount(cls, v):
        """Validate amount."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > Decimal("999999999.99"):
            raise ValueError("Amount exceeds maximum limit")
        return v
    
    @validator("pin")
    def validate_pin(cls, v):
        """Validate PIN is numeric."""
        if not v.isdigit():
            raise ValueError("PIN must be numeric")
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_different_accounts(cls, values):
        """Ensure from_account and to_account are different."""
        from_account = values.get("from_account")
        to_account = values.get("to_account")
        
        if from_account and to_account and from_account == to_account:
            raise ValueError("Cannot transfer to the same account")
        
        return values


class TransferLimitRequest(BaseModel):
    """Request model for setting transfer limits."""
    
    account_number: int = Field(..., gt=0, description="Account number")
    daily_limit: Decimal = Field(..., gt=0, description="Daily transfer limit")
    daily_transaction_count: int = Field(..., gt=0, description="Daily transaction count limit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_number": 1001,
                "daily_limit": "100000.00",
                "daily_transaction_count": 50
            }
        }


class TransactionLogQueryRequest(BaseModel):
    """Request model for querying transaction logs."""
    
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=10, ge=1, le=1000, description="Number of records to return")
    transaction_type: Optional[str] = Field(None, description="Filter by transaction type")
    start_date: Optional[str] = Field(None, description="Filter by start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Filter by end date (YYYY-MM-DD)")
