from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "omg its working in azure now"}
