import unittest
from core.keyword_filter import KeywordRegexFilter
from core.classifier_filter import ClassifierFilter
from core.perspective_api_filter import PerspectiveAPIFilter

class TestKeywordRegexFilter(unittest.TestCase):
    def setUp(self):
        self.filter = KeywordRegexFilter("config/safeguard_config.json")

    def test_blocked_keyword(self):
        allowed, flags, reasons = self.filter.check("Let's talk about drugs")
        self.assertFalse(allowed)
        self.assertIn("keyword", flags)

    def test_blocked_regex(self):
        allowed, flags, reasons = self.filter.check("He sent me a naked picture")
        self.assertFalse(allowed)
        self.assertIn("regex", flags)

    def test_allowed(self):
        allowed, flags, reasons = self.filter.check("Let's talk about healthy food")
        self.assertTrue(allowed)
        self.assertEqual(flags, [])

class TestClassifierFilter(unittest.TestCase):
    def setUp(self):
        self.filter = ClassifierFilter("config/safeguard_config.json")

    def test_classifier_toxic(self):
        if not self.filter.enabled:
            self.skipTest("Classifier not enabled in config")
        allowed, flags, reasons = self.filter.check("You are an idiot and should kill yourself")
        self.assertFalse(allowed)
        self.assertTrue(any("classifier" in f for f in flags))

class TestPerspectiveAPIFilter(unittest.TestCase):
    def setUp(self):
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
        self.filter.enabled = False
        allowed, flags, reasons = self.filter.check("You are trash")
        self.assertTrue(allowed)
        self.assertEqual(flags, [])

if __name__ == "__main__":
    unittest.main()
