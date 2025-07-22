import json
import os
from typing import Optional, Tuple

# Path to config file (assumes relative to root execution context)
CONFIG_PATH = os.path.join("config", "safeguard_config.json")

def load_override_phrases() -> dict:
    """Load parent/moderator/admin override phrases from config."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get("override", {})

def check_override(text: str, override_data: Optional[dict] = None) -> Tuple[bool, Optional[str], str]:
    """
    Check if the input text contains exactly one override phrase.
    If multiple phrases are found, fail safe and deny override.

    Returns:
        (override_used, role, cleaned_text)
    """
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

    # Fail-safe: none or multiple matches
    return False, None, text
