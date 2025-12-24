"""
Deposit API Routes (FE011)

POST /api/v1/deposits - Deposit funds to account
"""

import logging
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from app.models.request_models import DepositRequest
from app.models.response_models import DepositResponse, ErrorResponse
from app.services.deposit_service import deposit_service
from app.exceptions.transaction_exceptions import TransactionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["deposits"])


@router.post(
    "/deposits",
    response_model=DepositResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": DepositResponse, "description": "Deposit successful"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
)
async def deposit_funds(request: DepositRequest) -> DepositResponse:
    """
    Deposit funds to an account.

    **Request Body:**
    - account_number: Account to deposit to
    - amount: Amount to deposit (min 1, max 10,00,000)
    - description: Optional description

    **Response:**
    - status: SUCCESS/FAILED
    - transaction_id: Unique transaction ID
    - account_number: Account updated
    - amount: Amount deposited
    - new_balance: Account balance after deposit
    - transaction_date: When transaction occurred

    **Errors:**
    - 400: Invalid amount or account
    - 404: Account not found
    - 503: Account Service unavailable
    """
    logger.info(f"💰 Deposit request - Account: {request.account_number}, Amount: ₹{request.amount}")

    try:
        # Call deposit service
        result = await deposit_service.process_deposit(
            account_number=request.account_number,
            amount=Decimal(str(request.amount)),
            description=request.description,
        )

        logger.info(f"✅ Deposit successful for account {request.account_number}")

        return DepositResponse(**result)

    except TransactionException as e:
        # All transaction exceptions are mapped to appropriate HTTP codes
        logger.warning(f"⚠️ Deposit failed: {e.error_code} - {e.message}")

        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        # Unexpected errors become 500
        logger.error(f"❌ Unexpected error during deposit: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )
