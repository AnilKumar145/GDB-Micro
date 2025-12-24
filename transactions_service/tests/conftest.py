"""
Pytest Configuration and Fixtures for Transaction Service Tests

This module provides shared fixtures for:
- Mock database connections
- Mock Account Service client
- Mock repository instances
- Service instances with mocks
- Sample data for testing
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
import json
import tempfile
import os


# ============================================================================
# EVENT LOOP FIXTURE
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create and close event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
async def mock_db_connection():
    """Mock database connection for testing."""
    mock_db = AsyncMock()
    mock_db.fetch = AsyncMock()
    mock_db.fetchrow = AsyncMock()
    mock_db.execute = AsyncMock()
    return mock_db


@pytest.fixture
async def mock_db_pool():
    """Mock database connection pool."""
    pool = AsyncMock()
    pool.acquire = AsyncMock()
    pool.release = AsyncMock()
    return pool


# ============================================================================
# ACCOUNT SERVICE CLIENT FIXTURES
# ============================================================================

@pytest.fixture
async def mock_account_service_client():
    """Mock Account Service client for inter-service communication."""
    client = AsyncMock()
    
    # Setup default responses
    client.validate_account = AsyncMock(return_value={
        "account_number": 1001,
        "account_holder": "Test User",
        "account_type": "SAVINGS",
        "is_active": True,
        "balance": 100000.00,
        "privilege": "PREMIUM"
    })
    
    client.verify_pin = AsyncMock(return_value={"valid": True})
    
    client.debit_account = AsyncMock(return_value={
        "success": True,
        "new_balance": 95000.00
    })
    
    client.credit_account = AsyncMock(return_value={
        "success": True,
        "new_balance": 105000.00
    })
    
    client.get_account_privilege = AsyncMock(return_value="PREMIUM")
    
    return client


# ============================================================================
# REPOSITORY FIXTURES
# ============================================================================

@pytest.fixture
async def mock_transaction_repository():
    """Mock transaction repository."""
    repo = AsyncMock()
    repo.create_transaction = AsyncMock(return_value=1001)
    repo.get_transaction = AsyncMock(return_value={
        "transaction_id": 1001,
        "from_account": 1001,
        "to_account": 1002,
        "amount": 5000.00,
        "transaction_type": "TRANSFER",
        "status": "SUCCESS",
        "transaction_date": datetime.now()
    })
    repo.get_account_transactions = AsyncMock(return_value=[])
    return repo


@pytest.fixture
async def mock_transfer_limit_repository():
    """Mock transfer limit repository."""
    repo = AsyncMock()
    repo.get_daily_used_amount = AsyncMock(return_value=Decimal("30000.00"))
    repo.update_daily_used_amount = AsyncMock()
    repo.get_transfer_rule = AsyncMock(return_value={
        "privilege_level": "PREMIUM",
        "daily_limit": Decimal("100000.00"),
        "daily_transaction_count": 50
    })
    return repo


@pytest.fixture
async def mock_transaction_log_repository():
    """Mock transaction log repository."""
    repo = AsyncMock()
    repo.log_transaction_to_db = AsyncMock()
    repo.log_transaction_to_file = AsyncMock()
    repo.get_logs_for_transaction = AsyncMock(return_value={
        "transaction_id": 1001,
        "logs": []
    })
    repo.get_account_logs = AsyncMock(return_value={
        "account_number": 1001,
        "total_count": 10,
        "logs": []
    })
    return repo


# ============================================================================
# SERVICE FIXTURES
# ============================================================================

@pytest.fixture
async def deposit_service(mock_db_connection, mock_account_service_client, 
                          mock_transaction_repository, mock_transaction_log_repository):
    """Deposit service with mocked dependencies."""
    from unittest.mock import MagicMock
    
    service = MagicMock()
    service.db = mock_db_connection
    service.account_client = mock_account_service_client
    service.transaction_repo = mock_transaction_repository
    service.log_repo = mock_transaction_log_repository
    
    # Mock async method
    service.process_deposit = AsyncMock(return_value={
        "status": "SUCCESS",
        "transaction_id": 1001,
        "amount": 10000.00,
        "transaction_date": datetime.now(),
        "description": "Test Deposit"
    })
    
    return service


@pytest.fixture
async def withdraw_service(mock_db_connection, mock_account_service_client,
                           mock_transaction_repository, mock_transaction_log_repository):
    """Withdraw service with mocked dependencies."""
    from unittest.mock import MagicMock
    
    service = MagicMock()
    service.db = mock_db_connection
    service.account_client = mock_account_service_client
    service.transaction_repo = mock_transaction_repository
    service.log_repo = mock_transaction_log_repository
    
    # Mock async method
    service.process_withdraw = AsyncMock(return_value={
        "status": "SUCCESS",
        "transaction_id": 1001,
        "amount": 5000.00,
        "transaction_date": datetime.now(),
        "description": "Test Withdrawal"
    })
    
    return service


@pytest.fixture
async def transfer_service(mock_db_connection, mock_account_service_client,
                           mock_transaction_repository, mock_transfer_limit_repository,
                           mock_transaction_log_repository):
    """Transfer service with mocked dependencies."""
    from unittest.mock import MagicMock
    
    service = MagicMock()
    service.db = mock_db_connection
    service.account_client = mock_account_service_client
    service.transaction_repo = mock_transaction_repository
    service.limit_repo = mock_transfer_limit_repository
    service.log_repo = mock_transaction_log_repository
    
    # Mock async method
    service.process_transfer = AsyncMock(return_value={
        "status": "SUCCESS",
        "transaction_id": 1001,
        "from_account": 1001,
        "to_account": 1002,
        "amount": 5000.00,
        "transaction_date": datetime.now()
    })
    
    return service


@pytest.fixture
async def transfer_limit_service(mock_db_connection, mock_account_service_client,
                                 mock_transfer_limit_repository):
    """Transfer limit service with mocked dependencies."""
    from unittest.mock import MagicMock
    
    service = MagicMock()
    service.db = mock_db_connection
    service.account_client = mock_account_service_client
    service.limit_repo = mock_transfer_limit_repository
    
    # Mock async methods
    service.get_transfer_limit = AsyncMock(return_value={
        "account_number": 1001,
        "privilege_level": "PREMIUM",
        "daily_limit": Decimal("100000.00"),
        "used_today": Decimal("30000.00"),
        "remaining": Decimal("70000.00")
    })
    
    service.get_remaining_limit = AsyncMock(return_value=Decimal("70000.00"))
    
    service.get_all_transfer_rules = AsyncMock(return_value=[
        {
            "privilege_level": "PREMIUM",
            "daily_limit": Decimal("100000.00"),
            "daily_transaction_count": 50
        },
        {
            "privilege_level": "GOLD",
            "daily_limit": Decimal("50000.00"),
            "daily_transaction_count": 30
        },
        {
            "privilege_level": "SILVER",
            "daily_limit": Decimal("25000.00"),
            "daily_transaction_count": 20
        }
    ])
    
    return service


@pytest.fixture
async def transaction_log_service(mock_db_connection, mock_transaction_log_repository):
    """Transaction log service with mocked dependencies."""
    from unittest.mock import MagicMock
    
    service = MagicMock()
    service.db = mock_db_connection
    service.log_repo = mock_transaction_log_repository
    
    # Mock async methods
    service.log_transaction_to_db = AsyncMock()
    service.log_transaction_to_file = AsyncMock()
    service.get_logs_for_transaction = AsyncMock(return_value={})
    service.get_account_logs = AsyncMock(return_value={})
    
    return service


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_deposit_request():
    """Sample deposit request data."""
    return {
        "account_number": 1001,
        "amount": 10000.00,
        "description": "Salary Deposit"
    }


@pytest.fixture
def sample_withdraw_request():
    """Sample withdraw request data."""
    return {
        "account_number": 1001,
        "amount": 5000.00,
        "pin": "1234",
        "description": "ATM Withdrawal"
    }


@pytest.fixture
def sample_transfer_request():
    """Sample transfer request data."""
    return {
        "from_account": 1001,
        "to_account": 1002,
        "amount": 5000.00,
        "pin": "1234",
        "description": "Payment to friend"
    }


@pytest.fixture
def sample_account_data():
    """Sample account data from Account Service."""
    return {
        "account_number": 1001,
        "account_holder": "Test User",
        "account_type": "SAVINGS",
        "is_active": True,
        "balance": 100000.00,
        "privilege": "PREMIUM",
        "created_date": datetime.now(),
        "email": "test@example.com",
        "phone": "9999999999"
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction record."""
    return {
        "transaction_id": 1001,
        "from_account": 1001,
        "to_account": 1002,
        "amount": Decimal("5000.00"),
        "transaction_type": "TRANSFER",
        "status": "SUCCESS",
        "idempotency_key": "unique-key-123",
        "transaction_date": datetime.now(),
        "description": "Test transfer",
        "error_message": None
    }


@pytest.fixture
def sample_transfer_limit_data():
    """Sample transfer limit data."""
    return {
        "account_number": 1001,
        "privilege_level": "PREMIUM",
        "daily_limit": Decimal("100000.00"),
        "daily_transaction_count": 50,
        "used_today": Decimal("30000.00"),
        "transaction_count_today": 5,
        "reset_date": (datetime.now() + timedelta(days=1)).date()
    }


# ============================================================================
# EXCEPTION FIXTURES
# ============================================================================

@pytest.fixture
def exception_classes():
    """Transaction service exception classes."""
    exceptions = {
        "InsufficientBalanceException": type("InsufficientBalanceException", (Exception,), {
            "http_code": 400,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        }),
        "InvalidPINException": type("InvalidPINException", (Exception,), {
            "http_code": 401,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        }),
        "DailyLimitExceededException": type("DailyLimitExceededException", (Exception,), {
            "http_code": 400,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        }),
        "AccountNotFoundException": type("AccountNotFoundException", (Exception,), {
            "http_code": 404,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        }),
        "AccountInactiveException": type("AccountInactiveException", (Exception,), {
            "http_code": 400,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        }),
        "InvalidAmountException": type("InvalidAmountException", (Exception,), {
            "http_code": 400,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        }),
        "SameAccountTransferException": type("SameAccountTransferException", (Exception,), {
            "http_code": 400,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        }),
        "ServiceUnavailableException": type("ServiceUnavailableException", (Exception,), {
            "http_code": 503,
            "__init__": lambda self, msg="": Exception.__init__(self, msg)
        })
    }
    return exceptions


# ============================================================================
# TEMPORARY FILE FIXTURES
# ============================================================================

@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


# ============================================================================
# ASYNC HELPER FIXTURES
# ============================================================================

@pytest.fixture
def mock_async_context_manager():
    """Create mock for async context manager."""
    async_mock = AsyncMock()
    async_mock.__aenter__ = AsyncMock(return_value=async_mock)
    async_mock.__aexit__ = AsyncMock(return_value=None)
    return async_mock


# ============================================================================
# HTTPX CLIENT MOCK FIXTURE (for API testing)
# ============================================================================

@pytest.fixture
async def mock_http_client():
    """Mock HTTP client for Account Service calls."""
    client = AsyncMock()
    client.post = AsyncMock()
    client.get = AsyncMock()
    client.close = AsyncMock()
    return client
