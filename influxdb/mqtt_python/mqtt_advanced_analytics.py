#!/usr/bin/env python3
"""
Advanced MQTT Analytics
Implements advanced features from the tutorial
"""

import requests
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

def send_webhook_alert(alert_data):
    """Send alert to external system via webhook with retry logic"""
    
    webhook_url = "https://your-monitoring-system.com/webhook"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-webhook-token"
    }
    
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
                time.sleep(2 ** attempt)
    
    return False

def send_slack_notification(alert_data):
    """Send formatted alert to Slack channel"""
    
    slack_webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    
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

def detect_anomalies_ml(influxdb3_local, sensor_data):
    """Use machine learning for sophisticated anomaly detection"""
    
    if len(sensor_data) < 10:
        return []
    
    features = []
    timestamps = []
    
    for point in sensor_data:
        timestamp = datetime.fromisoformat(point['timestamp'])
        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()
        
        feature_vector = [
            point['value'],
            hour_of_day,
            day_of_week,
            point.get('humidity', 0),
            point.get('pressure', 0)
        ]
        
        features.append(feature_vector)
        timestamps.append(timestamp)
    
    features = np.array(features)
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    
    predictions = model.fit_predict(features_scaled)
    anomaly_scores = model.decision_function(features_scaled)
    
    anomalies = []
    for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
        if pred == -1:
            anomaly_data = {
                'timestamp': timestamps[i],
                'value': sensor_data[i]['value'],
                'anomaly_score': abs(score),
                'confidence': min(abs(score) * 10, 1.0),
                'features': features[i].tolist()
            }
            anomalies.append(anomaly_data)
    
    return anomalies

def custom_alert_rules(influxdb3_local, sensor_type, location, value, timestamp):
    """Advanced business logic for context-aware alerts"""
    
    if sensor_type == "temperature" and location == "server_room":
        if value > 28.0:
            create_alert(influxdb3_local, "server_room_critical", location, value,
                        f"Server room temperature CRITICAL: {value}°C", 
                        timestamp, "critical")
        elif value > 25.0:
            create_alert(influxdb3_local, "server_room_warning", location, value,
                        f"Server room temperature elevated: {value}°C", 
                        timestamp, "warning")
    
    elif sensor_type == "humidity" and location == "warehouse":
        import datetime
        current_month = datetime.datetime.now().month
        
        threshold = 75.0 if current_month in [6, 7, 8] else 70.0
            
        if value > threshold:
            create_alert(influxdb3_local, "warehouse_humidity", location, value,
                        f"Warehouse humidity high: {value}%", 
                        timestamp, "warning")

def create_alert(influxdb3_local, alert_type, location, value, message, timestamp, severity):
    """Create alert record in database"""
    
    alert_data = {
        "measurement": "sensor_alerts",
        "tags": {
            "alert_type": alert_type,
            "location": location,
            "severity": severity
        },
        "fields": {
            "value": float(value),
            "message": message
        },
        "time": timestamp
    }
    
    influxdb3_local.write(record=alert_data)

def calculate_comfort_index(temperature, humidity):
    """Calculate a simple comfort index (0-1 scale)"""
    temp_score = max(0, 1 - abs(temperature - 22) / 10)
    humidity_score = max(0, 1 - abs(humidity - 50) / 30)
    return (temp_score + humidity_score) / 2

if __name__ == "__main__":
    print("Advanced MQTT Analytics module loaded")
    print("Available functions:")
    print("- create_sensor_dashboard()")
    print("- send_webhook_alert()")
    print("- send_slack_notification()")
    print("- detect_anomalies_ml()")
    print("- custom_alert_rules()")
