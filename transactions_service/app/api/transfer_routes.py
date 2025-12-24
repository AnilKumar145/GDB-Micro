"""
Transfer API Routes

POST /api/v1/transfers - Transfer funds between accounts
"""

import logging
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from app.models import FundTransferCreate, FundTransferResponse, TransferMode
from app.services.transfer_service import transfer_service
from app.exceptions.transaction_exceptions import TransactionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["transfers"])


@router.post(
    "/transfers",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Transfer successful"},
        400: {"description": "Invalid input or limit exceeded"},
        401: {"description": "Invalid PIN"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def transfer_funds(
    from_account: int,
    to_account: int,
    amount: float,
    pin: str,
    transfer_mode: str = "NEFT",
    description: str = None
) -> dict:
    """
    Transfer funds between two accounts.

    **Query Parameters:**
    - from_account: Source account
    - to_account: Destination account
    - amount: Amount to transfer (min 1, max 10,00,000)
    - pin: 4-digit PIN for authorization
    - transfer_mode: NEFT/RTGS/IMPS (default: NEFT)
    - description: Optional description

    **Response:**
    - status: SUCCESS/FAILED
    - transaction_id: Unique transaction ID
    - from_account: Source account
    - to_account: Destination account
    - amount: Amount transferred
    - transfer_mode: Transfer mode used
    - from_account_new_balance: Source account balance after transfer
    - to_account_new_balance: Destination account balance after transfer
    - transaction_date: When transaction occurred

    **Errors:**
    - 400: Invalid amount, insufficient funds, same account, or limit exceeded
    - 401: PIN verification failed
    - 404: Account not found
    - 503: Account Service unavailable
    """
    logger.info(
        f"💳 Transfer request - From: {from_account}, "
        f"To: {to_account}, Amount: ₹{amount}"
    )

    try:
        # Determine transfer mode
        transfer_mode_enum = TransferMode[transfer_mode.upper()] if transfer_mode else TransferMode.NEFT

        # Call transfer service
        result = await transfer_service.process_transfer(
            from_account=from_account,
            to_account=to_account,
            amount=Decimal(str(amount)),
            pin=pin,
            transfer_mode=transfer_mode_enum,
            description=description,
        )

        logger.info(
            f"✅ Transfer successful - From: {from_account}, "
            f"To: {to_account}"
        )

        return result

    except TransactionException as e:
        # All transaction exceptions are mapped to appropriate HTTP codes
        logger.warning(f"⚠️ Transfer failed: {e.error_code} - {e.message}")

        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        # Unexpected errors become 500
        logger.error(f"❌ Unexpected error during transfer: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )
