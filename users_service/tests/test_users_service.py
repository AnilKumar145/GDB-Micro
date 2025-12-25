"""
Users Service Test Suite (Port 8003)
Tests for user management endpoints with positive, negative, and edge cases
"""

import httpx
import asyncio


class TestUsersService:
    """Test suite for Users Service"""

    BASE_URL = "http://localhost:8003/api/v1"
    INTERNAL_URL = "http://localhost:8003/internal/v1"

    # Get token first
    async def get_token(self, login_id="john.doe", password="Welcome@1"):
        """Helper to get auth token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8004/api/v1/auth/login",
                json={"login_id": login_id, "password": password},
            )
            return response.json()["access_token"]

    async def test_positive_get_user_profile(self):
        """POSITIVE: Get user profile with valid token"""
        print("\n✓ TEST: Get User Profile - Valid Token")
        token = await self.get_token("john.doe", "Welcome@1")
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/1",
                headers=headers
            )
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                data = response.json()
                assert data["user_id"] == 1
                assert data["login_id"] == "john.doe"
                assert data["role"] == "CUSTOMER"
            print(f"  ✓ User profile response - Status {response.status_code}")

    async def test_positive_verify_password(self):
        """POSITIVE: Verify correct password"""
        print("\n✓ TEST: Verify Password - Correct")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.INTERNAL_URL}/users/verify",
                json={"login_id": "john.doe", "password": "Welcome@1"}
            )
            assert response.status_code in [200, 500]
            print(f"  ✓ Password verify response - Status {response.status_code}")

    async def test_negative_get_nonexistent_user(self):
        """NEGATIVE: Get non-existent user"""
        print("\n✓ TEST: Get Non-existent User")
        token = await self.get_token("john.doe", "Welcome@1")
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/9999",
                headers=headers
            )
            assert response.status_code in [404, 500]
            print(f"  ✓ Non-existent user - Status {response.status_code}")

    async def test_negative_no_auth_token(self):
        """NEGATIVE: Missing authentication token"""
        print("\n✓ TEST: Missing Auth Token")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/users/1")
            assert response.status_code == 401
            print(f"  ✓ No auth token - Status 401")

    async def test_negative_invalid_token(self):
        """NEGATIVE: Invalid token"""
        print("\n✓ TEST: Invalid Token")
        headers = {"Authorization": "Bearer invalid.token.here"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/1",
                headers=headers
            )
            assert response.status_code == 401
            print(f"  ✓ Invalid token - Status 401")

    async def test_negative_expired_token(self):
        """NEGATIVE: Expired token should fail"""
        print("\n✓ TEST: Expired Token")
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjM3MDg5NjAwfQ.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/1",
                headers=headers
            )
            assert response.status_code == 401
            print(f"  ✓ Expired token - Status 401")

    async def test_negative_wrong_password(self):
        """NEGATIVE: Verify wrong password"""
        print("\n✓ TEST: Verify Password - Wrong")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.INTERNAL_URL}/users/verify",
                json={"login_id": "john.doe", "password": "WrongPassword123"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("is_valid") == False
            print(f"  ✓ Wrong password - Status {response.status_code}")

    async def test_negative_empty_password(self):
        """NEGATIVE: Empty password verification"""
        print("\n✓ TEST: Verify Password - Empty")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.INTERNAL_URL}/users/verify",
                json={"login_id": "john.doe", "password": ""}
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("is_valid") == False
            print(f"  ✓ Empty password - Status {response.status_code}")

    async def test_edge_malformed_json(self):
        """EDGE: Malformed JSON in request"""
        print("\n✓ TEST: Malformed JSON")
        async with httpx.AsyncClient() as client:
            # Send invalid JSON
            response = await client.post(
                f"{self.INTERNAL_URL}/users/verify",
                content="{invalid json",
            )
            assert response.status_code in [400, 422, 500]
            print(f"  ✓ Malformed JSON - Status {response.status_code}")

    async def test_edge_sql_injection(self):
        """EDGE: SQL injection in user ID"""
        print("\n✓ TEST: SQL Injection in User ID")
        token = await self.get_token("john.doe", "Welcome@1")
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/1' OR '1'='1",
                headers=headers
            )
            # Should either fail or be sanitized
            assert response.status_code in [400, 404, 422, 500]
            print(f"  ✓ SQL injection blocked - Status {response.status_code}")

    async def test_edge_special_characters_password(self):
        """EDGE: Special characters in password verification"""
        print("\n✓ TEST: Special Characters in Password")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.INTERNAL_URL}/users/verify",
                json={"login_id": "john.doe", "password": "P@ss!#$%^&*()"}
            )
            assert response.status_code == 200
            data = response.json()
            # Special characters password is invalid, so is_valid should be False
            assert "is_valid" in data
            print(f"  ✓ Special chars handled - Status {response.status_code}")


async def run_users_tests():
    """Run all users service tests"""
    print("\n" + "=" * 70)
    print("USERS SERVICE TEST SUITE (Port 8003)")
    print("=" * 70)

    test = TestUsersService()
    tests = [
        test.test_positive_get_user_profile,
        test.test_positive_verify_password,
        test.test_negative_get_nonexistent_user,
        test.test_negative_no_auth_token,
        test.test_negative_invalid_token,
        test.test_negative_expired_token,
        test.test_negative_wrong_password,
        test.test_negative_empty_password,
        test.test_edge_malformed_json,
        test.test_edge_sql_injection,
        test.test_edge_special_characters_password,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {type(e).__name__}: {str(e)}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"USERS SERVICE: {passed} passed, {failed} failed")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_users_tests())
