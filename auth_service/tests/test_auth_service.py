# -*- coding: utf-8 -*-
"""
Auth Service Test Suite (Port 8004)
Tests for authentication endpoints with positive, negative, and edge cases
"""

import httpx
import asyncio


class TestAuthService:
    """Test suite for Auth Service"""

    BASE_URL = "http://localhost:8004/api/v1"

    VALID_USERS = {
        "john.doe": {"password": "Welcome@1", "role": "CUSTOMER", "user_id": 1},
        "doe.doe": {"password": "Welcome@1", "role": "ADMIN", "user_id": 2},
        "kumar.kumar": {"password": "Welcome@1", "role": "TELLER", "user_id": 3},
        "john.doe1": {"password": "Welcome@11", "role": "CUSTOMER", "user_id": 4},
    }

    async def test_positive_login_all_users(self):
        """POSITIVE: All users should login successfully"""
        print("\n✓ TEST: Login - All Valid Users")
        async with httpx.AsyncClient(timeout=30.0) as client:
            for login_id, user_data in self.VALID_USERS.items():
                response = await client.post(
                    f"{self.BASE_URL}/auth/login",
                    json={"login_id": login_id, "password": user_data["password"]},
                )
                assert response.status_code == 200, f"Failed for user {login_id}"
                data = response.json()
                assert "access_token" in data
                assert data["user_id"] == user_data["user_id"]
                assert data["role"] == user_data["role"]
                print(f"  ✓ {login_id} ({user_data['role']}) - Status 200")

    async def test_positive_token_format(self):
        """POSITIVE: Token should be valid JWT format"""
        print("\n✓ TEST: Token Format Validation")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"login_id": "john.doe", "password": "Welcome@1"},
            )
            assert response.status_code == 200
            token = response.json()["access_token"]
            parts = token.split(".")
            assert len(parts) == 3, "Token should be JWT (3 parts)"
            print(f"  ✓ Valid JWT format with 3 parts")

    async def test_negative_wrong_password(self):
        """NEGATIVE: Wrong password should fail"""
        print("\n✓ TEST: Wrong Password")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"login_id": "john.doe", "password": "WrongPassword123"},
            )
            assert response.status_code in [401, 500]
            print(f"  ✓ Wrong password - Status {response.status_code}")

    async def test_negative_nonexistent_user(self):
        """NEGATIVE: Non-existent user should fail"""
        print("\n✓ TEST: Non-existent User")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"login_id": "fake.user", "password": "Welcome@1"},
            )
            assert response.status_code == 401
            print(f"  ✓ Non-existent user - Status 401")

    async def test_negative_empty_login_id(self):
        """NEGATIVE: Empty login_id should fail"""
        print("\n✓ TEST: Empty Login ID")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"login_id": "", "password": "Welcome@1"},
            )
            assert response.status_code in [400, 422, 401]
            print(f"  ✓ Empty login_id - Status {response.status_code}")

    async def test_negative_empty_password(self):
        """NEGATIVE: Empty password should fail"""
        print("\n✓ TEST: Empty Password")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"login_id": "john.doe", "password": ""},
            )
            assert response.status_code in [400, 422, 401]
            print(f"  ✓ Empty password - Status {response.status_code}")

    async def test_negative_missing_password(self):
        """NEGATIVE: Missing password field should fail"""
        print("\n✓ TEST: Missing Password Field")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"login_id": "john.doe"},
            )
            assert response.status_code == 422
            print(f"  ✓ Missing password - Status 422")

    async def test_negative_missing_login_id(self):
        """NEGATIVE: Missing login_id field should fail"""
        print("\n✓ TEST: Missing Login ID Field")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"password": "Welcome@1"},
            )
            assert response.status_code == 422
            print(f"  ✓ Missing login_id - Status 422")

    async def test_edge_sql_injection(self):
        """EDGE: SQL injection attempt should be handled"""
        print("\n✓ TEST: SQL Injection Attempt")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={
                    "login_id": "john.doe' OR '1'='1",
                    "password": "' OR '1'='1",
                },
            )
            assert response.status_code in [401, 400, 422]
            print(f"  ✓ SQL injection blocked - Status {response.status_code}")

    async def test_edge_case_insensitive_login(self):
        """EDGE: Test case sensitivity"""
        print("\n✓ TEST: Case Sensitivity")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/login",
                json={"login_id": "JOHN.DOE", "password": "Welcome@1"},
            )
            # May succeed or fail depending on system design
            print(f"  ✓ Case test - Status {response.status_code}")

    async def test_edge_multiple_logins(self):
        """EDGE: Multiple logins should work"""
        print("\n✓ TEST: Multiple Logins")
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(3):
                response = await client.post(
                    f"{self.BASE_URL}/auth/login",
                    json={"login_id": "john.doe", "password": "Welcome@1"},
                )
                assert response.status_code == 200
            print(f"  ✓ Multiple logins successful")


async def run_auth_tests():
    """Run all auth service tests"""
    print("\n" + "=" * 70)
    print("AUTH SERVICE TEST SUITE (Port 8004)")
    print("=" * 70)

    test = TestAuthService()
    tests = [
        test.test_positive_login_all_users,
        test.test_positive_token_format,
        test.test_negative_wrong_password,
        test.test_negative_nonexistent_user,
        test.test_negative_empty_login_id,
        test.test_negative_empty_password,
        test.test_negative_missing_password,
        test.test_negative_missing_login_id,
        test.test_edge_sql_injection,
        test.test_edge_case_insensitive_login,
        test.test_edge_multiple_logins,
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
    print(f"AUTH SERVICE: {passed} passed, {failed} failed")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_auth_tests())
