# Metroverse Data Scraper

Automated extraction tool for Harvard Growth Lab's Metroverse platform using Playwright.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Extract City Data
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

### 3. Find City IDs
Visit https://metroverse.hks.harvard.edu/ and search for your city. The URL will show: `/city/{ID}/`

## How It Works

The Playwright extractor:
- Opens the city page in a headless browser
- Captures all GraphQL network requests automatically
- Extracts JSON data including city metrics, industries, and economic data
- Saves to `metroverse_data/raw_json/{cityID}_data.json`

## Output Structure

```
metroverse_data/
├── raw_json/           # Extracted JSON files
│   ├── 1105_data.json  # Buenos Aires
│   ├── 2973_data.json  # Stockholm
│   └── 2643_data.json  # London
├── processed/          # Processed data
├── csv_tables/         # CSV exports
└── playwright_extractor.py  # Main extraction script
```

## Data Processing

After extraction, process the JSON data:
```bash
cd metroverse_data
python data_linker.py
```

This creates structured CSV tables from the raw JSON responses.

## Playwright Approach Details

### Network Interception
- Automatically captures all network requests
- Filters for JSON responses (GraphQL endpoints)
- No manual browser interaction required

### Data Extraction Process
1. **Page Load**: Opens city page in headless Chrome
2. **Network Capture**: Intercepts all API calls
3. **Data Wait**: Waits 15 seconds for React to load
4. **JSON Export**: Saves all captured responses
5. **File Naming**: Uses format `{cityID}_data.json`

### Advantages
- **Fully automated** - No manual steps
- **Complete data** - Captures all API responses
- **Reliable** - Handles JavaScript-heavy sites
- **Consistent naming** - Organized file structure

## Troubleshooting

**Installation Issues:**
```bash
# If playwright fails
playwright install --force chromium

# If dependencies conflict
pip install --upgrade playwright
```

**No Data Captured:**
- Verify city ID is correct
- Check internet connection
- Try with `headless=False` for debugging

**File Location:**
All extracted files are saved to `metroverse_data/raw_json/` with the naming pattern `{cityID}_data.json`
