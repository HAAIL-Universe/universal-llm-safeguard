import re
from typing import List
from safeguarding.utils.logger import log_flag


# --- RuleResult: for legacy/tests only, not used in Trinity orchestrator
class RuleResult:
    """
    Legacy/test compatibility object, not used in orchestrator.
    """
    def __init__(self, blocked: bool, reasons: List[str]):
        self.blocked = blocked
        self.reasons = reasons

class KeywordRegexFilter:
    """
    Checks text for banned keywords and regex patterns (Trinity-aligned).
    Logs all blocks/flags for auditability and transparency.
    Always returns (allowed, flags, reasons) for orchestrator contract.
    """
    def __init__(self, config):
        """
        Args:
            config (dict): Config dict to use (required).
        """
        self.config = config

        rules_cfg = self.config.get("rules", {})
        logging_cfg = self.config.get("logging", {})

        # Compile set of banned keywords (lowercase for match speed)
        self.banned_keywords = set(kw.lower() for kw in rules_cfg.get("banned_keywords", []))

        # Compile regex patterns for performance
        self.banned_regex = [re.compile(rx, re.IGNORECASE) for rx in rules_cfg.get("banned_regex", [])]

        # Logging settings (Trinity spec)
        self.log_path = logging_cfg.get("log_path", "safeguard_flags.log")
        self.anonymize = logging_cfg.get("anonymize", True)

    def check(self, text: str, source: str = "input"):
        """
        Checks provided text for banned keywords and regex patterns.
        Args:
            text (str): Input text to check.
            source (str): Source label for logging/audit ("input", "output", etc.)
        Returns:
            allowed (bool): True if clean, False if blocked.
            flags (list): ["keyword", "regex", ...] for each type matched.
            reasons (list): Human-readable reasons for block/flag.
        """
        flags = []
        reasons = []
        lower_text = text.lower()

        # --- Check all banned keywords (case-insensitive, fast scan)
        for keyword in self.banned_keywords:
            if keyword in lower_text:
                flags.append("keyword")
                reasons.append(f"Banned keyword: {keyword}")

        # --- Check all banned regex patterns (pre-compiled for perf)
        for rx in self.banned_regex:
            if rx.search(text):
                flags.append("regex")
                reasons.append(f"Banned pattern: {rx.pattern}")

        blocked = bool(flags)

        # --- Log all flags/blocks for audit (never skip logging blocked attempts)
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
        return allowed, flags, reasons

# --- Classic API for legacy/tests only; do NOT use in orchestrator
def rule_filter(text: str, source: str = "input", *, config: dict) -> RuleResult:
    """
    Returns a RuleResult object, for legacy/testing only.
    """
    if config is None:
        raise ValueError("Config must be provided to rule_filter (no default allowed).")
    allowed, _, reasons = KeywordRegexFilter(config).check(text, source)
    return RuleResult(blocked=not allowed, reasons=reasons)

