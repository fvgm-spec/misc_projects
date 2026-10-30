# Using Serverless Warehouse for Analytics

## Setup Steps

1. **Access SQL Warehouses**
   - Click "SQL Warehouses" in sidebar
   - Select "Serverless Starter Warehouse"
   - Start the warehouse (if not running)

2. **Connect SQL Editor**
   - Go to "SQL Editor"
   - Select Serverless Warehouse as compute
   - Run analytics queries from `04_analytics_queries.sql`

3. **Create Dashboards**
   - Execute queries in SQL Editor
   - Click "Add visualization" for charts
   - Save queries to dashboard

## Optimal Workflow

```
Notebooks (Compute Cluster) → Tables → SQL Analytics (Serverless Warehouse)
     ↓                          ↓              ↓
  ETL Pipeline              Delta Tables    Dashboards
```

## Cost Efficiency
- Serverless: $0.70/DBU (SQL workloads)
- Compute: $0.15/DBU (ETL workloads)
- Auto-shutdown prevents idle costs
