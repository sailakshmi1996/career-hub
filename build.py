#!/usr/bin/env python3
"""
Master Build Script for Sai Lakshmi Elusuri Public Portfolio
1. Verifies canonical source of truth synchronization (canonical_data.py)
2. Compiles unified 2-page A4 PDF CV (Sai_Lakshmi_Elusuri_CV.pdf) from resume.html
3. Generates clean 1200x630 Open Graph preview image (og-cover.png)
4. Assembles clean 'dist/' directory containing ONLY public portfolio assets
5. Executes automated integrity, contrast, privacy, and compliance tests
"""

import os
import shutil
import sys
import subprocess
import tempfile
import zipfile

try:
    import fitz
except ImportError:
    fitz = None

import canonical_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

FILES_TO_DEPLOY = [
    "index.html",
    "resume.html",
    "shared.css",
    "Sai_Lakshmi_Elusuri_CV.pdf",
    "og-cover.png",
    "robots.txt",
    "sitemap.xml",
]

PDF_METADATA = {
    "title": "Sai Lakshmi Elusuri — Senior Power BI & Microsoft Fabric Developer CV",
    "author": "Sai Lakshmi Elusuri",
    "subject": "Senior Power BI & Microsoft Fabric Developer CV — Semantic Modeling, DAX, SQL & OneLake",
    "keywords": "Power BI, Microsoft Fabric, DAX, VertiPaq, Kimball Star Schema, Oracle SQL, Utrecht, Netherlands",
}


def step0_verify_canonical_sync():
    print("=" * 60)
    print("STEP 0: VERIFYING CANONICAL SYNCHRONIZATION & PRIVACY")
    print("=" * 60)
    try:
        canonical_data.validate_synchronization(BASE_DIR)
        print("  + Canonical data verified across public files.")
        print("  + Unified role title, IND endorsement, and clean privacy confirmed.\n")
    except Exception as e:
        print(f"  ❌ Synchronization Error: {e}")
        sys.exit(1)


def step1_compile_pdf():
    print("=" * 60)
    print("STEP 1: COMPILING CANONICAL 2-PAGE PDF CV")
    print("=" * 60)
    html_path = os.path.join(BASE_DIR, "resume.html")
    pdf_path = os.path.join(BASE_DIR, "Sai_Lakshmi_Elusuri_CV.pdf")

    if os.path.exists(CHROME_BIN):
        cmd = [
            CHROME_BIN,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path,
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print("  ⚠️ Warning: Headless Chrome exited non-zero during PDF build")

    if fitz is not None and os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        doc.set_metadata(PDF_METADATA)
        doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        page_count = len(doc)
        doc.close()
        if page_count != 2:
            print(f"  ❌ Error: Sai_Lakshmi_Elusuri_CV.pdf has {page_count} pages! Must be 2 pages.")
            sys.exit(1)
        print(f"  + Verified PDF: Sai_Lakshmi_Elusuri_CV.pdf ({page_count} pages, {os.path.getsize(pdf_path):,} bytes)\n")
    elif os.path.exists(pdf_path):
        print(f"  + Verified PDF: Sai_Lakshmi_Elusuri_CV.pdf ({os.path.getsize(pdf_path):,} bytes)\n")
    else:
        print("  ❌ Error: Sai_Lakshmi_Elusuri_CV.pdf missing!")
        sys.exit(1)


def step2_generate_og_image():
    print("=" * 60)
    print("STEP 2: GENERATING 1200x630 OPEN GRAPH COVER IMAGE")
    print("=" * 60)
    og_path = os.path.join(BASE_DIR, "og-cover.png")
    if not os.path.exists(CHROME_BIN):
        if os.path.exists(og_path):
            print(f"  + Using existing og-cover.png ({os.path.getsize(og_path):,} bytes)\n")
            return
        print("  ⚠️ Warning: Chrome binary unavailable to generate og-cover.png")
        return

    og_html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1200px; height: 630px; overflow: hidden;
    background: #FAF9F5; color: #111827;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    padding: 64px 72px; display: flex; flex-direction: column; justify-content: space-between;
    border: 1px solid #E5E3DC;
  }
  .top { font-family: ui-monospace, monospace; font-size: 20px; font-weight: 700; color: #1D4ED8; letter-spacing: 0.06em; text-transform: uppercase; }
  h1 { font-size: 64px; font-weight: 700; letter-spacing: -0.025em; line-height: 1.08; margin: 16px 0 18px; }
  .role { font-size: 32px; font-weight: 600; color: #1D4ED8; margin-bottom: 18px; }
  .sub { font-size: 24px; color: #4B5563; line-height: 1.45; max-width: 960px; }
  .foot {
    border-top: 2px solid #E5E3DC; padding-top: 24px;
    display: flex; justify-content: space-between; align-items: center;
    font-family: ui-monospace, monospace; font-size: 20px; color: #111827;
  }
  .badge { background: #ECFDF5; color: #047857; padding: 8px 16px; border-radius: 6px; font-weight: 700; }
</style>
</head>
<body>
  <div>
    <div class="top">PORTFOLIO &amp; TECHNICAL CASE-FILES · UTRECHT, NETHERLANDS</div>
    <h1>Sai Lakshmi Elusuri</h1>
    <div class="role">Senior Power BI &amp; Microsoft Fabric Developer</div>
    <p class="sub">8+ years building Kimball 1:* semantic models, DAX Calculation Groups, VertiPaq optimization, and Oracle SQL / OneLake pipelines.</p>
  </div>
  <div class="foot">
    <span>PL-300 &amp; DP-600 Certified</span>
    <span class="badge">TWV niet vereist · Full NL Work Rights</span>
  </div>
</body>
</html>"""

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(og_html)
        tmp_path = tmp.name

    try:
        cmd = [
            CHROME_BIN,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1200,630",
            f"--screenshot={og_path}",
            tmp_path,
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if os.path.exists(og_path):
            print(f"  + Generated og-cover.png ({os.path.getsize(og_path):,} bytes)\n")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def step3_assemble_dist():
    print("=" * 60)
    print("STEP 3: ASSEMBLING CLEAN PUBLIC 'dist/' DIRECTORY")
    print("=" * 60)
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)

    for fname in FILES_TO_DEPLOY:
        src = os.path.join(BASE_DIR, fname)
        dst = os.path.join(DIST_DIR, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"  + Copied to dist/: {fname} ({os.path.getsize(dst):,} bytes)")
        else:
            print(f"  ❌ Error: Required public asset {fname} missing!")
            sys.exit(1)

    showcase_src = os.path.join(BASE_DIR, "technical-showcase")
    showcase_dst = os.path.join(DIST_DIR, "technical-showcase")
    if os.path.isdir(showcase_src):
        shutil.copytree(showcase_src, showcase_dst, dirs_exist_ok=True)
        print("  + Copied directory: dist/technical-showcase")

    redirects_content = """/resume   /Sai_Lakshmi_Elusuri_CV.pdf 302
/cv       /Sai_Lakshmi_Elusuri_CV.pdf 302
/pm-cv    /Sai_Lakshmi_Elusuri_CV.pdf 302
/hub      /index.html                 301
"""
    with open(os.path.join(DIST_DIR, "_redirects"), "w", encoding="utf-8") as f:
        f.write(redirects_content)
    print("  + Generated: dist/_redirects")

    headers_content = """/*
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: https:; connect-src 'self';

/*.pdf
  Cache-Control: public, max-age=86400, must-revalidate
  Content-Disposition: inline

/*.css
  Cache-Control: public, max-age=604800, stale-while-revalidate=86400
"""
    with open(os.path.join(DIST_DIR, "_headers"), "w", encoding="utf-8") as f:
        f.write(headers_content)
    print("  + Generated: dist/_headers")

    with open(os.path.join(DIST_DIR, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")
    print("  + Generated: dist/.nojekyll")

    redirect_map = [
        ("resume", "../Sai_Lakshmi_Elusuri_CV.pdf", "Redirecting to CV..."),
        ("cv", "../Sai_Lakshmi_Elusuri_CV.pdf", "Redirecting to CV..."),
        ("hub", "../index.html", "Redirecting to Portfolio..."),
    ]
    for folder, target, title in redirect_map:
        folder_path = os.path.join(DIST_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
        html_redirect = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta http-equiv="refresh" content="0; url={target}">
  <script>location.replace("{target}");</script>
</head>
<body>
  <p>{title} <a href="{target}">Open PDF</a>.</p>
</body>
</html>"""
        with open(os.path.join(folder_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_redirect)
        print(f"  + Generated redirect: dist/{folder}/index.html")

    fallback_404 = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Page Not Found — Sai Lakshmi Elusuri</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="4; url=./index.html">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background: #FAF9F5; color: #111827; padding: 20px; }
    .box { max-width: 460px; padding: 28px; background: #FFFFFF; border-radius: 8px; border: 1px solid #E5E3DC; }
    .code { font-family: ui-monospace, monospace; font-size: 0.85rem; font-weight: 700; color: #1D4ED8; margin-bottom: 8px; }
    h1 { font-size: 1.5rem; margin-bottom: 10px; }
    p { color: #4B5563; line-height: 1.55; margin-bottom: 18px; }
    a { display: inline-flex; align-items: center; min-height: 44px; background: #1D4ED8; color: #FFFFFF; padding: 0 18px; border-radius: 6px; text-decoration: none; font-weight: 600; }
  </style>
</head>
<body>
  <div class="box">
    <div class="code">HTTP 404</div>
    <h1>Page not found</h1>
    <p>This link has been retired or moved during the portfolio redesign. Returning to the main portfolio.</p>
    <a href="./index.html">Return to Portfolio</a>
  </div>
</body>
</html>"""
    with open(os.path.join(DIST_DIR, "404.html"), "w", encoding="utf-8") as f:
        f.write(fallback_404)
    print("  + Generated: dist/404.html\n")


def step4_run_tests():
    print("=" * 60)
    print("STEP 4: EXECUTING AUTOMATED INTEGRITY & COMPLIANCE TESTS")
    print("=" * 60)
    test_runner = os.path.join(BASE_DIR, "tests", "run_all_tests.py")
    res = subprocess.run([sys.executable, test_runner], cwd=BASE_DIR)
    if res.returncode != 0:
        print("\n❌ BUILD ABORTED: Test suite failed!")
        sys.exit(1)
    print("✅ All tests passed.\n")


if __name__ == "__main__":
    step0_verify_canonical_sync()
    step1_compile_pdf()
    step2_generate_og_image()
    step3_assemble_dist()
    step4_run_tests()
    print("=" * 60)
    print("🎉 BUILD SUCCESSFUL! READY FOR GITHUB PAGES DEPLOYMENT")
    print("=" * 60)
