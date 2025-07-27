from flask import Flask, request, jsonify
from safeguarding.core.orchestrator import run_all_filters

def safeguard_filter(text: str) -> dict:
    """
    Applies the full safeguard pipeline to the input text.

    Args:
        text (str): The user- or AI-generated message.

    Returns:
        dict: A structured response with status, flags, and reasons.
    """
    result = run_all_filters(text)
    return {
        "status": result.get("status", "blocked"),
        "flags": result.get("flags", []),
        "reasons": result.get("reasons", [])
    }

# Optional drop-in example Flask app (for standalone testing)
def create_flask_app() -> Flask:
    app = Flask(__name__)

    @app.route("/filter", methods=["POST"])
    def filter_text():
        """
        Expects JSON: { "text": "..." }
        Returns: { "status": "allowed|blocked", "flags": [...], "reasons": [...] }
        """
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' in request"}), 400
        result = safeguard_filter(data["text"])
        if result["status"] == "blocked":
            return jsonify(result), 403
        return jsonify(result)

    return app

# Optional: add safeguard as a reusable Flask decorator (drop-in)
def safeguard_endpoint(func):
    def wrapper(*args, **kwargs):
        data = request.get_json()
        text = data.get("text", "")
        result = run_all_filters(text)
        allowed = result.get("status", "") == "allowed"
        if not allowed:
            return jsonify({
                "error": "Input blocked by safeguard filters",
                "flags": result.get("flags", []),
                "reasons": result.get("reasons", [])
            }), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
