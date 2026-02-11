#!/usr/bin/env python3
"""
Complete Demo Script
Shows the full workflow of weather data collection and storage
"""

import json
import time
from test_weather import send_demo_data_to_influxdb, load_config

def generate_multiple_demo_readings():
    """Generate multiple demo weather readings"""
    print("🌤️  Generating multiple weather readings...")
    
    # Simulate different weather conditions
    demo_conditions = [
        {"temp": 20.1, "humidity": 70, "wind_speed": 2.1, "cloudiness": 10},
        {"temp": 22.5, "humidity": 65, "wind_speed": 3.2, "cloudiness": 25},
        {"temp": 25.3, "humidity": 55, "wind_speed": 4.5, "cloudiness": 40},
        {"temp": 18.7, "humidity": 80, "wind_speed": 1.8, "cloudiness": 75},
        {"temp": 16.2, "humidity": 85, "wind_speed": 6.2, "cloudiness": 90}
    ]
    
    config = load_config()
    
    for i, conditions in enumerate(demo_conditions, 1):
        print(f"📊 Reading {i}/5: {conditions['temp']}°C, {conditions['humidity']}% humidity")
        
        # Create and send demo data (you would modify test_weather.py to accept parameters)
        send_demo_data_to_influxdb()
        
        if i < len(demo_conditions):
            time.sleep(2)  # Wait 2 seconds between readings
    
    print("✅ All demo readings sent!")

def show_influxdb_info():
    """Show InfluxDB connection information"""
    config = load_config()
    
    print("\n" + "="*60)
    print("📊 INFLUXDB INFORMATION")
    print("="*60)
    print(f"🌐 Web UI: {config['url']}")
    print(f"🏢 Organization: {config['org']}")
    print(f"🪣 Bucket: {config['bucket']}")
    print(f"🔑 Token: {config['token'][:20]}...")
    print("\n💡 Next Steps:")
    print("   1. Open the InfluxDB UI in your browser")
    print("   2. Login with the token above")
    print("   3. Go to Data Explorer")
    print("   4. Select 'weather' bucket to view your data")
    print("   5. Create dashboards and alerts!")

def main():
    """Main demo function"""
    print("🚀 Weather Data to InfluxDB - Complete Demo")
    print("="*60)
    
    try:
        # Generate demo data
        generate_multiple_demo_readings()
        
        # Show connection info
        show_influxdb_info()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📈 Check your InfluxDB dashboard to see the weather data")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
