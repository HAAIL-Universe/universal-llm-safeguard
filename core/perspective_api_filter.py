import requests
from utils.logger import log_entry
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
            config (dict): Trinity-compliant config dict.
        """
        self.config = config
        perspective_cfg = config.get("perspective_api", {})
        logging_cfg = config.get("logging", {})
        self.enabled = perspective_cfg.get("enabled", False)
        self.api_key = perspective_cfg.get("api_key")
        self.thresholds = perspective_cfg.get("thresholds", {})
        self.privacy_mode = perspective_cfg.get("privacy_mode", True)
        self.log_path = logging_cfg.get("log_path", "safeguard_flags.log")

    def check(self, text: str, source: str = "input") -> Tuple[bool, List[str], List[str]]:
        """
        Check the given text using Perspective API. 
        Returns Trinity contract: (allowed, flags, reasons).
        """
        if not self.enabled or not self.api_key:
            return True, [], []

        endpoint = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
        headers = {"Content-Type": "application/json"}
        requested_attrs = {k: {} for k in self.thresholds.keys()}
        # --- Privacy mode: redact or send full text
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
                threshold = self.thresholds.get(attr, 1.0)  # Default: not blocking if not configured
                if score >= threshold:
                    flags.append(attr)
                    reasons.append(f"{attr} score {score:.2f} exceeds threshold {threshold:.2f}")

            # --- Log any flags/blocks for audit trail
            if flags:
                log_entry(
                    text=text,
                    status="blocked",
                    flags=flags,
                    reasons=reasons,
                    override_used=False,
                    override_role=None,
                    source=source
                )

            return not bool(flags), flags, reasons

        except requests.exceptions.RequestException as e:
            # --- Defensive: Log all errors for transparency
            error_reason = f"Perspective API request failed: {str(e)}"
            log_entry(
                text=text,
                status="error",  # More explicit than "allowed" for downstream audit
                flags=["API_ERROR"],
                reasons=[error_reason],
                override_used=False,
                override_role=None,
                source=source
            )
            # Senior: Always allow if API is down, but flag the failure for audit
            return True, [], ["Perspective API unavailable — filter bypassed."]

