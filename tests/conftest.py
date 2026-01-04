"""Pytest configuration and fixtures."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///:memory:",
)


@pytest.fixture(scope=\"session\")
def event_loop():
    \"\"\"Create event loop for async tests.\"\"\"
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    \"\"\"Create test database engine.\"\"\"
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    \"\"\"Create test database session.\"\"\"
    TestingSessionLocal = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    \"\"\"Create test client.\"\"\"
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url=\"http://test\") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    \"\"\"Test user data.\"\"\"
    return {
        \"email\": \"test@example.com\",
        \"password\": \"test_password_123\",
        \"organization\": \"Test Org\",
    }


@pytest.fixture
def test_vqe_request():
    \"\"\"Test VQE request data.\"\"\"
    return {
        \"hamiltonian\": '{\"Z0\": 1.0, \"Z1\": 0.5}',
        \"ansatz_circuit\": {
            \"num_parameters\": 2,
            \"gates\": [\"RY\", \"CNOT\", \"RY\"],
        },
        \"optimizer\": \"COBYLA\",
        \"max_iterations\": 50,
        \"shots\": 1024,
    }


@pytest.fixture
def test_qaoa_request():
    \"\"\"Test QAOA request data.\"\"\"
    return {
        \"problem_graph\": {
            \"nodes\": [0, 1, 2, 3],
            \"edges\": [[0, 1], [1, 2], [2, 3], [3, 0]],
        },
        \"p\": 2,
        \"optimizer\": \"COBYLA\",
        \"shots\": 1024,
    }
