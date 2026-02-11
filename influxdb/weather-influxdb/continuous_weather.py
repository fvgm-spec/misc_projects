#!/usr/bin/env python3
"""
Continuous Weather Data Collection
Runs weather data collection every 5 minutes
"""

import time
import schedule
from weather_to_influx import get_weather_data, send_to_influxdb

def collect_weather():
    """Collect and send weather data"""
    print(f"🕐 {time.strftime('%Y-%m-%d %H:%M:%S')} - Collecting weather data...")
    weather_data = get_weather_data()
    if weather_data:
        send_to_influxdb(weather_data)
    else:
        print("❌ Failed to collect weather data")

def main():
    """Main continuous collection loop"""
    print("🌤️  Starting continuous weather data collection...")
    print("📊 Data will be collected every 5 minutes")
    print("⏹️  Press Ctrl+C to stop")
    
    # Schedule weather collection every 5 minutes
    schedule.every(5).minutes.do(collect_weather)
    
    # Run initial collection
    collect_weather()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping weather data collection...")

if __name__ == "__main__":
    main()
