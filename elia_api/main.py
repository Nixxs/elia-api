import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware

from elia_api.database import database
from elia_api.routers.user import router as user_router
from elia_api.routers.chat import router as chat_router
from elia_api.routers.test import router as test_router
from elia_api.config import config
from elia_api.logging_conf import configure_logging

from elia_api.llm import init_gemini
from elia_api.bigquery import init_bigquery

logger = logging.getLogger(__name__)


# CORS settings
origins = [
    config.FRONTEND_URL,  # Add production frontend domain at some point
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting elia-api")

    # Initialize Gemini
    init_gemini()

    # Initialize BigQuery
    init_bigquery() 

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

app.add_middleware(CorrelationIdMiddleware)

# Include routers
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(test_router)

@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)