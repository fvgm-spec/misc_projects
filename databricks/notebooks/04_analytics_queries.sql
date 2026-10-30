-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Business Intelligence Analytics Queries
-- MAGIC 
-- MAGIC This notebook contains SQL queries for business analytics:
-- MAGIC - Executive dashboards
-- MAGIC - Customer insights
-- MAGIC - Product performance
-- MAGIC - Sales trends
-- MAGIC - Operational metrics

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Setup Database Context

-- COMMAND ----------

USE retail_analytics;

-- Show available tables
SHOW TABLES;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Executive Dashboard Queries

-- COMMAND ----------

-- Key Performance Indicators (KPIs)
SELECT 
    'Total Revenue' as metric,
    CONCAT('$', FORMAT_NUMBER(total_revenue, 0)) as value,
    'Last 12 months' as period
FROM retail_analytics.gold_executive_kpis

UNION ALL

SELECT 
    'Total Orders' as metric,
    FORMAT_NUMBER(total_orders, 0) as value,
    'All time' as period
FROM retail_analytics.gold_executive_kpis

UNION ALL

SELECT 
    'Active Customers' as metric,
    FORMAT_NUMBER(total_customers, 0) as value,
    'Unique customers' as period
FROM retail_analytics.gold_executive_kpis

UNION ALL

SELECT 
    'Average Order Value' as metric,
    CONCAT('$', FORMAT_NUMBER(avg_order_value, 2)) as value,
    'Per transaction' as period
FROM retail_analytics.gold_executive_kpis;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Revenue Trends Analysis

-- COMMAND ----------

-- Monthly revenue trends with growth rates
SELECT 
    order_year,
    order_month,
    CONCAT(order_year, '-', LPAD(order_month, 2, '0')) as year_month,
    FORMAT_NUMBER(monthly_revenue, 0) as revenue,
    total_orders,
    active_customers,
    FORMAT_NUMBER(avg_order_value, 2) as avg_order_value,
    COALESCE(revenue_growth_pct, 0) as growth_rate_pct,
    CASE 
        WHEN revenue_growth_pct > 10 THEN '📈 High Growth'
        WHEN revenue_growth_pct > 0 THEN '📊 Positive Growth'
        WHEN revenue_growth_pct < -10 THEN '📉 Declining'
        ELSE '➡️ Stable'
    END as trend_indicator
FROM retail_analytics.gold_monthly_trends
ORDER BY order_year, order_month;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Customer Segmentation Analysis

-- COMMAND ----------

-- Customer value distribution
SELECT 
    customer_value_tier,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage,
    FORMAT_NUMBER(AVG(total_spent), 0) as avg_spent,
    FORMAT_NUMBER(SUM(total_spent), 0) as total_revenue,
    ROUND(AVG(total_orders), 1) as avg_orders_per_customer
FROM retail_analytics.gold_customer_analytics
GROUP BY customer_value_tier
ORDER BY 
    CASE customer_value_tier 
        WHEN 'High Value' THEN 1 
        WHEN 'Medium Value' THEN 2 
        ELSE 3 
    END;

-- COMMAND ----------

-- Top 10 customers by lifetime value
SELECT 
    customer_name,
    customer_segment,
    customer_value_tier,
    total_orders,
    FORMAT_NUMBER(total_spent, 0) as lifetime_value,
    FORMAT_NUMBER(avg_order_value, 2) as avg_order_value,
    categories_purchased,
    ROUND(order_frequency, 2) as monthly_order_frequency
FROM retail_analytics.gold_customer_analytics
ORDER BY total_spent DESC
LIMIT 10;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Product Performance Analysis

-- COMMAND ----------

-- Category performance overview
SELECT 
    product_category,
    FORMAT_NUMBER(category_revenue, 0) as revenue,
    total_orders,
    unique_customers,
    unique_products,
    ROUND(profit_margin_pct, 1) as profit_margin_pct,
    ROUND(market_share_pct, 1) as market_share_pct,
    FORMAT_NUMBER(avg_order_value, 2) as avg_order_value
FROM retail_analytics.gold_category_performance
ORDER BY category_revenue DESC;

-- COMMAND ----------

-- Top performing products
SELECT 
    product_name,
    product_category,
    performance_category,
    total_quantity_sold,
    FORMAT_NUMBER(total_revenue, 0) as revenue,
    FORMAT_NUMBER(total_profit, 0) as profit,
    ROUND(profit_margin_pct, 1) as profit_margin_pct,
    unique_customers,
    revenue_rank,
    quantity_rank
FROM retail_analytics.gold_product_analytics
WHERE revenue_rank <= 15
ORDER BY total_revenue DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Sales Performance Insights

-- COMMAND ----------

-- Quarterly performance comparison
SELECT 
    order_year,
    order_quarter,
    COUNT(DISTINCT order_month) as months_in_quarter,
    SUM(monthly_revenue) as quarterly_revenue,
    SUM(total_orders) as quarterly_orders,
    AVG(active_customers) as avg_monthly_customers,
    ROUND(AVG(profit_margin_pct), 1) as avg_profit_margin
FROM retail_analytics.gold_monthly_trends
GROUP BY order_year, order_quarter
ORDER BY order_year, order_quarter;

-- COMMAND ----------

-- Customer segment performance by category
SELECT 
    c.customer_segment,
    o.product_category,
    COUNT(DISTINCT o.customer_id) as customers,
    COUNT(o.order_id) as orders,
    FORMAT_NUMBER(SUM(o.total_amount), 0) as revenue,
    ROUND(AVG(o.total_amount), 2) as avg_order_value,
    SUM(o.quantity) as items_sold
FROM retail_analytics.gold_analytics_dashboard o
JOIN retail_analytics.gold_customer_analytics c ON o.customer_id = c.customer_id
GROUP BY c.customer_segment, o.product_category
ORDER BY c.customer_segment, SUM(o.total_amount) DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Operational Analytics

-- COMMAND ----------

-- Order status distribution
SELECT 
    order_status,
    COUNT(*) as order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage,
    FORMAT_NUMBER(SUM(total_amount), 0) as total_value
FROM retail_analytics.gold_analytics_dashboard
GROUP BY order_status
ORDER BY order_count DESC;

-- COMMAND ----------

-- Daily order patterns (day of week analysis)
SELECT 
    DAYOFWEEK(order_date) as day_of_week,
    CASE DAYOFWEEK(order_date)
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END as day_name,
    COUNT(*) as total_orders,
    FORMAT_NUMBER(SUM(total_amount), 0) as total_revenue,
    ROUND(AVG(total_amount), 2) as avg_order_value
FROM retail_analytics.gold_analytics_dashboard
GROUP BY DAYOFWEEK(order_date)
ORDER BY day_of_week;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Advanced Analytics

-- COMMAND ----------

-- Customer cohort analysis (simplified)
WITH customer_first_order AS (
    SELECT 
        customer_id,
        MIN(order_date) as first_order_date,
        DATE_FORMAT(MIN(order_date), 'yyyy-MM') as cohort_month
    FROM retail_analytics.gold_analytics_dashboard
    GROUP BY customer_id
),
customer_orders AS (
    SELECT 
        o.customer_id,
        o.order_date,
        c.cohort_month,
        MONTHS_BETWEEN(o.order_date, c.first_order_date) as period_number
    FROM retail_analytics.gold_analytics_dashboard o
    JOIN customer_first_order c ON o.customer_id = c.customer_id
)
SELECT 
    cohort_month,
    COUNT(DISTINCT CASE WHEN period_number = 0 THEN customer_id END) as customers_month_0,
    COUNT(DISTINCT CASE WHEN period_number = 1 THEN customer_id END) as customers_month_1,
    COUNT(DISTINCT CASE WHEN period_number = 2 THEN customer_id END) as customers_month_2,
    COUNT(DISTINCT CASE WHEN period_number = 3 THEN customer_id END) as customers_month_3,
    ROUND(
        COUNT(DISTINCT CASE WHEN period_number = 1 THEN customer_id END) * 100.0 / 
        NULLIF(COUNT(DISTINCT CASE WHEN period_number = 0 THEN customer_id END), 0), 1
    ) as retention_month_1_pct
FROM customer_orders
GROUP BY cohort_month
ORDER BY cohort_month;

-- COMMAND ----------

-- Product affinity analysis (products bought together)
WITH order_products AS (
    SELECT 
        order_date,
        customer_id,
        COLLECT_LIST(product_category) as categories_in_order
    FROM retail_analytics.gold_analytics_dashboard
    GROUP BY order_date, customer_id
    HAVING COUNT(DISTINCT product_category) > 1
)
SELECT 
    'Cross-category orders' as metric,
    COUNT(*) as order_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT CONCAT(order_date, customer_id)) FROM retail_analytics.gold_analytics_dashboard), 1) as percentage
FROM order_products;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Data Quality Monitoring

-- COMMAND ----------

-- Data freshness and completeness check
SELECT 
    'Silver Orders' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN order_date IS NULL THEN 1 END) as null_dates,
    COUNT(CASE WHEN total_amount <= 0 THEN 1 END) as invalid_amounts,
    MIN(order_date) as earliest_date,
    MAX(order_date) as latest_date,
    MAX(processed_timestamp) as last_processed
FROM retail_analytics.silver_orders

UNION ALL

SELECT 
    'Gold Customer Analytics' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN total_spent <= 0 THEN 1 END) as invalid_spending,
    NULL as invalid_amounts,
    NULL as earliest_date,
    NULL as latest_date,
    MAX(processed_timestamp) as last_processed
FROM retail_analytics.gold_customer_analytics;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Summary Report

-- COMMAND ----------

-- Executive summary with key insights
SELECT 
    '📊 Business Overview' as section,
    CONCAT(
        'Total Revenue: $', FORMAT_NUMBER(total_revenue, 0), ' | ',
        'Orders: ', FORMAT_NUMBER(total_orders, 0), ' | ',
        'Customers: ', FORMAT_NUMBER(total_customers, 0), ' | ',
        'AOV: $', FORMAT_NUMBER(avg_order_value, 2)
    ) as summary
FROM retail_analytics.gold_executive_kpis

UNION ALL

SELECT 
    '🏆 Top Category' as section,
    CONCAT(product_category, ' - $', FORMAT_NUMBER(category_revenue, 0), ' (', ROUND(market_share_pct, 1), '% market share)')
FROM retail_analytics.gold_category_performance
ORDER BY category_revenue DESC
LIMIT 1

UNION ALL

SELECT 
    '👑 Best Customer Segment' as section,
    CONCAT(customer_value_tier, ' - ', COUNT(*), ' customers generating $', FORMAT_NUMBER(SUM(total_spent), 0))
FROM retail_analytics.gold_customer_analytics
GROUP BY customer_value_tier
ORDER BY SUM(total_spent) DESC
LIMIT 1;
