"""
anonymizer.py

Provides text anonymization utilities for SafeGuard middleware logging.
"""

import re

def anonymize_text(text: str) -> str:
    """
    Anonymize sensitive content in the given text.
    Currently replaces full text with a generic placeholder.
    Extend this function with smarter redaction if needed.

    Args:
        text (str): The original text to anonymize.

    Returns:
        str: Anonymized/redacted text.
    """
    if not text:
        return ""

    # Basic redact: replace entire text
    return "[REDACTED]"

def mask_email_addresses(text: str) -> str:
    """
    Example helper: mask email addresses in text.

    Args:
        text (str): Input text

    Returns:
        str: Text with email addresses masked.
    """
    email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    return re.sub(email_pattern, "[EMAIL]", text)

def mask_phone_numbers(text: str) -> str:
    """
    Example helper: mask phone numbers in text.

    Args:
        text (str): Input text

    Returns:
        str: Text with phone numbers masked.
    """
    phone_pattern = r"\b(\+?\d{1,3}[-.\s]?(\(?\d{1,4}\)?)[-.\s]?\d{1,4}[-.\s]?\d{1,9})\b"
    return re.sub(phone_pattern, "[PHONE]", text)
