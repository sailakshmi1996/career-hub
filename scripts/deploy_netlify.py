#!/usr/bin/env python3
"""
Automated Deployment Script for Netlify
Target: https://sailakshminl.netlify.app
Site ID: c48ae112-95f4-4603-bfbb-1201e50dd3fc
"""

import os
import sys
import zipfile
import urllib.request
import urllib.error
import json
import subprocess

SITE_ID = "c48ae112-95f4-4603-bfbb-1201e50dd3fc"
TARGET_URL = "https://sailakshminl.netlify.app"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_FILENAME = "Netherlands_Career_Hub_Sai_Lakshmi.zip"
ZIP_PATH = os.path.join(BASE_DIR, ZIP_FILENAME)

DEPLOY_FILES = [
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
    "influencer-insights.html",
    "netlify.toml"
]

def run_tests():
    print("=" * 60)
    print("1. RUNNING PRE-DEPLOYMENT TEST SUITE")
    print("=" * 60)
    test_runner = os.path.join(BASE_DIR, "tests", "run_all_tests.py")
    res = subprocess.run([sys.executable, test_runner], cwd=BASE_DIR)
    if res.returncode != 0:
        print("\n❌ ABORTING DEPLOYMENT: Tests failed! Please fix test issues before deploying.")
        sys.exit(1)
    print("✅ Pre-deployment tests passed.\n")

def package_bundle():
    print("=" * 60)
    print("2. PACKAGING PRODUCTION DEPLOYMENT BUNDLE")
    print("=" * 60)
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in DEPLOY_FILES:
            fpath = os.path.join(BASE_DIR, fname)
            if os.path.isfile(fpath):
                zf.write(fpath, arcname=fname)
                print(f"  + Added: {fname} ({os.path.getsize(fpath):,} bytes)")
            else:
                print(f"  ⚠️ Warning: {fname} not found on disk, skipping.")
    
    print(f"\n📦 Bundle created successfully: {ZIP_PATH} ({os.path.getsize(ZIP_PATH):,} bytes)\n")

def deploy_to_netlify():
    print("=" * 60)
    print("3. DEPLOYING TO NETLIFY")
    print("=" * 60)
    token = os.environ.get("NETLIFY_AUTH_TOKEN")
    
    if token:
        print(f"🔑 Detected NETLIFY_AUTH_TOKEN in environment.")
        print(f"🚀 Uploading {ZIP_FILENAME} to Netlify API (Site ID: {SITE_ID})...")
        api_url = f"https://api.netlify.com/api/v1/sites/{SITE_ID}/deploys"
        
        with open(ZIP_PATH, 'rb') as f:
            zip_data = f.read()

        req = urllib.request.Request(
            api_url,
            data=zip_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/zip",
                "User-Agent": "Antigravity-Netlify-Deployer/1.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
                deploy_id = resp_data.get("id")
                state = resp_data.get("state")
                ssl_url = resp_data.get("ssl_url") or TARGET_URL
                print(f"🎉 DEPLOY SUCCESSFUL!")
                print(f"   Deploy ID: {deploy_id}")
                print(f"   State:     {state}")
                print(f"   Live URL:  {ssl_url}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"❌ Netlify API Deploy Failed with HTTP {e.code}: {e.reason}")
            print(f"   Details: {err_body}")
    else:
        print("ℹ️  No NETLIFY_AUTH_TOKEN detected in environment.")
        print("   You can deploy instantly using either of these two methods:")
        print(f"   [Method A] Drag & Drop: Drop '{ZIP_FILENAME}' into https://app.netlify.com/drop")
        print(f"   [Method B] CLI Deploy:")
        print(f"              export NETLIFY_AUTH_TOKEN=<your_token>")
        print(f"              python3 scripts/deploy_netlify.py\n")

def check_live_status():
    print("=" * 60)
    print("4. LIVE SITE HEALTH-CHECK")
    print("=" * 60)
    print(f"Inspecting {TARGET_URL}...")
    req = urllib.request.Request(
        TARGET_URL,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            code = resp.getcode()
            print(f"✅ Target site responded with HTTP {code} OK!")
            print(f"🌐 Site is live and publicly accessible at {TARGET_URL}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"⚠️  HTTP 401 Unauthorized detected on {TARGET_URL}")
            print("   Netlify 'Visitor Access / Site Protection' is currently ACTIVE.")
            print("\n   👉 HOW TO UNLOCK IN 20 SECONDS:")
            print("      1. Log in to https://app.netlify.com")
            print("      2. Open site: sailakshminl")
            print("      3. Go to Site configuration -> Access & security (or Site protection)")
            print("      4. Change 'Visitor access' to 'Public' and click Save.")
        else:
            print(f"⚠️  HTTP {e.code} received from {TARGET_URL}: {e.reason}")
    except Exception as e:
        print(f"⚠️  Connection error: {e}")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
    package_bundle()
    deploy_to_netlify()
    check_live_status()
