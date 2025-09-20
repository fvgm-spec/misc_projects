
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

