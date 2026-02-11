#!/usr/bin/env python3
"""
Fixed test script for Time Series Autoregression Tutorial
"""

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.ar_model import AutoReg
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

print("🧪 Testing Time Series Autoregression Tutorial (Fixed)")
print("=" * 55)

# Initialize client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def generate_sample_temperature_data():
    """Generate realistic temperature data with seasonal patterns"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')  # Reduced for testing
    
    # Create temperature data with trend and seasonality
    trend = np.linspace(15, 18, len(dates))
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.normal(0, 2, len(dates))
    temperature = trend + seasonal + noise
    
    return pd.DataFrame({
        'timestamp': dates,
        'temperature': temperature
    })

def store_temperature_data(df):
    """Store temperature data in InfluxDB with proper measurement name"""
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    for _, row in df.iterrows():
        point = Point("temp_forecast") \
            .field("value", float(row['temperature'])) \
            .time(row['timestamp'], WritePrecision.NS)
        
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    
    print(f"✅ Stored {len(df)} temperature readings in InfluxDB")

def load_temperature_data():
    """Retrieve temperature data from InfluxDB"""
    query_api = client.query_api()
    
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "temp_forecast")
    |> filter(fn: (r) => r._field == "value")
    |> sort(columns: ["_time"])
    '''
    
    result = query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
    
    if len(result) == 0:
        return pd.Series(dtype=float)
    
    result['_time'] = pd.to_datetime(result['_time'])
    result = result.set_index('_time').sort_index()
    
    return result['_value']

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
    store_temperature_data(sample_data)
    
    # Step 2: Load data from InfluxDB
    print("\n2️⃣  Loading data from InfluxDB...")
    temperature_series = load_temperature_data()
    print(f"✅ Loaded {len(temperature_series)} temperature observations")
    
    if len(temperature_series) == 0:
        print("❌ No data found in InfluxDB")
        return
    
    # Step 3: Build AR model
    print("\n3️⃣  Building AR model...")
    ar_model, train_series, test_series = build_ar_model(temperature_series, order=5)
    
    # Step 4: Generate predictions
    print("\n4️⃣  Generating predictions...")
    train_predictions, test_predictions = make_predictions(ar_model, train_series, test_series)
    print(f"✅ Generated {len(test_predictions)} test predictions")
    
    # Step 5: Evaluate performance
    print("\n5️⃣  Evaluating model performance...")
    test_metrics = evaluate_model_performance(test_series, test_predictions, "AR(5) Test Set")
    
    # Step 6: Create simple visualization
    print("\n6️⃣  Creating visualization...")
    plt.figure(figsize=(12, 6))
    
    # Plot full series
    plt.subplot(1, 2, 1)
    full_series = pd.concat([train_series, test_series])
    full_pred = pd.concat([train_predictions, test_predictions])
    plt.plot(full_series.index, full_series.values, label='Actual', alpha=0.7)
    plt.plot(full_pred.index, full_pred.values, label='Predicted', alpha=0.7)
    plt.axvline(x=train_series.index[-1], color='red', linestyle='--', alpha=0.5, label='Train/Test Split')
    plt.title('Full Temperature Series')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot test period only
    plt.subplot(1, 2, 2)
    plt.plot(test_series.index, test_series.values, label='Actual', marker='o', markersize=4)
    plt.plot(test_predictions.index, test_predictions.values, label='Predicted', marker='s', markersize=4)
    plt.title('Test Period Predictions')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('ar_model_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✅ Visualization saved as 'ar_model_results.png'")
    
    print(f"\n🎉 Tutorial test completed successfully!")
    print(f"📊 Model achieved RMSE of {test_metrics['RMSE']:.2f}°C on test data")
    print(f"📈 Model achieved MAPE of {test_metrics['MAPE']:.1f}% on test data")
    
    client.close()

if __name__ == "__main__":
    main()
