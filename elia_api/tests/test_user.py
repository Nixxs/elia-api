import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.com", "1234")
    assert response.status_code == 201
    assert "User Created" in response.json()["detail"]


@pytest.mark.anyio
async def test_user_exists(async_client: AsyncClient, registered_user: dict):
    response = await register_user(async_client, registered_user["email"], "1234")
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
