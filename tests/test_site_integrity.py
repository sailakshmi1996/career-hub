import unittest
import os
import re

class TestSiteIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.index_path = os.path.join(cls.base_dir, 'index.html')
        with open(cls.index_path, 'r', encoding='utf-8') as f:
            cls.index_content = f.read()

        cls.hub_path = os.path.join(cls.base_dir, 'dutch-career-hub.html')
        with open(cls.hub_path, 'r', encoding='utf-8') as f:
            cls.hub_content = f.read()

    def test_local_assets_exist(self):
        """Verify that all core portfolio files and PDF CVs exist on disk and are non-empty."""
        required_files = [
            'cv_power_bi_developer.pdf',
            'cv_bi_project_delivery.pdf',
            'Sai_Lakshmi_Elusuri_Resume.pdf',
            'cv_power_bi_developer.html',
            'cv_bi_project_delivery.html',
            'resume.html',
            'dutch-career-hub.html',
            'Netherlands_Career_Hub_Sai_Lakshmi.zip'
        ]
        for filename in required_files:
            file_path = os.path.join(self.base_dir, filename)
            self.assertTrue(os.path.isfile(file_path), f"Required asset missing on disk: {filename}")
            self.assertGreater(os.path.getsize(file_path), 500, f"Asset file is unexpectedly small: {filename}")

    def test_internal_navigation_anchors(self):
        """Verify that every internal anchor link (#id) in index.html resolves to a valid element id."""
        anchor_links = set(re.findall(r'href="#([a-zA-Z0-9_\-]+)"', self.index_content))
        element_ids = set(re.findall(r'id="([a-zA-Z0-9_\-]+)"', self.index_content))

        self.assertGreater(len(anchor_links), 0, "No internal anchor links found")
        for anchor in anchor_links:
            self.assertIn(anchor, element_ids, f"Broken navigation link: href='#{anchor}' has no matching id='{anchor}' in index.html")

    def test_women_in_tech_communities_in_hub(self):
        """Verify that curated Netherlands women in tech communities are preserved in the regional hub."""
        required_communities = [
            "Equals Amsterdam",
            "Women in Tech NL",
            "Women in Data Amsterdam",
            "WomenHack Amsterdam"
        ]
        for community in required_communities:
            self.assertIn(community, self.hub_content, f"Missing featured community in regional hub: {community}")

    def test_technical_anchors_and_metrics(self):
        """Verify key technical skills and verified metrics are present with realistic context."""
        self.assertIn("40%", self.index_content, "Missing 40% dashboard load-time reduction metric")
        self.assertIn("VertiPaq", self.index_content, "Missing VertiPaq engine reference")
        self.assertIn("star schema", self.index_content.lower(), "Missing star schema reference")
        self.assertIn("Microsoft Fabric", self.index_content, "Missing Microsoft Fabric reference")
        self.assertIn("DAX", self.index_content, "Missing DAX reference")

if __name__ == '__main__':
    unittest.main()
