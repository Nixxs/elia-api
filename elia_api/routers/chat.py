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
        return f"Run Tool: {function_name} -> [GeoJSON with {len(result['features'])} features omitted]"
    elif isinstance(result, str) and len(result) > 500:
        return f"Run Tool: {function_name} -> [Large response omitted, length={len(result)}]"
    else:
        return f"Run Tool: {function_name} -> {str(result)[:500]}"  # Trim long responses

def format_content(role: str, message: str):
    return {
        "role": role,
        "parts": [{"text": message}]
    }

async def assemble_context(user_id: int, limit: int = 10):
    history = await get_chat_history(user_id, limit=limit)
    context = []

    for row in history:
        match row["role"]:
            case "user":
                context.append(format_content("user", row["message"]))

            case "model":
                try:
                    parsed = json.loads(row["message"])

                    if "function_response" in parsed:
                        # It's a function response
                        context.append({
                            "role": "model",
                            "parts": [{"function_response": parsed["function_response"]}]
                        })

                    elif "name" in parsed and "args" in parsed:
                        # It's a function call
                        context.append({
                            "role": "model",
                            "parts": [{"function_call": parsed}]
                        })

                    else:
                        # Regular model text message
                        context.append(format_content("model", row["message"]))

                except json.JSONDecodeError:
                    # Fallback: plain model message
                    context.append(format_content("model", row["message"]))

            case _:
                print(f"Unknown role '{row['role']}' in chat history, skipping...")

    # Walk backwards to find the earliest valid entry point
    # gemini needs to have a function_call > function_response > text order if you stuff that it won't work
    # so this trim is necessary so that we are sending valid context to the context window
    trim_index = 0  # Start of trimmed context

    for i in range(len(context)):
        part = context[i]["parts"][0]

        # If we find a user message -> valid conversation start
        if context[i]["role"] == "user":
            trim_index = i
            break  # Stop trimming here

        # If we find a natural text response from model, also a safe start
        if "text" in part:
            trim_index = i
            break  # Stop trimming here

        # Otherwise, keep trimming until we find something valid

    # Now return trimmed context
    trimmed_context = context[trim_index:]

    return trimmed_context

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
        model = genai.GenerativeModel(config.GOOGLE_LLM_MODEL)
        final_text_response = None

        while True:  # Loop allows Gemini to call multiple functions IF IT DECIDES to
            # Assemble latest context including function calls/results
            final_prompt = await assemble_context(user_id, limit=10)

            response = model.generate_content(
                contents=final_prompt,
                tools=tools,  # Callable tools
            )

            candidates = response.candidates or []
            if not candidates:
                break  # Nothing to process, exit loop

            parts = candidates[0].content.parts or []
            if not parts:
                break  # No content parts, exit loop

            part = parts[0]

            # CASE 1: LLM wants to call a function (backend or frontend)
            if part.function_call:
                function_call = part.function_call
                function_name = function_call.name
                arguments = dict(function_call.args)

                # 1. Store function call
                await database.execute(
                    chat_history_table.insert().values(
                        user_id=user_id,
                        message=json.dumps({"name": function_name, "args": arguments}),
                        role="model"
                    )
                )

                # backend function call
                if function_name in BACKEND_FUNCTION_REGISTRY:
                    arguments["map_data"] = prompt.map_data

                    # Backend function
                    result = BACKEND_FUNCTION_REGISTRY[function_name](**arguments)

                    # Store function result as function_response
                    await database.execute(
                        chat_history_table.insert().values(
                            user_id=user_id,
                            message=json.dumps({
                                "function_response": {
                                    "name": function_name,
                                    "response": result
                                }
                            }),
                            role="model"
                        )
                    )

                # front end function call
                else:
                    front_end_function_result = {"output": "front end function executed"}
                    # Store simulated function response (for frontend)
                    await database.execute(
                        chat_history_table.insert().values(
                            user_id=user_id,
                            message=json.dumps({
                                "function_response": {
                                    "name": function_name,
                                    "response": {
                                        "output": front_end_function_result
                                    }
                                }
                            }),
                            role="model"
                        )
                    )

                    await limit_chat_history(user_id)
                    # RETURN function call for frontend to execute
                    return FunctionCall(
                        name=function_name,
                        arguments=arguments,
                        message="Function call ready for frontend execution."
                    )

                await limit_chat_history(user_id)
                continue  # Go back to Gemini to "think" — but flag will now block more function calls until text reply

            # CASE 2: LLM responds with final plain chat message (no function call)
            elif part.text:
                # Store message
                await database.execute(
                    chat_history_table.insert().values(
                        user_id=user_id,
                        message=part.text,
                        role="model"
                    )
                )
                await limit_chat_history(user_id)
                logger.info(f"Final chat response to user {user_id}: {part.text}")

                final_text_response = part.text
                break  # Exit loop gracefully

        # After the while loop ends
        if final_text_response:
            return ChatResponse(message=final_text_response)

        # Fallback: No useful content
        await database.execute(
            chat_history_table.insert().values(
                user_id=user_id,
                message="No content returned.",
                role="model"
            )
        )
        await limit_chat_history(user_id)
        return ChatResponse(message="Something went wrong with the LLM, no content returned.")

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
