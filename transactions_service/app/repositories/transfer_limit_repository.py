"""
Transfer Limit Repository

Handles database operations for transfer limits and daily tracking.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
from app.database.db import database
from app.models.enums import PrivilegeLevel

logger = logging.getLogger(__name__)


class TransferLimitRepository:
    """Repository for transfer limit operations."""

    @staticmethod
    async def get_daily_used_amount(
        account_number: int,
        date: Optional[datetime] = None
    ) -> Decimal:
        """
        Get total amount transferred today.
        
        Args:
            account_number: Account number
            date: Date to check (defaults to today)
            
        Returns:
            Total amount used today
        """
        if not date:
            date = datetime.utcnow()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = """
            SELECT COALESCE(SUM(transfer_amount), 0) as total
            FROM fund_transfers
            WHERE from_account = $1
            AND transaction_type = 'TRANSFER'
            AND status = 'SUCCESS'
            AND created_at >= $2
            AND created_at < $3
        """
        
        conn = await database.get_connection()
        try:
            row = await conn.fetchrow(
                query,
                account_number,
                start_of_day,
                end_of_day
            )
            total = row['total'] if row else Decimal('0')
            return Decimal(str(total))
        finally:
            await database._pool.release(conn)

    @staticmethod
    async def get_daily_transaction_count(
        account_number: int,
        date: Optional[datetime] = None
    ) -> int:
        """
        Get number of transfers today.
        
        Args:
            account_number: Account number
            date: Date to check (defaults to today)
            
        Returns:
            Number of transactions today
        """
        if not date:
            date = datetime.utcnow()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = """
            SELECT COUNT(*) as count
            FROM fund_transfers
            WHERE from_account = $1
            AND transaction_type = 'TRANSFER'
            AND status = 'SUCCESS'
            AND created_at >= $2
            AND created_at < $3
        """
        
        conn = await database.get_connection()
        try:
            row = await conn.fetchrow(
                query,
                account_number,
                start_of_day,
                end_of_day
            )
            return row['count'] if row else 0
        finally:
            await database._pool.release(conn)

    @staticmethod
    async def get_transfer_rule(privilege_level: str) -> Optional[Dict[str, Any]]:
        """
        Get transfer limit rules for a privilege level.
        
        Args:
            privilege_level: Privilege level (PREMIUM, GOLD, SILVER, BASIC)
            
        Returns:
            Transfer rule dict or None
        """
        query = """
            SELECT * FROM transfer_rules
            WHERE privilege_level = $1
        """
        
        conn = await database.get_connection()
        try:
            row = await conn.fetchrow(query, privilege_level)
            return dict(row) if row else None
        finally:
            await database._pool.release(conn)

    @staticmethod
    async def create_transfer_rule(
        privilege_level: str,
        daily_limit: Decimal,
        daily_transaction_count: int
    ) -> bool:
        """
        Create or update a transfer rule.
        
        Args:
            privilege_level: Privilege level
            daily_limit: Daily transfer limit
            daily_transaction_count: Daily transaction count limit
            
        Returns:
            True if successful
        """
        query = """
            INSERT INTO transfer_rules (
                privilege_level, daily_limit, daily_transaction_count, created_at
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (privilege_level)
            DO UPDATE SET
                daily_limit = $2,
                daily_transaction_count = $3
        """
        
        try:
            conn = await database.get_connection()
            try:
                await conn.execute(
                    query,
                    privilege_level,
                    float(daily_limit),
                    daily_transaction_count,
                    datetime.utcnow()
                )
                logger.info(f"✅ Transfer rule for {privilege_level} created/updated")
                return True
            finally:
                await database._pool.release(conn)
        except Exception as e:
            logger.error(f"❌ Failed to create transfer rule: {str(e)}")
            return False

    @staticmethod
    async def get_all_transfer_rules() -> list[Dict[str, Any]]:
        """
        Get all transfer rules.
        
        Returns:
            List of transfer rules
        """
        query = "SELECT * FROM transfer_rules ORDER BY daily_limit DESC"
        
        conn = await database.get_connection()
        try:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
        finally:
            await database._pool.release(conn)
