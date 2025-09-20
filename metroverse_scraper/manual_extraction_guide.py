#!/usr/bin/env python3
"""
Manual Extraction Guide for Metroverse Data
Provides instructions and tools for manual data extraction
"""

import json
import csv
import os
from typing import Dict, List, Any

def create_manual_extraction_guide():
    """Create a comprehensive guide for manual data extraction"""
    
    guide = """
# Manual Metroverse Data Extraction Guide

Since the Metroverse portal uses a React-based frontend with dynamic data loading,
here are several approaches to extract the data:

## Method 1: Browser Developer Tools (Recommended)

1. **Open the city page** in Chrome/Firefox:
   https://metroverse.hks.harvard.edu/city/3444/ (Bucharest example)

2. **Open Developer Tools** (F12)

3. **Go to Network tab** and refresh the page

4. **Look for API calls** in the network requests:
   - Filter by "XHR" or "Fetch" 
   - Look for requests to endpoints containing:
     - /api/
     - /data/
     - .json files
     - GraphQL endpoints

5. **Copy the response data**:
   - Click on each API request
   - Go to "Response" tab
   - Copy the JSON data
   - Save to files

## Method 2: Console Data Extraction

1. **Open Console tab** in Developer Tools

2. **Try these JavaScript commands** to extract data:

```javascript
// Check for common data variables
console.log(window.__INITIAL_STATE__);
console.log(window.__DATA__);
console.log(window.cityData);
console.log(window.appData);

// Extract React component data
var reactRoot = document.querySelector('[data-reactroot]');
if (reactRoot) {
    console.log(reactRoot._reactInternalInstance);
}

// Look for Redux store
if (window.__REDUX_DEVTOOLS_EXTENSION__) {
    console.log('Redux store available');
}

// Extract all data attributes
var dataElements = document.querySelectorAll('[data-*]');
dataElements.forEach(el => {
    for (let attr of el.attributes) {
        if (attr.name.startsWith('data-')) {
            console.log(attr.name, attr.value);
        }
    }
});
```

## Method 3: Source Code Analysis

1. **View page source** (Ctrl+U)

2. **Look for embedded JSON** in script tags:
   - Search for "window.__" 
   - Search for large JSON objects
   - Look for data initialization scripts

3. **Extract and format** the JSON data

## Method 4: Using Browser Extensions

1. **Install JSON Viewer** extensions
2. **Install Web Scraper** extensions  
3. **Use network monitoring** extensions

## Data Structure to Look For

Based on the Metroverse frontend code, look for these data types:

### City Profile Data
- Basic city information (name, country, population)
- Economic indicators (GDP per capita, complexity index)
- Geographic data (coordinates, region)

### Industry Data
- Industry employment figures
- Revealed Comparative Advantage (RCA) values
- Industry complexity scores
- Growth opportunities by industry

### Cluster Data
- Industry cluster classifications
- Cluster employment data
- Cluster complexity metrics

### Time Series Data
- Historical economic indicators
- Employment trends over time
- Complexity evolution

## Expected API Endpoints (to monitor in Network tab)

Look for requests to URLs containing:
- `/city/{id}/profile`
- `/city/{id}/industries`
- `/city/{id}/clusters`
- `/city/{id}/opportunities`
- `/city/{id}/complexity`
- `/economic-composition`
- `/good-at`
- `/industry-position`
- `/growth-opportunities`

## Sample Cities to Test

- Bucharest: 3444
- New York: 1840  
- London: 2643
- Tokyo: 1275
- Berlin: 2077

## Data Processing

Once you have the raw JSON data:

1. **Validate the JSON** format
2. **Flatten nested structures** for CSV export
3. **Normalize data types** (dates, numbers)
4. **Create separate tables** for different data types
5. **Add city metadata** to each record

## Automation Options

If manual extraction becomes tedious:

1. **Browser automation** with Selenium
2. **Headless browser** scraping with Puppeteer
3. **API reverse engineering** with network analysis tools
4. **Contact Harvard Growth Lab** for official data access

## Legal Considerations

- Check the website's Terms of Service
- Respect rate limits and server resources  
- Consider reaching out for official data access
- Use data responsibly for research purposes

## Troubleshooting

**No data visible**: The page might be loading data asynchronously
**Empty API responses**: Check authentication or rate limiting
**CORS errors**: Data might only be accessible from the same domain
**Minified code**: Use browser dev tools to format/prettify

"""
    
    return guide

def create_data_template():
    """Create template files for organizing extracted data"""
    
    templates = {
        'city_metadata.csv': [
            'city_id', 'city_name', 'country', 'country_code', 
            'population', 'gdp_per_capita', 'latitude', 'longitude',
            'complexity_index', 'complexity_rank', 'data_year'
        ],
        
        'industries.csv': [
            'city_id', 'industry_id', 'industry_name', 'industry_code',
            'employment', 'employment_share', 'rca', 'complexity',
            'opportunity_gain', 'distance', 'feasibility'
        ],
        
        'clusters.csv': [
            'city_id', 'cluster_id', 'cluster_name', 'cluster_type',
            'employment', 'employment_share', 'rca', 'complexity',
            'num_industries', 'avg_wages'
        ],
        
        'economic_indicators.csv': [
            'city_id', 'year', 'indicator_name', 'indicator_value',
            'indicator_type', 'data_source', 'methodology'
        ],
        
        'growth_opportunities.csv': [
            'city_id', 'industry_id', 'industry_name', 'opportunity_gain',
            'distance', 'complexity', 'strategic_value', 'feasibility_score'
        ]
    }
    
    return templates

def save_templates_and_guide():
    """Save the extraction guide and templates to files"""
    
    # Create directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('guides', exist_ok=True)
    
    # Save guide
    guide_content = create_manual_extraction_guide()
    with open('guides/manual_extraction_guide.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    # Save CSV templates
    templates = create_data_template()
    for filename, headers in templates.items():
        filepath = os.path.join('templates', filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    print("Created extraction guide and templates:")
    print("- guides/manual_extraction_guide.md")
    for filename in templates.keys():
        print(f"- templates/{filename}")

def create_sample_extraction_script():
    """Create a sample script for processing manually extracted JSON"""
    
    script = '''#!/usr/bin/env python3
"""
Sample script for processing manually extracted Metroverse JSON data
"""

import json
import csv
import os
from typing import Dict, List, Any

def process_city_json(json_file: str, city_id: str) -> Dict[str, List[Dict]]:
    """Process a manually extracted JSON file"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract different data types
    extracted = {
        'city_metadata': [],
        'industries': [],
        'clusters': [],
        'economic_indicators': []
    }
    
    # Process city metadata
    if 'city' in data:
        city_info = data['city']
        extracted['city_metadata'].append({
            'city_id': city_id,
            'city_name': city_info.get('name', ''),
            'country': city_info.get('country', ''),
            'population': city_info.get('population'),
            'gdp_per_capita': city_info.get('gdp_per_capita')
        })
    
    # Process industries
    if 'industries' in data:
        for industry in data['industries']:
            extracted['industries'].append({
                'city_id': city_id,
                'industry_id': industry.get('id'),
                'industry_name': industry.get('name'),
                'employment': industry.get('employment'),
                'rca': industry.get('rca'),
                'complexity': industry.get('complexity')
            })
    
    # Add similar processing for clusters, indicators, etc.
    
    return extracted

def save_as_csv(data: Dict[str, List[Dict]], output_dir: str):
    """Save extracted data as CSV files"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    for table_name, records in data.items():
        if records:
            filename = os.path.join(output_dir, f'{table_name}.csv')
            
            # Get all unique keys
            all_keys = set()
            for record in records:
                all_keys.update(record.keys())
            
            fieldnames = sorted(all_keys)
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
            
            print(f"Saved {filename}: {len(records)} records")

# Example usage:
# data = process_city_json('bucharest_data.json', '3444')
# save_as_csv(data, 'processed_data')
'''
    
    with open('sample_processor.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("Created sample_processor.py")

def main():
    """Create all manual extraction resources"""
    print("Creating manual extraction resources...")
    
    save_templates_and_guide()
    create_sample_extraction_script()
    
    print("\nManual extraction resources created!")
    print("\nNext steps:")
    print("1. Read guides/manual_extraction_guide.md")
    print("2. Visit https://metroverse.hks.harvard.edu/city/3444/")
    print("3. Use browser dev tools to extract data")
    print("4. Use templates/ files to organize your data")
    print("5. Use sample_processor.py to process JSON files")

if __name__ == "__main__":
    main()
