from core.keyword_filter import KeywordRegexFilter
from core.classifier_filter import ClassifierFilter

def run_all_filters(text, source="input"):
    keyword = KeywordRegexFilter()
    classifier = ClassifierFilter()

    allowed_kw, flags_kw, reasons_kw = keyword.check(text, source)
    if not allowed_kw:
        return False, flags_kw, reasons_kw

    allowed_clf, flags_clf, reasons_clf = classifier.check(text, source)
    return allowed_clf, flags_kw + flags_clf, reasons_kw + reasons_clf
