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

---

## Portfolio Layout & Architecture Invariants

When authoring or revamping the career portfolio landing page, the following engineering invariants must be maintained:

1. **Complete Section Encapsulation (Scroll-Spy Invariant)**:
   - Navigable sections must encapsulate both the heading and all child cards/tables/grids inside `<section class="section-block" id="...">`.
   - Never place cards in sibling `<div>`s outside the section container, or `IntersectionObserver` scroll-spy active state tracking will fail as soon as the small header scrolls out of view.

2. **Single-Row Command Header**:
   - The sticky navigation bar must remain on a single row across standard desktop viewports (1280px–1440px) with responsive tiering to avoid action button overflow or broken double rows.

3. **Above-the-Fold Quantified HUD**:
   - The hero block must feature an integrated quantified telemetry HUD (e.g., 8+ Years Lakehouse, 5x Certified, 40% Query Speedup, NS Rail commute) to immediately establish senior credibility.

4. **Four-Pillar Tactical Architecture Standard**:
   - Any senior enterprise BI / lakehouse architect showcase must feature concrete code comparisons across:
     - *DAX VertiPaq Engine*: Vectorized Storage Engine (SE) scans vs Formula Engine (FE) iteration bottlenecks (`KEEPFILTERS`, integer `DateKey`).
     - *Dimensional Rigor*: Flat Denormalized Wide Tables vs pure Kimball Star Schema memory footprints.
     - *Microsoft Fabric Lakehouse (DP-600)*: Direct Lake mode vs Import vs DirectQuery, and OneLake Medallion layers.
     - *High-Throughput RDBMS Ingestion*: Partition folding with analytical window functions (`DENSE_RANK()`) over `RangeStart`/`RangeEnd` to eliminate production database locks.

5. **Live Capability Telemetry**:
   - Interactive simulators must reflect dynamic engine telemetry (SE vs FE execution split, compression ratios, Direct Lake paging states) and active DAX measure queries rather than static text changes.

6. **Legal & Compliance Guardrails**:
   - Never include prohibited calendar months or countdown timeline years in `index.html`.
   - Always preserve statutory BSN pre-employment protection notices, IND endorsement verbatim phrases (`"Arbeid vrij toegestaan, TWV niet vereist"`), and GDPR Art. 17 right to erasure (`clearTrackerData()`).
