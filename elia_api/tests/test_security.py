import pytest
from elia_api import security


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    # calling the registered_user dependancy will run the fixture which will create a user
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found(registered_user: dict):
    user = await security.get_user("not@a.user")

    assert user is None
