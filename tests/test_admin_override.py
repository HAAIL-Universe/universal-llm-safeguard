import unittest
from utils.override_checker import check_override

TEST_OVERRIDE_DATA = {
    "parent_phrases": ["override123"],
    "moderator_phrases": ["modunlock!"]
}

class TestAdminOverride(unittest.TestCase):

    def test_parent_override_detected(self):
        text = "Please allow this override123"
        used, role, cleaned = check_override(text, override_data=TEST_OVERRIDE_DATA)
        self.assertTrue(used)
        self.assertEqual(role, "parent")
        self.assertEqual(cleaned, "Please allow this")

    def test_moderator_override_detected(self):
        text = "Allow this modunlock! now"
        used, role, cleaned = check_override(text, override_data=TEST_OVERRIDE_DATA)
        self.assertTrue(used)
        self.assertEqual(role, "moderator")
        self.assertEqual(cleaned, "Allow this now")

    def test_no_override_detected(self):
        text = "This should be blocked"
        used, role, cleaned = check_override(text, override_data=TEST_OVERRIDE_DATA)
        self.assertFalse(used)
        self.assertIsNone(role)
        self.assertEqual(cleaned, text)

    def test_override_stripping_exact_parent(self):
        text = "override123"
        used, role, cleaned = check_override(text, override_data=TEST_OVERRIDE_DATA)
        self.assertTrue(used)
        self.assertEqual(role, "parent")
        self.assertEqual(cleaned, "")

    def test_override_stripping_exact_moderator(self):
        text = "modunlock!"
        used, role, cleaned = check_override(text, override_data=TEST_OVERRIDE_DATA)
        self.assertTrue(used)
        self.assertEqual(role, "moderator")
        self.assertEqual(cleaned, "")

    def test_multiple_phrases_only_first_applies(self):
        text = "modunlock! and then override123"
        used, role, cleaned = check_override(text, override_data=TEST_OVERRIDE_DATA)
        self.assertTrue(used)
        self.assertEqual(role, "moderator")  # first match wins
        self.assertEqual(cleaned, "and then override123")

if __name__ == '__main__':
    unittest.main()
