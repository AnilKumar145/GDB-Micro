"""
Add User Routes for User Management Service.
Endpoint: POST /api/v1/users
"""

from fastapi import APIRouter, HTTPException
from ..models.request_models import AddUserRequest
from ..models.response_models import AddUserResponse, ErrorResponse
from ..services.add_user_service import AddUserService
from ..exceptions.user_management_exception import (
    UserManagementException,
    UserAlreadyExistsException,
    InvalidUserInputException,
)
from ..repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["User Management"])


@router.post(
    "/users",
    response_model=AddUserResponse,
    status_code=201,
    responses={
        409: {"model": ErrorResponse, "description": "User already exists"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def add_user(request: AddUserRequest) -> AddUserResponse:
    """
    Add a new user to the system.

    **Endpoint:** POST /api/v1/users

    **Business Rules:**
    - login_id must be unique
    - Password will be hashed before storage
    - User is active by default

    **Request Body:**
    - username: User name (1-255 characters)
    - login_id: Unique login identifier (3-50 characters, alphanumeric + . - _)
    - password: Password (min 8 chars, uppercase, digit)

    **Success Response:** 201 Created
    **Error Responses:**
    - 409: User already exists
    - 400: Invalid input
    """
    try:
        # Create service instance with repository
        repo = UserRepository()
        service = AddUserService(repo)
        
        # Call service to add user
        result = await service.add_user(request)

        return result

    except UserAlreadyExistsException as e:
        logger.error(f"User already exists: {request.login_id}")
        raise HTTPException(status_code=409, detail=e.detail)

    except InvalidUserInputException as e:
        logger.error(f"Invalid input: {e.detail}")
        raise HTTPException(status_code=400, detail=e.detail)

    except UserManagementException as e:
        logger.error(f"User management error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        logger.error(f"Unexpected error adding user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
