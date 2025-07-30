from safeguarding.core.keyword_filter import KeywordRegexFilter
from safeguarding.core.classifier_filter import ClassifierFilter
from safeguarding.utils.override_checker import check_override
from safeguarding.utils.logger import log_entry
import traceback

from safeguarding.hooks.pre_process_hook import pre_process
from safeguarding.hooks.post_process_hook import post_process


def run_all_filters(
    text: str,
    source: str = "input",
    user_id: str = "anon",
    session_id: str = "anon_session",
    context: dict = None,
    log_path: str = None,
    anonymize: bool = None,
    config: dict = None
) -> dict:
    """
    Canonical safeguard pipeline for SafeGuard.
    - Applies override logic
    - Runs all filters
    - Merges/dedupes flags/reasons
    - Logs every run with full audit context (user/session/source)
    - Handles/logs error cases for full traceability

    Args:
        text (str): Input text from user or LLM.
        source (str): Context string (e.g., "input" or "output").
        user_id (str): User identifier or "anon".
        session_id (str): Session identifier or "anon_session".
        context (dict): Optional additional context for logs.
        log_path (str): Optional log file path (for test/prod separation).
        anonymize (bool): Redact text in logs if True (GDPR/test).

    Returns:
        dict: {
            "status": "allowed" | "blocked",
            "flags": [...],
            "reasons": [...],
            "override": True | False,
            "role": "parent" | "moderator" | None
        }
    """
    context = context or {}
        # --- Step 0: Pre-process hook (input sanitization/enrichment)
    text, context = pre_process(text, context)

    try:
        # --- Step 1: Check for parent/moderator override
        override_used, override_role, cleaned_text = check_override(
            text,
            log_path=log_path,
            anonymize=anonymize
        )

        # --- Step 2: Instantiate and run all core filters on cleaned input
        keyword = KeywordRegexFilter(config)
        classifier = ClassifierFilter(config)

        allowed_kw, flags_kw, reasons_kw = keyword.check(cleaned_text, source)
        allowed_clf, flags_clf, reasons_clf = classifier.check(cleaned_text, source)

        # --- Step 3: Merge and deduplicate all flags/reasons from every filter
        all_flags = list(set(flags_kw + flags_clf))
        all_reasons = list(set(reasons_kw + reasons_clf))

        # --- Step 4: Log the outcome of this filter run (audit traceable)
        log_entry(
            text=text,
            status="allowed" if (override_used or (allowed_kw and allowed_clf)) else "blocked",
            flags=all_flags,
            reasons=all_reasons,
            override_used=override_used,
            override_role=override_role if override_used else None,
            source=source,
            log_path=log_path,
            anonymize=anonymize,
            user_id=user_id,
            session_id=session_id,
            action_type="override" if override_used else ("allow" if (allowed_kw and allowed_clf) else "block"),
            error=None,
            context={
                **context,
                "filters": ["keyword", "classifier"],
                "endpoint": "run_all_filters"
            }
        )

        # --- Step 5: Return canonical result
        if override_used:
            result = {
                "status": "allowed",
                "flags": all_flags,
                "reasons": all_reasons,
                "override": True,
                "role": override_role,
            }
            result, context = post_process(result, context)
            return result

        final_allowed = allowed_kw and allowed_clf
        result = {
            "status": "allowed" if final_allowed else "blocked",
            "flags": all_flags,
            "reasons": all_reasons,
            "override": False,
            "role": None,
        }
        result, context = post_process(result, context)
        return result

    except Exception as e:
        # --- Step 6: Always log unexpected errors for forensics and traceability
        log_entry(
            text=text,
            status="error",
            flags=[],
            reasons=["filter_exception"],
            override_used=False,
            override_role=None,
            source=source,
            log_path=log_path,
            anonymize=anonymize,
            user_id=user_id,
            session_id=session_id,
            action_type="error",
            error=str(e),
            context={
                **context,
                "traceback": traceback.format_exc(),
                "endpoint": "run_all_filters"
            }
        )
        # Raise for upstream handling or crash reporting
        raise

# --- NOTES FOR AUDIT/MAINTAINERS:
# - All filter pipeline results, override attempts, and errors are logged in JSONL via log_entry.
# - Every log entry includes user/session/context for full auditability.
# - All errors, not just happy path, are persisted to the log for forensic review.
# - To extend: Add additional filters, context fields, or adapt for web adapter injection.
