-- ===============================================================================
-- ORACLE SQL PRODUCTION STAGING QUERY
-- Author: Sai Lakshmi Elusuri
-- Purpose: High-throughput incremental data extraction for Power BI Ingestion
-- Key Optimizations: Partition-pruned predicates, CTE deduplication, Query Folding
-- ===============================================================================

WITH RankedTelemetry AS (
    SELECT
        t.transaction_id,
        t.customer_account_id,
        t.store_id,
        t.transaction_timestamp,
        TRUNC(t.transaction_timestamp) AS date_key,
        t.net_amount_eur,
        t.tax_amount_eur,
        t.status_code,
        -- Single-scan deduplication selecting latest revision state
        ROW_NUMBER() OVER (
            PARTITION BY t.transaction_id
            ORDER BY t.revision_sequence DESC, t.transaction_timestamp DESC
        ) AS row_rank
    FROM
        erp_owner.sales_transactions_partitioned t
    WHERE
        -- Keep timestamp column unwrapped (sargable) for Oracle partition pruning
        -- Mapped directly from Power BI RangeStart / RangeEnd Incremental Refresh parameters
        t.transaction_timestamp >= TO_TIMESTAMP(:RangeStart, 'YYYY-MM-DD HH24:MI:SS')
        AND t.transaction_timestamp < TO_TIMESTAMP(:RangeEnd, 'YYYY-MM-DD HH24:MI:SS')
        AND t.status_code IN ('SETTLED', 'POSTED', 'AUDITED')
),
AggregatedLineItems AS (
    SELECT
        rt.transaction_id,
        rt.customer_account_id,
        rt.store_id,
        rt.date_key,
        rt.net_amount_eur,
        rt.tax_amount_eur,
        NVL(cust.tier_code, 'STANDARD') AS customer_tier,
        DENSE_RANK() OVER (
            PARTITION BY rt.date_key
            ORDER BY rt.net_amount_eur DESC
        ) AS daily_revenue_rank
    FROM
        RankedTelemetry rt
    LEFT JOIN
        erp_owner.dim_customer_account cust
        ON rt.customer_account_id = cust.customer_account_id
    WHERE
        rt.row_rank = 1 -- Only the latest verified transaction state
)
SELECT
    transaction_id,
    customer_account_id,
    store_id,
    date_key,
    net_amount_eur,
    tax_amount_eur,
    customer_tier,
    daily_revenue_rank,
    SYSDATE AS etl_ingestion_timestamp
FROM
    AggregatedLineItems
ORDER BY
    date_key, transaction_id;
