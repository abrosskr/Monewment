import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app

# We need an async client for FastAPI
@pytest.mark.asyncio
async def test_read_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

@pytest.mark.asyncio
async def test_get_services_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/services/list")
    assert response.status_code == 200
    assert "installed" in response.json()
