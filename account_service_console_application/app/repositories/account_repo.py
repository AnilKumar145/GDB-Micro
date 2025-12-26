"""
Account Service - Account Repository

Data access layer for account operations using SQLite (sync).

Author: GDB Architecture Team
"""

import logging
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

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
    """Repository for account data access using SQLite."""
    
    def __init__(self):
        """Initialize repository."""
        self.db = get_db()
    
    def create_savings_account(self, account: SavingsAccountCreate, pin_hash: str) -> int:
        """
        Create a new savings account.
        
        Args:
            account: SavingsAccountCreate model
            pin_hash: Hashed PIN
            
        Returns:
            Account number
            
        Raises:
            DuplicateConstraintError: If name+DOB combo exists
            DatabaseError: On database error
        """
        try:
            # Convert date string to date object if needed
            dob = account.date_of_birth
            if isinstance(dob, str):
                dob = datetime.strptime(dob, "%Y-%m-%d").date()
            
            # Insert into accounts table with explicit sequence call for account_number
            result = self.db.fetch_one("""
                INSERT INTO accounts 
                (account_number, account_type, name, pin_hash, balance, privilege, is_active, activated_date)
                VALUES (nextval('account_number_seq'), $1, $2, $3, $4, $5, TRUE, CURRENT_TIMESTAMP)
                RETURNING account_number
            """, "SAVINGS", account.name, pin_hash, 0.00, account.privilege)
            
            account_number = result['account_number']
            
            # Validate account number format
            if not AccountNumberGenerator.is_valid_account_number(account_number):
                raise DatabaseError(f"Invalid account number generated: {account_number}")
            
            # Insert into savings_account_details table
            self.db.execute("""
                INSERT INTO savings_account_details 
                (account_number, date_of_birth, gender, phone_no)
                VALUES ($1, $2, $3, $4)
            """, account_number, dob, account.gender, account.phone_no)
            
            logger.info(f"✅ Savings account created: {account_number}")
            return account_number
                
        except DuplicateConstraintError:
            raise
        except Exception as e:
            logger.error(f"❌ Error creating savings account: {e}")
            raise DatabaseError(str(e))
    
    def create_current_account(self, account: CurrentAccountCreate, pin_hash: str) -> int:
        """
        Create a new current account.
        
        Args:
            account: CurrentAccountCreate model
            pin_hash: Hashed PIN
            
        Returns:
            Account number
            
        Raises:
            DuplicateConstraintError: If registration_no exists
            DatabaseError: On database error
        """
        try:
            # Insert into accounts table with explicit sequence call for account_number
            result = self.db.fetch_one("""
                INSERT INTO accounts 
                (account_number, account_type, name, pin_hash, balance, privilege, is_active, activated_date)
                VALUES (nextval('account_number_seq'), $1, $2, $3, $4, $5, TRUE, CURRENT_TIMESTAMP)
                RETURNING account_number
            """, "CURRENT", account.name, pin_hash, 0.00, account.privilege)
            
            account_number = result['account_number']
            
            # Validate account number format
            if not AccountNumberGenerator.is_valid_account_number(account_number):
                raise DatabaseError(f"Invalid account number generated: {account_number}")
            
            # Insert into current_account_details table
            self.db.execute("""
                INSERT INTO current_account_details 
                (account_number, company_name, website, registration_no)
                VALUES ($1, $2, $3, $4)
            """, account_number, account.company_name, account.website, account.registration_no)
            
            logger.info(f"✅ Current account created: {account_number}")
            return account_number
                
        except DuplicateConstraintError:
            raise
        except Exception as e:
            logger.error(f"❌ Error creating current account: {e}")
            raise DatabaseError(str(e))
    
    def get_account(self, account_number: int) -> Optional[AccountDetailsResponse]:
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
            row = self.db.fetch_one("""
                SELECT 
                    account_number, account_type, name, balance::numeric(15,2) as balance,
                    privilege, is_active, activated_date, closed_date
                FROM accounts
                WHERE account_number = $1
            """, account_number)
            
            if not row:
                return None
            
            # Convert balance to float
            balance_value = float(row['balance']) if row['balance'] is not None else 0.0
            
            return AccountDetailsResponse(
                account_number=row['account_number'],
                account_type=row['account_type'],
                name=row['name'],
                balance=balance_value,
                privilege=row['privilege'],
                is_active=row['is_active'],
                activated_date=row['activated_date'],
                closed_date=row['closed_date']
            )
            
        except Exception as e:
            logger.error(f"❌ Error fetching account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def get_account_balance(self, account_number: int) -> Optional[float]:
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
            balance = self.db.fetch_val("""
                SELECT balance FROM accounts WHERE account_number = $1
            """, account_number)
            
            return float(balance) if balance is not None else None
            
        except Exception as e:
            logger.error(f"❌ Error fetching balance for {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def debit_account(self, account_number: int, amount: float) -> bool:
        """
        Debit amount from account (WITHDRAW/TRANSFER FROM).
        
        Args:
            account_number: Account to debit
            amount: Amount to debit (positive value)
            
        Returns:
            True if successful
            
        Raises:
            DatabaseError: On database error
        """
        try:
            with self.db.transaction() as cursor:
                # Perform debit with check
                result = self.db.fetch_val("""
                    UPDATE accounts
                    SET balance = balance - $1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE account_number = $2 
                    AND balance >= $1
                    AND is_active = TRUE
                    RETURNING 1
                """, amount, account_number)
                
                if not result:
                    logger.warning(f"⚠️ Debit failed for {account_number}: insufficient balance or inactive")
                    return False
                
                logger.info(f"✅ Debit successful: {account_number}, Amount: ₹{amount}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error debiting account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def credit_account(self, account_number: int, amount: float) -> bool:
        """
        Credit amount to account (DEPOSIT/TRANSFER TO).
        
        Args:
            account_number: Account to credit
            amount: Amount to credit (positive value)
            
        Returns:
            True if successful
            
        Raises:
            DatabaseError: On database error
        """
        try:
            with self.db.transaction() as cursor:
                # Perform credit
                result = self.db.fetch_val("""
                    UPDATE accounts
                    SET balance = balance + $1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE account_number = $2
                    AND is_active = TRUE
                    RETURNING 1
                """, amount, account_number)
                
                if not result:
                    logger.warning(f"⚠️ Credit failed for {account_number}: account not found or inactive")
                    return False
                
                logger.info(f"✅ Credit successful: {account_number}, Amount: ₹{amount}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error crediting account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def get_pin_hash(self, account_number: int) -> Optional[str]:
        """
        Get PIN hash for account.
        
        Args:
            account_number: Account number
            
        Returns:
            PIN hash or None if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            pin_hash = self.db.fetch_val("""
                SELECT pin_hash FROM accounts WHERE account_number = $1
            """, account_number)
            
            return pin_hash
            
        except Exception as e:
            logger.error(f"❌ Error fetching PIN hash for {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def update_account(self, account_number: int, update: AccountUpdate) -> bool:
        """
        Update account details.
        
        Args:
            account_number: Account to update
            update: AccountUpdate model
            
        Returns:
            True if updated
            
        Raises:
            DatabaseError: On database error
        """
        try:
            with self.db.transaction() as cursor:
                # Update accounts table
                update_fields = []
                update_values = []
                param_count = 1
                
                if update.name:
                    update_fields.append(f"name = ${param_count}")
                    update_values.append(update.name)
                    param_count += 1
                
                if update.privilege:
                    update_fields.append(f"privilege = ${param_count}")
                    update_values.append(update.privilege)
                    param_count += 1
                
                if not update_fields:
                    return True  # Nothing to update
                
                update_fields.append(f"updated_at = ${param_count}")
                update_values.append(datetime.utcnow())
                param_count += 1
                
                update_values.append(account_number)
                
                query = f"""
                    UPDATE accounts
                    SET {', '.join(update_fields)}
                    WHERE account_number = ${param_count}
                """
                
                cursor.execute(query, update_values)
                
                if cursor.rowcount == 0:
                    return False
                
                # Update account-type-specific table if needed
                if update.phone_no:
                    cursor.execute("""
                        UPDATE savings_account_details
                        SET phone_no = $1
                        WHERE account_number = $2
                    """, (update.phone_no, account_number))
                
                if update.website:
                    cursor.execute("""
                        UPDATE current_account_details
                        SET website = $1
                        WHERE account_number = $2
                    """, (update.website, account_number))
                
                logger.info(f"✅ Account updated: {account_number}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def activate_account(self, account_number: int) -> bool:
        """
        Activate an account.
        
        Args:
            account_number: Account to activate
            
        Returns:
            True if activated
            
        Raises:
            DatabaseError: On database error
        """
        try:
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE accounts
                    SET is_active = TRUE, updated_at = $1
                    WHERE account_number = $2
                    AND is_active = FALSE
                """, (datetime.utcnow(), account_number))
                
                if cursor.rowcount == 0:
                    return False
                
                logger.info(f"✅ Account activated: {account_number}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error activating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def inactivate_account(self, account_number: int) -> bool:
        """
        Inactivate an account.
        
        Args:
            account_number: Account to inactivate
            
        Returns:
            True if inactivated
            
        Raises:
            DatabaseError: On database error
        """
        try:
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE accounts
                    SET is_active = FALSE, updated_at = $1
                    WHERE account_number = $2
                    AND is_active = TRUE
                """, (datetime.utcnow(), account_number))
                
                if cursor.rowcount == 0:
                    return False
                
                logger.info(f"✅ Account inactivated: {account_number}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error inactivating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def close_account(self, account_number: int) -> bool:
        """
        Close an account.
        
        Args:
            account_number: Account to close
            
        Returns:
            True if closed
            
        Raises:
            DatabaseError: On database error
        """
        try:
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE accounts
                    SET is_active = FALSE, closed_date = $1, updated_at = $2
                    WHERE account_number = $3
                """, (datetime.utcnow(), datetime.utcnow(), account_number))
                
                if cursor.rowcount == 0:
                    return False
                
                logger.info(f"✅ Account closed: {account_number}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error closing account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    def list_accounts(self, limit: int = 100, offset: int = 0) -> list:
        """
        List all accounts with pagination.
        
        Args:
            limit: Number of records to fetch
            offset: Number of records to skip
            
        Returns:
            List of AccountDetailsResponse
            
        Raises:
            DatabaseError: On database error
        """
        try:
            rows = self.db.fetch_all("""
                SELECT 
                    account_number, account_type, name, balance,
                    privilege, is_active, activated_date, closed_date
                FROM accounts
                ORDER BY account_number DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)
            
            accounts = []
            for row in rows:
                balance_value = float(row['balance']) if row['balance'] is not None else 0.0
                
                activated_date = row['activated_date']
                if isinstance(activated_date, str):
                    activated_date = datetime.fromisoformat(activated_date)
                
                closed_date = row['closed_date']
                if isinstance(closed_date, str) and closed_date:
                    closed_date = datetime.fromisoformat(closed_date)
                else:
                    closed_date = None
                
                accounts.append(AccountDetailsResponse(
                    account_number=row['account_number'],
                    account_type=row['account_type'],
                    name=row['name'],
                    balance=balance_value,
                    privilege=row['privilege'],
                    is_active=row['is_active'],
                    activated_date=activated_date,
                    closed_date=closed_date
                ))
            
            return accounts
            
        except Exception as e:
            logger.error(f"❌ Error listing accounts: {e}")
            raise DatabaseError(str(e))
    
    def search_accounts(self, search_term: str) -> list:
        """
        Search accounts by name or account number.
        
        Args:
            search_term: Search term (name or account number)
            
        Returns:
            List of matching accounts
            
        Raises:
            DatabaseError: On database error
        """
        try:
            # Try parsing as account number first
            try:
                acc_num = int(search_term)
                rows = self.db.fetch_all("""
                    SELECT 
                        account_number, account_type, name, balance,
                        privilege, is_active, activated_date, closed_date
                    FROM accounts
                    WHERE account_number = $1
                """, acc_num)
            except ValueError:
                # Search by name
                rows = self.db.fetch_all("""
                    SELECT 
                        account_number, account_type, name, balance,
                        privilege, is_active, activated_date, closed_date
                    FROM accounts
                    WHERE name LIKE $1
                    ORDER BY account_number DESC
                """, f"%{search_term}%")
            
            accounts = []
            for row in rows:
                balance_value = float(row['balance']) if row['balance'] is not None else 0.0
                
                activated_date = row['activated_date']
                if isinstance(activated_date, str):
                    activated_date = datetime.fromisoformat(activated_date)
                
                closed_date = row['closed_date']
                if isinstance(closed_date, str) and closed_date:
                    closed_date = datetime.fromisoformat(closed_date)
                else:
                    closed_date = None
                
                accounts.append(AccountDetailsResponse(
                    account_number=row['account_number'],
                    account_type=row['account_type'],
                    name=row['name'],
                    balance=balance_value,
                    privilege=row['privilege'],
                    is_active=row['is_active'],
                    activated_date=activated_date,
                    closed_date=closed_date
                ))
            
            return accounts
            
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"❌ Error searching accounts: {e}")
            raise DatabaseError(str(e))
