import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from elia_api.models.user import User
from elia_api.models.chat import ChatResponse, Prompt
from elia_api.security import get_current_user
import google.generativeai as genai  # Gemini SDK

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse, status_code=200)
async def get_gemini_response(
    current_user: Annotated[User, Depends(get_current_user)],
    prompt: Prompt
):
    email = current_user.email
    logger.info(f"User {email} sent prompt: {prompt.message}")

    try:
        # Instantiate the Gemini model (this is lightweight and recommended per call)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        # Call Gemini with the user's message
        response = model.generate_content(prompt.message)

        # Extract text response
        gemini_reply = response.text

        return ChatResponse(message=gemini_reply)

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get response from LLM.")