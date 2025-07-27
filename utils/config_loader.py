import json
import os

def deep_merge(dflt: dict, user: dict) -> dict:
    for k, v in user.items():
        if (
            k in dflt
            and isinstance(dflt[k], dict)
            and isinstance(v, dict)
        ):
            dflt[k] = deep_merge(dflt[k], v)
        else:
            dflt[k] = v
    return dflt

def load_config(config_path=None):
    """
    Load the safeguard configuration from JSON.

    Resolution order:
    1. Use explicit config_path argument if provided.
    2. If not, check the SAFEGUARD_CONFIG environment variable (for containerized/prod/test).
    3. Fallback: search upward from this file for 'config/safeguard_config.json', up to four directory levels.

    Raises:
        FileNotFoundError: If the config file is not found.
        RuntimeError: If the config file is present but contains invalid JSON.

    Returns:
        dict: Parsed and merged configuration dictionary.
    """

    # --- Default config (keep updated as your safe baseline)
    default_config = {
        "rules": {
            "banned_keywords": ["sex", "drugs", "violence", "suicide", "kill", "groom", "address", "meet", "alone"],
            "banned_regex": [".*naked.*", ".*let's keep this secret.*"]
        },
        "classifier": {
            "enabled": True,
            "model": "unitary/toxic-bert",
            "thresholds": {
                "toxic": 0.8,
                "severe_toxic": 0.7,
                "insult": 0.75,
                "sexually_explicit": 0.7,
                "threat": 0.7
            }
        },
        "perspective_api": {
            "enabled": True,
            "api_key": None,
            "privacy_mode": True,
            "thresholds": {
                "TOXICITY": 0.8,
                "INSULT": 0.75,
                "THREAT": 0.7
            }
        },
        "logging": {
            "log_path": "safeguard_flags.log",
            "anonymize": True
        },
        "override": {
            "parent_phrases": ["override123"],
            "moderator_phrases": ["modunlock!"]
        }
    }

    # --- 1. Use explicit path if provided and exists
    if config_path:
        candidate = os.path.abspath(config_path)

    # --- 2. Try environment variable override
    elif (env_path := os.getenv("SAFEGUARD_CONFIG")):
        candidate = os.path.abspath(env_path)

    # --- 3. Search for canonical config location relative to project/package root
    else:
        here = os.path.abspath(os.path.dirname(__file__))
        for levels_up in range(4):
            root_candidate = os.path.join(here, *[".."] * levels_up, "config", "safeguard_config.json")
            root_candidate = os.path.abspath(root_candidate)
            if os.path.exists(root_candidate):
                candidate = root_candidate
                break
        else:
            candidate = os.path.abspath(os.path.join(here, "..", "config", "safeguard_config.json"))

    # --- Fail loudly if not found
    if not os.path.exists(candidate):
        raise FileNotFoundError(
            f"Config file not found at: {candidate}\n"
            "Expected at 'config/safeguard_config.json' in the project/package root,\n"
            "or provide a path via load_config(path) or SAFEGUARD_CONFIG environment variable."
        )

    # --- Load and parse JSON, fail loudly if invalid
    with open(candidate, "r", encoding="utf-8") as f:
        try:
            user_config = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON config ({candidate}): {e}")

    # --- Merge user config into default config
    merged_config = deep_merge(default_config, user_config)

    # --- Override sensitive fields from environment variables if set
    env_api_key = os.getenv("PERSPECTIVE_API_KEY")
    if env_api_key:
        if "perspective_api" not in merged_config:
            merged_config["perspective_api"] = {}
        merged_config["perspective_api"]["api_key"] = env_api_key

    return merged_config
