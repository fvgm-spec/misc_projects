#!/usr/bin/env python3
"""
Sample data generator for Databricks retail analytics project.
Creates CSV files that can be uploaded to DBFS for testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

def generate_orders_data(num_records=1000):
    """Generate sample orders data"""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    orders = []
    for i in range(num_records):
        order_date = datetime.now() - timedelta(days=random.randint(0, 365))
        orders.append({
            'order_id': f'ORD-{i+1:06d}',
            'customer_id': f'CUST-{random.randint(1, 200):05d}',
            'product_id': f'PROD-{random.randint(1, 50):03d}',
            'quantity': random.randint(1, 5),
            'unit_price': round(random.uniform(10.0, 500.0), 2),
            'order_date': order_date.strftime('%Y-%m-%d'),
            'order_time': order_date.strftime('%H:%M:%S'),
            'status': random.choice(['completed', 'pending', 'cancelled']),
            'payment_method': random.choice(['credit_card', 'debit_card', 'paypal', 'cash']),
            'shipping_cost': round(random.uniform(0, 25.0), 2)
        })
    
    return pd.DataFrame(orders)

def generate_customers_data(num_records=200):
    """Generate sample customers data"""
    
    np.random.seed(42)
    random.seed(42)
    
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily', 'James', 'Jessica']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    customers = []
    for i in range(1, num_records + 1):
        reg_date = datetime.now() - timedelta(days=random.randint(30, 1000))
        customers.append({
            'customer_id': f'CUST-{i:05d}',
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f'customer{i}@email.com',
            'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
            'registration_date': reg_date.strftime('%Y-%m-%d'),
            'customer_segment': random.choice(['Premium', 'Standard', 'Basic']),
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'state': random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
            'country': 'USA'
        })
    
    return pd.DataFrame(customers)

def generate_products_data(num_records=50):
    """Generate sample products data"""
    
    np.random.seed(42)
    random.seed(42)
    
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports & Outdoors']
    
    products = []
    for i in range(1, num_records + 1):
        category = random.choice(categories)
        cost_price = round(random.uniform(5.0, 200.0), 2)
        retail_price = round(cost_price * random.uniform(1.2, 3.0), 2)
        
        products.append({
            'product_id': f'PROD-{i:03d}',
            'product_name': f'{category} Product {i}',
            'category': category,
            'brand': f'Brand-{random.randint(1, 10)}',
            'cost_price': cost_price,
            'retail_price': retail_price,
            'supplier_id': f'SUP-{random.randint(1, 10):02d}',
            'weight_kg': round(random.uniform(0.1, 10.0), 2),
            'dimensions': f'{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)}',
            'in_stock': random.choice([True, False]),
            'stock_quantity': random.randint(0, 100)
        })
    
    return pd.DataFrame(products)

def generate_streaming_data(num_files=5, records_per_file=100):
    """Generate JSON files for streaming simulation"""
    
    streaming_data = []
    
    for file_num in range(num_files):
        file_data = []
        for i in range(records_per_file):
            record = {
                'event_id': f'EVT-{file_num}-{i:04d}',
                'customer_id': f'CUST-{random.randint(1, 200):05d}',
                'event_type': random.choice(['page_view', 'add_to_cart', 'purchase', 'search']),
                'product_id': f'PROD-{random.randint(1, 50):03d}',
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 1440))).isoformat(),
                'session_id': f'SESS-{random.randint(1000, 9999)}',
                'user_agent': 'Mozilla/5.0 (compatible; DataGenerator/1.0)',
                'ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}'
            }
            file_data.append(record)
        
        streaming_data.append({
            'filename': f'events_{file_num:02d}.json',
            'data': file_data
        })
    
    return streaming_data

def main():
    """Generate all sample data files"""
    
    print("Generating sample data for Databricks retail analytics project...")
    
    # Generate CSV files
    orders_df = generate_orders_data(1000)
    customers_df = generate_customers_data(200)
    products_df = generate_products_data(50)
    
    # Save CSV files
    orders_df.to_csv('orders.csv', index=False)
    customers_df.to_csv('customers.csv', index=False)
    products_df.to_csv('products.csv', index=False)
    
    print(f"✅ Generated orders.csv ({len(orders_df)} records)")
    print(f"✅ Generated customers.csv ({len(customers_df)} records)")
    print(f"✅ Generated products.csv ({len(products_df)} records)")
    
    # Generate streaming JSON files
    streaming_files = generate_streaming_data(5, 100)
    
    for file_info in streaming_files:
        with open(file_info['filename'], 'w') as f:
            for record in file_info['data']:
                f.write(json.dumps(record) + '\n')
        print(f"✅ Generated {file_info['filename']} ({len(file_info['data'])} records)")
    
    # Generate summary statistics
    print("\n📊 Data Summary:")
    print(f"Total Orders: {len(orders_df)}")
    print(f"Date Range: {orders_df['order_date'].min()} to {orders_df['order_date'].max()}")
    print(f"Total Revenue: ${orders_df['unit_price'].sum() * orders_df['quantity'].sum():,.2f}")
    print(f"Unique Customers: {orders_df['customer_id'].nunique()}")
    print(f"Unique Products: {orders_df['product_id'].nunique()}")
    print(f"Average Order Value: ${(orders_df['unit_price'] * orders_df['quantity']).mean():.2f}")
    
    print("\n🚀 Next Steps:")
    print("1. Upload these CSV files to Databricks DBFS")
    print("2. Run the data ingestion notebook")
    print("3. Execute the complete pipeline")

if __name__ == "__main__":
    main()
