# safeguarding/hooks/pre_process_hook.py

def pre_process(input_text: str, context: dict = None):
    """
    Pre-process the input before it hits the main Safeguard filters.
    - input_text: The raw incoming text.
    - context: Optional dict with metadata (user id, IP, etc).
    Returns: (processed_text, processed_context)
    """
    # Example: Normalize whitespace, lowercase text, strip leading/trailing spaces
    processed_text = input_text.strip()
    # You can add any enrichment or custom pre-checks here.
    # For now, just return untouched.
    return processed_text, context or {}