#!/usr/bin/env python3
"""
Test Weather Data Collection
Uses demo data to test InfluxDB integration
"""

import json
import os
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

def load_config():
    """Load InfluxDB configuration"""
    with open('influxdb_config.json', 'r') as f:
        return json.load(f)

def create_demo_weather_data():
    """Create demo weather data for testing"""
    return {
        "name": "Montevideo",
        "sys": {"country": "UY"},
        "main": {
            "temp": 22.5,
            "humidity": 65,
            "pressure": 1013
        },
        "wind": {
            "speed": 3.2,
            "deg": 180
        },
        "clouds": {"all": 25},
        "visibility": 10000
    }

def send_demo_data_to_influxdb():
    """Send demo weather data to InfluxDB"""
    config = load_config()
    weather_data = create_demo_weather_data()
    
    try:
        # Create InfluxDB client
        client = InfluxDBClient(
            url=config["url"], 
            token=config["token"], 
            org=config["org"]
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        # Create data point
        point = Point("weather") \
            .tag("city", weather_data["name"]) \
            .tag("country", weather_data["sys"]["country"]) \
            .field("temperature", weather_data["main"]["temp"]) \
            .field("humidity", weather_data["main"]["humidity"]) \
            .field("pressure", weather_data["main"]["pressure"]) \
            .field("wind_speed", weather_data["wind"]["speed"]) \
            .field("wind_direction", weather_data["wind"]["deg"]) \
            .field("cloudiness", weather_data["clouds"]["all"]) \
            .field("visibility", weather_data["visibility"]) \
            .time(datetime.utcnow(), WritePrecision.NS)
        
        # Write to InfluxDB
        write_api.write(bucket=config["bucket"], org=config["org"], record=point)
        
        print(f"✅ Demo weather data sent to InfluxDB!")
        print(f"📊 {weather_data['name']}: {weather_data['main']['temp']}°C, {weather_data['main']['humidity']}% humidity")
        
        # Query the data back to verify
        query_api = client.query_api()
        query = f'''
        from(bucket: "{config["bucket"]}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "weather")
        |> last()
        '''
        
        result = query_api.query(org=config["org"], query=query)
        
        print(f"\n📋 Data verification:")
        for table in result:
            for record in table.records:
                print(f"   {record.get_field()}: {record.get_value()}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing InfluxDB Weather Data Integration")
    print("=" * 50)
    
    if not os.path.exists('influxdb_config.json'):
        print("❌ Configuration file not found. Run setup_influxdb.py first.")
        return
    
    send_demo_data_to_influxdb()
    
    print(f"\n🌐 Access InfluxDB UI at: http://localhost:8086")
    print(f"📊 Navigate to Data Explorer to view your weather data")

if __name__ == "__main__":
    main()
