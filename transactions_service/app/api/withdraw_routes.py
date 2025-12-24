"""
Withdraw API Routes

POST /api/v1/withdrawals - Withdraw funds from account
"""

import logging
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from app.models import TransactionLoggingCreate, TransactionLoggingResponse
from app.services.withdraw_service import withdraw_service
from app.exceptions.transaction_exceptions import TransactionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["withdrawals"])


@router.post(
    "/withdrawals",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Withdrawal successful"},
        400: {"description": "Invalid input or insufficient funds"},
        401: {"description": "Invalid PIN"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def withdraw_funds(
    account_number: int,
    amount: float,
    pin: str,
    description: str = None
) -> dict:
    """
    Withdraw funds from an account.

    **Query Parameters:**
    - account_number: Account to withdraw from
    - amount: Amount to withdraw (min 1, max 10,00,000)
    - pin: 4-digit PIN for authorization
    - description: Optional description

    **Response:**
    - status: SUCCESS/FAILED
    - transaction_id: Unique transaction ID
    - account_number: Account updated
    - amount: Amount withdrawn
    - new_balance: Account balance after withdrawal
    - transaction_date: When transaction occurred

    **Errors:**
    - 400: Invalid amount, insufficient funds, or invalid PIN format
    - 401: PIN verification failed
    - 404: Account not found
    - 503: Account Service unavailable
    """
    logger.info(f"💸 Withdrawal request - Account: {account_number}, Amount: ₹{amount}")

    try:
        # Call withdraw service
        result = await withdraw_service.process_withdraw(
            account_number=account_number,
            amount=Decimal(str(amount)),
            pin=pin,
            description=description,
        )

        logger.info(f"✅ Withdrawal successful for account {account_number}")

        return result

    except TransactionException as e:
        # All transaction exceptions are mapped to appropriate HTTP codes
        logger.warning(f"⚠️ Withdrawal failed: {e.error_code} - {e.message}")

        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        # Unexpected errors become 500
        logger.error(f"❌ Unexpected error during withdrawal: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )
