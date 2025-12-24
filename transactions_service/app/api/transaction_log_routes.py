"""
Transaction Log API Routes

GET /api/v1/transaction-logs/{account} - Get logs for account
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from app.models import TransactionLoggingResponse
from app.services.transaction_log_service import transaction_log_service
from app.exceptions.transaction_exceptions import TransactionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["transaction-logs"])


@router.get(
    "/transaction-logs/{account_number}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Transaction logs retrieved"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def get_transaction_logs(
    account_number: int,
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Max results per page"),
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
):
    """
    Get transaction logs for an account.

    With optional date range filtering and pagination.

    **Path Parameters:**
    - account_number: Account number

    **Query Parameters:**
    - skip: Pagination offset (default 0)
    - limit: Max results per page (default 50, max 100)
    - start_date: Filter from date (YYYY-MM-DD format)
    - end_date: Filter to date (YYYY-MM-DD format)

    **Response:**
    - account_number: Requested account
    - logs: List of transaction logs with details
    - skip: Pagination offset used
    - limit: Pagination limit used
    - has_more: Whether more results available

    **Errors:**
    - 404: Account not found
    - 503: Service unavailable
    """
    logger.info(
        f"📋 Get transaction logs - Account: {account_number}, "
        f"Skip: {skip}, Limit: {limit}"
    )

    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        result = await transaction_log_service.get_transaction_logs(
            account_number=account_number,
            skip=skip,
            limit=limit,
            start_date=start_dt,
            end_date=end_dt,
        )

        logger.info(f"✅ Retrieved logs for account {account_number}")
        return result

    except ValueError as e:
        logger.warning(f"⚠️ Invalid date format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_DATE_FORMAT", "message": "Use YYYY-MM-DD format"},
        )

    except TransactionException as e:
        logger.warning(f"⚠️ Failed to get logs: {e.error_code}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@router.get(
    "/transaction-logs/transaction/{reference_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Transaction logs retrieved"},
        404: {"description": "Transaction not found"},
        503: {"description": "Service unavailable"},
    },
)
async def get_logs_by_reference_id(reference_id: str):
    """
    Get all logs for a specific transaction.

    **Path Parameters:**
    - reference_id: Transaction ID to look up

    **Response:**
    - reference_id: Transaction ID
    - logs: List of all logs for this transaction
    - count: Number of logs

    **Errors:**
    - 404: Transaction not found
    - 503: Service unavailable
    """
    logger.info(f"🔍 Get logs for transaction {reference_id}")

    try:
        result = await transaction_log_service.get_logs_by_reference_id(reference_id)
        logger.info(f"✅ Retrieved logs for transaction {reference_id}")
        return result

    except TransactionException as e:
        logger.warning(f"⚠️ Transaction not found: {reference_id}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@router.get(
    "/transaction-logs/date/{date}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "File logs retrieved"},
        404: {"description": "Logs not found for date"},
        503: {"description": "Service unavailable"},
    },
)
async def get_file_logs(date: str):
    """
    Get file-based transaction logs for a specific date.

    Useful for auditing and debugging.

    **Path Parameters:**
    - date: Date to read logs for (YYYY-MM-DD format)

    **Response:**
    - date: Date of logs
    - log_lines: List of raw log lines
    - count: Number of log entries

    **Errors:**
    - 404: No logs found for date
    - 503: Service unavailable
    """
    logger.info(f"📄 Get file logs for date {date}")

    try:
        # Parse date
        dt = datetime.strptime(date, "%Y-%m-%d")

        result = await transaction_log_service.get_file_logs(dt)
        logger.info(f"✅ Retrieved file logs for {date}")
        return result

    except ValueError:
        logger.warning(f"⚠️ Invalid date format: {date}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_DATE_FORMAT", "message": "Use YYYY-MM-DD format"},
        )

    except TransactionException as e:
        logger.warning(f"⚠️ File logs not found for {date}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@router.get(
    "/transaction-logs/summary/{account_number}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Summary stats retrieved"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def get_transaction_summary(
    account_number: int,
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
):
    """
    Get transaction summary statistics for an account.

    Provides overview of all transactions in period.

    **Path Parameters:**
    - account_number: Account number

    **Query Parameters:**
    - start_date: Filter from date (YYYY-MM-DD format)
    - end_date: Filter to date (YYYY-MM-DD format)

    **Response:**
    - account_number: Account
    - total_transactions: Total count
    - successful_transactions: Count of SUCCESS
    - failed_transactions: Count of FAILED
    - total_amount_transferred: Sum of amounts
    - by_type: Breakdown by transaction type (DEPOSIT, WITHDRAW, TRANSFER)
    - date_range: Applied filters

    **Errors:**
    - 404: Account not found
    - 503: Service unavailable
    """
    logger.info(f"📊 Get summary for account {account_number}")

    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        result = await transaction_log_service.get_summary_stats(
            account_number=account_number,
            start_date=start_dt,
            end_date=end_dt,
        )

        logger.info(f"✅ Summary retrieved for account {account_number}")
        return result

    except ValueError as e:
        logger.warning(f"⚠️ Invalid date format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_DATE_FORMAT", "message": "Use YYYY-MM-DD format"},
        )

    except TransactionException as e:
        logger.warning(f"⚠️ Failed to get summary: {e.error_code}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )
