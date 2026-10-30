# Fix for SCHEMA_NOT_FOUND error in Databricks

# Option 1: Create the schema first
spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.retail_analytics")

# Option 2: Use a different existing schema (like default)
df_orders.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("default.bronze_orders")

# Option 3: Write to a path instead of a table
df_orders.write \
    .format("delta") \
    .mode("overwrite") \
    .save("/tmp/bronze_orders")

print("✅ Data successfully written to bronze_orders table")
