#!/usr/bin/env python3
"""
Basic Metroverse Data Extractor
Works without pandas to avoid numpy compatibility issues
"""

import requests
import json
import csv
import os
import re
from typing import Dict, List, Any, Optional
import logging
from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasicMetroverseExtractor:
    def __init__(self, output_dir: str = "metroverse_data"):
        self.base_url = "https://metroverse.hks.harvard.edu"
        self.output_dir = output_dir
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'raw_html'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'extracted_json'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'csv_tables'), exist_ok=True)
        
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
            logger.info(f"Fetching city page for {city_id}: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully fetched city page ({len(response.text)} characters)")
                return response.text
            else:
                logger.error(f"Failed to fetch city page: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching city page: {e}")
            return None
    
    def extract_json_from_scripts(self, html_content: str) -> Dict[str, Any]:
        """Extract JSON data from script tags"""
        extracted_data = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            script_tags = soup.find_all('script')
            
            logger.info(f"Found {len(script_tags)} script tags")
            
            for i, script in enumerate(script_tags):
                if script.string:
                    script_content = script.string.strip()
                    
                    # Skip empty or very short scripts
                    if len(script_content) < 50:
                        continue
                    
                    # Look for JSON-like patterns
                    json_patterns = [
                        (r'window\.__INITIAL_STATE__\s*=\s*({.*?});', 'initial_state'),
                        (r'window\.__DATA__\s*=\s*({.*?});', 'window_data'),
                        (r'var\s+cityData\s*=\s*({.*?});', 'city_data'),
                        (r'const\s+data\s*=\s*({.*?});', 'const_data'),
                        (r'"city":\s*({[^}]*"name"[^}]*})', 'city_info'),
                        (r'"industries":\s*(\[[^\]]*\])', 'industries'),
                        (r'"clusters":\s*(\[[^\]]*\])', 'clusters'),
                        (r'"employment":\s*(\[[^\]]*\])', 'employment'),
                        (r'data:\s*(\{[^}]*"labels"[^}]*\})', 'chart_data')
                    ]
                    
                    for pattern, name in json_patterns:
                        matches = re.findall(pattern, script_content, re.DOTALL)
                        for j, match in enumerate(matches):
                            try:
                                # Clean up the JSON string
                                clean_match = match.strip()
                                if clean_match.endswith(','):
                                    clean_match = clean_match[:-1]
                                
                                data = json.loads(clean_match)
                                if data:  # Only save non-empty data
                                    key = f"{name}_{j}" if j > 0 else name
                                    extracted_data[key] = data
                                    logger.info(f"Extracted {name} data (script {i})")
                            except json.JSONDecodeError as e:
                                logger.debug(f"JSON decode error for {name}: {e}")
                                continue
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting JSON from scripts: {e}")
            return {}
    
    def extract_tables_from_html(self, html_content: str) -> Dict[str, List[Dict]]:
        """Extract data from HTML tables"""
        tables_data = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tables = soup.find_all('table')
            
            logger.info(f"Found {len(tables)} HTML tables")
            
            for i, table in enumerate(tables):
                table_data = []
                headers = []
                
                # Extract headers
                header_row = table.find('thead')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                elif table.find('tr'):
                    # Use first row as headers if no thead
                    first_row = table.find('tr')
                    headers = [cell.get_text(strip=True) for cell in first_row.find_all(['th', 'td'])]
                
                # Extract data rows
                tbody = table.find('tbody') or table
                rows = tbody.find_all('tr')
                
                # Skip header row if we used first row as headers
                start_idx = 1 if not table.find('thead') and headers else 0
                
                for row in rows[start_idx:]:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = {}
                        for j, cell in enumerate(cells):
                            header = headers[j] if j < len(headers) else f'column_{j}'
                            row_data[header] = cell.get_text(strip=True)
                        if any(row_data.values()):  # Only add non-empty rows
                            table_data.append(row_data)
                
                if table_data:
                    tables_data[f'table_{i}'] = table_data
                    logger.info(f"Extracted table_{i} with {len(table_data)} rows")
            
            return tables_data
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return {}
    
    def save_to_csv(self, data: List[Dict], filename: str, city_id: str):
        """Save list of dictionaries to CSV"""
        if not data:
            return
        
        try:
            # Add city_id to each row
            for row in data:
                row['city_id'] = city_id
            
            # Get all unique keys for headers
            all_keys = set()
            for row in data:
                all_keys.update(row.keys())
            
            fieldnames = ['city_id'] + [key for key in sorted(all_keys) if key != 'city_id']
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Saved CSV: {filename} ({len(data)} rows)")
            
        except Exception as e:
            logger.error(f"Error saving CSV {filename}: {e}")
    
    def flatten_json_to_rows(self, json_obj: Any, prefix: str = '') -> List[Dict]:
        """Convert JSON object to list of flat dictionaries"""
        rows = []
        
        try:
            if isinstance(json_obj, list):
                for i, item in enumerate(json_obj):
                    if isinstance(item, dict):
                        flat_item = self.flatten_dict(item, prefix)
                        rows.append(flat_item)
                    else:
                        rows.append({f'{prefix}value_{i}': item})
            
            elif isinstance(json_obj, dict):
                flat_dict = self.flatten_dict(json_obj, prefix)
                rows.append(flat_dict)
            
            else:
                rows.append({f'{prefix}value': json_obj})
            
            return rows
            
        except Exception as e:
            logger.error(f"Error flattening JSON: {e}")
            return []
    
    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if len(v) > 0 and isinstance(v[0], dict):
                    # For list of dicts, just take the count and first item
                    items.append((f"{new_key}_count", len(v)))
                    if v:
                        items.extend(self.flatten_dict(v[0], f"{new_key}_first", sep=sep).items())
                else:
                    # For simple lists, join as string
                    items.append((new_key, ', '.join(map(str, v))))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def process_city(self, city_id: str, city_name: str = None) -> Dict[str, Any]:
        """Process a single city and extract all available data"""
        logger.info(f"Processing city {city_id} ({city_name or 'Unknown'})")
        
        # Fetch the main page
        html_content = self.fetch_city_page(city_id)
        if not html_content:
            logger.error(f"Could not fetch HTML for city {city_id}")
            return {}
        
        # Save raw HTML
        html_file = os.path.join(self.output_dir, 'raw_html', f'{city_id}_page.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Saved raw HTML to {html_file}")
        
        # Extract JSON data from scripts
        json_data = self.extract_json_from_scripts(html_content)
        
        # Extract table data
        table_data = self.extract_tables_from_html(html_content)
        
        # Save extracted JSON data
        if json_data:
            json_file = os.path.join(self.output_dir, 'extracted_json', f'{city_id}_data.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved extracted JSON to {json_file}")
        
        # Convert JSON data to CSV tables
        for key, data in json_data.items():
            rows = self.flatten_json_to_rows(data)
            if rows:
                csv_file = os.path.join(self.output_dir, 'csv_tables', f'{city_id}_{key}.csv')
                self.save_to_csv(rows, csv_file, city_id)
        
        # Save table data as CSV
        for key, data in table_data.items():
            if data:
                csv_file = os.path.join(self.output_dir, 'csv_tables', f'{city_id}_{key}.csv')
                self.save_to_csv(data, csv_file, city_id)
        
        result = {
            'city_id': city_id,
            'city_name': city_name,
            'json_sections': len(json_data),
            'table_sections': len(table_data),
            'json_data': json_data,
            'table_data': table_data
        }
        
        logger.info(f"Completed processing city {city_id}")
        logger.info(f"Found {len(json_data)} JSON sections and {len(table_data)} HTML tables")
        
        return result

def main():
    """Test the extractor"""
    extractor = BasicMetroverseExtractor()
    
    # Test with Bucharest
    result = extractor.process_city("3444", "Bucharest")
    
    print(f"\nExtraction Results for Bucharest:")
    print(f"- JSON data sections: {result.get('json_sections', 0)}")
    print(f"- HTML table sections: {result.get('table_sections', 0)}")
    
    if result.get('json_data'):
        print(f"\nJSON sections found:")
        for key in result['json_data'].keys():
            print(f"  - {key}")
    
    if result.get('table_data'):
        print(f"\nHTML tables found:")
        for key, data in result['table_data'].items():
            print(f"  - {key}: {len(data)} rows")

if __name__ == "__main__":
    main()
