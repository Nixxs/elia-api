from pydantic import BaseModel
from typing import Any, Dict


class ChatResponse(BaseModel):
    response_type: str = "chat"
    message: str

class Prompt(BaseModel):
    message: str

class FunctionCall(BaseModel):
    response_type: str = "function_call"
    name: str
    arguments: Dict[str, Any]
    message: str