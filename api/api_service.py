from fastapi import FastAPI, Request
from pydantic import BaseModel
from filters.pipeline import run_full_pipeline

app = FastAPI()

class SafeguardRequest(BaseModel):
    text: str

@app.post("/filter")
async def filter_text(req: SafeguardRequest):
    result = run_full_pipeline(req.text)
    return result.dict()
