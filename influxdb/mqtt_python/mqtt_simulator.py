#!/usr/bin/env python3
"""
MQTT Data Simulator
Generates sample MQTT data for testing
"""

import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTDataSimulator:
    """Simulates IoT sensor data via MQTT"""
    
    def __init__(self):
        self.mqtt_broker = os.getenv('MQTT_BROKER', 'broker.hivemq.com')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.mqtt_username = os.getenv('MQTT_USERNAME')
        self.mqtt_password = os.getenv('MQTT_PASSWORD')
        
        self.client = mqtt.Client()
        if self.mqtt_username and self.mqtt_password:
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            logger.info(f"Connected to MQTT broker {self.mqtt_broker}")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    def generate_sensor_data(self, sensor_type: str, location: str) -> dict:
        """Generate realistic sensor data"""
        base_time = datetime.utcnow()
        
        if sensor_type == "temperature":
            return {
                "value": round(random.uniform(18.0, 35.0), 2),
                "unit": "celsius",
                "timestamp": base_time.isoformat(),
                "sensor_id": f"temp_{location}_{random.randint(1, 5)}"
            }
        elif sensor_type == "humidity":
            return {
                "value": round(random.uniform(30.0, 80.0), 2),
                "unit": "percent",
                "timestamp": base_time.isoformat(),
                "sensor_id": f"hum_{location}_{random.randint(1, 5)}"
            }
        elif sensor_type == "pressure":
            return {
                "value": round(random.uniform(980.0, 1020.0), 2),
                "unit": "hPa",
                "timestamp": base_time.isoformat(),
                "sensor_id": f"press_{location}_{random.randint(1, 3)}"
            }
        elif sensor_type == "motion":
            return {
                "detected": random.choice([True, False]),
                "confidence": round(random.uniform(0.7, 1.0), 2),
                "timestamp": base_time.isoformat(),
                "sensor_id": f"motion_{location}_{random.randint(1, 10)}"
            }
        else:
            return {
                "value": round(random.uniform(0, 100), 2),
                "timestamp": base_time.isoformat(),
                "sensor_id": f"generic_{location}"
            }
    
    def publish_data(self, topic: str, data: dict):
        """Publish data to MQTT topic"""
        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload)
            logger.debug(f"Published to {topic}: {payload}")
        except Exception as e:
            logger.error(f"Failed to publish data: {e}")
    
    def simulate_iot_environment(self, duration_minutes: int = 60):
        """Simulate a complete IoT environment"""
        self.connect()
        
        # Define sensors and locations
        sensors = ["temperature", "humidity", "pressure", "motion"]
        locations = ["office", "warehouse", "factory", "lab", "outdoor"]
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        message_count = 0
        
        logger.info(f"Starting simulation for {duration_minutes} minutes...")
        
        try:
            while time.time() < end_time:
                # Generate data for random sensor/location combinations
                sensor = random.choice(sensors)
                location = random.choice(locations)
                
                # Create topic
                topic = f"sensors/{sensor}/{location}"
                
                # Generate and publish data
                data = self.generate_sensor_data(sensor, location)
                self.publish_data(topic, data)
                
                message_count += 1
                
                # Log progress
                if message_count % 50 == 0:
                    elapsed = (time.time() - start_time) / 60
                    logger.info(f"Published {message_count} messages in {elapsed:.1f} minutes")
                
                # Random delay between messages (0.1 to 2 seconds)
                time.sleep(random.uniform(0.1, 2.0))
                
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        finally:
            self.client.disconnect()
            logger.info(f"Simulation completed. Total messages: {message_count}")

def main():
    """Main function"""
    simulator = MQTTDataSimulator()
    
    # Run simulation for 30 minutes
    simulator.simulate_iot_environment(duration_minutes=30)

if __name__ == "__main__":
    main()
