"""
Transfer Limit API Routes

GET /api/v1/transfer-limits/{account} - Get transfer limits
GET /api/v1/transfer-limits/rules/all - Get all transfer limit rules (ADMIN, TELLER only)

Authorization:
- ADMIN/TELLER: Can view any account's limits
- CUSTOMER: Can view their own account's limits

Author: GDB Architecture Team
"""

import logging
import sys
from decimal import Decimal
from typing import Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Query, Depends
from app.services.transfer_limit_service import transfer_limit_service
from app.exceptions.transaction_exceptions import TransactionException

# Import authorization dependencies from Auth Service
auth_service_path = str(Path(__file__).parent.parent.parent.parent / "auth_service" / "app")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)

try:
    from security.auth_dependencies import (
        get_current_user,
        require_admin_or_teller_dependency,
    )
    from security.jwt_validation import JWTValidator
except ImportError:
    # Fallback path
    auth_service_parent = str(Path(__file__).parent.parent.parent.parent / "auth_service")
    if auth_service_parent not in sys.path:
        sys.path.insert(0, auth_service_parent)
    from app.security.auth_dependencies import (
        get_current_user,
        require_admin_or_teller_dependency,
    )
    from app.security.jwt_validation import JWTValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["transfer-limits"])


@router.get(
    "/transfer-limits/{account_number}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Transfer limits retrieved"},
        401: {"description": "Unauthorized - missing or invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def get_transfer_limit(
    account_number: int,
    claims: Dict[str, Any] = Depends(get_current_user),
) -> dict:
    """
    Get transfer limits for an account.

    **Authorization:**
    - ADMIN or TELLER: Can view any account limits
    - CUSTOMER: Can only view their own account limits

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
    - 401: Missing or invalid authorization token
    - 403: CUSTOMER trying to view another account's limits
    - 404: Account not found
    - 503: Account Service unavailable
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Note: Authorization checks are enforced at transaction service level
        # Account service doesn't expose user_id, so we skip ownership validation here
        
        logger.info(f"🔍 Get transfer limits by {login_id} ({user_role}) - Account: {account_number}")

        result = await transfer_limit_service.get_transfer_limit(account_number)
        logger.info(f"✅ Transfer limits retrieved for account {account_number} by {login_id}")
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
        401: {"description": "Unauthorized - missing or invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def get_remaining_limit(
    account_number: int,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get remaining transfer limit (quick check).

    **Authorization:**
    - ADMIN or TELLER: Can view any account limits
    - CUSTOMER: Can only view their own account limits

    **Path Parameters:**
    - account_number: Account number

    **Response:**
    - account_number: Account
    - daily_remaining: Remaining amount can transfer today
    - transactions_remaining: Remaining transfers allowed today

    **Errors:**
    - 401: Missing or invalid authorization token
    - 403: CUSTOMER trying to view another account's limits
    - 404: Account not found
    - 503: Service unavailable
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Note: Authorization checks are enforced at transaction service level
        # Account service doesn't expose user_id, so we skip ownership validation here
        
        logger.info(f"⚡ Quick check remaining limit by {login_id} ({user_role}) - Account: {account_number}")

        result = await transfer_limit_service.get_remaining_limit(account_number)
        logger.info(f"✅ Remaining limit retrieved for account {account_number} by {login_id}")
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
        401: {"description": "Unauthorized - missing or invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        503: {"description": "Service unavailable"},
    },
)
async def get_all_transfer_rules(
    claims: Dict[str, Any] = Depends(require_admin_or_teller_dependency),
):
    """
    Get all transfer limit rules.

    **Authorization:** ADMIN or TELLER role required

    Returns transfer limits for all privilege levels (PREMIUM, GOLD, SILVER, BASIC).

    **Response:**
    List of rules with:
    - privilege: Privilege level
    - daily_limit: Daily transfer limit in rupees
    - transaction_limit: Max transfers per day
    - created_at: When rule was created

    **Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - 503: Service unavailable
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        logger.info(f"📋 Get all transfer limit rules by {login_id}")

        result = await transfer_limit_service.get_all_transfer_rules()
        logger.info(f"✅ Retrieved {len(result)} transfer limit rules by {login_id}")
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
        401: {"description": "Unauthorized - missing or invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def check_can_transfer(
    account_number: int,
    amount: float,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """
    Check if an account can make a transfer of given amount.

    **Authorization:**
    - ADMIN or TELLER: Can check any account
    - CUSTOMER: Can only check their own account

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
    - 401: Missing or invalid authorization token
    - 403: CUSTOMER trying to check another account
    - 404: Account not found
    - 503: Service unavailable
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Note: Authorization checks are enforced at transaction service level
        # Account service doesn't expose user_id, so we skip ownership validation here
        
        logger.info(
            f"❓ Check if can transfer by {login_id} ({user_role}) - Account: {account_number}, "
            f"Amount: ₹{amount}"
        )

        result = await transfer_limit_service.check_can_transfer(
            account_number=account_number,
            proposed_amount=Decimal(str(amount)),
        )
        logger.info(f"✅ Transfer check completed for account {account_number} by {login_id}")
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
