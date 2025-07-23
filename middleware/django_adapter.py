from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from core.orchestrator import run_all_filters

class SafeguardMiddleware(MiddlewareMixin):
    """
    Django middleware that intercepts POST requests containing 'text' in the JSON body,
    runs them through the safeguard pipeline, and attaches the result to request.safeguard_result.

    Only active for content-type: application/json.
    """
    def process_request(self, request):
        if request.method != "POST" or request.content_type != "application/json":
            return None

        try:
            import json
            payload = json.loads(request.body.decode("utf-8"))
            text = payload.get("text", "")
            if not text:
                return None

            result = run_all_filters(text)
            allowed = result.get("status") == "allowed"
            flags = result.get("flags", [])
            reasons = result.get("reasons", [])

            result = {
                "status": "allowed" if allowed else "blocked",
                "flags": flags,
                "reasons": reasons
            }

            request.safeguard_result = result

            if not allowed:
                return JsonResponse(result, status=403)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        return None
