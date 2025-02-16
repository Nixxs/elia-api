import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware

from elia_api.database import database
from elia_api.routers.account import router as account_router
from elia_api.config import config
from elia_api.logging_conf import configure_logging

logger = logging.getLogger(__name__)


# CORS settings
origins = [
    config.FRONTEND_URL,  # Add production frontend domain at some point
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting elia-api")
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(account_router)
