# Databricks Community Edition Setup Instructions

## Step-by-Step Implementation Guide

### Phase 1: Environment Setup (15 minutes)

#### 1.1 Create Compute Cluster
1. In your Databricks workspace, navigate to **Compute** → **Create Cluster**
2. Configure cluster:
   - **Name**: `retail-analytics-cluster`
   - **Runtime**: Latest LTS (e.g., 13.3 LTS)
   - **Node Type**: Single node (auto-selected in Community Edition)
   - **Terminate after**: 120 minutes
3. Click **Create Cluster** and wait for it to start

#### 1.2 Workspace Organization
1. Create folder structure in **Workspace**:
   ```
   /Users/your-email/
   ├── RetailAnalytics/
   │   ├── 01_DataIngestion/
   │   ├── 02_Transformations/
   │   ├── 03_Analytics/
   │   └── 04_Jobs/
   ```

### Phase 2: Data Setup (20 minutes)

#### 2.1 Generate Sample Data
1. Run the data generator script locally:
   ```bash
   cd /home/felix/misc_projects/databricks/data/sample_data
   python generate_sample_data.py
   ```

#### 2.2 Upload Data to DBFS
1. In Databricks, go to **Data** → **Create Table**
2. Upload the generated CSV files:
   - `orders.csv`
   - `customers.csv` 
   - `products.csv`
3. Files will be stored in `/FileStore/shared_uploads/`

#### 2.3 Alternative: Use File Upload UI
1. Navigate to **Data** → **DBFS** → **FileStore**
2. Create folder: `/FileStore/tables/retail_data/`
3. Upload CSV files to this location

### Phase 3: Notebook Implementation (45 minutes)

#### 3.1 Import Notebooks
1. In **Workspace**, right-click your folder → **Import**
2. Import each notebook file:
   - `01_data_ingestion.py`
   - `02_bronze_to_silver.py`
   - `03_silver_to_gold.py`
   - `04_analytics_queries.sql`

#### 3.2 Execute Pipeline
1. **Start with Data Ingestion**:
   - Open `01_data_ingestion.py`
   - Attach to your cluster
   - Run all cells (Ctrl+Shift+Enter)
   - Verify bronze tables are created

2. **Run Silver Transformation**:
   - Open `02_bronze_to_silver.py`
   - Execute all cells
   - Check data quality reports

3. **Create Gold Layer**:
   - Open `03_silver_to_gold.py`
   - Run transformation logic
   - Verify business metrics tables

4. **Execute Analytics**:
   - Open `04_analytics_queries.sql`
   - Run SQL queries for insights
   - Create visualizations

### Phase 4: Catalog & SQL Features (20 minutes)

#### 4.1 Explore Catalog
1. Navigate to **Data** → **Hive Metastore**
2. Explore `retail_analytics` database
3. View table schemas and sample data
4. Check table properties and statistics

#### 4.2 SQL Editor Usage
1. Go to **SQL Editor**
2. Connect to your cluster
3. Run sample queries from `04_analytics_queries.sql`
4. Create visualizations:
   - Revenue trends (line chart)
   - Category performance (bar chart)
   - Customer segmentation (pie chart)

#### 4.3 Create SQL Dashboard
1. In SQL Editor, click **+ Create** → **Dashboard**
2. Add queries as dashboard widgets
3. Configure refresh schedule
4. Share with team members

### Phase 5: Jobs & Scheduling (25 minutes)

#### 5.1 Create Notebook Job
1. Navigate to **Workflows** → **Jobs** → **Create Job**
2. Configure job:
   - **Name**: `Daily ETL Pipeline`
   - **Task Type**: Notebook
   - **Notebook Path**: `/Users/your-email/01_data_ingestion`
   - **Cluster**: Use existing cluster
3. Add dependent tasks for each notebook
4. Set up email notifications

#### 5.2 Schedule Job Execution
1. In job configuration, add **Schedule**:
   - **Trigger Type**: Scheduled
   - **Cron Expression**: `0 2 * * *` (daily at 2 AM)
   - **Timezone**: Your local timezone
2. Save and enable schedule

#### 5.3 Monitor Job Runs
1. Go to **Workflows** → **Job Runs**
2. View execution history
3. Check logs for debugging
4. Monitor performance metrics

### Phase 6: Advanced Features (30 minutes)

#### 6.1 Delta Lake Features
1. In notebooks, demonstrate:
   ```python
   # Time travel
   spark.sql("SELECT * FROM retail_analytics.silver_orders VERSION AS OF 1")
   
   # Table history
   spark.sql("DESCRIBE HISTORY retail_analytics.silver_orders")
   
   # Optimize tables
   spark.sql("OPTIMIZE retail_analytics.silver_orders")
   ```

#### 6.2 Streaming Simulation
1. Upload JSON files to `/FileStore/streaming_data/`
2. Create streaming notebook:
   ```python
   # Read streaming data
   df = spark.readStream.format("cloudFiles") \
     .option("cloudFiles.format", "json") \
     .load("/FileStore/streaming_data/")
   
   # Write to Delta table
   df.writeStream.format("delta") \
     .outputMode("append") \
     .table("retail_analytics.streaming_events")
   ```

#### 6.3 Data Lineage
1. Navigate to **Data** → **Tables**
2. Select a table → **Lineage** tab
3. View data flow and dependencies
4. Track upstream and downstream relationships

### Phase 7: Collaboration & Git Integration (15 minutes)

#### 7.1 Workspace Sharing
1. Right-click notebook → **Permissions**
2. Add collaborators with appropriate access
3. Enable real-time collaboration
4. Use comments for code reviews

#### 7.2 Version Control (Optional)
1. Go to **User Settings** → **Git Integration**
2. Connect to GitHub/GitLab repository
3. Clone repository to workspace
4. Commit and push changes

### Phase 8: Monitoring & Optimization (20 minutes)

#### 8.1 Performance Monitoring
1. In cluster UI, check **Metrics** tab
2. Monitor CPU, memory, and disk usage
3. Review Spark UI for job optimization
4. Identify bottlenecks and optimize queries

#### 8.2 Cost Management
1. Set cluster auto-termination
2. Use appropriate cluster sizes
3. Monitor DBU consumption
4. Optimize data storage with Delta Lake

#### 8.3 Data Quality Monitoring
1. Create data quality dashboard
2. Set up alerts for data anomalies
3. Implement automated data validation
4. Track data freshness metrics

## Key Features Demonstrated

### ✅ Catalog & Unity Catalog
- Database and table management
- Schema evolution and versioning
- Metadata management
- Data discovery and lineage

### ✅ Compute
- Single-node cluster configuration
- Auto-scaling and termination
- Library management
- Performance optimization

### ✅ SQL Editor & Warehouses
- Interactive SQL queries
- Visualization creation
- Query history and sharing
- Dashboard development

### ✅ Jobs & Pipelines
- Multi-task job orchestration
- Dependency management
- Scheduling and monitoring
- Error handling and retries

### ✅ Data Ingestion
- File upload to DBFS
- Batch and streaming processing
- Multiple data formats (CSV, JSON)
- Schema inference and validation

### ✅ Delta Lake
- ACID transactions
- Time travel and versioning
- Schema evolution
- Performance optimization

## Troubleshooting Common Issues

### Issue: Cluster Won't Start
- **Solution**: Check cluster configuration, ensure single-node setup
- **Alternative**: Create new cluster with default settings

### Issue: File Upload Fails
- **Solution**: Use smaller files (<2GB), check file format
- **Alternative**: Use DBFS CLI or REST API

### Issue: Job Fails
- **Solution**: Check logs, verify notebook paths, ensure cluster access
- **Debug**: Run notebooks manually first

### Issue: SQL Query Timeout
- **Solution**: Optimize query, add filters, use appropriate cluster size
- **Alternative**: Break down complex queries

### Issue: Permission Denied
- **Solution**: Check workspace permissions, verify cluster access
- **Contact**: Workspace administrator for access rights

## Next Steps & Extensions

1. **Real Data Integration**: Connect to external data sources
2. **Advanced Analytics**: Implement ML models with MLflow
3. **API Integration**: Build REST APIs with Databricks
4. **Streaming Analytics**: Real-time data processing
5. **Data Governance**: Implement data quality frameworks
6. **Cost Optimization**: Advanced cluster management
7. **Security**: Implement access controls and encryption
8. **Monitoring**: Advanced observability and alerting

## Resources & Documentation

- [Databricks Community Edition Guide](https://docs.databricks.com/getting-started/community-edition.html)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Apache Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Databricks SQL Reference](https://docs.databricks.com/sql/language-manual/index.html)
- [Job Configuration Reference](https://docs.databricks.com/workflows/jobs/create-run-jobs.html)
