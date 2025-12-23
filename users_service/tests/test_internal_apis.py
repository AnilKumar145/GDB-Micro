"""
Tests for Internal User Service APIs
These tests demonstrate how other microservices will interact with internal endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from app.main import app


@pytest.mark.asyncio
class TestInternalUserAPIs:
    """Test internal user service endpoints."""
    
    async def test_get_user_details(self):
        """Test getting user details by login_id."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First, create a user
            response = await client.post(
                "/api/v1/users",
                json={
                    "username": "Test User",
                    "login_id": "test.internal",
                    "password": "testpass123",
                    "role": "CUSTOMER"
                }
            )
            assert response.status_code == 201
            
            # Now test internal endpoint
            response = await client.get("/internal/v1/users/test.internal")
            assert response.status_code == 200
            
            data = response.json()
            assert data["login_id"] == "test.internal"
            assert data["username"] == "Test User"
            assert data["role"] == "CUSTOMER"
            assert data["is_active"] == True
    
    async def test_get_nonexistent_user(self):
        """Test getting non-existent user returns 404."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/internal/v1/users/nonexistent.user")
            assert response.status_code == 404
    
    async def test_verify_user_credentials_success(self):
        """Test successful user credential verification."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user
            await client.post(
                "/api/v1/users",
                json={
                    "username": "Auth Test",
                    "login_id": "auth.test",
                    "password": "authpass123",
                    "role": "TELLER"
                }
            )
            
            # Verify credentials
            response = await client.post(
                "/internal/v1/users/verify",
                params={
                    "login_id": "auth.test",
                    "password": "authpass123"
                }
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["is_valid"] == True
            assert data["login_id"] == "auth.test"
            assert data["role"] == "TELLER"
    
    async def test_verify_user_credentials_failed(self):
        """Test failed user credential verification."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user
            await client.post(
                "/api/v1/users",
                json={
                    "username": "Wrong Pass Test",
                    "login_id": "wrongpass.test",
                    "password": "correctpass123",
                    "role": "CUSTOMER"
                }
            )
            
            # Try with wrong password
            response = await client.post(
                "/internal/v1/users/verify",
                params={
                    "login_id": "wrongpass.test",
                    "password": "wrongpass123"
                }
            )
            assert response.status_code == 401
    
    async def test_validate_user_role_success(self):
        """Test successful role validation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create ADMIN user
            await client.post(
                "/api/v1/users",
                json={
                    "username": "Admin User",
                    "login_id": "admin.validate",
                    "password": "adminpass123",
                    "role": "ADMIN"
                }
            )
            
            # Validate role
            response = await client.post(
                "/internal/v1/users/validate-role",
                params={
                    "login_id": "admin.validate",
                    "required_role": "ADMIN"
                }
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["has_role"] == True
            assert data["user_role"] == "ADMIN"
    
    async def test_validate_user_role_mismatch(self):
        """Test role validation with mismatched role."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create CUSTOMER user
            await client.post(
                "/api/v1/users",
                json={
                    "username": "Customer User",
                    "login_id": "customer.validate",
                    "password": "custpass123",
                    "role": "CUSTOMER"
                }
            )
            
            # Try to validate as TELLER
            response = await client.post(
                "/internal/v1/users/validate-role",
                params={
                    "login_id": "customer.validate",
                    "required_role": "TELLER"
                }
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["has_role"] == False
            assert data["user_role"] == "CUSTOMER"
    
    async def test_get_user_role_by_id(self):
        """Test getting user role by user_id."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user
            create_response = await client.post(
                "/api/v1/users",
                json={
                    "username": "Role Test",
                    "login_id": "role.test",
                    "password": "rolepass123",
                    "role": "TELLER"
                }
            )
            user_id = create_response.json()["user_id"]
            
            # Get role by user_id
            response = await client.get(f"/internal/v1/users/{user_id}/role")
            assert response.status_code == 200
            
            data = response.json()
            assert data["user_id"] == user_id
            assert data["role"] == "TELLER"
            assert data["is_active"] == True
    
    async def test_check_user_active_status(self):
        """Test checking user active status."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user
            await client.post(
                "/api/v1/users",
                json={
                    "username": "Status Test",
                    "login_id": "status.test",
                    "password": "statuspass123",
                    "role": "CUSTOMER"
                }
            )
            
            # Check status
            response = await client.get("/internal/v1/users/status.test/status")
            assert response.status_code == 200
            
            data = response.json()
            assert data["login_id"] == "status.test"
            assert data["is_active"] == True
    
    async def test_bulk_validate_users(self):
        """Test bulk user validation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create multiple users
            for i in range(3):
                await client.post(
                    "/api/v1/users",
                    json={
                        "username": f"Bulk User {i}",
                        "login_id": f"bulk.user{i}",
                        "password": "bulkpass123",
                        "role": "CUSTOMER"
                    }
                )
            
            # Bulk validate
            response = await client.post(
                "/internal/v1/users/bulk-validate",
                json={
                    "login_ids": ["bulk.user0", "bulk.user1", "nonexistent"]
                }
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["total_valid"] == 2
            assert data["total_invalid"] == 1
            assert "bulk.user0" in [u["login_id"] for u in data["valid_users"]]
    
    async def test_search_users_by_role(self):
        """Test searching users by role."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create TELLER users
            for i in range(2):
                await client.post(
                    "/api/v1/users",
                    json={
                        "username": f"Teller {i}",
                        "login_id": f"teller.search{i}",
                        "password": "tellerpass123",
                        "role": "TELLER"
                    }
                )
            
            # Search by role
            response = await client.get(
                "/internal/v1/users",
                params={"role": "TELLER"}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["users"]) > 0
            assert all(u["role"] == "TELLER" for u in data["users"])
    
    async def test_search_users_with_limit(self):
        """Test searching users with limit."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Search with limit
            response = await client.get(
                "/internal/v1/users",
                params={"limit": 5}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["users"]) <= 5
    
    async def test_health_check(self):
        """Test internal health check endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/internal/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "user-management"
            assert "version" in data


# Integration test examples
class TestInternalAPIIntegration:
    """Examples of how other microservices would use internal APIs."""
    
    @staticmethod
    async def auth_service_example():
        """Example: Auth Service authentication flow."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Step 1: User submits login
            login_id = "auth.example"
            password = "authpass123"
            
            # Step 2: Create test user
            await client.post(
                "/api/v1/users",
                json={
                    "username": "Auth Example",
                    "login_id": login_id,
                    "password": password,
                    "role": "CUSTOMER"
                }
            )
            
            # Step 3: Auth Service calls verify endpoint
            verify_response = await client.post(
                "/internal/v1/users/verify",
                params={
                    "login_id": login_id,
                    "password": password
                }
            )
            
            if verify_response.status_code == 200:
                user_data = verify_response.json()
                # Generate JWT with user_id and role
                return {
                    "authenticated": True,
                    "user_id": user_data["user_id"],
                    "role": user_data["role"]
                }
    
    @staticmethod
    async def transactions_service_example():
        """Example: Transactions Service authorization check."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create test TELLER user
            create_resp = await client.post(
                "/api/v1/users",
                json={
                    "username": "Teller Example",
                    "login_id": "teller.example",
                    "password": "tellerpass123",
                    "role": "TELLER"
                }
            )
            
            # Transaction Service wants to verify user can transfer funds
            validate_response = await client.post(
                "/internal/v1/users/validate-role",
                params={
                    "login_id": "teller.example",
                    "required_role": "TELLER"
                }
            )
            
            if validate_response.status_code == 200:
                result = validate_response.json()
                if result["has_role"]:
                    # Proceed with transfer
                    return {"authorized": True}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
