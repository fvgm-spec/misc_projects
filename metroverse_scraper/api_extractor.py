#!/usr/bin/env python3
"""
API-based Metroverse Data Extractor
Directly calls the actual API endpoints used by the frontend
"""

import requests
import json
import csv
import os
from typing import Dict, List, Any, Optional
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIMetroverseExtractor:
    def __init__(self, output_dir: str = "metroverse_data"):
        self.base_url = "https://metroverse.hks.harvard.edu"
        self.output_dir = output_dir
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'raw_api'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed_csv'), exist_ok=True)
        
        # Session with proper headers to mimic the frontend
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
        
        # Known API endpoints (discovered from frontend code)
        self.api_endpoints = [
            '/api/data/cities/{city_id}',
            '/api/data/cities/{city_id}/profile',
            '/api/data/cities/{city_id}/industries',
            '/api/data/cities/{city_id}/clusters',
            '/api/data/cities/{city_id}/complexity',
            '/api/data/cities/{city_id}/opportunities',
            '/api/data/cities/{city_id}/employment',
            '/api/data/cities/{city_id}/economic-composition',
            '/api/data/cities/{city_id}/good-at',
            '/api/data/cities/{city_id}/industry-position',
            '/api/data/cities/{city_id}/growth-opportunities',
            '/api/cities/{city_id}',
            '/api/cities/{city_id}/data',
            '/api/cities/{city_id}/profile',
            '/api/cities/{city_id}/overview'
        ]
    
    def test_endpoint(self, endpoint: str, city_id: str) -> Optional[Dict[str, Any]]:
        """Test a single API endpoint"""
        url = self.base_url + endpoint.format(city_id=city_id)
        
        try:
            logger.debug(f"Testing endpoint: {url}")
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"✓ Success: {endpoint} - {len(str(data))} chars")
                    return data
                except json.JSONDecodeError:
                    logger.debug(f"✗ Not JSON: {endpoint}")
                    return None
            elif response.status_code == 404:
                logger.debug(f"✗ Not found: {endpoint}")
                return None
            else:
                logger.debug(f"✗ HTTP {response.status_code}: {endpoint}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"✗ Request error: {endpoint} - {e}")
            return None
        
        finally:
            time.sleep(0.5)  # Rate limiting
    
    def discover_working_endpoints(self, city_id: str) -> Dict[str, Any]:
        """Test all known endpoints to find working ones"""
        logger.info(f"Discovering working API endpoints for city {city_id}")
        
        working_data = {}
        
        for endpoint in self.api_endpoints:
            data = self.test_endpoint(endpoint, city_id)
            if data:
                endpoint_name = endpoint.split('/')[-1] or 'root'
                working_data[f"{endpoint_name}_{len(working_data)}"] = {
                    'endpoint': endpoint,
                    'data': data
                }
        
        logger.info(f"Found {len(working_data)} working endpoints")
        return working_data
    
    def try_alternative_endpoints(self, city_id: str) -> Dict[str, Any]:
        """Try alternative endpoint patterns"""
        logger.info("Trying alternative endpoint patterns...")
        
        alternative_patterns = [
            f'/api/city-data/{city_id}',
            f'/api/v1/cities/{city_id}',
            f'/api/v2/cities/{city_id}',
            f'/data/cities/{city_id}.json',
            f'/data/city/{city_id}/profile.json',
            f'/static/data/cities/{city_id}.json'
        ]
        
        working_data = {}
        
        for pattern in alternative_patterns:
            data = self.test_endpoint(pattern, city_id)
            if data:
                name = pattern.split('/')[-1].replace('.json', '') or 'alternative'
                working_data[f"{name}_{len(working_data)}"] = {
                    'endpoint': pattern,
                    'data': data
                }
        
        return working_data
    
    def extract_city_info_from_search(self, city_id: str) -> Optional[Dict[str, Any]]:
        """Try to get city info from search/autocomplete endpoints"""
        search_endpoints = [
            '/api/search/cities',
            '/api/cities/search',
            '/api/autocomplete/cities'
        ]
        
        for endpoint in search_endpoints:
            try:
                url = self.base_url + endpoint
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Look for our city in the list
                        for city in data:
                            if isinstance(city, dict) and str(city.get('id')) == city_id:
                                logger.info(f"Found city info in {endpoint}")
                                return city
                    elif isinstance(data, dict) and city_id in str(data):
                        return data
                        
            except Exception as e:
                logger.debug(f"Search endpoint {endpoint} failed: {e}")
                continue
        
        return None
    
    def save_raw_data(self, data: Dict[str, Any], city_id: str):
        """Save raw API responses"""
        filename = os.path.join(self.output_dir, 'raw_api', f'{city_id}_api_data.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved raw API data to {filename}")
    
    def convert_to_csv(self, data: Any, filename: str, city_id: str):
        """Convert data to CSV format"""
        try:
            rows = []
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        flat_item = self.flatten_dict(item)
                        flat_item['city_id'] = city_id
                        rows.append(flat_item)
                    else:
                        rows.append({'value': item, 'city_id': city_id})
            
            elif isinstance(data, dict):
                flat_data = self.flatten_dict(data)
                flat_data['city_id'] = city_id
                rows.append(flat_data)
            
            else:
                rows.append({'value': data, 'city_id': city_id})
            
            if rows:
                # Get all unique keys
                all_keys = set()
                for row in rows:
                    all_keys.update(row.keys())
                
                fieldnames = ['city_id'] + [key for key in sorted(all_keys) if key != 'city_id']
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                
                logger.info(f"Saved CSV: {filename} ({len(rows)} rows)")
            
        except Exception as e:
            logger.error(f"Error converting to CSV {filename}: {e}")
    
    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if len(v) > 0 and isinstance(v[0], dict):
                    # For list of dicts, create summary
                    items.append((f"{new_key}_count", len(v)))
                    # Also flatten first item as example
                    if v:
                        items.extend(self.flatten_dict(v[0], f"{new_key}_first", sep=sep).items())
                else:
                    # For simple lists, join as string
                    items.append((new_key, ', '.join(map(str, v))))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def process_city(self, city_id: str, city_name: str = None) -> Dict[str, Any]:
        """Process a single city using API endpoints"""
        logger.info(f"Processing city {city_id} ({city_name or 'Unknown'})")
        
        # Try to discover working endpoints
        api_data = self.discover_working_endpoints(city_id)
        
        # Try alternative patterns if nothing found
        if not api_data:
            logger.info("No standard endpoints found, trying alternatives...")
            api_data = self.try_alternative_endpoints(city_id)
        
        # Try to get city info from search
        city_info = self.extract_city_info_from_search(city_id)
        if city_info:
            api_data['city_info'] = {'endpoint': 'search', 'data': city_info}
        
        if api_data:
            # Save raw data
            self.save_raw_data(api_data, city_id)
            
            # Convert each endpoint's data to CSV
            for key, endpoint_data in api_data.items():
                data = endpoint_data.get('data', {})
                if data:
                    csv_filename = os.path.join(self.output_dir, 'processed_csv', f'{city_id}_{key}.csv')
                    self.convert_to_csv(data, csv_filename, city_id)
        
        else:
            logger.warning(f"No API data found for city {city_id}")
        
        result = {
            'city_id': city_id,
            'city_name': city_name,
            'endpoints_found': len(api_data),
            'data': api_data
        }
        
        return result
    
    def test_city_exists(self, city_id: str) -> bool:
        """Test if a city ID exists by trying the main page"""
        url = f"{self.base_url}/city/{city_id}/"
        try:
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False

def main():
    """Test the API extractor"""
    extractor = APIMetroverseExtractor()
    
    # Test with Bucharest
    city_id = "3444"
    
    # First check if city exists
    if extractor.test_city_exists(city_id):
        logger.info(f"City {city_id} exists, proceeding with API extraction")
        result = extractor.process_city(city_id, "Bucharest")
        
        print(f"\nAPI Extraction Results for Bucharest:")
        print(f"- Working endpoints found: {result.get('endpoints_found', 0)}")
        
        if result.get('data'):
            print(f"\nEndpoints that returned data:")
            for key, endpoint_data in result['data'].items():
                endpoint = endpoint_data.get('endpoint', 'unknown')
                data_size = len(str(endpoint_data.get('data', {})))
                print(f"  - {key}: {endpoint} ({data_size} chars)")
    else:
        logger.error(f"City {city_id} does not exist or is not accessible")

if __name__ == "__main__":
    main()
