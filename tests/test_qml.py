"""QML service tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_submit_vqe_job(client: AsyncClient, test_user_data, test_vqe_request):
    \"\"\"Test VQE job submission.\"\"\"
    # Register and login
    register_response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    access_token = register_response.json()[\"access_token\"]
    
    # Submit VQE job
    response = await client.post(
        \"/api/v1/qml/vqe\",
        json=test_vqe_request,
        headers={\"Authorization\": f\"Bearer {access_token}\"},
    )
    
    assert response.status_code == 202
    data = response.json()
    assert \"id\" in data
    assert data[\"job_type\"] == \"vqe\"
    assert data[\"status\"] == \"SUBMITTED\"


@pytest.mark.asyncio
async def test_submit_qaoa_job(client: AsyncClient, test_user_data, test_qaoa_request):
    \"\"\"Test QAOA job submission.\"\"\"
    # Register and login
    register_response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    access_token = register_response.json()[\"access_token\"]
    
    # Submit QAOA job
    response = await client.post(
        \"/api/v1/qml/qaoa\",
        json=test_qaoa_request,
        headers={\"Authorization\": f\"Bearer {access_token}\"},
    )
    
    assert response.status_code == 202
    data = response.json()
    assert \"id\" in data
    assert data[\"job_type\"] == \"qaoa\"
    assert data[\"status\"] == \"SUBMITTED\"


@pytest.mark.asyncio
async def test_get_job(client: AsyncClient, test_user_data, test_vqe_request):
    \"\"\"Test getting job status.\"\"\"
    # Register and login
    register_response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    access_token = register_response.json()[\"access_token\"]
    
    # Submit VQE job
    submit_response = await client.post(
        \"/api/v1/qml/vqe\",
        json=test_vqe_request,
        headers={\"Authorization\": f\"Bearer {access_token}\"},
    )
    job_id = submit_response.json()[\"id\"]
    
    # Get job
    response = await client.get(
        f\"/api/v1/qml/jobs/{job_id}\",
        headers={\"Authorization\": f\"Bearer {access_token}\"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data[\"id\"] == job_id
    assert data[\"job_type\"] == \"vqe\"


@pytest.mark.asyncio
async def test_list_jobs(client: AsyncClient, test_user_data, test_vqe_request):
    \"\"\"Test listing user's jobs.\"\"\"
    # Register and login
    register_response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    access_token = register_response.json()[\"access_token\"]
    
    # Submit multiple jobs
    for _ in range(3):
        await client.post(
            \"/api/v1/qml/vqe\",
            json=test_vqe_request,
            headers={\"Authorization\": f\"Bearer {access_token}\"},
        )
    
    # List jobs
    response = await client.get(
        \"/api/v1/qml/jobs\",
        headers={\"Authorization\": f\"Bearer {access_token}\"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data[\"jobs\"]) == 3
    assert data[\"total_count\"] == 3
    assert data[\"has_more\"] == False


@pytest.mark.asyncio
async def test_unauthorized_job_access(client: AsyncClient, test_user_data, test_vqe_request):
    \"\"\"Test unauthorized access to another user's job.\"\"\"
    # Register first user
    user1_response = await client.post(
        \"/api/v1/auth/register\",
        json=test_user_data,
    )
    user1_token = user1_response.json()[\"access_token\"]
    
    # Submit job as user1
    submit_response = await client.post(
        \"/api/v1/qml/vqe\",
        json=test_vqe_request,
        headers={\"Authorization\": f\"Bearer {user1_token}\"},
    )
    job_id = submit_response.json()[\"id\"]
    
    # Register second user
    user2_data = {
        \"email\": \"user2@example.com\",
        \"password\": \"test_password_123\",
    }
    user2_response = await client.post(
        \"/api/v1/auth/register\",
        json=user2_data,
    )
    user2_token = user2_response.json()[\"access_token\"]
    
    # Try to access user1's job as user2
    response = await client.get(
        f\"/api/v1/qml/jobs/{job_id}\",
        headers={\"Authorization\": f\"Bearer {user2_token}\"},
    )
    
    assert response.status_code == 403
    assert \"unauthorized\" in response.json()[\"detail\"].lower()
