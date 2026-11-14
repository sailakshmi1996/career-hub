---
name: career-hub-testing
description: >-
  Automated testing and compliance validation skill for Sai Lakshmi's Netherlands Career Command Center.
  Use when verifying site structural integrity, checking internal navigation anchors, enforcing zero-date/milestone constraints,
  auditing GDPR/AVG candidate privacy compliance, or running pre-deployment test suites.
---

# Career Hub Testing & Compliance Skill

This skill governs the automated verification of the Netherlands Career Hub website, ensuring that all code changes meet strict quality, legal, and privacy benchmarks before deployment.

## Test Suite Components

The test suite is located in the `tests/` directory:

1. **`tests/test_site_integrity.py`**:
   - **Local Asset Verification**: Asserts that all referenced documents (`cv_power_bi_developer.pdf`, `cv_bi_project_delivery.pdf`, HTML CVs, ZIP packages) exist on disk and are non-empty.
   - **Navigation Anchor Resolution**: Verifies that every `href="#<id>"` in the navigation bar matches a concrete element `id` in `index.html`.
   - **Curated Communities**: Asserts the presence of all 10 Amsterdam-Utrecht Women in Tech communities (Equals, Women in Data, WomenHack, WAI, PyLadies, etc.).
   - **Key Technical Anchors**: Asserts presence of verified technical metrics (40% load-time reduction, VertiPaq, Star Schema, Fabric).

2. **`tests/test_compliance_and_dates.py`**:
   - **Zero Prohibited Dates/Timelines**: Asserts that no rigid calendar months (Jan–Dec) or countdown years (2025–2027) appear in the milestone roadmap.
   - **GDPR & Dutch AVG Privacy**: Confirms zero third-party tracking scripts (Google Analytics, Facebook Pixel, Hotjar), presence of BSN legal protection notices, and local storage erasure functions (`clearTrackerData()`).
   - **IND Legal Endorsement**: Confirms explicit presence of the required labor authorization statement: `"Arbeid vrij toegestaan, TWV niet vereist"`.

## How to Execute Tests

### 1. Run Complete Test Suite
Run the centralized test runner:
```bash
python3 tests/run_all_tests.py
```

### 2. Run Individual Test Modules
```bash
# Site integrity only
python3 -m unittest tests/test_site_integrity.py

# GDPR & date compliance only
python3 -m unittest tests/test_compliance_and_dates.py
```

## Interpreting Failures & Remediation

* **Failure: `Forbidden calendar month found` or `Forbidden timeline years found`**
  - *Remediation*: Replace calendar dates with stage-based milestones (e.g., replace specific months with "Stage 2: Targeted Outreach").
* **Failure: `Broken navigation link: href='#...' has no matching id`**
  - *Remediation*: Ensure the target section or container in `index.html` has the corresponding `id="..."` attribute.
* **Failure: `GDPR Violation: Found tracking script`**
  - *Remediation*: Remove third-party telemetry or cookies. The site must remain strictly zero-cookie and zero-tracking.
* **Failure: `Required asset missing on disk`**
  - *Remediation*: Rebuild the missing asset (e.g. compile PDF CV or regenerate ZIP bundle).
