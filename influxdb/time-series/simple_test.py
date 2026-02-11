#!/usr/bin/env python3
"""
Simple test of Time Series Autoregression Tutorial
Uses synthetic data to test the AR model implementation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

print("🧪 Testing Time Series Autoregression Tutorial")
print("=" * 50)

def generate_temperature_data():
    """Generate realistic temperature data with seasonal patterns"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # Create temperature data with trend and seasonality
    trend = np.linspace(15, 18, len(dates))
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.normal(0, 2, len(dates))
    temperature = trend + seasonal + noise
    
    return pd.Series(temperature, index=dates)

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
    
    # Step 1: Generate sample data
    print("1️⃣  Generating sample temperature data...")
    temperature_series = generate_temperature_data()
    print(f"✅ Generated {len(temperature_series)} temperature observations")
    
    # Step 2: Build AR model
    print("\n2️⃣  Building AR model...")
    ar_model, train_series, test_series = build_ar_model(temperature_series, order=5)
    
    # Step 3: Generate predictions
    print("\n3️⃣  Generating predictions...")
    train_predictions, test_predictions = make_predictions(ar_model, train_series, test_series)
    print(f"✅ Generated {len(test_predictions)} test predictions")
    
    # Step 4: Evaluate performance
    print("\n4️⃣  Evaluating model performance...")
    test_metrics = evaluate_model_performance(test_series, test_predictions, "AR(5) Test Set")
    
    # Step 5: Create visualization
    print("\n5️⃣  Creating visualization...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Full time series with predictions
    ax1 = axes[0, 0]
    full_series = pd.concat([train_series, test_series])
    full_pred = pd.concat([train_predictions, test_predictions])
    ax1.plot(full_series.index, full_series.values, label='Actual', alpha=0.7)
    ax1.plot(full_pred.index, full_pred.values, label='Predicted', alpha=0.7)
    ax1.axvline(x=train_series.index[-1], color='red', linestyle='--', alpha=0.5, label='Train/Test Split')
    ax1.set_title('Temperature Forecast: AR Model')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Test period focus
    ax2 = axes[0, 1]
    ax2.plot(test_series.index, test_series.values, label='Actual', marker='o', markersize=3)
    ax2.plot(test_predictions.index, test_predictions.values, label='Predicted', marker='s', markersize=3)
    ax2.set_title('Test Period Predictions')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Residuals
    ax3 = axes[1, 0]
    residuals = test_series.values - test_predictions.values
    ax3.plot(test_series.index, residuals, marker='o', markersize=3)
    ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax3.set_title('Prediction Residuals')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Residuals histogram
    ax4 = axes[1, 1]
    ax4.hist(residuals, bins=10, alpha=0.7, edgecolor='black')
    ax4.set_title('Residuals Distribution')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('ar_model_complete_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✅ Visualization saved as 'ar_model_complete_results.png'")
    
    # Step 6: Model summary
    print(f"\n📋 Model Summary:")
    print(f"   AR Order: 5")
    print(f"   Training Period: {train_series.index[0].strftime('%Y-%m-%d')} to {train_series.index[-1].strftime('%Y-%m-%d')}")
    print(f"   Test Period: {test_series.index[0].strftime('%Y-%m-%d')} to {test_series.index[-1].strftime('%Y-%m-%d')}")
    print(f"   Model Coefficients: {len(ar_model.params)} parameters")
    
    print(f"\n🎉 Tutorial test completed successfully!")
    print(f"📊 Model achieved RMSE of {test_metrics['RMSE']:.2f}°C on test data")
    print(f"📈 Model achieved MAPE of {test_metrics['MAPE']:.1f}% on test data")
    
    if test_metrics['MAPE'] < 15:
        print("✅ Model performance is good (MAPE < 15%)")
    elif test_metrics['MAPE'] < 25:
        print("⚠️  Model performance is acceptable (MAPE < 25%)")
    else:
        print("❌ Model performance needs improvement (MAPE > 25%)")

if __name__ == "__main__":
    main()
