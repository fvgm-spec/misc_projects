#!/usr/bin/env python3
"""
Process extracted Metroverse data into structured tables
"""
import json
import csv
import os
import sys
from typing import Dict, List, Any

def load_json_files(directory: str = "metroverse_data/raw_json") -> Dict[str, Any]:
    """Load all JSON files from directory"""
    data = {}
    if not os.path.exists(directory):
        return data
        
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
        if isinstance(content, dict) and 'network_responses' in content:
            city_id = content.get('city_id', key.split('_')[0])
            # Extract from GraphQL responses
            for response in content['network_responses']:
                if 'graphql' in response.get('url', ''):
                    response_data = response.get('data', {}).get('data', {})
                    if 'city' in response_data:
                        city = response_data['city']
                        cities.append({
                            'city_id': city_id,
                            'name': city.get('name', ''),
                            'country': city.get('country', ''),
                            'population': city.get('population'),
                            'gdp_per_capita': city.get('gdpPerCapita'),
                            'source_file': key
                        })
    return cities

def save_csv(data: List[Dict], filename: str):
    """Save data to CSV"""
    if not data:
        return
    
    keys = set()
    for row in data:
        keys.update(row.keys())
    
    os.makedirs('metroverse_data/csv_tables', exist_ok=True)
    filepath = os.path.join('metroverse_data/csv_tables', filename)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(keys))
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Saved {filepath}: {len(data)} rows")

def main():
    # Load all JSON files
    data = load_json_files()
    print(f"Loaded {len(data)} JSON files")
    
    # Extract structured tables
    cities = extract_city_info(data)
    
    # Save tables
    save_csv(cities, 'cities.csv')
    
    print("Generated structured tables from fetched data")

if __name__ == "__main__":
    main()
