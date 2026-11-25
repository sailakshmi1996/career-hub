-- ===============================================================================
-- ORACLE SQL PARTITION-PRUNED STAGING VIEW FOR POWER BI QUERY FOLDING
-- Author: Sai Lakshmi Elusuri
-- Purpose: Expose latest deduplicated ERP revisions via a foldable view so
--          Power BI Incremental Refresh (RangeStart / RangeEnd in Power Query M)
--          pushes sargable timestamp predicates down to Oracle partition pruning.
-- Notes:
--   * No outer ORDER BY (VertiPaq re-sorts during columnar encoding; sorting in
--     Oracle wastes PGA memory during extraction).
--   * Pair in Power Query M with:
--       Table.SelectRows(Source, each [transaction_timestamp] >= RangeStart
--                                 and [transaction_timestamp] < RangeEnd)
--     or Value.NativeQuery(..., null, [EnableFolding = true]) over a subquery.
-- ===============================================================================

CREATE OR REPLACE VIEW erp_owner.vw_sales_latest_revision AS
WITH RankedTelemetry AS (
    SELECT
        t.transaction_id,
        t.customer_account_id,
        t.store_id,
        t.product_id,
        t.transaction_timestamp,
        CAST(TO_CHAR(t.transaction_timestamp, 'YYYYMMDD') AS NUMBER(8)) AS date_key,
        t.net_amount_eur,
        t.tax_amount_eur,
        t.status_code,
        ROW_NUMBER() OVER (
            PARTITION BY t.transaction_id
            ORDER BY t.revision_sequence DESC, t.transaction_timestamp DESC
        ) AS row_rank
    FROM
        erp_owner.sales_transactions_partitioned t
    WHERE
        t.status_code IN ('SETTLED', 'POSTED', 'AUDITED')
)
SELECT
    rt.transaction_id,
    rt.customer_account_id,
    rt.store_id,
    rt.product_id,
    -- Kept unwrapped (sargable) so Power BI RangeStart/RangeEnd filters prune partitions
    rt.transaction_timestamp,
    rt.date_key,
    rt.net_amount_eur,
    rt.tax_amount_eur,
    NVL(cust.tier_code, 'STANDARD') AS customer_tier
FROM
    RankedTelemetry rt
LEFT JOIN
    erp_owner.dim_customer_account cust
    ON rt.customer_account_id = cust.customer_account_id
WHERE
    rt.row_rank = 1;
