# Databricks notebook source
# MAGIC %md
# MAGIC # Data Ingestion - Bronze Layer (Community Edition)

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd

# Initialize Spark session (already available as 'spark')
print(f"Spark version: {spark.version}")
print("Databricks Community Edition")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE IF NOT EXISTS retail_analytics
# MAGIC COMMENT 'Retail analytics database for sample project';
# MAGIC 
# MAGIC USE retail_analytics;
# MAGIC 
# MAGIC SHOW DATABASES;

# COMMAND ----------

# Generate sample sales data
from datetime import datetime, timedelta
import random

# Create sample data
sample_data = []
for i in range(100):  # Reduced for faster execution
    sample_data.append({
        'order_id': f'ORD-{i+1:06d}',
        'customer_id': f'CUST-{random.randint(1, 20):05d}',
        'product_id': f'PROD-{random.randint(1, 10):03d}',
        'quantity': random.randint(1, 3),
        'unit_price': round(random.uniform(10.0, 100.0), 2),
        'order_date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
        'status': random.choice(['completed', 'pending'])
    })

# Convert to Spark DataFrame
df_orders = spark.createDataFrame(sample_data)
display(df_orders.limit(10))

# COMMAND ----------

# Save to Delta table
df_orders.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("retail_analytics.bronze_orders")

print("✅ Data successfully written to bronze_orders table")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) as total_records FROM retail_analytics.bronze_orders;
