"""
Integration test for the verify endpoint fix.
Tests the endpoint response with consistent user_id handling.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.user_repository import UserRepository
from unittest.mock import AsyncMock, patch
import json
import bcrypt


class TestVerifyEndpointFix:
    """Test that verify endpoint returns consistent response structure."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_verify_endpoint_response_structure_user_not_found(self):
        """Test response structure when user not found."""
        # Mock the repository
        with patch('app.api.internal_user_routes.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_user_by_login_id = AsyncMock(return_value=None)
            mock_repo_class.return_value = mock_repo
            
            response = self.client.post(
                "/internal/v1/users/verify",
                json={
                    "login_id": "nonexistent.user",
                    "password": "anypassword"
                }
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            # Verify response has all expected fields
            assert "is_valid" in data, "Response missing 'is_valid' field"
            assert "user_id" in data, "Response missing 'user_id' field"
            assert "role" in data, "Response missing 'role' field"
            assert "is_active" in data, "Response missing 'is_active' field"
            
            # Verify values for not found case
            assert data["is_valid"] is False, f"Expected is_valid=False, got {data['is_valid']}"
            assert data["user_id"] is None, f"Expected user_id=None, got {data['user_id']}"
            assert data["role"] is None, f"Expected role=None, got {data['role']}"
            assert data["is_active"] is False, f"Expected is_active=False, got {data['is_active']}"
            
            print("✅ User not found response has consistent structure")
            print(f"   Response: {json.dumps(data, indent=2)}")
    
    def test_verify_endpoint_response_structure_invalid_password(self):
        """Test response structure when password is invalid."""
        # Mock the repository with valid user but wrong password
        with patch('app.api.internal_user_routes.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock(spec=UserRepository)
            # Use a valid bcrypt hash for testing
            password = "ValidPassword123"
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            mock_repo.get_user_by_login_id = AsyncMock(return_value={
                "user_id": 456,
                "login_id": "john.doe",
                "username": "John Doe",
                "password": hashed,  # Fixed: use "password" not "password_hash"
                "role": "TELLER",
                "is_active": True
            })
            mock_repo_class.return_value = mock_repo
            
            response = self.client.post(
                "/internal/v1/users/verify",
                json={
                    "login_id": "john.doe",
                    "password": "WrongPassword456"
                }
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            # Verify response has all expected fields
            assert "is_valid" in data, "Response missing 'is_valid' field"
            assert "user_id" in data, "Response missing 'user_id' field"
            assert "role" in data, "Response missing 'role' field"
            assert "is_active" in data, "Response missing 'is_active' field"
            
            # For invalid password, fields should be null/false
            assert data["is_valid"] is False, f"Expected is_valid=False for wrong password, got {data['is_valid']}"
            assert data["user_id"] is None, "user_id should be null for invalid password"
            assert data["role"] is None, "role should be null for invalid password"
            assert data["is_active"] is True, "is_active should be true (account is still active despite invalid password)"
            
            print("✅ Invalid password response has consistent structure")
            print(f"   Response: {json.dumps(data, indent=2)}")
    
    def test_verify_endpoint_response_structure_valid_credentials(self):
        """Test response structure when credentials are valid."""
        # Mock the repository with valid user and correct password
        with patch('app.api.internal_user_routes.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock(spec=UserRepository)
            # Use a valid bcrypt hash for testing
            password = "ValidPassword123"
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            mock_repo.get_user_by_login_id = AsyncMock(return_value={
                "user_id": 789,
                "login_id": "jane.smith",
                "username": "Jane Smith",
                "password": hashed,  # Fixed: use "password" not "password_hash"
                "role": "ADMIN",
                "is_active": True
            })
            mock_repo_class.return_value = mock_repo
            
            response = self.client.post(
                "/internal/v1/users/verify",
                json={
                    "login_id": "jane.smith",
                    "password": password  # Correct password
                }
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            # Verify response has all expected fields
            assert "is_valid" in data, "Response missing 'is_valid' field"
            assert "user_id" in data, "Response missing 'user_id' field"
            assert "role" in data, "Response missing 'role' field"
            assert "is_active" in data, "Response missing 'is_active' field"
            
            # For valid credentials, fields should have actual values
            assert data["is_valid"] is True, f"Expected is_valid=True, got {data['is_valid']}"
            assert data["user_id"] == 789, f"Expected user_id=789, got {data['user_id']}"
            assert data["role"] == "ADMIN", f"Expected role=ADMIN, got {data['role']}"
            assert data["is_active"] is True, f"Expected is_active=True, got {data['is_active']}"
            
            print("✅ Valid credentials response has all actual values")
            print(f"   Response: {json.dumps(data, indent=2)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
