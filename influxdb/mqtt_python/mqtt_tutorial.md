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
```

### 2. Data Analyzer

Use `mqtt_analyzer.py` for comprehensive analysis:

```python
# Features:
# - Summary statistics
# - Time series plotting
# - Distribution analysis
# - Anomaly detection
# - Automated reporting

python mqtt_analyzer.py
```

### 3. Visualization Examples

The analyzer generates several types of plots:

- **Time Series**: Sensor trends over time with rolling averages
- **Distribution**: Box plots and histograms by location
- **Anomaly Detection**: Statistical outlier identification

## InfluxDB 3 Processing Engine

The Processing Engine enables real-time data analysis and automated responses.

### 1. Plugin Installation

```bash
# Copy the plugin to your InfluxDB plugin directory
cp mqtt_processing_plugin.py /path/to/influxdb/plugins/

# Start InfluxDB with processing engine enabled
influxdb3 serve --plugin-dir /path/to/influxdb/plugins
```

### 2. Create Triggers

```bash
# Trigger on data writes to sensors table
influxdb3 create trigger \
  --trigger-spec "table:sensors" \
  --path "mqtt_processing_plugin.py" \
  --trigger-arguments "temp_threshold_high=30.0,temp_threshold_low=15.0,humidity_threshold_high=80.0" \
  --database mqtt_data \
  mqtt_realtime_analysis

# Scheduled trigger for periodic summaries (every 5 minutes)
influxdb3 create trigger \
  --trigger-spec "every:5m" \
  --path "mqtt_processing_plugin.py" \
  --database mqtt_data \
  mqtt_scheduled_summary
```

### 3. Plugin Features

The processing plugin provides:

- **Real-time Alerting**: Temperature and humidity threshold monitoring
- **Statistical Analysis**: Moving averages and trend detection
- **Anomaly Detection**: Rapid change detection
- **Health Monitoring**: Sensor offline detection
- **Data Aggregation**: Hourly summaries and statistics

### 4. Generated Data

The plugin creates additional measurements:

```sql
-- View alerts
SELECT * FROM sensor_alerts ORDER BY time DESC;

-- View moving averages
SELECT * FROM sensor_moving_averages ORDER BY time DESC;

-- View hourly summaries
SELECT * FROM hourly_sensor_summary ORDER BY time DESC;

-- View sensor statistics
SELECT * FROM sensor_statistics ORDER BY time DESC;
```

## Advanced Examples

### 1. Custom Alert Rules

Extend the processing plugin with custom alert logic:

```python
def custom_alert_rules(influxdb3_local, sensor_type, location, value, timestamp):
    """Custom business logic for alerts"""
    
    if sensor_type == "temperature" and location == "server_room":
        # Critical temperature monitoring for server room
        if value > 25.0:
            create_alert(influxdb3_local, "server_room_critical", location, value,
                        f"Server room temperature critical: {value}°C", 
                        timestamp, "critical")
    
    elif sensor_type == "humidity" and location == "warehouse":
        # Humidity control for warehouse
        if value > 70.0:
            create_alert(influxdb3_local, "warehouse_humidity", location, value,
                        f"Warehouse humidity high: {value}%", 
                        timestamp, "warning")
```

### 2. Integration with External Systems

```python
def send_webhook_alert(alert_data):
    """Send alert to external system via webhook"""
    import requests
    
    webhook_url = "https://your-system.com/webhook"
    response = requests.post(webhook_url, json=alert_data)
    return response.status_code == 200

# Use in processing plugin
if severity == "critical":
    webhook_data = {
        "alert_type": alert_type,
        "location": location,
        "value": value,
        "message": message,
        "timestamp": timestamp.isoformat()
    }
    send_webhook_alert(webhook_data)
```

### 3. Machine Learning Integration

```python
def detect_anomalies_ml(influxdb3_local, sensor_data):
    """Use machine learning for anomaly detection"""
    import numpy as np
    from sklearn.ensemble import IsolationForest
    
    # Prepare data
    values = np.array([point['value'] for point in sensor_data]).reshape(-1, 1)
    
    # Train isolation forest
    model = IsolationForest(contamination=0.1)
    predictions = model.fit_predict(values)
    
    # Identify anomalies
    anomalies = [sensor_data[i] for i, pred in enumerate(predictions) if pred == -1]
    
    return anomalies
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
