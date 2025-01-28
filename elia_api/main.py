from fastapi import FastAPI
from elia_api.models.account import CreateAccount, CreateAccountIn

app = FastAPI()


account_table = {}


@app.post("/create-account", response_model=CreateAccount)
async def create_account(post: CreateAccountIn):
    data = post.model_dump()

    last_record_id = len(account_table)
    new_post = {**data, "id": last_record_id}

    account_table[last_record_id] = new_post

    return new_post

@app.get("/")
async def root():
    return {"message": "omg its working in azure now"}
