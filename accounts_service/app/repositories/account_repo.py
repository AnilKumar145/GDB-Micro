"""
Accounts Service - Account Repository

Data access layer for account operations using raw SQL.
No ORM - pure asyncpg.

Author: GDB Architecture Team
"""

import logging
from typing import Optional, List
from datetime import datetime, date
import asyncpg

from app.database.db import get_db
from app.exceptions.account_exceptions import (
    DatabaseError,
    AccountNotFoundError,
    DuplicateConstraintError
)
from app.models.account import (
    AccountDetailsResponse,
    SavingsAccountCreate,
    CurrentAccountCreate,
    AccountUpdate
)
from app.utils.helpers import AccountNumberGenerator

logger = logging.getLogger(__name__)


class AccountRepository:
    """
    Repository for account data access.
    
    Provides methods for CRUD operations on accounts.
    Uses raw SQL with asyncpg for type safety.
    """
    
    def __init__(self):
        """Initialize repository."""
        self.db = get_db()
    
    async def create_savings_account(self, account: SavingsAccountCreate, pin_hash: str) -> int:
        """
        Create a new savings account.
        
        Args:
            account: SavingsAccountCreate model
            pin_hash: Hashed PIN
            
        Returns:
            Account number (auto-generated)
            
        Raises:
            DuplicateConstraintError: If name+DOB combo exists
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Generate account number from sequence (starts at 1000)
                account_number = await conn.fetchval(
                    "SELECT nextval('account_number_seq')"
                )
                
                # Validate account number format
                if not AccountNumberGenerator.is_valid_account_number(account_number):
                    raise DatabaseError(f"Invalid account number generated: {account_number}")
                
                # Insert into accounts table with explicit account_number
                await conn.execute("""
                    INSERT INTO accounts 
                    (account_number, account_type, name, pin_hash, balance, privilege, is_active, activated_date)
                    VALUES ($1, $2, $3, $4, $5, $6, TRUE, CURRENT_TIMESTAMP)
                """, account_number, "SAVINGS", account.name, pin_hash, 0.00, account.privilege)
                
                # Parse date_of_birth from string to date object
                dob = datetime.strptime(account.date_of_birth, "%Y-%m-%d").date()
                
                # Insert into savings_account_details table
                await conn.execute("""
                    INSERT INTO savings_account_details 
                    (account_number, date_of_birth, gender, phone_no)
                    VALUES ($1, $2, $3, $4)
                """, account_number, dob, account.gender, account.phone_no)
                
                logger.info(f"✅ Savings account created: {account_number}")
                return account_number
                
        except asyncpg.UniqueViolationError as e:
            if "unique_savings_holder" in str(e) or "unique" in str(e).lower():
                raise DuplicateConstraintError("name + DOB")
            raise DatabaseError(str(e))
        except asyncpg.IntegrityConstraintViolationError as e:
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"❌ Error creating savings account: {e}")
            raise DatabaseError(str(e))
    
    async def create_current_account(self, account: CurrentAccountCreate, pin_hash: str) -> int:
        """
        Create a new current account.
        
        Args:
            account: CurrentAccountCreate model
            pin_hash: Hashed PIN
            
        Returns:
            Account number (auto-generated)
            
        Raises:
            DuplicateConstraintError: If registration_no exists
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Generate account number from sequence (starts at 1000)
                account_number = await conn.fetchval(
                    "SELECT nextval('account_number_seq')"
                )
                
                # Validate account number format
                if not AccountNumberGenerator.is_valid_account_number(account_number):
                    raise DatabaseError(f"Invalid account number generated: {account_number}")
                
                # Insert into accounts table with explicit account_number
                await conn.execute("""
                    INSERT INTO accounts 
                    (account_number, account_type, name, pin_hash, balance, privilege, is_active, activated_date)
                    VALUES ($1, $2, $3, $4, $5, $6, TRUE, CURRENT_TIMESTAMP)
                """, account_number, "CURRENT", account.name, pin_hash, 0.00, account.privilege)
                
                # Insert into current_account_details table
                await conn.execute("""
                    INSERT INTO current_account_details 
                    (account_number, company_name, website, registration_no)
                    VALUES ($1, $2, $3, $4)
                """, account_number, account.company_name, account.website, account.registration_no)
                
                logger.info(f"✅ Current account created: {account_number}")
                return account_number
                
        except asyncpg.UniqueViolationError as e:
            if "registration_no" in str(e):
                raise DuplicateConstraintError("registration_no")
            raise DatabaseError(str(e))
        except asyncpg.IntegrityConstraintViolationError as e:
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"❌ Error creating current account: {e}")
            raise DatabaseError(str(e))
    
    async def get_account(self, account_number: int) -> Optional[AccountDetailsResponse]:
        """
        Fetch account details.
        
        Args:
            account_number: Account number to fetch
            
        Returns:
            AccountDetailsResponse or None if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            row = await self.db.fetch_one("""
                SELECT 
                    account_number, account_type, name, balance, 
                    privilege, is_active, activated_date, closed_date
                FROM accounts
                WHERE account_number = $1
            """, account_number)
            
            if not row:
                return None
            
            return AccountDetailsResponse(
                account_number=row['account_number'],
                account_type=row['account_type'],
                name=row['name'],
                balance=float(row['balance']),
                privilege=row['privilege'],
                is_active=row['is_active'],
                activated_date=row['activated_date'],
                closed_date=row['closed_date']
            )
            
        except Exception as e:
            logger.error(f"❌ Error fetching account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def get_account_balance(self, account_number: int) -> Optional[float]:
        """
        Get account balance.
        
        Args:
            account_number: Account number
            
        Returns:
            Balance or None if account doesn't exist
            
        Raises:
            DatabaseError: On database error
        """
        try:
            balance = await self.db.fetch_val("""
                SELECT balance FROM accounts WHERE account_number = $1
            """, account_number)
            
            return float(balance) if balance is not None else None
            
        except Exception as e:
            logger.error(f"❌ Error fetching balance for {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def debit_account(
        self,
        account_number: int,
        amount: float,
        idempotency_key: Optional[str] = None
    ) -> bool:
        """
        Debit amount from account (WITHDRAW/TRANSFER FROM).
        
        Uses idempotency key for at-most-once semantics.
        
        Args:
            account_number: Account to debit
            amount: Amount to debit (positive value)
            idempotency_key: Idempotency key for retry safety
            
        Returns:
            True if successful
            
        Raises:
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Check idempotency
                if idempotency_key:
                    existing = await conn.fetchval("""
                        SELECT 1 FROM transactions 
                        WHERE idempotency_key = $1 AND status = 'SUCCESS'
                    """, idempotency_key)
                    
                    if existing:
                        logger.info(f"⚠️ Debit already processed: {idempotency_key}")
                        return True
                
                # Perform debit with check
                result = await conn.execute("""
                    UPDATE accounts
                    SET balance = balance - $1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE account_number = $2 
                    AND balance >= $1
                    AND is_active = TRUE
                """, amount, account_number)
                
                if result == "UPDATE 0":
                    logger.warning(f"⚠️ Debit failed for {account_number}: insufficient balance or inactive")
                    return False
                
                logger.info(f"✅ Debit successful: {account_number}, Amount: ₹{amount}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error debiting account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def credit_account(
        self,
        account_number: int,
        amount: float,
        idempotency_key: Optional[str] = None
    ) -> bool:
        """
        Credit amount to account (DEPOSIT/TRANSFER TO).
        
        Uses idempotency key for at-most-once semantics.
        
        Args:
            account_number: Account to credit
            amount: Amount to credit (positive value)
            idempotency_key: Idempotency key for retry safety
            
        Returns:
            True if successful
            
        Raises:
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Check idempotency
                if idempotency_key:
                    existing = await conn.fetchval("""
                        SELECT 1 FROM transactions 
                        WHERE idempotency_key = $1 AND status = 'SUCCESS'
                    """, idempotency_key)
                    
                    if existing:
                        logger.info(f"⚠️ Credit already processed: {idempotency_key}")
                        return True
                
                # Perform credit
                result = await conn.execute("""
                    UPDATE accounts
                    SET balance = balance + $1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE account_number = $2
                    AND is_active = TRUE
                """, amount, account_number)
                
                if result == "UPDATE 0":
                    logger.warning(f"⚠️ Credit failed for {account_number}: account not found or inactive")
                    return False
                
                logger.info(f"✅ Credit successful: {account_number}, Amount: ₹{amount}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error crediting account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def update_account(self, account_number: int, update: AccountUpdate) -> bool:
        """
        Update account details.
        
        Args:
            account_number: Account to update
            update: AccountUpdate model with changes
            
        Returns:
            True if updated, False if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            # Build dynamic update query
            updates = []
            values = []
            param_count = 1
            
            if update.name:
                updates.append(f"name = ${param_count}")
                values.append(update.name)
                param_count += 1
            
            if update.privilege:
                updates.append(f"privilege = ${param_count}")
                values.append(update.privilege)
                param_count += 1
            
            if not updates:
                return True  # Nothing to update
            
            updates.append(f"updated_at = CURRENT_TIMESTAMP")
            values.append(account_number)
            
            query = f"""
                UPDATE accounts
                SET {', '.join(updates)}
                WHERE account_number = ${param_count}
            """
            
            result = await self.db.execute(query, *values)
            
            if result == "UPDATE 0":
                return False
            
            logger.info(f"✅ Account updated: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def activate_account(self, account_number: int) -> bool:
        """
        Activate an account.
        
        Args:
            account_number: Account to activate
            
        Returns:
            True if activated, False if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            result = await self.db.execute("""
                UPDATE accounts
                SET is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_number = $1
            """, account_number)
            
            if result == "UPDATE 0":
                return False
            
            logger.info(f"✅ Account activated: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error activating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def inactivate_account(self, account_number: int) -> bool:
        """
        Inactivate an account.
        
        Args:
            account_number: Account to inactivate
            
        Returns:
            True if inactivated, False if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            result = await self.db.execute("""
                UPDATE accounts
                SET is_active = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_number = $1
            """, account_number)
            
            if result == "UPDATE 0":
                return False
            
            logger.info(f"✅ Account inactivated: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inactivating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def close_account(self, account_number: int) -> bool:
        """
        Close an account (soft delete).
        
        Args:
            account_number: Account to close
            
        Returns:
            True if closed, False if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            result = await self.db.execute("""
                UPDATE accounts
                SET is_active = FALSE,
                    closed_date = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_number = $1
            """, account_number)
            
            if result == "UPDATE 0":
                return False
            
            logger.info(f"✅ Account closed: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error closing account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def get_pin_hash(self, account_number: int) -> Optional[str]:
        """
        Get PIN hash for an account (for verification).
        
        Args:
            account_number: Account number
            
        Returns:
            PIN hash or None
            
        Raises:
            DatabaseError: On database error
        """
        try:
            return await self.db.fetch_val("""
                SELECT pin_hash FROM accounts WHERE account_number = $1
            """, account_number)
            
        except Exception as e:
            logger.error(f"❌ Error fetching PIN hash: {e}")
            raise DatabaseError(str(e))
