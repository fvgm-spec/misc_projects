# Databricks notebook source
# MAGIC %md
# MAGIC # Delta Live Tables Pipeline Example
# MAGIC 
# MAGIC This notebook demonstrates Delta Live Tables (DLT) syntax for creating a data pipeline.
# MAGIC Note: Full DLT functionality requires Databricks Pro/Premium, but this shows the concepts.

# COMMAND ----------

import dlt
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze Layer - Raw Data Ingestion

# COMMAND ----------

@dlt.table(
    name="bronze_orders_stream",
    comment="Raw orders data from source systems"
)
def bronze_orders():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/pipelines/retail_analytics/schema/orders")
        .load("/FileStore/streaming_data/orders/")
        .withColumn("ingestion_timestamp", current_timestamp())
        .withColumn("source_file", input_file_name())
    )

@dlt.table(
    name="bronze_customers",
    comment="Customer master data"
)
def bronze_customers():
    return spark.table("retail_analytics.bronze_customers")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Layer - Cleaned and Validated Data

# COMMAND ----------

@dlt.table(
    name="silver_orders_clean",
    comment="Cleaned and validated orders data"
)
@dlt.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_drop("positive_quantity", "quantity > 0")
@dlt.expect_or_drop("positive_price", "unit_price > 0")
def silver_orders():
    return (
        dlt.read_stream("bronze_orders_stream")
        .filter(col("order_id").isNotNull())
        .filter(col("quantity") > 0)
        .filter(col("unit_price") > 0)
        .withColumn("order_date", to_date(col("order_date"), "yyyy-MM-dd"))
        .withColumn("total_amount", col("quantity") * col("unit_price"))
        .withColumn("processed_timestamp", current_timestamp())
        .select(
            "order_id",
            "customer_id", 
            "product_id",
            "quantity",
            "unit_price",
            "total_amount",
            "order_date",
            "status",
            "processed_timestamp"
        )
    )

@dlt.table(
    name="silver_customers_enriched",
    comment="Enriched customer data with derived attributes"
)
def silver_customers():
    return (
        dlt.read("bronze_customers")
        .filter(col("customer_id").isNotNull())
        .filter(col("email").contains("@"))
        .withColumn("registration_date", to_date(col("registration_date"), "yyyy-MM-dd"))
        .withColumn("full_name", concat(col("first_name"), lit(" "), col("last_name")))
        .withColumn("customer_tenure_days", datediff(current_date(), col("registration_date")))
        .withColumn("processed_timestamp", current_timestamp())
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer - Business Metrics

# COMMAND ----------

@dlt.table(
    name="gold_daily_sales_metrics",
    comment="Daily aggregated sales metrics for reporting"
)
def gold_daily_metrics():
    return (
        dlt.read("silver_orders_clean")
        .filter(col("status") == "completed")
        .groupBy("order_date")
        .agg(
            count("order_id").alias("daily_orders"),
            sum("total_amount").alias("daily_revenue"),
            countDistinct("customer_id").alias("active_customers"),
            avg("total_amount").alias("avg_order_value")
        )
        .withColumn("processed_timestamp", current_timestamp())
    )

@dlt.table(
    name="gold_customer_lifetime_value",
    comment="Customer lifetime value calculations"
)
def gold_customer_ltv():
    orders = dlt.read("silver_orders_clean").filter(col("status") == "completed")
    customers = dlt.read("silver_customers_enriched")
    
    return (
        orders.groupBy("customer_id")
        .agg(
            count("order_id").alias("total_orders"),
            sum("total_amount").alias("lifetime_value"),
            avg("total_amount").alias("avg_order_value"),
            min("order_date").alias("first_order_date"),
            max("order_date").alias("last_order_date")
        )
        .join(customers.select("customer_id", "full_name", "customer_segment"), "customer_id")
        .withColumn("customer_lifetime_days", 
                   datediff(col("last_order_date"), col("first_order_date")) + 1)
        .withColumn("processed_timestamp", current_timestamp())
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Monitoring

# COMMAND ----------

@dlt.table(
    name="data_quality_metrics",
    comment="Data quality monitoring metrics"
)
def data_quality_monitoring():
    bronze_count = dlt.read_stream("bronze_orders_stream").count()
    silver_count = dlt.read("silver_orders_clean").count()
    
    return spark.createDataFrame([
        ("bronze_orders", bronze_count, current_timestamp()),
        ("silver_orders", silver_count, current_timestamp())
    ], ["table_name", "record_count", "check_timestamp"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline Configuration Notes
# MAGIC 
# MAGIC To use this DLT pipeline:
# MAGIC 1. Create a new Delta Live Tables pipeline in Databricks
# MAGIC 2. Add this notebook as a library
# MAGIC 3. Configure target database and storage location
# MAGIC 4. Set up appropriate cluster configuration
# MAGIC 5. Schedule pipeline runs or trigger manually
# MAGIC 
# MAGIC Key DLT Features Demonstrated:
# MAGIC - `@dlt.table()` decorator for table definitions
# MAGIC - `@dlt.expect_or_drop()` for data quality constraints
# MAGIC - `dlt.read()` and `dlt.read_stream()` for reading data
# MAGIC - Streaming and batch processing patterns
# MAGIC - Automatic dependency management
