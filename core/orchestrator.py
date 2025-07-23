from core.keyword_filter import KeywordRegexFilter
from core.classifier_filter import ClassifierFilter
from utils.override_checker import check_override


def run_all_filters(text: str, source: str = "input") -> dict:
    """
    Canonical safeguard pipeline. Applies override logic, runs all filters,
    and returns manifest-compliant structured output.

    Args:
        text (str): Input text from user or LLM
        source (str): Optional source context string (e.g. "input" or "output")

    Returns:
        dict: {
            "status": "allowed" | "blocked",
            "flags": [...],
            "reasons": [...],
            "override": true | false,
            "role": "parent" | "moderator" | None
        }
    """
    override_used, override_role, cleaned_text = check_override(text)

    keyword = KeywordRegexFilter()
    classifier = ClassifierFilter()

    # Always run filters for logging
    allowed_kw, flags_kw, reasons_kw = keyword.check(cleaned_text, source)
    allowed_clf, flags_clf, reasons_clf = classifier.check(cleaned_text, source)

    all_flags = list(set(flags_kw + flags_clf))
    all_reasons = list(set(reasons_kw + reasons_clf))

    if override_used:
        return {
            "status": "allowed",
            "flags": all_flags,
            "reasons": all_reasons,
            "override": True,
            "role": override_role,
        }

    final_allowed = allowed_kw and allowed_clf
    return {
        "status": "allowed" if final_allowed else "blocked",
        "flags": all_flags,
        "reasons": all_reasons,
        "override": False,
        "role": None,
    }
