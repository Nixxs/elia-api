import logging

from fastapi import APIRouter, HTTPException

from elia_api.database import database, user_table
from elia_api.models.user import UserIn
from elia_api.security import get_user, get_password_hash

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn):
    # if a user is returned then the email aready exists
    if await get_user(user.email):
        raise HTTPException(
            status_code=400, detail="A user with that email already exists"
        )

    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)

    await database.execute(query)

    return {"detail": "User Created."}
