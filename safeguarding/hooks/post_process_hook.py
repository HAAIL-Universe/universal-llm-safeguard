# safeguarding/hooks/post_process_hook.py

def post_process(result: dict, context: dict = None):
    """
    Post-process the filtering result before returning.
    - result: The dict returned by Safeguard filter (should include 'allowed', 'flags', 'reasons', etc.)
    - context: Optional dict with request/user metadata.
    Returns: (final_result, final_context)
    """
    # Example: Add a timestamp or audit trail if blocked
    import datetime
    final_result = dict(result)  # copy to avoid mutating original

    if not final_result.get("allowed", True):
        final_result["blocked_at"] = datetime.datetime.utcnow().isoformat() + "Z"

    # Optionally, add more info, notify, redact, etc.

    return final_result, context or {}
