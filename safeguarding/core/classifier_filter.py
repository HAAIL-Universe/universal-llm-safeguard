import json
from typing import List
from transformers.pipelines import pipeline

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
    def __init__(self, config):
        """
        Args:
            config (dict, optional): Config dictionary. If None, falls back to loading from config_path.
            config_path (str, optional): Path to config JSON if config is None.
        """
        self.config = config
        
        classifier_cfg = self.config.get("classifier", {})
        logging_cfg = self.config.get("logging", {})

        self.enabled = classifier_cfg.get("enabled", False)
        self.model_name = classifier_cfg.get("model", "unitary/toxic-bert")
        self.thresholds = classifier_cfg.get("thresholds", {})
        self.log_path = logging_cfg.get("log_path", "safeguard_flags.log")
        self.anonymize = logging_cfg.get("anonymize", True)
        self.classifier = None

        if self.enabled:
            try:
                self.classifier = pipeline("text-classification", model=self.model_name)
            except Exception as e:
                raise RuntimeError(f"Failed to load classifier pipeline '{self.model_name}': {e}")

    def check(self, text: str, source: str = "input"):
        """
        Run text classification and compare scores to configured warn/block thresholds.
        Args:
            text (str): Text to classify.
            source (str): Source label for audit/logging ("input" or "output").
        Returns:
            dict: {
                allowed (bool): False if any block tier triggered.
                flags (list): List of dicts with flag info: {"name": str, "score": float, "tier": "warn"|"block"}
                reasons (list): Human-readable reasons for block/flag.
            }
        """
        if not self.enabled or not self.classifier:
            return {"allowed": True, "flags": [], "reasons": []}

        try:
            result = self.classifier(text)
        except Exception as e:
            raise RuntimeError(f"Classifier inference failed: {e}")

        flags = []
        reasons = []
        blocked = False

        for r in result:
            label = r['label'].lower().replace(" ", "_")
            score = r['score']

            # Get tiered thresholds from config
            thresh_config = self.thresholds.get(label, {})
            warn_thresh = thresh_config.get("warn", 0.5)  # default warn threshold
            block_thresh = thresh_config.get("block", 0.7)  # default block threshold

            tier = None
            if score >= block_thresh:
                tier = "block"
                blocked = True
            elif score >= warn_thresh:
                tier = "warn"

            if tier:
                flags.append({
                    "name": f"classifier_{label}",
                    "score": score,
                    "tier": tier
                })
                reasons.append(f"Classifier ({label}): {score:.2f} ≥ {warn_thresh if tier=='warn' else block_thresh:.2f} ({tier})")

        allowed = not blocked
        return allowed, flags, reasons

# --- Classic API for legacy/tests only; not for orchestrator
def classifier_filter(text: str, source: str = "input", config: dict = None) -> ClassifierResult:
    """
    Returns a ClassifierResult object, for compatibility/testing only.
    Config must be passed explicitly—no fallback.
    """
    if config is None:
        raise ValueError("Config must be provided to classifier_filter (no default allowed).")
    allowed, _, reasons = ClassifierFilter(config).check(text, source)
    return ClassifierResult(score=1.0 if allowed else 0.0, blocked=not allowed, reasons=reasons)

