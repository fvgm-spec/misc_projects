# Metroverse Data Scraper Makefile

.PHONY: install setup test clean extract help

# Default target
help:
	@echo "Metroverse Data Scraper - Available Commands:"
	@echo ""
	@echo "  make install    - Install all dependencies"
	@echo "  make setup      - Setup project directories"
	@echo "  make test       - Test extraction with Buenos Aires"
	@echo "  make clean      - Clean extracted data"
	@echo "  make extract    - Interactive city extraction"
	@echo "  make help       - Show this help message"
	@echo ""

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Playwright browsers..."
	playwright install chromium
	@echo "Setup complete!"

# Setup project structure
setup:
	@echo "Creating project directories..."
	mkdir -p metroverse_data/raw_json
	mkdir -p metroverse_data/csv_tables
	@echo "Directories created!"

# Test extraction
test:
	@echo "Testing extraction with Buenos Aires (ID: 1105)..."
	python playwright_extractor.py 1105
	@echo "Test complete! Check metroverse_data/raw_json/1105_data.json"

# Clean extracted data
clean:
	@echo "Cleaning extracted data..."
	rm -f metroverse_data/raw_json/*.json
	rm -f metroverse_data/csv_tables/*.csv
	@echo "Data cleaned!"

# Interactive extraction
extract:
	@echo "Enter city ID to extract:"
	@read city_id; python playwright_extractor.py $$city_id

# Full setup (install + setup + test)
all: install setup test
	@echo "Full setup complete!"
