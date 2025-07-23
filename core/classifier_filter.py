import json
from typing import List
from transformers.pipelines import pipeline
from utils.logger import log_flag
from utils.config_loader import load_config

# --- ClassifierResult is kept only for legacy/tests, not used in orchestrator
class ClassifierResult:
    """
    Legacy/test-only compatibility object. Not used by orchestrator.
    """
    def __init__(self, score: float, blocked: bool, reasons: List[str]):
        self.score = score
        self.blocked = blocked
        self.reasons = reasons

class ClassifierFilter:
    """
    HuggingFace text classifier filter for Trinity orchestrator.
    Flags or blocks messages above a configured toxicity/abuse/etc. threshold.
    Returns (allowed, flags, reasons), always three values (Trinity contract).
    """
    def __init__(self, config_path=None):
        """
        Args:
            config_path (str, optional): Override config path. If None, uses Trinity loader's resolution.
        """
        # --- Senior: Always load config using the canonical loader
        self.config = load_config(config_path)
        classifier_cfg = self.config.get("classifier", {})
        logging_cfg = self.config.get("logging", {})
        self.enabled = classifier_cfg.get("enabled", False)
        self.model_name = classifier_cfg.get("model", "unitary/toxic-bert")
        self.thresholds = classifier_cfg.get("thresholds", {})
        self.log_path = logging_cfg.get("log_path", "safeguard_flags.log")
        self.anonymize = logging_cfg.get("anonymize", True)
        self.classifier = None

        # --- Senior: Only instantiate pipeline if classifier is enabled
        if self.enabled:
            try:
                self.classifier = pipeline("text-classification", model=self.model_name)
            except Exception as e:
                # Defensive: fail loudly, do not silently disable
                raise RuntimeError(f"Failed to load classifier pipeline '{self.model_name}': {e}")

    def check(self, text: str, source: str = "input"):
        """
        Run text classification and compare scores to configured thresholds.
        Args:
            text (str): Text to classify.
            source (str): Source label for audit/logging ("input" or "output").
        Returns:
            allowed (bool): True if all scores below thresholds.
            flags (list): List of triggered classifier flags.
            reasons (list): Human-readable reasons for block/flag.
        """
        # --- Senior: If classifier is disabled, always allow (transparent for audit/tests)
        if not self.enabled or not self.classifier:
            return True, [], []

        try:
            result = self.classifier(text)
        except Exception as e:
            # Defensive: raise for orchestrator, do not silently allow
            raise RuntimeError(f"Classifier inference failed: {e}")

        flags = []
        reasons = []
        max_score = 0.0

        # --- Evaluate every label returned by the classifier pipeline
        for r in result:
            label = r['label'].lower().replace(" ", "_")
            score = r['score']
            max_score = max(max_score, score)
            threshold = self.thresholds.get(label, 1.1)  # Default: non-blocking if no threshold configured
            if score >= threshold:
                flags.append(f"classifier_{label}")
                reasons.append(f"Classifier ({label}): {score:.2f} ≥ {threshold:.2f}")

        blocked = bool(flags)

        # --- Log all blocks/flags for transparency and audit
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

        allowed = not blocked
        return allowed, flags, reasons  # --- Always three values, Trinity-compliant

# --- Classic API for legacy/tests only; not for orchestrator
def classifier_filter(text: str, source: str = "input") -> ClassifierResult:
    """
    Returns a ClassifierResult object, for compatibility/testing only.
    """
    allowed, _, reasons = ClassifierFilter().check(text, source)
    return ClassifierResult(score=1.0 if allowed else 0.0, blocked=not allowed, reasons=reasons)
