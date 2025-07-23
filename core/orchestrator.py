from core.keyword_filter import KeywordRegexFilter
from core.classifier_filter import ClassifierFilter
from utils.override_checker import check_override

# --- DEBUG: Confirm this orchestrator.py is being loaded
print(">>> RUNNING orchestrator.py FROM", __file__)  # [DEBUG - file loaded]

def run_all_filters(text: str, source: str = "input") -> dict:
    """
    Canonical safeguard pipeline.
    Applies override logic, runs all filters, and returns manifest-compliant structured output.

    Args:
        text (str): Input text from user or LLM.
        source (str): Optional source context string (e.g. "input" or "output").

    Returns:
        dict: {
            "status": "allowed" | "blocked",
            "flags": [...],
            "reasons": [...],
            "override": True | False,
            "role": "parent" | "moderator" | None
        }
    """
    # --- DEBUG: Show every function call
    print(">>> run_all_filters CALLED FROM", __file__)  # [DEBUG - function called]

    # --- Check for parent/moderator override in the input
    override_used, override_role, cleaned_text = check_override(text)

    # --- Instantiate the core filter modules
    keyword = KeywordRegexFilter()
    classifier = ClassifierFilter()

    # --- Run all core filters on the cleaned input (logging always happens)
    allowed_kw, flags_kw, reasons_kw = keyword.check(cleaned_text, source)
    print("keyword.check returned:", allowed_kw, flags_kw, reasons_kw, type(allowed_kw), type(flags_kw), type(reasons_kw))  # [DEBUG]

    allowed_clf, flags_clf, reasons_clf = classifier.check(cleaned_text, source)
    print("classifier.check returned:", allowed_clf, flags_clf, reasons_clf, type(allowed_clf), type(flags_clf), type(reasons_clf))  # [DEBUG]

    # --- Merge and deduplicate all flags and reasons from every filter
    all_flags = list(set(flags_kw + flags_clf))
    all_reasons = list(set(reasons_kw + reasons_clf))

    # --- If override is present, always allow, but log all flags/reasons for auditing
    if override_used:
        result = {
            "status": "allowed",
            "flags": all_flags,
            "reasons": all_reasons,
            "override": True,
            "role": override_role,
        }
        print(">>> RETURNING from run_all_filters (OVERRIDE):", result, type(result))  # [DEBUG - override return]
        return result

    # --- Block if any filter blocks, allow only if both allow
    final_allowed = allowed_kw and allowed_clf

    result = {
        "status": "allowed" if final_allowed else "blocked",
        "flags": all_flags,
        "reasons": all_reasons,
        "override": False,
        "role": None,
    }
    print(">>> RETURNING from run_all_filters:", result, type(result))  # [DEBUG - normal return]
    return result
