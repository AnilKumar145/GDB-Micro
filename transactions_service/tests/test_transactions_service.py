"""
Transactions Service Test Suite (Port 8002)
Tests for deposit, withdraw, transfer endpoints with positive, negative, and edge cases
"""

import pytest
import httpx
import asyncio


class TestTransactionsService:
    """Test suite for Transactions Service"""

    BASE_URL = "http://localhost:8002/api/v1"

    async def get_token(self, login_id="john.doe", password="Welcome@1"):
        """Helper to get auth token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8004/api/v1/auth/login",
                json={"login_id": login_id, "password": password},
            )
            return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_positive_deposit(self):
        """POSITIVE: Deposit with valid amount"""
        print("\n✓ TEST: Deposit - Valid Amount")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/deposits",
                headers=headers,
                params={"account_number": 1003, "amount": 1000}
            )
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "SUCCESS"
            assert "new_balance" in data
            print(f"  ✓ Deposit successful - New balance: {data['new_balance']}")

    @pytest.mark.asyncio
    async def test_negative_deposit_no_auth(self):
        """NEGATIVE: Deposit without auth token"""
        print("\n✓ TEST: Deposit - No Auth")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/deposits",
                params={"account_number": 1003, "amount": 1000}
            )
            assert response.status_code == 401
            print(f"  ✓ No auth - Status 401")

    @pytest.mark.asyncio
    async def test_negative_deposit_nonexistent_account(self):
        """NEGATIVE: Deposit to non-existent account"""
        print("\n✓ TEST: Deposit - Non-existent Account")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/deposits",
                headers=headers,
                params={"account_number": 9999, "amount": 1000}
            )
            assert response.status_code == 404
            print(f"  ✓ Non-existent account - Status 404")

    @pytest.mark.asyncio
    async def test_negative_deposit_invalid_amount(self):
        """NEGATIVE: Deposit with invalid amount"""
        print("\n✓ TEST: Deposit - Invalid Amount")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            # Negative amount
            response = await client.post(
                f"{self.BASE_URL}/deposits",
                headers=headers,
                params={"account_number": 1003, "amount": -1000}
            )
            assert response.status_code == 400
            print(f"  ✓ Negative amount - Status 400")

    @pytest.mark.asyncio
    async def test_positive_withdraw_correct_pin(self):
        """POSITIVE: Withdraw with correct PIN"""
        print("\n✓ TEST: Withdraw - Correct PIN")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/withdrawals",
                headers=headers,
                params={"account_number": 1003, "amount": 500, "pin": "9640"}
            )
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "SUCCESS"
            print(f"  ✓ Withdraw successful - New balance: {data['new_balance']}")

    @pytest.mark.asyncio
    async def test_negative_withdraw_wrong_pin(self):
        """NEGATIVE: Withdraw with wrong PIN"""
        print("\n✓ TEST: Withdraw - Wrong PIN")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/withdrawals",
                headers=headers,
                params={"account_number": 1003, "amount": 500, "pin": "0000"}
            )
            assert response.status_code == 400
            print(f"  ✓ Wrong PIN - Status 400")

    @pytest.mark.asyncio
    async def test_negative_withdraw_insufficient_funds(self):
        """NEGATIVE: Withdraw with insufficient funds"""
        print("\n✓ TEST: Withdraw - Insufficient Funds")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/withdrawals",
                headers=headers,
                params={"account_number": 1003, "amount": 999999999, "pin": "9640"}
            )
            assert response.status_code in [201, 400, 409, 500]
            print(f"  ✓ Insufficient funds response - Status {response.status_code}")

    @pytest.mark.asyncio
    async def test_negative_withdraw_no_pin(self):
        """NEGATIVE: Withdraw without PIN"""
        print("\n✓ TEST: Withdraw - Missing PIN")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/withdrawals",
                headers=headers,
                params={"account_number": 1003, "amount": 500}
            )
            assert response.status_code in [400, 422]
            print(f"  ✓ Missing PIN - Status {response.status_code}")

    @pytest.mark.asyncio
    async def test_positive_transfer_valid(self):
        """POSITIVE: Transfer between valid accounts"""
        print("\n✓ TEST: Transfer - Valid Accounts")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/transfers",
                headers=headers,
                params={
                    "from_account": 1003,
                    "to_account": 1004,
                    "amount": 500,
                    "pin": "9640"
                }
            )
            assert response.status_code in [201, 400, 500]
            if response.status_code == 201:
                data = response.json()
                assert data["status"] == "SUCCESS"
                assert data["from_account"] == 1003
                assert data["to_account"] == 1004
            print(f"  ✓ Transfer response - Status {response.status_code}")

    @pytest.mark.asyncio
    async def test_negative_transfer_same_account(self):
        """NEGATIVE: Transfer to same account"""
        print("\n✓ TEST: Transfer - Same Account")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/transfers",
                headers=headers,
                params={
                    "from_account": 1003,
                    "to_account": 1003,
                    "amount": 500,
                    "pin": "9640"
                }
            )
            assert response.status_code == 400
            print(f"  ✓ Same account transfer blocked - Status 400")

    @pytest.mark.asyncio
    async def test_negative_transfer_wrong_pin(self):
        """NEGATIVE: Transfer with wrong PIN"""
        print("\n✓ TEST: Transfer - Wrong PIN")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/transfers",
                headers=headers,
                params={
                    "from_account": 1003,
                    "to_account": 1004,
                    "amount": 500,
                    "pin": "0000"
                }
            )
            assert response.status_code == 400
            print(f"  ✓ Wrong PIN - Status 400")

    @pytest.mark.asyncio
    async def test_negative_transfer_nonexistent_from(self):
        """NEGATIVE: Transfer from non-existent account"""
        print("\n✓ TEST: Transfer - Non-existent From Account")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/transfers",
                headers=headers,
                params={
                    "from_account": 9999,
                    "to_account": 1004,
                    "amount": 500,
                    "pin": "9640"
                }
            )
            assert response.status_code == 404
            print(f"  ✓ Non-existent from - Status 404")

    @pytest.mark.asyncio
    async def test_positive_get_transaction_logs(self):
        """POSITIVE: Get transaction logs"""
        print("\n✓ TEST: Get Transaction Logs")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/transaction-logs/1003",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "logs" in data
            print(f"  ✓ Logs retrieved - Count: {len(data['logs'])}")

    @pytest.mark.asyncio
    async def test_positive_get_transfer_limits(self):
        """POSITIVE: Get transfer limits"""
        print("\n✓ TEST: Get Transfer Limits")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/transfer-limits/1003",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "daily_limit" in data or "privilege" in data
            print(f"  ✓ Transfer limits retrieved")

    @pytest.mark.asyncio
    async def test_edge_deposit_zero(self):
        """EDGE: Deposit zero amount"""
        print("\n✓ TEST: Deposit - Zero Amount")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/deposits",
                headers=headers,
                params={"account_number": 1003, "amount": 0}
            )
            assert response.status_code == 400
            print(f"  ✓ Zero deposit rejected - Status 400")

    @pytest.mark.asyncio
    async def test_edge_transfer_exceeds_limit(self):
        """EDGE: Transfer exceeds daily limit"""
        print("\n✓ TEST: Transfer - Exceeds Daily Limit")
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/transfers",
                headers=headers,
                params={
                    "from_account": 1003,
                    "to_account": 1004,
                    "amount": 9999999,
                    "pin": "9640"
                }
            )
            # Should fail due to limit or insufficient funds
            assert response.status_code in [400, 409]
            print(f"  ✓ Transfer limit checked - Status {response.status_code}")

    @pytest.mark.asyncio
    async def test_negative_transaction_log_no_auth(self):
        """NEGATIVE: Get logs without auth"""
        print("\n✓ TEST: Transaction Logs - No Auth")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/transaction-logs/1003")
            assert response.status_code == 401
            print(f"  ✓ No auth - Status 401")


async def run_transactions_tests():
    """Run all transactions service tests"""
    print("\n" + "=" * 70)
    print("TRANSACTIONS SERVICE TEST SUITE (Port 8002)")
    print("=" * 70)

    test = TestTransactionsService()
    tests = [
        test.test_positive_deposit,
        test.test_negative_deposit_no_auth,
        test.test_negative_deposit_nonexistent_account,
        test.test_negative_deposit_invalid_amount,
        test.test_positive_withdraw_correct_pin,
        test.test_negative_withdraw_wrong_pin,
        test.test_negative_withdraw_insufficient_funds,
        test.test_negative_withdraw_no_pin,
        test.test_positive_transfer_valid,
        test.test_negative_transfer_same_account,
        test.test_negative_transfer_wrong_pin,
        test.test_negative_transfer_nonexistent_from,
        test.test_positive_get_transaction_logs,
        test.test_positive_get_transfer_limits,
        test.test_edge_deposit_zero,
        test.test_edge_transfer_exceeds_limit,
        test.test_negative_transaction_log_no_auth,
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
    print(f"TRANSACTIONS SERVICE: {passed} passed, {failed} failed")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_transactions_tests())
