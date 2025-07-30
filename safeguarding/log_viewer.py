import argparse
import json
import os
from datetime import datetime
from typing import List, Optional

LOG_PATH = "safeguard_flags.log"

def parse_log_line(line: str) -> Optional[dict]:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None

def load_logs(path: str = LOG_PATH) -> List[dict]:
    if not os.path.exists(path):
        print(f"No log file found at {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [log for line in f if (log := parse_log_line(line))]

def filter_logs(
    logs: List[dict], 
    keyword: Optional[str] = None, 
    reason: Optional[str] = None, 
    after: Optional[str] = None, 
    before: Optional[str] = None
):
    # Normalize any CLI-passed 'None' strings
    keyword = None if keyword in ("None", "none", "") else keyword
    reason  = None if reason  in ("None", "none", "") else reason
    after   = None if after   in ("None", "none", "") else after
    before  = None if before  in ("None", "none", "") else before

    filtered = []
    for log in logs:
        # 🔍 Keyword filter (search across full log JSON)
        if keyword and keyword.lower() not in json.dumps(log).lower():
            continue

        # 🏷 Reason filter (match against flags list)
        if reason and reason.lower() not in [r.lower() for r in log.get("flags", [])]:
            continue

        # ⏰ Time filters — ISO parsing
        timestamp = log.get("timestamp", "")
        try:
            log_time = datetime.fromisoformat(timestamp)
        except Exception:
            continue  # Skip invalid timestamps

        if after:
            try:
                if log_time < datetime.fromisoformat(after):
                    continue
            except Exception:
                continue

        if before:
            try:
                if log_time > datetime.fromisoformat(before):
                    continue
            except Exception:
                continue

        filtered.append(log)

    return filtered

def display_logs(logs: List[dict]):
    for i, log in enumerate(logs, 1):
        print(f"\n--- Log Entry {i} ---")
        print(f"Timestamp: {log.get('timestamp')}")
        print(f"Source:    {log.get('source', 'N/A')}")
        print(f"Flags:     {', '.join(log.get('flags', []))}")
        print(f"Reasons:   {', '.join(log.get('reasons', []))}")
        print(f"Text:      {log.get('text', '').strip()[:300]}")

def main():
    parser = argparse.ArgumentParser(description="Universal LLM Safeguard Log Viewer")
    parser.add_argument("--reason", help="Filter by reason/flag type (e.g., keyword, regex, classifier)")
    parser.add_argument("--keyword", help="Search by keyword in log text")
    parser.add_argument("--after", help="Filter logs after this ISO timestamp (e.g., 2025-07-21T00:00:00)")
    parser.add_argument("--before", help="Filter logs before this ISO timestamp")
    parser.add_argument("--limit", type=int, default=25, help="Limit number of results (default: 25)")

    args = parser.parse_args()
    logs = load_logs()
    filtered_logs = filter_logs(
        logs,
        keyword=args.keyword,
        reason=args.reason,
        after=args.after,
        before=args.before
    )
    display_logs(filtered_logs[:args.limit])
    print(f"\nDisplayed {min(len(filtered_logs), args.limit)} of {len(filtered_logs)} total matching entries.")

if __name__ == "__main__":
    main()
