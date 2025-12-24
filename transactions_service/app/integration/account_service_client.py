"""
Account Service Client

Handles all communication with Account Service.
CRITICAL: Every withdrawal, deposit, and transfer MUST validate via Account Service.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from app.config.settings import settings
from app.exceptions.transaction_exceptions import (
    AccountNotFoundException,
    AccountNotActiveException,
    InvalidPINException,
    ServiceUnavailableException,
    AccountServiceException,
)

logger = logging.getLogger(__name__)


class AccountServiceClient:
    """Client for Account Service communication."""

    def __init__(self):
        """Initialize Account Service client."""
        self.base_url = settings.ACCOUNT_SERVICE_URL
        self.timeout = settings.ACCOUNT_SERVICE_TIMEOUT

    async def validate_account(self, account_number: int) -> Dict[str, Any]:
        """
        Validate account exists and is active.
        
        MANDATORY CALL before any transaction operation.
        
        Args:
            account_number: Account to validate
            
        Returns:
            Account details dict with keys:
            - accountNumber
            - isActive
            - balance
            - privilege (PREMIUM/GOLD/SILVER/BASIC)
            
        Raises:
            AccountNotFoundException: If account doesn't exist
            AccountNotActiveException: If account is not active
            ServiceUnavailableException: If Account Service is down
        """
        endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/validation"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                
                if response.status_code == 404:
                    raise AccountNotFoundException(
                        f"Account {account_number} not found"
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if account is active
                    if not data.get("isActive", False):
                        raise AccountNotActiveException(
                            f"Account {account_number} is not active"
                        )
                    
                    return data
                
                # Any other error
                raise AccountServiceException(
                    f"Account Service error: {response.text}"
                )
                
        except httpx.RequestError as e:
            logger.error(f"Account Service connection error: {str(e)}")
            raise ServiceUnavailableException(
                "Account Service is currently unavailable"
            )
        except httpx.HTTPError as e:
            logger.error(f"Account Service HTTP error: {str(e)}")
            raise ServiceUnavailableException(
                "Account Service returned an error"
            )

    async def verify_pin(self, account_number: int, pin: str) -> bool:
        """
        Verify account PIN.
        
        MANDATORY for withdraw and transfer operations.
        
        Args:
            account_number: Account number
            pin: PIN to verify
            
        Returns:
            True if PIN is valid
            
        Raises:
            InvalidPINException: If PIN is invalid
            AccountNotFoundException: If account doesn't exist
            ServiceUnavailableException: If Account Service is down
        """
        endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/verify-pin"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    json={"pin": pin}
                )
                
                if response.status_code == 404:
                    raise AccountNotFoundException(
                        f"Account {account_number} not found"
                    )
                
                if response.status_code == 401:
                    raise InvalidPINException(
                        "Invalid PIN provided"
                    )
                
                if response.status_code == 200:
                    return response.json().get("valid", False)
                
                raise AccountServiceException(
                    f"PIN verification failed: {response.text}"
                )
                
        except httpx.RequestError:
            raise ServiceUnavailableException(
                "Account Service is unavailable"
            )

    async def debit_account(
        self,
        account_number: int,
        amount: float,
        description: str = "Transaction",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Debit amount from account (for withdrawal/transfer).
        
        Args:
            account_number: Account to debit
            amount: Amount to debit
            description: Transaction description
            idempotency_key: For retry safety
            
        Returns:
            Account data after debit
            
        Raises:
            InsufficientFundsException: If not enough balance
            ServiceUnavailableException: If Account Service is down
        """
        endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/debit"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if idempotency_key:
                    headers["Idempotency-Key"] = idempotency_key
                
                response = await client.post(
                    endpoint,
                    json={
                        "amount": amount,
                        "description": description
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                
                if response.status_code == 400:
                    raise AccountServiceException(response.json().get("error"))
                
                raise ServiceUnavailableException(
                    "Debit operation failed"
                )
                
        except httpx.RequestError:
            raise ServiceUnavailableException(
                "Account Service is unavailable"
            )

    async def credit_account(
        self,
        account_number: int,
        amount: float,
        description: str = "Transaction",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Credit amount to account (for deposit/transfer).
        
        Args:
            account_number: Account to credit
            amount: Amount to credit
            description: Transaction description
            idempotency_key: For retry safety
            
        Returns:
            Account data after credit
            
        Raises:
            ServiceUnavailableException: If Account Service is down
        """
        endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/credit"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if idempotency_key:
                    headers["Idempotency-Key"] = idempotency_key
                
                response = await client.post(
                    endpoint,
                    json={
                        "amount": amount,
                        "description": description
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                
                raise ServiceUnavailableException(
                    "Credit operation failed"
                )
                
        except httpx.RequestError:
            raise ServiceUnavailableException(
                "Account Service is unavailable"
            )

    async def get_account_privilege(self, account_number: int) -> str:
        """
        Get account privilege level.
        
        Args:
            account_number: Account number
            
        Returns:
            Privilege level (PREMIUM/GOLD/SILVER/BASIC)
        """
        endpoint = f"{self.base_url}/api/v1/accounts/{account_number}/privilege"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                
                if response.status_code == 200:
                    return response.json().get("privilege", "BASIC")
                
                raise ServiceUnavailableException(
                    "Could not fetch account privilege"
                )
                
        except httpx.RequestError:
            raise ServiceUnavailableException(
                "Account Service is unavailable"
            )


# Singleton instance
account_service_client = AccountServiceClient()
