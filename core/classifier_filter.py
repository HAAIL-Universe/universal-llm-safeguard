import json
from pydantic import BaseModel
from typing import List
from transformers.pipelines import pipeline
from utils.logger import log_flag


class ClassifierResult(BaseModel):
    score: float
    blocked: bool
    reasons: List[str]


def load_config(config_path="config/safeguard_config.json"):
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


class ClassifierFilter:
    def __init__(self, config_path="config/safeguard_config.json"):
        self.config = load_config(config_path)
        self.enabled = self.config.get("classifier", {}).get("enabled", False)
        self.model_name = self.config.get("classifier", {}).get("model", "unitary/toxic-bert")
        self.thresholds = self.config.get("classifier", {}).get("thresholds", {})
        self.log_path = self.config["logging"].get("log_path", "safeguard_flags.log")
        self.anonymize = self.config["logging"].get("anonymize", True)

        self.classifier = None
        if self.enabled:
            self.classifier = pipeline("text-classification", model=self.model_name)

    def check(self, text: str, source: str = "input") -> ClassifierResult:
        if not self.enabled or not self.classifier:
            return ClassifierResult(score=0.0, blocked=False, reasons=[])

        result = self.classifier(text)
        flags = []
        reasons = []
        max_score = 0.0

        for r in result:
            label = r['label'].lower().replace(" ", "_")
            score = r['score']
            max_score = max(max_score, score)
            threshold = self.thresholds.get(label, 1.1)  # Default threshold high to avoid false positives
            if score >= threshold:
                flags.append(f"classifier_{label}")
                reasons.append(f"Classifier ({label}): {score:.2f} ≥ {threshold:.2f}")

        blocked = bool(flags)

        if blocked:
            log_flag(
                self.log_path,
                {
                    "text": text,
                    "source": source,
                    "flags": flags,
                    "reasons": reasons
                },
                anonymize=self.anonymize
            )

        return ClassifierResult(score=max_score, blocked=blocked, reasons=reasons)


def classifier_filter(text: str, source: str = "input") -> ClassifierResult:
    return ClassifierFilter().check(text, source)
