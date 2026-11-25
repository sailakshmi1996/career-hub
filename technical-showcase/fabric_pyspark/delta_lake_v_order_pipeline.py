"""
================================================================================
MICROSOFT FABRIC & PYSPARK LAKEHOUSE PIPELINE (INCREMENTAL MERGE + V-ORDER)
Author: Sai Lakshmi Elusuri
Purpose: Incremental Silver-to-Gold Delta Lake upsert resolving integer
         surrogate keys, enforcing pre-write data quality checks, enabling
         write-time V-Order for Direct Lake paging, and applying Liquid Clustering.
Environment: Microsoft Fabric Runtime 1.3+ (Apache Spark 3.5, Delta Lake 3.2)
================================================================================
"""

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def configure_fabric_spark() -> SparkSession:
    """Configures Spark session with V-Order and Delta write optimization for Direct Lake."""
    return (
        SparkSession.builder
        .appName("Fabric_Gold_Sales_Incremental_Merge")
        .config("spark.sql.parquet.vorder.enabled", "true")
        .config("spark.microsoft.delta.optimizeWrite.enabled", "true")
        .config("spark.microsoft.delta.autoCompact.enabled", "true")
        .getOrCreate()
    )


def assert_quality_checks(df: DataFrame) -> None:
    """Validates grain uniqueness and non-null surrogate keys before Gold merge."""
    total_rows = df.count()
    if total_rows == 0:
        return

    invalid_rows = df.filter(
        F.col("SalesNaturalId").isNull()
        | F.col("DateKey").isNull()
        | (F.col("Revenue_EUR") < 0)
    ).count()
    if invalid_rows > 0:
        raise ValueError(f"Data quality check failed: {invalid_rows} invalid rows detected.")

    dup_count = df.groupBy("SalesNaturalId").count().filter(F.col("count") > 1).count()
    if dup_count > 0:
        raise ValueError(f"Grain violation: {dup_count} duplicate SalesNaturalId keys found.")


def build_gold_batch(spark: SparkSession, silver_table: str, watermark_ts: str) -> DataFrame:
    """
    Reads incremental Silver rows since watermark, deduplicates latest revision,
    and resolves integer surrogate keys from Gold dimensions (-1 fallback for unknown).
    """
    dedup_window = Window.partitionBy("transaction_id").orderBy(
        F.col("revision_sequence").desc(), F.col("updated_at").desc()
    )

    df_silver_inc = (
        spark.read.table(silver_table)
        .filter((F.col("updated_at") > F.lit(watermark_ts)) & (F.col("status_code") == "SETTLED"))
        .withColumn("_rn", F.row_number().over(dedup_window))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )

    dim_customer = spark.read.table("gold_dim_customer").filter(F.col("is_current") == True).select(
        F.col("customer_account_id"), F.col("CustomerKey")
    )
    dim_product = spark.read.table("gold_dim_product").select("product_id", "ProductKey")
    dim_store = spark.read.table("gold_dim_geography").select("store_id", "StoreKey")

    return (
        df_silver_inc.alias("s")
        .join(dim_customer.alias("c"), "customer_account_id", "left")
        .join(dim_product.alias("p"), "product_id", "left")
        .join(dim_store.alias("g"), "store_id", "left")
        .select(
            F.col("s.transaction_id").alias("SalesNaturalId"),
            F.date_format(F.col("s.transaction_timestamp"), "yyyyMMdd").cast("int").alias("DateKey"),
            F.date_format(F.col("s.transaction_timestamp"), "HHmmss").cast("int").alias("TimeKey"),
            F.coalesce(F.col("c.CustomerKey"), F.lit(-1)).cast("int").alias("CustomerKey"),
            F.coalesce(F.col("p.ProductKey"), F.lit(-1)).cast("int").alias("ProductKey"),
            F.coalesce(F.col("g.StoreKey"), F.lit(-1)).cast("int").alias("StoreKey"),
            F.col("s.net_amount_eur").cast("decimal(18, 2)").alias("Revenue_EUR"),
            F.col("s.tax_amount_eur").cast("decimal(18, 2)").alias("Tax_EUR"),
            F.col("s.updated_at").alias("SilverUpdatedAt"),
        )
    )


def merge_into_gold(spark: SparkSession, df_batch: DataFrame, gold_table: str) -> None:
    """Performs idempotent Delta MERGE INTO with V-Order and Liquid Clustering."""
    assert_quality_checks(df_batch)

    if not spark.catalog.tableExists(gold_table):
        (
            df_batch.write.format("delta")
            .option("delta.enableChangeDataFeed", "true")
            .clusterBy("DateKey", "StoreKey")
            .saveAsTable(gold_table)
        )
        return

    target = DeltaTable.forName(spark, gold_table)
    (
        target.alias("t")
        .merge(df_batch.alias("s"), "t.SalesNaturalId = s.SalesNaturalId AND t.DateKey = s.DateKey")
        .whenMatchedUpdateAll(condition="s.SilverUpdatedAt > t.SilverUpdatedAt")
        .whenNotMatchedInsertAll()
        .execute()
    )


if __name__ == "__main__":
    spark_session = configure_fabric_spark()
    batch = build_gold_batch(spark_session, "silver_sales_transactions", "2026-11-01 00:00:00")
    merge_into_gold(spark_session, batch, "gold_fact_sales_telemetry")
