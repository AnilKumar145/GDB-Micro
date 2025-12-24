"""
Accounts Service - Account Business Logic Service

High-level business logic for account management.
Orchestrates repository and validation layer.

Author: GDB Architecture Team
"""

import logging
from typing import Optional

from app.repositories.account_repo import AccountRepository
from app.models.account import (
    SavingsAccountCreate,
    CurrentAccountCreate,
    AccountUpdate,
    AccountResponse,
    SavingsAccountResponse,
    CurrentAccountResponse,
    AccountDetailsResponse
)
from app.exceptions.account_exceptions import (
    AccountNotFoundError,
    AccountInactiveError,
    AccountClosedError,
    InsufficientFundsError,
    InvalidPinError,
    AccountAlreadyActiveError,
    AccountAlreadyInactiveError
)
from app.utils.validators import (
    validate_age,
    validate_pin,
    validate_phone_number,
    validate_name,
    validate_company_name,
    validate_registration_number,
    validate_privilege
)
from app.utils.encryption import EncryptionManager
from app.utils.helpers import mask_account_number, generate_idempotency_key

logger = logging.getLogger(__name__)


class AccountService:
    """
    Business logic service for account operations.
    
    Provides high-level methods for account management.
    Coordinates with repository and validation.
    """
    
    def __init__(self):
        """Initialize service."""
        self.repo = AccountRepository()
        self.encryption = EncryptionManager()
    
    async def create_savings_account(
        self,
        account: SavingsAccountCreate
    ) -> int:
        """
        Create a new savings account.
        
        Validates:
        - Age >= 18
        - Valid DOB format
        - Valid PIN
        - Valid phone number
        - Unique name + DOB combination
        
        Args:
            account: SavingsAccountCreate model
            
        Returns:
            Account number
            
        Raises:
            AgeRestrictionError: If age < 18
            ValidationError: If validation fails
            DuplicateConstraintError: If name+DOB exists
        """
        # Validate all inputs
        validate_name(account.name)
        validate_age(account.date_of_birth, min_age=18)
        validate_pin(account.pin)
        validate_phone_number(account.phone_no, country="IN")
        validate_privilege(account.privilege)
        
        # Hash PIN
        pin_hash = self.encryption.hash_pin(account.pin)
        
        # Create account in database
        account_number = await self.repo.create_savings_account(account, pin_hash)
        
        logger.info(f"✅ Savings account service created: {account_number}")
        return account_number
    
    async def create_current_account(
        self,
        account: CurrentAccountCreate
    ) -> int:
        """
        Create a new current account.
        
        Validates:
        - Valid PIN
        - Valid company name
        - Valid registration number
        
        Args:
            account: CurrentAccountCreate model
            
        Returns:
            Account number
            
        Raises:
            ValidationError: If validation fails
            DuplicateConstraintError: If registration_no exists
        """
        # Validate all inputs
        validate_name(account.name)
        validate_pin(account.pin)
        validate_company_name(account.company_name)
        validate_registration_number(account.registration_no)
        validate_privilege(account.privilege)
        
        # Hash PIN
        pin_hash = self.encryption.hash_pin(account.pin)
        
        # Create account in database
        account_number = await self.repo.create_current_account(account, pin_hash)
        
        logger.info(f"✅ Current account service created: {account_number}")
        return account_number
    
    async def get_account_details(
        self,
        account_number: int
    ) -> AccountDetailsResponse:
        """
        Get account details.
        
        Args:
            account_number: Account number
            
        Returns:
            AccountDetailsResponse
            
        Raises:
            AccountNotFoundError: If account doesn't exist
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        return account
    
    async def get_balance(self, account_number: int) -> float:
        """
        Get account balance.
        
        Checks that account is active.
        
        Args:
            account_number: Account number
            
        Returns:
            Account balance
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            AccountInactiveError: If account is not active
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        if not account.is_active:
            raise AccountInactiveError(account_number)
        
        return account.balance
    
    async def verify_pin(self, account_number: int, pin: str) -> bool:
        """
        Verify account PIN.
        
        Args:
            account_number: Account number
            pin: PIN to verify
            
        Returns:
            True if PIN is correct
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            InvalidPinError: If PIN is incorrect
        """
        pin_hash = await self.repo.get_pin_hash(account_number)
        
        if not pin_hash:
            raise AccountNotFoundError(account_number)
        
        if not self.encryption.verify_pin(pin, pin_hash):
            raise InvalidPinError("PIN verification failed")
        
        return True
    
    async def debit_account(
        self,
        account_number: int,
        amount: float,
        description: str = "Withdrawal",
        idempotency_key: str = None
    ) -> bool:
        """
        Debit amount from account.
        
        Checks:
        - Account exists and is active
        - Account is not closed
        - Sufficient funds
        
        Args:
            account_number: Account to debit
            amount: Amount (positive value)
            description: Transaction description
            idempotency_key: For retry safety
            
        Returns:
            True if successful
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            AccountInactiveError: If account is inactive
            AccountClosedError: If account is closed
            InsufficientFundsError: If insufficient balance
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        if not account.is_active:
            raise AccountInactiveError(account_number)
        
        if account.closed_date is not None:
            raise AccountClosedError(account_number)
        
        if account.balance < amount:
            raise InsufficientFundsError(account.balance, amount)
        
        # Perform debit
        success = await self.repo.debit_account(
            account_number,
            amount,
            idempotency_key
        )
        
        if not success:
            raise InsufficientFundsError(account.balance, amount)
        
        logger.info(f"✅ Debit successful for {account_number}: ₹{amount}")
        return True
    
    async def credit_account(
        self,
        account_number: int,
        amount: float,
        description: str = "Deposit",
        idempotency_key: str = None
    ) -> bool:
        """
        Credit amount to account.
        
        Checks:
        - Account exists and is active
        - Account is not closed
        
        Args:
            account_number: Account to credit
            amount: Amount (positive value)
            description: Transaction description
            idempotency_key: For retry safety
            
        Returns:
            True if successful
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            AccountInactiveError: If account is inactive
            AccountClosedError: If account is closed
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        if not account.is_active:
            raise AccountInactiveError(account_number)
        
        if account.closed_date is not None:
            raise AccountClosedError(account_number)
        
        # Perform credit
        success = await self.repo.credit_account(
            account_number,
            amount,
            idempotency_key
        )
        
        if not success:
            raise AccountNotFoundError(account_number)
        
        logger.info(f"✅ Credit successful for {account_number}: ₹{amount}")
        return True
    
    async def update_account(
        self,
        account_number: int,
        update: AccountUpdate
    ) -> bool:
        """
        Update account details.
        
        Args:
            account_number: Account to update
            update: AccountUpdate model
            
        Returns:
            True if updated
            
        Raises:
            AccountNotFoundError: If account doesn't exist
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        # Validate updated fields
        if update.name:
            validate_name(update.name)
        
        if update.privilege:
            validate_privilege(update.privilege)
        
        # Update in database
        success = await self.repo.update_account(account_number, update)
        
        if not success:
            raise AccountNotFoundError(account_number)
        
        logger.info(f"✅ Account updated: {account_number}")
        return True
    
    async def activate_account(self, account_number: int) -> bool:
        """
        Activate an account.
        
        Args:
            account_number: Account to activate
            
        Returns:
            True if activated
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            AccountAlreadyActiveError: If account is already active
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        # Check if account is already active
        if account.is_active:
            raise AccountAlreadyActiveError(account_number)
        
        success = await self.repo.activate_account(account_number)
        
        if not success:
            raise AccountNotFoundError(account_number)
        
        logger.info(f"✅ Account activated: {account_number}")
        return True
    
    async def inactivate_account(self, account_number: int) -> bool:
        """
        Inactivate an account.
        
        Args:
            account_number: Account to inactivate
            
        Returns:
            True if inactivated
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            AccountAlreadyInactiveError: If account is already inactive
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        # Check if account is already inactive
        if not account.is_active:
            raise AccountAlreadyInactiveError(account_number)
        
        success = await self.repo.inactivate_account(account_number)
        
        if not success:
            raise AccountNotFoundError(account_number)
        
        logger.info(f"✅ Account inactivated: {account_number}")
        return True
    
    async def close_account(self, account_number: int) -> bool:
        """
        Close an account.
        
        Args:
            account_number: Account to close
            
        Returns:
            True if closed
            
        Raises:
            AccountNotFoundError: If account doesn't exist
        """
        account = await self.repo.get_account(account_number)
        
        if not account:
            raise AccountNotFoundError(account_number)
        
        # Check balance before closing (must be zero or negative)
        if account.balance > 0:
            logger.warning(f"⚠️ Account {account_number} has remaining balance: ₹{account.balance}")
        
        success = await self.repo.close_account(account_number)
        
        if not success:
            raise AccountNotFoundError(account_number)
        
        logger.info(f"✅ Account closed: {account_number}")
        return True
