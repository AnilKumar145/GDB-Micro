"""
Accounts Service - Internal API Routes

Service-to-service REST API endpoints.
Called only by other microservices (Transactions, Auth).
NOT publicly exposed.

Author: GDB Architecture Team
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends

from app.services.internal_service import InternalAccountService
from app.exceptions.account_exceptions import AccountException

logger = logging.getLogger(__name__)

router = APIRouter()


def get_internal_service() -> InternalAccountService:
    """
    Dependency injection function for InternalAccountService.
    Ensures database is initialized before creating service.
    """
    return InternalAccountService()


# ========================================
# INTERNAL ACCOUNT INFORMATION
# ========================================

@router.get(
    "/accounts/{account_number}",
    tags=["Internal - Account Info"],
    summary="Get Account Details (Internal)",
    description="Fetch account details for inter-service use. Internal API only."
)
async def get_account_details_internal(
    account_number: int,
    internal_service: InternalAccountService = Depends(get_internal_service)
):
    """
    Get account details for service-to-service use.
    
    **Called by:** Transactions Service, Auth Service
    **Purpose:** Fetch account details before processing transactions
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Response:**
    - `account_number`: Account number
    - `account_type`: SAVINGS or CURRENT
    - `name`: Account holder name
    - `balance`: Current balance
    - `privilege`: PREMIUM, GOLD, or SILVER
    - `is_active`: Account active status
    - `activated_date`: Account creation timestamp
    - `closed_date`: Account close timestamp (null if active)
    
    **Possible Errors:**
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist (404)
    - `DATABASE_ERROR`: Database operation failed (500)
    """
    try:
        details = await internal_service.get_account_details(account_number)
        return details
        
    except AccountException as e:
        logger.error(f"❌ Get account details failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get(
    "/accounts/{account_number}/privilege",
    tags=["Internal - Account Info"],
    summary="Get Account Privilege (Internal)",
    description="Get privilege level for transfer limit determination"
)
async def get_privilege_internal(
    account_number: int,
    internal_service: InternalAccountService = Depends(get_internal_service)
):
    """
    Get account privilege level for transfer limit enforcement.
    
    **Called by:** Transactions Service
    **Purpose:** Determine daily transfer limits
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Response:**
    - `account_number`: Account number
    - `privilege`: PREMIUM, GOLD, or SILVER
    - `status`: SUCCESS or FAILED
    
    **Privilege Limits:**
    - PREMIUM: ₹100,000 per day
    - GOLD: ₹50,000 per day
    - SILVER: ₹25,000 per day
    """
    try:
        result = await internal_service.get_privilege(account_number)
        return result
        
    except AccountException as e:
        logger.error(f"❌ Get privilege failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get(
    "/accounts/{account_number}/active",
    tags=["Internal - Account Info"],
    summary="Check Account Active Status (Internal)",
    description="Check if account is active"
)
async def check_account_active_internal(
    account_number: int,
    internal_service: InternalAccountService = Depends(get_internal_service)
):
    """
    Check if account is active.
    
    **Called by:** Transactions Service, Auth Service
    **Purpose:** Verify account can process transactions
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Response:**
    - `account_number`: Account number
    - `is_active`: true if account is active and not closed
    - `status`: SUCCESS or FAILED
    
    **Validation Rules:**
    - Account must exist
    - Account must not be closed
    - Account is_active flag must be TRUE
    """
    try:
        result = await internal_service.check_account_active(account_number)
        return result
        
    except AccountException as e:
        logger.error(f"❌ Check active failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


# ========================================
# INTERNAL DEBIT/CREDIT OPERATIONS
# ========================================

@router.post(
    "/accounts/{account_number}/debit",
    tags=["Internal - Transactions"],
    summary="Debit Account (Internal)",
    description="Debit amount from account. Called by Transactions Service only."
)
async def debit_account_internal(
    account_number: int,
    amount: float,
    idempotency_key: str = None,
    internal_service: InternalAccountService = Depends(get_internal_service),
    description: str = "Internal Debit"
):
    """
    Debit amount from account (WITHDRAW, TRANSFER FROM).
    
    **Called by:** Transactions Service
    **Purpose:** Withdraw or transfer funds from account
    
    **Path Parameters:**
    - `account_number`: Account to debit
    
    **Query Parameters:**
    - `amount`: Amount to debit (positive value, must be > 0)
    - `idempotency_key`: Optional idempotency key for retry safety
    - `description`: Transaction description (default: "Internal Debit")
    
    **Response (Success):**
    ```json
    {
        "success": true,
        "account_number": 1001,
        "amount_debited": 5000.00,
        "new_balance": 25000.00,
        "status": "SUCCESS"
    }
    ```
    
    **Response (Failure):**
    ```json
    {
        "success": false,
        "account_number": 1001,
        "status": "FAILED",
        "error_code": "INSUFFICIENT_FUNDS",
        "error_message": "Insufficient funds..."
    }
    ```
    
    **Idempotency:**
    - If same `idempotency_key` is used twice, only first debit succeeds
    - Returns SUCCESS on retry with same key (idempotent)
    - Use UUIDs for idempotency keys
    
    **Possible Errors:**
    - `INSUFFICIENT_FUNDS`: Balance < amount
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `ACCOUNT_INACTIVE`: Account is inactive or closed
    - `DATABASE_ERROR`: Database operation failed
    
    **Transaction Safety:**
    - Uses database transactions
    - Rollback on failure
    - At-most-once semantics with idempotency key
    """
    try:
        result = await internal_service.debit_for_transfer(
            account_number,
            amount,
            idempotency_key
        )
        
        # Return appropriate status code based on result
        status_code = status.HTTP_200_OK if result["status"] == "SUCCESS" else status.HTTP_400_BAD_REQUEST
        return result
        
    except Exception as e:
        logger.error(f"❌ Debit failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post(
    "/accounts/{account_number}/credit",
    tags=["Internal - Transactions"],
    summary="Credit Account (Internal)",
    description="Credit amount to account. Called by Transactions Service only."
)
async def credit_account_internal(
    account_number: int,
    amount: float,
    idempotency_key: str = None,
    description: str = "Internal Credit",
    internal_service: InternalAccountService = Depends(get_internal_service),
):
    """
    Credit amount to account (DEPOSIT, TRANSFER TO).
    
    **Called by:** Transactions Service
    **Purpose:** Deposit or transfer funds to account
    
    **Path Parameters:**
    - `account_number`: Account to credit
    
    **Query Parameters:**
    - `amount`: Amount to credit (positive value, must be > 0)
    - `idempotency_key`: Optional idempotency key for retry safety
    - `description`: Transaction description (default: "Internal Credit")
    
    **Response (Success):**
    ```json
    {
        "success": true,
        "account_number": 1002,
        "amount_credited": 5000.00,
        "new_balance": 35000.00,
        "status": "SUCCESS"
    }
    ```
    
    **Response (Failure):**
    ```json
    {
        "success": false,
        "account_number": 1002,
        "status": "FAILED",
        "error_code": "ACCOUNT_NOT_FOUND",
        "error_message": "Account 1002 not found"
    }
    ```
    
    **Idempotency:**
    - If same `idempotency_key` is used twice, only first credit succeeds
    - Returns SUCCESS on retry with same key (idempotent)
    - Use UUIDs for idempotency keys
    
    **Possible Errors:**
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `ACCOUNT_INACTIVE`: Account is inactive or closed
    - `DATABASE_ERROR`: Database operation failed
    
    **Transaction Safety:**
    - Uses database transactions
    - Rollback on failure
    - At-most-once semantics with idempotency key
    """
    try:
        result = await internal_service.credit_for_transfer(
            account_number,
            amount,
            idempotency_key
        )
        
        # Return appropriate status code based on result
        status_code = status.HTTP_200_OK if result["status"] == "SUCCESS" else status.HTTP_400_BAD_REQUEST
        return result
        
    except Exception as e:
        logger.error(f"❌ Credit failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


# ========================================
# INTERNAL SECURITY OPERATIONS
# ========================================

@router.post(
    "/accounts/{account_number}/verify-pin",
    tags=["Internal - Security"],
    summary="Verify Account PIN (Internal)",
    description="Verify PIN for transaction authorization"
)
async def verify_pin_internal(
    account_number: int,
    pin: str,
    internal_service: InternalAccountService = Depends(get_internal_service),
):
    """
    Verify account PIN for transaction authorization.
    
    **Called by:** Auth Service, Transactions Service
    **Purpose:** Validate PIN before processing sensitive operations
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Query Parameters:**
    - `pin`: PIN to verify
    
    **Response (Valid PIN):**
    ```json
    {
        "account_number": 1001,
        "pin_valid": true,
        "status": "SUCCESS"
    }
    ```
    
    **Response (Invalid PIN):**
    ```json
    {
        "account_number": 1001,
        "pin_valid": false,
        "status": "FAILED",
        "error_code": "INVALID_PIN"
    }
    ```
    
    **Security:**
    - PIN is never logged or returned in responses
    - Uses bcrypt for verification
    - Time-constant comparison (protected against timing attacks)
    
    **Possible Errors:**
    - `INVALID_PIN`: PIN doesn't match
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    """
    try:
        result = await internal_service.verify_account_pin(account_number, pin)
        return result
        
    except Exception as e:
        logger.error(f"❌ PIN verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )
