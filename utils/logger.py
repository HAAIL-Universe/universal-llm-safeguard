import json
import os
from datetime import datetime, timezone
from typing import List, Optional

# Local JSON config loader
def load_config():
    with open(os.path.join("config", "safeguard_config.json"), "r", encoding="utf-8") as f:
        return json.load(f)

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
    Expected fields in `data`: text, source, flags, reasons
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
