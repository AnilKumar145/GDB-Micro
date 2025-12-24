"""
Test to verify the verify_user_credentials endpoint fix.
Tests that user_id, role, and is_active are always present in response.
"""

import pytest
import asyncio
from app.api.internal_user_routes import InternalUserService
from app.repositories.user_repository import UserRepository
from unittest.mock import AsyncMock, MagicMock


class TestVerifyUserCredentialsFix:
    """Test that verify_user_credentials always returns consistent fields."""
    
    @pytest.mark.asyncio
    async def test_verify_credentials_user_not_found(self):
        """Test: User not found returns null user_id but consistent structure."""
        # Mock repository
        repo = AsyncMock(spec=UserRepository)
        repo.get_user_by_login_id = AsyncMock(return_value=None)
        
        service = InternalUserService(repo)
        result = await service.verify_user_credentials("unknown.user", "password123")
        
        # Verify response structure is consistent
        assert "is_valid" in result
        assert "user_id" in result
        assert "role" in result
        assert "is_active" in result
        
        # Verify values for not found case
        assert result["is_valid"] is False
        assert result["user_id"] is None
        assert result["role"] is None
        assert result["is_active"] is False
        
        print("✅ Test passed: User not found returns consistent structure with null user_id")
    
    @pytest.mark.asyncio
    async def test_verify_credentials_invalid_password(self):
        """Test: Invalid password returns null user_id but consistent structure."""
        # Mock repository with valid user but wrong password
        repo = AsyncMock(spec=UserRepository)
        repo.get_user_by_login_id = AsyncMock(return_value={
            "id": 123,
            "login_id": "john.doe",
            "username": "John Doe",
            "password_hash": "$2b$12$invalidhash",
            "role": "TELLER",
            "is_active": True
        })
        
        service = InternalUserService(repo)
        result = await service.verify_user_credentials("john.doe", "wrongpassword")
        
        # Verify response structure is consistent
        assert "is_valid" in result
        assert "user_id" in result
        assert "role" in result
        assert "is_active" in result
        
        # Verify values for invalid password case
        assert result["is_valid"] is False
        assert result["user_id"] is None
        assert result["role"] is None
        assert result["is_active"] is False
        
        print("✅ Test passed: Invalid password returns consistent structure with null user_id")
    
    @pytest.mark.asyncio
    async def test_verify_credentials_valid(self):
        """Test: Valid credentials return all fields with actual values."""
        # Create a valid bcrypt hash for password "TestPass123"
        import bcrypt
        password = "TestPass123"
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Mock repository with valid user
        repo = AsyncMock(spec=UserRepository)
        repo.get_user_by_login_id = AsyncMock(return_value={
            "id": 456,
            "login_id": "jane.smith",
            "username": "Jane Smith",
            "password_hash": hashed,
            "role": "ADMIN",
            "is_active": True
        })
        
        service = InternalUserService(repo)
        result = await service.verify_user_credentials("jane.smith", password)
        
        # Verify response structure is consistent
        assert "is_valid" in result
        assert "user_id" in result
        assert "role" in result
        assert "is_active" in result
        
        # Verify values for valid credentials case
        assert result["is_valid"] is True
        assert result["user_id"] == 456
        assert result["role"] == "ADMIN"
        assert result["is_active"] is True
        
        print("✅ Test passed: Valid credentials return all fields with actual values")


if __name__ == "__main__":
    # Run tests manually
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
