# Sai Lakshmi Elusuri — Senior Power BI & Microsoft Fabric Developer

**Utrecht Region, Netherlands** · Full Dutch labor access (*Arbeid vrij toegestaan, TWV niet vereist*)

* **Live Portfolio:** [sailakshmi1996.github.io/career-hub](https://sailakshmi1996.github.io/career-hub/)
* **Canonical CV (PDF):** [Sai_Lakshmi_Elusuri_CV.pdf](./Sai_Lakshmi_Elusuri_CV.pdf)
* **LinkedIn:** [linkedin.com/in/sailakshmielusuri-data-analyst](https://www.linkedin.com/in/sailakshmielusuri-data-analyst/)
* **Technical Showcase:** [`technical-showcase/`](./technical-showcase/)

---

## Overview

8+ years of enterprise BI experience across Apexon, Accenture, Genpact, and Conduent turning slow SQL reporting estates and legacy Qlik Sense assets into governed Kimball star-schema semantic models in Power BI and Microsoft Fabric.

### Core Areas
* **Semantic Modeling & VertiPaq Tuning:** Single-direction `1:*` Kimball stars, integer `DateKey` / `TimeKey` splitting, Calculation Groups (`Precedence`), `KEEPFILTERS`, and Storage Engine optimization verified with DAX Studio & Tabular Editor 3.
* **SQL & Incremental Ingestion:** Oracle SQL and T-SQL deduplication views (`ROW_NUMBER()`) preserving Power Query `RangeStart` / `RangeEnd` partition folding without unnecessary outer sorts.
* **Microsoft Fabric & OneLake:** Incremental PySpark Delta `MERGE INTO` pipelines resolving surrogate integer keys, pre-write quality assertions, V-Order write optimization, and Liquid Clustering (`clusterBy`) for Direct Lake models.
* **Migration & Governance:** Coordinated 50+ Qlik Sense → Power BI asset migrations across 3 Agile pods, enforcing Entra ID dynamic RLS (`USERPRINCIPALNAME()`) and Dev/Test/Prod Deployment Pipelines.

---

## Technical Showcase Artifacts

| Area | Artifact | Pattern Demonstrated |
| :--- | :--- | :--- |
| **DAX & Calculation Groups** | [`calculation_groups_and_semi_additive.dax`](./technical-showcase/dax/calculation_groups_and_semi_additive.dax) | Time Intelligence (`Precedence = 20`), daily-grain FX translation with ratio protection (`Precedence = 10`), semi-additive closing balance, and apples-to-apples FE vs. SE benchmark. |
| **Oracle SQL Folding** | [`oracle_incremental_staging_cte.sql`](./technical-showcase/sql/oracle_incremental_staging_cte.sql) | Partition-pruned foldable Oracle view (`vw_sales_latest_revision`) with latest-revision `ROW_NUMBER()` deduplication. |
| **Fabric PySpark Lakehouse** | [`delta_lake_v_order_pipeline.py`](./technical-showcase/fabric_pyspark/delta_lake_v_order_pipeline.py) | Incremental Delta `MERGE INTO`, surrogate key lookup with `-1` fallback, data-quality checks, V-Order, and Liquid Clustering. |

*(Client `.pbix` models remain under NDA; synthetic `.pbip` demonstrations are staged alongside the visual slots on the live portfolio.)*

---

## Microsoft Certifications

* **PL-300** — Power BI Data Analyst Associate
* **DP-600** — Fabric Analytics Engineer Associate
* *Foundational:* DP-900 (Azure Data), AZ-900 (Azure), AI-900 (Azure AI)

---

## Build & Validation

```bash
python3 build.py
```

Builds the canonical 2-page PDF CV, updates `og-cover.png`, assembles clean public output into `dist/`, and executes `tests/run_all_tests.py`.
