"""
InfluxDB 3 Processing Engine Plugin for MQTT Data Analysis
Real-time analysis and alerting for MQTT sensor data
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

def process_writes(influxdb3_local, table_batches, args=None):
    """
    Process incoming MQTT sensor data writes
    Triggered when data is written to the sensors table
    """
    
    # Get configuration from trigger arguments
    temp_threshold_high = float(args.get('temp_threshold_high', 30.0)) if args else 30.0
    temp_threshold_low = float(args.get('temp_threshold_low', 15.0)) if args else 15.0
    humidity_threshold_high = float(args.get('humidity_threshold_high', 80.0)) if args else 80.0
    
    influxdb3_local.info(f"Processing {len(table_batches)} table batches")
    
    for table_batch in table_batches:
        table_name = table_batch["table_name"]
        rows = table_batch["rows"]
        
        influxdb3_local.info(f"Processing {len(rows)} rows from {table_name}")
        
        # Process each row
        for row in rows:
            try:
                # Extract data from row
                sensor_type = row.get("sensor_type")
                location = row.get("location")
                value = row.get("value")
                timestamp = row.get("time")
                
                if not all([sensor_type, location, value is not None]):
                    continue
                
                # Temperature analysis
                if sensor_type == "temperature":
                    analyze_temperature(influxdb3_local, location, value, timestamp, 
                                     temp_threshold_high, temp_threshold_low)
                
                # Humidity analysis
                elif sensor_type == "humidity":
                    analyze_humidity(influxdb3_local, location, value, timestamp, 
                                   humidity_threshold_high)
                
                # Motion detection analysis
                elif sensor_type == "motion":
                    analyze_motion(influxdb3_local, location, row, timestamp)
                
                # Update sensor statistics
                update_sensor_stats(influxdb3_local, sensor_type, location, value, timestamp)
                
            except Exception as e:
                influxdb3_local.error(f"Error processing row: {e}")

def analyze_temperature(influxdb3_local, location: str, value: float, timestamp, 
                       high_threshold: float, low_threshold: float):
    """Analyze temperature readings and generate alerts"""
    
    # Check for threshold violations
    if value > high_threshold:
        create_alert(influxdb3_local, "temperature_high", location, value, 
                    f"Temperature {value}°C exceeds high threshold {high_threshold}°C", 
                    timestamp, "warning")
    
    elif value < low_threshold:
        create_alert(influxdb3_local, "temperature_low", location, value,
                    f"Temperature {value}°C below low threshold {low_threshold}°C",
                    timestamp, "warning")
    
    # Calculate moving average for trend analysis
    calculate_moving_average(influxdb3_local, "temperature", location, value, timestamp)

def analyze_humidity(influxdb3_local, location: str, value: float, timestamp, 
                    high_threshold: float):
    """Analyze humidity readings"""
    
    if value > high_threshold:
        create_alert(influxdb3_local, "humidity_high", location, value,
                    f"Humidity {value}% exceeds threshold {high_threshold}%",
                    timestamp, "info")
    
    # Check for rapid humidity changes
    check_rapid_change(influxdb3_local, "humidity", location, value, timestamp, 
                      change_threshold=20.0, time_window_minutes=5)

def analyze_motion(influxdb3_local, location: str, row: Dict[str, Any], timestamp):
    """Analyze motion detection data"""
    
    detected = row.get("detected", False)
    confidence = row.get("confidence", 0.0)
    
    if detected and confidence > 0.8:
        # Log high-confidence motion detection
        line = LineBuilder("motion_events")
        line.tag("location", location)
        line.tag("event_type", "motion_detected")
        line.float64_field("confidence", confidence)
        line.bool_field("detected", detected)
        influxdb3_local.write(line)
        
        influxdb3_local.info(f"High-confidence motion detected at {location} (confidence: {confidence})")

def update_sensor_stats(influxdb3_local, sensor_type: str, location: str, 
                       value: float, timestamp):
    """Update running statistics for sensors"""
    
    # Get current stats from cache
    cache_key = f"stats_{sensor_type}_{location}"
    current_stats = influxdb3_local.cache.get(cache_key, default={
        "count": 0,
        "sum": 0.0,
        "sum_squares": 0.0,
        "min": float('inf'),
        "max": float('-inf'),
        "last_value": None,
        "last_timestamp": None
    })
    
    # Update statistics
    current_stats["count"] += 1
    current_stats["sum"] += value
    current_stats["sum_squares"] += value * value
    current_stats["min"] = min(current_stats["min"], value)
    current_stats["max"] = max(current_stats["max"], value)
    current_stats["last_value"] = value
    current_stats["last_timestamp"] = timestamp
    
    # Calculate derived statistics
    mean = current_stats["sum"] / current_stats["count"]
    variance = (current_stats["sum_squares"] / current_stats["count"]) - (mean * mean)
    std_dev = variance ** 0.5 if variance > 0 else 0.0
    
    # Store updated stats in cache (with 1-hour TTL)
    influxdb3_local.cache.put(cache_key, current_stats, ttl=3600)
    
    # Write aggregated statistics every 100 readings
    if current_stats["count"] % 100 == 0:
        line = LineBuilder("sensor_statistics")
        line.tag("sensor_type", sensor_type)
        line.tag("location", location)
        line.int64_field("sample_count", current_stats["count"])
        line.float64_field("mean_value", mean)
        line.float64_field("std_dev", std_dev)
        line.float64_field("min_value", current_stats["min"])
        line.float64_field("max_value", current_stats["max"])
        influxdb3_local.write(line)

def calculate_moving_average(influxdb3_local, sensor_type: str, location: str, 
                           value: float, timestamp, window_size: int = 10):
    """Calculate moving average for trend analysis"""
    
    # Get recent values from cache
    cache_key = f"moving_avg_{sensor_type}_{location}"
    recent_values = influxdb3_local.cache.get(cache_key, default=[])
    
    # Add new value
    recent_values.append({"value": value, "timestamp": timestamp})
    
    # Keep only the last window_size values
    if len(recent_values) > window_size:
        recent_values = recent_values[-window_size:]
    
    # Calculate moving average
    if len(recent_values) >= window_size:
        avg_value = sum(item["value"] for item in recent_values) / len(recent_values)
        
        # Write moving average
        line = LineBuilder("sensor_moving_averages")
        line.tag("sensor_type", sensor_type)
        line.tag("location", location)
        line.int64_field("window_size", window_size)
        line.float64_field("moving_average", avg_value)
        line.float64_field("current_value", value)
        line.float64_field("deviation", abs(value - avg_value))
        influxdb3_local.write(line)
    
    # Update cache
    influxdb3_local.cache.put(cache_key, recent_values, ttl=1800)  # 30 minutes TTL

def check_rapid_change(influxdb3_local, sensor_type: str, location: str, 
                      current_value: float, timestamp, change_threshold: float, 
                      time_window_minutes: int):
    """Check for rapid changes in sensor values"""
    
    cache_key = f"rapid_change_{sensor_type}_{location}"
    last_reading = influxdb3_local.cache.get(cache_key)
    
    if last_reading:
        time_diff = (timestamp - last_reading["timestamp"]).total_seconds() / 60
        value_diff = abs(current_value - last_reading["value"])
        
        if time_diff <= time_window_minutes and value_diff > change_threshold:
            create_alert(influxdb3_local, f"{sensor_type}_rapid_change", location, 
                        current_value, 
                        f"Rapid {sensor_type} change: {value_diff:.1f} in {time_diff:.1f} minutes",
                        timestamp, "warning")
    
    # Update cache with current reading
    influxdb3_local.cache.put(cache_key, {
        "value": current_value,
        "timestamp": timestamp
    }, ttl=time_window_minutes * 60)

def create_alert(influxdb3_local, alert_type: str, location: str, value: float,
                message: str, timestamp, severity: str = "info"):
    """Create an alert record"""
    
    line = LineBuilder("sensor_alerts")
    line.tag("alert_type", alert_type)
    line.tag("location", location)
    line.tag("severity", severity)
    line.string_field("message", message)
    line.float64_field("trigger_value", value)
    influxdb3_local.write(line)
    
    # Log the alert
    if severity == "warning":
        influxdb3_local.warn(f"ALERT: {message}")
    else:
        influxdb3_local.info(f"Alert: {message}")

def process_scheduled_call(influxdb3_local, call_time, args=None):
    """
    Scheduled processing for periodic analysis
    Runs every 5 minutes to generate summary reports
    """
    
    influxdb3_local.info(f"Running scheduled analysis at {call_time}")
    
    try:
        # Generate hourly sensor summaries
        generate_hourly_summary(influxdb3_local)
        
        # Check for sensor health
        check_sensor_health(influxdb3_local)
        
        # Clean up old cache entries
        cleanup_cache(influxdb3_local)
        
    except Exception as e:
        influxdb3_local.error(f"Error in scheduled processing: {e}")

def generate_hourly_summary(influxdb3_local):
    """Generate hourly summary statistics"""
    
    # Query recent data
    query = """
    SELECT 
        sensor_type,
        location,
        COUNT(*) as reading_count,
        AVG(value) as avg_value,
        MIN(value) as min_value,
        MAX(value) as max_value
    FROM sensors 
    WHERE time >= now() - INTERVAL '1 hour'
    AND value IS NOT NULL
    GROUP BY sensor_type, location
    """
    
    try:
        results = influxdb3_local.query(query)
        
        for result in results:
            line = LineBuilder("hourly_sensor_summary")
            line.tag("sensor_type", result["sensor_type"])
            line.tag("location", result["location"])
            line.int64_field("reading_count", result["reading_count"])
            line.float64_field("avg_value", result["avg_value"])
            line.float64_field("min_value", result["min_value"])
            line.float64_field("max_value", result["max_value"])
            influxdb3_local.write(line)
        
        influxdb3_local.info(f"Generated hourly summary for {len(results)} sensor/location combinations")
        
    except Exception as e:
        influxdb3_local.error(f"Error generating hourly summary: {e}")

def check_sensor_health(influxdb3_local):
    """Check if sensors are reporting regularly"""
    
    # Check for sensors that haven't reported in the last 10 minutes
    query = """
    SELECT 
        sensor_type,
        location,
        MAX(time) as last_reading
    FROM sensors
    WHERE time >= now() - INTERVAL '1 hour'
    GROUP BY sensor_type, location
    HAVING MAX(time) < now() - INTERVAL '10 minutes'
    """
    
    try:
        stale_sensors = influxdb3_local.query(query)
        
        for sensor in stale_sensors:
            create_alert(influxdb3_local, "sensor_offline", sensor["location"], 0,
                        f"Sensor {sensor['sensor_type']} at {sensor['location']} last seen at {sensor['last_reading']}",
                        datetime.utcnow(), "warning")
        
        if stale_sensors:
            influxdb3_local.warn(f"Found {len(stale_sensors)} potentially offline sensors")
        
    except Exception as e:
        influxdb3_local.error(f"Error checking sensor health: {e}")

def cleanup_cache(influxdb3_local):
    """Clean up old cache entries (placeholder - cache has TTL)"""
    # Cache entries automatically expire based on TTL
    # This function can be used for additional cleanup logic if needed
    influxdb3_local.info("Cache cleanup completed (TTL-based)")

# Helper class for line protocol (this would be provided by InfluxDB 3)
class LineBuilder:
    def __init__(self, measurement):
        self.measurement = measurement
        self.tags = {}
        self.fields = {}
        self._timestamp = None
    
    def tag(self, key, value):
        self.tags[key] = str(value)
        return self
    
    def string_field(self, key, value):
        self.fields[key] = f'"{value}"'
        return self
    
    def float64_field(self, key, value):
        self.fields[key] = float(value)
        return self
    
    def int64_field(self, key, value):
        self.fields[key] = int(value)
        return self
    
    def bool_field(self, key, value):
        self.fields[key] = bool(value)
        return self
