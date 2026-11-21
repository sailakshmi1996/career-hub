"""
================================================================================
MICROSOFT FABRIC & PYSPARK LAKEHOUSE PIPELINE
Author: Sai Lakshmi Elusuri
Purpose: Silver to Gold Lakehouse Transformation with V-Order for Direct Lake
Environment: Microsoft Fabric Lakehouse / Azure Synapse Spark 3.4+
================================================================================
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from delta.tables import DeltaTable

def configure_fabric_spark() -> SparkSession:
    """Configures Spark session with V-Order columnar optimization enabled."""
    return (
        SparkSession.builder
        .appName("Fabric_Gold_Sales_DirectLake_Optimizer")
        .config("spark.sql.parquet.vorder.enabled", "true") # Critical for Direct Lake read performance
        .config("spark.microsoft.delta.optimizeWrite.enabled", "true")
        .config("spark.microsoft.delta.autoCompact.enabled", "true")
        .getOrCreate()
    )

def transform_silver_to_gold(spark: SparkSession, silver_path: str, gold_table: str):
    """
    Transforms normalized Silver transactions into a Kimball Star Schema Gold Fact Table.
    Applies surrogate keys, prunes unnecessary string columns, and writes with V-Order.
    """
    # 1. Read Silver Delta Table from OneLake
    df_silver = spark.read.format("delta").load(silver_path)

    # 2. Curate Fact Sales Telemetry
    df_gold_fact = (
        df_silver
        .filter(F.col("status_code") == "SETTLED")
        # Split composite datetime into DateKey and TimeKey for VertiPaq dictionary compression
        .withColumn("DateKey", F.date_format(F.col("transaction_timestamp"), "yyyyMMdd").cast("int"))
        .withColumn("TimeKey", F.date_format(F.col("transaction_timestamp"), "HHmmss").cast("int"))
        .withColumn("Revenue_EUR", F.col("net_amount_eur").cast("decimal(18, 2)"))
        .select(
            F.col("transaction_id").alias("SalesKey"),
            F.col("DateKey"),
            F.col("TimeKey"),
            F.col("customer_account_id").alias("CustomerKey"),
            F.col("store_id").alias("StoreKey"),
            F.col("Revenue_EUR"),
            F.col("tax_amount_eur").alias("Tax_EUR")
        )
    )

    # 3. Write directly into Lakehouse Gold table in Delta Parquet format
    (
        df_gold_fact.write
        .format("delta")
        .mode("overwrite")
        .option("mergeSchema", "true")
        .saveAsTable(gold_table)
    )

    # 4. Apply Liquid Clustering on High-Selectivity Columns
    spark.sql(f"OPTIMIZE {gold_table} ZORDER BY (DateKey, CustomerKey)")

if __name__ == "__main__":
    spark = configure_fabric_spark()
    silver_lakehouse_path = "abfss://workspace@onelake.dfs.fabric.microsoft.com/Analytics.Lakehouse/Tables/silver_sales"
    gold_target_table = "gold_fact_sales_telemetry"
    transform_silver_to_gold(spark, silver_lakehouse_path, gold_target_table)
