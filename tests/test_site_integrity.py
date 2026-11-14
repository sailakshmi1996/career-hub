import unittest
import os
import re

class TestSiteIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.index_path = os.path.join(cls.base_dir, 'index.html')
        with open(cls.index_path, 'r', encoding='utf-8') as f:
            cls.content = f.read()

    def test_local_assets_exist(self):
        """Verify that all files referenced in index.html actually exist in the repository."""
        required_files = [
            'cv_power_bi_developer.pdf',
            'cv_bi_project_delivery.pdf',
            'cv_power_bi_developer.html',
            'cv_bi_project_delivery.html',
            'dutch-career-hub.html',
            'Netherlands_Career_Hub_Sai_Lakshmi.zip'
        ]
        for filename in required_files:
            file_path = os.path.join(self.base_dir, filename)
            self.assertTrue(os.path.isfile(file_path), f"Required asset missing on disk: {filename}")
            # Ensure file is not empty
            self.assertGreater(os.path.getsize(file_path), 100, f"Asset file is unexpectedly empty: {filename}")

    def test_internal_navigation_anchors(self):
        """Verify that every internal anchor link (#id) has a corresponding target element id."""
        # Find all href="#id"
        anchor_links = set(re.findall(r'href="#([a-zA-Z0-9_\-]+)"', self.content))
        # Find all id="id"
        element_ids = set(re.findall(r'id="([a-zA-Z0-9_\-]+)"', self.content))

        self.assertGreater(len(anchor_links), 0, "No internal anchor links found")
        for anchor in anchor_links:
            self.assertIn(anchor, element_ids, f"Broken navigation link: href='#{anchor}' has no matching id='{anchor}' in document")

    def test_women_in_tech_communities(self):
        """Verify that all 10 curated Amsterdam-Utrecht women in tech communities are featured."""
        required_communities = [
            "Equals Amsterdam",
            "Women in Tech NL",
            "Women in Data Amsterdam",
            "WomenHack Amsterdam",
            "Women in AI",
            "PyLadies Amsterdam",
            "Girl Code Amsterdam",
            "She's Coding",
            "R-Ladies Amsterdam",
            "Women in Tech Regatta"
        ]
        for community in required_communities:
            self.assertIn(community, self.content, f"Missing featured community: {community}")

    def test_technical_anchors_and_metrics(self):
        """Verify key technical interview topics and metrics are present."""
        self.assertIn("40%", self.content, "Missing key 40% dashboard load-time reduction metric")
        self.assertIn("VertiPaq", self.content, "Missing VertiPaq engine optimization reference")
        self.assertIn("star schema", self.content.lower(), "Missing star schema reference")
        self.assertIn("Microsoft Fabric", self.content, "Missing Microsoft Fabric reference")

if __name__ == '__main__':
    unittest.main()
