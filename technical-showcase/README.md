# 🛠️ Senior Power BI & Lakehouse Architecture Technical Showcase
### Real-World Production Code & Architectural Patterns by Sai Lakshmi Elusuri

This directory provides concrete, runnable technical artifacts demonstrating enterprise semantic modeling, advanced DAX optimization, high-throughput SQL staging, and Microsoft Fabric Lakehouse engineering.

---

## 📂 Contents

1. [📊 Advanced DAX & VertiPaq Optimization (`dax/`)](./dax/calculation_groups_and_semi_additive.dax)
   - **Calculation Groups for Multi-Currency & Time-Intelligence:** Eliminates measure sprawl (from 150+ derived combinations down to core base measures + Calculation Items) while protecting Storage Engine (SE) multi-threaded batching and passing `'Dim_Date'[Date]` properly to time-intelligence functions.
   - **VertiPaq Engine Cache Optimization:** Utilizing `KEEPFILTERS` and integer `DateKey` relationships instead of expensive Formula Engine (FE) `FILTER(ALL(...))` row iterations.
   - **Semi-Additive Measure Patterns:** Fast closing balance calculation using single-scan `MAX` snapshot lookup + `KEEPFILTERS`.

2. [⚡ Oracle SQL & Relational Staging Queries (`sql/`)](./sql/oracle_incremental_staging_cte.sql)
   - **Common Table Expressions (CTEs) & Analytical Window Functions:** Replaces correlated subqueries with `ROW_NUMBER()` and `DENSE_RANK()` single-pass deduplication.
   - **Incremental Refresh Query Folding:** Sargable `RangeStart` / `RangeEnd` predicates preserving Oracle range-partition pruning and Power BI query folding.

3. [☁️ Microsoft Fabric & PySpark Delta Lake Pipeline (`fabric_pyspark/`)](./fabric_pyspark/delta_lake_v_order_pipeline.py)
   - **Medallion Gold Table Lakehouse Pipeline:** PySpark transformation creating Delta Parquet tables in OneLake with integer `DateKey`/`TimeKey` splitting.
   - **V-Order & Columnar Compression:** Enabling write-time V-Order sorting for optimal read-time decompression and memory paging in **Direct Lake mode**.
   - **Z-Ordering / Data Skipping:** Co-locating high-selectivity `DateKey` and `CustomerKey` predicates to minimize file scans across multi-year telemetry.

---

## 🎯 Architectural Philosophy

| Principle | Anti-Pattern (What to Avoid) | Production Standard (What Sai Lakshmi Deploys) |
| :--- | :--- | :--- |
| **Data Modeling** | Wide flat denormalized tables; bi-directional filtering (`Both`); snowflaked dimensions | Strict **Kimball Star Schema** (Single-directional 1:* filtering, integer surrogate keys) |
| **DAX Evaluation** | Iterative row-by-row filtering (`FILTER(ALL(...))`); excessive calculated columns | Set-based filtering via `KEEPFILTERS`; DAX Calculation Groups; Tabular Editor metadata script |
| **Storage Engine** | Heavy Formula Engine (FE) bottleneck (> 40% query time spent in single-threaded FE) | Maximize Storage Engine (SE) batch processing (> 85% SE query resolution) |
| **Lakehouse Architecture** | Fragile 30-minute scheduled ETL import batch refreshes | **Microsoft Fabric Direct Lake** over Delta Parquet tables with graceful fallback to DirectQuery |
