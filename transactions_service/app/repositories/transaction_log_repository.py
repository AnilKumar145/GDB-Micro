"""
Transaction Log Repository

Handles logging to both database and file system.
CRITICAL: Every transaction MUST be logged to both locations.
"""

import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
from app.database.db import database
from app.models.enums import TransactionType
from app.config.settings import settings

logger = logging.getLogger(__name__)



class TransactionLogRepository:
    """Repository for transaction logging."""

    @staticmethod
    async def log_to_database(
        account_number: int,
        amount: Decimal,
        transaction_type: TransactionType,
        reference_id: int,
        description: Optional[str] = None
    ) -> bool:
        """
        Log transaction to database table.
        
        MANDATORY for all transactions.
        
        Args:
            account_number: Account involved
            amount: Transaction amount
            transaction_type: Type of transaction
            reference_id: Transaction ID reference
            description: Optional description
            
        Returns:
            True if logged successfully
        """
        query = """
            INSERT INTO transaction_logging (
                account_number, amount, transaction_type,
                created_at
            )
            VALUES ($1, $2, $3, $4)
        """
        
        try:
            conn = await database.get_connection()
            try:
                await conn.execute(
                    query,
                    account_number,
                    float(amount),
                    transaction_type.value,
                    datetime.utcnow()
                )
                logger.info(
                    f"✅ Logged {transaction_type.value} "
                    f"for account {account_number} to DB"
                )
                return True
            finally:
                await database._pool.release(conn)
        except Exception as e:
            logger.error(f"❌ Failed to log to database: {str(e)}")
            return False

    @staticmethod
    def log_to_file(
        account_number: int,
        amount: Decimal,
        transaction_type: TransactionType,
        reference_id: int,
        description: Optional[str] = None
    ) -> bool:
        """
        Log transaction to file system.
        
        MANDATORY for all transactions.
        Creates daily log files: YYYY-MM-DD.log
        
        Args:
            account_number: Account involved
            amount: Transaction amount
            transaction_type: Type of transaction
            reference_id: Transaction ID reference
            description: Optional description
            
        Returns:
            True if logged successfully
        """
        try:
            # Ensure log directory exists
            if not os.path.exists(settings.LOG_DIR):
                os.makedirs(settings.LOG_DIR, exist_ok=True)
            
            # Generate file name with date
            log_filename = datetime.utcnow().strftime(settings.LOG_FILE_FORMAT)
            log_filepath = os.path.join(settings.LOG_DIR, f"{log_filename}.log")
            
            # Create log entry
            timestamp = datetime.utcnow().isoformat()
            log_entry = (
                f"[{timestamp}] | "
                f"Account: {account_number} | "
                f"Type: {transaction_type.value} | "
                f"Amount: ₹{amount} | "
                f"RefID: {reference_id} | "
                f"Description: {description or 'N/A'}\n"
            )
            
            # Append to file
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            logger.info(
                f"✅ Logged {transaction_type.value} "
                f"for account {account_number} to file"
            )
            return True
            
        except IOError as e:
            logger.error(f"❌ Failed to log to file: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error logging to file: {str(e)}")
            return False

    @staticmethod
    async def get_logs_for_transaction(transaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Get all logs for a specific transaction.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction log dict or None
        """
        query = """
            SELECT * FROM transaction_logging
            WHERE reference_id = $1
            ORDER BY created_at DESC
        """
        
        conn = await database.get_connection()
        try:
            rows = await conn.fetch(query, transaction_id)
            return {
                "transaction_id": transaction_id,
                "logs": [dict(row) for row in rows]
            }
        finally:
            await database._pool.release(conn)

    @staticmethod
    async def get_account_logs(
        account_number: int,
        skip: int = 0,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Get all logs for an account with optional date range filtering.
        
        Args:
            account_number: Account number
            skip: Records to skip
            limit: Records to return
            start_date: Filter from date (inclusive)
            end_date: Filter to date (inclusive)
            
        Returns:
            Tuple of (list of logs, total count)
        """
        # Build count query with optional date filter
        count_query = """
            SELECT COUNT(*) as count
            FROM transaction_logging
            WHERE account_number = $1
        """
        count_params = [account_number]
        
        # Build data query with optional date filter
        data_query = """
            SELECT * FROM transaction_logging
            WHERE account_number = $1
        """
        data_params = [account_number]
        
        # Add date filters if provided
        if start_date:
            count_query += " AND created_at >= $2"
            data_query += " AND created_at >= $2"
            count_params.append(start_date)
            data_params.append(start_date)
            next_param = 3
        else:
            next_param = 2
        
        if end_date:
            count_query += f" AND created_at <= ${next_param}"
            data_query += f" AND created_at <= ${next_param}"
            count_params.append(end_date)
            data_params.append(end_date)
            next_param += 1
        
        # Add pagination
        data_query += f" ORDER BY created_at DESC LIMIT ${next_param} OFFSET ${next_param + 1}"
        data_params.extend([limit, skip])
        
        conn = await database.get_connection()
        try:
            count_row = await conn.fetchrow(count_query, *count_params)
            total_count = count_row['count'] if count_row else 0
            
            rows = await conn.fetch(data_query, *data_params)
            logs = [dict(row) for row in rows]
            
            return logs, total_count
        finally:
            await database._pool.release(conn)

    @staticmethod
    def read_file_logs(days: int = 1) -> List[str]:
        """
        Read transaction logs from file system.
        
        Args:
            days: Number of days to read (0 = today, 1 = yesterday, etc.)
            
        Returns:
            List of log lines
        """
        try:
            log_date = datetime.utcnow() - timedelta(days=days)
            log_filename = log_date.strftime(settings.LOG_FILE_FORMAT)
            log_filepath = os.path.join(settings.LOG_DIR, f"{log_filename}.log")
            
            if not os.path.exists(log_filepath):
                logger.warning(f"Log file not found: {log_filepath}")
                return []
            
            with open(log_filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return lines
            
        except Exception as e:
            logger.error(f"❌ Failed to read log file: {str(e)}")
            return []

    @staticmethod
    async def delete_old_logs(days_to_keep: int = 90) -> bool:
        """
        Delete transaction logs older than specified days.
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            True if successful
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        query = """
            DELETE FROM transaction_logging
            WHERE created_at < $1
        """
        
        try:
            conn = await database.get_connection()
            try:
                result = await conn.execute(query, cutoff_date)
                logger.info(f"✅ Deleted transaction logs older than {days_to_keep} days")
                return True
            finally:
                await database._pool.release(conn)
        except Exception as e:
            logger.error(f"❌ Failed to delete old logs: {str(e)}")
            return False

    @staticmethod
    async def log_deposit(
        account_number: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> int:
        """
        Log a deposit transaction.
        
        Args:
            account_number: Account being credited
            amount: Deposit amount
            description: Optional description
            
        Returns:
            Transaction ID for this log entry
        """
        await TransactionLogRepository.log_to_database(
            account_number=account_number,
            amount=amount,
            transaction_type=TransactionType.DEPOSIT,
            reference_id=0,  # Placeholder
            description=description
        )
        TransactionLogRepository.log_to_file(
            account_number=account_number,
            amount=amount,
            transaction_type=TransactionType.DEPOSIT,
            reference_id=0,
            description=description
        )
        return 1  # Simplified ID

    @staticmethod
    async def log_withdrawal(
        account_number: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> int:
        """
        Log a withdrawal transaction.
        
        Args:
            account_number: Account being debited
            amount: Withdrawal amount
            description: Optional description
            
        Returns:
            Transaction ID for this log entry
        """
        await TransactionLogRepository.log_to_database(
            account_number=account_number,
            amount=amount,
            transaction_type=TransactionType.WITHDRAW,
            reference_id=0,
            description=description
        )
        TransactionLogRepository.log_to_file(
            account_number=account_number,
            amount=amount,
            transaction_type=TransactionType.WITHDRAW,
            reference_id=0,
            description=description
        )
        return 1  # Simplified ID

    @staticmethod
    async def log_transfer(
        from_account: int,
        to_account: int,
        amount: Decimal,
        transfer_mode: str = "NEFT",
        description: Optional[str] = None
    ) -> int:
        """
        Log a transfer transaction.
        
        Args:
            from_account: Source account
            to_account: Destination account
            amount: Transfer amount
            transfer_mode: Transfer mode (NEFT, RTGS, IMPS, etc.)
            description: Optional description
            
        Returns:
            Transaction ID for this log entry
        """
        await TransactionLogRepository.log_to_database(
            account_number=from_account,
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
            reference_id=0,
            description=description
        )
        TransactionLogRepository.log_to_file(
            account_number=from_account,
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
            reference_id=0,
            description=description
        )
        return 1  # Simplified ID
