"""
Configuration file for Metroverse scraper
"""

# API endpoints and structure
METROVERSE_CONFIG = {
    'base_url': 'https://metroverse.hks.harvard.edu',
    'api_endpoints': {
        'city_profile': '/api/city/{city_id}',
        'economic_composition': '/api/city/{city_id}/economic-composition',
        'good_at': '/api/city/{city_id}/good-at',
        'industry_position': '/api/city/{city_id}/industry-position', 
        'growth_opportunities': '/api/city/{city_id}/growth-opportunities'
    },
    'rate_limit_delay': 1.5,  # seconds between requests
    'timeout': 30
}

# Sample city IDs for testing
SAMPLE_CITIES = [
    {"id": "3444", "name": "Bucharest", "country": "Romania"},
    {"id": "1840", "name": "New York", "country": "United States"},
    {"id": "2643", "name": "London", "country": "United Kingdom"},
    {"id": "1275", "name": "Tokyo", "country": "Japan"},
    {"id": "2077", "name": "Berlin", "country": "Germany"}
]

# Output configuration
OUTPUT_CONFIG = {
    'formats': ['csv', 'excel'],
    'include_raw_json': True,
    'combine_cities': True
}
