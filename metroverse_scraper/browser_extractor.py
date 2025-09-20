#!/usr/bin/env python3
"""
Browser-based Metroverse Data Extractor
Uses selenium to load the page and extract data after JavaScript execution
"""

import json
import csv
import os
import time
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserMetroverseExtractor:
    def __init__(self, output_dir: str = "metroverse_data", headless: bool = True):
        self.base_url = "https://metroverse.hks.harvard.edu"
        self.output_dir = output_dir
        self.headless = headless
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'screenshots'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'network_logs'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'extracted_data'), exist_ok=True)
        
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome driver with network logging"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            
            # Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Enable logging
            caps = DesiredCapabilities.CHROME
            caps['goog:loggingPrefs'] = {'performance': 'ALL'}
            
            self.driver = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)
            logger.info("Chrome driver initialized successfully")
            return True
            
        except ImportError:
            logger.error("Selenium not installed. Install with: pip install selenium")
            return False
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            logger.info("Make sure Chrome and chromedriver are installed")
            return False
    
    def extract_network_requests(self) -> List[Dict]:
        """Extract network requests from browser logs"""
        try:
            logs = self.driver.get_log('performance')
            network_requests = []
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    if 'json' in response.get('mimeType', '').lower():
                        network_requests.append({
                            'url': response['url'],
                            'status': response['status'],
                            'mimeType': response.get('mimeType', ''),
                            'timestamp': log['timestamp']
                        })
            
            return network_requests
            
        except Exception as e:
            logger.error(f"Error extracting network requests: {e}")
            return []
    
    def wait_for_data_load(self, timeout: int = 30):
        """Wait for data to load by checking for specific elements"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Wait for various possible data containers
            wait = WebDriverWait(self.driver, timeout)
            
            # Common selectors for data visualization libraries
            selectors = [
                '[class*="chart"]',
                '[class*="graph"]',
                '[class*="visualization"]',
                '[class*="data"]',
                'svg',
                'canvas',
                '[id*="chart"]',
                '[id*="graph"]'
            ]
            
            for selector in selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info(f"Found data element: {selector}")
                    return True
                except:
                    continue
            
            logger.warning("No data elements found, proceeding anyway")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for data load: {e}")
            return False
    
    def extract_javascript_data(self) -> Dict[str, Any]:
        """Extract data from JavaScript variables"""
        try:
            # Common JavaScript variable patterns to check
            js_patterns = [
                "return window.__INITIAL_STATE__",
                "return window.__DATA__",
                "return window.cityData",
                "return window.appData",
                "return window.pageData"
            ]
            
            extracted_data = {}
            
            for i, pattern in enumerate(js_patterns):
                try:
                    result = self.driver.execute_script(pattern)
                    if result:
                        extracted_data[f'js_data_{i}'] = result
                        logger.info(f"Extracted data from: {pattern}")
                except Exception as e:
                    logger.debug(f"No data from {pattern}: {e}")
            
            # Try to extract from React components
            try:
                react_data = self.driver.execute_script("""
                    var reactElements = document.querySelectorAll('[data-reactroot]');
                    if (reactElements.length > 0) {
                        return reactElements[0]._reactInternalInstance || 
                               reactElements[0]._reactInternalFiber ||
                               'React found but no data';
                    }
                    return null;
                """)
                if react_data:
                    extracted_data['react_data'] = react_data
            except:
                pass
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript data: {e}")
            return {}
    
    def extract_dom_data(self) -> Dict[str, Any]:
        """Extract data from DOM elements"""
        try:
            from selenium.webdriver.common.by import By
            
            dom_data = {}
            
            # Look for data attributes
            elements_with_data = self.driver.find_elements(By.CSS_SELECTOR, '[data-*]')
            data_attributes = {}
            
            for element in elements_with_data[:50]:  # Limit to first 50
                try:
                    attrs = self.driver.execute_script("""
                        var attrs = {};
                        for (var i = 0; i < arguments[0].attributes.length; i++) {
                            var attr = arguments[0].attributes[i];
                            if (attr.name.startsWith('data-')) {
                                attrs[attr.name] = attr.value;
                            }
                        }
                        return attrs;
                    """, element)
                    
                    if attrs:
                        data_attributes.update(attrs)
                except:
                    continue
            
            if data_attributes:
                dom_data['data_attributes'] = data_attributes
            
            # Extract text content from potential data containers
            selectors = [
                '.city-profile',
                '.economic-data',
                '.industry-data',
                '.chart-container',
                '[class*="data"]',
                '[class*="metric"]'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        texts = [elem.text.strip() for elem in elements if elem.text.strip()]
                        if texts:
                            dom_data[f'text_{selector.replace(".", "").replace("[", "").replace("]", "")}'] = texts
                except:
                    continue
            
            return dom_data
            
        except Exception as e:
            logger.error(f"Error extracting DOM data: {e}")
            return {}
    
    def process_city(self, city_id: str, city_name: str = None) -> Dict[str, Any]:
        """Process a single city using browser automation"""
        if not self.setup_driver():
            return {}
        
        try:
            logger.info(f"Processing city {city_id} ({city_name or 'Unknown'})")
            
            # Navigate to city page
            url = f"{self.base_url}/city/{city_id}/"
            logger.info(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for initial load
            time.sleep(5)
            
            # Take screenshot
            screenshot_path = os.path.join(self.output_dir, 'screenshots', f'{city_id}_page.png')
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Wait for data to load
            self.wait_for_data_load()
            
            # Additional wait for dynamic content
            time.sleep(10)
            
            # Extract network requests
            network_data = self.extract_network_requests()
            
            # Extract JavaScript data
            js_data = self.extract_javascript_data()
            
            # Extract DOM data
            dom_data = self.extract_dom_data()
            
            # Get page source
            page_source = self.driver.page_source
            
            # Compile results
            result = {
                'city_id': city_id,
                'city_name': city_name,
                'url': url,
                'network_requests': network_data,
                'javascript_data': js_data,
                'dom_data': dom_data,
                'page_source_length': len(page_source)
            }
            
            # Save results
            self.save_extraction_results(result, city_id)
            
            # Save page source
            source_path = os.path.join(self.output_dir, 'extracted_data', f'{city_id}_page_source.html')
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            logger.info(f"Extraction completed for city {city_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing city {city_id}: {e}")
            return {}
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_extraction_results(self, result: Dict[str, Any], city_id: str):
        """Save extraction results to files"""
        
        # Save network requests
        if result.get('network_requests'):
            network_file = os.path.join(self.output_dir, 'network_logs', f'{city_id}_network.json')
            with open(network_file, 'w', encoding='utf-8') as f:
                json.dump(result['network_requests'], f, indent=2)
            logger.info(f"Network requests saved: {network_file}")
        
        # Save all extracted data
        data_file = os.path.join(self.output_dir, 'extracted_data', f'{city_id}_extracted.json')
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Extracted data saved: {data_file}")
        
        # Convert to CSV where possible
        self.convert_to_csv(result, city_id)
    
    def convert_to_csv(self, result: Dict[str, Any], city_id: str):
        """Convert extracted data to CSV format"""
        
        # Convert network requests to CSV
        if result.get('network_requests'):
            csv_file = os.path.join(self.output_dir, 'extracted_data', f'{city_id}_network_requests.csv')
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if result['network_requests']:
                    writer = csv.DictWriter(f, fieldnames=result['network_requests'][0].keys())
                    writer.writeheader()
                    writer.writerows(result['network_requests'])
            logger.info(f"Network requests CSV saved: {csv_file}")
        
        # Convert JavaScript data to CSV
        if result.get('javascript_data'):
            for key, data in result['javascript_data'].items():
                if isinstance(data, (list, dict)):
                    csv_file = os.path.join(self.output_dir, 'extracted_data', f'{city_id}_{key}.csv')
                    self.save_data_as_csv(data, csv_file, city_id)

    def save_data_as_csv(self, data: Any, filename: str, city_id: str):
        """Save data as CSV"""
        try:
            rows = []
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        flat_item = self.flatten_dict(item)
                        flat_item['city_id'] = city_id
                        rows.append(flat_item)
            elif isinstance(data, dict):
                flat_data = self.flatten_dict(data)
                flat_data['city_id'] = city_id
                rows.append(flat_data)
            
            if rows:
                all_keys = set()
                for row in rows:
                    all_keys.update(row.keys())
                
                fieldnames = ['city_id'] + [key for key in sorted(all_keys) if key != 'city_id']
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                
                logger.info(f"Data CSV saved: {filename} ({len(rows)} rows)")
        
        except Exception as e:
            logger.error(f"Error saving CSV {filename}: {e}")
    
    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if len(v) > 0 and isinstance(v[0], dict):
                    items.append((f"{new_key}_count", len(v)))
                    if v:
                        items.extend(self.flatten_dict(v[0], f"{new_key}_first", sep=sep).items())
                else:
                    items.append((new_key, ', '.join(map(str, v))))
            else:
                items.append((new_key, v))
        return dict(items)

def main():
    """Test the browser extractor"""
    print("Browser-based Metroverse Extractor")
    print("This requires selenium and chromedriver to be installed")
    print("Install with: pip install selenium")
    print("And download chromedriver from: https://chromedriver.chromium.org/")
    
    try:
        extractor = BrowserMetroverseExtractor(headless=False)  # Set to True for headless mode
        result = extractor.process_city("3444", "Bucharest")
        
        print(f"\nExtraction Results:")
        print(f"- Network requests captured: {len(result.get('network_requests', []))}")
        print(f"- JavaScript data sections: {len(result.get('javascript_data', {}))}")
        print(f"- DOM data sections: {len(result.get('dom_data', {}))}")
        print(f"- Page source length: {result.get('page_source_length', 0)} characters")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure selenium and chromedriver are properly installed")

if __name__ == "__main__":
    main()
