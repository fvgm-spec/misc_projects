# MQTT Data Collection and Analysis with Python and InfluxDB 3

This comprehensive tutorial demonstrates how to collect, store, and analyze MQTT data using Python and InfluxDB 3. We'll cover the complete workflow from MQTT data ingestion to advanced analysis using InfluxDB 3's processing engine.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [MQTT Basics](#mqtt-basics)
5. [Data Collection](#data-collection)
6. [Writing to InfluxDB](#writing-to-influxdb)
7. [Data Analysis](#data-analysis)
8. [InfluxDB 3 Processing Engine](#influxdb-3-processing-engine)
9. [Advanced Examples](#advanced-examples)
10. [Best Practices](#best-practices)

## Overview

MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol designed for IoT devices and applications with limited bandwidth. This tutorial shows how to:

- Connect to MQTT brokers and subscribe to topics
- Process and transform MQTT messages
- Store time-series data in InfluxDB 3
- Analyze data using SQL and Python
- Use InfluxDB 3's processing engine for real-time analysis
- Create automated workflows and alerts

## Prerequisites

- Python 3.8 or higher
- InfluxDB 3 Core or Enterprise
- Basic understanding of MQTT concepts
- Familiarity with time-series data

## Environment Setup

### 1. Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Required Dependencies

The `requirements.txt` includes:
- `paho-mqtt==1.6.1` - MQTT client library
- `influxdb3-python==0.5.0` - InfluxDB 3 client
- `pandas==2.1.4` - Data analysis
- `numpy==1.24.3` - Numerical computing
- `matplotlib==3.7.2` - Plotting
- `seaborn==0.12.2` - Statistical visualization
- `python-dotenv==1.0.0` - Environment variables
- `requests==2.31.0` - HTTP requests

### 3. Configuration

Create a `.env` file for your configuration:

```bash
# MQTT Configuration
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_TOPICS=sensors/temperature,sensors/humidity,sensors/pressure

# InfluxDB Configuration
INFLUXDB_HOST=localhost
INFLUXDB_PORT=8181
INFLUXDB_TOKEN=your-admin-token
INFLUXDB_DATABASE=mqtt_data
INFLUXDB_ORG=your-org
```

## MQTT Basics

MQTT is a publish-subscribe messaging protocol ideal for IoT applications. Key concepts:

- **Broker**: Central server that routes messages between clients
- **Topics**: Hierarchical message channels (e.g., `sensors/temperature/office`)
- **QoS**: Quality of Service levels (0, 1, 2) for message delivery guarantees
- **Retained Messages**: Last message on a topic is stored for new subscribers

### Popular MQTT Brokers

- **HiveMQ**: Public broker at `broker.hivemq.com` (great for testing)
- **Eclipse Mosquitto**: Open-source broker
- **AWS IoT Core**: Managed MQTT service
- **Azure IoT Hub**: Microsoft's IoT platform

## Data Collection

### 1. MQTT Data Collector

The `mqtt_collector.py` script connects to an MQTT broker and writes data to InfluxDB 3:

```python
# Key features:
# - Automatic JSON payload parsing
# - Topic-based tagging
# - Error handling and logging
# - Configurable via environment variables

python mqtt_collector.py
```

### 2. Data Simulator

For testing, use the `mqtt_simulator.py` to generate realistic sensor data:

```python
# Simulates various sensor types:
# - Temperature (18-35°C)
# - Humidity (30-80%)
# - Pressure (980-1020 hPa)
# - Motion detection

python mqtt_simulator.py
```

### 3. Topic Structure

Recommended MQTT topic hierarchy:
```
sensors/
├── temperature/
│   ├── office/
│   ├── warehouse/
│   └── factory/
├── humidity/
│   ├── office/
│   └── warehouse/
└── motion/
    ├── entrance/
    └── parking/
```

## Writing to InfluxDB

### Data Model

MQTT messages are stored in InfluxDB with this structure:

```
Measurement: sensors
Tags:
- topic: Original MQTT topic
- sensor_type: Extracted from topic (temperature, humidity, etc.)
- location: Extracted from topic (office, warehouse, etc.)
- source: "mqtt"

Fields:
- value: Numeric sensor reading
- Additional fields from JSON payload

Timestamp: Message arrival time
```

### Example Data Points

```
sensors,topic=sensors/temperature/office,sensor_type=temperature,location=office,source=mqtt value=23.5,sensor_id="temp_office_1" 1640995200000000000
sensors,topic=sensors/humidity/office,sensor_type=humidity,location=office,source=mqtt value=65.2,sensor_id="hum_office_1" 1640995200000000000
```

## Data Analysis

Data analysis is the cornerstone of any IoT monitoring system. With MQTT sensor data flowing into InfluxDB 3, you gain access to powerful SQL-based analytics that can reveal patterns, detect anomalies, and provide actionable insights. The time-series nature of MQTT data makes it particularly well-suited for trend analysis, forecasting, and real-time monitoring.

InfluxDB 3's SQL engine provides advanced window functions, statistical operations, and time-based aggregations that are essential for IoT analytics. Unlike traditional databases, InfluxDB 3 is optimized for time-series workloads, making complex temporal queries execute efficiently even with millions of data points.

### Understanding Time-Series Analysis Patterns

Before diving into specific queries, it's important to understand the common analysis patterns for MQTT sensor data:

**Temporal Aggregation**: Grouping data by time intervals (hourly, daily, weekly) to identify patterns and trends. This is crucial for understanding seasonal variations, usage patterns, and long-term trends in your sensor network.

**Comparative Analysis**: Comparing current readings against historical baselines to detect deviations. This helps identify when sensors are behaving abnormally compared to their typical patterns.

**Cross-Sensor Correlation**: Analyzing relationships between different sensor types to understand environmental interactions. For example, temperature and humidity often have inverse relationships that can indicate HVAC system performance.

**Anomaly Detection**: Identifying data points that deviate significantly from expected patterns. This is essential for predictive maintenance and early warning systems.

### 1. Basic Queries

```sql
-- Get latest readings for all sensors
SELECT * FROM sensors 
WHERE time >= now() - INTERVAL '1 hour'
ORDER BY time DESC;

-- Average temperature by location
SELECT 
    location,
    AVG(value) as avg_temp
FROM sensors 
WHERE sensor_type = 'temperature'
AND time >= now() - INTERVAL '24 hours'
GROUP BY location;

-- Detect high temperature alerts
SELECT * FROM sensors
WHERE sensor_type = 'temperature'
AND value > 30.0
AND time >= now() - INTERVAL '1 hour';

-- Moving averages for trend analysis
SELECT 
    time,
    location,
    value,
    AVG(value) OVER (
        PARTITION BY location 
        ORDER BY time 
        ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
    ) as moving_avg_10
FROM sensors 
WHERE sensor_type = 'temperature'
AND time >= now() - INTERVAL '24 hours'
ORDER BY location, time;

-- Identify sensor anomalies using statistical methods
WITH stats AS (
    SELECT 
        location,
        AVG(value) as mean_value,
        STDDEV(value) as std_value
    FROM sensors 
    WHERE sensor_type = 'temperature'
    AND time >= now() - INTERVAL '7 days'
    GROUP BY location
)
SELECT 
    s.time,
    s.location,
    s.value,
    st.mean_value,
    ABS(s.value - st.mean_value) / st.std_value as z_score
FROM sensors s
JOIN stats st ON s.location = st.location
WHERE s.sensor_type = 'temperature'
AND s.time >= now() - INTERVAL '1 hour'
AND ABS(s.value - st.mean_value) / st.std_value > 2.0
ORDER BY z_score DESC;
```

### 2. Data Analyzer

The `mqtt_analyzer.py` script serves as a comprehensive analytical toolkit designed specifically for MQTT sensor data. Unlike simple query tools, this analyzer understands the unique characteristics of IoT data streams and provides domain-specific insights that are immediately actionable for operations teams.

**Why Specialized Analysis Matters**: MQTT sensor data has unique characteristics that generic analytics tools often miss. Sensors can go offline, produce erratic readings during calibration, or exhibit drift over time. The analyzer is designed to handle these real-world scenarios and provide meaningful insights despite data quality issues.

**Statistical Foundation**: The analyzer employs robust statistical methods that are resistant to outliers and missing data. It uses techniques like median absolute deviation (MAD) for outlier detection, which is more reliable than standard deviation when dealing with sensor data that may contain occasional erroneous readings.

**Temporal Context**: Unlike snapshot analysis, the analyzer maintains temporal context, understanding that a sensor reading's significance depends on when it occurred, what happened before it, and the seasonal or operational context of that time period.

#### Core Analytical Capabilities

**Descriptive Analytics**: The analyzer provides comprehensive summary statistics that go beyond simple averages. It calculates percentiles, skewness, and kurtosis to understand the distribution shape of your sensor data. This helps identify whether sensors are operating within normal parameters or showing signs of drift or degradation.

**Time Series Decomposition**: Complex sensor patterns are broken down into trend, seasonal, and residual components. This decomposition helps distinguish between normal cyclical variations (like daily temperature cycles) and genuine anomalies that require attention.

**Distribution Analysis**: Understanding how sensor values are distributed helps in setting appropriate alert thresholds and identifying sensors that may be miscalibrated. The analyzer fits multiple distribution types to your data and recommends the best fit.

**Correlation Discovery**: The analyzer automatically discovers relationships between different sensor types and locations. These correlations can reveal insights about your environment that aren't obvious from individual sensor readings.

#### Advanced Analytical Features

**Adaptive Thresholding**: Instead of static alert thresholds, the analyzer can recommend dynamic thresholds that adapt to seasonal patterns, operational schedules, and historical performance. This reduces false alarms while maintaining sensitivity to genuine issues.

**Sensor Health Monitoring**: The analyzer tracks metadata about sensor performance, including data completeness, reading consistency, and communication reliability. This helps identify sensors that may need maintenance before they fail completely.

**Pattern Recognition**: The analyzer can identify recurring patterns in your sensor data, such as daily operational cycles, weekly patterns, or seasonal variations. Understanding these patterns is crucial for optimizing operations and predicting future behavior.

**Anomaly Contextualization**: When anomalies are detected, the analyzer provides context about what makes them unusual, whether they're isolated incidents or part of a larger pattern, and their potential operational impact.

### 3. Visualization Examples

The analyzer generates several types of plots:

- **Time Series**: Sensor trends over time with rolling averages
- **Distribution**: Box plots and histograms by location
- **Anomaly Detection**: Statistical outlier identification
- **Correlation Heatmaps**: Relationships between sensor measurements
- **Geographic Distribution**: Sensor locations and their readings
- **Alert Frequency**: Historical alert patterns and trends

#### Advanced Visualization Features

```python
# Example: Create comprehensive dashboard
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_sensor_dashboard(data):
    """Generate multi-panel sensor analysis dashboard"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Time series plot
    axes[0,0].plot(data['time'], data['temperature'])
    axes[0,0].set_title('Temperature Over Time')
    axes[0,0].set_xlabel('Time')
    axes[0,0].set_ylabel('Temperature (°C)')
    
    # Distribution histogram
    axes[0,1].hist(data['temperature'], bins=30, alpha=0.7)
    axes[0,1].set_title('Temperature Distribution')
    axes[0,1].set_xlabel('Temperature (°C)')
    axes[0,1].set_ylabel('Frequency')
    
    # Box plot by location
    sns.boxplot(data=data, x='location', y='temperature', ax=axes[0,2])
    axes[0,2].set_title('Temperature by Location')
    axes[0,2].tick_params(axis='x', rotation=45)
    
    # Correlation heatmap
    corr_data = data[['temperature', 'humidity', 'pressure']].corr()
    sns.heatmap(corr_data, annot=True, ax=axes[1,0])
    axes[1,0].set_title('Sensor Correlation Matrix')
    
    # Anomaly scatter plot
    axes[1,1].scatter(data['time'], data['temperature'], 
                     c=data['is_anomaly'], cmap='coolwarm')
    axes[1,1].set_title('Anomaly Detection')
    axes[1,1].set_xlabel('Time')
    axes[1,1].set_ylabel('Temperature (°C)')
    
    # Alert frequency over time
    alert_counts = data.groupby(data['time'].dt.date)['is_alert'].sum()
    axes[1,2].plot(alert_counts.index, alert_counts.values)
    axes[1,2].set_title('Daily Alert Frequency')
    axes[1,2].set_xlabel('Date')
    axes[1,2].set_ylabel('Alert Count')
    
    plt.tight_layout()
    return fig
```

## InfluxDB 3 Processing Engine

The Processing Engine enables real-time data analysis and automated responses.

### 1. Plugin Installation

The Processing Engine represents a paradigm shift in how databases handle real-time data processing. Instead of extracting data for external processing, the engine brings computation directly to where the data lives, eliminating latency and enabling true real-time responses to changing conditions.

**Why In-Database Processing Matters**: Traditional IoT architectures require data to be extracted from the database, processed externally, and then results written back. This creates latency, complexity, and potential data consistency issues. The Processing Engine eliminates these problems by executing your custom logic directly within the database engine, ensuring immediate response to data changes.

**Security and Isolation**: The Processing Engine runs plugins in a secure, isolated Python environment. Each plugin operates in its own namespace with controlled access to system resources. This ensures that custom code cannot interfere with database operations or access unauthorized data.

**Scalability Considerations**: The Processing Engine is designed to scale with your data volume. Plugins can be configured to run asynchronously, allowing multiple instances to process data in parallel. The engine also provides built-in caching mechanisms to optimize performance for frequently accessed data.

#### Understanding Plugin Architecture

**Plugin Lifecycle**: Plugins follow a well-defined lifecycle from installation through execution. Understanding this lifecycle is crucial for developing robust, maintainable plugins that integrate seamlessly with your InfluxDB instance.

**Execution Context**: Each plugin execution receives a specific context that includes the triggering event, relevant data, and access to the shared API. This context provides everything needed to make intelligent decisions about data processing and response actions.

**State Management**: Unlike stateless functions, Processing Engine plugins can maintain state between executions using the built-in caching system. This enables sophisticated scenarios like tracking trends over time, maintaining counters, or building complex analytical models.

#### Installation Strategies

**Development vs. Production**: The installation approach differs significantly between development and production environments. Development environments benefit from the flexibility of local uploads and frequent updates, while production environments require more controlled deployment processes with proper testing and validation.

**Plugin Distribution**: Organizations can choose between using community plugins, developing custom solutions, or creating hybrid approaches that extend existing plugins. The GitHub integration makes it easy to share and maintain plugins across teams and environments.

**Dependency Management**: The Processing Engine includes a sophisticated package management system that handles Python dependencies automatically. This ensures that plugins have access to the libraries they need while maintaining isolation between different plugin environments.

#### Setting up the Plugin Directory

```bash
# Create a dedicated plugin directory
mkdir -p ~/.influxdb3/plugins

# Start InfluxDB 3 with processing engine enabled
influxdb3 serve \
  --node-id node0 \
  --object-store file \
  --data-dir ~/.influxdb3 \
  --plugin-dir ~/.influxdb3/plugins
```

#### Plugin Installation Methods

**Method 1: Copy plugins locally**
```bash
# Clone the official plugin repository
git clone https://github.com/influxdata/influxdb3_plugins.git

# Copy the MQTT processing plugin to your plugin directory
cp influxdb3_plugins/examples/mqtt_processing_plugin.py ~/.influxdb3/plugins/
```

**Method 2: Reference plugins directly from GitHub**
```bash
# Use plugins directly from GitHub (no local copy needed)
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "gh:examples/mqtt_processing_plugin.py" \
  --database mqtt_data \
  mqtt_realtime_analysis
```

**Method 3: Upload local plugins**
```bash
# Upload a local plugin file when creating triggers
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "/local/path/to/mqtt_processing_plugin.py" \
  --upload \
  --database mqtt_data \
  mqtt_local_plugin
```

#### Managing Plugin Dependencies

Install required Python packages for your plugins:

```bash
# Install common packages for MQTT processing
influxdb3 install package paho-mqtt
influxdb3 install package pandas
influxdb3 install package numpy
influxdb3 install package requests

# For Docker environments
docker exec -it influxdb3_container influxdb3 install package pandas
```

#### Plugin Security Considerations

- **Admin privileges required**: Plugin uploads and updates require admin tokens
- **Path validation**: All plugin paths are validated to prevent directory traversal attacks
- **Sandboxed execution**: Plugins run in an isolated Python environment
- **Disable package installation**: For secure environments, use `--package-manager disabled`

```bash
# Secure deployment with disabled package manager
influxdb3 serve \
  --node-id node0 \
  --object-store file \
  --data-dir ~/.influxdb3 \
  --plugin-dir ~/.influxdb3/plugins \
  --package-manager disabled
```

#### Viewing Installed Plugins

```bash
# List all loaded plugins
influxdb3 show plugins --token $ADMIN_TOKEN

# Query plugin information via SQL
influxdb3 query \
  -d _internal \
  "SELECT * FROM system.plugin_files ORDER BY plugin_name" \
  --token $ADMIN_TOKEN
```

### 2. Create Triggers

Triggers are the bridge between database events and your custom processing logic. They define when, how, and under what conditions your plugins execute. Understanding trigger design is crucial for building responsive, efficient IoT monitoring systems.

**Event-Driven Architecture**: The Processing Engine implements a sophisticated event-driven architecture where triggers respond to specific database events. This approach ensures that processing happens exactly when needed, without wasting computational resources on polling or scheduled checks that may not be necessary.

**Trigger Granularity**: The granularity of your triggers significantly impacts system performance and responsiveness. Fine-grained triggers (responding to individual table writes) provide immediate response but may create high computational overhead. Coarse-grained triggers (scheduled or batched) are more efficient but introduce latency.

**Resource Management**: Each trigger consumes system resources including CPU, memory, and I/O. The Processing Engine provides controls for managing resource usage, including asynchronous execution options and error handling strategies that prevent runaway processes from impacting database performance.

#### Trigger Design Patterns

**Real-Time Processing Pattern**: Data write triggers enable real-time processing of incoming sensor data. This pattern is ideal for immediate alerting, data validation, and real-time transformations. However, it requires careful consideration of processing time to avoid impacting ingestion performance.

**Batch Processing Pattern**: Scheduled triggers enable batch processing of accumulated data. This pattern is more efficient for complex analytics, reporting, and operations that benefit from processing multiple data points together. The trade-off is increased latency between data arrival and processing.

**On-Demand Processing Pattern**: HTTP request triggers enable on-demand processing triggered by external systems or user requests. This pattern is perfect for interactive dashboards, manual analysis requests, or integration with external workflow systems.

#### Trigger Configuration Strategy

**Argument Passing**: Trigger arguments provide a powerful mechanism for configuring plugin behavior without modifying code. This separation of configuration from logic enables the same plugin to be used in different contexts with different parameters, improving reusability and maintainability.

**Error Handling Philosophy**: The choice of error handling strategy reflects your operational philosophy. Retry strategies work well for transient issues but can create cascading problems if the underlying issue persists. Disable strategies provide safety but require manual intervention to restore functionality.

**Performance Optimization**: Asynchronous execution can significantly improve system throughput by allowing multiple trigger instances to run concurrently. However, this introduces complexity around shared state and resource contention that must be carefully managed.

#### Data Write Triggers

Execute plugins when data is written to specific tables:

```bash
# Trigger on writes to sensors table
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "mqtt_processing_plugin.py" \
  --trigger-arguments "temp_threshold_high=30.0,temp_threshold_low=15.0,humidity_threshold_high=80.0" \
  --database mqtt_data \
  mqtt_realtime_analysis

# Trigger on writes to all tables
influxdb3 create trigger \
  --trigger-spec "all_tables" \
  --path "mqtt_processing_plugin.py" \
  --database mqtt_data \
  mqtt_all_tables_processor

# Trigger with table exclusion (using plugin logic)
influxdb3 create trigger \
  --trigger-spec "all_tables" \
  --path "mqtt_processing_plugin.py" \
  --trigger-arguments "exclude_tables=temp_data,debug_info,system_logs" \
  --database mqtt_data \
  mqtt_filtered_processor
```

#### Scheduled Triggers

Execute plugins at regular intervals or specific times:

```bash
# Run every 5 minutes for periodic summaries
influxdb3 create trigger \
  --trigger-spec "every:5m" \
  --path "mqtt_processing_plugin.py" \
  --database mqtt_data \
  mqtt_scheduled_summary

# Run every hour for detailed analysis
influxdb3 create trigger \
  --trigger-spec "every:1h" \
  --path "mqtt_processing_plugin.py" \
  --trigger-arguments "analysis_type=detailed,report_email=admin@example.com" \
  --database mqtt_data \
  mqtt_hourly_analysis

# Run daily at 8 AM using cron syntax (supports seconds)
influxdb3 create trigger \
  --trigger-spec "cron:0 0 8 * * *" \
  --path "mqtt_processing_plugin.py" \
  --trigger-arguments "report_type=daily" \
  --database mqtt_data \
  mqtt_daily_report
```

#### HTTP Request Triggers

Create custom API endpoints that execute plugins:

```bash
# Create webhook endpoint at /api/v3/engine/mqtt-webhook
influxdb3 create trigger \
  --trigger-spec "request:mqtt-webhook" \
  --path "mqtt_processing_plugin.py" \
  --database mqtt_data \
  mqtt_webhook_processor

# Create status endpoint for monitoring
influxdb3 create trigger \
  --trigger-spec "request:status" \
  --path "mqtt_status_plugin.py" \
  --database mqtt_data \
  mqtt_status_endpoint
```

#### Advanced Trigger Configuration

**Asynchronous Execution**
```bash
# Allow multiple trigger instances to run simultaneously
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "mqtt_processing_plugin.py" \
  --run-asynchronous \
  --database mqtt_data \
  mqtt_async_processor
```

**Error Handling**
```bash
# Automatically retry on error
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "mqtt_processing_plugin.py" \
  --error-behavior retry \
  --database mqtt_data \
  mqtt_retry_processor

# Disable trigger on error
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "mqtt_processing_plugin.py" \
  --error-behavior disable \
  --database mqtt_data \
  mqtt_auto_disable_processor
```

#### Trigger Management

```bash
# View all triggers for a database
influxdb3 show summary --database mqtt_data --token $ADMIN_TOKEN

# Update an existing trigger with new plugin code
influxdb3 update trigger \
  --database mqtt_data \
  --trigger-name mqtt_realtime_analysis \
  --path "/path/to/updated/mqtt_processing_plugin.py"

# Test a trigger before deployment
influxdb3 test wal_plugin \
  --database mqtt_data \
  --plugin-filename mqtt_processing_plugin.py \
  --token $ADMIN_TOKEN
```

#### Trigger Arguments and Configuration

Pass configuration parameters to your plugins:

```bash
# Complex configuration with multiple parameters
influxdb3 create trigger \
  --trigger-spec "every:10m" \
  --path "mqtt_processing_plugin.py" \
  --trigger-arguments "temp_threshold_high=35.0,temp_threshold_low=10.0,humidity_threshold_high=85.0,humidity_threshold_low=20.0,alert_email=ops@company.com,webhook_url=https://alerts.company.com/webhook" \
  --database mqtt_data \
  mqtt_comprehensive_monitor
```

These arguments are accessible in your plugin as a dictionary:

```python
def process_writes(influxdb3_local, table_batches, args=None):
    if args:
        temp_high = float(args.get("temp_threshold_high", 30.0))
        temp_low = float(args.get("temp_threshold_low", 15.0))
        alert_email = args.get("alert_email", "default@example.com")
        
        # Use configuration in your processing logic
        influxdb3_local.info(f"Monitoring temperature: {temp_low}°C to {temp_high}°C")
```

### 3. Plugin Features

The processing plugin provides:

- **Real-time Alerting**: Temperature and humidity threshold monitoring
- **Statistical Analysis**: Moving averages and trend detection
- **Anomaly Detection**: Rapid change detection
- **Health Monitoring**: Sensor offline detection
- **Data Aggregation**: Hourly summaries and statistics

### 4. Generated Data

The Processing Engine's ability to generate derived data transforms raw sensor readings into actionable intelligence. This generated data represents the value-added layer that turns simple measurements into comprehensive monitoring and analysis capabilities.

**Data Enrichment Philosophy**: Raw MQTT sensor data tells you what happened, but generated data tells you what it means. By creating derived measurements, statistical summaries, and analytical results, the Processing Engine transforms reactive monitoring into proactive management.

**Temporal Aggregation Strategy**: Generated data often involves aggregating raw measurements across different time windows. This multi-resolution approach provides both immediate operational visibility and long-term trend analysis. Short-term aggregations (minutes to hours) support operational decisions, while long-term aggregations (days to months) support strategic planning.

**Metadata Preservation**: Generated data maintains links to its source data, preserving the analytical chain from raw measurements to final insights. This traceability is crucial for debugging analysis results and understanding the confidence level of derived conclusions.

#### Alert and Notification Tables

**Alert Lifecycle Management**: Alert tables don't just store when alerts occurred; they track the complete lifecycle of each alert from detection through resolution. This includes escalation paths, acknowledgment status, and resolution actions, providing a complete audit trail for operational incidents.

**Severity Classification**: The multi-level severity system (info, warning, critical) enables graduated response strategies. Info-level alerts might only be logged, warning-level alerts might trigger notifications, and critical alerts might initiate automated response procedures.

**Alert Correlation**: Advanced alert systems correlate related alerts to prevent notification storms and identify root causes. For example, a cooling system failure might trigger temperature alerts across multiple locations, but the system can identify these as related incidents rather than independent problems.

#### Statistical Analysis Tables

**Moving Averages and Trends**: Moving averages smooth out short-term fluctuations to reveal underlying trends. Different window sizes serve different purposes: short windows (5-15 minutes) for operational monitoring, medium windows (1-4 hours) for shift-based analysis, and long windows (daily/weekly) for strategic planning.

**Statistical Process Control**: Generated statistical data enables statistical process control (SPC) techniques that can detect when processes are going out of control before they reach critical thresholds. This predictive capability is essential for maintaining system reliability.

**Baseline Establishment**: Statistical tables help establish dynamic baselines that adapt to changing operational conditions. Unlike static thresholds, these baselines account for seasonal variations, operational schedules, and equipment aging.

#### Data Quality and Health Monitoring

**Sensor Reliability Metrics**: Generated data includes metrics about sensor reliability, including uptime percentages, data completeness ratios, and communication quality indicators. These metrics help prioritize maintenance activities and identify sensors that may need replacement.

**Data Validation Results**: The Processing Engine can validate incoming data against expected ranges, patterns, and relationships. Validation results are stored as generated data, providing visibility into data quality issues that might otherwise go unnoticed.

**Performance Benchmarking**: Generated data includes performance metrics about the monitoring system itself, including processing latencies, storage utilization, and query performance. This meta-monitoring ensures that the monitoring system remains healthy and responsive.

#### Alert Tables

```sql
-- View all sensor alerts with severity levels
SELECT * FROM sensor_alerts 
ORDER BY time DESC 
LIMIT 20;

-- Filter alerts by severity
SELECT 
    time,
    alert_type,
    location,
    value,
    message,
    severity
FROM sensor_alerts 
WHERE severity = 'critical'
AND time >= now() - INTERVAL '24 hours'
ORDER BY time DESC;

-- Alert frequency analysis
SELECT 
    DATE_TRUNC('hour', time) as hour,
    alert_type,
    COUNT(*) as alert_count
FROM sensor_alerts 
WHERE time >= now() - INTERVAL '7 days'
GROUP BY hour, alert_type
ORDER BY hour DESC, alert_count DESC;
```

#### Statistical Analysis Tables

```sql
-- View moving averages for trend analysis
SELECT 
    time,
    location,
    sensor_type,
    current_value,
    moving_avg_5min,
    moving_avg_15min,
    moving_avg_1hour
FROM sensor_moving_averages 
WHERE sensor_type = 'temperature'
ORDER BY time DESC;

-- Hourly sensor summaries with statistics
SELECT 
    hour,
    location,
    sensor_type,
    min_value,
    max_value,
    avg_value,
    stddev_value,
    data_points
FROM hourly_sensor_summary 
WHERE hour >= now() - INTERVAL '24 hours'
ORDER BY hour DESC, location;

-- Sensor health and performance metrics
SELECT 
    time,
    location,
    sensor_type,
    last_reading_time,
    readings_per_minute,
    health_status,
    uptime_percentage
FROM sensor_statistics 
ORDER BY time DESC;
```

#### Anomaly Detection Results

```sql
-- View detected anomalies with confidence scores
SELECT 
    time,
    location,
    sensor_type,
    value,
    expected_value,
    anomaly_score,
    anomaly_type
FROM sensor_anomalies 
WHERE time >= now() - INTERVAL '6 hours'
ORDER BY anomaly_score DESC;

-- Rapid change detection
SELECT 
    time,
    location,
    sensor_type,
    previous_value,
    current_value,
    change_rate,
    change_magnitude
FROM sensor_rapid_changes 
WHERE ABS(change_rate) > 5.0
ORDER BY time DESC;
```

#### Data Quality Metrics

```sql
-- Sensor offline detection
SELECT 
    sensor_id,
    location,
    sensor_type,
    last_seen,
    offline_duration_minutes,
    expected_interval_seconds
FROM sensor_offline_alerts 
WHERE offline_duration_minutes > 10
ORDER BY offline_duration_minutes DESC;

-- Data ingestion rates and patterns
SELECT 
    DATE_TRUNC('minute', time) as minute,
    COUNT(*) as messages_per_minute,
    COUNT(DISTINCT location) as active_locations,
    AVG(processing_latency_ms) as avg_latency
FROM sensor_ingestion_stats 
WHERE time >= now() - INTERVAL '1 hour'
GROUP BY minute
ORDER BY minute DESC;
```

#### Aggregated Metrics

```sql
-- Daily sensor summaries by location
SELECT 
    date,
    location,
    sensor_type,
    daily_min,
    daily_max,
    daily_avg,
    total_readings,
    alert_count
FROM daily_sensor_summary 
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC, location;

-- Environmental correlation analysis
SELECT 
    time,
    location,
    temperature,
    humidity,
    pressure,
    comfort_index,
    air_quality_score
FROM environmental_correlations 
WHERE time >= now() - INTERVAL '24 hours'
ORDER BY time DESC;
```

#### Custom Business Logic Results

```sql
-- Equipment efficiency metrics
SELECT 
    time,
    equipment_id,
    location,
    efficiency_score,
    energy_consumption,
    performance_rating,
    maintenance_alert
FROM equipment_efficiency 
WHERE time >= now() - INTERVAL '12 hours'
ORDER BY efficiency_score ASC;

-- Predictive maintenance indicators
SELECT 
    equipment_id,
    location,
    predicted_failure_date,
    confidence_level,
    maintenance_priority,
    estimated_cost
FROM predictive_maintenance 
WHERE predicted_failure_date <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY predicted_failure_date ASC;
```

#### System Performance Monitoring

```sql
-- Processing engine performance metrics
SELECT 
    time,
    plugin_name,
    execution_time_ms,
    memory_usage_mb,
    records_processed,
    success_rate
FROM plugin_performance_stats 
ORDER BY time DESC;

-- Cache utilization statistics
SELECT 
    cache_namespace,
    total_keys,
    memory_usage_mb,
    hit_rate_percentage,
    eviction_count
FROM cache_statistics 
ORDER BY memory_usage_mb DESC;
```

These generated tables provide comprehensive insights into your MQTT sensor network, enabling:

- **Real-time Monitoring**: Immediate alerts and status updates
- **Historical Analysis**: Trend identification and pattern recognition  
- **Predictive Analytics**: Forecasting and maintenance planning
- **Performance Optimization**: System efficiency and resource utilization
- **Data Quality Assurance**: Missing data detection and sensor health monitoring

## Advanced Examples

### 1. Custom Alert Rules

Custom alert rules represent the business logic layer of your IoT monitoring system. While generic thresholds can catch obvious problems, custom rules encode domain expertise and operational knowledge that transforms raw sensor data into actionable intelligence.

**Domain Expertise Integration**: Custom alert rules capture the nuanced understanding that operations teams have about their systems. For example, a temperature reading of 25°C might be normal in an office but critical in a server room. Custom rules encode this contextual knowledge directly into the monitoring system.

**Contextual Awareness**: Advanced alert rules consider multiple factors beyond simple threshold violations. They account for time of day, operational schedules, seasonal variations, and correlations between different sensors. This contextual awareness dramatically reduces false alarms while improving detection of genuine issues.

**Adaptive Thresholds**: Rather than using static thresholds, custom rules can implement adaptive thresholds that change based on historical patterns, external conditions, or operational states. This adaptability is crucial for systems that operate in varying conditions or have seasonal patterns.

#### Business Logic Implementation

**Multi-Tier Alerting**: Sophisticated alerting systems implement multiple severity levels with different response protocols. This graduated approach ensures that minor issues receive appropriate attention without overwhelming operations teams with unnecessary urgency.

**Correlation Analysis**: Custom rules can correlate events across multiple sensors, locations, or time periods to identify complex failure patterns that wouldn't be apparent from individual sensor readings. This correlation capability is essential for understanding system-level issues.

**Predictive Alerting**: Advanced custom rules don't just react to current conditions; they predict future problems based on trends and patterns. This predictive capability enables proactive maintenance and prevents minor issues from becoming major failures.

#### Operational Integration

**Workflow Integration**: Custom alert rules can integrate with existing operational workflows, automatically creating work orders, scheduling maintenance, or escalating issues according to established procedures. This integration ensures that alerts translate into appropriate actions.

**Knowledge Capture**: Custom rules serve as a repository of operational knowledge, capturing the expertise of experienced operators in executable form. This knowledge preservation is valuable for training new staff and maintaining consistent operational standards.

**Continuous Improvement**: Custom rules can be continuously refined based on operational experience, false alarm analysis, and changing system characteristics. This iterative improvement process ensures that the alerting system becomes more accurate and useful over time.

```python
def custom_alert_rules(influxdb3_local, sensor_type, location, value, timestamp):
    """Advanced business logic for context-aware alerts"""
    
    # Critical infrastructure monitoring
    if sensor_type == "temperature" and location == "server_room":
        # Multi-tier temperature monitoring for server room
        if value > 28.0:
            create_alert(influxdb3_local, "server_room_critical", location, value,
                        f"Server room temperature CRITICAL: {value}°C - Immediate action required", 
                        timestamp, "critical")
        elif value > 25.0:
            create_alert(influxdb3_local, "server_room_warning", location, value,
                        f"Server room temperature elevated: {value}°C - Monitor closely", 
                        timestamp, "warning")
    
    # Warehouse environmental control
    elif sensor_type == "humidity" and location == "warehouse":
        # Seasonal humidity thresholds
        import datetime
        current_month = datetime.datetime.now().month
        
        # Summer months (higher tolerance)
        if current_month in [6, 7, 8]:
            threshold = 75.0
        else:
            threshold = 70.0
            
        if value > threshold:
            create_alert(influxdb3_local, "warehouse_humidity", location, value,
                        f"Warehouse humidity high: {value}% (threshold: {threshold}%)", 
                        timestamp, "warning")
    
    # Manufacturing equipment monitoring
    elif sensor_type == "vibration" and "production_line" in location:
        # Vibration analysis with frequency components
        if value > 10.0:  # High vibration
            # Check recent trend
            recent_readings = influxdb3_local.query(
                "SELECT value FROM sensors WHERE sensor_type = 'vibration' "
                "AND location = $location AND time >= $start_time ORDER BY time DESC LIMIT 5",
                {"location": location, "start_time": timestamp - timedelta(minutes=5)}
            )
            
            if len(recent_readings) >= 3:
                avg_recent = sum(r['value'] for r in recent_readings) / len(recent_readings)
                if avg_recent > 8.0:  # Sustained high vibration
                    create_alert(influxdb3_local, "equipment_vibration_critical", location, value,
                                f"Sustained high vibration detected: {value} (avg: {avg_recent:.1f})", 
                                timestamp, "critical")
    
    # Energy consumption anomalies
    elif sensor_type == "power_consumption":
        # Get historical baseline for this time of day
        hour_of_day = timestamp.hour
        baseline_query = """
            SELECT AVG(value) as baseline_avg, STDDEV(value) as baseline_std
            FROM sensors 
            WHERE sensor_type = 'power_consumption' 
            AND location = $location
            AND EXTRACT(hour FROM time) = $hour
            AND time >= $start_date AND time < $end_date
        """
        
        baseline_result = influxdb3_local.query(baseline_query, {
            "location": location,
            "hour": hour_of_day,
            "start_date": timestamp - timedelta(days=30),
            "end_date": timestamp - timedelta(days=1)
        })
        
        if baseline_result:
            baseline_avg = baseline_result[0]['baseline_avg']
            baseline_std = baseline_result[0]['baseline_std']
            
            if baseline_avg and baseline_std:
                z_score = abs(value - baseline_avg) / baseline_std
                if z_score > 3.0:  # 3 standard deviations
                    severity = "critical" if z_score > 4.0 else "warning"
                    create_alert(influxdb3_local, "power_anomaly", location, value,
                                f"Power consumption anomaly: {value}kW (z-score: {z_score:.1f})", 
                                timestamp, severity)

def create_composite_alerts(influxdb3_local, timestamp):
    """Create alerts based on multiple sensor correlations"""
    
    # Get recent readings from multiple sensors
    multi_sensor_query = """
        SELECT 
            sensor_type,
            location,
            AVG(value) as avg_value,
            MAX(value) as max_value,
            MIN(value) as min_value
        FROM sensors 
        WHERE time >= $start_time 
        AND location IN ('office_floor_1', 'office_floor_2', 'office_floor_3')
        GROUP BY sensor_type, location
    """
    
    readings = influxdb3_local.query(multi_sensor_query, {
        "start_time": timestamp - timedelta(minutes=10)
    })
    
    # Analyze building-wide patterns
    temp_readings = {r['location']: r['avg_value'] for r in readings if r['sensor_type'] == 'temperature'}
    humidity_readings = {r['location']: r['avg_value'] for r in readings if r['sensor_type'] == 'humidity'}
    
    # Check for HVAC system issues
    if len(temp_readings) >= 3:
        temp_variance = max(temp_readings.values()) - min(temp_readings.values())
        if temp_variance > 5.0:  # More than 5°C difference between floors
            create_alert(influxdb3_local, "hvac_imbalance", "building", temp_variance,
                        f"Large temperature variance across floors: {temp_variance:.1f}°C", 
                        timestamp, "warning")
    
    # Check for comfort index violations
    for location in temp_readings:
        if location in humidity_readings:
            temp = temp_readings[location]
            humidity = humidity_readings[location]
            
            # Simple comfort index calculation
            comfort_index = calculate_comfort_index(temp, humidity)
            if comfort_index < 0.3:  # Poor comfort
                create_alert(influxdb3_local, "comfort_violation", location, comfort_index,
                            f"Poor comfort conditions: temp={temp}°C, humidity={humidity}%", 
                            timestamp, "info")

def calculate_comfort_index(temperature, humidity):
    """Calculate a simple comfort index (0-1 scale)"""
    # Optimal ranges: 20-24°C, 40-60% humidity
    temp_score = max(0, 1 - abs(temperature - 22) / 10)
    humidity_score = max(0, 1 - abs(humidity - 50) / 30)
    return (temp_score + humidity_score) / 2
```

### 2. Integration with External Systems

Modern IoT monitoring systems don't operate in isolation; they're part of larger operational ecosystems that include ticketing systems, communication platforms, and business applications. Effective integration with these external systems transforms monitoring alerts into coordinated organizational responses.

**Ecosystem Integration Philosophy**: The goal of external system integration isn't just to send notifications; it's to create seamless workflows that connect sensor data to business processes. This integration ensures that sensor insights drive appropriate organizational actions without requiring manual intervention.

**Communication Strategy**: Different types of alerts require different communication strategies. Critical infrastructure failures need immediate, multi-channel notifications, while routine maintenance alerts might only require ticket creation. The integration system should match communication methods to alert severity and urgency.

**Reliability and Resilience**: External system integrations must be designed for reliability, with appropriate retry mechanisms, fallback options, and error handling. A monitoring system that fails to communicate alerts effectively is worse than no monitoring system at all.

#### Multi-Channel Notification Strategy

**Channel Selection Logic**: Different stakeholders prefer different communication channels, and the urgency of the situation should influence channel selection. Email works well for non-urgent notifications, Slack for team coordination, SMS for urgent alerts, and phone calls for critical emergencies.

**Message Formatting**: Each communication channel has different formatting capabilities and constraints. Effective integration adapts message content and format to match the capabilities of each channel while preserving essential information.

**Escalation Procedures**: Integration systems should implement escalation procedures that automatically escalate unacknowledged alerts through different channels or to different personnel. This ensures that critical issues receive attention even if the primary contact is unavailable.

#### Workflow Automation

**Ticketing System Integration**: Automatic ticket creation transforms alerts into trackable work items with proper prioritization, assignment, and resolution tracking. This integration ensures that alerts don't get lost and provides accountability for resolution actions.

**Approval Workflows**: Some alert responses require approval workflows, especially for actions that might impact production systems. Integration with approval systems ensures that automated responses follow proper authorization procedures.

**Documentation and Audit Trails**: External system integration should maintain comprehensive audit trails that document what actions were taken in response to alerts, who authorized them, and what the outcomes were. This documentation is crucial for continuous improvement and compliance requirements.

#### Business System Integration

**Asset Management Integration**: Alerts should be linked to asset management systems to provide context about equipment history, maintenance schedules, and warranty status. This integration helps prioritize responses and plan maintenance activities.

**Financial System Integration**: For alerts that might trigger significant expenses (like emergency repairs or equipment replacement), integration with financial systems can provide budget impact analysis and approval workflows.

**Compliance Reporting**: Many industries have regulatory requirements for monitoring and reporting. Integration with compliance systems ensures that alert data is properly captured and formatted for regulatory reporting requirements.

```python
import requests
import json
from datetime import datetime, timedelta

def send_webhook_alert(alert_data):
    """Send alert to external system via webhook with retry logic"""
    
    webhook_url = "https://your-monitoring-system.com/webhook"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-webhook-token"
    }
    
    # Add metadata
    alert_data.update({
        "source": "influxdb_mqtt_processor",
        "version": "1.0",
        "sent_at": datetime.utcnow().isoformat()
    })
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                webhook_url, 
                json=alert_data, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Webhook failed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Webhook attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return False

def send_slack_notification(alert_data):
    """Send formatted alert to Slack channel"""
    
    slack_webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    
    # Format message based on severity
    severity_colors = {
        "critical": "#FF0000",
        "warning": "#FFA500", 
        "info": "#0000FF"
    }
    
    color = severity_colors.get(alert_data.get("severity", "info"), "#808080")
    
    slack_message = {
        "attachments": [{
            "color": color,
            "title": f"🚨 MQTT Sensor Alert - {alert_data['alert_type']}",
            "fields": [
                {
                    "title": "Location",
                    "value": alert_data['location'],
                    "short": True
                },
                {
                    "title": "Value",
                    "value": f"{alert_data['value']} {alert_data.get('unit', '')}",
                    "short": True
                },
                {
                    "title": "Severity",
                    "value": alert_data['severity'].upper(),
                    "short": True
                },
                {
                    "title": "Time",
                    "value": alert_data['timestamp'],
                    "short": True
                },
                {
                    "title": "Message",
                    "value": alert_data['message'],
                    "short": False
                }
            ],
            "footer": "InfluxDB MQTT Processor",
            "ts": int(datetime.fromisoformat(alert_data['timestamp']).timestamp())
        }]
    }
    
    try:
        response = requests.post(slack_webhook_url, json=slack_message, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Slack notification failed: {e}")
        return False

def send_email_alert(alert_data):
    """Send email alert using SMTP"""
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Email configuration
    smtp_server = "smtp.company.com"
    smtp_port = 587
    sender_email = "alerts@company.com"
    sender_password = "your-email-password"
    
    # Recipient based on alert type and severity
    recipients = {
        "critical": ["ops-team@company.com", "manager@company.com"],
        "warning": ["ops-team@company.com"],
        "info": ["monitoring@company.com"]
    }
    
    severity = alert_data.get("severity", "info")
    to_emails = recipients.get(severity, ["default@company.com"])
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = f"[{severity.upper()}] MQTT Sensor Alert: {alert_data['alert_type']}"
    
    # HTML email body
    html_body = f"""
    <html>
    <body>
        <h2 style="color: {'red' if severity == 'critical' else 'orange' if severity == 'warning' else 'blue'}">
            Sensor Alert: {alert_data['alert_type']}
        </h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><td><strong>Location:</strong></td><td>{alert_data['location']}</td></tr>
            <tr><td><strong>Value:</strong></td><td>{alert_data['value']} {alert_data.get('unit', '')}</td></tr>
            <tr><td><strong>Severity:</strong></td><td>{severity.upper()}</td></tr>
            <tr><td><strong>Time:</strong></td><td>{alert_data['timestamp']}</td></tr>
            <tr><td><strong>Message:</strong></td><td>{alert_data['message']}</td></tr>
        </table>
        <p><em>Generated by InfluxDB MQTT Processing Engine</em></p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email alert failed: {e}")
        return False

def integrate_with_ticketing_system(alert_data):
    """Create tickets in external ticketing system for critical alerts"""
    
    if alert_data.get("severity") != "critical":
        return True  # Only create tickets for critical alerts
    
    jira_url = "https://your-company.atlassian.net"
    jira_api_token = "your-jira-api-token"
    jira_email = "your-email@company.com"
    
    ticket_data = {
        "fields": {
            "project": {"key": "OPS"},
            "summary": f"Critical Sensor Alert: {alert_data['alert_type']} at {alert_data['location']}",
            "description": f"""
Critical sensor alert detected:

*Location:* {alert_data['location']}
*Sensor Type:* {alert_data.get('sensor_type', 'Unknown')}
*Value:* {alert_data['value']} {alert_data.get('unit', '')}
*Time:* {alert_data['timestamp']}
*Message:* {alert_data['message']}

This ticket was automatically created by the InfluxDB MQTT Processing Engine.
Please investigate and resolve the underlying issue.
            """,
            "issuetype": {"name": "Incident"},
            "priority": {"name": "High"},
            "labels": ["mqtt", "sensor", "automated", "critical"]
        }
    }
    
    try:
        response = requests.post(
            f"{jira_url}/rest/api/3/issue",
            json=ticket_data,
            auth=(jira_email, jira_api_token),
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 201:
            ticket_key = response.json()['key']
            print(f"Created ticket: {ticket_key}")
            return True
        else:
            print(f"Failed to create ticket: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Ticketing system integration failed: {e}")
        return False

# Use in processing plugin
def process_writes(influxdb3_local, table_batches, args=None):
    """Main plugin function with external integrations"""
    
    for table_batch in table_batches:
        for row in table_batch["rows"]:
            # Process sensor data and generate alerts
            alert_data = process_sensor_reading(row)
            
            if alert_data:  # Alert was generated
                severity = alert_data.get("severity", "info")
                
                # Send to multiple external systems based on severity
                if severity == "critical":
                    send_webhook_alert(alert_data)
                    send_slack_notification(alert_data)
                    send_email_alert(alert_data)
                    integrate_with_ticketing_system(alert_data)
                elif severity == "warning":
                    send_webhook_alert(alert_data)
                    send_slack_notification(alert_data)
                else:  # info level
                    send_webhook_alert(alert_data)
```

### 3. Machine Learning Integration

Implement advanced analytics and predictive capabilities using machine learning:

```python
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pickle
import os

def detect_anomalies_ml(influxdb3_local, sensor_data):
    """Use machine learning for sophisticated anomaly detection"""
    
    if len(sensor_data) < 10:  # Need minimum data points
        return []
    
    # Prepare feature matrix
    features = []
    timestamps = []
    
    for point in sensor_data:
        # Extract time-based features
        timestamp = datetime.fromisoformat(point['timestamp'])
        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Create feature vector
        feature_vector = [
            point['value'],
            hour_of_day,
            day_of_week,
            point.get('humidity', 0),  # Additional sensor readings
            point.get('pressure', 0)
        ]
        
        features.append(feature_vector)
        timestamps.append(timestamp)
    
    features = np.array(features)
    
    # Normalize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Train isolation forest
    model = IsolationForest(
        contamination=0.1,  # Expect 10% anomalies
        random_state=42,
        n_estimators=100
    )
    
    predictions = model.fit_predict(features_scaled)
    anomaly_scores = model.decision_function(features_scaled)
    
    # Identify anomalies
    anomalies = []
    for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
        if pred == -1:  # Anomaly detected
            anomaly_data = {
                'timestamp': timestamps[i],
                'value': sensor_data[i]['value'],
                'anomaly_score': abs(score),
                'confidence': min(abs(score) * 10, 1.0),  # Convert to 0-1 scale
                'features': features[i].tolist()
            }
            anomalies.append(anomaly_data)
    
    return anomalies

def predict_sensor_failure(influxdb3_local, sensor_id, location):
    """Predict potential sensor failures using trend analysis"""
    
    # Get historical data for the sensor
    query = """
        SELECT time, value, sensor_type
        FROM sensors 
        WHERE location = $location 
        AND time >= $start_time
        ORDER BY time ASC
    """
    
    historical_data = influxdb3_local.query(query, {
        "location": location,
        "start_time": datetime.now() - timedelta(days=30)
    })
    
    if len(historical_data) < 100:  # Need sufficient history
        return None
    
    # Prepare time series data
    timestamps = [datetime.fromisoformat(d['time']) for d in historical_data]
    values = [d['value'] for d in historical_data]
    
    # Convert timestamps to numeric (days since start)
    start_time = timestamps[0]
    time_numeric = [(t - start_time).total_seconds() / 86400 for t in timestamps]
    
    # Fit trend line
    X = np.array(time_numeric).reshape(-1, 1)
    y = np.array(values)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate prediction metrics
    predictions = model.predict(X)
    residuals = y - predictions
    mse = np.mean(residuals ** 2)
    trend_slope = model.coef_[0]
    
    # Detect degradation patterns
    recent_residuals = residuals[-20:]  # Last 20 readings
    recent_mse = np.mean(recent_residuals ** 2)
    
    # Failure prediction logic
    failure_risk = 0.0
    failure_indicators = []
    
    # Check for increasing error trend
    if recent_mse > mse * 2:
        failure_risk += 0.3
        failure_indicators.append("Increasing measurement error")
    
    # Check for significant drift
    if abs(trend_slope) > 0.1:  # Adjust threshold based on sensor type
        failure_risk += 0.2
        failure_indicators.append(f"Sensor drift detected: {trend_slope:.3f}/day")
    
    # Check for recent anomalies
    recent_anomalies = detect_anomalies_ml(influxdb3_local, historical_data[-50:])
    if len(recent_anomalies) > 5:
        failure_risk += 0.3
        failure_indicators.append(f"High anomaly rate: {len(recent_anomalies)} in last 50 readings")
    
    # Check for data gaps (missing readings)
    expected_readings = (timestamps[-1] - timestamps[0]).total_seconds() / 300  # Every 5 minutes
    actual_readings = len(timestamps)
    data_completeness = actual_readings / expected_readings
    
    if data_completeness < 0.8:
        failure_risk += 0.2
        failure_indicators.append(f"Data completeness: {data_completeness:.1%}")
    
    # Generate prediction
    if failure_risk > 0.7:
        prediction = {
            'sensor_id': sensor_id,
            'location': location,
            'failure_risk': failure_risk,
            'predicted_failure_days': max(1, int(30 * (1 - failure_risk))),
            'confidence': min(failure_risk, 1.0),
            'indicators': failure_indicators,
            'recommendation': 'Schedule immediate maintenance inspection'
        }
    elif failure_risk > 0.4:
        prediction = {
            'sensor_id': sensor_id,
            'location': location,
            'failure_risk': failure_risk,
            'predicted_failure_days': max(7, int(60 * (1 - failure_risk))),
            'confidence': failure_risk,
            'indicators': failure_indicators,
            'recommendation': 'Monitor closely and schedule maintenance'
        }
    else:
        prediction = {
            'sensor_id': sensor_id,
            'location': location,
            'failure_risk': failure_risk,
            'predicted_failure_days': None,
            'confidence': 1 - failure_risk,
            'indicators': [],
            'recommendation': 'Sensor operating normally'
        }
    
    return prediction

def optimize_hvac_system(influxdb3_local, building_data):
    """Use ML to optimize HVAC system based on occupancy and weather"""
    
    # This would integrate with external APIs for weather and occupancy data
    # and use reinforcement learning or optimization algorithms
    
    # Simplified example of energy optimization
    current_temp = building_data.get('temperature', 22)
    current_humidity = building_data.get('humidity', 50)
    occupancy = building_data.get('occupancy', 0.5)  # 0-1 scale
    
    # Simple optimization logic (in practice, use more sophisticated ML)
    optimal_temp = 22 + (occupancy - 0.5) * 2  # Adjust based on occupancy
    optimal_humidity = 45 + occupancy * 10
    
    # Calculate energy savings
    temp_adjustment = abs(current_temp - optimal_temp)
    energy_savings = temp_adjustment * 0.08  # 8% savings per degree
    
    return {
        'current_temperature': current_temp,
        'optimal_temperature': optimal_temp,
        'current_humidity': current_humidity,
        'optimal_humidity': optimal_humidity,
        'estimated_energy_savings': energy_savings,
        'occupancy_factor': occupancy
    }
```

## Best Practices

### 1. MQTT Configuration

- **Use appropriate QoS levels**: QoS 0 for high-frequency data, QoS 1 for important messages
- **Implement reconnection logic**: Handle network interruptions gracefully
- **Use retained messages**: For configuration and status topics
- **Optimize topic structure**: Use hierarchical topics for efficient filtering

### 2. InfluxDB Schema Design

- **Use consistent tag naming**: Standardize location, sensor_type, etc.
- **Limit tag cardinality**: Avoid high-cardinality tags (like sensor_id as tag)
- **Store metadata as tags**: Use tags for dimensions you'll group by
- **Use appropriate field types**: Store numeric values as floats/integers

### 3. Processing Engine

- **Handle errors gracefully**: Use try-catch blocks in plugins
- **Use caching wisely**: Cache frequently accessed data with appropriate TTL
- **Monitor plugin performance**: Log execution times and resource usage
- **Test plugins thoroughly**: Validate with various data scenarios

### 4. Monitoring and Alerting

- **Set up health checks**: Monitor data ingestion rates and plugin execution
- **Use graduated alert levels**: Info, warning, critical severity levels
- **Implement alert fatigue prevention**: Rate limiting and deduplication
- **Create dashboards**: Visualize key metrics and system health

### 5. Security Considerations

- **Use TLS encryption**: Enable MQTT over TLS (port 8883)
- **Implement authentication**: Use username/password or certificates
- **Secure InfluxDB**: Use tokens and proper access controls
- **Network security**: Use VPNs or private networks for production

## Running the Complete System

### 1. Start InfluxDB 3

```bash
# Start with processing engine enabled
influxdb3 serve \
  --node-id node0 \
  --object-store file \
  --data-dir ~/.influxdb3 \
  --plugin-dir ./plugins
```

### 2. Set up Processing Triggers

```bash
# Create database
influxdb3 create database mqtt_data

# Set up real-time processing
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "mqtt_processing_plugin.py" \
  --database mqtt_data \
  mqtt_realtime

# Set up scheduled processing
influxdb3 create trigger \
  --trigger-spec "every:5m" \
  --path "mqtt_processing_plugin.py" \
  --database mqtt_data \
  mqtt_scheduled
```

### 3. Start Data Collection

```bash
# Terminal 1: Start data simulator
python mqtt_simulator.py

# Terminal 2: Start data collector
python mqtt_collector.py

# Terminal 3: Run analysis (after some data is collected)
python mqtt_analyzer.py
```

### 4. Monitor Results

```sql
-- Check data ingestion
SELECT COUNT(*) FROM sensors WHERE time >= now() - INTERVAL '1 hour';

-- View recent alerts
SELECT * FROM sensor_alerts ORDER BY time DESC LIMIT 10;

-- Check processing engine logs
SELECT * FROM system.processing_engine_logs ORDER BY time DESC LIMIT 10;
```

## Conclusion

This tutorial demonstrates a complete MQTT data pipeline using Python and InfluxDB 3:

1. **Data Collection**: MQTT client subscribes to sensor topics
2. **Data Storage**: Time-series data stored in InfluxDB 3
3. **Real-time Processing**: Processing engine analyzes data as it arrives
4. **Analysis & Visualization**: Python tools for comprehensive analysis
5. **Alerting**: Automated threshold monitoring and notifications

The combination of MQTT's lightweight messaging with InfluxDB 3's powerful processing engine creates a robust IoT data platform suitable for production environments.

### Next Steps

- Explore InfluxDB 3's advanced querying capabilities
- Implement custom visualization dashboards
- Add machine learning models for predictive analytics
- Scale the system with multiple MQTT brokers and InfluxDB instances
- Integrate with cloud services for enhanced functionality

For more information, visit:
- [InfluxDB 3 Documentation](https://docs.influxdata.com/influxdb3/)
- [MQTT.org](https://mqtt.org/)
- [HiveMQ MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)
