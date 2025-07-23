import json
import os

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
        dict: Parsed configuration dictionary.
    """

    # --- 1. Use explicit path if provided and exists
    if config_path:
        candidate = os.path.abspath(config_path)

    # --- 2. Try environment variable override
    elif (env_path := os.getenv("SAFEGUARD_CONFIG")):
        candidate = os.path.abspath(env_path)

    # --- 3. Search for canonical config location relative to project/package root
    else:
        here = os.path.abspath(os.path.dirname(__file__))
        # Attempt to find the config directory upwards (robust for pip installs, tests, monorepos)
        for levels_up in range(4):
            root_candidate = os.path.join(here, *[".."] * levels_up, "config", "safeguard_config.json")
            root_candidate = os.path.abspath(root_candidate)
            if os.path.exists(root_candidate):
                candidate = root_candidate
                break
        else:
            # If not found, default to one-level-up (legacy/fallback behavior)
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
            config = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON config ({candidate}): {e}")

    return config
