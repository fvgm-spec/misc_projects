#!/usr/bin/env python3
"""
InfluxDB Setup Script
Creates organization, bucket, and token for weather data
"""

import requests
import json
import sys

INFLUXDB_URL = "http://localhost:8086"

def setup_influxdb():
    """Setup InfluxDB for weather data"""
    print("🔧 Setting up InfluxDB for weather data...")
    
    # Initial setup payload
    setup_data = {
        "username": "admin",
        "password": "password123",
        "org": "weather_org",
        "bucket": "weather",
        "retentionPeriodSeconds": 0  # Infinite retention
    }
    
    try:
        # Check if setup is needed
        response = requests.get(f"{INFLUXDB_URL}/api/v2/setup")
        setup_status = response.json()
        
        if setup_status.get("allowed", False):
            print("📝 Performing initial InfluxDB setup...")
            
            # Perform setup
            response = requests.post(
                f"{INFLUXDB_URL}/api/v2/setup",
                json=setup_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                result = response.json()
                print("✅ InfluxDB setup completed!")
                print(f"📋 Organization: {result['org']['name']}")
                print(f"📋 Bucket: {result['bucket']['name']}")
                print(f"🔑 Token: {result['auth']['token']}")
                
                # Save configuration to file
                config = {
                    "url": INFLUXDB_URL,
                    "org": result['org']['name'],
                    "bucket": result['bucket']['name'],
                    "token": result['auth']['token']
                }
                
                with open('influxdb_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("💾 Configuration saved to influxdb_config.json")
                
            else:
                print(f"❌ Setup failed: {response.text}")
        else:
            print("ℹ️  InfluxDB is already set up")
            print("🔍 Check existing configuration or use the web UI at http://localhost:8086")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to InfluxDB. Make sure it's running on http://localhost:8086")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_influxdb()
