#!/usr/bin/env python3
"""
MQTT Data Collector for InfluxDB 3
Collects MQTT messages and stores them in InfluxDB 3
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from influxdb3 import InfluxDB3Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MQTTInfluxDBCollector:
    """MQTT to InfluxDB 3 data collector"""
    
    def __init__(self):
        # MQTT Configuration
        self.mqtt_broker = os.getenv('MQTT_BROKER', 'broker.hivemq.com')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.mqtt_username = os.getenv('MQTT_USERNAME')
        self.mqtt_password = os.getenv('MQTT_PASSWORD')
        self.mqtt_topics = os.getenv('MQTT_TOPICS', 'sensors/+').split(',')
        
        # InfluxDB Configuration
        self.influxdb_host = os.getenv('INFLUXDB_HOST', 'localhost')
        self.influxdb_port = int(os.getenv('INFLUXDB_PORT', 8181))
        self.influxdb_token = os.getenv('INFLUXDB_TOKEN')
        self.influxdb_database = os.getenv('INFLUXDB_DATABASE', 'mqtt_data')
        
        # Initialize clients
        self.mqtt_client = None
        self.influxdb_client = None
        self.message_count = 0
        
    def setup_influxdb(self):
        """Initialize InfluxDB 3 client"""
        try:
            self.influxdb_client = InfluxDB3Client(
                host=f"http://{self.influxdb_host}:{self.influxdb_port}",
                token=self.influxdb_token,
                database=self.influxdb_database
            )
            logger.info(f"Connected to InfluxDB at {self.influxdb_host}:{self.influxdb_port}")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            raise
    
    def setup_mqtt(self):
        """Initialize MQTT client"""
        self.mqtt_client = mqtt.Client()
        
        # Set callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        
        # Set credentials if provided
        if self.mqtt_username and self.mqtt_password:
            self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker {self.mqtt_broker}")
            # Subscribe to topics
            for topic in self.mqtt_topics:
                client.subscribe(topic.strip())
                logger.info(f"Subscribed to topic: {topic.strip()}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        logger.info("Disconnected from MQTT broker")
    
    def on_message(self, client, userdata, msg):
        """Process incoming MQTT messages"""
        try:
            # Decode message
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            timestamp = datetime.utcnow()
            
            logger.debug(f"Received message on {topic}: {payload}")
            
            # Parse payload (assume JSON format)
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # If not JSON, treat as simple value
                data = {"value": payload}
            
            # Write to InfluxDB
            self.write_to_influxdb(topic, data, timestamp)
            
            self.message_count += 1
            if self.message_count % 100 == 0:
                logger.info(f"Processed {self.message_count} messages")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def write_to_influxdb(self, topic: str, data: Dict[str, Any], timestamp: datetime):
        """Write data to InfluxDB 3"""
        try:
            # Parse topic to extract measurement and tags
            topic_parts = topic.split('/')
            measurement = topic_parts[0] if topic_parts else 'mqtt_data'
            
            # Create line protocol data
            point_data = {
                "measurement": measurement,
                "tags": {
                    "topic": topic,
                    "source": "mqtt"
                },
                "fields": {},
                "time": timestamp
            }
            
            # Add topic parts as tags
            if len(topic_parts) > 1:
                point_data["tags"]["sensor_type"] = topic_parts[1]
            if len(topic_parts) > 2:
                point_data["tags"]["location"] = topic_parts[2]
            
            # Process data fields
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    point_data["fields"][key] = float(value)
                elif isinstance(value, bool):
                    point_data["fields"][key] = value
                else:
                    point_data["tags"][key] = str(value)
            
            # Ensure at least one field exists
            if not point_data["fields"]:
                point_data["fields"]["message_count"] = 1
            
            # Write to InfluxDB
            self.influxdb_client.write(
                record=point_data,
                database=self.influxdb_database
            )
            
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")
    
    def start_collecting(self):
        """Start the MQTT data collection"""
        try:
            # Setup connections
            self.setup_influxdb()
            self.setup_mqtt()
            
            # Connect to MQTT broker
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            
            # Start the loop
            logger.info("Starting MQTT data collection...")
            self.mqtt_client.loop_forever()
            
        except KeyboardInterrupt:
            logger.info("Stopping data collection...")
            self.stop_collecting()
        except Exception as e:
            logger.error(f"Error in data collection: {e}")
            raise
    
    def stop_collecting(self):
        """Stop the data collection"""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        logger.info(f"Collection stopped. Total messages processed: {self.message_count}")

def main():
    """Main function"""
    collector = MQTTInfluxDBCollector()
    collector.start_collecting()

if __name__ == "__main__":
    main()
