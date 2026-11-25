# Senior Power BI & Microsoft Fabric Technical Showcase

**Reference architectural patterns by Sai Lakshmi Elusuri**

This folder holds clean, NDA-safe reference code illustrating the semantic modeling, DAX optimization, Oracle SQL query folding, and Microsoft Fabric Lakehouse patterns I deploy in enterprise BI delivery. Production `.pbix` files and client datasets remain confidential under NDA; anonymized synthetic `.pbip` demonstrations are in progress to pair with these code artifacts.

## Contents

1. **DAX Calculation Groups, Safe FX Translation & VertiPaq Patterns** (`dax/calculation_groups_and_semi_additive.dax`)
   - Time Intelligence Calculation Group (`Precedence = 20`) operating on `'Dim_Date'[Date]` while Fact joins on integer `DateKey` (`YYYYMMDD`).
   - Daily-grain Currency Calculation Group (`Precedence = 10`) using `SUMX(VALUES('Dim_Date'[DateKey]), ...)` with explicit ratio-measure protection (`NOT ISSELECTEDMEASURE(...)`) and strict `BLANK()` handling on missing rates.
   - Semantically equivalent **Slow (FE iteration)** vs. **Tuned (SE vector scan)** benchmark pair (`FILTER('Fact_Sales', ...)` vs. `KEEPFILTERS(...)`).
   - Semi-additive snapshot balance measure without redundant `CALCULATE` wrappers.

2. **Oracle SQL Partition-Pruned View for Power Query Folding** (`sql/oracle_incremental_staging_cte.sql`)
   - Exposes deduplicated latest ERP revisions (`ROW_NUMBER()`) in a foldable view (`vw_sales_latest_revision`) with an unwrapped `transaction_timestamp` column so Power BI `RangeStart` / `RangeEnd` filters push directly to Oracle partition pruning without forcing unnecessary `ORDER BY` PGA sorts.

3. **Microsoft Fabric PySpark Incremental Delta Merge & V-Order** (`fabric_pyspark/delta_lake_v_order_pipeline.py`)
   - Watermarked Silver-to-Gold incremental transform resolving true integer surrogate keys (`CustomerKey`, `ProductKey`, `StoreKey`) with `-1` unknown-member fallback.
   - Pre-write data-quality assertions (null keys, negative amounts, grain uniqueness).
   - Idempotent Delta `MERGE INTO` upsert with `spark.sql.parquet.vorder.enabled = true`, `optimizeWrite`, and Liquid Clustering (`clusterBy("DateKey", "StoreKey")`) for Fabric Direct Lake consumption.

## Direct Lake vs. Import vs. DirectQuery Guardrails

| Mode | When Chosen | Memory & Freshness Behavior | Fallback / Guardrail |
| :--- | :--- | :--- | :--- |
| **VertiPaq Import** | Sub-second SLA across complex DAX, incremental ERP tables (`RangeStart`/`RangeEnd`), and standard F-SKU/Pro capacities | Full in-memory columnar dictionary & RLE compression; predictable warm cache | Bound by capacity memory and scheduled/XMLA partition refresh windows |
| **Direct Lake (OneLake)** | Large Fabric Gold Delta tables (`V-Order`) needing near-real-time freshness without Import duplication | Dynamically pages Delta Parquet columns into VertiPaq memory on demand | Transparently falls back to **DirectQuery** over the SQL Analytics Endpoint if capacity memory guardrails, SQL views, or unsupported DAX/RLS patterns trigger |
| **DirectQuery** | Strict real-time operational reads or tables exceeding memory limits | Pushes SQL queries directly to source engine (`Oracle` / `Fabric SQL Endpoint`) | Sensitive to source latency, concurrency, and high-cardinality joins |
