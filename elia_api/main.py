from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware

from elia_api.database import database
from elia_api.routers.account import router as account_router

# CORS settings
origins = [
    "http://localhost:8080",  # Frontend running locally
    "http://127.0.0.1:8080",
    "https://frontend-domain.com",  # Add production frontend domain at some point
]

@asynccontextmanager
async def lifespan(app: FastAPI):
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
