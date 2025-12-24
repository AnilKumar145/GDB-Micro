"""
Transaction Repository

Handles all database operations for transactions table.
Uses raw SQL with asyncpg (no ORM).
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
from app.database.db import database
from app.models.enums import TransactionType, TransactionStatus

logger = logging.getLogger(__name__)


class TransactionRepository:
    """Repository for transaction CRUD operations."""

    @staticmethod
    async def create_transaction(
        from_account: Optional[int],
        to_account: Optional[int],
        amount: Decimal,
        transaction_type: TransactionType,
        status: TransactionStatus,
        description: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> int:
        """
        Create a new transaction record.
        
        Args:
            from_account: Source account (None for deposit)
            to_account: Destination account (None for withdrawal)
            amount: Transaction amount
            transaction_type: Type of transaction
            status: Transaction status
            description: Transaction description
            idempotency_key: For idempotency
            error_message: Error message if failed
            
        Returns:
            transaction_id of created record
        """
        query = """
            INSERT INTO fund_transfers (
                from_account, to_account, transfer_amount,
                transaction_type, status, description,
                idempotency_key, error_message, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING transaction_id
        """
        
        try:
            conn = await database.get_connection()
            try:
                transaction_id = await conn.fetchval(
                    query,
                    from_account,
                    to_account,
                    float(amount),
                    transaction_type.value,
                    status.value,
                    description,
                    idempotency_key,
                    error_message,
                    datetime.utcnow()
                )
                logger.info(f"✅ Transaction {transaction_id} created")
                return transaction_id
            finally:
                await database._pool.release(conn)
        except asyncpg.UniqueViolationError:
            # Idempotency key already exists
            query = "SELECT transaction_id FROM fund_transfers WHERE idempotency_key = $1"
            conn = await database.get_connection()
            try:
                transaction_id = await conn.fetchval(query, idempotency_key)
                return transaction_id
            finally:
                await database._pool.release(conn)

    @staticmethod
    async def get_transaction(transaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Get transaction details by ID.
        
        Args:
            transaction_id: Transaction ID to fetch
            
        Returns:
            Transaction dict or None if not found
        """
        query = "SELECT * FROM fund_transfers WHERE transaction_id = $1"
        
        conn = await database.get_connection()
        try:
            row = await conn.fetchrow(query, transaction_id)
            return dict(row) if row else None
        finally:
            await database._pool.release(conn)

    @staticmethod
    async def get_account_transactions(
        account_number: int,
        skip: int = 0,
        limit: int = 10,
        days: int = 30
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Get transactions for an account.
        
        Args:
            account_number: Account to fetch transactions for
            skip: Number of records to skip
            limit: Number of records to return
            days: Days to look back
            
        Returns:
            Tuple of (list of transactions, total count)
        """
        from_date = datetime.utcnow() - timedelta(days=days)
        
        # Get total count
        count_query = """
            SELECT COUNT(*) as count FROM fund_transfers
            WHERE (from_account = $1 OR to_account = $1)
            AND created_at >= $2
        """
        
        # Get records
        data_query = """
            SELECT * FROM fund_transfers
            WHERE (from_account = $1 OR to_account = $1)
            AND created_at >= $2
            ORDER BY created_at DESC
            LIMIT $3 OFFSET $4
        """
        
        conn = await database.get_connection()
        try:
            count_row = await conn.fetchrow(count_query, account_number, from_date)
            total_count = count_row['count'] if count_row else 0
            
            rows = await conn.fetch(data_query, account_number, from_date, limit, skip)
            transactions = [dict(row) for row in rows]
            
            return transactions, total_count
        finally:
            await database._pool.release(conn)

    @staticmethod
    async def update_transaction_status(
        transaction_id: int,
        status: TransactionStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update transaction status.
        
        Args:
            transaction_id: Transaction to update
            status: New status
            error_message: Error message if failed
            
        Returns:
            True if updated successfully
        """
        query = """
            UPDATE fund_transfers
            SET status = $1, error_message = $2
            WHERE transaction_id = $3
        """
        
        conn = await database.get_connection()
        try:
            result = await conn.execute(
                query,
                status.value,
                error_message,
                transaction_id
            )
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update transaction {transaction_id}: {str(e)}")
            return False
        finally:
            await database._pool.release(conn)

    @staticmethod
    async def get_daily_transactions(
        account_number: int,
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all transactions for an account on a specific day.
        
        Args:
            account_number: Account number
            date: Date to filter (defaults to today)
            
        Returns:
            List of transactions
        """
        if not date:
            date = datetime.utcnow()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = """
            SELECT * FROM fund_transfers
            WHERE (from_account = $1 OR to_account = $1)
            AND created_at >= $2
            AND created_at < $3
            ORDER BY created_at DESC
        """
        
        conn = await database.get_connection()
        try:
            rows = await conn.fetch(query, account_number, start_of_day, end_of_day)
            return [dict(row) for row in rows]
        finally:
            await database._pool.release(conn)
