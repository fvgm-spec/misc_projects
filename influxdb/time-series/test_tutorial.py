#!/usr/bin/env python3
"""
Test script for Time Series Autoregression Tutorial
Tests all code examples from the tutorial with local InfluxDB
"""

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error, mean_absolute_error
import json
import warnings
warnings.filterwarnings('ignore')

# Load InfluxDB configuration
with open('../weather-influxdb/influxdb_config.json', 'r') as f:
    config = json.load(f)

INFLUXDB_URL = config["url"]
INFLUXDB_TOKEN = config["token"]
INFLUXDB_ORG = config["org"]
INFLUXDB_BUCKET = config["bucket"]

print("🧪 Testing Time Series Autoregression Tutorial")
print("=" * 50)

# Initialize client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def generate_sample_temperature_data():
    """Generate realistic temperature data with seasonal patterns"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    
    # Create temperature data with trend and seasonality
    trend = np.linspace(15, 18, len(dates))
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.normal(0, 2, len(dates))
    temperature = trend + seasonal + noise
    
    return pd.DataFrame({
        'timestamp': dates,
        'temperature': temperature
    })

def store_data_in_influxdb(df):
    """Store temperature data in InfluxDB"""
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    for _, row in df.iterrows():
        point = Point("temperature") \
            .field("value", row['temperature']) \
            .time(row['timestamp'], WritePrecision.NS)
        
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    
    print(f"✅ Stored {len(df)} temperature readings in InfluxDB")

def load_data_from_influxdb():
    """Retrieve temperature data from InfluxDB"""
    query_api = client.query_api()
    
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: -1y)
    |> filter(fn: (r) => r._measurement == "temperature")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    
    result = query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
    if len(result) == 0:
        return pd.Series(dtype=float)
    
    result['_time'] = pd.to_datetime(result['_time'])
    result = result.set_index('_time').sort_index()
    
    return result['value']

def build_ar_model(series, order=5, train_size=0.8):
    """Build and train an autoregressive model"""
    
    # Split data into training and testing sets
    split_point = int(len(series) * train_size)
    train_data = series[:split_point]
    test_data = series[split_point:]
    
    # Fit AR model
    model = AutoReg(train_data, lags=order, trend='c')
    fitted_model = model.fit()
    
    print(f"📊 AR({order}) Model fitted successfully")
    print(f"   Training samples: {len(train_data)}")
    print(f"   Test samples: {len(test_data)}")
    
    return fitted_model, train_data, test_data

def make_predictions(model, train_data, test_data):
    """Generate predictions using the fitted AR model"""
    
    # In-sample predictions (on training data)
    in_sample_pred = model.fittedvalues
    
    # Out-of-sample predictions (on test data)
    start_idx = len(train_data)
    end_idx = len(train_data) + len(test_data) - 1
    out_sample_pred = model.predict(start=start_idx, end=end_idx)
    
    return in_sample_pred, out_sample_pred

def evaluate_model_performance(actual, predicted, model_name="AR Model"):
    """Calculate and display model performance metrics"""
    
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(actual, predicted)
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    
    print(f"\n📈 {model_name} Performance Metrics:")
    print(f"   MSE: {mse:.4f}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   MAE: {mae:.4f}")
    print(f"   MAPE: {mape:.2f}%")
    
    return {"MSE": mse, "RMSE": rmse, "MAE": mae, "MAPE": mape}

def main():
    """Main test function"""
    
    # Step 1: Generate and store sample data
    print("1️⃣  Generating sample temperature data...")
    sample_data = generate_sample_temperature_data()
    store_data_in_influxdb(sample_data)
    
    # Step 2: Load data from InfluxDB
    print("\n2️⃣  Loading data from InfluxDB...")
    temperature_series = load_data_from_influxdb()
    print(f"✅ Loaded {len(temperature_series)} temperature observations")
    
    if len(temperature_series) == 0:
        print("❌ No data found in InfluxDB")
        return
    
    # Step 3: Build AR model
    print("\n3️⃣  Building AR model...")
    ar_model, train_series, test_series = build_ar_model(temperature_series, order=7)
    
    # Step 4: Generate predictions
    print("\n4️⃣  Generating predictions...")
    train_predictions, test_predictions = make_predictions(ar_model, train_series, test_series)
    print(f"✅ Generated {len(test_predictions)} test predictions")
    
    # Step 5: Evaluate performance
    print("\n5️⃣  Evaluating model performance...")
    test_metrics = evaluate_model_performance(test_series, test_predictions, "AR(7) Test Set")
    
    # Step 6: Create simple visualization
    print("\n6️⃣  Creating visualization...")
    plt.figure(figsize=(12, 6))
    plt.plot(test_series.index, test_series.values, label='Actual', marker='o', markersize=3)
    plt.plot(test_predictions.index, test_predictions.values, label='Predicted', marker='s', markersize=3)
    plt.title('Temperature Forecast: AR Model Test Results')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('ar_model_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✅ Visualization saved as 'ar_model_results.png'")
    
    print(f"\n🎉 Tutorial test completed successfully!")
    print(f"📊 Model achieved RMSE of {test_metrics['RMSE']:.2f}°C on test data")
    
    client.close()

if __name__ == "__main__":
    main()
