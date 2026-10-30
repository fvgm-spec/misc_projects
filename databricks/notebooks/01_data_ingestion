# Databricks notebook source
# MAGIC %md
# MAGIC # Data Ingestion - Bronze Layer
# MAGIC 
# MAGIC This notebook demonstrates data ingestion patterns in Databricks Community Edition:
# MAGIC - File upload to DBFS
# MAGIC - CSV/JSON data reading
# MAGIC - Delta table creation
# MAGIC - Data validation

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd

# Initialize Spark session (already available as 'spark')
print(f"Spark version: {spark.version}")
print("Databricks Community Edition")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Database and Set Context

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE IF NOT EXISTS retail_analytics
# MAGIC COMMENT 'Retail analytics database for sample project';
# MAGIC 
# MAGIC USE retail_analytics;
# MAGIC 
# MAGIC SHOW DATABASES;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Sample Data

# COMMAND ----------

# Generate sample sales data
from datetime import datetime, timedelta
import random
import builtins

# Create sample data
sample_data = []
for i in range(1000):
    sample_data.append({
        'order_id': f'ORD-{i+1:06d}',
        'customer_id': f'CUST-{random.randint(1, 200):05d}',
        'product_id': f'PROD-{random.randint(1, 50):03d}',
        'quantity': random.randint(1, 5),
        'unit_price': builtins.round(random.uniform(10.0, 500.0), 2),
        'order_date': (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
        'status': random.choice(['completed', 'pending', 'cancelled'])
    })

# Convert to Spark DataFrame
schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("order_date", StringType(), True),
    StructField("status", StringType(), True)
])

df_orders = spark.createDataFrame(sample_data, schema)
display(df_orders.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Checks

# COMMAND ----------

# Basic data quality checks
print("=== Data Quality Report ===")
print(f"Total records: {df_orders.count()}")
print(f"Columns: {len(df_orders.columns)}")
print("\nNull value counts:")
df_orders.select([count(when(col(c).isNull(), c)).alias(c) for c in df_orders.columns]).show()

print("\nData types:")
df_orders.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save to Bronze Layer (Delta Table)

# COMMAND ----------

# Add ingestion metadata
df_bronze = df_orders.withColumn("ingestion_timestamp", current_timestamp()) \
                    .withColumn("source_file", lit("sample_generation")) \
                    .withColumn("data_quality_flag", lit("valid"))

# Drop existing table if it exists to avoid schema conflicts
spark.sql("DROP TABLE IF EXISTS retail_analytics.bronze_orders")

# Write to Delta table
df_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable("retail_analytics.bronze_orders")

print("✅ Data successfully written to bronze_orders table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Bronze Layer

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
#     COUNT(*) as total_records,
#     COUNT(DISTINCT customer_id) as unique_customers,
#     COUNT(DISTINCT product_id) as unique_products,
#     MIN(order_date) as earliest_order,
#     MAX(order_date) as latest_order
# FROM retail_analytics.bronze_orders;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Additional Sample Tables

# COMMAND ----------

# Customer data
customers_data = []
for i in range(1, 201):
    customers_data.append({
        'customer_id': f'CUST-{i:05d}',
        'first_name': f'Customer{i}',
        'last_name': f'LastName{i}',
        'email': f'customer{i}@email.com',
        'registration_date': (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime('%Y-%m-%d'),
        'customer_segment': random.choice(['Premium', 'Standard', 'Basic'])
    })

df_customers = spark.createDataFrame(customers_data)
df_customers.write.format("delta").mode("overwrite").saveAsTable("retail_analytics.bronze_customers")

# Product data
products_data = []
categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
for i in range(1, 51):
    products_data.append({
        'product_id': f'PROD-{i:03d}',
        'product_name': f'Product {i}',
        'category': random.choice(categories),
        'cost_price': round(random.uniform(5.0, 200.0), 2),
        'retail_price': round(random.uniform(10.0, 500.0), 2),
        'supplier_id': f'SUP-{random.randint(1, 10):02d}'
    })

df_products = spark.createDataFrame(products_data)
df_products.write.format("delta").mode("overwrite").saveAsTable("retail_analytics.bronze_products")

print("✅ All bronze tables created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Show all tables in the database
# MAGIC SHOW TABLES IN retail_analytics;

# COMMAND ----------

print("🎉 Data Ingestion Complete!")
print("Bronze layer tables created:")
print("- bronze_orders: Sales transaction data")
print("- bronze_customers: Customer information")
print("- bronze_products: Product catalog")
print("\nNext: Run notebook 02_bronze_to_silver.py for data cleaning and validation")
