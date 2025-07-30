from fastapi import FastAPI, Request
from middleware.fastapi_adapter import SafeguardMiddleware

app = FastAPI()
app.add_middleware(SafeguardMiddleware)

@app.post("/filter")
async def filtered_chat(request: Request):
    """
    Example endpoint to show usage of the Universal LLM Safeguard in FastAPI.
    Assumes SafeguardMiddleware attaches `request.state.safeguard_result`.
    """
    body = await request.json()
    text = body.get("text", "")

    result = getattr(request.state, "safeguard_result", None)
    if not result:
        return {"error": "Safeguard did not process the request"}

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_example:app", host="0.0.0.0", port=8000, reload=True)
