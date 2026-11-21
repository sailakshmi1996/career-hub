import unittest
import re
import os

class TestComplianceAndDates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.index_path = os.path.join(base_dir, 'index.html')
        with open(cls.index_path, 'r', encoding='utf-8') as f:
            cls.index_content = f.read()

        cls.cv_path = os.path.join(base_dir, 'cv_power_bi_developer.html')
        with open(cls.cv_path, 'r', encoding='utf-8') as f:
            cls.cv_content = f.read()

    def test_no_future_employment_dates(self):
        """Verify no future employment end dates exist (e.g. Dec 2026 when review date is Nov 16, 2026)."""
        future_patterns = [r'December 2026', r'Dec 2026', r'2027', r'2028']
        for pat in future_patterns:
            matches_idx = re.findall(pat, self.index_content, re.IGNORECASE)
            self.assertEqual(len(matches_idx), 0, f"Future date pattern '{pat}' found in index.html: {matches_idx}")
            matches_cv = re.findall(pat, self.cv_content, re.IGNORECASE)
            self.assertEqual(len(matches_cv), 0, f"Future date pattern '{pat}' found in cv_power_bi_developer.html: {matches_cv}")

    def test_consistent_current_role(self):
        """Verify ongoing Apexon role is marked as Present consistently."""
        self.assertIn("Present", self.index_content, "Apexon current role should specify Present in index.html")
        self.assertIn("Present", self.cv_content, "Apexon current role should specify Present in cv_power_bi_developer.html")

    def test_no_third_party_trackers(self):
        """Verify that index.html contains no third-party tracking scripts."""
        trackers = ['google-analytics.com', 'googletagmanager.com', 'connect.facebook.net', 'hotjar.com']
        for tracker in trackers:
            self.assertNotIn(tracker, self.index_content.lower(), f"Privacy violation: Found tracking script {tracker}")

    def test_ind_legal_endorsement(self):
        """Verify official IND legal work authorization endorsement is present."""
        self.assertIn("Arbeid vrij toegestaan", self.index_content, "Missing IND legal phrase 'Arbeid vrij toegestaan'")
        self.assertIn("TWV niet vereist", self.index_content, "Missing IND legal phrase 'TWV niet vereist'")

    def test_no_misleading_gdpr_wipes(self):
        """Ensure no misleading 'GDPR deletion' button exists that purges unrelated origin storage."""
        self.assertNotIn("cleartrackerdata", self.index_content.lower(), "Misleading origin-clearing script found in index.html")

if __name__ == '__main__':
    unittest.main()
