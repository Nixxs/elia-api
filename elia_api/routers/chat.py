import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from elia_api.models.user import User
from elia_api.models.chat import ChatResponse
from elia_api.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# protect a route by requireing the current user
@router.post("/chat", response_model=ChatResponse, status_code=200)
async def get_user_by_id(current_user: Annotated[User, Depends(get_current_user)]):
    email = current_user.email
    return ChatResponse(message=f"Hello {email}")