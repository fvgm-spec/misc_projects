# Databricks Asset Bundle - Retail Analytics Pipeline

This bundle manages a retail analytics pipeline using your existing sample data (orders, customers, products).

## Setup

1. Install Databricks CLI:
```bash
pip install databricks-cli
```

2. Configure authentication:
```bash
databricks configure --token
```

3. Update `databricks.yml` with your workspace URL

## Usage

### Deploy to Development
```bash
databricks bundle deploy --target dev
```

### Run the Pipeline
```bash
databricks bundle run retail_data_pipeline --target dev
```

### Validate Bundle
```bash
databricks bundle validate
```

## Pipeline Structure

The bundle creates a 3-stage pipeline:
1. **Bronze** - Raw data ingestion (orders.csv, customers.csv, products.csv)
2. **Silver** - Cleaned and validated data
3. **Gold** - Business metrics and aggregations

## Resources Created

- Job: `retail_data_pipeline` with 3 dependent tasks
- Notebooks: Data ingestion, transformation, and aggregation
- Delta tables: Bronze, Silver, and Gold layers
