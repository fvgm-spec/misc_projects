# Complete working solution for Databricks notebook

# Cell 1: Imports and setup
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd

# Cell 2: Generate sample data (FIXED VERSION)
import random
from datetime import datetime, timedelta

# Generate sample sales data
sample_data = []
for i in range(1000):
    sample_data.append({
        'order_id': f'ORD-{i+1:06d}',
        'customer_id': f'CUST-{random.randint(1, 200):05d}',
        'product_id': f'PROD-{random.randint(1, 50):03d}',
        'quantity': random.randint(1, 5),
        'unit_price': round(random.uniform(10.0, 500.0), 2),
        'order_date': (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
        'status': random.choice(['completed', 'pending', 'cancelled'])
    })

print(f"✅ Generated {len(sample_data)} sample records")

# Cell 3: Create DataFrame with explicit schema
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

# Cell 4: Create schema and save table
spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.retail_analytics")

df_orders.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.retail_analytics.bronze_orders")

print("✅ Data successfully written to bronze_orders table")
