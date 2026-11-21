import unittest
import re
import os

class TestComplianceAndDates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.html_files = {}
        for fname in [
            'index.html',
            'dutch-career-hub.html',
            'job-finder.html',
            'linkedin-optimizer.html',
            'strategy.html',
            'influencer-insights.html',
            'resume.html',
            'cv_power_bi_developer.html',
            'cv_bi_project_delivery.html'
        ]:
            fpath = os.path.join(base_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    cls.html_files[fname] = f.read()

        cls.index_content = cls.html_files.get('index.html', '')
        cls.cv_content = cls.html_files.get('cv_power_bi_developer.html', '')

    def test_no_future_employment_dates(self):
        """Verify no future employment end dates exist across all HTML documents."""
        future_patterns = [r'December 2026', r'Dec 2026', r'2027', r'2028']
        for fname, content in self.html_files.items():
            for pat in future_patterns:
                matches = re.findall(pat, content, re.IGNORECASE)
                self.assertEqual(len(matches), 0, f"Future date pattern '{pat}' found in {fname}: {matches}")

    def test_consistent_current_role(self):
        """Verify ongoing Apexon role is marked as Present consistently."""
        self.assertIn("Present", self.index_content, "Apexon current role should specify Present in index.html")
        self.assertIn("Present", self.cv_content, "Apexon current role should specify Present in cv_power_bi_developer.html")

    def test_no_third_party_trackers(self):
        """Verify that all hub pages contain zero third-party tracking scripts."""
        trackers = ['google-analytics.com', 'googletagmanager.com', 'connect.facebook.net', 'hotjar.com']
        for fname, content in self.html_files.items():
            for tracker in trackers:
                self.assertNotIn(tracker, content.lower(), f"Privacy violation in {fname}: Found tracking script {tracker}")

    def test_ind_legal_endorsement(self):
        """Verify official IND legal work authorization endorsement is present."""
        self.assertIn("Arbeid vrij toegestaan", self.index_content, "Missing IND legal phrase 'Arbeid vrij toegestaan'")
        self.assertIn("TWV niet vereist", self.index_content, "Missing IND legal phrase 'TWV niet vereist'")

    def test_no_misleading_gdpr_wipes(self):
        """Ensure no misleading 'GDPR deletion' button exists that purges unrelated origin storage."""
        self.assertNotIn("cleartrackerdata", self.index_content.lower(), "Misleading origin-clearing script found in index.html")

if __name__ == '__main__':
    unittest.main()
