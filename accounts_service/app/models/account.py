"""
Accounts Service - Account Models

Data models for account objects using Pydantic v2.

Author: GDB Architecture Team
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class AccountBase(BaseModel):
    """Base account model with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Account holder name")
    privilege: Literal["PREMIUM", "GOLD", "SILVER"] = Field(
        default="SILVER",
        description="Account privilege level"
    )


class SavingsAccountCreate(AccountBase):
    """Request model for creating savings account."""
    
    account_type: Literal["SAVINGS"] = "SAVINGS"
    pin: str = Field(..., min_length=4, max_length=6, description="4-6 digit PIN")
    date_of_birth: str = Field(..., description="DOB in YYYY-MM-DD format")
    gender: Literal["M", "F", "OTHER"] = Field(..., description="Gender")
    phone_no: str = Field(..., min_length=10, max_length=20, description="Phone number")
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v):
        """Validate date of birth format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return v
    
    @field_validator("phone_no")
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number is numeric."""
        if not v.isdigit():
            raise ValueError("Phone number must be numeric")
        return v


class CurrentAccountCreate(AccountBase):
    """Request model for creating current account."""
    
    account_type: Literal["CURRENT"] = "CURRENT"
    pin: str = Field(..., min_length=4, max_length=6, description="4-6 digit PIN")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    website: Optional[str] = Field(None, max_length=255, description="Company website")
    registration_no: str = Field(..., min_length=1, max_length=50, description="Company registration number")


class AccountUpdate(BaseModel):
    """Request model for updating account."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    privilege: Optional[Literal["PREMIUM", "GOLD", "SILVER"]] = None
    phone_no: Optional[str] = None  # For savings accounts
    website: Optional[str] = None  # For current accounts


class AccountResponse(AccountBase):
    """Response model for account details."""
    
    account_number: int = Field(..., description="Unique account number")
    account_type: Literal["SAVINGS", "CURRENT"] = Field(..., description="Account type")
    balance: float = Field(..., description="Current account balance")
    is_active: bool = Field(..., description="Account active status")
    activated_date: datetime = Field(..., description="Account opening date")
    closed_date: Optional[datetime] = Field(None, description="Account closing date")
    
    class Config:
        from_attributes = True


class SavingsAccountResponse(AccountResponse):
    """Response model for savings account with details."""
    
    date_of_birth: str
    gender: Literal["M", "F", "OTHER"]
    phone_no: str


class CurrentAccountResponse(AccountResponse):
    """Response model for current account with details."""
    
    company_name: str
    website: Optional[str]
    registration_no: str


class BalanceResponse(BaseModel):
    """Response model for balance query."""
    
    account_number: int
    balance: float
    currency: str = "INR"


class DebitRequest(BaseModel):
    """Internal request model for debit operation."""
    
    account_number: int
    amount: float = Field(..., gt=0, description="Amount to debit")
    description: Optional[str] = None
    idempotency_key: Optional[str] = None


class CreditRequest(BaseModel):
    """Internal request model for credit operation."""
    
    account_number: int
    amount: float = Field(..., gt=0, description="Amount to credit")
    description: Optional[str] = None
    idempotency_key: Optional[str] = None


class AccountDetailsResponse(BaseModel):
    """Response model for account details (internal use)."""
    
    account_number: int
    account_type: Literal["SAVINGS", "CURRENT"]
    name: str
    balance: float
    privilege: Literal["PREMIUM", "GOLD", "SILVER"]
    is_active: bool
    activated_date: datetime
    closed_date: Optional[datetime]


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
