import json
import os
from datetime import datetime, timezone
from typing import List, Optional
from config_loader import load_config

# --- Load config once at module load (used for legacy/global logging, not for filters)
CONFIG = load_config()
LOG_PATH = CONFIG.get("logging", {}).get("log_path", "logs/safeguard_flags.log")
ANONYMIZE = CONFIG.get("logging", {}).get("anonymize", True)

def log_entry(
    text: str,
    status: str,
    flags: List[str],
    reasons: List[str],
    override_used: bool = False,
    override_role: Optional[str] = None,
    source: str = "input"
):
    """
    Write a structured JSONL log entry for each filter decision or override.
    Uses global LOG_PATH and ANONYMIZE from Trinity config.
    NOTE: For per-filter logging, use log_flag() instead.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "status": status,
        "flags": flags,
        "reasons": reasons,
        "override_used": override_used,
        "override_role": override_role or "none",
        "text": text if not ANONYMIZE else "[REDACTED]"
    }

    # --- Always ensure log directory exists
    os.makedirs(os.path.dirname(LOG_PATH) or ".", exist_ok=True)

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def log_flag(
    log_path: str,
    data: dict,
    anonymize: bool = True
):
    """
    Log a flag event in structured format (called by filters).
    Args:
        log_path (str): Log file path (from config; per-filter).
        data (dict): Should include text, source, flags, reasons.
        anonymize (bool): Redact text if True.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": data.get("source", "input"),
        "status": "blocked",
        "flags": data.get("flags", []),
        "reasons": data.get("reasons", []),
        "override_used": False,
        "override_role": "none",
        "text": data.get("text") if not anonymize else "[REDACTED]"
    }

    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# --- NOTES:
# - All config fields (log_path, anonymize) are now sourced only via Trinity config.
# - Never hardcode log paths or config fields—keep everything configurable for pip/dev/test/deploy.
# - log_flag() should be used by filters that may have their own log_path (e.g., in tests or modular pipelines).
# - log_entry() is for global/legacy use, using default config settings.
