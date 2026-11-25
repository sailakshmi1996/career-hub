import os
import re
import unittest


class TestSiteIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(cls.base_dir, "index.html"), "r", encoding="utf-8") as f:
            cls.index_content = f.read()
        with open(os.path.join(cls.base_dir, "resume.html"), "r", encoding="utf-8") as f:
            cls.resume_content = f.read()
        with open(os.path.join(cls.base_dir, "shared.css"), "r", encoding="utf-8") as f:
            cls.css_content = f.read()

    def test_public_assets_exist(self):
        """Verify all canonical public portfolio assets exist and are non-empty."""
        required_files = [
            "index.html",
            "resume.html",
            "shared.css",
            "Sai_Lakshmi_Elusuri_CV.pdf",
            "og-cover.png",
            "robots.txt",
            "sitemap.xml",
        ]
        for filename in required_files:
            fpath = os.path.join(self.base_dir, filename)
            self.assertTrue(os.path.isfile(fpath), f"Missing public asset: {filename}")
            self.assertGreater(os.path.getsize(fpath), 50, f"Asset unexpectedly small: {filename}")

    def test_private_files_excluded_from_public_repo_and_dist(self):
        """Ensure private job-hunt tools, research, and unconfirmed registers stay out of root & dist/."""
        forbidden_paths = [
            "FACTS_TO_CONFIRM.md",
            "research",
            "job-finder.html",
            "strategy.html",
            "linkedin-optimizer.html",
            "influencer-insights.html",
            "dutch-career-hub.html",
            "Netherlands_Career_Hub_Sai_Lakshmi.zip",
            "netlify_deploy.zip",
            "cv_bi_project_delivery.pdf",
            "cv_bi_project_delivery.html",
            "cv_power_bi_developer.pdf",
        ]
        for rel in forbidden_paths:
            self.assertFalse(os.path.exists(os.path.join(self.base_dir, rel)), f"Private/retired path leaked in root: {rel}")
            self.assertFalse(os.path.exists(os.path.join(self.base_dir, "dist", rel)), f"Private/retired path leaked in dist/: {rel}")

    def test_internal_navigation_anchors(self):
        """Verify every href='#id' in index.html resolves to a matching element id."""
        anchors = set(re.findall(r'href="#([a-zA-Z0-9_\-]+)"', self.index_content))
        ids = set(re.findall(r'id="([a-zA-Z0-9_\-]+)"', self.index_content))
        self.assertGreater(len(anchors), 0, "No internal anchor links found")
        for anchor in anchors:
            self.assertIn(anchor, ids, f"Broken anchor link href='#{anchor}'")

    def test_semantic_landmarks_and_balanced_divs(self):
        """Verify <nav>, <main>, <header>, <footer>, skip-link, and balanced <div> tags."""
        for label, html in [("index.html", self.index_content), ("resume.html", self.resume_content)]:
            opens = len(re.findall(r"<div\b", html))
            closes = len(re.findall(r"</div>", html))
            self.assertEqual(opens, closes, f"Unbalanced <div> tags in {label}: {opens} vs {closes}")

        self.assertIn("<nav ", self.index_content)
        self.assertIn("<main ", self.index_content)
        self.assertIn("skip-link", self.index_content)
        self.assertIn("<footer ", self.index_content)

    def test_technical_showcase_accuracy(self):
        """Verify fixed DAX, Oracle SQL, and Fabric PySpark patterns."""
        dax_path = os.path.join(self.base_dir, "technical-showcase", "dax", "calculation_groups_and_semi_additive.dax")
        with open(dax_path, "r", encoding="utf-8") as f:
            dax = f.read()
        self.assertIn("DATESYTD('Dim_Date'[Date])", dax)
        self.assertIn("SAMEPERIODLASTYEAR('Dim_Date'[Date])", dax)
        self.assertIn("ISSELECTEDMEASURE(", dax)
        self.assertNotIn("COALESCE(_Rate, 1.0)", dax)
        self.assertNotIn("FILTER(ALL(FactSales)", dax)

        sql_path = os.path.join(self.base_dir, "technical-showcase", "sql", "oracle_incremental_staging_cte.sql")
        with open(sql_path, "r", encoding="utf-8") as f:
            sql = f.read()
        self.assertIn("CREATE OR REPLACE VIEW", sql)
        self.assertNotIn("ORDER BY\n    date_key", sql)

        py_path = os.path.join(self.base_dir, "technical-showcase", "fabric_pyspark", "delta_lake_v_order_pipeline.py")
        with open(py_path, "r", encoding="utf-8") as f:
            py_code = f.read()
        self.assertIn("DeltaTable.forName", py_code)
        self.assertIn(".merge(", py_code)
        self.assertIn("assert_quality_checks", py_code)
        self.assertNotIn('.mode("overwrite")', py_code)

    def test_no_fake_simulator_or_vercel_traces(self):
        """Ensure fake telemetry simulator and out-of-scope Vercel traces are absent."""
        for content in [self.index_content, self.resume_content, self.css_content]:
            self.assertNotIn("vercel", content.lower())
        self.assertNotIn("telemetryModes", self.index_content)
        self.assertNotIn("telemetry-stats-grid", self.index_content)
        self.assertNotIn("Verified Performance ROI", self.index_content)


if __name__ == "__main__":
    unittest.main()
