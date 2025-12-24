"""
Response Models for Transaction Service

Pydantic models for API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.models.enums import TransactionType, TransactionStatus, TransferMode


class TransactionResponse(BaseModel):
    """Response model for successful transaction."""
    
    status: str = Field(..., description="Transaction status (SUCCESS/FAILED)")
    transaction_id: int = Field(..., description="Transaction ID")
    amount: Decimal = Field(..., description="Transaction amount")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    account_number: Optional[int] = Field(None, description="Account number")
    from_account: Optional[int] = Field(None, description="Source account (for transfers)")
    to_account: Optional[int] = Field(None, description="Destination account (for transfers)")
    transaction_date: datetime = Field(..., description="Transaction timestamp")
    description: Optional[str] = Field(None, description="Transaction description")
    new_balance: Optional[Decimal] = Field(None, description="New account balance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "transaction_id": 1001,
                "amount": "5000.00",
                "transaction_type": "DEPOSIT",
                "account_number": 1001,
                "transaction_date": "2024-12-24T10:30:00",
                "description": "Salary deposit",
                "new_balance": "105000.00"
            }
        }


class DepositResponse(TransactionResponse):
    """Response model for deposit operation."""
    pass


class WithdrawResponse(TransactionResponse):
    """Response model for withdrawal operation."""
    pass


class TransferResponse(BaseModel):
    """Response model for transfer operation."""
    
    status: str = Field(..., description="Transfer status")
    transaction_id: int = Field(..., description="Transaction ID")
    from_account: int = Field(..., description="Source account")
    to_account: int = Field(..., description="Destination account")
    amount: Decimal = Field(..., description="Transfer amount")
    transfer_mode: TransferMode = Field(..., description="Transfer mode")
    transaction_date: datetime = Field(..., description="Transfer timestamp")
    description: Optional[str] = Field(None, description="Transfer description")
    from_account_new_balance: Optional[Decimal] = Field(None, description="Source account new balance")
    to_account_new_balance: Optional[Decimal] = Field(None, description="Destination account new balance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "transaction_id": 1001,
                "from_account": 1001,
                "to_account": 1002,
                "amount": "5000.00",
                "transfer_mode": "INTERNAL",
                "transaction_date": "2024-12-24T10:30:00",
                "description": "Payment to friend",
                "from_account_new_balance": "95000.00",
                "to_account_new_balance": "105000.00"
            }
        }


class TransferLimitResponse(BaseModel):
    """Response model for transfer limit query."""
    
    account_number: int = Field(..., description="Account number")
    privilege_level: str = Field(..., description="Account privilege level")
    daily_limit: Decimal = Field(..., description="Daily transfer limit")
    used_today: Decimal = Field(..., description="Amount used today")
    remaining: Decimal = Field(..., description="Remaining limit for today")
    transaction_count_today: int = Field(..., description="Transactions done today")
    transaction_count_limit: int = Field(..., description="Daily transaction limit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_number": 1001,
                "privilege_level": "PREMIUM",
                "daily_limit": "100000.00",
                "used_today": "30000.00",
                "remaining": "70000.00",
                "transaction_count_today": 3,
                "transaction_count_limit": 50
            }
        }


class TransactionLogResponse(BaseModel):
    """Response model for a transaction log entry."""
    
    log_id: int = Field(..., description="Log entry ID")
    account_number: int = Field(..., description="Account number")
    amount: Decimal = Field(..., description="Transaction amount")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    transaction_date: datetime = Field(..., description="Transaction timestamp")
    reference_id: int = Field(..., description="Transaction/Reference ID")
    status: TransactionStatus = Field(..., description="Transaction status")
    created_at: datetime = Field(..., description="Log creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_id": 1,
                "account_number": 1001,
                "amount": "5000.00",
                "transaction_type": "WITHDRAW",
                "transaction_date": "2024-12-24T10:30:00",
                "reference_id": 1001,
                "status": "SUCCESS",
                "created_at": "2024-12-24T10:30:01"
            }
        }


class TransactionLogsListResponse(BaseModel):
    """Response model for list of transaction logs."""
    
    account_number: int = Field(..., description="Account number")
    total_count: int = Field(..., description="Total number of logs")
    skip: int = Field(..., description="Records skipped")
    limit: int = Field(..., description="Records returned")
    logs: List[TransactionLogResponse] = Field(..., description="List of transaction logs")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: datetime = Field(..., description="Error timestamp")
    details: Optional[str] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Insufficient balance",
                "error_code": "INSUFFICIENT_FUNDS",
                "timestamp": "2024-12-24T10:30:00",
                "details": "Account balance is ₹5000, but withdrawal of ₹10000 was requested"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Timestamp")
    version: str = Field(..., description="API version")
