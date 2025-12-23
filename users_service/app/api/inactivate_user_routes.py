"""
Inactivate User Routes for User Management Service.
Endpoint: PATCH /api/v1/users/{login_id}/inactivate
"""

from fastapi import APIRouter, HTTPException
from ..models.response_models import InactivateUserResponse, ErrorResponse
from ..services.inactivate_user_service import InactivateUserService
from ..repositories.user_repository import UserRepository
from ..exceptions.user_management_exception import (
    UserManagementException,
    UserNotFoundException,
    UserAlreadyInactiveException,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["User Management"])

@router.patch(
    "/users/{login_id}/inactivate",
    response_model=InactivateUserResponse,
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        400: {"model": ErrorResponse, "description": "User already inactive"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def inactivate_user(login_id: str) -> InactivateUserResponse:
    """
    Inactivate a user (soft delete).

    **Endpoint:** PATCH /api/v1/users/{login_id}/inactivate

    **Business Rules:**
    - User must exist
    - User must be active (cannot inactivate already inactive user)
    - Sets is_active = false
    - No hard delete operation

    **Path Parameters:**
    - login_id: User's login identifier

    **Success Response:** 200 OK
    **Error Responses:**
    - 404: User not found
    - 400: User already inactive
    """
    try:
        # Create service instance with repository
        repo = UserRepository()
        service = InactivateUserService(repo)
        
        # Call service to inactivate user
        result = await service.inactivate_user(login_id)

        return result

    except UserNotFoundException as e:
        logger.error(f"User not found: {login_id}")
        raise HTTPException(status_code=404, detail=e.detail)

    except UserAlreadyInactiveException as e:
        logger.error(f"User already inactive: {login_id}")
        raise HTTPException(status_code=400, detail=e.detail)

    except UserManagementException as e:
        logger.error(f"User management error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        logger.error(f"Unexpected error inactivating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
