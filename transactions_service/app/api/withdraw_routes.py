"""
Withdraw API Routes (FE010)

POST /api/v1/withdrawals - Withdraw funds from account
"""

import logging
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from app.models.request_models import WithdrawRequest
from app.models.response_models import WithdrawResponse, ErrorResponse
from app.services.withdraw_service import withdraw_service
from app.exceptions.transaction_exceptions import TransactionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["withdrawals"])


@router.post(
    "/withdrawals",
    response_model=WithdrawResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": WithdrawResponse, "description": "Withdrawal successful"},
        400: {"model": ErrorResponse, "description": "Invalid input or insufficient funds"},
        401: {"model": ErrorResponse, "description": "Invalid PIN"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
)
async def withdraw_funds(request: WithdrawRequest) -> WithdrawResponse:
    """
    Withdraw funds from an account.

    **Request Body:**
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
    logger.info(f"💸 Withdrawal request - Account: {request.account_number}, Amount: ₹{request.amount}")

    try:
        # Call withdraw service
        result = await withdraw_service.process_withdraw(
            account_number=request.account_number,
            amount=Decimal(str(request.amount)),
            pin=request.pin,
            description=request.description,
        )

        logger.info(f"✅ Withdrawal successful for account {request.account_number}")

        return WithdrawResponse(**result)

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
