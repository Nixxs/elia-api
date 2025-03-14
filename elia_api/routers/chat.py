import logging
import json
from typing import Annotated, Union, List
from elia_api.config import config

from fastapi import APIRouter, HTTPException, Depends

from elia_api.models.user import User
from elia_api.models.chat import ChatResponse, Prompt, FunctionCall
from elia_api.security import get_current_user
import google.generativeai as genai

from elia_api.tools.registry import BACKEND_FUNCTION_REGISTRY
from elia_api.tools import tools

from elia_api.database import database, chat_history_table


router = APIRouter()
logger = logging.getLogger(__name__)

async def limit_chat_history(user_id: int, limit: int = config.CHAT_HISTORY_LIMIT):
    query = """
        DELETE FROM chat_history
        WHERE id IN (
            SELECT id FROM chat_history
            WHERE user_id = :user_id
            ORDER BY timestamp ASC
            OFFSET :limit
        )
    """
    await database.execute(query, {"user_id": user_id, "limit": limit})

async def get_chat_history(user_id: int, limit: int = 10):
    query = chat_history_table.select().where(
        chat_history_table.c.user_id == user_id
    ).order_by(
        chat_history_table.c.timestamp.desc()
    ).limit(limit)
    rows = await database.fetch_all(query)
    return list(reversed(rows))  # Chronological order

def summarise_result(result, function_name):
    if isinstance(result, dict) and "features" in result:
        return f"Function Call: {function_name} -> [GeoJSON with {len(result['features'])} features omitted]"
    elif isinstance(result, str) and len(result) > 500:
        return f"Function Call: {function_name} -> [Large response omitted, length={len(result)}]"
    else:
        return f"Function Call: {function_name} -> {str(result)[:500]}"  # Trim long responses

def format_content(role: str, message: str):
    return {
        "role": role,
        "parts": [{"text": message}]
    }


async def assemble_context(user_id: int, new_prompt: str, limit: int = 10):
    history = await get_chat_history(user_id, limit=limit)
    context = []

    for row in history:
        match row["role"]:
            case "user":
                context.append(format_content("user", row["message"]))

            case "function":
                # Gemini doesn't accept 'function' role, map to 'model'
                context.append(format_content("model", row["message"]))

            case "model":
                # Check if it's a function call or plain text
                try:
                    parsed = json.loads(row["message"])
                    if "name" in parsed and "args" in parsed:
                        # It's a function call
                        context.append({
                            "role": "model",
                            "parts": [{"function_call": parsed}]
                        })
                    else:
                        # Regular model message
                        context.append(format_content("model", row["message"]))
                except json.JSONDecodeError:
                    # Regular model message if not JSON
                    context.append(format_content("model", row["message"]))

            case _:
                print(f"Unknown role '{row['role']}' in chat history, skipping...")

    # Add latest user message
    context.append(format_content("user", new_prompt))
    return context

@router.post("/chat", response_model=Union[ChatResponse, FunctionCall], status_code=200)
async def chat_with_function_call(
    current_user: Annotated[User, Depends(get_current_user)],
    prompt: Prompt
):
    user_id = current_user.id
    logger.info(f"User ID {user_id} sent prompt: {prompt.message}")

    # Store user message
    await database.execute(
        chat_history_table.insert().values(
            user_id=user_id,
            message=prompt.message,
            role="user"
        )
    )

    try:
        final_prompt = await assemble_context(user_id, prompt.message, limit=10)
        model = genai.GenerativeModel(config.GOOGLE_LLM_MODEL)

        response = model.generate_content(
            contents=final_prompt,
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

                    # Handle backend-registered functions (like get_weather)
                    if function_name in BACKEND_FUNCTION_REGISTRY:
                        result = BACKEND_FUNCTION_REGISTRY[function_name](**arguments)

                        result_summary = summarise_result(result, function_name)
                        await database.execute(
                            chat_history_table.insert().values(
                                user_id=user_id,
                                message=result_summary,
                                role="model"
                            )
                        )

                        await limit_chat_history(user_id)
                        return ChatResponse(message=str(result))  # Return as chat message

                    # Handle frontend-only functions (like add_marker)
                    await limit_chat_history(user_id)
                    func_call_summary = f"Function Call: {function_name} with args {arguments}"
                    return FunctionCall(name=function_name, arguments=arguments, message=func_call_summary)

                # Handle plain chat message
                elif part.text:
                    await database.execute(
                        chat_history_table.insert().values(
                            user_id=user_id,
                            message=part.text,
                            role="model"
                        )
                    )
                    await limit_chat_history(user_id)

                    logger.info(f"Chat Response to User ID {user_id}: {part.text}")
                    return ChatResponse(message=part.text)
                
        # No content case
        await database.execute(
            chat_history_table.insert().values(
                user_id=user_id,
                message="No content returned.",
                role="model"
            )
        )
        await limit_chat_history(user_id)
        return ChatResponse(message="No content returned.")

    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get response from LLM.")

@router.get("/chat/history", response_model=List[str])
async def get_history(current_user: Annotated[User, Depends(get_current_user)]):
    history = await get_chat_history(current_user.id, limit=100)

    readable_history = []
    for h in history:
        # Map role to readable name
        if h["role"] == "user":
            speaker = "User"
        elif h["role"] == "model":
            speaker = "Assistant"
        elif h["role"] == "function":
            speaker = "Function Result"
        else:
            speaker = "Unknown"

        readable_history.append(f"{speaker}: {h['message']}")

    return readable_history
