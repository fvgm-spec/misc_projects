# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks Fundamentals
# MAGIC
# MAGIC Covers the core building blocks:
# MAGIC 1. Generate sample data with Faker
# MAGIC 2. Create DataFrames & explore schemas
# MAGIC 3. Basic transformations (select, filter, groupBy, join)
# MAGIC 4. Write & read Delta tables
# MAGIC 5. Delta features: time travel, MERGE (upsert)

# COMMAND ----------
# MAGIC %md ## 1. Generate Sample Data

# COMMAND ----------

# Install faker (only needed once per cluster)
%pip install faker -q

# COMMAND ----------

from faker import Faker
from pyspark.sql import Row
import random

fake = Faker()
Faker.seed(42)
random.seed(42)

PRODUCTS = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Mouse", "Headphones", "Webcam"]
CATEGORIES = {"Laptop": "Computers", "Phone": "Mobile", "Tablet": "Mobile",
               "Monitor": "Computers", "Keyboard": "Accessories", "Mouse": "Accessories",
               "Headphones": "Audio", "Webcam": "Accessories"}

# --- customers ---
customers = [
    Row(customer_id=i,
        name=fake.name(),
        email=fake.email(),
        country=fake.country_code(),
        signup_date=str(fake.date_between(start_date="-3y", end_date="today")))
    for i in range(1, 201)
]

# --- orders ---
orders = [
    Row(order_id=i,
        customer_id=random.randint(1, 200),
        product=random.choice(PRODUCTS),
        quantity=random.randint(1, 5),
        unit_price=round(random.uniform(10, 1500), 2),
        order_date=str(fake.date_between(start_date="-1y", end_date="today")),
        status=random.choice(["completed", "completed", "completed", "returned", "pending"]))
    for i in range(1, 1001)
]

df_customers = spark.createDataFrame(customers)
df_orders    = spark.createDataFrame(orders)

print(f"Customers: {df_customers.count()}")
print(f"Orders:    {df_orders.count()}")

# COMMAND ----------
# MAGIC %md ## 2. Explore Schemas & Preview Data

# COMMAND ----------

df_customers.printSchema()
df_customers.show(5)

# COMMAND ----------

df_orders.printSchema()
df_orders.show(5)

# COMMAND ----------
# MAGIC %md ## 3. Basic Transformations

# COMMAND ----------

from pyspark.sql.functions import col, round as spark_round, when, lit

# Add derived columns
df_orders_enriched = df_orders.withColumn(
    "total_amount", spark_round(col("quantity") * col("unit_price"), 2)
).withColumn(
    "category", when(col("product") == "Laptop",      lit("Computers"))
                .when(col("product").isin("Phone","Tablet"), lit("Mobile"))
                .when(col("product").isin("Keyboard","Mouse","Webcam"), lit("Accessories"))
                .otherwise(lit("Audio"))
)

df_orders_enriched.select("order_id", "product", "category", "quantity", "unit_price", "total_amount").show(5)

# COMMAND ----------

# Filter: only completed orders
df_completed = df_orders_enriched.filter(col("status") == "completed")
print(f"Completed orders: {df_completed.count()}")

# COMMAND ----------

# GroupBy: revenue by category
from pyspark.sql.functions import sum as spark_sum, count, avg

df_by_category = (df_completed
    .groupBy("category")
    .agg(
        count("order_id").alias("num_orders"),
        spark_sum("total_amount").alias("total_revenue"),
        avg("total_amount").alias("avg_order_value")
    )
    .orderBy(col("total_revenue").desc())
)
df_by_category.show()

# COMMAND ----------

# Join: enrich orders with customer info
df_joined = df_completed.join(df_customers, on="customer_id", how="left")
df_joined.select("order_id", "name", "country", "product", "total_amount", "order_date").show(5)

# COMMAND ----------
# MAGIC %md ## 4. Delta Tables — Write & Read

# COMMAND ----------

DB = "fundamentals_db"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {DB}")

# Write customers as Delta table
(df_customers.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(f"{DB}.customers"))

# Write orders as Delta table
(df_orders_enriched.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(f"{DB}.orders"))

print("Tables written.")
spark.sql(f"SHOW TABLES IN {DB}").show()

# COMMAND ----------

# Read back and query with SQL
spark.sql(f"""
    SELECT category, COUNT(*) AS orders, ROUND(SUM(total_amount), 2) AS revenue
    FROM {DB}.orders
    WHERE status = 'completed'
    GROUP BY category
    ORDER BY revenue DESC
""").show()

# COMMAND ----------
# MAGIC %md ## 5. Delta Features: Time Travel & MERGE

# COMMAND ----------

# Check table history
spark.sql(f"DESCRIBE HISTORY {DB}.customers").select("version", "timestamp", "operation").show(5)

# COMMAND ----------

# Time travel: read version 0
df_v0 = spark.read.format("delta").option("versionAsOf", 0).table(f"{DB}.customers")
print(f"Version 0 row count: {df_v0.count()}")

# COMMAND ----------

# MERGE (upsert): update one customer, insert a new one
from pyspark.sql.functions import current_timestamp

updates = spark.createDataFrame([
    Row(customer_id=1,   name="Updated Name",  email="updated@example.com", country="US", signup_date="2024-01-01"),
    Row(customer_id=999, name=fake.name(),      email=fake.email(),          country="BR", signup_date="2025-01-01"),
])

updates.createOrReplaceTempView("updates")

spark.sql(f"""
    MERGE INTO {DB}.customers AS target
    USING updates AS source
    ON target.customer_id = source.customer_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")

print(f"Customers after MERGE: {spark.table(f'{DB}.customers').count()}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Summary
# MAGIC | Concept | What we did |
# MAGIC |---|---|
# MAGIC | Faker | Generated 200 customers + 1000 orders |
# MAGIC | DataFrame | Schema, show, printSchema |
# MAGIC | Transformations | withColumn, filter, groupBy, join |
# MAGIC | Delta write | saveAsTable with overwrite |
# MAGIC | SQL on Delta | SELECT with GROUP BY |
# MAGIC | Time travel | versionAsOf |
# MAGIC | MERGE | Upsert with MATCHED / NOT MATCHED |
