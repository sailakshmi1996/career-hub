#!/usr/bin/env python3
"""
Master Build Script for Netlify & Production Delivery
1. Runs full test suite
2. Assembles clean, isolated 'dist/' directory (no .git, zero security warnings)
3. Generates _redirects and _headers
4. Packages standalone deployment ZIP
"""

import os
import shutil
import sys
import subprocess
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
ZIP_PATH = os.path.join(BASE_DIR, "Netherlands_Career_Hub_Sai_Lakshmi.zip")

FILES_TO_DEPLOY = [
    "index.html",
    "dutch-career-hub.html",
    "shared.css",
    "cv_power_bi_developer.pdf",
    "cv_bi_project_delivery.pdf",
    "cv_power_bi_developer.html",
    "cv_bi_project_delivery.html",
    "job-finder.html",
    "linkedin-optimizer.html",
    "strategy.html",
    "influencer-insights.html"
]

def step1_run_tests():
    print("=" * 60)
    print("STEP 1: EXECUTING PRE-BUILD INTEGRITY & COMPLIANCE TESTS")
    print("=" * 60)
    test_runner = os.path.join(BASE_DIR, "tests", "run_all_tests.py")
    res = subprocess.run([sys.executable, test_runner], cwd=BASE_DIR)
    if res.returncode != 0:
        print("\n❌ BUILD ABORTED: Test suite failed! Fix errors before deploying.")
        sys.exit(1)
    print("✅ All tests passed.\n")

def step2_assemble_dist():
    print("=" * 60)
    print("STEP 2: ASSEMBLING CLEAN 'dist/' PUBLISH DIRECTORY")
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
            print(f"  ⚠️ Warning: {fname} missing from source, skipping.")

    # Generate _redirects for Netlify
    redirects_content = """/cv       /cv_power_bi_developer.pdf   302
/pm-cv    /cv_bi_project_delivery.pdf  302
/hub      /index.html                  301
"""
    with open(os.path.join(DIST_DIR, "_redirects"), "w", encoding="utf-8") as f:
        f.write(redirects_content)
    print("  + Generated: dist/_redirects")

    # Generate _headers for Netlify
    headers_content = """/*
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self';

/*.pdf
  Cache-Control: public, max-age=86400, must-revalidate
  Content-Disposition: inline

/*.css
  Cache-Control: public, max-age=604800, stale-while-revalidate=86400
"""
    with open(os.path.join(DIST_DIR, "_headers"), "w", encoding="utf-8") as f:
        f.write(headers_content)
    print("  + Generated: dist/_headers")
    print(f"\n✅ 'dist/' assembly complete. Directory ready for Netlify publish.\n")

def step3_package_zip():
    print("=" * 60)
    print("STEP 3: COMPILING STANDALONE ZIP BUNDLE")
    print("=" * 60)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(DIST_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DIST_DIR)
                zf.write(full_path, arcname=rel_path)
    print(f"📦 Archive compiled: {ZIP_PATH} ({os.path.getsize(ZIP_PATH):,} bytes)\n")

if __name__ == "__main__":
    step1_run_tests()
    step2_assemble_dist()
    step3_package_zip()
    print("=" * 60)
    print("🎉 BUILD SUCCESSFUL! READY FOR INSTANT NETLIFY DEPLOYMENT")
    print("=" * 60)
