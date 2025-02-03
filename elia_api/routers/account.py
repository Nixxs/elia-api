from fastapi import APIRouter, HTTPException

from elia_api.database import accounts_table, database
from elia_api.models.account import (
    CreateAccount, 
    CreateAccountIn
)

router = APIRouter()

async def find_account(account_id: int):
    query = accounts_table.select().where(accounts_table.c.id == account_id)

    return await database.fetch_one(query)

@router.post("/create-account", response_model=CreateAccount, status_code=201)
async def create_account(account: CreateAccountIn):
    data = account.model_dump()
    query = accounts_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

@router.get("/get-account/{account_id}", response_model=CreateAccount)
async def get_account(account_id: int):
    account = await find_account(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account