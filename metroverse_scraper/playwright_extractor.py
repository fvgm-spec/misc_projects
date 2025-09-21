#!/usr/bin/env python3
"""
Playwright automation - Automated Metroverse data extraction
"""
import json
import sys
import os

def extract_with_playwright(city_id, city_name=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install playwright: pip install playwright")
        print("Then run: playwright install")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Capture network responses
        responses = []
        
        def handle_response(response):
            if 'json' in response.headers.get('content-type', ''):
                try:
                    data = response.json()
                    responses.append({
                        'url': response.url,
                        'status': response.status,
                        'data': data
                    })
                    print(f"Captured: {response.url}")
                except:
                    pass
        
        page.on('response', handle_response)
        
        # Navigate and wait for network activity
        url = f'https://metroverse.hks.harvard.edu/city/{city_id}/'
        try:
            page.goto(url, wait_until='networkidle', timeout=60000)  # 60 second timeout
        except:
            # Fallback if networkidle fails
            page.goto(url, timeout=30000)
            page.wait_for_timeout(10000)  # Wait 10 seconds instead
        
        # Wait for React to load data
        page.wait_for_timeout(10000)  # Reduced from 15 to 10 seconds
        
        # Try to extract from page context
        page_data = page.evaluate("""
            () => {
                return {
                    windowData: window.__DATA__ || null,
                    initialState: window.__INITIAL_STATE__ || null,
                    cityData: window.cityData || null,
                    reactProps: window.__REACT_DEVTOOLS_GLOBAL_HOOK__ ? 'available' : null
                };
            }
        """)
        
        # Save all captured data
        all_data = {
            'network_responses': responses,
            'page_data': page_data,
            'city_id': city_id
        }
        
        # Create filename as {cityID}_data.json in metroverse_data/raw_json/
        os.makedirs('metroverse_data/raw_json', exist_ok=True)
        filename = f'metroverse_data/raw_json/{city_id}_data.json'
        
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"Saved {len(responses)} network responses to {filename}")
        print(f"Data location: {os.path.abspath(filename)}")
        print(f"File size: {os.path.getsize(filename) / 1024 / 1024:.1f} MB")
        browser.close()
        
        return filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playwright_extractor.py <city_id>")
        print("Example: python playwright_extractor.py 1105")
        sys.exit(1)
    
    city_id = sys.argv[1]
    extract_with_playwright(city_id)
