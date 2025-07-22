import re
import json
from pydantic import BaseModel
from typing import List
from utils.logger import log_flag


class RuleResult(BaseModel):
    blocked: bool
    reasons: List[str]


def load_config(config_path="config/safeguard_config.json"):
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


class KeywordRegexFilter:
    def __init__(self, config_path="config/safeguard_config.json"):
        self.config = load_config(config_path)
        self.banned_keywords = set(self.config["rules"].get("banned_keywords", []))
        self.banned_regex = [re.compile(rx, re.IGNORECASE) for rx in self.config["rules"].get("banned_regex", [])]
        self.log_path = self.config["logging"].get("log_path", "safeguard_flags.log")
        self.anonymize = self.config["logging"].get("anonymize", True)

    def check(self, text, source="input") -> RuleResult:
        """
        Checks the text for banned keywords and regex.
        Returns a RuleResult.
        Logs any block/flag.
        """
        flags = []
        reasons = []
        lower_text = text.lower()

        for keyword in self.banned_keywords:
            if keyword in lower_text:
                flags.append("keyword")
                reasons.append(f"Banned keyword: {keyword}")

        for rx in self.banned_regex:
            if rx.search(text):
                flags.append("regex")
                reasons.append(f"Banned pattern: {rx.pattern}")

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

        return RuleResult(blocked=blocked, reasons=reasons)


def rule_filter(text: str, source: str = "input") -> RuleResult:
    return KeywordRegexFilter().check(text, source)
