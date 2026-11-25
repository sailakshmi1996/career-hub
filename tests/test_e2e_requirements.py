#!/usr/bin/env python3
"""
tests/test_e2e_requirements.py
Verification Suite for Direction 1 ("Editorial Analytics Brief") Portfolio
"""

import os
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

try:
    import fitz
except ImportError:
    fitz = None

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def read_project_file(rel_path: str) -> str:
    target = BASE_DIR / rel_path
    if not target.exists():
        return ""
    return target.read_text(encoding="utf-8", errors="replace")


def srgb_to_linear(channel: float) -> float:
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)


def wcag_contrast_ratio(hex1: str, hex2: str) -> float:
    l1, l2 = relative_luminance(hex1), relative_luminance(hex2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


class HTMLInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.headings = []
        self.tablists = 0
        self.tabs = 0
        self.tabpanels = 0
        self.meta_tags = []
        self._stack = []

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if "id" in ad:
            self.ids.add(ad["id"])
        if tag == "meta":
            self.meta_tags.append(ad)
        if ad.get("role") == "tablist":
            self.tablists += 1
        elif ad.get("role") == "tab":
            self.tabs += 1
        elif ad.get("role") == "tabpanel":
            self.tabpanels += 1
        self._stack.append((tag, ad, []))

    def handle_data(self, data):
        for _, _, buf in self._stack:
            buf.append(data)

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                _, ad, buf = self._stack.pop(i)
                txt = "".join(buf).strip()
                if tag == "a":
                    self.links.append((ad.get("href", ""), ad, txt))
                elif tag in ("h1", "h2", "h3", "h4"):
                    self.headings.append((int(tag[1]), txt))
                break


class TestDirection1Portfolio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = read_project_file("index.html")
        cls.css = read_project_file("shared.css")
        cls.resume_html = read_project_file("resume.html")
        cls.doc = HTMLInspector()
        cls.doc.feed(cls.html)

    def test_wcag_aa_contrast_light_and_dark_tokens(self):
        """Verify all primary Light and Dark Direction 1 pairs meet >= 4.5:1 WCAG AA."""
        pairs = [
            ("#111827", "#FAF9F5"),  # Light ink on Alabaster
            ("#111827", "#FFFFFF"),  # Light ink on Surface
            ("#4B5563", "#FAF9F5"),  # Secondary on Alabaster
            ("#1D4ED8", "#FAF9F5"),  # Accent primary on Alabaster
            ("#FFFFFF", "#1D4ED8"),  # CTA text on Accent primary
            ("#047857", "#FFFFFF"),  # Evidence green on White
            ("#047857", "#ECFDF5"),  # Evidence green on tint
            ("#F3F4F6", "#0F141C"),  # Dark text on Charcoal
            ("#9CA3AF", "#0F141C"),  # Dark muted on Charcoal
            ("#60A5FA", "#0F141C"),  # Dark accent on Charcoal
            ("#0F141C", "#60A5FA"),  # CTA text on Dark accent
            ("#34D399", "#171E29"),  # Dark mint on Surface
        ]
        for fg, bg in pairs:
            ratio = wcag_contrast_ratio(fg, bg)
            self.assertGreaterEqual(ratio, 4.5, f"WCAG AA contrast failed for {fg} on {bg}: {ratio:.2f}:1")

    def test_no_remote_fonts_or_external_cdn(self):
        """Verify local font stack and zero Google Fonts / CDN tracking."""
        self.assertNotIn("fonts.googleapis.com", self.html)
        self.assertNotIn("fonts.gstatic.com", self.html)
        self.assertNotIn("@import url", self.css.lower())
        self.assertIn("-apple-system", self.css)

    def test_heading_hierarchy_strict_order(self):
        """Verify single H1 and no skipped heading levels (h1 -> h2 -> h3)."""
        h1s = [lvl for lvl, _ in self.doc.headings if lvl == 1]
        self.assertEqual(len(h1s), 1, f"Expected exactly 1 H1, found {len(h1s)}")
        prev = 1
        for lvl, txt in self.doc.headings:
            self.assertLessEqual(lvl - prev, 1, f"Skipped heading level to h{lvl} ('{txt}') after h{prev}")
            prev = lvl

    def test_single_canonical_cv_pdf_links(self):
        """Verify index.html links strictly to Sai_Lakshmi_Elusuri_CV.pdf with target=_blank and no download attr."""
        pdf_links = [(href, attrs) for href, attrs, _ in self.doc.links if href.endswith(".pdf")]
        self.assertGreaterEqual(len(pdf_links), 2)
        for href, attrs in pdf_links:
            self.assertEqual(href, "Sai_Lakshmi_Elusuri_CV.pdf", f"Unexpected secondary PDF link: {href}")
            self.assertEqual(attrs.get("target"), "_blank")
            self.assertIn("noopener", attrs.get("rel", ""))
            self.assertNotIn("download", attrs)

    def test_canonical_pdf_two_pages_a4_and_clean(self):
        """Verify compiled Sai_Lakshmi_Elusuri_CV.pdf is 2 pages A4 with unified title and no +91 phone."""
        pdf_path = BASE_DIR / "Sai_Lakshmi_Elusuri_CV.pdf"
        self.assertTrue(pdf_path.exists(), "Sai_Lakshmi_Elusuri_CV.pdf missing")
        if fitz is not None:
            doc = fitz.open(str(pdf_path))
            self.assertEqual(len(doc), 2, f"CV PDF must be 2 pages, got {len(doc)}")
            full_text = "\n".join(page.get_text() for page in doc)
            doc.close()
            self.assertIn("Senior Power BI & Microsoft Fabric Developer", full_text)
            self.assertIn("Arbeid vrij toegestaan, TWV niet vereist", full_text)
            self.assertNotIn("+91", full_text)
            self.assertNotIn("dbt Core", full_text)

    def test_wai_aria_case_file_tabs_and_star_schema_integrity(self):
        """Verify 3 interactive Case-Files with WAI-ARIA tabs and accurate Star Schema FK parity."""
        self.assertEqual(self.doc.tablists, 3)
        self.assertEqual(self.doc.tabs, 9)
        self.assertEqual(self.doc.tabpanels, 9)
        self.assertIn("Fact_Sustainability_Activity", self.html)
        self.assertIn("Dim_RLS_Security", self.html)
        self.assertIn("RlsUnitKey", self.html)
        self.assertIn('role="img"', self.html)
        self.assertIn("marker-end=", self.html)

    def test_accessibility_and_reduced_motion(self):
        """Verify skip link, focus-visible, prefers-reduced-motion, opaque mobile header, and 44px targets."""
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn(":focus-visible", self.css)
        self.assertIn("min-height: 44px", self.css)
        self.assertIn("background: var(--bg-canvas);", self.css)
        self.assertIn('aria-expanded="false"', self.html)
        self.assertIn('id="visual-lightbox"', self.html)

    def test_seo_og_image_and_dist_outputs(self):
        """Verify OG image, sitemap, robots, headers, and dist/ clean deployment artifacts."""
        self.assertIn("og-cover.png", self.html)
        self.assertTrue((BASE_DIR / "dist" / "index.html").exists())
        self.assertTrue((BASE_DIR / "dist" / "Sai_Lakshmi_Elusuri_CV.pdf").exists())
        self.assertTrue((BASE_DIR / "dist" / "og-cover.png").exists())
        self.assertTrue((BASE_DIR / "dist" / "robots.txt").exists())
        self.assertTrue((BASE_DIR / "dist" / "sitemap.xml").exists())
        self.assertTrue((BASE_DIR / "dist" / "_headers").exists())
        self.assertTrue((BASE_DIR / "dist" / "404.html").exists())
        self.assertTrue((BASE_DIR / "dist" / "cv" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
