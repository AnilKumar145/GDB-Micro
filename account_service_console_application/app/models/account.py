"""
Account Service - Account Models

Data models for account objects.

Author: GDB Architecture Team
"""

from datetime import datetime
from typing import Optional, Literal


class AccountBase:
    """Base account model with common fields."""
    
    def __init__(self, name: str, privilege: Literal["PREMIUM", "GOLD", "SILVER"] = "SILVER"):
        self.name = name
        self.privilege = privilege


class SavingsAccountCreate(AccountBase):
    """Request model for creating savings account."""
    
    def __init__(
        self,
        name: str,
        pin: str,
        date_of_birth: str,
        gender: Literal["Male", "Female", "Others"],
        phone_no: str,
        privilege: Literal["PREMIUM", "GOLD", "SILVER"] = "SILVER"
    ):
        super().__init__(name, privilege)
        self.account_type = "SAVINGS"
        self.pin = pin
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.phone_no = phone_no


class CurrentAccountCreate(AccountBase):
    """Request model for creating current account."""
    
    def __init__(
        self,
        name: str,
        pin: str,
        company_name: str,
        registration_no: str,
        website: Optional[str] = None,
        privilege: Literal["PREMIUM", "GOLD", "SILVER"] = "SILVER"
    ):
        super().__init__(name, privilege)
        self.account_type = "CURRENT"
        self.pin = pin
        self.company_name = company_name
        self.registration_no = registration_no
        self.website = website


class AccountUpdate:
    """Request model for updating account."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        privilege: Optional[Literal["PREMIUM", "GOLD", "SILVER"]] = None,
        phone_no: Optional[str] = None,
        website: Optional[str] = None
    ):
        self.name = name
        self.privilege = privilege
        self.phone_no = phone_no
        self.website = website


class AccountResponse:
    """Response model for account details."""
    
    def __init__(
        self,
        account_number: int,
        account_type: Literal["SAVINGS", "CURRENT"],
        name: str,
        balance: float,
        privilege: Literal["PREMIUM", "GOLD", "SILVER"],
        is_active: bool,
        activated_date: datetime,
        closed_date: Optional[datetime] = None
    ):
        self.account_number = account_number
        self.account_type = account_type
        self.name = name
        self.balance = balance
        self.privilege = privilege
        self.is_active = is_active
        self.activated_date = activated_date
        self.closed_date = closed_date


class SavingsAccountResponse(AccountResponse):
    """Response model for savings account with details."""
    
    def __init__(
        self,
        account_number: int,
        name: str,
        balance: float,
        privilege: str,
        is_active: bool,
        activated_date: datetime,
        date_of_birth: str,
        gender: str,
        phone_no: str,
        closed_date: Optional[datetime] = None
    ):
        super().__init__(
            account_number,
            "SAVINGS",
            name,
            balance,
            privilege,
            is_active,
            activated_date,
            closed_date
        )
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.phone_no = phone_no


class CurrentAccountResponse(AccountResponse):
    """Response model for current account with details."""
    
    def __init__(
        self,
        account_number: int,
        name: str,
        balance: float,
        privilege: str,
        is_active: bool,
        activated_date: datetime,
        company_name: str,
        registration_no: str,
        website: Optional[str] = None,
        closed_date: Optional[datetime] = None
    ):
        super().__init__(
            account_number,
            "CURRENT",
            name,
            balance,
            privilege,
            is_active,
            activated_date,
            closed_date
        )
        self.company_name = company_name
        self.registration_no = registration_no
        self.website = website


class BalanceResponse:
    """Response model for balance query."""
    
    def __init__(self, account_number: int, balance: float, currency: str = "INR"):
        self.account_number = account_number
        self.balance = balance
        self.currency = currency


class AccountDetailsResponse:
    """Response model for account details (internal use)."""
    
    def __init__(
        self,
        account_number: int,
        account_type: Literal["SAVINGS", "CURRENT"],
        name: str,
        balance: float,
        privilege: Literal["PREMIUM", "GOLD", "SILVER"],
        is_active: bool,
        activated_date: datetime,
        closed_date: Optional[datetime] = None
    ):
        self.account_number = account_number
        self.account_type = account_type
        self.name = name
        self.balance = balance
        self.privilege = privilege
        self.is_active = is_active
        self.activated_date = activated_date
        self.closed_date = closed_date
