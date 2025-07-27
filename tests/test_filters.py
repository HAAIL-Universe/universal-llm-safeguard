import unittest
from core.keyword_filter import KeywordRegexFilter
from core.classifier_filter import ClassifierFilter
from core.perspective_api_filter import PerspectiveAPIFilter
import os
import json

# --- Always use an override-able path for configs in tests for portability and reproducibility.
TEST_CONFIG_PATH = os.getenv("TEST_SAFEGUARD_CONFIG", "config/safeguard_config.json")

class TestKeywordRegexFilter(unittest.TestCase):
    def setUp(self):
        self.log_path = "logs/test_flags.log"
        self.filter = KeywordRegexFilter(TEST_CONFIG_PATH)
        # (Optional) Ensure log file is clean before each test
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_blocked_keyword(self):
        allowed, flags, reasons = self.filter.check("Let's talk about drugs")
        self.assertFalse(allowed, "Keyword filter failed to block banned keyword.")
        self.assertIn("keyword", flags, "Flag type 'keyword' missing for banned keyword.")

    def test_blocked_regex(self):
        allowed, flags, reasons = self.filter.check("He sent me a naked picture")
        self.assertFalse(allowed, "Keyword filter failed to block banned regex.")
        self.assertIn("regex", flags, "Flag type 'regex' missing for banned regex.")

    def test_multi_banned_words(self):
        allowed, flags, reasons = self.filter.check("He mentioned drugs and violence.")
        self.assertFalse(allowed, "Multi-banned words input not blocked.")
        self.assertTrue("keyword" in flags, "Missing keyword flag for multi-trigger.")

    def test_false_positive_substring(self):
        allowed, flags, reasons = self.filter.check("Our addressable market is huge.")
        self.assertTrue(allowed, "False positive: innocent substring incorrectly blocked.")
        self.assertEqual(flags, [], "False positive: flags present for innocent substring.")

    def test_misspelled_banned_word(self):
        allowed, flags, reasons = self.filter.check("He mentioned dr.ugs")
        self.assertTrue(allowed, "Minor misspelling caused false block (review regex aggressiveness).")

    def test_allowed(self):
        allowed, flags, reasons = self.filter.check("Let's talk about healthy food")
        self.assertTrue(allowed, "Clean input was incorrectly blocked.")
        self.assertEqual(flags, [], "No flags should be present for clean input.")

    def test_blocked_logs_written(self):
        self.filter.check("Let's talk about drugs")
        found_keyword = False
        found_flag = False
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                    except Exception:
                        continue
                    if "drugs" in entry.get("input", ""):
                        found_keyword = True
                    if "keyword" in entry.get("flags", []):
                        found_flag = True
        self.assertTrue(found_keyword, "Blocked keyword not found in logs.")
        self.assertTrue(found_flag, "Flag type not logged for blocked keyword.")

    def test_unicode_keyword(self):
        allowed, flags, reasons = self.filter.check("Let’s talk about drügs 💊")
        self.assertFalse(allowed, "Unicode variant of banned keyword not blocked.")
        self.assertIn("keyword", flags + reasons, "Unicode keyword flag/reason missing.")

    def test_only_emoji(self):
        allowed, flags, reasons = self.filter.check("😀😃😄")
        self.assertTrue(allowed, "Emoji-only input should not be blocked.")
        self.assertEqual(flags, [], "Flags should be empty for unrelated emoji.")

    def test_empty_and_long_input(self):
        allowed, flags, reasons = self.filter.check("")
        self.assertTrue(allowed, "Empty input should not be blocked.")
        self.assertEqual(flags, [], "No flags for empty input.")

        long_str = "hello " * 5000
        allowed, flags, reasons = self.filter.check(long_str)
        self.assertTrue(allowed, "Long but innocent input should not be blocked.")

class TestClassifierFilter(unittest.TestCase):
    def setUp(self):
        self.log_path = "logs/test_flags.log"
        self.filter = ClassifierFilter(TEST_CONFIG_PATH)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_classifier_toxic(self):
        if not self.filter.enabled:
            self.skipTest("Classifier not enabled in config")
        allowed, flags, reasons = self.filter.check("You are an idiot and should kill yourself")
        self.assertFalse(allowed, "Classifier failed to block toxic language.")
        self.assertTrue(any("classifier" in f for f in flags), "Expected classifier flag missing.")

    def test_classifier_failure(self):
        original_enabled = self.filter.enabled
        self.filter.enabled = False
        allowed, flags, reasons = self.filter.check("This is a test of failure mode.")
        self.assertTrue(allowed, "Classifier failure should not block safe input.")
        self.filter.enabled = original_enabled

class TestPerspectiveAPIFilter(unittest.TestCase):
    def setUp(self):
        self.log_path = "test_perspective.log"
        self.filter = PerspectiveAPIFilter({
            "perspective_api": {
                "enabled": True,
                "api_key": "DUMMY_KEY",
                "privacy_mode": True,
                "thresholds": {
                    "TOXICITY": 0.8
                }
            },
            "logging": {
                "log_path": self.log_path
            }
        })
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_disabled_bypass(self):
        self.filter.enabled = False
        allowed, flags, reasons = self.filter.check("You are trash")
        self.assertTrue(allowed, "Disabled filter should never block input.")
        self.assertEqual(flags, [], "Flags should be empty when filter is disabled.")

    def test_perspective_api_failure(self):
        self.filter.enabled = True
        try:
            allowed, flags, reasons = self.filter.check("This should trigger API failure mode.")
            self.assertTrue(allowed, "Perspective API failure should not block input by default.")
        except Exception as e:
            self.fail(f"Perspective API filter crashed on error: {e}")

if __name__ == "__main__":
    unittest.main()
