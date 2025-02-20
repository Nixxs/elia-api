import logging
import datetime
from jose import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from elia_api.database import database, user_table
from elia_api.config import config


logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])

SECRET_KEY = config.JWT_SECRET
ALGORITHM = "HS256"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail = "Could not validate credentials"
)

def access_token_expire_minutes() -> int:
    return 30

def create_access_token(user_id: str):
    logger.debug("Creating access token", extra={"id": user_id})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expire_minutes())
    jwt_data = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    logger.debug("Fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)

    if result:
        return result

async def authenticate_user(email: str, password: str) -> dict:
    user = await get_user(email)
    if not user:
        raise credentials_exception
    if not verify_password(password, user.password):
        raise credentials_exception

    return user