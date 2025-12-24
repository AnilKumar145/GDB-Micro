"""
Transfer Service

Handles transfer operations (FE012).

Business Logic:
1. Validate both from and to accounts via Account Service
2. Check both accounts are active
3. Verify PIN for source account
4. Validate amount
5. Check sufficient balance in source account
6. Check daily transfer limits (by privilege level)
7. Create transaction record
8. Debit source account, credit destination account
9. Log transaction to DB + file
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
    TransferFailedException,
    ServiceUnavailableException,
    InsufficientFundsException,
    SameAccountTransferException,
    TransferLimitExceededException,
    DailyTransactionCountExceededException,
)
from app.models.enums import TransactionType, TransferMode
from app.validation.validators import (
    AmountValidator,
    BalanceValidator,
    PINValidator,
    TransferValidator,
    TransferLimitValidator,
)
from app.integration.account_service_client import account_service_client
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.transfer_limit_repository import TransferLimitRepository
from app.repositories.transaction_log_repository import TransactionLogRepository

logger = logging.getLogger(__name__)


class TransferService:
    """Service for transfer operations."""

    def __init__(self):
        """Initialize service with repositories."""
        self.transaction_repo = TransactionRepository()
        self.limit_repo = TransferLimitRepository()
        self.log_repo = TransactionLogRepository()
        self.account_client = account_service_client

    async def process_transfer(
        self,
        from_account: int,
        to_account: int,
        amount: Decimal,
        pin: str,
        transfer_mode: TransferMode = TransferMode.NEFT,
        description: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process fund transfer operation.

        CRITICAL FLOW:
        1. Validate from and to accounts exist and are active
        2. Ensure accounts are different
        3. Verify PIN for source account
        4. Validate amount
        5. Check source account balance
        6. Check privilege and daily transfer limits
        7. Debit source account, credit destination account
        8. Log transaction to DB and file
        9. Return transaction details

        Args:
            from_account: Source account
            to_account: Destination account
            amount: Transfer amount
            pin: Account PIN for authorization
            transfer_mode: NEFT, RTGS, IMPS, etc.
            description: Optional description
            idempotency_key: For idempotency

        Returns:
            Dict with transaction details

        Raises:
            AccountNotFoundException: If account doesn't exist
            AccountNotActiveException: If account is not active
            SameAccountTransferException: If from == to
            InvalidPINException: If PIN is invalid
            InvalidAmountException: If amount is invalid
            InsufficientFundsException: If balance is insufficient
            TransferLimitExceededException: If daily limit exceeded
            DailyTransactionCountExceededException: If txn count exceeded
            TransferFailedException: If transfer fails
            ServiceUnavailableException: If Account Service is down
        """
        try:
            # STEP 1: Validate both accounts exist and are active (CRITICAL)
            logger.info(f"📋 Validating from account {from_account}")
            from_account_data = await self.account_client.validate_account(from_account)

            logger.info(f"📋 Validating to account {to_account}")
            to_account_data = await self.account_client.validate_account(to_account)

            # STEP 2: Ensure accounts are different
            logger.info(f"🔍 Checking accounts are different")
            TransferValidator.validate_different_accounts(from_account, to_account)

            # STEP 3: Verify PIN for source account
            logger.info(f"🔐 Validating PIN format")
            PINValidator.validate_pin_format(pin)

            logger.info(f"🔒 Verifying PIN for account {from_account}")
            await self.account_client.verify_pin(from_account, pin)

            # STEP 4: Validate amount
            logger.info(f"💰 Validating amount: ₹{amount}")
            AmountValidator.validate_transfer_amount(amount)

            # STEP 5: Check source account balance
            logger.info(f"💵 Checking balance")
            current_balance = from_account_data.get("balance", 0)
            BalanceValidator.validate_sufficient_balance(current_balance, float(amount))

            # STEP 6: Check privilege and daily transfer limits
            logger.info(f"📊 Checking daily transfer limits")
            privilege = from_account_data.get("privilege", "BASIC")
            daily_used = await self.limit_repo.get_daily_used_amount(from_account)
            daily_count = await self.limit_repo.get_daily_transaction_count(from_account)

            TransferLimitValidator.validate_transfer_limits(
                privilege, daily_used, daily_count, amount
            )

            # STEP 7: Debit source and credit destination via Account Service
            logger.info(f"💳 Debiting source account {from_account}")
            debit_result = await self.account_client.debit_account(
                account_number=from_account,
                amount=float(amount),
                description=description or f"Transfer to {to_account}",
                idempotency_key=idempotency_key,
            )

            logger.info(f"💳 Crediting destination account {to_account}")
            credit_result = await self.account_client.credit_account(
                account_number=to_account,
                amount=float(amount),
                description=description or f"Transfer from {from_account}",
                idempotency_key=idempotency_key,
            )

            from_new_balance = debit_result.get("new_balance", 0)
            to_new_balance = credit_result.get("new_balance", 0)

            # STEP 8: Log transaction to database - CREATE fund_transfers record FIRST
            transaction_id = await self.transaction_repo.create_transaction(
                from_account=from_account,
                to_account=to_account,
                amount=float(amount),
                transaction_type=TransactionType.TRANSFER,
                description=description or f"Transfer from {from_account} to {to_account}",
            )

            # STEP 9: Log to transaction_logging
            await self.log_repo.log_to_database(
                account_number=from_account,
                amount=float(amount),
                transaction_type=TransactionType.TRANSFER,
                reference_id=transaction_id,
                description=description,
            )

            # STEP 10: Log to file
            self.log_repo.log_to_file(
                account_number=from_account,
                amount=float(amount),
                transaction_type=TransactionType.TRANSFER,
                reference_id=transaction_id,
                description=description,
            )

            logger.info(f"✅ Transfer successful: Transaction ID {transaction_id}")

            return {
                "status": "SUCCESS",
                "transaction_id": transaction_id,
                "from_account": from_account,
                "to_account": to_account,
                "amount": float(amount),
                "transfer_mode": transfer_mode.value,
                "transaction_type": TransactionType.TRANSFER.value,
                "description": description,
                "from_account_new_balance": from_new_balance,
                "to_account_new_balance": to_new_balance,
                "transaction_date": datetime.utcnow().isoformat(),
            }

        except (
            AccountNotFoundException,
            AccountNotActiveException,
            SameAccountTransferException,
            InvalidPINException,
            InvalidAmountException,
            InsufficientFundsException,
            TransferLimitExceededException,
            DailyTransactionCountExceededException,
        ):
            raise

        except ServiceUnavailableException:
            raise

        except Exception as e:
            # Unexpected error
            logger.error(f"❌ Transfer failed: {str(e)}")
            raise TransferFailedException(f"Transfer failed: {str(e)}")



# Singleton instance
transfer_service = TransferService()
