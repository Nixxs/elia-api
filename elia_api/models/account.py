from pydantic import BaseModel


class CreateAccountIn(BaseModel):
    email: str
    password: str


class CreateAccount(CreateAccountIn):
    id: int
