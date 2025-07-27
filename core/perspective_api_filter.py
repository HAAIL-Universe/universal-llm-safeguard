import requests
from safeguarding.utils.logger import log_entry
from typing import Dict, Any, Tuple, List

class PerspectiveAPIFilter:
    """
    Google Perspective API filter.
    This class is designed for explicit dependency injection:
    Always construct with a config dict (not with a path or loader).
    - In production, use:   PerspectiveAPIFilter(load_config())
    - In tests, inject a dummy/minimal config dict directly.
    This pattern ensures full Trinity-compliance, test isolation, and no hidden config state.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config (dict, optional): Trinity-compliant config dict.
            config_path (str, optional): Path to config JSON if config is None.
        """
        self.config = config
        
        perspective_cfg = self.config.get("perspective_api", {})
        logging_cfg = self.config.get("logging", {})

        self.enabled = perspective_cfg.get("enabled", False)
        self.api_key = perspective_cfg.get("api_key", "")
        self.thresholds = perspective_cfg.get("thresholds", {})
        self.privacy_mode = perspective_cfg.get("privacy_mode", True)
        self.log_path = logging_cfg.get("log_path", "safeguard_flags.log")

    def check(self, text: str, source: str = "input") -> dict:
        """
        Check the given text using Perspective API.
        Returns a dict with allowed status, flags, and reasons.
        """
        if not self.enabled or not self.api_key:
            return {"allowed": True, "flags": [], "reasons": []}

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
            blocked = False

            for attr, details in result.get("attributeScores", {}).items():
                score = details["summaryScore"]["value"]
                # Expect threshold config like {"toxicity": {"warn": 0.5, "block": 0.7}, ...}
                thresh_config = self.thresholds.get(attr, {})
                warn_thresh = thresh_config.get("warn", 0.5)
                block_thresh = thresh_config.get("block", 0.7)

                tier = None
                if score >= block_thresh:
                    tier = "block"
                    blocked = True
                elif score >= warn_thresh:
                    tier = "warn"

                if tier:
                    flags.append({
                        "name": attr,
                        "score": score,
                        "tier": tier
                    })
                    reasons.append(f"{attr} score {score:.2f} ≥ {warn_thresh if tier=='warn' else block_thresh:.2f} ({tier})")

            allowed = not blocked
            return {"allowed": allowed, "flags": flags, "reasons": reasons}

        except requests.exceptions.RequestException as e:
            return {"allowed": True, "flags": [], "reasons": ["Perspective API unavailable — filter bypassed."]}

