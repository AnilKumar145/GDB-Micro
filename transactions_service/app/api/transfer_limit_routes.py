"""
Transfer Limit API Routes (FE013, FE014)

GET /api/v1/transfer-limits/{account} - Get transfer limits
GET /api/v1/transfer-limits/rules/all - Get all transfer rules
POST /api/v1/transfer-limits/check - Check if transfer is possible
"""

import logging
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status, Query
from app.models.response_models import TransferLimitResponse, ErrorResponse
from app.models.request_models import TransferLimitRequest
from app.services.transfer_limit_service import transfer_limit_service
from app.exceptions.transaction_exceptions import TransactionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["transfer-limits"])


@router.get(
    "/transfer-limits/{account_number}",
    response_model=TransferLimitResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": TransferLimitResponse, "description": "Transfer limits retrieved"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
)
async def get_transfer_limit(account_number: int) -> TransferLimitResponse:
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
        return TransferLimitResponse(**result)

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
        404: {"model": ErrorResponse, "description": "Account not found"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
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
        503: {"model": ErrorResponse, "description": "Service unavailable"},
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
        404: {"model": ErrorResponse, "description": "Account not found"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
)
async def check_can_transfer(request: TransferLimitRequest):
    """
    Check if an account can make a transfer of given amount.

    Quick validation before initiating transfer.

    **Request Body:**
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
        f"❓ Check if can transfer - Account: {request.account_number}, "
        f"Amount: ₹{request.amount}"
    )

    try:
        result = await transfer_limit_service.check_can_transfer(
            account_number=request.account_number,
            proposed_amount=Decimal(str(request.amount)),
        )
        logger.info(f"✅ Transfer check completed for account {request.account_number}")
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
