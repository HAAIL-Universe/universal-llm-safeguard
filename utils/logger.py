import json
from datetime import datetime, timezone

def log_flag(log_path, entry, anonymize=True):
    """
    Append a flag/log entry to the log file.
    Adds a timezone-aware UTC ISO8601 timestamp for audit.
    Anonymizes the text field if requested.
    """
    if anonymize and "text" in entry:
        entry["text"] = "[REDACTED]"
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
