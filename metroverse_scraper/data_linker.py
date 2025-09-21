#!/usr/bin/env python3
"""
Links fetched Metroverse data and generates structured tables
"""
import json
import csv
import os
import sys
from typing import Dict, List, Any

def load_json_files(directory: str = ".") -> Dict[str, Any]:
    """Load all JSON files from directory"""
    data = {}
    for file in os.listdir(directory):
        if file.endswith('.json'):
            with open(os.path.join(directory, file), 'r') as f:
                try:
                    data[file.replace('.json', '')] = json.load(f)
                except:
                    continue
    return data

def extract_city_info(data: Dict[str, Any]) -> List[Dict]:
    """Extract city metadata"""
    cities = []
    for key, content in data.items():
        if isinstance(content, dict):
            city_data = content.get('city', content)
            if 'name' in city_data or 'id' in city_data:
                cities.append({
                    'city_id': city_data.get('id', key.split('_')[0]),
                    'name': city_data.get('name', ''),
                    'country': city_data.get('country', ''),
                    'population': city_data.get('population'),
                    'gdp_per_capita': city_data.get('gdp_per_capita'),
                    'source_file': key
                })
    return cities

def extract_industries(data: Dict[str, Any]) -> List[Dict]:
    """Extract industry data"""
    industries = []
    for key, content in data.items():
        city_id = key.split('_')[0]
        if isinstance(content, dict) and 'industries' in content:
            for ind in content['industries']:
                industries.append({
                    'city_id': city_id,
                    'industry_id': ind.get('id'),
                    'name': ind.get('name'),
                    'employment': ind.get('employment'),
                    'rca': ind.get('rca'),
                    'complexity': ind.get('complexity')
                })
        elif isinstance(content, list):
            for ind in content:
                if isinstance(ind, dict) and 'name' in ind:
                    industries.append({
                        'city_id': city_id,
                        'industry_id': ind.get('id'),
                        'name': ind.get('name'),
                        'employment': ind.get('employment'),
                        'rca': ind.get('rca'),
                        'complexity': ind.get('complexity')
                    })
    return industries

def save_csv(data: List[Dict], filename: str):
    """Save data to CSV"""
    if not data:
        return
    
    keys = set()
    for row in data:
        keys.update(row.keys())
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(keys))
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Saved {filename}: {len(data)} rows")

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Load all JSON files
    data = load_json_files(directory)
    print(f"Loaded {len(data)} JSON files")
    
    # Extract structured tables
    cities = extract_city_info(data)
    industries = extract_industries(data)
    
    # Save tables
    save_csv(cities, 'cities.csv')
    save_csv(industries, 'industries.csv')
    
    print("Generated structured tables from fetched data")

if __name__ == "__main__":
    main()
