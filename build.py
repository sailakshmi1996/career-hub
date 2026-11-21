#!/usr/bin/env python3
"""
Master Build Script for Sai Lakshmi Elusuri Portfolio & Career Bundle
1. Compiles and updates PDF CVs from canonical HTML sources
2. Executes pre-build automated tests for site integrity and compliance
3. Assembles clean 'dist/' publish directory containing recruiter-facing assets
4. Packages standalone deployment ZIP bundle with accurate README manifest
"""

import os
import shutil
import sys
import subprocess
import zipfile

try:
    import fitz
except ImportError:
    fitz = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
ZIP_NAME = "Netherlands_Career_Hub_Sai_Lakshmi.zip"
ZIP_PATH_ROOT = os.path.join(BASE_DIR, ZIP_NAME)
ZIP_PATH_DIST = os.path.join(DIST_DIR, ZIP_NAME)

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Recruiter-facing public assets only
FILES_TO_DEPLOY = [
    "index.html",
    "dutch-career-hub.html",
    "shared.css",
    "cv_power_bi_developer.html",
    "cv_bi_project_delivery.html",
    "resume.html",
    "cv_power_bi_developer.pdf",
    "cv_bi_project_delivery.pdf",
    "Sai_Lakshmi_Elusuri_Resume.pdf"
]

PDF_METADATA = {
    "cv_power_bi_developer.pdf": {
        "title": "Sai Lakshmi Elusuri - Senior Power BI Developer CV",
        "author": "Sai Lakshmi Elusuri",
        "subject": "Senior Power BI Developer CV - Semantic Modeling, DAX, SQL & Fabric Lakehouse",
        "keywords": "Power BI, DAX, SQL, Fabric, Lakehouse, Semantic Modeling, Netherlands, Utrecht"
    },
    "cv_bi_project_delivery.pdf": {
        "title": "Sai Lakshmi Elusuri - BI Delivery Coordinator & Analytics Lead CV",
        "author": "Sai Lakshmi Elusuri",
        "subject": "BI Delivery Coordinator & Analytics Delivery Lead CV",
        "keywords": "BI Delivery, Project Coordination, Agile Analytics, Jira, Confluence, Qlik Migration, Netherlands"
    },
    "Sai_Lakshmi_Elusuri_Resume.pdf": {
        "title": "Sai Lakshmi Elusuri – Master Resume | Senior Power BI Developer & Lakehouse Analytics Specialist",
        "author": "Sai Lakshmi Elusuri",
        "subject": "Master Curriculum Vitae - Senior Power BI Developer & Lakehouse Specialist",
        "keywords": "Power BI, Lakehouse, DAX, SQL, Azure Data Factory, Celonis, Netherlands"
    }
}

def step1_compile_pdfs():
    print("=" * 60)
    print("STEP 1: COMPILING & VERIFYING CANDIDATE PDF CVS")
    print("=" * 60)
    html_to_pdf_map = [
        ("cv_power_bi_developer.html", "cv_power_bi_developer.pdf"),
        ("cv_bi_project_delivery.html", "cv_bi_project_delivery.pdf"),
        ("resume.html", "Sai_Lakshmi_Elusuri_Resume.pdf")
    ]

    for html_file, pdf_file in html_to_pdf_map:
        html_path = os.path.join(BASE_DIR, html_file)
        pdf_path = os.path.join(BASE_DIR, pdf_file)
        
        if os.path.exists(CHROME_BIN):
            cmd = [
                CHROME_BIN,
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}",
                html_path
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode != 0:
                print(f"  ⚠️ Warning: Headless Chrome compilation had non-zero exit for {pdf_file}")

        # Set clean metadata
        if fitz is not None and os.path.exists(pdf_path):
            doc = fitz.open(pdf_path)
            meta = PDF_METADATA.get(pdf_file, {})
            doc.set_metadata(meta)
            doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            page_count = len(doc)
            doc.close()
            print(f"  + Verified PDF: {pdf_file} ({page_count} pages, {os.path.getsize(pdf_path):,} bytes)")
        elif os.path.exists(pdf_path):
            print(f"  + Verified PDF: {pdf_file} ({os.path.getsize(pdf_path):,} bytes)")
        else:
            print(f"  ❌ Error: {pdf_file} does not exist!")
            sys.exit(1)
    print()

def step2_run_tests():
    print("=" * 60)
    print("STEP 2: EXECUTING AUTOMATED INTEGRITY & COMPLIANCE TESTS")
    print("=" * 60)
    test_runner = os.path.join(BASE_DIR, "tests", "run_all_tests.py")
    res = subprocess.run([sys.executable, test_runner], cwd=BASE_DIR)
    if res.returncode != 0:
        print("\n❌ BUILD ABORTED: Test suite failed! Fix errors before deploying.")
        sys.exit(1)
    print("✅ All tests passed.\n")

def step3_assemble_dist():
    print("=" * 60)
    print("STEP 3: ASSEMBLING CLEAN 'dist/' DIRECTORY FOR NETLIFY")
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
            print(f"  ❌ Error: Required asset {fname} missing from source!")
            sys.exit(1)

    # Copy bundle README into dist
    readme_src = os.path.join(BASE_DIR, "README_BUNDLE.txt")
    readme_dst = os.path.join(DIST_DIR, "README.txt")
    if os.path.isfile(readme_src):
        shutil.copy2(readme_src, readme_dst)
        print(f"  + Copied manifest: dist/README.txt")

    # Generate Netlify _redirects
    redirects_content = """/resume   /Sai_Lakshmi_Elusuri_Resume.pdf 302
/cv       /cv_power_bi_developer.pdf   302
/pm-cv    /cv_bi_project_delivery.pdf  302
/hub      /index.html                  301
"""
    with open(os.path.join(DIST_DIR, "_redirects"), "w", encoding="utf-8") as f:
        f.write(redirects_content)
    print("  + Generated: dist/_redirects")

    # Generate Netlify _headers
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

/*.zip
  Cache-Control: public, max-age=86400, must-revalidate
  Content-Disposition: attachment; filename="Netherlands_Career_Hub_Sai_Lakshmi.zip"

/*.css
  Cache-Control: public, max-age=604800, stale-while-revalidate=86400
"""
    with open(os.path.join(DIST_DIR, "_headers"), "w", encoding="utf-8") as f:
        f.write(headers_content)
    print("  + Generated: dist/_headers\n")

def step4_package_zip():
    print("=" * 60)
    print("STEP 4: COMPILING RECRUITER CAREER BUNDLE (ZIP)")
    print("=" * 60)
    bundle_files = [
        ("cv_power_bi_developer.pdf", "cv_power_bi_developer.pdf"),
        ("cv_bi_project_delivery.pdf", "cv_bi_project_delivery.pdf"),
        ("Sai_Lakshmi_Elusuri_Resume.pdf", "Sai_Lakshmi_Elusuri_Resume.pdf"),
        ("cv_power_bi_developer.html", "cv_power_bi_developer.html"),
        ("cv_bi_project_delivery.html", "cv_bi_project_delivery.html"),
        ("resume.html", "resume.html"),
        ("index.html", "index.html"),
        ("shared.css", "shared.css"),
        ("README_BUNDLE.txt", "README.txt")
    ]

    for target_zip in [ZIP_PATH_DIST, ZIP_PATH_ROOT]:
        with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for src_name, arc_name in bundle_files:
                src_path = os.path.join(BASE_DIR, src_name)
                if os.path.exists(src_path):
                    zf.write(src_path, arcname=arc_name)
                    print(f"  + Added to {os.path.basename(target_zip)}: {arc_name}")
                else:
                    print(f"  ⚠️ Warning: {src_name} missing for zip packaging")
        print(f"📦 Archive compiled: {target_zip} ({os.path.getsize(target_zip):,} bytes)\n")

if __name__ == "__main__":
    step1_compile_pdfs()
    step3_assemble_dist()
    step2_run_tests()
    step4_package_zip()
    print("=" * 60)
    print("🎉 BUILD SUCCESSFUL! FULLY READY FOR PRODUCTION NETLIFY DEPLOYMENT")
    print("=" * 60)
