import requests
from utils.logger import log_flag
from datetime import datetime
import time


class PerspectiveAPIFilter:
    def __init__(self, config: dict):
        self.config = config
        perspective_cfg = config.get("perspective_api", {})
        self.enabled = perspective_cfg.get("enabled", False)
        self.api_key = perspective_cfg.get("api_key")
        self.thresholds = perspective_cfg.get("thresholds", {})
        self.privacy_mode = perspective_cfg.get("privacy_mode", True)
        self.log_path = config.get("logging", {}).get("log_path", "safeguard_flags.log")

    def check(self, text: str, source="input"):
        if not self.enabled or not self.api_key:
            return True, [], []

        endpoint = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
        headers = {"Content-Type": "application/json"}
        requested_attrs = {k: {} for k in self.thresholds.keys()}
        payload = {
            "comment": {"text": "[REDACTED]" if self.privacy_mode else text},
            "languages": ["en"],
            "requestedAttributes": requested_attrs
        }

        try:
            response = requests.post(
                url=f"{endpoint}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            result = response.json()

            flags = []
            reasons = []
            for attr, details in result.get("attributeScores", {}).items():
                score = details["summaryScore"]["value"]
                threshold = self.thresholds.get(attr, 1.0)
                if score >= threshold:
                    flags.append(attr)
                    reasons.append(f"{attr} score {score:.2f} exceeds threshold of {threshold:.2f}")

            if flags:
                log_flag(self.log_path, {
                    "timestamp": datetime.now().isoformat(),
                    "filter": "PerspectiveAPI",
                    "flags": flags,
                    "reasons": reasons,
                    "text": text,
                    "source": source,
                }, anonymize=self.privacy_mode)

            return not flags, flags, reasons

        except requests.exceptions.RequestException as e:
            error_reason = f"Perspective API request failed: {str(e)}"
            log_flag(self.log_path, {
                "timestamp": datetime.now().isoformat(),
                "filter": "PerspectiveAPI",
                "flags": ["API_ERROR"],
                "reasons": [error_reason],
                "text": text,
                "source": source,
            }, anonymize=self.privacy_mode)
            return True, [], ["Perspective API unavailable — bypassed filter."]
