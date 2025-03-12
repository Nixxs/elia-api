import logging
from typing import Annotated, Union

from fastapi import APIRouter, HTTPException, Depends

from elia_api.models.user import User
from elia_api.models.chat import ChatResponse, Prompt, FunctionCall
from elia_api.security import get_current_user
import google.generativeai as genai

from elia_api.tools.registry import BACKEND_FUNCTION_REGISTRY
from elia_api.tools import tools

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=Union[ChatResponse, FunctionCall], status_code=200)
async def chat_with_function_call(
    current_user: Annotated[User, Depends(get_current_user)],
    prompt: Prompt
):
    email = current_user.email
    logger.info(f"User {email} sent prompt: {prompt.message}")

    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        response = model.generate_content(
            prompt.message,
            tools=tools,  # List of callable tools
        )

        candidates = response.candidates or []
        if candidates:
            parts = candidates[0].content.parts or []
            if parts:
                part = parts[0]
                # Handle function call
                if part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    arguments = dict(function_call.args)

                    logger.info(f"Tool Call: {function_name} with args {arguments}")

                    # Handle backend-registered functions (like get_weather)
                    if function_name in BACKEND_FUNCTION_REGISTRY:
                        result = BACKEND_FUNCTION_REGISTRY[function_name](**arguments)
                        return ChatResponse(message=str(result))  # Return as chat message

                    # Handle frontend-only functions (like add_marker)
                    return FunctionCall(name=function_name, arguments=arguments)

                # Handle plain chat message
                elif part.text:
                    logger.info(f"Chat Response: {part.text}")
                    return ChatResponse(message=part.text)

        return ChatResponse(message="No content returned.")

    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get response from LLM.")
