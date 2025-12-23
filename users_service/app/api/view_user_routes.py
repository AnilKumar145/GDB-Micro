"""
View User Routes for User Management Service.
Endpoints:
- GET /api/v1/users/{login_id} - View single user
- GET /api/v1/users - List all users
"""

from fastapi import APIRouter, HTTPException
from ..models.response_models import (
    ViewUserResponse,
    ListUsersResponse,
    ErrorResponse,
)
from ..services.view_user_service import ViewUserService
from ..repositories.user_repository import UserRepository
from ..exceptions.user_management_exception import (
    UserManagementException,
    UserNotFoundException,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["User Management"])


@router.get(
    "/users/{login_id}",
    response_model=ViewUserResponse,
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def view_user(login_id: str) -> ViewUserResponse:
    """
    View user details by login_id.

    **Endpoint:** GET /api/v1/users/{login_id}

    **Business Rules:**
    - User must exist
    - Password is never returned
    - Returns user profile data

    **Path Parameters:**
    - login_id: User's login identifier

    **Success Response:** 200 OK
    **Error Responses:**
    - 404: User not found
    """
    try:
        # Create service instance with repository
        repo = UserRepository()
        service = ViewUserService(repo)
        
        # Call service to view user
        result = await service.get_user(login_id)

        return result

    except UserNotFoundException as e:
        logger.error(f"User not found: {login_id}")
        raise HTTPException(status_code=404, detail=e.detail)

    except UserManagementException as e:
        logger.error(f"User management error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        logger.error(f"Unexpected error viewing user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/users",
    response_model=ListUsersResponse,
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def list_users() -> ListUsersResponse:
    """
    List all active users.

    **Endpoint:** GET /api/v1/users

    **Business Rules:**
    - Returns only active users
    - Passwords are never returned
    - Ordered by creation date (newest first)

    **Success Response:** 200 OK
    """
    try:
        # Create service instance with repository
        repo = UserRepository()
        service = ViewUserService(repo)
        
        # Call service to list users
        result = await service.list_users()

        return result

    except UserManagementException as e:
        logger.error(f"User management error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        logger.error(f"Unexpected error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
