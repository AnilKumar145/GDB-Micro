"""
Deposit Service

Handles deposit operations (FE011).

Business Logic:
1. Validate account via Account Service
2. Check account is active
3. Credit amount to account
4. Log transaction to DB + file
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

from app.exceptions.transaction_exceptions import (
    AccountNotFoundException,
    AccountNotActiveException,
    InvalidAmountException,
    DepositFailedException,
    ServiceUnavailableException,
)
from app.models.enums import TransactionType, TransactionStatus
from app.validation.validators import AmountValidator
from app.integration.account_service_client import account_service_client
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.transaction_log_repository import TransactionLogRepository

logger = logging.getLogger(__name__)


class DepositService:
    """Service for deposit operations."""

    def __init__(self):
        """Initialize service with repositories."""
        self.transaction_repo = TransactionRepository()
        self.log_repo = TransactionLogRepository()
        self.account_client = account_service_client

    async def process_deposit(
        self,
        account_number: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process deposit operation.

        CRITICAL FLOW:
        1. Validate account exists and is active via Account Service
        2. Validate amount
        3. Create transaction record
        4. Credit account via Account Service
        5. Log transaction to DB and file
        6. Return transaction details

        Args:
            account_number: Account to deposit to
            amount: Deposit amount
            description: Optional description

        Returns:
            Dict with transaction details

        Raises:
            AccountNotFoundException: If account doesn't exist
            AccountNotActiveException: If account is not active
            InvalidAmountException: If amount is invalid
            DepositFailedException: If deposit fails
            ServiceUnavailableException: If Account Service is down
        """
        transaction_id = None

        try:
            # STEP 1: Validate account exists and is active (CRITICAL)
            logger.info(f"📋 Validating account {account_number}")
            account_data = await self.account_client.validate_account(account_number)

            # STEP 2: Validate amount
            logger.info(f"💰 Validating amount: ₹{amount}")
            AmountValidator.validate_deposit_amount(amount)

            # STEP 3: Create transaction record
            logger.info(f"📝 Creating transaction record")
            transaction_id = await self.transaction_repo.create_transaction(
                from_account=None,  # Deposit has no source
                to_account=account_number,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.PENDING,
                description=description,
            )

            # STEP 4: Credit account via Account Service
            logger.info(f"💳 Crediting account {account_number}")
            credit_result = await self.account_client.credit_account(
                account_number=account_number,
                amount=float(amount),
                description=description or "Deposit",
            )

            new_balance = credit_result.get("new_balance", 0)

            # STEP 5: Update transaction status to SUCCESS
            await self.transaction_repo.update_transaction_status(
                transaction_id, TransactionStatus.SUCCESS
            )

            # STEP 6: Log to database
            await self.log_repo.log_to_database(
                account_number=account_number,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.SUCCESS,
                reference_id=transaction_id,
                description=description,
            )

            # STEP 7: Log to file
            self.log_repo.log_to_file(
                account_number=account_number,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.SUCCESS,
                reference_id=transaction_id,
                description=description,
            )

            logger.info(f"✅ Deposit successful: Transaction ID {transaction_id}")

            return {
                "status": "SUCCESS",
                "transaction_id": transaction_id,
                "account_number": account_number,
                "amount": float(amount),
                "transaction_type": TransactionType.DEPOSIT.value,
                "description": description,
                "new_balance": new_balance,
                "transaction_date": datetime.utcnow().isoformat(),
            }

        except (
            AccountNotFoundException,
            AccountNotActiveException,
            InvalidAmountException,
        ):
            # Log failed transaction
            if transaction_id:
                await self.transaction_repo.update_transaction_status(
                    transaction_id, TransactionStatus.FAILED
                )
            raise

        except ServiceUnavailableException:
            # Account Service is down
            if transaction_id:
                await self.transaction_repo.update_transaction_status(
                    transaction_id, TransactionStatus.FAILED
                )
            raise

        except Exception as e:
            # Unexpected error
            logger.error(f"❌ Deposit failed: {str(e)}")
            if transaction_id:
                await self.transaction_repo.update_transaction_status(
                    transaction_id,
                    TransactionStatus.FAILED,
                    error_message=str(e),
                )

            raise DepositFailedException(f"Deposit failed: {str(e)}")


# Singleton instance
deposit_service = DepositService()
