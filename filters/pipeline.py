from core.keyword_filter import rule_filter
from core.classifier_filter import classifier_filter
from utils.override_checker import check_override
from core.models import FilterResult




def run_full_pipeline(text: str) -> FilterResult:
    override_used, override_role, cleaned_text = check_override(text)

    result = FilterResult(
        original_text=text,
        override_used=override_used,
        override_role=override_role,
        cleaned_text=cleaned_text,
        rule_triggered=False,
        rule_reasons=[],
        classifier_triggered=False,
        classifier_score=0.0,
        classifier_reasons=[],
        is_blocked=False,
        final_reasons=[]
    )

    rule_result = rule_filter(cleaned_text)
    classifier_result = classifier_filter(cleaned_text)

    result.rule_triggered = rule_result.blocked
    result.rule_reasons = rule_result.reasons
    result.classifier_triggered = classifier_result.blocked
    result.classifier_score = classifier_result.score
    result.classifier_reasons = classifier_result.reasons

    result.evaluate()  # Final block decision

    return result
