#!/usr/bin/env python3
"""
Enhanced Metroverse Data Extractor
Handles the actual API structure and data formats
"""

import requests
import json
import pandas as pd
import os
from typing import Dict, List, Any, Optional, Union
import logging
from urllib.parse import urljoin
import time
from datetime import datetime
import numpy as np
from config import METROVERSE_CONFIG, SAMPLE_CITIES, OUTPUT_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMetroverseExtractor:
    def __init__(self, output_dir: str = "metroverse_data"):
        self.base_url = METROVERSE_CONFIG['base_url']
        self.endpoints = METROVERSE_CONFIG['api_endpoints']
        self.output_dir = output_dir
        self.rate_limit = METROVERSE_CONFIG['rate_limit_delay']
        
        # Create output directory structure
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'raw_json'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed_csv'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed_excel'), exist_ok=True)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://metroverse.hks.harvard.edu/'
        })
    
    def fetch_endpoint_data(self, city_id: str, endpoint_key: str) -> Optional[Dict[str, Any]]:
        """Fetch data from a specific endpoint"""
        endpoint = self.endpoints[endpoint_key].format(city_id=city_id)
        url = self.base_url + endpoint
        
        try:
            logger.info(f"Fetching {endpoint_key} for city {city_id}")
            response = self.session.get(url, timeout=METROVERSE_CONFIG['timeout'])
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched {endpoint_key}")
                return data
            else:
                logger.warning(f"Failed to fetch {endpoint_key}: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {endpoint_key}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {endpoint_key}: {e}")
            return None
        finally:
            time.sleep(self.rate_limit)
    
    def fetch_all_city_data(self, city_id: str) -> Dict[str, Any]:
        """Fetch all available data for a city"""
        city_data = {
            'city_id': city_id,
            'fetch_timestamp': datetime.now().isoformat(),
            'data': {}
        }
        
        for endpoint_key in self.endpoints.keys():
            data = self.fetch_endpoint_data(city_id, endpoint_key)
            if data:
                city_data['data'][endpoint_key] = data
        
        return city_data
    
    def extract_city_metadata(self, city_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract city metadata from any available endpoint"""
        metadata = []
        city_id = city_data['city_id']
        
        # Look for city info in any endpoint
        for endpoint_name, endpoint_data in city_data['data'].items():
            if isinstance(endpoint_data, dict):
                # Check various possible locations for city info
                city_info = None
                if 'city' in endpoint_data:
                    city_info = endpoint_data['city']
                elif 'location' in endpoint_data:
                    city_info = endpoint_data['location']
                elif 'metadata' in endpoint_data:
                    city_info = endpoint_data['metadata']
                
                if city_info:
                    metadata.append({
                        'city_id': city_id,
                        'city_name': city_info.get('name', ''),
                        'country': city_info.get('country', ''),
                        'country_code': city_info.get('country_code', ''),
                        'population': city_info.get('population'),
                        'gdp_per_capita': city_info.get('gdp_per_capita'),
                        'latitude': city_info.get('lat'),
                        'longitude': city_info.get('lng'),
                        'data_source': endpoint_name,
                        'fetch_timestamp': city_data['fetch_timestamp']
                    })
                    break
        
        if not metadata:
            # Create minimal metadata if no city info found
            metadata.append({
                'city_id': city_id,
                'city_name': f'City_{city_id}',
                'fetch_timestamp': city_data['fetch_timestamp']
            })
        
        return pd.DataFrame(metadata)
    
    def flatten_nested_data(self, data: Any, prefix: str = '') -> Dict[str, Any]:
        """Recursively flatten nested dictionaries and lists"""
        flattened = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    flattened.update(self.flatten_nested_data(value, new_key))
                else:
                    flattened[new_key] = value
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_key = f"{prefix}_{i}" if prefix else str(i)
                if isinstance(item, (dict, list)):
                    flattened.update(self.flatten_nested_data(item, new_key))
                else:
                    flattened[new_key] = item
        else:
            flattened[prefix] = data
        
        return flattened
    
    def extract_industries_data(self, city_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract and normalize industries data from all endpoints"""
        industries = []
        city_id = city_data['city_id']
        
        for endpoint_name, endpoint_data in city_data['data'].items():
            if isinstance(endpoint_data, dict):
                # Look for industry data in various structures
                industry_lists = []
                
                if 'industries' in endpoint_data:
                    industry_lists.append(('industries', endpoint_data['industries']))
                if 'data' in endpoint_data and isinstance(endpoint_data['data'], list):
                    industry_lists.append(('data', endpoint_data['data']))
                if 'results' in endpoint_data and isinstance(endpoint_data['results'], list):
                    industry_lists.append(('results', endpoint_data['results']))
                
                for list_name, industry_list in industry_lists:
                    if isinstance(industry_list, list):
                        for industry in industry_list:
                            if isinstance(industry, dict):
                                # Flatten the industry data
                                flat_industry = self.flatten_nested_data(industry)
                                flat_industry.update({
                                    'city_id': city_id,
                                    'data_source': endpoint_name,
                                    'list_source': list_name
                                })
                                industries.append(flat_industry)
        
        return pd.DataFrame(industries)
    
    def extract_economic_indicators(self, city_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract economic indicators and time series data"""
        indicators = []
        city_id = city_data['city_id']
        
        for endpoint_name, endpoint_data in city_data['data'].items():
            if isinstance(endpoint_data, dict):
                # Look for time series or indicator data
                for key, value in endpoint_data.items():
                    if isinstance(value, list) and key in ['time_series', 'indicators', 'metrics', 'years']:
                        for item in value:
                            if isinstance(item, dict):
                                flat_item = self.flatten_nested_data(item)
                                flat_item.update({
                                    'city_id': city_id,
                                    'data_source': endpoint_name,
                                    'indicator_type': key
                                })
                                indicators.append(flat_item)
        
        return pd.DataFrame(indicators)
    
    def extract_all_tabular_data(self, city_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Extract all possible tabular data from city data"""
        tables = {}
        
        # Basic metadata
        tables['city_metadata'] = self.extract_city_metadata(city_data)
        
        # Industries/sectors data
        industries_df = self.extract_industries_data(city_data)
        if not industries_df.empty:
            tables['industries'] = industries_df
        
        # Economic indicators
        indicators_df = self.extract_economic_indicators(city_data)
        if not indicators_df.empty:
            tables['economic_indicators'] = indicators_df
        
        # Extract data from each endpoint separately
        for endpoint_name, endpoint_data in city_data['data'].items():
            if isinstance(endpoint_data, dict):
                # Create a flattened version of the entire endpoint
                flat_data = self.flatten_nested_data(endpoint_data)
                if flat_data:
                    flat_data['city_id'] = city_data['city_id']
                    tables[f'{endpoint_name}_raw'] = pd.DataFrame([flat_data])
                
                # Look for specific data structures
                for key, value in endpoint_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        # Convert list of dicts to DataFrame
                        if all(isinstance(item, dict) for item in value):
                            df_data = []
                            for item in value:
                                flat_item = self.flatten_nested_data(item)
                                flat_item['city_id'] = city_data['city_id']
                                df_data.append(flat_item)
                            
                            if df_data:
                                table_name = f'{endpoint_name}_{key}'
                                tables[table_name] = pd.DataFrame(df_data)
        
        return tables
    
    def save_raw_data(self, city_data: Dict[str, Any], city_id: str):
        """Save raw JSON data"""
        if OUTPUT_CONFIG['include_raw_json']:
            filename = os.path.join(self.output_dir, 'raw_json', f'{city_id}_raw.json')
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(city_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved raw data to {filename}")
    
    def save_processed_tables(self, tables: Dict[str, pd.DataFrame], city_id: str):
        """Save processed tables in multiple formats"""
        for table_name, df in tables.items():
            if df.empty:
                continue
            
            # Save as CSV
            if 'csv' in OUTPUT_CONFIG['formats']:
                csv_path = os.path.join(self.output_dir, 'processed_csv', f'{city_id}_{table_name}.csv')
                df.to_csv(csv_path, index=False, encoding='utf-8')
                logger.info(f"Saved {table_name} CSV: {len(df)} rows")
            
            # Save as Excel
            if 'excel' in OUTPUT_CONFIG['formats']:
                excel_path = os.path.join(self.output_dir, 'processed_excel', f'{city_id}_{table_name}.xlsx')
                df.to_excel(excel_path, index=False, engine='openpyxl')
                logger.info(f"Saved {table_name} Excel: {len(df)} rows")
    
    def process_single_city(self, city_id: str, city_name: str = None) -> Dict[str, pd.DataFrame]:
        """Process a single city completely"""
        logger.info(f"Starting processing for city {city_id} ({city_name or 'Unknown'})")
        
        # Fetch all data
        city_data = self.fetch_all_city_data(city_id)
        
        # Save raw data
        self.save_raw_data(city_data, city_id)
        
        # Extract all tables
        tables = self.extract_all_tabular_data(city_data)
        
        # Save processed tables
        self.save_processed_tables(tables, city_id)
        
        logger.info(f"Completed processing for city {city_id}. Extracted {len(tables)} tables.")
        return tables
    
    def process_multiple_cities(self, cities: List[Dict[str, str]]):
        """Process multiple cities and create combined datasets"""
        all_tables = {}
        
        for city_info in cities:
            city_id = city_info['id']
            city_name = city_info.get('name', city_id)
            
            try:
                tables = self.process_single_city(city_id, city_name)
                
                # Collect tables for combination
                for table_name, df in tables.items():
                    if table_name not in all_tables:
                        all_tables[table_name] = []
                    all_tables[table_name].append(df)
                    
            except Exception as e:
                logger.error(f"Error processing city {city_id}: {e}")
                continue
        
        # Create combined datasets
        if OUTPUT_CONFIG['combine_cities']:
            self.create_combined_datasets(all_tables)
    
    def create_combined_datasets(self, all_tables: Dict[str, List[pd.DataFrame]]):
        """Combine data from multiple cities"""
        for table_name, df_list in all_tables.items():
            if not df_list:
                continue
            
            try:
                combined_df = pd.concat(df_list, ignore_index=True, sort=False)
                
                # Save combined CSV
                if 'csv' in OUTPUT_CONFIG['formats']:
                    csv_path = os.path.join(self.output_dir, 'processed_csv', f'combined_{table_name}.csv')
                    combined_df.to_csv(csv_path, index=False, encoding='utf-8')
                
                # Save combined Excel
                if 'excel' in OUTPUT_CONFIG['formats']:
                    excel_path = os.path.join(self.output_dir, 'processed_excel', f'combined_{table_name}.xlsx')
                    combined_df.to_excel(excel_path, index=False, engine='openpyxl')
                
                logger.info(f"Created combined {table_name}: {len(combined_df)} total rows")
                
            except Exception as e:
                logger.error(f"Error combining {table_name}: {e}")

def main():
    """Main execution function"""
    extractor = EnhancedMetroverseExtractor()
    
    # Process Bucharest as example
    logger.info("Processing Bucharest (city_id: 3444)")
    bucharest_tables = extractor.process_single_city("3444", "Bucharest")
    
    # Uncomment to process multiple cities
    # logger.info("Processing multiple sample cities")
    # extractor.process_multiple_cities(SAMPLE_CITIES[:3])  # Process first 3 cities

if __name__ == "__main__":
    main()
