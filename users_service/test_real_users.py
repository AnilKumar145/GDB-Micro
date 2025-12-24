"""
Quick test to verify the endpoint works with real database users.
"""

import asyncio
import httpx


async def test_verify_with_real_users():
    """Test verify endpoint with real database users."""
    
    base_url = "http://localhost:8003"
    
    print("=" * 70)
    print("Testing Verify Endpoint with Real Database Users")
    print("=" * 70)
    
    # Test Case 1: Valid credentials for john.doe
    print("\n✅ Test 1: Valid Credentials - john.doe with correct password")
    print("-" * 70)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/internal/v1/users/verify",
            json={
                "login_id": "john.doe",
                "password": "SecurePass123"  # You'll need to know the actual password
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    # Test Case 2: Invalid password
    print("\n❌ Test 2: Invalid Password - john.doe with wrong password")
    print("-" * 70)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/internal/v1/users/verify",
            json={
                "login_id": "john.doe",
                "password": "WrongPassword123"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    # Test Case 3: User not found
    print("\n❌ Test 3: User Not Found")
    print("-" * 70)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/internal/v1/users/verify",
            json={
                "login_id": "nonexistent.user",
                "password": "anypassword"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    # Test Case 4: Valid credentials for anil.kumar (ADMIN)
    print("\n✅ Test 4: Valid Credentials - anil.kumar (ADMIN role)")
    print("-" * 70)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/internal/v1/users/verify",
            json={
                "login_id": "anil.kumar",
                "password": "CorrectPassword123"  # You'll need to know the actual password
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    # Test Case 5: Valid credentials for doe.doe (TELLER)
    print("\n✅ Test 5: Valid Credentials - doe.doe (TELLER role)")
    print("-" * 70)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/internal/v1/users/verify",
            json={
                "login_id": "doe.doe",
                "password": "CorrectPassword123"  # You'll need to know the actual password
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("Note: For valid credentials tests, you need to provide the actual")
    print("password that was used to create these users in the database.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_verify_with_real_users())
