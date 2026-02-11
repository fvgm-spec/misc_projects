#!/usr/bin/env python3
"""
Weather Data to InfluxDB Script
Fetches weather data from OpenWeather API and sends it to InfluxDB
"""

import requests
import json
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time

# Configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'your_token_here')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'your_org')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'weather')

# Weather location
CITY = "Montevideo"
COUNTRY_CODE = "UY"

def get_weather_data():
    """Fetch weather data from OpenWeather API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&appid={OPENWEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def send_to_influxdb(weather_data):
    """Send weather data to InfluxDB"""
    if not weather_data:
        return False
    
    try:
        # Create InfluxDB client
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        # Create data point
        point = Point("weather") \
            .tag("city", weather_data["name"]) \
            .tag("country", weather_data["sys"]["country"]) \
            .field("temperature", weather_data["main"]["temp"]) \
            .field("humidity", weather_data["main"]["humidity"]) \
            .field("pressure", weather_data["main"]["pressure"]) \
            .field("wind_speed", weather_data["wind"].get("speed", 0)) \
            .field("wind_direction", weather_data["wind"].get("deg", 0)) \
            .field("cloudiness", weather_data["clouds"]["all"]) \
            .field("visibility", weather_data.get("visibility", 0)) \
            .time(datetime.utcnow(), WritePrecision.NS)
        
        # Write to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        
        print(f"✅ Weather data sent to InfluxDB: {weather_data['name']}, {weather_data['main']['temp']}°C")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error sending data to InfluxDB: {e}")
        return False

def main():
    """Main function"""
    print("🌤️  Weather Data to InfluxDB")
    print("=" * 40)
    
    # Check configuration
    if OPENWEATHER_API_KEY == 'your_api_key_here':
        print("❌ Please set your OpenWeather API key in OPENWEATHER_API_KEY environment variable")
        return
    
    if INFLUXDB_TOKEN == 'your_token_here':
        print("❌ Please set your InfluxDB token in INFLUXDB_TOKEN environment variable")
        return
    
    # Fetch and send weather data
    weather_data = get_weather_data()
    if weather_data:
        print(f"📊 Current weather in {weather_data['name']}: {weather_data['main']['temp']}°C")
        send_to_influxdb(weather_data)
    else:
        print("❌ Failed to fetch weather data")

if __name__ == "__main__":
    main()
