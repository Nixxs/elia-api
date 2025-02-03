from contextlib import asynccontextmanager

from fastapi import FastAPI

from elia_api.database import database
from elia_api.routers.account import router as account_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(account_router)
