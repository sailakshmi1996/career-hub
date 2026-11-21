# Facts to Confirm & Candidate Claim Verification Register

**Candidate:** Sai Lakshmi Elusuri  
**Target Roles:** Senior Power BI Developer / BI Delivery Coordinator  
**Last Updated:** 2026-11-16  
**Document Status:** Pending Candidate Review & Sign-Off  

---

## 1. Executive Summary & Purpose

In compliance with Dutch and European recruitment compliance standards, candidate integrity guidelines, and the single canonical data architecture of this career portfolio, all metrics, project scopes, and technical claims must be strictly substantiated. 

This register catalogs **candidate-reported performance metrics**, **operational volume figures**, and **technical architecture statements** that appear across Sai Lakshmi Elusuri's CVs and portfolio materials. These entries represent self-reported operational accomplishments. To ensure complete credibility with Dutch enterprise hiring managers and technical audit committees, each item below has been qualified with technical context and documented here for candidate verification before any third-party attestation.

---

## 2. Facts to Confirm by Role

### 2.1 Apexon (Apr 2026–Present) — Senior Data Analyst

| Item # | Candidate-Reported Metric / Claim | Context & Artifact Location | Technical Qualification & Fact-Check Note | Candidate Status |
| :--- | :--- | :--- | :--- | :--- |
| **APX-01** | **30+ hours/month manual exports saved** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Achieved by replacing periodic manual Excel/CSV extracts with automated Oracle SQL DB ingestion into Power BI Service via DirectQuery and incremental refresh partitions. | [ ] Confirmed by Candidate |
| **APX-02** | **45% data refresh / reporting latency reduction** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Measured against legacy batch extract schedules; attributed to partitioned table loading, query folding, and incremental refresh windows in Power BI Service. | [ ] Confirmed by Candidate |
| **APX-03** | **35% staging query runtime shrink** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Achieved on Oracle SQL database by refactoring nested subqueries into Common Table Expressions (CTEs), utilizing analytical window functions (`ROW_NUMBER()`, `RANK()`), and leveraging partitioned views. | [ ] Confirmed by Candidate |
| **APX-04** | **40% increase in weekly active report adoption** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Telemetry derived from Power BI Service usage metrics app following stakeholder alignment workshops, UX redesign, and governed KPI scorecards. | [ ] Confirmed by Candidate |
| **APX-05** | **Low-latency visual rendering vs. "Sub-Second" claims** | `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | **Corrected:** Hyperbolic claims of "sub-second visual rendering" have been qualified. Render speed depends on client browser capacity, VertiPaq engine cache states, and Direct Lake memory paging over OneLake Parquet files. | [x] Qualified in Materials |

---

### 2.2 Accenture (February 2022 – April 2026) — Power BI Developer

| Item # | Candidate-Reported Metric / Claim | Context & Artifact Location | Technical Qualification & Fact-Check Note | Candidate Status |
| :--- | :--- | :--- | :--- | :--- |
| **ACN-01** | **Up to 40% dashboard load-time reduction** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Achieved across sustainability and executive reporting dashboards by refactoring flat/denormalized models into Kimball star schemas, removing bi-directional cross-filtering, and optimizing DAX calculations. | [ ] Confirmed by Candidate |
| **ACN-02** | **Up to 35% VertiPaq memory footprint reduction** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Documented through DAX Studio / Tabular Editor VertiPaq Analyzer metrics after eliminating high-cardinality timestamp columns, splitting datetime fields, and integer-encoding foreign keys. | [ ] Confirmed by Candidate |
| **ACN-03** | **End-to-end legacy Qlik Sense to Power BI migration** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Managed business logic translation from Qlik set analysis to DAX measures, standardized semantic layer models, and conducted user acceptance testing across business units. | [ ] Confirmed by Candidate |
| **ACN-04** | **Celonis Process Mining integration** | `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Extracted event log process mining telemetry from Celonis to surface process friction and operational bottleneck KPIs in executive Power BI dashboards. | [ ] Confirmed by Candidate |

---

### 2.3 Conduent (June 2018 – April 2021) — Data Analyst

| Item # | Candidate-Reported Metric / Claim | Context & Artifact Location | Technical Qualification & Fact-Check Note | Candidate Status |
| :--- | :--- | :--- | :--- | :--- |
| **CND-01** | **60+ person-hours monthly saved** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Replaced legacy manual spreadsheet collation and periodic operational report compilation with automated Power BI dashboards and scheduled dataset refreshes. | [ ] Confirmed by Candidate |
| **CND-02** | **SLA compliance elevated from 91% to 98%** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Result of executive insight packs, visibility into workflow bottleneck queues, and proactive alerting on turnaround milestones for business operations leadership. | [ ] Confirmed by Candidate |
| **CND-03** | **40+ optimized SQL queries, views, and stored procedures** | `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Staging layer SQL objects authored across enterprise relational database instances to feed operational Power BI dashboards. | [ ] Confirmed by Candidate |

---

### 2.4 Genpact (April 2021 – January 2022) — Data Risk Analyst

| Item # | Candidate-Reported Metric / Claim | Context & Artifact Location | Technical Qualification & Fact-Check Note | Candidate Status |
| :--- | :--- | :--- | :--- | :--- |
| **GEN-01** | **100% data reconciliation across mortgage insurance portfolios** | `canonical_data.py`, `cv_power_bi_developer.html`, `cv_bi_project_delivery.html`, `resume.html` | Established automated SQL Server validation scripts and tie-out checks matching transactional source systems against executive credit risk dashboards. | [ ] Confirmed by Candidate |

---

## 3. Technical Accuracy & Microsoft Documentation Alignment

In accordance with official Microsoft Fabric, Delta Lake, and Power BI architecture guidelines, the following technical terminology adjustments have been enforced across all CV and portfolio artifacts:

1. **Direct Lake Mode Mechanics**:
   - *Previous Marketing Description:* "Zero data movement, instantaneous VertiPaq decompression, zero refresh lag."
   - *Official Microsoft Fact-Checked Standard:* Direct Lake loads Delta Parquet table metadata from OneLake without requiring scheduled data imports. Column data is dynamically paged into VertiPaq memory on demand. If queries exceed capacity memory thresholds (e.g. F-SKU limits) or invoke unsupported DAX operations, Direct Lake transparently falls back to DirectQuery over the Lakehouse SQL analytics endpoint.
   - *Action Taken:* All absolute "zero latency", "zero data movement", and "sub-second" guarantees have been replaced with precise architectural language (e.g. "low-latency visual rendering via Direct Lake memory paging and star-schema semantic models").

2. **V-Order Optimization**:
   - *Previous Description:* "Instantaneous VertiPaq column decompression."
   - *Official Microsoft Standard:* V-Order is a Microsoft write-time optimization applied to Parquet files to maximize in-memory compression ratios and accelerate read-time vector processing in VertiPaq and Spark.
   - *Action Taken:* Updated to reflect optimized columnar compression rather than instantaneous decompression.

3. **VertiPaq Memory & Storage Engine Execution**:
   - Visual calculation speed depends on the ratio of Storage Engine (SE) multi-threaded batch operations to Formula Engine (FE) single-threaded evaluations.
   - Measures avoid iterative row-by-row functions (`FILTER(ALL(...))`) in favor of `KEEPFILTERS` and star-schema dimensional filtering to maximize VertiPaq cache utilization.

---

## 4. Quarantined External Client Names & Entities

During repository auditing, certain legacy draft files (such as `data.js`) referenced third-party corporate entities (e.g., *ABN AMRO Bank*, *T-Mobile*) under informal project descriptions:

| Entity Name | Source File | Status & Handling |
| :--- | :--- | :--- |
| **ABN AMRO Bank** | `data.js` (legacy file) | **QUARANTINED / EXCLUDED.** Not listed in `canonical_data.py`. Sai Lakshmi was employed by Conduent, Genpact, Accenture, and Apexon. References to non-employer client names without formal NDA clearance have been strictly excluded from all public portfolio pages, HTML CVs, and PDF outputs. |
| **T-Mobile** | `data.js` (legacy file) | **QUARANTINED / EXCLUDED.** Not listed in `canonical_data.py`. Strictly excluded from all public deliverables. |

---

## 5. Candidate Sign-Off & Verification Checklist

Please review each listed metric and confirm its accuracy for formal documentation:

- [ ] **APX-01** (Apexon: 30+ hrs/mo manual exports saved)
- [ ] **APX-02** (Apexon: 45% refresh latency reduction)
- [ ] **APX-03** (Apexon: 35% staging query runtime shrink)
- [ ] **APX-04** (Apexon: 40% weekly active adoption boost)
- [ ] **ACN-01** (Accenture: up to 40% dashboard load-time reduction)
- [ ] **ACN-02** (Accenture: up to 35% memory footprint reduction)
- [ ] **ACN-03** (Accenture: Qlik Sense to Power BI migration scope)
- [ ] **ACN-04** (Accenture: Celonis process intelligence integration)
- [ ] **CND-01** (Conduent: 60+ person-hours monthly saved)
- [ ] **CND-02** (Conduent: SLA compliance 91% to 98%)
- [ ] **CND-03** (Conduent: 40+ SQL staging objects authored)
- [ ] **GEN-01** (Genpact: 100% data reconciliation across portfolios)

**Candidate Signature:** ___________________________  
**Date:** ___________________________  
