import json
import os
from datetime import datetime, timezone
from typing import List, Optional
from safeguarding.utils.anonymizer import anonymize_text

DEFAULT_LOG_PATH = "logs/safeguard_flags.log"
DEFAULT_ANONYMIZE = True

def log_entry(
    text: str,
    status: str,
    flags: List[str],
    reasons: List[str],
    override_used: bool = False,
    override_role: Optional[str] = None,
    source: str = "input",
    log_path: Optional[str] = None,
    anonymize: Optional[bool] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    action_type: Optional[str] = None,
    error: Optional[str] = None,
    context: Optional[dict] = None,
):
    """
    Log a structured entry (JSONL) for audit and traceability.
    - log_path: File destination for this log (should be passed from config, defaults to safeguard_flags.log).
    - anonymize: Redacts text if True (should be passed from config, defaults to True).
    - All other parameters as before.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "status": status,
        "flags": flags,
        "reasons": reasons,
        "override_used": override_used,
        "override_role": override_role or "none",
        "text": text if not (anonymize if anonymize is not None else DEFAULT_ANONYMIZE) else anonymize_text(text),
        "user_id": user_id or "anonymous",
        "session_id": session_id or "unknown",
        "action_type": action_type or "unspecified",
    }
    if context is not None:
        entry["context"] = context

    actual_log_path = log_path if log_path else DEFAULT_LOG_PATH
    os.makedirs(os.path.dirname(actual_log_path) or ".", exist_ok=True)
    with open(actual_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def log_flag(
    log_path: str,
    data: dict,
    anonymize: bool = True,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    action_type: Optional[str] = None,
):
    """
    Log a 'flag' event in structured format (to be called by filters for modular, testable logging).
    - log_path: File destination for this log (always pass in tests!).
    - data: Must contain at minimum text, source, flags, and reasons.
    - anonymize: Redacts text if True (set False in tests if you want to verify content).
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": data.get("source", "input"),
        "status": "blocked",                                      # Flags are always blocks in this context
        "flags": data.get("flags", []),
        "reasons": data.get("reasons", []),
        "override_used": False,                                   # Use log_entry for override cases
        "override_role": "none",
        "text": data.get("text") if not anonymize else anonymize_text(data.get("text")),
        "user_id": user_id or "anonymous",
        "session_id": session_id or "unknown",
        "action_type": action_type or "unspecified",
    }

    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# --- NOTES FOR AUDITORS/CONTRIBUTORS:
# - All log writes are JSONL (not plain text) for full machine readability, traceability, and GDPR audit.
# - Never hardcode log file locations or anonymization—always pass from config or via argument for true modularity and testability.
# - log_flag() is designed for unit/integration testing and filter modularity. log_entry() covers all general/cross-pipeline events.
# - If you extend for error events, pass status="error", and set reasons=["Classifier unavailable"] or similar.
# - Text is redacted by default unless running in test/dev mode.
