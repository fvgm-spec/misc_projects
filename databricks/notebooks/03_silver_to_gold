# Databricks notebook source
# MAGIC %md
# MAGIC # Silver to Gold Layer - Business Metrics
# MAGIC 
# MAGIC This notebook creates business-ready datasets:
# MAGIC - Customer analytics and segmentation
# MAGIC - Product performance metrics
# MAGIC - Sales KPIs and trends
# MAGIC - Revenue analysis
# MAGIC - Cohort analysis

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# Set database context
spark.sql("USE retail_analytics")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Silver Layer Data

# COMMAND ----------

# Load silver tables and enriched view
df_orders = spark.table("retail_analytics.silver_orders_enriched")
df_customers = spark.table("retail_analytics.silver_customers")
df_products = spark.table("retail_analytics.silver_products")

print("Silver layer data loaded for gold transformations")
print(f"Enriched orders: {df_orders.count()} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer 1: Customer Analytics

# COMMAND ----------

# Customer lifetime value and behavior metrics
customer_metrics = df_orders.groupBy("customer_id", "customer_name", "customer_segment") \
    .agg(
        count("order_id").alias("total_orders"),
        sum("total_amount").alias("total_spent"),
        avg("total_amount").alias("avg_order_value"),
        sum("quantity").alias("total_items_purchased"),
        countDistinct("product_category").alias("categories_purchased"),
        min("order_date").alias("first_order_date"),
        max("order_date").alias("last_order_date"),
        sum("profit").alias("total_profit_generated")
    ) \
    .withColumn("customer_lifetime_days", 
                datediff(col("last_order_date"), col("first_order_date")) + 1) \
    .withColumn("order_frequency", 
                col("total_orders") / (col("customer_lifetime_days") / 30.0)) \
    .withColumn("profit_margin_pct", 
                round(col("total_profit_generated") / col("total_spent") * 100, 2))

# Customer segmentation based on RFM analysis
window_spec = Window.orderBy(col("total_spent").desc())
customer_analytics = customer_metrics \
    .withColumn("spending_rank", row_number().over(window_spec)) \
    .withColumn("customer_value_tier",
                when(col("total_spent") >= 1000, "High Value")
                .when(col("total_spent") >= 500, "Medium Value")
                .otherwise("Low Value")) \
    .withColumn("processed_timestamp", current_timestamp())

# Save customer analytics
customer_analytics.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("retail_analytics.gold_customer_analytics")

print("✅ Customer analytics table created")
display(customer_analytics.orderBy(col("total_spent").desc()).limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer 2: Product Performance

# COMMAND ----------

# Product performance metrics
product_performance = df_orders.groupBy("product_id", "product_name", "product_category") \
    .agg(
        count("order_id").alias("total_orders"),
        sum("quantity").alias("total_quantity_sold"),
        sum("total_amount").alias("total_revenue"),
        sum("profit").alias("total_profit"),
        avg("unit_price").alias("avg_selling_price"),
        countDistinct("customer_id").alias("unique_customers")
    ) \
    .withColumn("profit_margin_pct", 
                round(col("total_profit") / col("total_revenue") * 100, 2)) \
    .withColumn("revenue_per_customer", 
                round(col("total_revenue") / col("unique_customers"), 2)) \
    .withColumn("processed_timestamp", current_timestamp())

# Product ranking
window_revenue = Window.orderBy(col("total_revenue").desc())
window_quantity = Window.orderBy(col("total_quantity_sold").desc())

product_analytics = product_performance \
    .withColumn("revenue_rank", row_number().over(window_revenue)) \
    .withColumn("quantity_rank", row_number().over(window_quantity)) \
    .withColumn("performance_category",
                when(col("revenue_rank") <= 10, "Top Revenue")
                .when(col("quantity_rank") <= 10, "High Volume")
                .when(col("profit_margin_pct") >= 30, "High Margin")
                .otherwise("Standard"))

# Save product analytics
product_analytics.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("retail_analytics.gold_product_analytics")

print("✅ Product analytics table created")
display(product_analytics.orderBy(col("total_revenue").desc()).limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer 3: Sales KPIs and Trends

# COMMAND ----------

# Monthly sales trends
monthly_sales = df_orders.groupBy("order_year", "order_month") \
    .agg(
        count("order_id").alias("total_orders"),
        sum("total_amount").alias("monthly_revenue"),
        sum("profit").alias("monthly_profit"),
        countDistinct("customer_id").alias("active_customers"),
        countDistinct("product_id").alias("products_sold"),
        avg("total_amount").alias("avg_order_value")
    ) \
    .withColumn("profit_margin_pct", 
                round(col("monthly_profit") / col("monthly_revenue") * 100, 2)) \
    .withColumn("revenue_per_customer", 
                round(col("monthly_revenue") / col("active_customers"), 2)) \
    .withColumn("processed_timestamp", current_timestamp()) \
    .orderBy("order_year", "order_month")

# Calculate month-over-month growth
window_monthly = Window.orderBy("order_year", "order_month")
monthly_trends = monthly_sales \
    .withColumn("prev_month_revenue", 
                lag("monthly_revenue", 1).over(window_monthly)) \
    .withColumn("revenue_growth_pct",
                round(((col("monthly_revenue") - col("prev_month_revenue")) / 
                       col("prev_month_revenue")) * 100, 2))

# Save monthly trends
monthly_trends.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("retail_analytics.gold_monthly_trends")

print("✅ Monthly trends table created")
display(monthly_trends)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer 4: Category Performance

# COMMAND ----------

# Category-wise performance analysis
category_performance = df_orders.groupBy("product_category") \
    .agg(
        count("order_id").alias("total_orders"),
        sum("total_amount").alias("category_revenue"),
        sum("profit").alias("category_profit"),
        sum("quantity").alias("total_quantity"),
        countDistinct("customer_id").alias("unique_customers"),
        countDistinct("product_id").alias("unique_products"),
        avg("total_amount").alias("avg_order_value")
    ) \
    .withColumn("profit_margin_pct", 
                round(col("category_profit") / col("category_revenue") * 100, 2)) \
    .withColumn("market_share_pct", 
                round(col("category_revenue") / sum("category_revenue").over(Window.partitionBy()) * 100, 2)) \
    .withColumn("processed_timestamp", current_timestamp()) \
    .orderBy(col("category_revenue").desc())

# Save category performance
category_performance.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("retail_analytics.gold_category_performance")

print("✅ Category performance table created")
display(category_performance)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer 5: Executive Dashboard KPIs

# COMMAND ----------

# Executive summary metrics
executive_kpis = df_orders.agg(
    count("order_id").alias("total_orders"),
    sum("total_amount").alias("total_revenue"),
    sum("profit").alias("total_profit"),
    countDistinct("customer_id").alias("total_customers"),
    countDistinct("product_id").alias("total_products"),
    avg("total_amount").alias("avg_order_value"),
    min("order_date").alias("data_start_date"),
    max("order_date").alias("data_end_date")
) \
.withColumn("profit_margin_pct", 
            round(col("total_profit") / col("total_revenue") * 100, 2)) \
.withColumn("revenue_per_customer", 
            round(col("total_revenue") / col("total_customers"), 2)) \
.withColumn("orders_per_customer", 
            round(col("total_orders") / col("total_customers"), 2)) \
.withColumn("report_date", current_date()) \
.withColumn("processed_timestamp", current_timestamp())

# Save executive KPIs
executive_kpis.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("retail_analytics.gold_executive_kpis")

print("✅ Executive KPIs table created")
display(executive_kpis)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Gold Layer Views for Analytics

# COMMAND ----------

# Create comprehensive analytics view
analytics_view_query = """
CREATE OR REPLACE VIEW retail_analytics.gold_analytics_dashboard AS
SELECT 
    -- Time dimensions
    o.order_date,
    o.order_year,
    o.order_month,
    o.order_quarter,
    
    -- Customer dimensions
    o.customer_id,
    o.customer_name,
    o.customer_segment,
    ca.customer_value_tier,
    ca.total_orders as customer_lifetime_orders,
    ca.total_spent as customer_lifetime_value,
    
    -- Product dimensions
    o.product_id,
    o.product_name,
    o.product_category,
    pa.performance_category as product_performance_tier,
    
    -- Metrics
    o.quantity,
    o.unit_price,
    o.total_amount,
    o.profit,
    round(o.profit / o.total_amount * 100, 2) as order_profit_margin_pct,
    
    -- Flags
    o.status as order_status
    
FROM retail_analytics.silver_orders_enriched o
LEFT JOIN retail_analytics.gold_customer_analytics ca ON o.customer_id = ca.customer_id
LEFT JOIN retail_analytics.gold_product_analytics pa ON o.product_id = pa.product_id
WHERE o.status = 'completed'
"""

spark.sql(analytics_view_query)
print("✅ Comprehensive analytics dashboard view created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality and Validation

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Validate gold layer data consistency
# MAGIC SELECT 
#     'Customer Analytics' as table_name,
#     COUNT(*) as record_count,
#     SUM(total_spent) as total_revenue_check
# FROM retail_analytics.gold_customer_analytics
# 
# UNION ALL
# 
# SELECT 
#     'Product Analytics' as table_name,
#     COUNT(*) as record_count,
#     SUM(total_revenue) as total_revenue_check
# FROM retail_analytics.gold_product_analytics
# 
# UNION ALL
# 
# SELECT 
#     'Monthly Trends' as table_name,
#     COUNT(*) as record_count,
#     SUM(monthly_revenue) as total_revenue_check
# FROM retail_analytics.gold_monthly_trends;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary and Next Steps

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Show all tables in the database
# MAGIC SHOW TABLES IN retail_analytics;

# COMMAND ----------

print("🎉 Silver to Gold Transformation Complete!")
print("\nGold layer tables created:")
print("- ✅ gold_customer_analytics: Customer segmentation and LTV")
print("- ✅ gold_product_analytics: Product performance metrics")
print("- ✅ gold_monthly_trends: Time-series sales analysis")
print("- ✅ gold_category_performance: Category-wise insights")
print("- ✅ gold_executive_kpis: High-level business metrics")
print("- ✅ gold_analytics_dashboard: Comprehensive analytics view")
print("\nNext: Run notebook 04_analytics_queries.sql for business intelligence queries")
