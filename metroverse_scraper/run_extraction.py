#!/usr/bin/env python3
"""
Simple runner script for Metroverse data extraction
"""

from enhanced_extractor import EnhancedMetroverseExtractor
from config import SAMPLE_CITIES
import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description='Extract data from Metroverse portal')
    parser.add_argument('--city-id', type=str, help='Single city ID to process')
    parser.add_argument('--city-name', type=str, help='City name (optional)')
    parser.add_argument('--multiple', action='store_true', help='Process multiple sample cities')
    parser.add_argument('--output-dir', type=str, default='metroverse_data', help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    extractor = EnhancedMetroverseExtractor(args.output_dir)
    
    if args.city_id:
        # Process single city
        print(f"Processing city {args.city_id} ({args.city_name or 'Unknown'})")
        tables = extractor.process_single_city(args.city_id, args.city_name)
        print(f"Extracted {len(tables)} tables for city {args.city_id}")
        
    elif args.multiple:
        # Process multiple cities
        print(f"Processing {len(SAMPLE_CITIES)} sample cities")
        extractor.process_multiple_cities(SAMPLE_CITIES)
        print("Completed processing all cities")
        
    else:
        # Default: process Bucharest
        print("Processing Bucharest (default)")
        tables = extractor.process_single_city("3444", "Bucharest")
        print(f"Extracted {len(tables)} tables for Bucharest")

if __name__ == "__main__":
    main()
