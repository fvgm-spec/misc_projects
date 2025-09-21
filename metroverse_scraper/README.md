# Metroverse Data Scraper

Automated extraction tool for Harvard Growth Lab's Metroverse platform using Playwright.

## About Playwright

This project uses [Playwright for Python](https://playwright.dev/python/docs/intro) - a powerful browser automation library that enables reliable end-to-end testing and web scraping. Playwright provides:

- **Cross-browser support**: Chromium, Firefox, and WebKit
- **Network interception**: Capture API calls and responses
- **JavaScript execution**: Handle dynamic content loading
- **Headless operation**: Run without visible browser window

### How Playwright is Used in This Project

1. **Browser Automation**: Opens Metroverse city pages in headless Chrome
2. **Network Monitoring**: Intercepts GraphQL API calls automatically
3. **Data Extraction**: Captures JSON responses from network requests
4. **JavaScript Handling**: Waits for React components to load data
5. **Reliable Extraction**: Handles timeouts and dynamic content gracefully

## Installation

### Option 1: Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Option 2: Using Makefile
```bash
# Install everything with one command
make install
```

## Usage

### Extract City Data
```bash
python playwright_extractor.py <city_id>
```

**Examples:**
```bash
# Buenos Aires (ID: 1105)
python playwright_extractor.py 1105

# Stockholm (ID: 2973)  
python playwright_extractor.py 2973

# London (ID: 2643)
python playwright_extractor.py 2643
```

### Find City IDs
Visit https://metroverse.hks.harvard.edu/ and search for your city. The URL will show: `/city/{ID}/`

## Data Storage

### Extracted Data Location
All extracted data is automatically saved to:
```
metroverse_data/raw_json/{cityID}_data.json
```

**Example file paths:**
- `metroverse_data/raw_json/1105_data.json` (Buenos Aires)
- `metroverse_data/raw_json/2973_data.json` (Stockholm)
- `metroverse_data/raw_json/2643_data.json` (London)

### Data Structure
Each JSON file contains:
```json
{
  "network_responses": [
    {
      "url": "https://metroverse.hks.harvard.edu/graphql",
      "status": 200,
      "data": {
        "city": {
          "name": "Buenos Aires",
          "population": 15000000,
          "gdpPerCapita": 25000,
          "industries": [...]
        }
      }
    }
  ],
  "page_data": {...},
  "city_id": "1105"
}
```

## Project Structure

```
metroverse_scraper/
├── README.md                    # This documentation
├── requirements.txt             # Python dependencies
├── Makefile                     # Installation automation
├── playwright_extractor.py      # Main extraction script
├── data_processor.py            # Data processing utilities
└── metroverse_data/
    └── raw_json/               # Extracted JSON files
        ├── 1105_data.json      # Buenos Aires data
        ├── 2973_data.json      # Stockholm data
        └── {cityID}_data.json  # Other city extractions
```

## Data Processing

After extraction, process the JSON data:
```bash
python data_processor.py
```

This creates structured CSV tables in `metroverse_data/csv_tables/`

## Playwright Technical Details

### Network Interception
```python
def handle_response(response):
    if 'json' in response.headers.get('content-type', ''):
        # Capture GraphQL responses automatically
        data = response.json()
```

### Timeout Handling
- **Page load timeout**: 60 seconds for networkidle
- **Fallback mechanism**: 30-second load + 10-second wait
- **Data wait**: 10 seconds for React components

### Browser Configuration
- **Headless mode**: No visible browser window
- **Chromium engine**: Most reliable for Metroverse
- **Network logging**: Captures all JSON responses

## Troubleshooting

**Installation Issues:**
```bash
# Force reinstall Playwright browsers
playwright install --force chromium

# Update dependencies
pip install --upgrade playwright
```

**Timeout Errors:**
- Script automatically handles timeouts with fallback
- Increase wait times if needed for slow connections
- Check internet connectivity

**No Data Captured:**
- Verify city ID exists on Metroverse
- Check console output for captured URLs
- Ensure GraphQL endpoints are being hit

**File Not Found:**
- Data is saved to `metroverse_data/raw_json/`
- Check file naming: `{cityID}_data.json`
- Verify directory permissions
