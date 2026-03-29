"""
Unit tests for the health endpoint.
Example of the test pattern to follow for all route tests.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_returns_200(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_health_returns_ok_status(client: AsyncClient) -> None:
    response = await client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_health_returns_version(client: AsyncClient) -> None:
    response = await client.get("/health")
    data = response.json()
    assert "version" in data


@pytest.mark.anyio
async def test_health_returns_environment(client: AsyncClient) -> None:
    response = await client.get("/health")
    data = response.json()
    assert "environment" in data
