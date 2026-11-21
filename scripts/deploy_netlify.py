#!/usr/bin/env python3
"""
Automated Deployment Script for Netlify
Target: https://sailakshminl.netlify.app
Site ID: 787b918a-9066-43e5-815f-4710abbfd307
"""

import os
import sys
import urllib.request
import urllib.error
import json
import subprocess

SITE_ID = "787b918a-9066-43e5-815f-4710abbfd307"
TARGET_URL = "https://sailakshminl.netlify.app"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETLIFY_ZIP_FILENAME = "netlify_deploy.zip"
RECRUITER_ZIP_FILENAME = "Netherlands_Career_Hub_Sai_Lakshmi.zip"
ZIP_PATH = os.path.join(BASE_DIR, NETLIFY_ZIP_FILENAME)
DIST_DIR = os.path.join(BASE_DIR, "dist")

def run_build():
    build_script = os.path.join(BASE_DIR, "build.py")
    res = subprocess.run([sys.executable, build_script], cwd=BASE_DIR)
    if res.returncode != 0:
        print("\n❌ Build failed! Aborting deployment.")
        sys.exit(1)

def deploy_to_netlify():
    print("=" * 60)
    print("DEPLOYING TO NETLIFY")
    print("=" * 60)
    token = os.environ.get("NETLIFY_AUTH_TOKEN")
    
    if token:
        print(f"🔑 Detected NETLIFY_AUTH_TOKEN.")
        print(f"🚀 Uploading {NETLIFY_ZIP_FILENAME} directly to Netlify API (Site ID: {SITE_ID})...")
        api_url = f"https://api.netlify.com/api/v1/sites/{SITE_ID}/deploys"
        
        with open(ZIP_PATH, 'rb') as f:
            zip_data = f.read()

        req = urllib.request.Request(
            api_url,
            data=zip_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/zip",
                "User-Agent": "Antigravity-Netlify-Deployer/2.0"
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
        print("\n   👉 HOW TO DEPLOY IN 5 SECONDS (CHOOSE ONE):")
        print(f"   ─────────────────────────────────────────────────────────────")
        print(f"   [OPTION 1 - DRAG & DROP NETLIFY ZIP]:")
        print(f"   1. Open: https://app.netlify.com/sites/sailakshminl/deploys (or https://app.netlify.com/drop)")
        print(f"   2. Drag and drop '{ZIP_PATH}' (or the '{DIST_DIR}' folder)")
        print(f"      into the Netlify drop zone.")
        print(f"   ─────────────────────────────────────────────────────────────")
        print(f"   [OPTION 2] CLI / Token Deploy:")
        print(f"      export NETLIFY_AUTH_TOKEN=\"<your_token>\"")
        print(f"      python3 scripts/deploy_netlify.py\n")

def check_live_status():
    print("=" * 60)
    print("LIVE SITE HEALTH-CHECK")
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
            content_length = resp.headers.get("Content-Length")
            print(f"   Content-Length: {content_length} bytes")
            print(f"🌐 Site is live and accessible at {TARGET_URL}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"⚠️  HTTP 401 Unauthorized detected on {TARGET_URL}")
            print("   Netlify 'Visitor Access / Site Protection' is active.")
        else:
            print(f"⚠️  HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"⚠️  Connection error: {e}")
    print("=" * 60)

if __name__ == '__main__':
    run_build()
    deploy_to_netlify()
    check_live_status()
