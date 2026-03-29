"""
Shared pytest fixtures for yooti-dashboard API tests.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def anyio_backend():
    return "asyncio"
