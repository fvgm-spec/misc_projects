#!/usr/bin/env python3
"""
Playwright automation - more reliable than Selenium
"""
import json
import sys

def extract_with_playwright(city_id):
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
        page.goto(url, wait_until='networkidle')
        
        # Wait for React to load data
        page.wait_for_timeout(15000)
        
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
        
        filename = f'{city_id}_playwright_data.json'
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"Saved {len(responses)} network responses to {filename}")
        browser.close()

if __name__ == "__main__":
    city_id = sys.argv[1] if len(sys.argv) > 1 else "1105"
    extract_with_playwright(city_id)
