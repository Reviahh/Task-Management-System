"""Pytest configuration and fixtures."""
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.task import Task


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_tasks.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """Create test database and tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    TestSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestSessionLocal
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_db):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def sample_task(client):
    """Create a sample task for testing."""
    response = await client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "medium",
            "tags": ["test", "sample"]
        }
    )
    return response.json()

