from fastapi import FastAPI
import os
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
app = FastAPI()
@app.get("/")
async def read_root():
    return {"Hello": "World", "Google_API_Key": GOOGLE_API_KEY}

#docker compose up --build --force-recreate
