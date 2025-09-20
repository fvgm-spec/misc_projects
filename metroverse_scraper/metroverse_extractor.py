#!/usr/bin/env python3
"""
Metroverse Data Extractor
Fetches and processes data from Harvard Growth Lab's Metroverse portal
"""

import requests
import json
import pandas as pd
import os
from typing import Dict, List, Any, Optional
import logging
from urllib.parse import urljoin
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetroverseExtractor:
    def __init__(self, output_dir: str = "output"):
        self.base_url = "https://metroverse.hks.harvard.edu"
        self.api_base = "https://metroverse.hks.harvard.edu/api"
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def fetch_city_data(self, city_id: str) -> Dict[str, Any]:
        """Fetch all city profile data sections"""
        sections = [
            'economic-composition',
            'good-at', 
            'industry-position',
            'growth-opportunities'
        ]
        
        city_data = {'city_id': city_id, 'sections': {}}
        
        for section in sections:
            url = f"{self.api_base}/city/{city_id}/{section}"
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    city_data['sections'][section] = response.json()
                    logger.info(f"Fetched {section} data for city {city_id}")
                else:
                    logger.warning(f"Failed to fetch {section}: {response.status_code}")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching {section}: {e}")
        
        return city_data
    
    def extract_city_metadata(self, city_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract basic city information"""
        metadata = []
        
        # Try to get city info from any available section
        for section_name, section_data in city_data['sections'].items():
            if isinstance(section_data, dict) and 'city' in section_data:
                city_info = section_data['city']
                metadata.append({
                    'city_id': city_data['city_id'],
                    'city_name': city_info.get('name', ''),
                    'country': city_info.get('country', ''),
                    'population': city_info.get('population'),
                    'gdp_per_capita': city_info.get('gdp_per_capita'),
                    'section_source': section_name
                })
                break
        
        return pd.DataFrame(metadata)
    
    def extract_industries_data(self, city_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract industries and employment data"""
        industries = []
        
        for section_name, section_data in city_data['sections'].items():
            if isinstance(section_data, dict) and 'industries' in section_data:
                for industry in section_data['industries']:
                    industries.append({
                        'city_id': city_data['city_id'],
                        'section': section_name,
                        'industry_id': industry.get('id'),
                        'industry_name': industry.get('name'),
                        'employment': industry.get('employment'),
                        'rca': industry.get('rca'),
                        'complexity': industry.get('complexity'),
                        'opportunity_gain': industry.get('opportunity_gain'),
                        'distance': industry.get('distance')
                    })
        
        return pd.DataFrame(industries)
    
    def extract_clusters_data(self, city_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract cluster employment data"""
        clusters = []
        
        for section_name, section_data in city_data['sections'].items():
            if isinstance(section_data, dict) and 'clusters' in section_data:
                for cluster in section_data['clusters']:
                    clusters.append({
                        'city_id': city_data['city_id'],
                        'section': section_name,
                        'cluster_id': cluster.get('id'),
                        'cluster_name': cluster.get('name'),
                        'employment': cluster.get('employment'),
                        'rca': cluster.get('rca'),
                        'complexity': cluster.get('complexity'),
                        'opportunity_gain': cluster.get('opportunity_gain')
                    })
        
        return pd.DataFrame(clusters)
    
    def extract_economic_composition(self, city_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Extract economic composition specific data"""
        tables = {}
        
        if 'economic-composition' in city_data['sections']:
            data = city_data['sections']['economic-composition']
            
            # Employment by industry
            if 'employment_by_industry' in data:
                emp_data = []
                for item in data['employment_by_industry']:
                    emp_data.append({
                        'city_id': city_data['city_id'],
                        'industry_id': item.get('industry_id'),
                        'industry_name': item.get('industry_name'),
                        'employment': item.get('employment'),
                        'share': item.get('share')
                    })
                tables['employment_by_industry'] = pd.DataFrame(emp_data)
            
            # Complexity data
            if 'complexity_data' in data:
                comp_data = []
                for item in data['complexity_data']:
                    comp_data.append({
                        'city_id': city_data['city_id'],
                        'year': item.get('year'),
                        'complexity': item.get('complexity'),
                        'rank': item.get('rank')
                    })
                tables['complexity_timeline'] = pd.DataFrame(comp_data)
        
        return tables
    
    def extract_growth_opportunities(self, city_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract growth opportunities data"""
        opportunities = []
        
        if 'growth-opportunities' in city_data['sections']:
            data = city_data['sections']['growth-opportunities']
            
            if 'opportunities' in data:
                for opp in data['opportunities']:
                    opportunities.append({
                        'city_id': city_data['city_id'],
                        'industry_id': opp.get('industry_id'),
                        'industry_name': opp.get('industry_name'),
                        'opportunity_gain': opp.get('opportunity_gain'),
                        'distance': opp.get('distance'),
                        'complexity': opp.get('complexity'),
                        'rca': opp.get('rca')
                    })
        
        return pd.DataFrame(opportunities)
    
    def process_city(self, city_id: str, city_name: str = None) -> Dict[str, pd.DataFrame]:
        """Process a single city and return all extracted tables"""
        logger.info(f"Processing city {city_id} ({city_name or 'Unknown'})")
        
        # Fetch raw data
        city_data = self.fetch_city_data(city_id)
        
        # Extract all tables
        tables = {}
        
        # Basic metadata
        tables['city_metadata'] = self.extract_city_metadata(city_data)
        
        # Industries data
        tables['industries'] = self.extract_industries_data(city_data)
        
        # Clusters data  
        tables['clusters'] = self.extract_clusters_data(city_data)
        
        # Economic composition tables
        econ_tables = self.extract_economic_composition(city_data)
        tables.update(econ_tables)
        
        # Growth opportunities
        tables['growth_opportunities'] = self.extract_growth_opportunities(city_data)
        
        # Save raw JSON for reference
        raw_file = os.path.join(self.output_dir, f"raw_data_{city_id}.json")
        with open(raw_file, 'w') as f:
            json.dump(city_data, f, indent=2)
        
        return tables
    
    def save_tables(self, tables: Dict[str, pd.DataFrame], city_id: str, format: str = 'csv'):
        """Save extracted tables to files"""
        for table_name, df in tables.items():
            if not df.empty:
                if format == 'csv':
                    filename = os.path.join(self.output_dir, f"{city_id}_{table_name}.csv")
                    df.to_csv(filename, index=False)
                elif format == 'excel':
                    filename = os.path.join(self.output_dir, f"{city_id}_{table_name}.xlsx")
                    df.to_excel(filename, index=False)
                
                logger.info(f"Saved {table_name}: {len(df)} rows to {filename}")
    
    def process_multiple_cities(self, city_list: List[Dict[str, str]], format: str = 'csv'):
        """Process multiple cities"""
        all_tables = {}
        
        for city_info in city_list:
            city_id = city_info['id']
            city_name = city_info.get('name', city_id)
            
            try:
                tables = self.process_city(city_id, city_name)
                self.save_tables(tables, city_id, format)
                
                # Combine tables across cities
                for table_name, df in tables.items():
                    if table_name not in all_tables:
                        all_tables[table_name] = []
                    all_tables[table_name].append(df)
                
            except Exception as e:
                logger.error(f"Error processing city {city_id}: {e}")
        
        # Save combined tables
        for table_name, df_list in all_tables.items():
            if df_list:
                combined_df = pd.concat(df_list, ignore_index=True)
                if format == 'csv':
                    filename = os.path.join(self.output_dir, f"combined_{table_name}.csv")
                    combined_df.to_csv(filename, index=False)
                elif format == 'excel':
                    filename = os.path.join(self.output_dir, f"combined_{table_name}.xlsx")
                    combined_df.to_excel(filename, index=False)
                
                logger.info(f"Saved combined {table_name}: {len(combined_df)} rows")

def main():
    """Example usage"""
    extractor = MetroverseExtractor("output")
    
    # Example: Process Bucharest (city_id: 3444)
    bucharest_tables = extractor.process_city("3444", "Bucharest")
    extractor.save_tables(bucharest_tables, "3444", format='csv')
    
    # Example: Process multiple cities
    cities = [
        {"id": "3444", "name": "Bucharest"},
        {"id": "1234", "name": "Another City"}  # Replace with actual city IDs
    ]
    # extractor.process_multiple_cities(cities, format='csv')

if __name__ == "__main__":
    main()
