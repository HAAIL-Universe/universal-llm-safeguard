import os
from typing import Optional, Tuple
from config_loader import load_config

def load_override_phrases() -> dict:
    """
    Load parent/moderator/admin override phrases from Trinity config.
    Uses canonical loader for flexibility and testability.
    """
    config = load_config()
    return config.get("override", {})

def check_override(text: str, override_data: Optional[dict] = None) -> Tuple[bool, Optional[str], str]:
    """
    Check if the input text contains exactly one override phrase.
    If multiple phrases are found, fail safe and deny override.

    Args:
        text (str): The user input.
        override_data (dict, optional): Injected override data (for test or batch).
    
    Returns:
        tuple: (override_used [bool], role [str|None], cleaned_text [str])
    """
    # --- Allow for testability by injecting override_data
    if override_data is None:
        override_data = load_override_phrases()

    matches = []

    for key in ["parent_phrases", "moderator_phrases"]:
        phrases = override_data.get(key, [])
        for phrase in phrases:
            if phrase in text:
                role = key.replace("_phrases", "")  # "parent" or "moderator"
                matches.append((role, phrase))

    if len(matches) == 1:
        role, matched_phrase = matches[0]
        cleaned_text = text.replace(matched_phrase, "").replace("  ", " ").strip()
        return True, role, cleaned_text

    # --- Fail-safe, never allow override if ambiguous or missing
    return False, None, text

# --- NOTES:
# - All config is now loaded via the canonical loader (supports env override, testing, and Trinity modularity).
# - Never hardcode config paths, filenames, or structure.
# - check_override supports injection for batch/tests; always fail-safe for ambiguous/multiple matches.
