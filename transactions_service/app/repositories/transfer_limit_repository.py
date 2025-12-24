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
    async def get_transfer_rule(privilege: str) -> Optional[Dict[str, Any]]:
        """
        Get transfer limit rule for a privilege level.
        Uses hardcoded rules (no database table needed).
        
        Args:
            privilege: Privilege level (PREMIUM, GOLD, SILVER)
            
        Returns:
            Dict with daily_limit and transaction_limit
        """
        rules = {
            "PREMIUM": {
                "daily_limit": 100000,      # ₹100,000 per day
                "transaction_limit": 50     # 50 transfers per day
            },
            "GOLD": {
                "daily_limit": 50000,       # ₹50,000 per day
                "transaction_limit": 25     # 25 transfers per day
            },
            "SILVER": {
                "daily_limit": 25000,       # ₹25,000 per day
                "transaction_limit": 10     # 10 transfers per day
            }
        }
        
        return rules.get(privilege.upper())

    @staticmethod
    async def get_daily_used_amount(
        account_number: int,
        date: Optional[datetime] = None
    ) -> Decimal:
        """
        Get total amount transferred today from the account.
        Queries fund_transfers table for all transactions from this account.
        
        Args:
            account_number: Account number
            date: Date to check (defaults to today)
            
        Returns:
            Total amount transferred today
        """
        if date is None:
            date = datetime.utcnow().date()
        
        try:
            conn = await database.get_connection()
            try:
                query = """
                    SELECT COALESCE(SUM(transfer_amount), 0) as total
                    FROM fund_transfers
                    WHERE from_account = $1
                    AND DATE(created_at) = $2
                """
                result = await conn.fetchrow(query, account_number, date)
                total = Decimal(str(result['total'])) if result else Decimal('0')
                logger.info(f"💰 Daily used amount for account {account_number}: ₹{total}")
                return total
            finally:
                await database._pool.release(conn)
        except Exception as e:
            logger.error(f"❌ Error getting daily used amount: {str(e)}")
            return Decimal('0')


    @staticmethod
    async def get_daily_transaction_count(
        account_number: int,
        date: Optional[datetime] = None
    ) -> int:
        """
        Get number of transfers today from the account.
        Queries fund_transfers table for all transactions from this account.
        
        Args:
            account_number: Account number
            date: Date to check (defaults to today)
            
        Returns:
            Number of transactions today
        """
        if date is None:
            date = datetime.utcnow().date()
        
        try:
            conn = await database.get_connection()
            try:
                query = """
                    SELECT COUNT(*) as cnt
                    FROM fund_transfers
                    WHERE from_account = $1
                    AND DATE(created_at) = $2
                """
                result = await conn.fetchrow(query, account_number, date)
                count = result['cnt'] if result else 0
                logger.info(f"📊 Daily transaction count for account {account_number}: {count}")
                return count
            finally:
                await database._pool.release(conn)
        except Exception as e:
            logger.error(f"❌ Error getting daily transaction count: {str(e)}")
            return 0

