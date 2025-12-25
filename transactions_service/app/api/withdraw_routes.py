"""
Withdraw API Routes - Withdraw funds from account (CUSTOMER, TELLER only)

Authorization:
- CUSTOMER: Can only withdraw from their own accounts
- TELLER: Can withdraw from any account
- ADMIN: No withdraw access

Author: GDB Architecture Team
"""

import logging
import sys
from decimal import Decimal
from typing import Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends
from app.models import TransactionLoggingCreate, TransactionLoggingResponse
from app.services.withdraw_service import withdraw_service
from app.exceptions.transaction_exceptions import TransactionException

# Import authorization dependencies from Auth Service
auth_service_path = str(Path(__file__).parent.parent.parent.parent / "auth_service" / "app")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)

try:
    from security.auth_dependencies import (
        get_current_user,
        require_customer_or_teller_dependency,
    )
    from security.jwt_validation import JWTValidator
except ImportError:
    # Fallback path
    auth_service_parent = str(Path(__file__).parent.parent.parent.parent / "auth_service")
    if auth_service_parent not in sys.path:
        sys.path.insert(0, auth_service_parent)
    from app.security.auth_dependencies import (
        get_current_user,
        require_customer_or_teller_dependency,
    )
    from app.security.jwt_validation import JWTValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["withdrawals"])


@router.post(
    "/withdrawals",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Withdrawal successful"},
        400: {"description": "Invalid input or insufficient funds"},
        401: {"description": "Unauthorized - missing/invalid token or invalid PIN"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def withdraw_funds(
    account_number: int,
    amount: float,
    pin: str,
    description: str = None,
    claims: Dict[str, Any] = Depends(require_customer_or_teller_dependency),
) -> dict:
    """
    Withdraw funds from an account.

    **Authorization:** CUSTOMER (own accounts only) or TELLER (any account)

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
    - 401: Unauthorized (missing/invalid token or invalid PIN)
    - 403: CUSTOMER trying to withdraw from someone else's account
    - 400: Invalid amount, insufficient funds, or invalid PIN format
    - 404: Account not found
    - 503: Account Service unavailable
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        logger.info(f"💸 Withdrawal request by {login_id} ({user_role}) - Account: {account_number}, Amount: ₹{amount}")

        # Call withdraw service
        result = await withdraw_service.process_withdraw(
            account_number=account_number,
            amount=Decimal(str(amount)),
            pin=pin,
            description=description,
        )

        logger.info(f"✅ Withdrawal successful by {login_id} for account {account_number}")

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
