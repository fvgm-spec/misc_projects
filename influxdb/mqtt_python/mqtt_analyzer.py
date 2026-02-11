#!/usr/bin/env python3
"""
MQTT Data Analyzer
Analyzes MQTT data stored in InfluxDB 3
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from influxdb3 import InfluxDB3Client
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTDataAnalyzer:
    """Analyzes MQTT data from InfluxDB 3"""
    
    def __init__(self):
        self.influxdb_host = os.getenv('INFLUXDB_HOST', 'localhost')
        self.influxdb_port = int(os.getenv('INFLUXDB_PORT', 8181))
        self.influxdb_token = os.getenv('INFLUXDB_TOKEN')
        self.influxdb_database = os.getenv('INFLUXDB_DATABASE', 'mqtt_data')
        
        # Initialize client
        self.client = InfluxDB3Client(
            host=f"http://{self.influxdb_host}:{self.influxdb_port}",
            token=self.influxdb_token,
            database=self.influxdb_database
        )
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def query_data(self, query: str) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        try:
            result = self.client.query(query)
            df = result.to_pandas()
            logger.info(f"Query returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return pd.DataFrame()
    
    def get_sensor_summary(self) -> pd.DataFrame:
        """Get summary statistics for all sensors"""
        query = """
        SELECT 
            sensor_type,
            location,
            COUNT(*) as message_count,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            STDDEV(value) as std_value
        FROM sensors
        WHERE time >= now() - INTERVAL '24 hours'
        AND value IS NOT NULL
        GROUP BY sensor_type, location
        ORDER BY message_count DESC
        """
        return self.query_data(query)
    
    def get_time_series_data(self, sensor_type: str, hours: int = 24) -> pd.DataFrame:
        """Get time series data for specific sensor type"""
        query = f"""
        SELECT 
            time,
            location,
            value,
            sensor_id
        FROM sensors
        WHERE sensor_type = '{sensor_type}'
        AND time >= now() - INTERVAL '{hours} hours'
        AND value IS NOT NULL
        ORDER BY time
        """
        return self.query_data(query)
    
    def plot_sensor_trends(self, sensor_type: str, hours: int = 24):
        """Plot sensor trends over time"""
        df = self.get_time_series_data(sensor_type, hours)
        
        if df.empty:
            logger.warning(f"No data found for sensor type: {sensor_type}")
            return
        
        # Convert time to datetime
        df['time'] = pd.to_datetime(df['time'])
        
        # Create subplots for each location
        locations = df['location'].unique()
        fig, axes = plt.subplots(len(locations), 1, figsize=(12, 4*len(locations)))
        
        if len(locations) == 1:
            axes = [axes]
        
        for i, location in enumerate(locations):
            location_data = df[df['location'] == location]
            
            # Plot time series
            axes[i].plot(location_data['time'], location_data['value'], 
                        marker='o', markersize=2, alpha=0.7)
            axes[i].set_title(f'{sensor_type.title()} - {location.title()}')
            axes[i].set_ylabel('Value')
            axes[i].grid(True, alpha=0.3)
            
            # Add rolling average
            if len(location_data) > 10:
                location_data_sorted = location_data.sort_values('time')
                rolling_avg = location_data_sorted['value'].rolling(window=10, center=True).mean()
                axes[i].plot(location_data_sorted['time'], rolling_avg, 
                           color='red', linewidth=2, alpha=0.8, label='10-point average')
                axes[i].legend()
        
        plt.tight_layout()
        plt.savefig(f'mqtt_{sensor_type}_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_sensor_distribution(self, sensor_type: str):
        """Plot distribution of sensor values by location"""
        df = self.get_time_series_data(sensor_type, hours=24)
        
        if df.empty:
            logger.warning(f"No data found for sensor type: {sensor_type}")
            return
        
        plt.figure(figsize=(12, 6))
        
        # Box plot
        plt.subplot(1, 2, 1)
        sns.boxplot(data=df, x='location', y='value')
        plt.title(f'{sensor_type.title()} Distribution by Location')
        plt.xticks(rotation=45)
        
        # Histogram
        plt.subplot(1, 2, 2)
        for location in df['location'].unique():
            location_data = df[df['location'] == location]['value']
            plt.hist(location_data, alpha=0.6, label=location, bins=20)
        
        plt.title(f'{sensor_type.title()} Value Distribution')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'mqtt_{sensor_type}_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def detect_anomalies(self, sensor_type: str, threshold_std: float = 2.0) -> pd.DataFrame:
        """Detect anomalies using statistical methods"""
        df = self.get_time_series_data(sensor_type, hours=24)
        
        if df.empty:
            return pd.DataFrame()
        
        # Calculate statistics by location
        anomalies = []
        
        for location in df['location'].unique():
            location_data = df[df['location'] == location].copy()
            
            # Calculate mean and standard deviation
            mean_val = location_data['value'].mean()
            std_val = location_data['value'].std()
            
            # Define anomaly thresholds
            upper_threshold = mean_val + (threshold_std * std_val)
            lower_threshold = mean_val - (threshold_std * std_val)
            
            # Find anomalies
            location_anomalies = location_data[
                (location_data['value'] > upper_threshold) | 
                (location_data['value'] < lower_threshold)
            ].copy()
            
            location_anomalies['anomaly_type'] = location_anomalies['value'].apply(
                lambda x: 'high' if x > upper_threshold else 'low'
            )
            location_anomalies['threshold_exceeded'] = location_anomalies['value'].apply(
                lambda x: abs(x - mean_val) / std_val
            )
            
            anomalies.append(location_anomalies)
        
        if anomalies:
            result = pd.concat(anomalies, ignore_index=True)
            logger.info(f"Found {len(result)} anomalies for {sensor_type}")
            return result
        
        return pd.DataFrame()
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        logger.info("Generating MQTT data analysis report...")
        
        # Get summary statistics
        summary = self.get_sensor_summary()
        print("\n=== SENSOR SUMMARY ===")
        print(summary.to_string(index=False))
        
        # Analyze each sensor type
        sensor_types = summary['sensor_type'].unique()
        
        for sensor_type in sensor_types:
            print(f"\n=== {sensor_type.upper()} ANALYSIS ===")
            
            # Plot trends and distributions
            self.plot_sensor_trends(sensor_type)
            self.plot_sensor_distribution(sensor_type)
            
            # Detect anomalies
            anomalies = self.detect_anomalies(sensor_type)
            if not anomalies.empty:
                print(f"\nAnomalies detected for {sensor_type}:")
                print(anomalies[['time', 'location', 'value', 'anomaly_type', 'threshold_exceeded']].to_string(index=False))
            else:
                print(f"No anomalies detected for {sensor_type}")
        
        logger.info("Report generation completed")

def main():
    """Main function"""
    analyzer = MQTTDataAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
