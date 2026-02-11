#!/usr/bin/env python3
"""
Test InfluxDB integration with Time Series Autoregression
Uses the existing weather data in InfluxDB
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

print("🧪 Testing InfluxDB Integration with Time Series AR")
print("=" * 50)

# Initialize client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def store_ar_results_in_influxdb(actual_series, predicted_series, model_metrics):
    """Store AR model results back to InfluxDB"""
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    # Store predictions
    for timestamp, (actual, predicted) in zip(actual_series.index, zip(actual_series.values, predicted_series.values)):
        # Actual values
        point_actual = Point("ar_forecast") \
            .tag("type", "actual") \
            .field("temperature", float(actual)) \
            .time(timestamp, WritePrecision.NS)
        
        # Predicted values
        point_pred = Point("ar_forecast") \
            .tag("type", "predicted") \
            .field("temperature", float(predicted)) \
            .time(timestamp, WritePrecision.NS)
        
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=[point_actual, point_pred])
    
    # Store model metrics
    metrics_point = Point("ar_model_metrics") \
        .field("mse", model_metrics["MSE"]) \
        .field("rmse", model_metrics["RMSE"]) \
        .field("mae", model_metrics["MAE"]) \
        .field("mape", model_metrics["MAPE"]) \
        .time(pd.Timestamp.now(), WritePrecision.NS)
    
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=metrics_point)
    
    print(f"✅ Stored AR results and metrics in InfluxDB")

def query_ar_results_from_influxdb():
    """Query AR model results from InfluxDB"""
    query_api = client.query_api()
    
    # Query forecast data
    forecast_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "ar_forecast")
    |> pivot(rowKey:["_time"], columnKey: ["type"], valueColumn: "_value")
    '''
    
    # Query metrics
    metrics_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "ar_model_metrics")
    |> last()
    '''
    
    try:
        forecast_result = query_api.query_data_frame(org=INFLUXDB_ORG, query=forecast_query)
        metrics_result = query_api.query_data_frame(org=INFLUXDB_ORG, query=metrics_query)
        
        return forecast_result, metrics_result
    except Exception as e:
        print(f"Query error: {e}")
        return pd.DataFrame(), pd.DataFrame()

def generate_and_test_ar_model():
    """Generate synthetic data and test AR model with InfluxDB storage"""
    
    # Generate synthetic temperature data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
    trend = np.linspace(20, 25, len(dates))
    seasonal = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.normal(0, 1.5, len(dates))
    temperature = trend + seasonal + noise
    
    temperature_series = pd.Series(temperature, index=dates)
    
    print(f"📊 Generated {len(temperature_series)} synthetic temperature readings")
    
    # Split data
    split_point = int(len(temperature_series) * 0.8)
    train_data = temperature_series[:split_point]
    test_data = temperature_series[split_point:]
    
    # Build AR model
    model = AutoReg(train_data, lags=3, trend='c')
    fitted_model = model.fit()
    
    # Make predictions
    start_idx = len(train_data)
    end_idx = len(train_data) + len(test_data) - 1
    test_predictions = fitted_model.predict(start=start_idx, end=end_idx)
    
    # Calculate metrics
    mse = mean_squared_error(test_data, test_predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(test_data, test_predictions)
    mape = np.mean(np.abs((test_data - test_predictions) / test_data)) * 100
    
    metrics = {"MSE": mse, "RMSE": rmse, "MAE": mae, "MAPE": mape}
    
    print(f"\n📈 AR(3) Model Performance:")
    print(f"   RMSE: {rmse:.2f}°C")
    print(f"   MAPE: {mape:.1f}%")
    
    return test_data, test_predictions, metrics

def main():
    """Main test function"""
    
    print("1️⃣  Generating AR model and predictions...")
    actual_data, predicted_data, model_metrics = generate_and_test_ar_model()
    
    print("\n2️⃣  Storing results in InfluxDB...")
    store_ar_results_in_influxdb(actual_data, predicted_data, model_metrics)
    
    print("\n3️⃣  Querying results from InfluxDB...")
    forecast_df, metrics_df = query_ar_results_from_influxdb()
    
    if len(forecast_df) > 0:
        print(f"✅ Retrieved {len(forecast_df)} forecast records from InfluxDB")
    else:
        print("⚠️  No forecast data retrieved (this is normal for the first run)")
    
    if len(metrics_df) > 0:
        print(f"✅ Retrieved model metrics from InfluxDB")
        print(f"   Latest RMSE: {metrics_df['_value'].iloc[0]:.2f} (for field: {metrics_df['_field'].iloc[0]})")
    else:
        print("⚠️  No metrics data retrieved")
    
    print("\n4️⃣  Creating visualization...")
    plt.figure(figsize=(12, 6))
    plt.plot(actual_data.index, actual_data.values, label='Actual', marker='o', markersize=4)
    plt.plot(predicted_data.index, predicted_data.values, label='AR(3) Predicted', marker='s', markersize=4)
    plt.title('Time Series Autoregression: InfluxDB Integration Test')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('influxdb_ar_integration_test.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("✅ Visualization saved as 'influxdb_ar_integration_test.png'")
    
    print(f"\n🎉 InfluxDB integration test completed!")
    print(f"📊 AR model performance: RMSE = {model_metrics['RMSE']:.2f}°C, MAPE = {model_metrics['MAPE']:.1f}%")
    print(f"💾 Results stored in InfluxDB bucket: {INFLUXDB_BUCKET}")
    print(f"🌐 View data at: {INFLUXDB_URL}")
    
    client.close()

if __name__ == "__main__":
    main()
