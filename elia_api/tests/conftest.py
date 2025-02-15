import os

os.environ["ENV_STATE"] = "test"
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from elia_api.database import database, metadata, engine
from elia_api.main import app


# only run once for all tests
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# provides the tests with the client object that can be used to make requests against
@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)

# provides the database for our tests to use anc cleans it before each test
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()

# resets the database before each test
@pytest.fixture(autouse=True, scope="function")
async def reset_database():
    """Drop and recreate tables before each test function."""
    async with database.transaction():
        metadata.drop_all(engine)
        metadata.create_all(engine)

# allows tests to use the async client
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url=client.base_url,
    ) as ac:
        yield ac
