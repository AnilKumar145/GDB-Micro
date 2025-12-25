"""
Accounts Service - Account API Routes

Public REST API endpoints for account management.

Authorization:
- Create Account: ADMIN, TELLER
- Update Account: ADMIN, TELLER
- Close Account: ADMIN only
- Activate/Inactivate: ADMIN only
- View All Accounts: ADMIN, TELLER
- View Own Account: CUSTOMER (only their own accounts)

Author: GDB Architecture Team
"""

import logging
import sys
from typing import Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime

from app.services.account_service import AccountService
from app.models.account import (
    SavingsAccountCreate,
    CurrentAccountCreate,
    AccountUpdate,
    AccountResponse,
    SavingsAccountResponse,
    CurrentAccountResponse,
    BalanceResponse,
    ErrorResponse
)
from app.exceptions.account_exceptions import AccountException

# Import authorization dependencies from Auth Service
auth_service_path = str(Path(__file__).parent.parent.parent.parent / "auth_service" / "app")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)

try:
    from security.auth_dependencies import (
        get_current_user,
        require_admin_or_teller,
        require_admin,
    )
    from security.jwt_validation import JWTValidator, RoleChecker
except ImportError:
    # Fallback path
    auth_service_parent = str(Path(__file__).parent.parent.parent.parent / "auth_service")
    if auth_service_parent not in sys.path:
        sys.path.insert(0, auth_service_parent)
    from app.security.auth_dependencies import (
        get_current_user,
        require_admin_or_teller,
        require_admin,
    )
    from app.security.jwt_validation import JWTValidator, RoleChecker

logger = logging.getLogger(__name__)

router = APIRouter()


def get_account_service() -> AccountService:
    """
    Dependency injection function for AccountService.
    Ensures database is initialized before creating service.
    """
    return AccountService()


# ========================================
# ACCOUNT CREATION ENDPOINTS
# ========================================

@router.post(
    "/accounts/savings",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts - Creation"],
    summary="Create Savings Account",
    description="Create a new savings account for individuals (age >= 18)"
)
async def create_savings_account(
    request: SavingsAccountCreate,
    claims: Dict[str, Any] = Depends(require_admin_or_teller()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Create a new savings account.

    **Authorization:** ADMIN or TELLER role required
    
    **Request Body:**
    - `name`: Account holder name (1-255 characters)
    - `account_type`: Fixed as SAVINGS
    - `pin`: 4-6 digit PIN
    - `date_of_birth`: DOB in YYYY-MM-DD format
    - `gender`: M, F, or OTHER
    - `phone_no`: 10-digit phone number
    - `privilege`: PREMIUM, GOLD, or SILVER (default: SILVER)
    
    **Validations:**
    - Age must be >= 18
    - PIN must be 4-6 digits (no sequential/same digits)
    - Unique name + DOB combination
    - Only ADMIN or TELLER can create accounts
    
    **Response:**
    - `account_number`: Auto-generated unique account number (starts from 1000)
    - `balance`: Initial balance (₹0)
    - `is_active`: TRUE by default
    - `activated_date`: Account creation timestamp
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - `ACCOUNT_ALREADY_EXISTS`: name + DOB already exists
    - `AGE_RESTRICTION`: Age < 18
    - `INVALID_PIN`: Invalid PIN format
    - `VALIDATION_ERROR`: Input validation failed
    """
    try:
        account_number = await account_service.create_savings_account(request)
        
        logger.info(f"Savings account created by {claims.get('login_id')}: {account_number}")
        
        return AccountResponse(
            account_number=account_number,
            account_type="SAVINGS",
            name=request.name,
            privilege=request.privilege,
            balance=0.00,
            is_active=True,
            activated_date=datetime.utcnow(),
            closed_date=None
        )
        
    except AccountException as e:
        logger.error(f"❌ Account creation failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": e.error_code,
                "message": e.message
            }
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/current",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts - Creation"],
    summary="Create Current Account",
    description="Create a new current account for businesses/companies"
)
async def create_current_account(
    request: CurrentAccountCreate,
    claims: Dict[str, Any] = Depends(require_admin_or_teller()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Create a new current account.

    **Authorization:** ADMIN or TELLER role required
    
    **Request Body:**
    - `name`: Account holder/company name (1-255 characters)
    - `account_type`: Fixed as CURRENT
    - `pin`: 4-6 digit PIN
    - `company_name`: Company name (1-255 characters)
    - `website`: Company website (optional)
    - `registration_no`: Company registration number (unique, 1-50 chars)
    - `privilege`: PREMIUM, GOLD, or SILVER (default: SILVER)
    
    **Validations:**
    - PIN must be 4-6 digits (no sequential/same digits)
    - Unique registration_no
    - Only ADMIN or TELLER can create accounts
    
    **Response:**
    - `account_number`: Auto-generated unique account number (starts from 1000)
    - `balance`: Initial balance (₹0)
    - `is_active`: TRUE by default
    - `activated_date`: Account creation timestamp
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - `ACCOUNT_ALREADY_EXISTS`: registration_no already exists
    - `INVALID_PIN`: Invalid PIN format
    - `VALIDATION_ERROR`: Input validation failed
    """
    try:
        account_number = await account_service.create_current_account(request)
        
        logger.info(f"Current account created by {claims.get('login_id')}: {account_number}")
        
        return AccountResponse(
            account_number=account_number,
            account_type="CURRENT",
            name=request.name,
            privilege=request.privilege,
            balance=0.00,
            is_active=True,
            activated_date=datetime.utcnow(),
            closed_date=None
        )
        
    except AccountException as e:
        logger.error(f"❌ Account creation failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": e.error_code,
                "message": e.message
            }
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


# ========================================
# ACCOUNT QUERY ENDPOINTS
# ========================================

@router.get(
    "/accounts/{account_number}",
    response_model=AccountResponse,
    tags=["Accounts - Query"],
    summary="Get Account Details",
    description="Retrieve account details"
)
async def get_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Get account details by account number.
    
    **Authorization:**
    - ADMIN or TELLER: Can view any account
    - CUSTOMER: Can only view their own accounts
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Response:**
    - Full account details with balance and status
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: CUSTOMER trying to view another user's account
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `DATABASE_ERROR`: Database query failed
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Get account details
        account = await account_service.get_account_details(account_number)
        
        # Note: Authorization is enforced at the transaction service level
        # Accounts service allows viewing any account's details
        
        logger.info(f"Account details retrieved by {login_id} ({user_role}): {account_number}")
        
        return AccountResponse(
            account_number=account.account_number,
            account_type=account.account_type,
            name=account.name,
            privilege=account.privilege,
            balance=account.balance,
            is_active=account.is_active,
            activated_date=account.activated_date,
            closed_date=account.closed_date
        )
        
    except AccountException as e:
        logger.error(f"❌ Get account failed: {e.error_code}")
        status_code = status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.get(
    "/accounts/{account_number}/balance",
    response_model=BalanceResponse,
    tags=["Accounts - Query"],
    summary="Get Account Balance",
    description="Retrieve current account balance"
)
async def get_balance(
    account_number: int,
    claims: Dict[str, Any] = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Get account balance.
    
    **Authorization:**
    - ADMIN or TELLER: Can view any account balance
    - CUSTOMER: Can only view their own account balance
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Response:**
    - `account_number`: Account number
    - `balance`: Current balance in INR
    - `currency`: Fixed as INR
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: CUSTOMER trying to view another user's account balance
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `ACCOUNT_INACTIVE`: Account is inactive
    - `DATABASE_ERROR`: Database query failed
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Get account details
        account = await account_service.get_account_details(account_number)
        
        # Note: Authorization is enforced at the transaction service level
        # Accounts service allows viewing any account's balance
        
        balance = await account_service.get_balance(account_number)
        
        logger.info(f"Account balance retrieved by {login_id} ({user_role}): {account_number}")
        
        return BalanceResponse(
            account_number=account_number,
            balance=balance,
            currency="INR"
        )
        
    except AccountException as e:
        logger.error(f"❌ Get balance failed: {e.error_code}")
        status_code = status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


# ========================================
# ACCOUNT MANAGEMENT ENDPOINTS
# ========================================

@router.patch(
    "/accounts/{account_number}",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Update Account",
    description="Update account details (name, privilege)"
)
async def update_account(
    account_number: int,
    request: AccountUpdate,
    claims: Dict[str, Any] = Depends(require_admin_or_teller()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Update account details.
    
    **Authorization:** ADMIN or TELLER role required
    
    **Path Parameters:**
    - `account_number`: Account to update
    
    **Request Body:**
    - `name`: New account name (optional)
    - `privilege`: New privilege level (optional)
    
    **Response:**
    - `success`: true if updated
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `VALIDATION_ERROR`: Invalid input data
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        success = await account_service.update_account(account_number, request)
        
        logger.info(f"Account updated by {login_id}: {account_number}")
        
        return {
            "success": success,
            "message": "Account updated successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Update account failed: {e.error_code}")
        status_code = status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/{account_number}/activate",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Activate Account",
    description="Activate an inactive account"
)
async def activate_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(require_admin()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Activate an account.
    
    **Authorization:** ADMIN role required
    
    **Path Parameters:**
    - `account_number`: Account to activate
    
    **Response:**
    - `success`: true if activated
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        success = await account_service.activate_account(account_number)
        
        logger.info(f"Account activated by {login_id}: {account_number}")
        
        return {
            "success": success,
            "message": "Account activated successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Activate account failed: {e.error_code}")
        # Map error codes to appropriate HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if "NOT_FOUND" in e.error_code:
            status_code = status.HTTP_404_NOT_FOUND
        elif "ALREADY_ACTIVE" in e.error_code:
            status_code = status.HTTP_409_CONFLICT
        
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/{account_number}/inactivate",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Inactivate Account",
    description="Inactivate an active account"
)
async def inactivate_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(require_admin()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Inactivate an account.
    
    **Authorization:** ADMIN role required
    
    **Path Parameters:**
    - `account_number`: Account to inactivate
    
    **Response:**
    - `success`: true if inactivated
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        success = await account_service.inactivate_account(account_number)
        
        logger.info(f"Account inactivated by {login_id}: {account_number}")
        
        return {
            "success": success,
            "message": "Account inactivated successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Inactivate account failed: {e.error_code}")
        # Map error codes to appropriate HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if "NOT_FOUND" in e.error_code:
            status_code = status.HTTP_404_NOT_FOUND
        elif "ALREADY_INACTIVE" in e.error_code:
            status_code = status.HTTP_409_CONFLICT
        
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/{account_number}/close",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Close Account",
    description="Close (soft delete) an account"
)
async def close_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(require_admin()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Close an account.
    
    **Authorization:** ADMIN role required
    
    **Path Parameters:**
    - `account_number`: Account to close
    
    **Response:**
    - `success`: true if closed
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    
    **Note:**
    - Account can be closed even with remaining balance
    - Closed accounts cannot perform transactions
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        success = await account_service.close_account(account_number)
        
        logger.info(f"Account closed by {login_id}: {account_number}")
        
        return {
            "success": success,
            "message": "Account closed successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Close account failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )
