import unittest
import re
import os

class TestComplianceAndDates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.index_path = os.path.join(base_dir, 'index.html')
        with open(cls.index_path, 'r', encoding='utf-8') as f:
            cls.content = f.read()

    def test_zero_calendar_dates_and_timelines(self):
        """Verify that index.html contains no rigid calendar dates, months, or countdown years in roadmap."""
        # Find forbidden calendar months
        months = ['January', 'February', 'March', 'April', 'June', 'July', 
                  'August', 'September', 'October', 'November', 'December']
        for month in months:
            matches = re.findall(rf'\b{month}\b', self.content, re.IGNORECASE)
            self.assertEqual(len(matches), 0, f"Forbidden calendar month found: {month} in index.html")

        # Find specific timeline years in roadmap context (2025, 2026, 2027)
        year_matches = re.findall(r'\b(202[4-7])\b', self.content)
        self.assertEqual(len(year_matches), 0, f"Forbidden timeline years found: {year_matches}")

    def test_gdpr_privacy_guarantees(self):
        """Verify GDPR/AVG compliance elements are present in index.html."""
        # Must not contain third-party tracking scripts
        trackers = ['google-analytics.com', 'googletagmanager.com', 'connect.facebook.net', 'hotjar.com']
        for tracker in trackers:
            self.assertNotIn(tracker, self.content.lower(), f"GDPR Violation: Found tracking script {tracker}")

        # Must include Dutch AVG legal notices & BSN protection
        self.assertIn("BSN", self.content, "Missing BSN privacy protection notice")
        self.assertIn("legally forbidden", self.content.lower(), "Missing notice about forbidden BSN pre-employment requests")
        self.assertIn("cleartrackerdata", self.content.lower(), "Missing candidate right-to-erasure / local storage purge script")

    def test_ind_legal_endorsement(self):
        """Verify IND legal work authorization endorsement is explicitly present."""
        self.assertIn("Arbeid vrij toegestaan", self.content, "Missing IND legal phrase 'Arbeid vrij toegestaan'")
        self.assertIn("TWV niet vereist", self.content, "Missing IND legal phrase 'TWV niet vereist'")

if __name__ == '__main__':
    unittest.main()
