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
from app.models.enums import TransactionType, TransactionStatus
from app.config.settings import settings

logger = logging.getLogger(__name__)


class TransactionLogRepository:
    """Repository for transaction logging."""

    @staticmethod
    async def log_to_database(
        account_number: int,
        amount: Decimal,
        transaction_type: TransactionType,
        status: TransactionStatus,
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
            status: Transaction status
            reference_id: Transaction ID reference
            description: Optional description
            
        Returns:
            True if logged successfully
        """
        query = """
            INSERT INTO transaction_logs (
                account_number, amount, transaction_type,
                status, reference_id, description, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        try:
            conn = await database.get_connection()
            try:
                await conn.execute(
                    query,
                    account_number,
                    float(amount),
                    transaction_type.value,
                    status.value,
                    reference_id,
                    description,
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
        status: TransactionStatus,
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
            status: Transaction status
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
                f"Status: {status.value} | "
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
            SELECT * FROM transaction_logs
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
        limit: int = 10
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Get all logs for an account.
        
        Args:
            account_number: Account number
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (list of logs, total count)
        """
        count_query = """
            SELECT COUNT(*) as count
            FROM transaction_logs
            WHERE account_number = $1
        """
        
        data_query = """
            SELECT * FROM transaction_logs
            WHERE account_number = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """
        
        conn = await database.get_connection()
        try:
            count_row = await conn.fetchrow(count_query, account_number)
            total_count = count_row['count'] if count_row else 0
            
            rows = await conn.fetch(data_query, account_number, limit, skip)
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
            DELETE FROM transaction_logs
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
