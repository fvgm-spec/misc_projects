#!/usr/bin/env python3
"""
Simple Metroverse Data Extractor
Handles the actual website structure and extracts data from the frontend
"""

import requests
import json
import pandas as pd
import os
import re
from typing import Dict, List, Any, Optional
import logging
from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMetroverseExtractor:
    def __init__(self, output_dir: str = "metroverse_data"):
        self.base_url = "https://metroverse.hks.harvard.edu"
        self.output_dir = output_dir
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'raw_data'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed'), exist_ok=True)
        
        # Session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def fetch_city_page(self, city_id: str) -> str:
        """Fetch the main city page HTML"""
        url = f"{self.base_url}/city/{city_id}/"
        
        try:
            logger.info(f"Fetching city page for {city_id}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully fetched city page")
                return response.text
            else:
                logger.error(f"Failed to fetch city page: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching city page: {e}")
            return None
    
    def extract_json_from_html(self, html_content: str) -> Dict[str, Any]:
        """Extract JSON data embedded in the HTML"""
        extracted_data = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for script tags containing JSON data
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Look for various JSON patterns
                    json_patterns = [
                        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                        r'window\.__DATA__\s*=\s*({.*?});',
                        r'var\s+cityData\s*=\s*({.*?});',
                        r'const\s+data\s*=\s*({.*?});',
                        r'"city":\s*({.*?})',
                        r'"industries":\s*(\[.*?\])',
                        r'"clusters":\s*(\[.*?\])'
                    ]
                    
                    for pattern in json_patterns:
                        matches = re.findall(pattern, script_content, re.DOTALL)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                if isinstance(data, dict) and data:
                                    extracted_data[f'pattern_{len(extracted_data)}'] = data
                            except json.JSONDecodeError:
                                continue
            
            # Also look for data attributes
            data_elements = soup.find_all(attrs={'data-city': True})
            for element in data_elements:
                try:
                    data = json.loads(element.get('data-city', '{}'))
                    if data:
                        extracted_data['data_city'] = data
                except json.JSONDecodeError:
                    continue
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting JSON from HTML: {e}")
            return {}
    
    def extract_table_data_from_html(self, html_content: str) -> Dict[str, List[Dict]]:
        """Extract tabular data from HTML tables"""
        tables_data = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all tables
            tables = soup.find_all('table')
            
            for i, table in enumerate(tables):
                table_data = []
                headers = []
                
                # Extract headers
                header_row = table.find('thead')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                # Extract data rows
                tbody = table.find('tbody') or table
                rows = tbody.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = {}
                        for j, cell in enumerate(cells):
                            header = headers[j] if j < len(headers) else f'column_{j}'
                            row_data[header] = cell.get_text(strip=True)
                        table_data.append(row_data)
                
                if table_data:
                    tables_data[f'table_{i}'] = table_data
            
            return tables_data
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return {}
    
    def extract_chart_data_from_html(self, html_content: str) -> Dict[str, Any]:
        """Extract data used for charts/visualizations"""
        chart_data = {}
        
        try:
            # Look for common chart library data patterns
            chart_patterns = [
                r'data:\s*(\[.*?\])',
                r'datasets:\s*(\[.*?\])',
                r'series:\s*(\[.*?\])',
                r'values:\s*(\[.*?\])'
            ]
            
            for i, pattern in enumerate(chart_patterns):
                matches = re.findall(pattern, html_content, re.DOTALL)
                for j, match in enumerate(matches):
                    try:
                        data = json.loads(match)
                        chart_data[f'chart_data_{i}_{j}'] = data
                    except json.JSONDecodeError:
                        continue
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error extracting chart data: {e}")
            return {}
    
    def process_city(self, city_id: str, city_name: str = None) -> Dict[str, Any]:
        """Process a single city and extract all available data"""
        logger.info(f"Processing city {city_id} ({city_name or 'Unknown'})")
        
        # Fetch the main page
        html_content = self.fetch_city_page(city_id)
        if not html_content:
            return {}
        
        # Save raw HTML
        html_file = os.path.join(self.output_dir, 'raw_data', f'{city_id}_page.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Extract different types of data
        extracted_data = {
            'city_id': city_id,
            'city_name': city_name,
            'json_data': self.extract_json_from_html(html_content),
            'table_data': self.extract_table_data_from_html(html_content),
            'chart_data': self.extract_chart_data_from_html(html_content)
        }
        
        # Save extracted data
        json_file = os.path.join(self.output_dir, 'raw_data', f'{city_id}_extracted.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        # Convert to DataFrames and save
        self.save_as_dataframes(extracted_data, city_id)
        
        return extracted_data
    
    def save_as_dataframes(self, data: Dict[str, Any], city_id: str):
        """Convert extracted data to DataFrames and save"""
        
        # Process JSON data
        if data.get('json_data'):
            for key, json_obj in data['json_data'].items():
                try:
                    df = self.json_to_dataframe(json_obj, city_id)
                    if not df.empty:
                        csv_path = os.path.join(self.output_dir, 'processed', f'{city_id}_{key}.csv')
                        df.to_csv(csv_path, index=False, encoding='utf-8')
                        logger.info(f"Saved {key}: {len(df)} rows")
                except Exception as e:
                    logger.error(f"Error processing {key}: {e}")
        
        # Process table data
        if data.get('table_data'):
            for key, table_list in data['table_data'].items():
                try:
                    df = pd.DataFrame(table_list)
                    if not df.empty:
                        df['city_id'] = city_id
                        csv_path = os.path.join(self.output_dir, 'processed', f'{city_id}_{key}.csv')
                        df.to_csv(csv_path, index=False, encoding='utf-8')
                        logger.info(f"Saved {key}: {len(df)} rows")
                except Exception as e:
                    logger.error(f"Error processing table {key}: {e}")
        
        # Process chart data
        if data.get('chart_data'):
            for key, chart_obj in data['chart_data'].items():
                try:
                    df = self.json_to_dataframe(chart_obj, city_id)
                    if not df.empty:
                        csv_path = os.path.join(self.output_dir, 'processed', f'{city_id}_{key}.csv')
                        df.to_csv(csv_path, index=False, encoding='utf-8')
                        logger.info(f"Saved {key}: {len(df)} rows")
                except Exception as e:
                    logger.error(f"Error processing chart {key}: {e}")
    
    def json_to_dataframe(self, json_obj: Any, city_id: str) -> pd.DataFrame:
        """Convert JSON object to DataFrame"""
        try:
            if isinstance(json_obj, list):
                if all(isinstance(item, dict) for item in json_obj):
                    df = pd.DataFrame(json_obj)
                    df['city_id'] = city_id
                    return df
                else:
                    # Convert list of values to DataFrame
                    df = pd.DataFrame({'value': json_obj})
                    df['city_id'] = city_id
                    return df
            
            elif isinstance(json_obj, dict):
                # Flatten nested dictionary
                flattened = self.flatten_dict(json_obj)
                df = pd.DataFrame([flattened])
                df['city_id'] = city_id
                return df
            
            else:
                # Single value
                df = pd.DataFrame({'value': [json_obj]})
                df['city_id'] = city_id
                return df
                
        except Exception as e:
            logger.error(f"Error converting JSON to DataFrame: {e}")
            return pd.DataFrame()
    
    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                # Handle list of dicts by taking first item or creating summary
                items.append((f"{new_key}_count", len(v)))
                if v:
                    items.extend(self.flatten_dict(v[0], f"{new_key}_first", sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

def main():
    """Test the extractor"""
    extractor = SimpleMetroverseExtractor()
    
    # Test with Bucharest
    result = extractor.process_city("3444", "Bucharest")
    
    print(f"Extraction completed. Found:")
    print(f"- JSON data sections: {len(result.get('json_data', {}))}")
    print(f"- Table data sections: {len(result.get('table_data', {}))}")
    print(f"- Chart data sections: {len(result.get('chart_data', {}))}")

if __name__ == "__main__":
    main()
