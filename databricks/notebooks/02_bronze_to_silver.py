# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze to Silver Layer Transformation
# MAGIC 
# MAGIC This notebook demonstrates:
# MAGIC - Data cleaning and validation
# MAGIC - Schema enforcement
# MAGIC - Data type conversions
# MAGIC - Business rule applications
# MAGIC - Delta Lake features (ACID transactions, time travel)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import *

# Set database context
spark.sql("USE retail_analytics")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read Bronze Layer Data

# COMMAND ----------

# Read bronze tables
df_bronze_orders = spark.table("retail_analytics.bronze_orders")
df_bronze_customers = spark.table("retail_analytics.bronze_customers")
df_bronze_products = spark.table("retail_analytics.bronze_products")

print("Bronze layer data loaded:")
print(f"Orders: {df_bronze_orders.count()} records")
print(f"Customers: {df_bronze_customers.count()} records")
print(f"Products: {df_bronze_products.count()} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Cleaning - Orders

# COMMAND ----------

# Clean and validate orders data
df_silver_orders = df_bronze_orders \
    .filter(col("order_id").isNotNull()) \
    .filter(col("quantity") > 0) \
    .filter(col("unit_price") > 0) \
    .withColumn("order_date", to_date(col("order_date"), "yyyy-MM-dd")) \
    .withColumn("total_amount", col("quantity") * col("unit_price")) \
    .withColumn("processed_timestamp", current_timestamp()) \
    .filter(col("status").isin(["completed", "pending", "cancelled"]))

# Add data quality flags
df_silver_orders = df_silver_orders \
    .withColumn("is_valid_order", 
                when((col("quantity") > 0) & (col("unit_price") > 0) & 
                     (col("order_date").isNotNull()), True).otherwise(False)) \
    .withColumn("order_year", year(col("order_date"))) \
    .withColumn("order_month", month(col("order_date"))) \
    .withColumn("order_quarter", quarter(col("order_date")))

print(f"Silver orders after cleaning: {df_silver_orders.count()} records")
display(df_silver_orders.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Cleaning - Customers

# COMMAND ----------

# Clean customers data
df_silver_customers = df_bronze_customers \
    .filter(col("customer_id").isNotNull()) \
    .filter(col("email").contains("@")) \
    .withColumn("registration_date", to_date(col("registration_date"), "yyyy-MM-dd")) \
    .withColumn("full_name", concat(col("first_name"), lit(" "), col("last_name"))) \
    .withColumn("processed_timestamp", current_timestamp()) \
    .withColumn("customer_tenure_days", 
                datediff(current_date(), col("registration_date")))

print(f"Silver customers after cleaning: {df_silver_customers.count()} records")
display(df_silver_customers.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Cleaning - Products

# COMMAND ----------

# Clean products data
df_silver_products = df_bronze_products \
    .filter(col("product_id").isNotNull()) \
    .filter(col("retail_price") > col("cost_price")) \
    .withColumn("profit_margin", 
                round((col("retail_price") - col("cost_price")) / col("retail_price") * 100, 2)) \
    .withColumn("processed_timestamp", current_timestamp()) \
    .withColumn("price_category", 
                when(col("retail_price") < 50, "Budget")
                .when(col("retail_price") < 200, "Mid-range")
                .otherwise("Premium"))

print(f"Silver products after cleaning: {df_silver_products.count()} records")
display(df_silver_products.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Validation

# COMMAND ----------

# Comprehensive data quality checks
print("=== Data Quality Report - Silver Layer ===")

# Orders validation
invalid_orders = df_silver_orders.filter(col("is_valid_order") == False).count()
print(f"Invalid orders: {invalid_orders}")

# Check for duplicates
duplicate_orders = df_silver_orders.groupBy("order_id").count().filter(col("count") > 1).count()
print(f"Duplicate order IDs: {duplicate_orders}")

# Date range validation
date_stats = df_silver_orders.select(
    min("order_date").alias("min_date"),
    max("order_date").alias("max_date"),
    count("*").alias("total_orders")
).collect()[0]

print(f"Order date range: {date_stats['min_date']} to {date_stats['max_date']}")
print(f"Total valid orders: {date_stats['total_orders']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Silver Layer Tables

# COMMAND ----------

# Write silver orders with Delta Lake features
df_silver_orders.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable("retail_analytics.silver_orders")

# Write silver customers
df_silver_customers.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable("retail_analytics.silver_customers")

# Write silver products
df_silver_products.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable("retail_analytics.silver_products")

print("✅ Silver layer tables created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Delta Lake Features Demo

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Show table history (Delta Lake time travel)
# MAGIC DESCRIBE HISTORY retail_analytics.silver_orders;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Table details and statistics
# MAGIC DESCRIBE DETAIL retail_analytics.silver_orders;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Enriched Silver Views

# COMMAND ----------

# Create enriched order view with customer and product information
enriched_orders_query = """
CREATE OR REPLACE VIEW retail_analytics.silver_orders_enriched AS
SELECT 
    o.order_id,
    o.customer_id,
    c.full_name as customer_name,
    c.customer_segment,
    o.product_id,
    p.product_name,
    p.category as product_category,
    o.quantity,
    o.unit_price,
    o.total_amount,
    p.cost_price,
    (o.total_amount - (p.cost_price * o.quantity)) as profit,
    o.order_date,
    o.order_year,
    o.order_month,
    o.order_quarter,
    o.status,
    o.processed_timestamp
FROM retail_analytics.silver_orders o
LEFT JOIN retail_analytics.silver_customers c ON o.customer_id = c.customer_id
LEFT JOIN retail_analytics.silver_products p ON o.product_id = p.product_id
WHERE o.is_valid_order = true
"""

spark.sql(enriched_orders_query)
print("✅ Enriched orders view created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Validation Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
#     'Orders' as table_name,
#     COUNT(*) as record_count,
#     COUNT(DISTINCT customer_id) as unique_customers,
#     COUNT(DISTINCT product_id) as unique_products,
#     SUM(total_amount) as total_revenue
# FROM retail_analytics.silver_orders
# WHERE is_valid_order = true
# 
# UNION ALL
# 
# SELECT 
#     'Customers' as table_name,
#     COUNT(*) as record_count,
#     COUNT(DISTINCT customer_segment) as unique_segments,
#     NULL as unique_products,
#     AVG(customer_tenure_days) as avg_tenure_days
# FROM retail_analytics.silver_customers
# 
# UNION ALL
# 
# SELECT 
#     'Products' as table_name,
#     COUNT(*) as record_count,
#     COUNT(DISTINCT category) as unique_categories,
#     NULL as unique_products,
#     AVG(profit_margin) as avg_profit_margin
# FROM retail_analytics.silver_products;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("🎉 Bronze to Silver Transformation Complete!")
print("\nSilver layer achievements:")
print("- ✅ Data cleaning and validation")
print("- ✅ Schema standardization")
print("- ✅ Business rule enforcement")
print("- ✅ Data quality flags")
print("- ✅ Delta Lake ACID transactions")
print("- ✅ Enriched views for analytics")
print("\nNext: Run notebook 03_silver_to_gold.py for business metrics and aggregations")
