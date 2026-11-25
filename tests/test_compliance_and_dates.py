import os
import re
import unittest


class TestComplianceAndDates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.html_files = {}
        for fname in ["index.html", "resume.html"]:
            fpath = os.path.join(base_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    cls.html_files[fname] = f.read()
        cls.index_content = cls.html_files.get("index.html", "")
        cls.resume_content = cls.html_files.get("resume.html", "")

    def test_no_future_employment_dates(self):
        """Verify no future employment dates exist across public HTML documents."""
        future_patterns = [r"December 2026", r"Dec 2026", r"2027", r"2028"]
        for fname, content in self.html_files.items():
            for pat in future_patterns:
                matches = re.findall(pat, content, re.IGNORECASE)
                self.assertEqual(len(matches), 0, f"Future date pattern '{pat}' found in {fname}: {matches}")

    def test_consistent_current_role_and_unified_title(self):
        """Verify unified title and ongoing Apexon role across public pages."""
        for fname, content in self.html_files.items():
            self.assertIn("Senior Power BI &amp; Microsoft Fabric Developer", content, f"Missing unified title in {fname}")
            self.assertIn("Apr 2026–Present", content, f"Missing Apexon Present date in {fname}")

    def test_no_third_party_trackers(self):
        """Verify zero third-party analytics or tracking scripts."""
        trackers = ["google-analytics.com", "googletagmanager.com", "connect.facebook.net", "hotjar.com"]
        for fname, content in self.html_files.items():
            for tracker in trackers:
                self.assertNotIn(tracker, content.lower(), f"Tracking script {tracker} found in {fname}")

    def test_no_public_phone_or_scraper_leaks(self):
        """Verify +91 phone is removed from public HTML pages and raw mailto is guarded on index.html."""
        for fname, content in self.html_files.items():
            self.assertNotIn("+91", content, f"Public +91 phone found in {fname}")
            self.assertNotIn("8142674401", content, f"Phone digits leaked in {fname}")
        self.assertNotIn("mailto:sailakshmi.elusuri@gmail.com", self.index_content, "Raw mailto exposed in index.html")

    def test_ind_legal_endorsement(self):
        """Verify official IND legal work authorization endorsement is present."""
        for fname, content in self.html_files.items():
            self.assertIn("Arbeid vrij toegestaan", content, f"Missing IND phrase in {fname}")
            self.assertIn("TWV niet vereist", content, f"Missing TWV phrase in {fname}")


if __name__ == "__main__":
    unittest.main()
