from core.keyword_filter import KeywordRegexFilter
from core.classifier_filter import ClassifierFilter
from utils.override_checker import check_override

def run_all_filters(text, source="input"):
    override_used, override_role, cleaned_text = check_override(text)

    keyword = KeywordRegexFilter()
    classifier = ClassifierFilter()

    # Still run filters for logging, even if override is used
    allowed_kw, flags_kw, reasons_kw = keyword.check(cleaned_text, source)
    allowed_clf, flags_clf, reasons_clf = classifier.check(cleaned_text, source)

    all_flags = flags_kw + flags_clf
    all_reasons = reasons_kw + reasons_clf

    if override_used:
        # Optional: call your logger here
        # logger.log_entry(text, status="allowed", flags=all_flags, reasons=all_reasons, override_used=True, override_role=override_role)
        return True, all_flags, all_reasons  # force allow

    # If no override, return normal filter result
    final_allowed = allowed_kw and allowed_clf
    return final_allowed, all_flags, all_reasons
