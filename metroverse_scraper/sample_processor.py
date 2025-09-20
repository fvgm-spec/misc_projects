#!/usr/bin/env python3
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
