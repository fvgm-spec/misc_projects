# Weather Data to InfluxDB

This project fetches weather data from OpenWeather API and stores it in InfluxDB for time-series analysis.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup InfluxDB
```bash
python setup_influxdb.py
```

### 3. Get OpenWeather API Key
1. Sign up at https://openweathermap.org/api
2. Get your free API key

### 4. Configure Environment Variables
```bash
export OPENWEATHER_API_KEY="your_api_key_here"
export INFLUXDB_TOKEN="your_token_from_setup"
export INFLUXDB_ORG="weather_org"
export INFLUXDB_BUCKET="weather"
```

## Usage

### Single Run
```bash
python weather_to_influx.py
```

### Continuous Monitoring
```bash
python continuous_weather.py
```

## InfluxDB Web UI

Access the InfluxDB web interface at: http://localhost:8086

## Data Structure

The weather data is stored with the following fields:
- `temperature` (°C)
- `humidity` (%)
- `pressure` (hPa)
- `wind_speed` (m/s)
- `wind_direction` (degrees)
- `cloudiness` (%)
- `visibility` (meters)

Tags:
- `city`
- `country`
