"""
Withdraw Service

Handles withdrawal operations (FE010).

Business Logic:
1. Validate account via Account Service
2. Check account is active
3. Verify PIN
4. Check sufficient balance
5. Debit amount from account
6. Log transaction to DB + file
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

from app.exceptions.transaction_exceptions import (
    AccountNotFoundException,
    AccountNotActiveException,
    InvalidAmountException,
    InvalidPINException,
    WithdrawalFailedException,
    ServiceUnavailableException,
    InsufficientFundsException,
)
from app.models.enums import TransactionType, TransactionStatus
from app.validation.validators import (
    AmountValidator,
    BalanceValidator,
    PINValidator,
)
from app.integration.account_service_client import account_service_client
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.transaction_log_repository import TransactionLogRepository

logger = logging.getLogger(__name__)


class WithdrawService:
    """Service for withdrawal operations."""

    def __init__(self):
        """Initialize service with repositories."""
        self.transaction_repo = TransactionRepository()
        self.log_repo = TransactionLogRepository()
        self.account_client = account_service_client

    async def process_withdraw(
        self,
        account_number: int,
        amount: Decimal,
        pin: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process withdrawal operation.

        CRITICAL FLOW:
        1. Validate account exists and is active via Account Service
        2. Validate PIN format
        3. Verify PIN via Account Service
        4. Validate amount
        5. Check sufficient balance
        6. Create transaction record
        7. Debit account via Account Service
        8. Log transaction to DB and file
        9. Return transaction details

        Args:
            account_number: Account to withdraw from
            amount: Withdrawal amount
            pin: Account PIN
            description: Optional description

        Returns:
            Dict with transaction details

        Raises:
            AccountNotFoundException: If account doesn't exist
            AccountNotActiveException: If account is not active
            InvalidPINException: If PIN is invalid
            InvalidAmountException: If amount is invalid
            InsufficientFundsException: If balance is insufficient
            WithdrawalFailedException: If withdrawal fails
            ServiceUnavailableException: If Account Service is down
        """
        transaction_id = None

        try:
            # STEP 1: Validate account exists and is active (CRITICAL)
            logger.info(f"📋 Validating account {account_number}")
            account_data = await self.account_client.validate_account(account_number)

            # STEP 2: Validate PIN format
            logger.info(f"🔐 Validating PIN format")
            PINValidator.validate_pin_format(pin)

            # STEP 3: Verify PIN via Account Service
            logger.info(f"🔒 Verifying PIN")
            await self.account_client.verify_pin(account_number, pin)

            # STEP 4: Validate amount
            logger.info(f"💰 Validating amount: ₹{amount}")
            AmountValidator.validate_withdrawal_amount(amount)

            # STEP 5: Check sufficient balance
            logger.info(f"💵 Checking balance")
            current_balance = account_data.get("balance", 0)
            BalanceValidator.validate_sufficient_balance(current_balance, float(amount))

            # STEP 6: Create transaction record
            logger.info(f"📝 Creating transaction record")
            transaction_id = await self.transaction_repo.create_transaction(
                from_account=account_number,
                to_account=None,  # Withdrawal has no destination
                amount=amount,
                transaction_type=TransactionType.WITHDRAW,
                status=TransactionStatus.PENDING,
                description=description,
            )

            # STEP 7: Debit account via Account Service
            logger.info(f"💳 Debiting account {account_number}")
            debit_result = await self.account_client.debit_account(
                account_number=account_number,
                amount=float(amount),
                description=description or "Withdrawal",
            )

            new_balance = debit_result.get("new_balance", 0)

            # STEP 8: Update transaction status to SUCCESS
            await self.transaction_repo.update_transaction_status(
                transaction_id, TransactionStatus.SUCCESS
            )

            # STEP 9: Log to database
            await self.log_repo.log_to_database(
                account_number=account_number,
                amount=amount,
                transaction_type=TransactionType.WITHDRAW,
                status=TransactionStatus.SUCCESS,
                reference_id=transaction_id,
                description=description,
            )

            # STEP 10: Log to file
            self.log_repo.log_to_file(
                account_number=account_number,
                amount=amount,
                transaction_type=TransactionType.WITHDRAW,
                status=TransactionStatus.SUCCESS,
                reference_id=transaction_id,
                description=description,
            )

            logger.info(f"✅ Withdrawal successful: Transaction ID {transaction_id}")

            return {
                "status": "SUCCESS",
                "transaction_id": transaction_id,
                "account_number": account_number,
                "amount": float(amount),
                "transaction_type": TransactionType.WITHDRAW.value,
                "description": description,
                "new_balance": new_balance,
                "transaction_date": datetime.utcnow().isoformat(),
            }

        except (
            AccountNotFoundException,
            AccountNotActiveException,
            InvalidPINException,
            InvalidAmountException,
            InsufficientFundsException,
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
            logger.error(f"❌ Withdrawal failed: {str(e)}")
            if transaction_id:
                await self.transaction_repo.update_transaction_status(
                    transaction_id,
                    TransactionStatus.FAILED,
                    error_message=str(e),
                )

            raise WithdrawalFailedException(f"Withdrawal failed: {str(e)}")


# Singleton instance
withdraw_service = WithdrawService()
