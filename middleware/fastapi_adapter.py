from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from utils.override_checker import check_override
from filters.pipeline import run_full_pipeline
from middleware.base import LLMSafeguardMiddleware
from core.orchestrator import run_all_filters
from typing import Callable
import json

class SafeguardMiddleware(BaseHTTPMiddleware, LLMSafeguardMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # --- Step 1: Handle incoming request body ---
        try:
            body_bytes = await request.body()
            body_data = json.loads(body_bytes.decode("utf-8"))
            text = body_data.get("text", "")
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid request body"})

        # --- Step 2: Check for override ---
        override_used, override_role, cleaned_text = check_override(text)

        # --- Step 3: Run input safeguard ---
        result = run_full_pipeline(cleaned_text)
        if result.is_blocked and not override_used:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Input blocked by safeguard",
                    "reasons": result.final_reasons
                }
            )

        # --- Step 4: Continue if safe ---
        response = await call_next(request)

        # --- Optional: Intercept output response body (not required for input-only middleware) ---
        # Uncomment this block if you want to scan output responses too
        #
        # if response.media_type == "application/json":
        #     response_body = [section async for section in response.body_iterator]
        #     decoded = b"".join(response_body).decode("utf-8")
        #     try:
        #         output_data = json.loads(decoded)
        #         output_text = output_data.get("text", "")
        #         output_result = run_full_pipeline(output_text)
        #         if output_result.is_blocked:
        #             return JSONResponse(
        #                 status_code=403,
        #                 content={"error": "Output blocked", "reasons": output_result.final_reasons}
        #             )
        #     except Exception:
        #         pass  # if response is not JSON, let it pass unchanged

        return response
    
class FastAPISafeguardMiddleware(BaseHTTPMiddleware):
    """
    Minimal plug-and-play FastAPI middleware that runs universal safeguard logic via run_all_filters.
    Compatible with any FastAPI app expecting 'text' in the request JSON.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            body_bytes = await request.body()
            body_data = json.loads(body_bytes.decode("utf-8"))
            text = body_data.get("text", "")
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON in request body"})

        result = run_all_filters(text)
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