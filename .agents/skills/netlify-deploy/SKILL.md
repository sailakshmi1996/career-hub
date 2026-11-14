---
name: netlify-deploy
description: >-
  Automated deployment, bundling, and live health verification skill for Netlify (sailakshminl.netlify.app).
  Use when packaging deployment bundles, deploying updates via Netlify API or CLI, verifying security headers
  and redirects in netlify.toml, or troubleshooting HTTP 401 Site Protection / Visitor Access issues.
---

# Netlify Deployment & Verification Skill

This skill governs the packaging, automated deployment, and live status verification of the Netherlands Career Command Center to Netlify.

## Site Specifications
* **Target Domain:** `https://sailakshminl.netlify.app`
* **Netlify Site ID:** `c48ae112-95f4-4603-bfbb-1201e50dd3fc`
* **Configuration File:** `netlify.toml`
* **Primary Deployable Bundle:** `Netherlands_Career_Hub_Sai_Lakshmi.zip`

## Automated Deployment Workflow

### Method 1: The Automated Python Deployer (Recommended)
Run the automated deployment script:
```bash
python3 scripts/deploy_netlify.py
```
This script executes four automated phases:
1. **Pre-Deployment Tests:** Runs `tests/run_all_tests.py` to prevent broken builds.
2. **Bundle Packaging:** Compiles clean production ZIP bundle containing only required assets.
3. **API Upload:** If `NETLIFY_AUTH_TOKEN` is set, uploads the ZIP directly to Netlify's deployment API.
4. **Live Health-Check:** Inspects `https://sailakshminl.netlify.app` and reports HTTP status.

### Method 2: Netlify CLI
If Node.js / Netlify CLI is installed:
```bash
# Preview deploy
npx netlify-cli deploy --dir=. --site=c48ae112-95f4-4603-bfbb-1201e50dd3fc

# Production deploy
npx netlify-cli deploy --prod --dir=. --site=c48ae112-95f4-4603-bfbb-1201e50dd3fc --auth=$NETLIFY_AUTH_TOKEN
```

### Method 3: Netlify Drop (Manual Drag & Drop)
1. Open [https://app.netlify.com/drop](https://app.netlify.com/drop) or the **Deploys** tab of the `sailakshminl` dashboard.
2. Drag and drop `Netherlands_Career_Hub_Sai_Lakshmi.zip`.
3. Netlify will unpack and publish the site in ~5 seconds.

## Troubleshooting HTTP 401 (Visitor Access / Site Protection)

If `curl -I https://sailakshminl.netlify.app` returns `HTTP/2 401 Unauthorized`:
1. Log in to [app.netlify.com](https://app.netlify.com).
2. Select the site **`sailakshminl`**.
3. Navigate to: **Site configuration** → **Access & security** (or **Site protection**).
4. Under **Visitor access**, change the setting to **"Public"** (or uncheck *"Require password / Netlify access control"*).
5. Click **Save**.

## Security Headers in `netlify.toml`
The configuration in `netlify.toml` automatically injects:
* `Content-Security-Policy`: Restricts scripts and styles to self and Google Fonts.
* `Strict-Transport-Security`: HSTS preload enabled for 1 year.
* `X-Frame-Options: DENY`: Prevents clickjacking.
* `Permissions-Policy`: Restricts camera, microphone, and geolocation.
* Vanity redirects: `/cv` redirects directly to `cv_power_bi_developer.pdf`.
