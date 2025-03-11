from pydantic import BaseModel


class ChatResponse(BaseModel):
    message: str

class Prompt(BaseModel):
    message: str