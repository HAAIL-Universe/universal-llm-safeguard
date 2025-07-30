import os
from typing import Optional, Tuple
from safeguarding.utils.logger import log_entry  # Import the logger

def load_override_phrases(config: dict) -> dict:
    """
    Load parent/moderator/admin override phrases from passed-in Trinity config.
    """
    return config.get("override", {})

def check_override(
    text: str,
    config: Optional[dict] = None,
    override_data: Optional[dict] = None,
    log_path: Optional[str] = None,
    anonymize: Optional[bool] = None
) -> Tuple[bool, Optional[str], str]:
    """
    Check if the input text contains exactly one override phrase.
    Log every attempt (success, failure, ambiguous) for auditability.

    Args:
        text (str): The user input.
        config (dict, optional): Trinity config dict (required unless override_data provided).
        override_data (dict, optional): Override data, injected for testing.
        log_path (str, optional): Log file to write to (tests, prod, etc).
        anonymize (bool, optional): Redact text in log if True.

    Returns:
        tuple: (override_used [bool], role [str|None], cleaned_text [str])
    """
    # Allow for testability by injecting override_data, but otherwise require config
    if override_data is None:
        if config is None:
            raise ValueError("Must pass either config or override_data to check_override.")
        override_data = load_override_phrases(config)

    matches = []
    matched_phrase = None
    role = None

    for key in ["parent_phrases", "moderator_phrases"]:
        phrases = override_data.get(key, [])
        for phrase in phrases:
            if phrase in text:
                role = key.replace("_phrases", "")  # "parent" or "moderator"
                matches.append((role, phrase))

    # --- If exactly one override found, allow and log success
    if len(matches) == 1:
        role, matched_phrase = matches[0]
        cleaned_text = text.replace(matched_phrase, "").replace("  ", " ").strip()
        log_entry(
            text=text,
            status="override_success",
            flags=[],
            reasons=[f"phrase:{matched_phrase}"],
            override_used=True,
            override_role=role,
            source="input",
            log_path=log_path,
            anonymize=anonymize
        )
        return True, role, cleaned_text

    # --- Fail-safe, always log ambiguous or failed attempts
    log_entry(
        text=text,
        status="override_failed",
        flags=[],
        reasons=["no_match" if len(matches) == 0 else "ambiguous_match"],
        override_used=False,
        override_role=None,
        source="input",
        log_path=log_path,
        anonymize=anonymize
    )
    return False, None, text

# --- NOTES FOR AUDITORS/DEVS:
# - All override attempts are logged—no admin/moderator bypass goes unlogged.
# - Logging is always JSONL for audit and automated tools.
# - Tests can control log_path/anonymize for clean test/prod separation.
# - Fail-safe: ambiguous/multiple matches never allow override and are logged as failures.
