"""
Transfer Limit API Routes

GET /api/v1/transfer-limits/{account} - Get transfer limits
"""

import logging
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status, Query
from app.services.transfer_limit_service import transfer_limit_service
from app.exceptions.transaction_exceptions import TransactionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["transfer-limits"])


@router.get(
    "/transfer-limits/{account_number}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Transfer limits retrieved"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def get_transfer_limit(account_number: int) -> dict:
    """
    Get transfer limits for an account.

    Returns privilege-based daily transfer limit and current usage.

    **Path Parameters:**
    - account_number: Account number

    **Response:**
    - account_number: Requested account
    - privilege: PREMIUM/GOLD/SILVER/BASIC
    - daily_limit: Daily transfer limit in rupees
    - daily_used: Amount transferred today
    - daily_remaining: Limit minus usage
    - transaction_limit: Max transfers per day
    - transactions_today: Transfers made today
    - transactions_remaining: Allowed transfers minus used

    **Errors:**
    - 404: Account not found
    - 503: Account Service unavailable
    """
    logger.info(f"🔍 Get transfer limits - Account: {account_number}")

    try:
        result = await transfer_limit_service.get_transfer_limit(account_number)
        logger.info(f"✅ Transfer limits retrieved for account {account_number}")
        return result

    except TransactionException as e:
        logger.warning(f"⚠️ Failed to get transfer limits: {e.error_code}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@router.get(
    "/transfer-limits/remaining/{account_number}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Remaining limits retrieved"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def get_remaining_limit(account_number: int):
    """
    Get remaining transfer limit (quick check).

    **Path Parameters:**
    - account_number: Account number

    **Response:**
    - account_number: Account
    - daily_remaining: Remaining amount can transfer today
    - transactions_remaining: Remaining transfers allowed today

    **Errors:**
    - 404: Account not found
    - 503: Service unavailable
    """
    logger.info(f"⚡ Quick check remaining limit - Account: {account_number}")

    try:
        result = await transfer_limit_service.get_remaining_limit(account_number)
        logger.info(f"✅ Remaining limit retrieved for account {account_number}")
        return result

    except TransactionException as e:
        logger.warning(f"⚠️ Failed to get remaining limit: {e.error_code}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@router.get(
    "/transfer-limits/rules/all",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "All transfer rules retrieved"},
        503: {"description": "Service unavailable"},
    },
)
async def get_all_transfer_rules():
    """
    Get all transfer limit rules.

    Returns transfer limits for all privilege levels (PREMIUM, GOLD, SILVER, BASIC).

    **Response:**
    List of rules with:
    - privilege: Privilege level
    - daily_limit: Daily transfer limit in rupees
    - transaction_limit: Max transfers per day
    - created_at: When rule was created

    **Errors:**
    - 503: Service unavailable
    """
    logger.info("📋 Get all transfer limit rules")

    try:
        result = await transfer_limit_service.get_all_transfer_rules()
        logger.info(f"✅ Retrieved {len(result)} transfer limit rules")
        return result

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@router.post(
    "/transfer-limits/check",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Transfer feasibility checked"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def check_can_transfer(account_number: int, amount: float):
    """
    Check if an account can make a transfer of given amount.

    Quick validation before initiating transfer.

    **Query Parameters:**
    - account_number: Account to check
    - amount: Proposed transfer amount

    **Response:**
    - can_transfer: True/False
    - reason: Why blocked (if can_transfer=False)
    - daily_remaining: Amount remaining to transfer today
    - transactions_remaining: Transfers remaining today

    **Errors:**
    - 404: Account not found
    - 503: Service unavailable
    """
    logger.info(
        f"❓ Check if can transfer - Account: {account_number}, "
        f"Amount: ₹{amount}"
    )

    try:
        result = await transfer_limit_service.check_can_transfer(
            account_number=account_number,
            proposed_amount=Decimal(str(amount)),
        )
        logger.info(f"✅ Transfer check completed for account {account_number}")
        return result

    except TransactionException as e:
        logger.warning(f"⚠️ Transfer check failed: {e.error_code}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@router.get(
    "/transfer-limits/debug/fund-transfers/{account_number}",
    status_code=status.HTTP_200_OK,
)
async def debug_fund_transfers(account_number: int):
    """
    DEBUG ENDPOINT: Show all fund_transfers for an account today.
    Used to debug transfer limit validation.
    """
    from app.database.db import database
    from datetime import datetime
    
    logger.info(f"🔍 DEBUG: Getting fund_transfers for account {account_number}")
    
    try:
        conn = await database.get_connection()
        try:
            today = datetime.utcnow().date()
            
            query = """
                SELECT id, from_account, to_account, transfer_amount, transfer_mode, created_at
                FROM fund_transfers
                WHERE from_account = $1
                AND DATE(created_at) = $2
                ORDER BY created_at DESC
            """
            records = await conn.fetch(query, account_number, today)
            
            total = sum(r['transfer_amount'] for r in records) if records else 0
            
            return {
                "account_number": account_number,
                "date": str(today),
                "total_transferred": float(total),
                "transaction_count": len(records),
                "records": [
                    {
                        "id": r['id'],
                        "from_account": r['from_account'],
                        "to_account": r['to_account'],
                        "amount": float(r['transfer_amount']),
                        "mode": r['transfer_mode'],
                        "created_at": r['created_at'].isoformat()
                    }
                    for r in records
                ]
            }
        finally:
            await database._pool.release(conn)
    except Exception as e:
        logger.error(f"❌ Debug error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)},
        )
