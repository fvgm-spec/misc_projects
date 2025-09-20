# Metroverse Data Extractor

A comprehensive toolkit for extracting and processing data from Harvard Growth Lab's Metroverse portal (https://metroverse.hks.harvard.edu/).

## Overview

The Metroverse portal contains rich economic data for cities worldwide, including:
- Industry employment and complexity data
- Economic composition analysis
- Growth opportunities assessment
- Cluster analysis
- Time series economic indicators

This toolkit provides multiple approaches to extract this data for analysis.

## Project Structure

```
metroverse_scraper/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── requirements_simple.txt      # Minimal dependencies
├── config.py                   # Configuration settings
├── 
├── # Extraction Scripts
├── enhanced_extractor.py        # Full-featured extractor (requires pandas)
├── simple_extractor.py          # HTML-based extractor
├── basic_extractor.py           # No pandas dependency
├── api_extractor.py             # Direct API approach
├── browser_extractor.py         # Selenium-based automation
├── 
├── # Utilities
├── run_extraction.py            # Command-line runner
├── manual_extraction_guide.py   # Creates manual extraction resources
├── sample_processor.py          # Process manually extracted JSON
├── 
├── # Templates and Guides
├── guides/
│   └── manual_extraction_guide.md
├── templates/
│   ├── city_metadata.csv
│   ├── industries.csv
│   ├── clusters.csv
│   ├── economic_indicators.csv
│   └── growth_opportunities.csv
└── 
└── # Output Directories (created during extraction)
    ├── metroverse_data/
    ├── raw_html/
    ├── extracted_json/
    ├── csv_tables/
    ├── screenshots/
    └── network_logs/
```

## Installation

### Basic Setup
```bash
cd /home/felix/projects/metroverse_scraper
pip install -r requirements_simple.txt
```

### Full Setup (with pandas)
```bash
pip install -r requirements.txt
```

### Browser Automation Setup
```bash
pip install selenium
# Download chromedriver from https://chromedriver.chromium.org/
```

## Usage Methods

### Method 1: Manual Extraction (Recommended)

The Metroverse portal uses React with dynamic data loading, making manual extraction the most reliable approach:

```bash
python manual_extraction_guide.py
```

This creates:
- Detailed extraction guide (`guides/manual_extraction_guide.md`)
- CSV templates for organizing data
- Sample processing script

**Steps:**
1. Visit https://metroverse.hks.harvard.edu/city/3444/ (Bucharest)
2. Open browser Developer Tools (F12)
3. Go to Network tab and refresh page
4. Look for API calls containing city data
5. Copy JSON responses and save to files
6. Use provided templates to organize data

### Method 2: Basic HTML Extraction

```bash
python basic_extractor.py
```

Extracts data from the HTML page structure (limited data available).

### Method 3: Browser Automation

```bash
python browser_extractor.py
```

Uses Selenium to load the page and capture network requests (requires chromedriver).

### Method 4: API Discovery

```bash
python api_extractor.py
```

Attempts to discover and call API endpoints directly.

## Sample City IDs

- **Bucharest**: 3444
- **New York**: 1840
- **London**: 2643
- **Tokyo**: 1275
- **Berlin**: 2077

## Expected Data Structure

### City Metadata
- Basic information (name, country, population)
- Economic indicators (GDP per capita, complexity index)
- Geographic data (coordinates, region)

### Industry Data
- Employment figures by industry
- Revealed Comparative Advantage (RCA) values
- Industry complexity scores
- Growth opportunities

### Cluster Data
- Industry cluster classifications
- Cluster employment and complexity
- Strategic value assessments

### Time Series Data
- Historical economic indicators
- Employment trends
- Complexity evolution

## Output Formats

All extractors save data in multiple formats:
- **Raw JSON**: Original API responses
- **CSV**: Structured tabular data
- **Excel**: Formatted spreadsheets (where supported)

## Configuration

Edit `config.py` to modify:
- API endpoints to test
- Rate limiting settings
- Output formats
- Sample cities list

## Troubleshooting

### No Data Extracted
- The site uses dynamic loading; try manual extraction
- Check network requests in browser dev tools
- Verify city ID exists

### API Endpoints Not Working
- The APIs may require authentication
- Try browser automation approach
- Use manual extraction method

### Dependencies Issues
- Use `requirements_simple.txt` for minimal setup
- Install selenium separately for browser automation
- Check numpy/pandas compatibility

## Legal and Ethical Considerations

- **Respect Terms of Service**: Check Metroverse terms before large-scale extraction
- **Rate Limiting**: Don't overwhelm the servers
- **Research Use**: Intended for academic/research purposes
- **Contact Harvard**: Consider reaching out for official data access

## Data Quality Notes

- **Completeness**: Not all cities have complete data
- **Updates**: Data may be updated periodically
- **Methodology**: Check Harvard Growth Lab documentation for data methodology
- **Validation**: Cross-reference with official sources when possible

## Advanced Usage

### Processing Multiple Cities
```python
from basic_extractor import BasicMetroverseExtractor

extractor = BasicMetroverseExtractor()
cities = ["3444", "1840", "2643"]  # Bucharest, NYC, London

for city_id in cities:
    result = extractor.process_city(city_id)
    print(f"Processed {city_id}: {result}")
```

### Custom Data Processing
```python
import json
from sample_processor import process_city_json, save_as_csv

# Process manually extracted JSON
data = process_city_json('bucharest_data.json', '3444')
save_as_csv(data, 'output_folder')
```

## Contributing

To extend the toolkit:
1. Add new extraction methods in separate files
2. Update `config.py` with new endpoints
3. Create corresponding CSV templates
4. Update this README

## Support

For issues:
1. Check the manual extraction guide first
2. Verify city IDs and URLs
3. Test with browser dev tools
4. Consider contacting Harvard Growth Lab for official data access

## References

- **Metroverse Portal**: https://metroverse.hks.harvard.edu/
- **Harvard Growth Lab**: https://growthlab.cid.harvard.edu/
- **Frontend Code**: https://github.com/cid-harvard/cities-atlas-front-end
- **Economic Complexity**: https://atlas.cid.harvard.edu/

---

**Note**: This toolkit is for research and educational purposes. Always respect the website's terms of service and consider official data access channels for large-scale projects.
