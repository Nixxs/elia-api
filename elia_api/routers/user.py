import logging

from fastapi import APIRouter, HTTPException, Depends

from elia_api.database import database, user_table
from elia_api.models.user import UserIn, User
from elia_api.security import get_user, get_password_hash, authenticate_user, create_access_token, oauth2_scheme, get_current_user

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


@router.post("/token", status_code=200)
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


# protect a route by requireing the token
# get the user in the route
@router.get("/user", response_model=User, status_code=200)
async def get_user_by_id(token: str = Depends(oauth2_scheme)):
    current_user: User = await get_current_user(token)  # noqa
    return current_user

