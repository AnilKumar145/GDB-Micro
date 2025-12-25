"""
User Service Client

Makes HTTP calls to User Service internal APIs.
Auth Service uses User Service as the sole source of truth for user credentials.

One-way communication: Auth Service → User Service ONLY

User Service Internal APIs:
  - POST /internal/v1/users/verify - Verify user credentials
  - GET /internal/v1/users/{login_id}/status - Get user status
  - GET /internal/v1/users/{login_id}/role - Get user role

Author: GDB Architecture Team
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.config.settings import settings
from app.exceptions.auth_exceptions import ServiceUnavailableException


logger = logging.getLogger(__name__)


class UserServiceClient:
    """HTTP client for User Service communication."""
    
    @staticmethod
    async def verify_user_credentials(login_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Verify user credentials by calling User Service.
        
        Calls User Service internal API:
        POST /internal/v1/users/verify
        
        Request Body:
        {
            "login_id": str,
            "password": str (plain text)
        }
        
        Args:
            login_id: User login identifier
            password: User password (plain text)
        
        Returns:
            User data dict if credentials are valid:
            {
                'user_id': str (UUID),
                'login_id': str,
                'role': str (ADMIN, TELLER, CUSTOMER),
                'is_active': bool
            }
            
            Returns None if credentials are invalid or user not found
        
        Raises:
            ServiceUnavailableException: If User Service is unreachable
        """
        url = f"{settings.USER_SERVICE_URL}/internal/v1/users/verify"
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "login_id": login_id,
                    "password": password,
                }
                
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(
                        total=settings.USER_SERVICE_TIMEOUT
                    ),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"Verified credentials for user {login_id} with User Service"
                        )
                        return data
                    elif response.status == 401:
                        logger.warning(
                            f"Invalid credentials for user {login_id}"
                        )
                        return None
                    elif response.status == 404:
                        logger.warning(
                            f"User {login_id} not found in User Service"
                        )
                        return None
                    else:
                        logger.error(
                            f"User Service error: HTTP {response.status}"
                        )
                        raise ServiceUnavailableException(
                            "User service returned error"
                        )
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to User Service: {str(e)}")
            raise ServiceUnavailableException(
                f"User service unavailable: {str(e)}"
            )
        except asyncio.TimeoutError:
            logger.error("User Service request timed out")
            raise ServiceUnavailableException("User service request timed out")
        except Exception as e:
            logger.error(f"Unexpected error calling User Service: {str(e)}")
            raise ServiceUnavailableException("User service error")
    
    @staticmethod
    async def get_user_status(login_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user status (active/inactive) from User Service.
        
        Calls User Service internal API:
        GET /internal/v1/users/{login_id}/status
        
        Args:
            login_id: User login identifier
        
        Returns:
            User status dict:
            {
                'login_id': str,
                'is_active': bool,
                'user_id': str (UUID)
            }
            
            Returns None if user not found
        
        Raises:
            ServiceUnavailableException: If User Service is unreachable
        """
        url = f"{settings.USER_SERVICE_URL}/internal/v1/users/{login_id}/status"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(
                        total=settings.USER_SERVICE_TIMEOUT
                    ),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"Retrieved status for user {login_id}: active={data.get('is_active')}"
                        )
                        return data
                    elif response.status == 404:
                        logger.warning(f"User {login_id} not found")
                        return None
                    else:
                        logger.error(
                            f"User Service error: HTTP {response.status}"
                        )
                        raise ServiceUnavailableException()
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to User Service: {str(e)}")
            raise ServiceUnavailableException()
        except Exception as e:
            logger.error(f"Unexpected error calling User Service: {str(e)}")
            raise ServiceUnavailableException()
    
    @staticmethod
    async def get_user_role(login_id: str) -> Optional[str]:
        """
        Get user role from User Service.
        
        Calls User Service internal API:
        GET /internal/v1/users/{login_id}/role
        
        Args:
            login_id: User login identifier
        
        Returns:
            User role (ADMIN, TELLER, CUSTOMER) or None if user not found
        
        Raises:
            ServiceUnavailableException: If User Service is unreachable
        """
        url = f"{settings.USER_SERVICE_URL}/internal/v1/users/{login_id}/role"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(
                        total=settings.USER_SERVICE_TIMEOUT
                    ),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        role = data.get("role")
                        logger.info(
                            f"Retrieved role for user {login_id}: {role}"
                        )
                        return role
                    elif response.status == 404:
                        logger.warning(f"User {login_id} not found")
                        return None
                    else:
                        logger.error(
                            f"User Service error: HTTP {response.status}"
                        )
                        raise ServiceUnavailableException()
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to User Service: {str(e)}")
            raise ServiceUnavailableException()
        except Exception as e:
            logger.error(f"Unexpected error calling User Service: {str(e)}")
            raise ServiceUnavailableException()
