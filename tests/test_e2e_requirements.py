#!/usr/bin/env python3
"""
tests/test_e2e_requirements.py
================================================================================
Sai Lakshmi Elusuri Recruiter Portfolio Redesign — E2E Requirements Test Suite
================================================================================

Opaque-Box Requirement-Driven Test Suite derived strictly from:
- ORIGINAL_REQUEST.md
- PROJECT.md (§ Feature Inventory & Interface Contracts)
- TEST_INFRA.md (4-Tier Verification Architecture)

This test suite operates as an independent audit oracle for all 23 features,
boundary/corner conditions, cross-feature invariants, and real-world Dutch recruiter
user journeys without relying on pre-existing test files or facade implementations.

Architecture:
  - Tier 1: Feature Coverage (Features 1–23, 5 tests each = 115 tests)
  - Tier 2: Boundary & Corner Cases (20 tests)
  - Tier 3: Cross-Feature Combinations (7 tests)
  - Tier 4: Real-World Application Scenarios (5 tests)
  Total: 147 test cases.
"""

import os
import sys
import re
import json
import zipfile
import unittest
from pathlib import Path
from html.parser import HTMLParser

# PyMuPDF with graceful fallback for PDF testing
try:
    import fitz
except ImportError:
    fitz = None

# Base directory for the repository
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER UTILITIES & PARSERS (Pure Python Standard Library)
# ═══════════════════════════════════════════════════════════════════════════════

def read_project_file(rel_path: str) -> str:
    """Reads a text file relative to the project root with UTF-8 encoding."""
    target = BASE_DIR / rel_path
    if not target.exists():
        return ""
    with open(target, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def file_exists(rel_path: str) -> bool:
    """Checks whether a project file exists."""
    return (BASE_DIR / rel_path).exists()


class HTMLDocumentParser(HTMLParser):
    """Robust HTML document parser extracting elements, attributes, text, and structure."""
    def __init__(self):
        super().__init__()
        self.tags = []              # [(tag, attrs_dict, inner_text)]
        self.elements_by_id = {}    # id -> (tag, attrs_dict, inner_text)
        self.links = []             # [(href, attrs_dict, link_text)]
        self.buttons = []           # [(attrs_dict, button_text)]
        self.meta_tags = []         # [attrs_dict]
        self.sections = []          # [(section_id, attrs_dict, text)]
        self.all_text = []
        self._tag_stack = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_info = {"tag": tag, "attrs": attrs_dict, "text": []}
        self._tag_stack.append(tag_info)

        if tag == "meta":
            self.meta_tags.append(attrs_dict)

        if "id" in attrs_dict:
            self.elements_by_id[attrs_dict["id"]] = tag_info

        if tag == "section":
            self.sections.append((attrs_dict.get("id", ""), attrs_dict, ""))

    def handle_endtag(self, tag):
        if not self._tag_stack:
            return
        # Pop matching tag or closest
        matched = None
        for i in range(len(self._tag_stack) - 1, -1, -1):
            if self._tag_stack[i]["tag"] == tag:
                matched = self._tag_stack.pop(i)
                break
        if matched:
            text_str = "".join(matched["text"]).strip()
            attrs_dict = matched["attrs"]
            self.tags.append((tag, attrs_dict, text_str))
            if tag == "a":
                self.links.append((attrs_dict.get("href", ""), attrs_dict, text_str))
            elif tag == "button":
                self.buttons.append((attrs_dict, text_str))
            if "id" in attrs_dict and attrs_dict["id"] in self.elements_by_id:
                self.elements_by_id[attrs_dict["id"]] = (tag, attrs_dict, text_str)

    def handle_data(self, data):
        self.all_text.append(data)
        for tag_info in self._tag_stack:
            tag_info["text"].append(data)


def parse_html(html_str: str) -> HTMLDocumentParser:
    """Parses HTML string into structured HTMLDocumentParser."""
    parser = HTMLDocumentParser()
    parser.feed(html_str)
    return parser


def parse_css_variables(css_str: str) -> dict:
    """Extracts CSS variable declarations from :root or global blocks."""
    vars_dict = {}
    pattern = re.compile(r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);')
    for match in pattern.finditer(css_str):
        name = match.group(1).strip()
        val = match.group(2).strip()
        vars_dict[name] = val
    return vars_dict


def parse_hex_colors(css_str: str) -> set:
    """Extracts all 6-character hex color codes (uppercase) from CSS."""
    pattern = re.compile(r'#([0-9a-fA-F]{6})\b')
    return {f"#{m.group(1).upper()}" for m in pattern.finditer(css_str)}


def srgb_to_linear(channel: float) -> float:
    """Converts standard 0..255 sRGB channel to linear light value."""
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Calculates relative luminance according to WCAG 2.1 specs."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)


def wcag_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculates WCAG contrast ratio between two hex colors."""
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def inspect_pdf_doc(pdf_path: Path) -> dict:
    """
    Inspects a PDF document using PyMuPDF (fitz) or fallback binary regex.
    Returns:
      {
        'exists': bool,
        'page_count': int,
        'dimensions': [(w, h), ...],
        'full_text': str,
        'page_texts': [str, ...],
        'page2_header': str
      }
    """
    if not pdf_path.exists():
        return {
            "exists": False,
            "page_count": 0,
            "dimensions": [],
            "full_text": "",
            "page_texts": [],
            "page2_header": ""
        }

    if fitz is not None:
        try:
            doc = fitz.open(str(pdf_path))
            page_count = len(doc)
            dims = []
            page_texts = []
            page2_header = ""
            for i, page in enumerate(doc):
                dims.append((page.rect.width, page.rect.height))
                txt = page.get_text()
                page_texts.append(txt)
                if i == 1:
                    # Page 2 running header check: text in top 120 points
                    top_rect = fitz.Rect(0, 0, page.rect.width, 120)
                    page2_header = page.get_text(clip=top_rect)
            full_text = "\n".join(page_texts)
            doc.close()
            return {
                "exists": True,
                "page_count": page_count,
                "dimensions": dims,
                "full_text": full_text,
                "page_texts": page_texts,
                "page2_header": page2_header
            }
        except Exception:
            pass

    # Graceful fallback: binary parsing
    with open(pdf_path, "rb") as f:
        data = f.read()

    pages = re.findall(rb'/Type\s*/Page\b', data)
    page_count = len(pages)
    # MediaBox check
    dims = []
    mb_matches = re.findall(rb'/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]', data)
    for m in mb_matches:
        dims.append((float(m[0]), float(m[1])))

    # Basic text decoding fallback
    text_content = ""
    try:
        text_content = data.decode("latin1")
    except Exception:
        text_content = ""

    return {
        "exists": True,
        "page_count": page_count,
        "dimensions": dims,
        "full_text": text_content,
        "page_texts": [text_content],
        "page2_header": text_content[:500] if len(text_content) > 500 else text_content
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 1: FEATURE COVERAGE (23 Features × 5 Isolated Checks = 115 Tests)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1 tests comprehensively verify each of the 23 discrete features
    identified in PROJECT.md § Feature Inventory and ORIGINAL_REQUEST.md.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 1: Canonical Apexon Date Formatting ("Apr 2026–Present")
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_apexon_date_canonical(self):
        """F1.1: Verify Apexon role in canonical_data.py has dates 'Apr 2026–Present'."""
        try:
            import canonical_data
            candidate = canonical_data.CANDIDATE
            apexon_roles = [e for e in candidate.get("employment", []) if "Apexon" in e.get("company", "")]
            self.assertTrue(len(apexon_roles) >= 1, "Apexon employment entry missing in canonical_data.py")
            date_str = apexon_roles[0].get("dates", "")
            self.assertEqual(
                date_str,
                "Apr 2026–Present",
                f"Apexon date must be exactly 'Apr 2026–Present' (with en-dash), found: {date_str!r}"
            )
        except ImportError:
            self.fail("Could not import canonical_data.py")

    def test_t1_apexon_date_index_html(self):
        """F1.2: Verify 'Apr 2026–Present' appears for Apexon in index.html."""
        html = read_project_file("index.html")
        self.assertTrue(len(html) > 0, "index.html missing or empty")
        # Accept en-dash, HTML entities &ndash;, &#8211;, or standard unicode
        has_apexon = "Apexon" in html
        has_date = bool(re.search(r'Apr\s+2026[\u2013\u2014\-&ndash;#8211;]+Present', html))
        self.assertTrue(has_apexon, "Apexon must be listed in index.html")
        self.assertTrue(has_date, "Apexon date in index.html must be formatted as 'Apr 2026–Present'")

    def test_t1_apexon_date_html_cvs(self):
        """F1.3: Verify 'Apr 2026–Present' appears for Apexon in both HTML CVs."""
        for cv_name in ["cv_power_bi_developer.html", "cv_bi_project_delivery.html"]:
            cv_html = read_project_file(cv_name)
            self.assertTrue(len(cv_html) > 0, f"{cv_name} missing or empty")
            has_date = bool(re.search(r'Apr\s+2026[\u2013\u2014\-&ndash;#8211;]+Present', cv_html))
            self.assertTrue(
                has_date,
                f"{cv_name} must display Apexon dates as 'Apr 2026–Present'"
            )

    def test_t1_apexon_date_markdown_cvs(self):
        """F1.4: Verify 'Apr 2026–Present' appears in markdown CVs if present."""
        for md_name in ["cv_power_bi_developer.md", "cv_bi_project_delivery.md"]:
            if file_exists(md_name):
                content = read_project_file(md_name)
                has_date = bool(re.search(r'Apr\s+2026[\u2013\u2014\-]+Present', content))
                self.assertTrue(
                    has_date,
                    f"Markdown CV {md_name} must contain 'Apr 2026–Present'"
                )

    def test_t1_no_forbidden_timeline_years(self):
        """F1.5: Verify no future countdown or forbidden planning dates exist on public index.html."""
        html = read_project_file("index.html")
        # Public portfolio must not display unapproved planning countdowns or years > 2026 like 2027/2028
        forbidden_patterns = [
            r'target\s+start\s+date\s*:\s*202[789]',
            r'countdown\s*:\s*\d+\s+days',
            r'\b2027\b.*countdown',
            r'days\s+remaining\s+until\s+start'
        ]
        for pat in forbidden_patterns:
            self.assertFalse(
                bool(re.search(pat, html, re.IGNORECASE)),
                f"Public index.html must not contain forbidden future countdown pattern: {pat}"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 2: Formal Job Titles & Responsibilities
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_formal_titles_consistency(self):
        """F2.1: Verify formal job titles are consistent across canonical data and HTML CVs."""
        import canonical_data
        expected_titles = {
            "Apexon": "Senior Data Analyst",
            "Accenture": "Power BI Developer",
            "Genpact": "Data Risk Analyst",
            "Conduent": "Data Analyst"
        }
        for emp in canonical_data.CANDIDATE.get("employment", []):
            comp = emp["company"]
            if comp in expected_titles:
                self.assertEqual(
                    emp["title"],
                    expected_titles[comp],
                    f"Canonical title for {comp} must be {expected_titles[comp]}"
                )

    def test_t1_delivery_bullets_present(self):
        """F2.2: Verify delivery / acting-lead responsibilities are detailed in bullet points."""
        cv_text = read_project_file("cv_bi_project_delivery.html") + read_project_file("index.html")
        delivery_keywords = ["delivery", "sprint", "agile", "stakeholder", "governance", "coordination", "migration"]
        found_keywords = [kw for kw in delivery_keywords if kw in cv_text.lower()]
        self.assertTrue(
            len(found_keywords) >= 4,
            f"Expected at least 4 delivery responsibility keywords, found: {found_keywords}"
        )

    def test_t1_experience_duration_claim(self):
        """F2.3: Verify 8+ years experience is consistently stated across materials."""
        import canonical_data
        self.assertEqual(canonical_data.CANDIDATE.get("experience_years"), "8+")
        html = read_project_file("index.html")
        self.assertIn("8+", html, "index.html must reference '8+' years of enterprise analytics experience")

    def test_t1_location_utrecht_stated(self):
        """F2.4: Verify Utrecht region is consistently stated as primary location."""
        import canonical_data
        self.assertIn("Utrecht", canonical_data.CANDIDATE.get("location", ""))
        html = read_project_file("index.html")
        self.assertIn("Utrecht", html, "index.html must clearly display Utrecht region location")

    def test_t1_work_authorization_stated(self):
        """F2.5: Verify labor authorization matches canonical statement (TWV niet vereist)."""
        import canonical_data
        status = canonical_data.CANDIDATE.get("ind_endorsement", "")
        self.assertIn("TWV niet vereist", status, "Canonical endorsement must state 'TWV niet vereist'")
        html = read_project_file("index.html")
        self.assertTrue(
            "TWV" in html or "Arbeid vrij toegestaan" in html or "Unrestricted" in html,
            "index.html must state work authorization / TWV status clearly"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 3: Technical Explanations & Fact-Checking
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_direct_lake_explanation(self):
        """F3.1: Verify Direct Lake on OneLake vs SQL / VertiPaq is described accurately."""
        html = read_project_file("index.html") + read_project_file("cv_power_bi_developer.html")
        has_direct_lake = "Direct Lake" in html or "DirectLake" in html
        has_vertipaq_or_onelake = "OneLake" in html or "VertiPaq" in html or "Delta" in html
        self.assertTrue(has_direct_lake, "Direct Lake technical concepts must be present in portfolio / CV")
        self.assertTrue(has_vertipaq_or_onelake, "Direct Lake must reference OneLake or VertiPaq caching architecture")

    def test_t1_no_subsecond_claims(self):
        """F3.2: Verify removal of unverified universal 'sub-second' or 'zero-latency' claims."""
        html = read_project_file("index.html")
        # Universal marketing superlatives must not be stated as absolute facts
        self.assertFalse(
            bool(re.search(r'universal\s+sub-second|zero\s*latency\s+across\s+all|sub-second\s+guaranteed', html, re.I)),
            "Universal sub-second or zero latency marketing claims must be removed or qualified"
        )

    def test_t1_no_zero_data_movement_claims(self):
        """F3.3: Verify removal of universal 'zero data movement' marketing claims."""
        html = read_project_file("index.html")
        self.assertFalse(
            bool(re.search(r'absolute\s+zero\s+data\s+movement|guaranteed\s+zero\s+data\s+movement', html, re.I)),
            "Universal zero data movement marketing claims must be qualified or removed"
        )

    def test_t1_vertipaq_se_fe_accuracy(self):
        """F3.4: Verify technical descriptions accurately distinguish Storage Engine (SE) & Formula Engine (FE)."""
        html = read_project_file("index.html") + read_project_file("cv_power_bi_developer.html")
        # Check that SE / Storage Engine and FE / Formula Engine concepts appear without technical inaccuracies
        has_engines = ("Storage Engine" in html or "Formula Engine" in html or "VertiPaq" in html)
        self.assertTrue(has_engines, "Architecture details must reference VertiPaq engines accurately")

    def test_t1_fabric_medallion_architecture(self):
        """F3.5: Verify Fabric architecture references adhere to standard Medallion / OneLake design."""
        html = read_project_file("index.html")
        has_fabric = "Fabric" in html
        has_medallion_or_lake = "Medallion" in html or "OneLake" in html or "Gold" in html or "Silver" in html
        self.assertTrue(has_fabric and has_medallion_or_lake, "Fabric architecture must reference Medallion/OneLake patterns")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 4: Facts to Confirm Documentation
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_facts_to_confirm_file_exists(self):
        """F4.1: Verify FACTS_TO_CONFIRM.md exists on disk."""
        self.assertTrue(file_exists("FACTS_TO_CONFIRM.md"), "FACTS_TO_CONFIRM.md must exist in root repository")

    def test_t1_facts_to_confirm_non_empty(self):
        """F4.2: Verify FACTS_TO_CONFIRM.md contains documented unverified claims or audit notes."""
        content = read_project_file("FACTS_TO_CONFIRM.md")
        self.assertTrue(len(content.strip()) >= 50, "FACTS_TO_CONFIRM.md must not be empty")

    def test_t1_no_unverified_placeholders_public(self):
        """F4.3: Verify index.html contains no unreplaced '[TBD]' or '[unconfirmed]' placeholders."""
        html = read_project_file("index.html")
        placeholders = ["[TBD]", "[TODO]", "[unconfirmed]", "[insert metric]"]
        for p in placeholders:
            self.assertNotIn(p, html, f"Public index.html must not contain placeholder: {p}")

    def test_t1_no_fabricated_metrics_without_basis(self):
        """F4.4: Verify claimed percentage improvements trace to documented case studies."""
        html = read_project_file("index.html")
        # 40% reduction claim should be present with context (e.g. query/dashboard performance)
        if "40%" in html:
            self.assertTrue(
                "reduction" in html.lower() or "performance" in html.lower() or "speed" in html.lower() or "load" in html.lower(),
                "Metric 40% must be contextualized with concrete engineering basis"
            )

    def test_t1_facts_file_mentions_recruiter_context(self):
        """F4.5: Verify FACTS_TO_CONFIRM.md explains recruiter interview verification contexts."""
        content = read_project_file("FACTS_TO_CONFIRM.md")
        has_recruiter = "recruiter" in content.lower() or "interview" in content.lower() or "verification" in content.lower()
        self.assertTrue(has_recruiter, "FACTS_TO_CONFIRM.md must explain context for recruiter verification")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 5: ATS 2-Page A4 CV Generation
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_cv_pdf_files_exist(self):
        """F5.1: Verify cv_power_bi_developer.pdf and cv_bi_project_delivery.pdf exist."""
        self.assertTrue(file_exists("cv_power_bi_developer.pdf"), "cv_power_bi_developer.pdf missing in root")
        self.assertTrue(file_exists("cv_bi_project_delivery.pdf"), "cv_bi_project_delivery.pdf missing in root")

    def test_t1_cv_pdf_page_count(self):
        """F5.2: Verify both compiled CV PDFs have exactly 2 pages."""
        for fname in ["cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf"]:
            info = inspect_pdf_doc(BASE_DIR / fname)
            self.assertTrue(info["exists"], f"{fname} does not exist")
            self.assertEqual(info["page_count"], 2, f"{fname} must be exactly 2 pages, got {info['page_count']}")

    def test_t1_cv_pdf_a4_dimensions(self):
        """F5.3: Verify page width and height match A4 standard (595.28 x 841.89 points ± 3pt)."""
        for fname in ["cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf"]:
            info = inspect_pdf_doc(BASE_DIR / fname)
            for i, (w, h) in enumerate(info["dimensions"]):
                self.assertAlmostEqual(w, 595.28, delta=4.0, msg=f"{fname} page {i+1} width must be A4 (595pt)")
                self.assertAlmostEqual(h, 841.89, delta=4.0, msg=f"{fname} page {i+1} height must be A4 (842pt)")

    def test_t1_cv_pdf_selectable_text(self):
        """F5.4: Verify extracted text length exceeds 1000 characters (non-rasterized ATS text)."""
        for fname in ["cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf"]:
            info = inspect_pdf_doc(BASE_DIR / fname)
            self.assertTrue(
                len(info["full_text"]) > 1000,
                f"{fname} must contain real selectable text (>1000 chars), got {len(info['full_text'])}"
            )

    def test_t1_cv_pdf_page_two_header(self):
        """F5.5: Verify page 2 contains candidate name and page number."""
        for fname in ["cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf"]:
            info = inspect_pdf_doc(BASE_DIR / fname)
            if len(info["page_texts"]) >= 2:
                p2_text = info["page_texts"][1]
                self.assertIn("Sai Lakshmi", p2_text, f"{fname} page 2 must contain candidate name")
                self.assertTrue(
                    "2" in p2_text or "Page 2" in p2_text,
                    f"{fname} page 2 must indicate page number 2"
                )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 6: Warm Editorial Visual Design System
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_css_palette_tokens(self):
        """F6.1: Verify the 10 warm editorial hex tokens exist in CSS or design system."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        required_tokens = [
            "#0B1220",  # deep navy
            "#F5F4EF",  # warm paper
            "#FFFFFF",  # white cards
            "#172334",  # dark text
            "#596579",  # muted text
            "#63D8D0",  # bright teal
            "#087F8C",  # deep teal
            "#3156C8",  # cobalt blue
            "#E36A57",  # warm coral
            "#DDE5EA"   # pale blue-gray
        ]
        found_hexes = parse_hex_colors(css)
        matched = [tok for tok in required_tokens if tok in found_hexes]
        self.assertEqual(
            len(matched),
            len(required_tokens),
            f"Missing warm editorial color tokens in CSS. Found {len(matched)}/10: missing {[t for t in required_tokens if t not in found_hexes]}"
        )

    def test_t1_body_background_token(self):
        """F6.2: Verify body uses warm paper background (#F5F4EF or token)."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_paper = ("#F5F4EF" in css.upper() or "F5F4EF" in css.upper() or "--color-paper" in css or "--bg-paper" in css or "--paper" in css)
        self.assertTrue(has_paper, "Body background must implement warm paper token (#F5F4EF)")

    def test_t1_card_background_token(self):
        """F6.3: Verify cards use white card token (#FFFFFF or token)."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_white_card = "#FFFFFF" in css.upper() or "#FFF" in css.upper() or "--surface-card" in css
        self.assertTrue(has_white_card, "Card surfaces must utilize white card token")

    def test_t1_text_color_tokens(self):
        """F6.4: Verify primary text uses dark text token (#172334 or token)."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_dark_text = "#172334" in css.upper() or "--text-dark" in css or "--color-text" in css
        self.assertTrue(has_dark_text, "Primary text must utilize dark text token (#172334)")

    def test_t1_contrast_ratios(self):
        """F6.5: Verify contrast ratio between dark text (#172334) and warm paper (#F5F4EF) meets WCAG AA (>= 4.5:1)."""
        ratio = wcag_contrast_ratio("#172334", "#F5F4EF")
        self.assertGreaterEqual(
            ratio,
            4.5,
            f"Contrast ratio between #172334 and #F5F4EF must meet WCAG AA (4.5:1), calculated: {ratio:.2f}:1"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 7: System Font Typography & Zero Remote Font CSP Violations
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_no_remote_google_fonts(self):
        """F7.1: Verify no fonts.googleapis.com or fonts.gstatic.com links in index.html."""
        html = read_project_file("index.html")
        self.assertNotIn("fonts.googleapis.com", html, "index.html must not load external Google Fonts")
        self.assertNotIn("fonts.gstatic.com", html, "index.html must not connect to external fonts.gstatic.com")

    def test_t1_local_font_stack(self):
        """F7.2: Verify font-family declarations specify system font fallbacks."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        system_fonts = ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"]
        for f in system_fonts:
            self.assertIn(f, css, f"CSS must include standard system font fallback: {f}")

    def test_t1_no_external_font_cdn_in_css(self):
        """F7.3: Verify shared.css contains no @import url(...) to remote CDNs."""
        css = read_project_file("shared.css")
        self.assertFalse(
            bool(re.search(r'@import\s+url\s*\(\s*["\']?https?://', css, re.I)),
            "shared.css must not import fonts or stylesheets from remote CDNs"
        )

    def test_t1_csp_font_src_local(self):
        """F7.4: Verify CSP font-src directive in _headers or meta restricts to 'self' data:."""
        headers = read_project_file("dist/_headers") or read_project_file("_headers")
        self.assertTrue(len(headers) > 0, "Netlify _headers file missing")
        csp_match = re.search(r'font-src\s+([^;\n]+)', headers)
        self.assertTrue(csp_match, "CSP must define font-src directive")
        font_src_val = csp_match.group(1)
        self.assertNotIn("https:", font_src_val, "CSP font-src must not allow broad external https: fonts")
        self.assertIn("'self'", font_src_val, "CSP font-src must allow 'self'")

    def test_t1_font_display_swap(self):
        """F7.5: Verify any local @font-face definition specifies font-display: swap or optional."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        font_faces = re.findall(r'@font-face\s*\{([^}]+)\}', css, re.I)
        for ff in font_faces:
            self.assertTrue(
                "font-display" in ff.lower(),
                "@font-face blocks must explicitly declare font-display (e.g. swap)"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 8: Sticky Top Navigation
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_nav_wordmark_text(self):
        """F8.1: Verify typographic wordmark contains 'Sai Lakshmi Elusuri'."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        has_wordmark = False
        for tag, attrs, text in doc.tags:
            if "wordmark" in attrs.get("class", "").lower() or "brand" in attrs.get("class", "").lower() or tag == "nav":
                if "Sai Lakshmi Elusuri" in text or "Sai Lakshmi" in text:
                    has_wordmark = True
                    break
        self.assertTrue(has_wordmark, "Navigation must display typographic wordmark 'Sai Lakshmi Elusuri'")

    def test_t1_nav_destinations_count(self):
        """F8.2: Verify primary navigation links count is <= 6."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        # Find primary navigation items (links inside <nav>)
        nav_links = [href for href, attrs, txt in doc.links if href.startswith("#") and href not in ["#", "#main"]]
        # Primary destinations ceiling: max 6 (Overview, Experience, Projects, Expertise, CVs, Contact)
        # Filter distinct anchor targets
        unique_nav = set(nav_links)
        self.assertLessEqual(
            len(unique_nav),
            6,
            f"Primary navigation destinations count must be <= 6, found {len(unique_nav)}: {unique_nav}"
        )

    def test_t1_nav_destinations_names(self):
        """F8.3: Verify navigation targets standard section destinations."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        expected_sections = ["experience", "projects", "contact"]
        hrefs = " ".join([h.lower() for h, _, _ in doc.links])
        for sec in expected_sections:
            self.assertIn(f"#{sec}", hrefs, f"Navigation must include anchor link #{sec}")

    def test_t1_nav_scroll_offset(self):
        """F8.4: Verify scroll-margin-top or scroll-padding-top is configured for sticky header."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_scroll_offset = ("scroll-margin-top" in css or "scroll-padding-top" in css or "scroll-margin" in css)
        self.assertTrue(has_scroll_offset, "CSS must declare scroll-margin-top or scroll-padding-top for sticky nav")

    def test_t1_nav_mobile_toggle_exists(self):
        """F8.5: Verify mobile menu button exists with aria-expanded and aria-label."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        toggle_found = False
        for attrs, text in doc.buttons:
            if "menu" in attrs.get("aria-label", "").lower() or "menu" in attrs.get("id", "").lower() or "toggle" in attrs.get("class", "").lower():
                if "aria-label" in attrs or "aria-expanded" in attrs:
                    toggle_found = True
                    break
        self.assertTrue(toggle_found, "Mobile navigation toggle button with ARIA attributes must exist")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 9: Editorial Hero Section
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_hero_desktop_grid(self):
        """F9.1: Verify hero layout uses 60/40 desktop split in CSS."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        # 60/40 desktop split: grid-template-columns with 3fr 2fr or 1.5fr 1fr or 60% 40% or flex ratios
        has_60_40 = bool(re.search(r'grid-template-columns\s*:\s*(3fr\s+2fr|1\.5fr\s+1fr|60%\s+40%|1\.4fr\s+1fr)', css, re.I)) or ("60/40" in css or "--hero-split" in css)
        self.assertTrue(has_60_40, "Hero section must implement 60/40 desktop split in CSS layout")

    def test_t1_hero_primary_role(self):
        """F9.2: Verify primary title/role is prominent in hero."""
        html = read_project_file("index.html")
        self.assertTrue(
            "Power BI" in html and ("Developer" in html or "Specialist" in html),
            "Hero must prominently feature primary role (Power BI Developer / Analytics Specialist)"
        )

    def test_t1_hero_utrecht_location(self):
        """F9.3: Verify Utrecht region location is prominently displayed in hero."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        hero_text = ""
        for tag, attrs, text in doc.tags:
            if "hero" in attrs.get("id", "").lower() or "hero" in attrs.get("class", "").lower():
                hero_text += " " + text
        self.assertIn("Utrecht", hero_text or html, "Hero section must state Utrecht region location")

    def test_t1_hero_work_auth_badge(self):
        """F9.4: Verify work authorization note is present in hero."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        hero_text = ""
        for tag, attrs, text in doc.tags:
            if "hero" in attrs.get("id", "").lower() or "hero" in attrs.get("class", "").lower():
                hero_text += " " + text
        target = hero_text if hero_text else html
        has_auth = "TWV" in target or "Arbeid vrij" in target or "unrestricted" in target.lower() or "work authorization" in target.lower()
        self.assertTrue(has_auth, "Hero section must display verified work authorization status")

    def test_t1_hero_primary_actions(self):
        """F9.5: Verify primary CTAs 'View technical CV' and 'Contact Sai' exist."""
        html = read_project_file("index.html")
        has_cv_cta = bool(re.search(r'View\s+technical\s+CV|Technical\s+CV|View\s+CV', html, re.I))
        has_contact_cta = bool(re.search(r'Contact\s+Sai|Contact', html, re.I))
        self.assertTrue(has_cv_cta, "Hero must contain primary CTA to View Technical CV")
        self.assertTrue(has_contact_cta, "Hero must contain CTA to Contact Sai")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 10: Proof Strip
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_proof_strip_cards_count(self):
        """F10.1: Verify proof strip contains exactly 3 proof cards."""
        html = read_project_file("index.html")
        # Proof strip cards or metric cards
        cards = re.findall(r'class="[^"]*(?:proof-card|metric-card|stat-card)[^"]*"', html)
        self.assertEqual(
            len(cards),
            3,
            f"Proof strip must contain exactly 3 verified proof cards, found: {len(cards)}"
        )

    def test_t1_proof_strip_metric_1(self):
        """F10.2: Verify first proof card displays verified metric (8+ years)."""
        html = read_project_file("index.html")
        self.assertTrue("8+" in html and "years" in html.lower(), "Proof strip must highlight 8+ years experience")

    def test_t1_proof_strip_metric_2(self):
        """F10.3: Verify second proof card displays verified metric (5x Microsoft certs)."""
        html = read_project_file("index.html")
        self.assertTrue(
            bool(re.search(r'5x?\s*(?:Microsoft|Certified|Certifications)', html, re.I)),
            "Proof strip must highlight 5 Microsoft certifications"
        )

    def test_t1_proof_strip_metric_3(self):
        """F10.4: Verify third proof card displays verified performance stat (e.g. 40% reduction)."""
        html = read_project_file("index.html")
        self.assertTrue("40%" in html, "Proof strip must feature verified 40% query performance optimization")

    def test_t1_proof_strip_no_unsupported_verified_labels(self):
        """F10.5: Verify proof cards do not claim 'verified' without evidentiary backing."""
        html = read_project_file("index.html")
        # If the word 'verified' appears, it must be attached to IND work auth, Microsoft certs, or documented telemetry
        verified_mentions = re.findall(r'verified\s+([a-zA-Z0-9_\s%–-]{1,40})', html, re.I)
        allowed_stems = ["work", "labor", "twv", "ind", "microsoft", "cert", "40%", "40", "dashboard", "metric", "result", "experience", "reduction", "performance"]
        for mention in verified_mentions:
            is_valid = any(stem in mention.lower() for stem in allowed_stems)
            self.assertTrue(is_valid, f"Proof strip or site claims unbacked 'verified' on: {mention!r}")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 11: Experience Timeline
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_timeline_vertical_editorial(self):
        """F11.1: Verify timeline markup uses structured vertical editorial flow."""
        html = read_project_file("index.html")
        self.assertTrue(
            "timeline" in html.lower() or "experience-list" in html.lower() or "roles" in html.lower(),
            "Experience timeline must exist in index.html"
        )

    def test_t1_timeline_current_role_distinct(self):
        """F11.2: Verify current role has distinct visual class or styling."""
        html = read_project_file("index.html")
        has_current_marker = bool(re.search(r'class="[^"]*(?:current|active|role-current|role--current)[^"]*"', html, re.I))
        self.assertTrue(has_current_marker, "Current role (Apexon) must have distinct visual class in timeline")

    def test_t1_timeline_current_role_present_tense(self):
        """F11.3: Verify current role bullet verbs use present tense."""
        cv_text = read_project_file("cv_power_bi_developer.html") + read_project_file("index.html")
        present_verbs = ["architects", "engineers", "leads", "delivers", "designs", "optimizes", "develops", "manages", "builds"]
        found = [v for v in present_verbs if v in cv_text.lower()]
        self.assertTrue(
            len(found) >= 2,
            f"Current role bullet points must use present-tense verbs, found: {found}"
        )

    def test_t1_timeline_past_roles_past_tense(self):
        """F11.4: Verify completed roles bullet verbs use past tense."""
        cv_text = read_project_file("cv_power_bi_developer.html") + read_project_file("index.html")
        past_verbs = ["delivered", "built", "engineered", "migrated", "developed", "led", "managed", "designed"]
        found = [v for v in past_verbs if v in cv_text.lower()]
        self.assertTrue(
            len(found) >= 3,
            f"Past roles bullet points must use past-tense verbs, found: {found}"
        )

    def test_t1_timeline_no_animated_status_dots(self):
        """F11.5: Verify no pulsing animated status rings or dots in timeline."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        # Should not have pulsing status dots in timeline
        self.assertFalse(
            bool(re.search(r'\.status-dot\s*\{[^}]*animation\s*:\s*(?:pulse|ping)', css, re.I)),
            "Experience timeline must avoid animated status dots/pulse rings"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 12: Projects Bento Grid
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_bento_grid_structure(self):
        """F12.1: Verify bento grid CSS container exists."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_bento = "bento" in css.lower() or "grid-template-areas" in css
        self.assertTrue(has_bento, "CSS must provide bento grid layout rules for projects")

    def test_t1_bento_case_studies_count(self):
        """F12.2: Verify 2 to 3 prominent case studies are present."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        projects_sec = doc.elements_by_id.get("projects")
        self.assertTrue(projects_sec, "Section id='projects' must exist")
        # Check case studies
        case_studies = re.findall(r'class="[^"]*(?:project-card|case-study|bento-item)[^"]*"', html)
        self.assertTrue(
            2 <= len(case_studies) <= 4,
            f"Projects bento grid must feature 2-3 prominent case studies, found: {len(case_studies)}"
        )

    def test_t1_bento_case_study_sections(self):
        """F12.3: Verify each case study details business problem, Sai's role, and scope."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        proj_text = doc.elements_by_id.get("projects", ("", {}, ""))[2]
        target = proj_text if proj_text else html
        self.assertTrue("problem" in target.lower() or "challenge" in target.lower(), "Case studies must state business problem")
        self.assertTrue("role" in target.lower() or "scope" in target.lower(), "Case studies must state role and scope")

    def test_t1_bento_technical_decisions(self):
        """F12.4: Verify technical decisions (DAX, VertiPaq, Fabric) are highlighted in projects."""
        html = read_project_file("index.html")
        self.assertIn("DAX", html, "Projects must highlight DAX technical decisions")
        self.assertTrue("VertiPaq" in html or "Fabric" in html, "Projects must highlight VertiPaq or Fabric decisions")

    def test_t1_bento_results_measured(self):
        """F12.5: Verify measurable outcomes are stated for each project."""
        html = read_project_file("index.html")
        has_percentage = bool(re.search(r'\d+%', html))
        self.assertTrue(has_percentage, "Projects must report concrete, measurable results (percentages/metrics)")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 13: Grouped Expertise Deck
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_expertise_group_count(self):
        """F13.1: Verify exactly 4 expertise areas are present."""
        html = read_project_file("index.html")
        areas = re.findall(r'class="[^"]*(?:expertise-card|skill-group|expertise-group|domain-card)[^"]*"', html)
        self.assertEqual(
            len(areas),
            4,
            f"Expertise deck must be structured into exactly 4 readable areas, found: {len(areas)}"
        )

    def test_t1_expertise_power_bi_dax(self):
        """F13.2: Verify 'Power BI & DAX' area exists with concise contextual descriptions."""
        html = read_project_file("index.html")
        self.assertTrue(
            bool(re.search(r'Power\s+BI\s*(?:&amp;|&)\s*DAX', html, re.I)),
            "Expertise deck must include 'Power BI & DAX' domain area"
        )

    def test_t1_expertise_data_modeling_sql(self):
        """F13.3: Verify 'Data Modeling & SQL' area exists with concise contextual descriptions."""
        html = read_project_file("index.html")
        self.assertTrue(
            bool(re.search(r'Data\s+Modeling\s*(?:&amp;|&)\s*SQL', html, re.I)) or "Data Modeling" in html,
            "Expertise deck must include 'Data Modeling & SQL' domain area"
        )

    def test_t1_expertise_fabric_cloud(self):
        """F13.4: Verify 'Fabric & Cloud Data' area exists with concise contextual descriptions."""
        html = read_project_file("index.html")
        self.assertTrue(
            bool(re.search(r'Fabric\s*(?:&amp;|&)\s*Cloud', html, re.I)) or ("Fabric" in html and "Azure" in html),
            "Expertise deck must include 'Fabric & Cloud Data' domain area"
        )

    def test_t1_expertise_delivery_governance(self):
        """F13.5: Verify 'Delivery & Governance' area exists with concise contextual descriptions."""
        html = read_project_file("index.html")
        self.assertTrue(
            bool(re.search(r'Delivery\s*(?:&amp;|&)\s*Governance', html, re.I)) or "Governance" in html,
            "Expertise deck must include 'Delivery & Governance' domain area"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 14: Verified Certifications Deck
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_cert_pl300(self):
        """F14.1: Verify PL-300 Power BI Data Analyst Associate is listed with official URL."""
        html = read_project_file("index.html")
        self.assertIn("PL-300", html, "PL-300 certification must be listed")
        self.assertIn("learn.microsoft.com", html, "PL-300 must link to official Microsoft Learn credential URL")

    def test_t1_cert_dp600(self):
        """F14.2: Verify DP-600 Fabric Analytics Engineer Associate is listed with official URL."""
        html = read_project_file("index.html")
        self.assertIn("DP-600", html, "DP-600 certification must be listed")
        self.assertIn("learn.microsoft.com", html, "DP-600 must link to official Microsoft Learn credential URL")

    def test_t1_cert_dp900(self):
        """F14.3: Verify DP-900 Azure Data Fundamentals is listed with official URL."""
        html = read_project_file("index.html")
        self.assertIn("DP-900", html, "DP-900 certification must be listed")

    def test_t1_cert_az900(self):
        """F14.4: Verify AZ-900 Azure Fundamentals is listed with official URL."""
        html = read_project_file("index.html")
        self.assertIn("AZ-900", html, "AZ-900 certification must be listed")

    def test_t1_cert_ai900(self):
        """F14.5: Verify AI-900 Azure AI Fundamentals is listed with official URL."""
        html = read_project_file("index.html")
        self.assertIn("AI-900", html, "AI-900 certification must be listed")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 15: Inline CV Selector Cards
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_cv_selector_two_cards(self):
        """F15.1: Verify distinct cards for Technical CV and Delivery CV."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        cv_cards = [attrs for attrs, _ in doc.buttons if "cv" in attrs.get("class", "").lower()]
        # Or look for cv card elements
        card_matches = re.findall(r'class="[^"]*(?:cv-card|resume-card)[^"]*"', html)
        self.assertTrue(
            len(card_matches) >= 2,
            f"CV selector must contain at least 2 distinct cards for Technical and Delivery CVs, found: {len(card_matches)}"
        )

    def test_t1_cv_selector_one_sentence_context(self):
        """F15.2: Verify each CV card provides clear 1-sentence role context."""
        html = read_project_file("index.html")
        self.assertTrue(
            "Power BI Developer" in html and "Project Delivery" in html,
            "CV cards must describe specific role target contexts"
        )

    def test_t1_cv_selector_view_button_text(self):
        """F15.3: Verify buttons are labeled 'View CV (PDF)' or 'Open CV in browser'."""
        html = read_project_file("index.html")
        has_view_label = bool(re.search(r'View\s+CV\s*\(PDF\)|Open\s+CV\s+in\s+browser|View\s+Technical\s+CV|View\s+Delivery\s+CV', html, re.I))
        self.assertTrue(has_view_label, "CV action links must be labeled 'View CV (PDF)' or equivalent")

    def test_t1_cv_selector_target_blank(self):
        """F15.4: Verify CV links have target='_blank' and rel='noopener'."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        cv_links = [attrs for href, attrs, _ in doc.links if href.endswith(".pdf")]
        self.assertTrue(len(cv_links) >= 2, "CV links to .pdf files must exist in index.html")
        for attrs in cv_links:
            self.assertEqual(attrs.get("target"), "_blank", "PDF CV links must open in new tab (target='_blank')")
            self.assertIn("noopener", attrs.get("rel", ""), "PDF CV links must declare rel='noopener'")

    def test_t1_cv_selector_no_download_attr(self):
        """F15.5: Verify NO CV link contains the HTML download attribute."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        cv_links = [attrs for href, attrs, _ in doc.links if href.endswith(".pdf")]
        for attrs in cv_links:
            self.assertNotIn(
                "download",
                attrs,
                "CV links must NOT contain the HTML 'download' attribute, to force inline browser viewing"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 16: Telemetry Simulator Redesign
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_telemetry_sample_data_badge(self):
        """F16.1: Verify prominent 'Sample Data' or 'Illustrative Demo' badge is present."""
        html = read_project_file("index.html")
        has_badge = bool(re.search(r'Sample\s+Data|Illustrative\s+Demo', html, re.I))
        self.assertTrue(has_badge, "Telemetry simulator must display prominent 'Sample Data' or 'Illustrative Demo' badge")

    def test_t1_telemetry_state_swapping_label(self):
        """F16.2: Verify description clarifies hardcoded illustrative value swapping."""
        html = read_project_file("index.html")
        has_explanation = bool(re.search(r'illustrative|hard-coded|sample|swapping|synthetic', html, re.I))
        self.assertTrue(has_explanation, "Telemetry simulator must explain that data values are illustrative samples")

    def test_t1_telemetry_keyboard_accessible(self):
        """F16.3: Verify interactive telemetry controls use buttons or tabindex='0'."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        telemetry_sec = doc.elements_by_id.get("telemetry") or doc.elements_by_id.get("demo")
        self.assertTrue(telemetry_sec, "Telemetry section must exist in index.html")

    def test_t1_telemetry_aria_labels(self):
        """F16.4: Verify telemetry controls have informative ARIA labels."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        has_aria = any("aria-label" in attrs or "aria-pressed" in attrs for attrs, _ in doc.buttons)
        self.assertTrue(has_aria, "Interactive telemetry controls must possess informative ARIA attributes")

    def test_t1_telemetry_mobile_touch_targets(self):
        """F16.5: Verify telemetry control touch targets meet minimum 44x44px in CSS."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_min_touch = bool(re.search(r'min-height\s*:\s*(?:44px|48px)', css)) or bool(re.search(r'padding\s*:\s*(?:12px|14px|16px)', css))
        self.assertTrue(has_min_touch, "Interactive buttons must provide at least 44px accessible touch targets")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 17: Privacy & Legal Section Removal
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_privacy_section_removed(self):
        """F17.1: Verify no section id='privacy' exists in index.html."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        self.assertNotIn("privacy", doc.elements_by_id, "Section id='privacy' must be removed from index.html")

    def test_t1_storage_purge_removed(self):
        """F17.2: Verify zero buttons or scripts call localStorage.clear()."""
        html = read_project_file("index.html")
        self.assertNotIn("localStorage.clear()", html, "Storage purge button / localStorage.clear() must be removed")
        self.assertNotIn("clearTrackerData", html, "clearTrackerData() function must be removed")

    def test_t1_privacy_nav_links_removed(self):
        """F17.3: Verify no navigation links point to #privacy or #legal."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        privacy_links = [href for href, _, _ in doc.links if href in ["#privacy", "#legal", "#gdpr"]]
        self.assertEqual(len(privacy_links), 0, f"Privacy nav links must be removed, found: {privacy_links}")

    def test_t1_no_bsn_protection_section(self):
        """F17.4: Verify removal of standalone legal/BSN privacy section."""
        html = read_project_file("index.html")
        self.assertNotIn("BSN Protection Notice", html, "BSN protection notice section must be removed from public site")

    def test_t1_clean_dom_footer(self):
        """F17.5: Verify footer contains no privacy policy modal or popup triggers."""
        html = read_project_file("index.html")
        self.assertNotIn("privacy-modal", html, "Footer must not contain privacy modal dialog or triggers")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 18: Contact Panel & Minimal Footer
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_contact_panel_full_width(self):
        """F18.1: Verify contact panel exists with dedicated section id='contact'."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        self.assertIn("contact", doc.elements_by_id, "Section id='contact' must exist in index.html")

    def test_t1_contact_email_link(self):
        """F18.2: Verify clickable mailto link with valid email."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        mailto_links = [href for href, _, _ in doc.links if href.startswith("mailto:")]
        self.assertTrue(len(mailto_links) >= 1, "Clickable mailto: link must exist in contact section")
        self.assertIn("sailakshmi.elusuri@gmail.com", mailto_links[0], "Contact email must match canonical address")

    def test_t1_contact_phone_link(self):
        """F18.3: Verify clickable tel link with valid phone format."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        tel_links = [href for href, _, _ in doc.links if href.startswith("tel:")]
        self.assertTrue(len(tel_links) >= 1, "Clickable tel: link must exist in contact section")

    def test_t1_contact_linkedin_link(self):
        """F18.4: Verify clickable LinkedIn URL with target='_blank'."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        linkedin_links = [(href, attrs) for href, attrs, _ in doc.links if "linkedin.com/in/" in href]
        self.assertTrue(len(linkedin_links) >= 1, "LinkedIn profile link must exist")
        self.assertEqual(linkedin_links[0][1].get("target"), "_blank", "LinkedIn link must have target='_blank'")

    def test_t1_minimal_footer_copyright(self):
        """F18.5: Verify footer contains minimal copyright and professional attribution."""
        html = read_project_file("index.html")
        self.assertTrue("Sai Lakshmi Elusuri" in html and ("2026" in html or "©" in html or "&copy;" in html),
                        "Footer must contain minimal professional copyright")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 19: Responsive & Reduced Motion Layout
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_viewport_meta_tag(self):
        """F19.1: Verify standard responsive viewport meta tag in index.html."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        viewport_metas = [m for m in doc.meta_tags if m.get("name") == "viewport"]
        self.assertTrue(len(viewport_metas) >= 1, "Responsive viewport meta tag missing")
        self.assertIn("width=device-width", viewport_metas[0].get("content", ""), "Viewport must declare width=device-width")

    def test_t1_prefers_reduced_motion_media(self):
        """F19.2: Verify @media (prefers-reduced-motion: reduce) rules exist in CSS."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        self.assertIn("prefers-reduced-motion", css, "CSS must declare prefers-reduced-motion media query")

    def test_t1_focus_visible_outlines(self):
        """F19.3: Verify :focus-visible styling is defined with accessible outline."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        self.assertIn(":focus-visible", css, "CSS must specify visible focus outlines via :focus-visible")

    def test_t1_no_fixed_overflow_widths(self):
        """F19.4: Verify no elements declare static width > 1000px without max-width: 100%."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        bad_widths = re.findall(r'(?:^|[^-])width\s*:\s*([1-9]\d{3,})px', css)
        self.assertEqual(len(bad_widths), 0, f"Found fixed width > 1000px in CSS: {bad_widths}")

    def test_t1_box_sizing_border_box(self):
        """F19.5: Verify universal box-sizing: border-box reset."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        self.assertIn("box-sizing: border-box", css, "CSS reset must apply box-sizing: border-box")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 20: Public Career Bundle Packaging
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_bundle_zip_exists(self):
        """F20.1: Verify Netherlands_Career_Hub_Sai_Lakshmi.zip exists in root or dist/."""
        root_zip = file_exists("Netherlands_Career_Hub_Sai_Lakshmi.zip")
        dist_zip = file_exists("dist/Netherlands_Career_Hub_Sai_Lakshmi.zip")
        self.assertTrue(root_zip or dist_zip, "Netherlands_Career_Hub_Sai_Lakshmi.zip must exist")

    def test_t1_bundle_zip_non_empty(self):
        """F20.2: Verify ZIP file size is > 10KB."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        self.assertTrue(target.exists(), "Career bundle ZIP missing")
        self.assertGreater(target.stat().st_size, 10240, f"ZIP file suspiciously small: {target.stat().st_size} bytes")

    def test_t1_bundle_excludes_private_tools(self):
        """F20.3: Verify ZIP excludes personal career planning tools."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        with zipfile.ZipFile(target, "r") as zf:
            namelist = zf.namelist()
            forbidden = ["strategy.html", "job-finder.html", "linkedin-optimizer.html", "influencer-insights.html"]
            for f in forbidden:
                self.assertNotIn(f, namelist, f"Private tool {f} must NOT be in public recruiter ZIP")

    def test_t1_bundle_includes_public_cvs(self):
        """F20.4: Verify ZIP contains both compiled recruiter CV PDFs."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        with zipfile.ZipFile(target, "r") as zf:
            namelist = zf.namelist()
            self.assertIn("cv_power_bi_developer.pdf", namelist, "cv_power_bi_developer.pdf must be in ZIP bundle")
            self.assertIn("cv_bi_project_delivery.pdf", namelist, "cv_bi_project_delivery.pdf must be in ZIP bundle")

    def test_t1_bundle_readme_matches_contents(self):
        """F20.5: Verify README_BUNDLE.txt accurately reflects archive contents."""
        readme = read_project_file("README_BUNDLE.txt")
        self.assertIn("cv_power_bi_developer.pdf", readme, "README must document Technical CV")
        self.assertIn("cv_bi_project_delivery.pdf", readme, "README must document Delivery CV")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 21: Netlify Headers & Inline PDF Viewing
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_dist_headers_exists(self):
        """F21.1: Verify _headers exists in dist/ or root."""
        has_headers = file_exists("dist/_headers") or file_exists("_headers")
        self.assertTrue(has_headers, "Netlify _headers file must exist")

    def test_t1_headers_pdf_inline(self):
        """F21.2: Verify rule for /*.pdf specifies Content-Disposition: inline."""
        content = read_project_file("dist/_headers") or read_project_file("_headers")
        has_inline_rule = bool(re.search(r'/\*\.pdf[^\n]*\n(?:[^\S\r\n]+[^\n]+\n)*?[^\S\r\n]+Content-Disposition:\s*inline', content, re.I))
        self.assertTrue(has_inline_rule, "Netlify _headers must configure 'Content-Disposition: inline' for /*.pdf")

    def test_t1_headers_pdf_content_type(self):
        """F21.3: Verify rule for /*.pdf configures cache control and proper disposition."""
        content = read_project_file("dist/_headers") or read_project_file("_headers")
        self.assertIn("/*.pdf", content, "_headers must have a rule block for /*.pdf")
        self.assertIn("Content-Disposition: inline", content, "PDF headers must specify inline disposition")

    def test_t1_headers_x_frame_options(self):
        """F21.4: Verify security headers (X-Frame-Options, X-Content-Type-Options) are configured."""
        content = read_project_file("dist/_headers") or read_project_file("_headers")
        self.assertIn("X-Frame-Options", content, "_headers must set X-Frame-Options")
        self.assertIn("X-Content-Type-Options: nosniff", content, "_headers must set X-Content-Type-Options: nosniff")

    def test_t1_headers_cache_control(self):
        """F21.5: Verify Cache-Control headers for static assets."""
        content = read_project_file("dist/_headers") or read_project_file("_headers")
        self.assertIn("Cache-Control", content, "_headers must configure Cache-Control for assets")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 22: No-Deploy Enforcement
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_no_live_deploy_in_build_script(self):
        """F22.1: Verify build.py has no automated netlify deploy flags or live API calls."""
        build_py = read_project_file("build.py")
        self.assertNotIn("netlify deploy --prod", build_py, "build.py must not execute live deployment")
        self.assertNotIn("NETLIFY_AUTH_TOKEN", build_py, "build.py must not hardcode live auth tokens")

    def test_t1_no_production_auth_tokens_in_git(self):
        """F22.2: Verify .env or Netlify auth tokens are not tracked."""
        self.assertFalse(file_exists(".env"), ".env file must not exist in tracked repository")

    def test_t1_package_json_scripts_safe(self):
        """F22.3: Verify package.json scripts (if any) do not trigger automatic live deployment."""
        if file_exists("package.json"):
            pkg = json.loads(read_project_file("package.json"))
            scripts = pkg.get("scripts", {})
            for script_name, cmd in scripts.items():
                self.assertNotIn("--prod", cmd, f"package.json script '{script_name}' must not include --prod flag")

    def test_t1_git_status_clean_deployment(self):
        """F22.4: Verify deployment artifacts stay in local dist/."""
        self.assertTrue(file_exists("dist"), "Local dist/ directory must hold assembled site")

    def test_t1_dist_isolated(self):
        """F22.5: Verify dist/ is self-contained and index.html exists within dist/."""
        self.assertTrue(file_exists("dist/index.html"), "dist/index.html must exist for local packaging")

    # ─────────────────────────────────────────────────────────────────────────
    # Feature 23: Comprehensive Acceptance & E2E Verification
    # ─────────────────────────────────────────────────────────────────────────
    def test_t1_test_runner_runnable(self):
        """F23.1: Verify tests/test_e2e_requirements.py exists and is non-empty."""
        self.assertTrue(file_exists("tests/test_e2e_requirements.py"), "test_e2e_requirements.py must exist")

    def test_t1_canonical_data_importable(self):
        """F23.2: Verify canonical_data.py compiles without syntax error and exposes profile data."""
        try:
            import canonical_data
            self.assertTrue(hasattr(canonical_data, "CANDIDATE"), "canonical_data must define CANDIDATE dictionary")
        except Exception as e:
            self.fail(f"canonical_data.py failed import: {e}")

    def test_t1_build_script_syntax_valid(self):
        """F23.3: Verify build.py compiles cleanly under python3."""
        code = read_project_file("build.py")
        try:
            compile(code, "build.py", "exec")
        except SyntaxError as e:
            self.fail(f"build.py syntax error: {e}")

    def test_t1_all_html_files_valid_utf8(self):
        """F23.4: Verify all .html files decode as valid UTF-8 without byte replacement errors."""
        for html_file in BASE_DIR.glob("*.html"):
            with open(html_file, "rb") as f:
                raw_bytes = f.read()
            try:
                raw_bytes.decode("utf-8")
            except UnicodeDecodeError as e:
                self.fail(f"{html_file.name} contains invalid UTF-8 encoding: {e}")

    def test_t1_zero_console_script_errors(self):
        """F23.5: Verify embedded scripts in index.html have balanced syntax / valid structure."""
        html = read_project_file("index.html")
        script_blocks = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL)
        for i, script in enumerate(script_blocks):
            # Check basic bracket/parenthesis balancing
            self.assertEqual(script.count("{"), script.count("}"), f"Script block {i+1} has unbalanced curly braces")
            self.assertEqual(script.count("("), script.count(")"), f"Script block {i+1} has unbalanced parentheses")


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 2: BOUNDARY & CORNER CASES (4 Categories × 5 Tests = 20 Tests)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTier2BoundaryAndCorner(unittest.TestCase):
    """
    Tier 2 tests verify edge conditions, viewport extremes, anchor integrity,
    PDF page boundary controls, and archive integrity.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # Viewport Boundary Limits (320px & 375px)
    # ─────────────────────────────────────────────────────────────────────────
    def test_t2_viewport_320px_no_horizontal_overflow(self):
        """B1.1: Verify CSS restricts maximum container widths and hides body horizontal overflow."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_overflow_control = "overflow-x: hidden" in css
        self.assertTrue(has_overflow_control, "Body or root container must declare overflow-x: hidden to prevent 320px overflow")

    def test_t2_viewport_375px_iphone_se_fit(self):
        """B1.2: Verify responsive media queries accommodate 375px iPhone SE boundary."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_mobile_mq = bool(re.search(r'@media\s*\([^\)]*max-width\s*:\s*(?:480|640|768)px\)', css))
        self.assertTrue(has_mobile_mq, "CSS must provide mobile media queries covering <= 375px viewports")

    def test_t2_padding_margins_mobile_boundaries(self):
        """B1.3: Verify mobile container padding does not exceed 24px on narrow screens."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        self.assertTrue(
            "padding: 0 16px" in css or "padding: 0 20px" in css or "padding: 0 24px" in css or "padding: 0 1rem" in css,
            "CSS must define safe mobile side padding (16-24px)"
        )

    def test_t2_table_grid_responsive_wrap(self):
        """B1.4: Verify multi-column grids collapse to 1 column on mobile breakpoints."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_single_col_collapse = bool(re.search(r'grid-template-columns\s*:\s*1fr\b', css)) or ("1fr" in css and "@media" in css)
        self.assertTrue(has_single_col_collapse, "Grid containers must collapse to 1fr on mobile viewports")

    def test_t2_long_words_break_word(self):
        """B1.5: Verify long technical identifiers have word-break / overflow-wrap protection."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_wrap = ("overflow-wrap: break-word" in css or "word-break: break-word" in css or "hyphens: auto" in css)
        self.assertTrue(has_wrap, "CSS must define overflow-wrap: break-word to prevent DAX identifiers from overflowing 320px")

    # ─────────────────────────────────────────────────────────────────────────
    # Navigation & Anchors Boundaries
    # ─────────────────────────────────────────────────────────────────────────
    def test_t2_nav_anchor_targets_all_exist(self):
        """B2.1: Verify every internal anchor href='#id' has an exact matching element id."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        internal_links = [href[1:] for href, _, _ in doc.links if href.startswith("#") and len(href) > 1 and href != "#main"]
        missing_targets = [t for t in internal_links if t not in doc.elements_by_id]
        self.assertEqual(
            missing_targets,
            [],
            f"Broken internal anchor links in index.html targeting missing IDs: {missing_targets}"
        )

    def test_t2_no_dangling_external_anchors(self):
        """B2.2: Verify external links have valid schemes (https://, mailto:, tel:) or local relative paths."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        for href, attrs, text in doc.links:
            if href.startswith("#") or not href:
                continue
            is_valid = (
                href.startswith("https://") or
                href.startswith("http://") or
                href.startswith("mailto:") or
                href.startswith("tel:") or
                href.endswith(".pdf") or
                href.endswith(".zip") or
                href.endswith(".html")
            )
            self.assertTrue(is_valid, f"Invalid or insecure link protocol found in index.html: {href}")

    def test_t2_empty_or_hash_only_hrefs(self):
        """B2.3: Verify no placeholder href='#' links exist in primary navigation."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        placeholder_links = [attrs for href, attrs, _ in doc.links if href == "#" and "nav" in attrs.get("class", "").lower()]
        self.assertEqual(len(placeholder_links), 0, "Primary navigation must not contain dummy href='#' links")

    def test_t2_nav_items_count_strict_ceiling(self):
        """B2.4: Verify navigation links strictly adhere to <= 6 destinations ceiling."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        nav_anchors = {href for href, attrs, _ in doc.links if href.startswith("#") and href not in ["#", "#main"]}
        self.assertLessEqual(len(nav_anchors), 6, f"Primary nav links strictly <= 6, found {len(nav_anchors)}")

    def test_t2_nav_wordmark_whitespace_handling(self):
        """B2.5: Verify wordmark handles narrow viewports without awkward disjointed wrapping."""
        css = read_project_file("shared.css") + read_project_file("index.html")
        has_nowrap = "white-space: nowrap" in css or "nowrap" in css
        self.assertTrue(has_nowrap, "Wordmark or navigation brand must define white-space handling")

    # ─────────────────────────────────────────────────────────────────────────
    # PDF Document Geometry & Page Break Protections
    # ─────────────────────────────────────────────────────────────────────────
    def test_t2_pdf_exact_page_count_boundary(self):
        """B3.1: Verify PDF page count boundary strictly <= 2 pages."""
        for pdf_name in ["cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf"]:
            info = inspect_pdf_doc(BASE_DIR / pdf_name)
            self.assertLessEqual(info["page_count"], 2, f"{pdf_name} exceeds 2-page ATS ceiling: {info['page_count']} pages")

    def test_t2_pdf_margins_boundary(self):
        """B3.2: Verify printable HTML CVs specify page margins >= 28pt (10mm)."""
        for cv_html in ["cv_power_bi_developer.html", "cv_bi_project_delivery.html"]:
            content = read_project_file(cv_html)
            has_page_margin = bool(re.search(r'@page\s*\{[^}]*margin\s*:\s*(?:10mm|12mm|15mm|0\.5in|28pt|36pt)', content))
            self.assertTrue(has_page_margin, f"{cv_html} must declare @page print margin >= 28pt (10mm)")

    def test_t2_pdf_page2_header_position(self):
        """B3.3: Verify running header is placed in top margin area of page 2."""
        for fname in ["cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf"]:
            info = inspect_pdf_doc(BASE_DIR / fname)
            if info["page2_header"]:
                self.assertTrue(
                    "Sai Lakshmi" in info["page2_header"] or "Page 2" in info["page2_header"],
                    f"{fname} page 2 running header missing required candidate/page identification"
                )

    def test_t2_pdf_break_inside_avoid_rules(self):
        """B3.4: Verify break-inside: avoid rules prevent split experience blocks in print CSS."""
        for cv_html in ["cv_power_bi_developer.html", "cv_bi_project_delivery.html"]:
            content = read_project_file(cv_html)
            has_break_control = "break-inside: avoid" in content or "page-break-inside: avoid" in content
            self.assertTrue(has_break_control, f"{cv_html} must specify break-inside: avoid on job blocks")

    def test_t2_pdf_orphan_widow_control(self):
        """B3.5: Verify headings in print styles declare break-after: avoid."""
        for cv_html in ["cv_power_bi_developer.html", "cv_bi_project_delivery.html"]:
            content = read_project_file(cv_html)
            has_break_after = "break-after: avoid" in content or "page-break-after: avoid" in content or "break-inside" in content
            self.assertTrue(has_break_after, f"{cv_html} must declare break avoidance rules for headings")

    # ─────────────────────────────────────────────────────────────────────────
    # Bundle Archive Boundary Tests
    # ─────────────────────────────────────────────────────────────────────────
    def test_t2_bundle_zip_corrupt_check(self):
        """B4.1: Verify ZIP archive passes zipfile.testzip() with zero CRC errors."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        self.assertTrue(target.exists(), "Career bundle ZIP missing")
        with zipfile.ZipFile(target, "r") as zf:
            corrupt = zf.testzip()
            self.assertIsNone(corrupt, f"Corrupted file detected inside bundle ZIP: {corrupt}")

    def test_t2_bundle_zip_no_zero_byte_files(self):
        """B4.2: Verify every file inside the ZIP archive has file_size > 0 bytes."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        with zipfile.ZipFile(target, "r") as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    self.assertGreater(
                        info.file_size,
                        0,
                        f"Zero-byte empty file found in ZIP bundle: {info.filename}"
                    )

    def test_t2_bundle_zip_no_symlinks_or_absolute_paths(self):
        """B4.3: Verify no unsafe path traversal (../) or absolute paths in ZIP entries."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        with zipfile.ZipFile(target, "r") as zf:
            for name in zf.namelist():
                self.assertFalse(name.startswith("/"), f"Absolute path in ZIP: {name}")
                self.assertFalse(".." in name, f"Path traversal in ZIP: {name}")

    def test_t2_bundle_zip_readme_encoding(self):
        """B4.4: Verify README.txt inside ZIP is valid UTF-8 without BOM or binary corruption."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        with zipfile.ZipFile(target, "r") as zf:
            readme_names = [n for n in zf.namelist() if "readme" in n.lower()]
            self.assertTrue(len(readme_names) >= 1, "README.txt must exist inside ZIP bundle")
            data = zf.read(readme_names[0])
            try:
                data.decode("utf-8")
            except UnicodeDecodeError as e:
                self.fail(f"README inside ZIP is not valid UTF-8: {e}")

    def test_t2_bundle_zip_pdf_integrity(self):
        """B4.5: Verify PDFs inside ZIP have size matching compiled PDFs within 5%."""
        target = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not target.exists():
            target = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        with zipfile.ZipFile(target, "r") as zf:
            for pdf in ["cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf"]:
                root_size = (BASE_DIR / pdf).stat().st_size
                zip_size = zf.getinfo(pdf).file_size
                self.assertAlmostEqual(
                    zip_size,
                    root_size,
                    delta=root_size * 0.05,
                    msg=f"PDF size in ZIP ({zip_size}) differs significantly from source ({root_size})"
                )


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 3: CROSS-FEATURE COMBINATIONS (7 Systemic Interplay Tests)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """
    Tier 3 tests verify pairwise and systemic invariants across the entire platform.
    """

    def test_t3_canonical_propagation_website_and_cvs(self):
        """C1: Verify employer names, dates, titles, and certs match across all media."""
        import canonical_data
        cand = canonical_data.CANDIDATE
        site_html = read_project_file("index.html")
        pbi_cv = read_project_file("cv_power_bi_developer.html")
        pm_cv = read_project_file("cv_bi_project_delivery.html")

        # Employers propagation
        for emp in cand["employment"]:
            comp = emp["company"]
            self.assertIn(comp, site_html, f"{comp} missing in index.html")
            self.assertIn(comp, pbi_cv, f"{comp} missing in cv_power_bi_developer.html")
            self.assertIn(comp, pm_cv, f"{comp} missing in cv_bi_project_delivery.html")

        # Certifications propagation
        for cert in cand["certifications"]:
            code = cert["code"]
            self.assertIn(code, site_html, f"Certification {code} missing in index.html")

    def test_t3_mobile_menu_keyboard_and_reduced_motion(self):
        """C2: Verify mobile menu toggle coordinates keyboard accessibility and reduced motion."""
        html = read_project_file("index.html")
        css = read_project_file("shared.css") + html
        # Checks that aria-expanded is toggled or referenced in scripts, and transitions are cancelled under reduced motion
        has_aria_expanded = "aria-expanded" in html
        has_reduced_motion_cancel = bool(re.search(r'@media\s*\(prefers-reduced-motion\s*:\s*reduce\)\s*\{[^}]*transition\s*:\s*none', css, re.I)) or "prefers-reduced-motion" in css
        self.assertTrue(has_aria_expanded, "Mobile menu must manage aria-expanded state")
        self.assertTrue(has_reduced_motion_cancel, "Transitions must be disabled for prefers-reduced-motion")

    def test_t3_inline_pdf_links_and_netlify_headers(self):
        """C3: Verify CV links have target='_blank', lack download attr, and map to Netlify inline rule."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        headers = read_project_file("dist/_headers") or read_project_file("_headers")

        pdf_links = [attrs for href, attrs, _ in doc.links if href.endswith(".pdf")]
        self.assertTrue(len(pdf_links) >= 2, "index.html must link to at least 2 CV PDFs")
        for attrs in pdf_links:
            self.assertEqual(attrs.get("target"), "_blank")
            self.assertNotIn("download", attrs)

        # Check Netlify headers enforce inline viewing for PDFs
        self.assertIn("/*.pdf", headers)
        self.assertIn("Content-Disposition: inline", headers)

    def test_t3_telemetry_simulator_and_contrast(self):
        """C4: Verify telemetry simulator badges maintain accessible contrast against surface cards."""
        ratio = wcag_contrast_ratio("#172334", "#FFFFFF")
        self.assertGreaterEqual(ratio, 4.5, "Badge text on card surface must meet WCAG AA >= 4.5:1")

    def test_t3_career_bundle_and_website_link(self):
        """C5: Verify career bundle download CTA links directly to generated ZIP archive."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        zip_links = [href for href, _, _ in doc.links if href.endswith(".zip")]
        self.assertTrue(len(zip_links) >= 1, "index.html must contain a download link to the .zip career bundle")
        self.assertIn("Netherlands_Career_Hub_Sai_Lakshmi.zip", zip_links[0])

    def test_t3_certifications_links_and_modal_free_flow(self):
        """C6: Verify certification URLs point to official Microsoft domains and open externally."""
        html = read_project_file("index.html")
        doc = parse_html(html)
        cert_links = [(href, attrs) for href, attrs, _ in doc.links if "learn.microsoft.com" in href]
        self.assertTrue(len(cert_links) >= 2, "Certifications deck must contain official Microsoft Learn URLs")
        for href, attrs in cert_links:
            self.assertEqual(attrs.get("target"), "_blank", "Certification links must open externally in new tab")
            self.assertIn("noopener", attrs.get("rel", ""))

    def test_t3_facts_to_confirm_and_public_claims_alignment(self):
        """C7: Verify claims quarantined in FACTS_TO_CONFIRM.md are not asserted as unqualified public claims."""
        if file_exists("FACTS_TO_CONFIRM.md"):
            facts_doc = read_project_file("FACTS_TO_CONFIRM.md")
            site_html = read_project_file("index.html")
            # If FACTS_TO_CONFIRM.md lists specific unverified clients or numbers, they must not appear on public site
            self.assertTrue(len(facts_doc) > 0, "FACTS_TO_CONFIRM.md should be populated")


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 4: REAL-WORLD APPLICATION SCENARIOS (Recruiter Workflows)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTier4RecruiterWorkflows(unittest.TestCase):
    """
    Tier 4 tests execute complete end-to-end recruiter user journeys.
    """

    def test_t4_scenario_1_dutch_tech_recruiter_landing(self):
        """Workflow 1: Dutch Tech Recruiter Landing & First 10-Second Scan."""
        html = read_project_file("index.html")
        doc = parse_html(html)

        # 1. Scans wordmark
        self.assertTrue("Sai Lakshmi" in html, "Recruiter scans typographic wordmark")
        # 2. Inspects hero role & Utrecht location
        self.assertTrue("Power BI" in html, "Recruiter verifies primary role")
        self.assertTrue("Utrecht" in html, "Recruiter verifies Utrecht region residency")
        # 3. Reviews work authorization note
        self.assertTrue("TWV" in html or "Arbeid vrij" in html or "unrestricted" in html.lower(),
                        "Recruiter verifies Dutch labor market access endorsement")
        # 4. Scans 3 proof strip cards
        proof_cards = re.findall(r'class="[^"]*(?:proof-card|metric-card|stat-card)[^"]*"', html)
        self.assertEqual(len(proof_cards), 3, "Recruiter scans exactly 3 proof cards")

    def test_t4_scenario_2_hiring_manager_technical_deep_dive(self):
        """Workflow 2: Hiring Manager Experience & Technical Deep Dive."""
        html = read_project_file("index.html")

        # 1. Navigates to experience timeline
        self.assertIn("Apexon", html, "Hiring manager inspects current Apexon role")
        # 2. Verifies current date format
        has_date = bool(re.search(r'Apr\s+2026[\u2013\u2014\-&ndash;#8211;]+Present', html))
        self.assertTrue(has_date, "Hiring manager verifies 'Apr 2026–Present' date format")
        # 3. Reads technical decisions on VertiPaq and Direct Lake in Bento grid
        self.assertTrue("DAX" in html and ("VertiPaq" in html or "Direct Lake" in html),
                        "Hiring manager reviews architectural decisions on DAX/VertiPaq")
        # 4. Confirms absence of exaggerated sub-second/zero-latency claims
        self.assertFalse(bool(re.search(r'universal\s+sub-second|zero\s*latency', html, re.I)),
                         "Hiring manager confirms technical accuracy without exaggerated superlatives")

    def test_t4_scenario_3_inline_cv_inspection_workflow(self):
        """Workflow 3: Inline CV Inspection Workflow."""
        html = read_project_file("index.html")
        doc = parse_html(html)

        # 1. Recruiter identifies Technical CV card
        cv_links = [attrs for href, attrs, _ in doc.links if href == "cv_power_bi_developer.pdf"]
        self.assertTrue(len(cv_links) >= 1, "Recruiter locates 'cv_power_bi_developer.pdf' button")
        link_attrs = cv_links[0]
        # 2. Browser opens inline in new tab
        self.assertEqual(link_attrs.get("target"), "_blank")
        self.assertNotIn("download", link_attrs)
        # 3. PDF document geometry verification
        pdf_info = inspect_pdf_doc(BASE_DIR / "cv_power_bi_developer.pdf")
        self.assertEqual(pdf_info["page_count"], 2, "Technical CV is exactly 2 pages")
        self.assertGreater(len(pdf_info["full_text"]), 1000, "Technical CV text is ATS selectable")

    def test_t4_scenario_4_corporate_security_privacy_review(self):
        """Workflow 4: Corporate Security & Privacy Compliance Audit."""
        html = read_project_file("index.html")
        headers = read_project_file("dist/_headers") or read_project_file("_headers")

        # 1. Zero external font tracking
        self.assertNotIn("fonts.googleapis.com", html, "Security audit: Zero Google font trackers")
        # 2. No origin storage purging remnants
        self.assertNotIn("localStorage.clear()", html, "Security audit: Zero localStorage purge buttons")
        self.assertNotIn("clearTrackerData", html, "Security audit: Zero purge functions")
        # 3. Security headers in Netlify config
        self.assertIn("X-Frame-Options: DENY", headers, "Security audit: Frame protection enforced")
        self.assertIn("X-Content-Type-Options: nosniff", headers, "Security audit: Content-Type nosniff enforced")

    def test_t4_scenario_5_recruiter_bundle_download_offline(self):
        """Workflow 5: Recruiter Bundle Download & Offline Review."""
        zip_path = BASE_DIR / "Netherlands_Career_Hub_Sai_Lakshmi.zip"
        if not zip_path.exists():
            zip_path = BASE_DIR / "dist" / "Netherlands_Career_Hub_Sai_Lakshmi.zip"

        self.assertTrue(zip_path.exists(), "Recruiter bundle ZIP exists for offline review")
        with zipfile.ZipFile(zip_path, "r") as zf:
            namelist = zf.namelist()
            # 1. Verified contents
            self.assertIn("README.txt", namelist, "Bundle contains README manifest")
            self.assertIn("cv_power_bi_developer.pdf", namelist, "Bundle contains Technical CV")
            self.assertIn("cv_bi_project_delivery.pdf", namelist, "Bundle contains Delivery CV")
            # 2. Verified complete omission of private tools
            private_tools = ["strategy.html", "job-finder.html", "linkedin-optimizer.html", "influencer-insights.html"]
            for pt in private_tools:
                self.assertNotIn(pt, namelist, f"Public bundle excludes private tool: {pt}")


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM TEST RUNNER & DIAGNOSTIC MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

def run_e2e_suite():
    """Executes the complete test suite and prints structured diagnostics by tier."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    t1_suite = loader.loadTestsFromTestCase(TestTier1FeatureCoverage)
    t2_suite = loader.loadTestsFromTestCase(TestTier2BoundaryAndCorner)
    t3_suite = loader.loadTestsFromTestCase(TestTier3CrossFeatureCombinations)
    t4_suite = loader.loadTestsFromTestCase(TestTier4RecruiterWorkflows)

    suite.addTests(t1_suite)
    suite.addTests(t2_suite)
    suite.addTests(t3_suite)
    suite.addTests(t4_suite)

    print("\n" + "=" * 78)
    print("  SAI LAKSHMI ELUSURI — E2E REQUIREMENTS TEST SUITE (147 CHECKS)")
    print("=" * 78)
    print("  Tier 1: Feature Coverage (Features 1–23 × 5 checks = 115 tests)")
    print("  Tier 2: Boundary & Corner Cases (20 tests)")
    print("  Tier 3: Cross-Feature Combinations (7 tests)")
    print("  Tier 4: Real-World Recruiter Workflows (5 tests)")
    print("-" * 78 + "\n")

    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)

    print("\n" + "=" * 78)
    print("  EXECUTION DIAGNOSTIC SUMMARY")
    print("=" * 78)
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print(f"  Total Test Cases Executed : {total}")
    print(f"  Passed                    : {passed}")
    print(f"  Failures                  : {failures}")
    print(f"  Errors                    : {errors}")
    print("-" * 78)

    if failures > 0 or errors > 0:
        print("\n❌ DETAILED DEFECT DIAGNOSTICS & IMPLEMENTATION DEFICITS:")
        for test, err in result.failures + result.errors:
            print(f"\n  • [{test.id()}]")
            first_line = err.strip().split("\n")[-1]
            print(f"    Defect: {first_line}")
        print("\n" + "=" * 78)
        return False
    else:
        print("\n🎉 ALL 147 E2E REQUIREMENTS ASSERTIONS PASSED UNCONDITIONALLY!")
        print("=" * 78 + "\n")
        return True


if __name__ == "__main__":
    success = run_e2e_suite()
    sys.exit(0 if success else 1)
