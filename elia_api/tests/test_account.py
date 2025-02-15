import pytest
from httpx import AsyncClient

email = "test@user.com"
password = "password"

async def create_user(email: str, password: str, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/create-account",
        json={
            "email": email,
            "password": password,
        }
    )
    return response.json()

@pytest.fixture()
async def created_user(async_client: AsyncClient):
    return await create_user(email, password, async_client)

# test create user route
@pytest.mark.anyio
async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/create-account",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201
    print(response.json())
    assert {"id":1, "email":email, "password":password}.items() <= response.json().items()

# test get user route
@pytest.mark.anyio
async def test_get_user(async_client: AsyncClient, created_user: dict):
    response = await async_client.get(f"/get-account/{created_user['id']}")
    assert response.status_code == 200
    assert created_user.items() <= response.json().items()