from pydantic import BaseModel
from typing import List

class FilterResult(BaseModel):
    original_text: str
    override_used: bool
    override_role: str | None
    cleaned_text: str
    rule_triggered: bool
    rule_reasons: List[str]
    classifier_triggered: bool
    classifier_score: float
    classifier_reasons: List[str]
    is_blocked: bool
    final_reasons: List[str]

    def evaluate(self):
        self.is_blocked = self.rule_triggered or self.classifier_triggered
        reasons = []
        if self.rule_triggered:
            reasons.append("Rule-based filter triggered.")
        if self.classifier_triggered:
            reasons.append("Classifier flagged content.")
        self.final_reasons = reasons
