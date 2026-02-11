#!/bin/bash

# MQTT Python Tutorial Setup Script
# Sets up the complete environment for MQTT data collection and analysis

echo "🚀 Setting up MQTT Python Tutorial Environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Create plugins directory
mkdir -p plugins
cp mqtt_processing_plugin.py plugins/

# Make scripts executable
chmod +x mqtt_collector.py
chmod +x mqtt_simulator.py
chmod +x mqtt_analyzer.py

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your InfluxDB and MQTT configuration"
echo "2. Start InfluxDB 3 with: influxdb3 serve --plugin-dir ./plugins"
echo "3. Run data simulator: python mqtt_simulator.py"
echo "4. Run data collector: python mqtt_collector.py"
echo "5. Analyze data: python mqtt_analyzer.py"
echo ""
echo "📚 See mqtt_tutorial.md for complete documentation"
