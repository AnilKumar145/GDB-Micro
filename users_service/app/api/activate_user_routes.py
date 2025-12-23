"""
Activate User Routes for User Management Service.
Endpoint: PATCH /api/v1/users/{login_id}/activate
"""

from fastapi import APIRouter, HTTPException
from ..models.response_models import InactivateUserResponse, ErrorResponse
from ..services.activate_user_service import ActivateUserService
from ..repositories.user_repository import UserRepository
from ..exceptions.user_management_exception import (
    UserManagementException,
    UserNotFoundException,
    UserAlreadyActiveException,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["User Management"])


@router.patch(
    "/users/{login_id}/activate",
    response_model=InactivateUserResponse,
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        400: {"model": ErrorResponse, "description": "User already active"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def activate_user(login_id: str) -> InactivateUserResponse:
    """
    Activate a user (reactivate an inactive user).

    **Endpoint:** PATCH /api/v1/users/{login_id}/activate

    **Business Rules:**
    - User must exist
    - User must be inactive (cannot activate already active user)
    - Sets is_active = true
    - Restores user's access to the system

    **Path Parameters:**
    - login_id: User's login identifier

    **Success Response:** 200 OK
    **Error Responses:**
    - 404: User not found
    - 400: User already active
    """
    try:
        # Create service instance with repository
        repo = UserRepository()
        service = ActivateUserService(repo)
        
        # Call service to activate user
        result = await service.activate_user(login_id)

        return result

    except UserNotFoundException as e:
        logger.error(f"User not found: {login_id}")
        raise HTTPException(status_code=404, detail=e.detail)

    except UserAlreadyActiveException as e:
        logger.error(f"User already active: {login_id}")
        raise HTTPException(status_code=400, detail=e.detail)

    except UserManagementException as e:
        logger.error(f"User management error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        logger.error(f"Unexpected error activating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
