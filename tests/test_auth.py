"""Authentication tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_user_data):
    \"\"\"Test user registration.\"\"\"
    response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert \"access_token\" in data
    assert \"refresh_token\" in data
    assert data[\"token_type\"] == \"bearer\"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user_data):
    \"\"\"Test registration with duplicate email.\"\"\"
    # First registration
    await client.post(\"/api/v1/auth/register\", json=test_user_data)
    
    # Second registration with same email
    response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    
    assert response.status_code == 409
    assert \"already registered\" in response.json()[\"detail\"].lower()


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, test_user_data):
    \"\"\"Test user login.\"\"\"
    # Register user
    await client.post(\"/api/v1/auth/register\", json=test_user_data)
    
    # Login
    response = await client.post(
        \"/api/v1/auth/login\",
        json={
            \"email\": test_user_data[\"email\"],
            \"password\": test_user_data[\"password\"],
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert \"access_token\" in data
    assert \"refresh_token\" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user_data):
    \"\"\"Test login with invalid credentials.\"\"\"
    # Register user
    await client.post(\"/api/v1/auth/register\", json=test_user_data)
    
    # Login with wrong password
    response = await client.post(
        \"/api/v1/auth/login\",
        json={
            \"email\": test_user_data[\"email\"],
            \"password\": \"wrong_password\",
        },
    )
    
    assert response.status_code == 401
    assert \"invalid\" in response.json()[\"detail\"].lower()


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user_data):
    \"\"\"Test token refresh.\"\"\"
    # Register user
    register_response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    refresh_token = register_response.json()[\"refresh_token\"]
    
    # Refresh token
    response = await client.post(
        \"/api/v1/auth/refresh\",
        json={\"refresh_token\": refresh_token},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert \"access_token\" in data
    assert \"refresh_token\" in data


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user_data):
    \"\"\"Test getting current user profile.\"\"\"
    # Register user
    register_response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    access_token = register_response.json()[\"access_token\"]
    
    # Get current user
    response = await client.get(
        \"/api/v1/auth/me\",
        headers={\"Authorization\": f\"Bearer {access_token}\"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data[\"email\"] == test_user_data[\"email\"]
    assert \"id\" in data
