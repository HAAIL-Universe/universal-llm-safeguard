import unittest
from core.keyword_filter import KeywordRegexFilter
from core.classifier_filter import ClassifierFilter
from core.perspective_api_filter import PerspectiveAPIFilter
import os

# --- Always use an override-able path for configs in tests for portability and reproducibility.
TEST_CONFIG_PATH = os.getenv("TEST_SAFEGUARD_CONFIG", "config/safeguard_config.json")

class TestKeywordRegexFilter(unittest.TestCase):
    def setUp(self):
        # --- Avoid hardcoded paths—prefer env or param for testability
        self.filter = KeywordRegexFilter(TEST_CONFIG_PATH)

    def test_blocked_keyword(self):
        # --- Test: should block if text contains a banned keyword
        allowed, flags, reasons = self.filter.check("Let's talk about drugs")
        self.assertFalse(allowed, "Keyword filter failed to block banned keyword.")
        self.assertIn("keyword", flags, "Flag type 'keyword' missing for banned keyword.")

    def test_blocked_regex(self):
        # --- Test: should block if text matches banned regex
        allowed, flags, reasons = self.filter.check("He sent me a naked picture")
        self.assertFalse(allowed, "Keyword filter failed to block banned regex.")
        self.assertIn("regex", flags, "Flag type 'regex' missing for banned regex.")

    def test_allowed(self):
        # --- Test: should pass if text is clean
        allowed, flags, reasons = self.filter.check("Let's talk about healthy food")
        self.assertTrue(allowed, "Clean input was incorrectly blocked.")
        self.assertEqual(flags, [], "No flags should be present for clean input.")

class TestClassifierFilter(unittest.TestCase):
    def setUp(self):
        # --- Always use config override, not prod, for repeatable unit tests
        self.filter = ClassifierFilter(TEST_CONFIG_PATH)

    def test_classifier_toxic(self):
        # --- Only run if classifier enabled in test config (skip, don’t fail)
        if not self.filter.enabled:
            self.skipTest("Classifier not enabled in config")
        allowed, flags, reasons = self.filter.check("You are an idiot and should kill yourself")
        self.assertFalse(allowed, "Classifier failed to block toxic language.")
        self.assertTrue(any("classifier" in f for f in flags), "Expected classifier flag missing.")

class TestPerspectiveAPIFilter(unittest.TestCase):
    def setUp(self):
        # --- Use dummy config, never real API keys or endpoints in unit tests.
        self.filter = PerspectiveAPIFilter({
            "perspective_api": {
                "enabled": True,
                "api_key": "DUMMY_KEY",  # Not called in this test
                "privacy_mode": True,
                "thresholds": {
                    "TOXICITY": 0.8
                }
            },
            "logging": {
                "log_path": "test_perspective.log"
            }
        })

    def test_disabled_bypass(self):
        # --- Explicitly disable filter, should always pass input through
        self.filter.enabled = False
        allowed, flags, reasons = self.filter.check("You are trash")
        self.assertTrue(allowed, "Disabled filter should never block input.")
        self.assertEqual(flags, [], "Flags should be empty when filter is disabled.")

if __name__ == "__main__":
    # --- Running as main should trigger all test discovery/exec (trivial but required)
    unittest.main()
