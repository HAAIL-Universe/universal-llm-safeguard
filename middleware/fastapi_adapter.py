from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from safeguarding.utils.override_checker import check_override
from safeguarding.filters.pipeline import run_full_pipeline
from safeguarding.middleware.base import LLMSafeguardMiddleware
from safeguarding.core.orchestrator import run_all_filters
from typing import Callable
import json

# === Full-featured, override-aware safeguard middleware ===
class SafeguardMiddleware(BaseHTTPMiddleware, LLMSafeguardMiddleware):
    """
    Handles input override logic, then pipeline, for advanced control and full Trinity compliance.
    Use for internal AI/LLM integration, or if you want to audit override attempts.
    """
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            body_bytes = await request.body()
            body_data = json.loads(body_bytes.decode("utf-8"))
            text = body_data.get("text", "")
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid request body"})

        override_used, override_role, cleaned_text = check_override(text)

        # run_full_pipeline returns an object with .is_blocked, .final_reasons, etc.
        result = run_full_pipeline(cleaned_text)
        if result.is_blocked and not override_used:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Input blocked by safeguard",
                    "reasons": result.final_reasons
                }
            )
        # If allowed or override, continue
        response = await call_next(request)
        # (Optional: add response output filtering here)
        return response

# === Minimal universal safeguard middleware ===
class FastAPISafeguardMiddleware(BaseHTTPMiddleware):
    """
    Minimal plug-and-play FastAPI middleware that runs universal safeguard logic via run_all_filters.
    Use if you want quick/portable integration (no advanced override logic).
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            body_bytes = await request.body()
            body_data = json.loads(body_bytes.decode("utf-8"))
            text = body_data.get("text", "")
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON in request body"})

        result = run_all_filters(text, config=self.config)
        allowed = result.get("status") == "allowed"
        flags = result.get("flags", [])
        reasons = result.get("reasons", [])

        if not allowed:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Input blocked by safeguard filters",
                    "flags": flags,
                    "reasons": reasons
                }
            )
        return await call_next(request)

# === FastAPI app (choose ONE middleware for your use case) ===
app = FastAPI()

# Use EITHER SafeguardMiddleware (full feature) OR FastAPISafeguardMiddleware (minimal).
# Comment out one or the other as needed.
app.add_middleware(FastAPISafeguardMiddleware)  # Use for most real-world use, plug-and-play
# app.add_middleware(SafeguardMiddleware)       # Uncomment for override/advanced logic

@app.get("/")
async def health():
    """
    Basic healthcheck endpoint.
    """
    return {"status": "ok"}

@app.post("/")
async def receive_text(data: dict):
    return {"message": "Received", "text": data.get("text")}
