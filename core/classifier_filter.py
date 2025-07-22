import json
from transformers.pipelines import pipeline
from utils.logger import log_flag

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

        # Only load if enabled to avoid slow import if not used
        if self.enabled:
            self.classifier = pipeline("text-classification", model=self.model_name)

    def check(self, text, source="input"):
        """
        Runs the classifier, checks each label against threshold.
        Returns (allowed: bool, flags: list, reasons: list)
        Logs any block/flag.
        """
        if not self.enabled:
            return True, [], []

        result = self.classifier(text)
        flags = []
        reasons = []

        # Hugging Face classifiers may return multiple results, use all above threshold
        for r in result:
            label = r['label'].lower().replace(" ", "_")
            score = r['score']
            threshold = self.thresholds.get(label, 1.1)  # default: not block
            if score >= threshold:
                flags.append(f"classifier_{label}")
                reasons.append(f"Classifier ({label}): {score:.2f} ≥ {threshold:.2f}")

        allowed = not bool(flags)
        if not allowed:
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
        return allowed, flags, reasons
