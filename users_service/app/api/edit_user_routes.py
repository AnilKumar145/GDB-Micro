"""
Edit User Routes for User Management Service.
Endpoint: PUT /api/v1/users/{login_id}
"""

from fastapi import APIRouter, HTTPException
from ..models.request_models import EditUserRequest
from ..models.response_models import EditUserResponse, ErrorResponse
from ..services.edit_user_service import EditUserService
from ..repositories.user_repository import UserRepository
from ..exceptions.user_management_exception import (
    UserManagementException,
    UserNotFoundException,
    UserInactiveException,
    InvalidUserInputException,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["User Management"])


@router.put(
    "/users/{login_id}",
    response_model=EditUserResponse,
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "User is inactive"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def edit_user(login_id: str, request: EditUserRequest) -> EditUserResponse:
    """
    Edit user information.

    **Endpoint:** PUT /api/v1/users/{login_id}

    **Business Rules:**
    - User must exist
    - User must be active
    - login_id is immutable (cannot change)
    - Editable fields: username, password

    **Path Parameters:**
    - login_id: User's login identifier

    **Request Body:**
    - username: New username (optional)
    - password: New password (optional)

    **Success Response:** 200 OK
    **Error Responses:**
    - 404: User not found
    - 403: User is inactive
    - 400: Invalid input
    """
    try:
        # Create service instance with repository
        repo = UserRepository()
        service = EditUserService(repo)
        
        # Call service to edit user
        result = await service.edit_user(login_id, request)

        return result

    except UserNotFoundException as e:
        logger.error(f"User not found: {login_id}")
        raise HTTPException(status_code=404, detail=e.detail)

    except UserInactiveException as e:
        logger.error(f"User is inactive: {login_id}")
        raise HTTPException(status_code=403, detail=e.detail)

    except InvalidUserInputException as e:
        logger.error(f"Invalid input: {e.detail}")
        raise HTTPException(status_code=400, detail=e.detail)

    except UserManagementException as e:
        logger.error(f"User management error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        logger.error(f"Unexpected error editing user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
