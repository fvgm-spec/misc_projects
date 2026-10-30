# Fix for the random.uniform error in Databricks

# Make sure you have the import at the top
import random
from datetime import datetime, timedelta

# Fixed sample data generation
sample_data = []
for i in range(1000):
    sample_data.append({
        'order_id': f'ORD-{i+1:06d}',
        'customer_id': f'CUST-{random.randint(1, 200):05d}',
        'product_id': f'PROD-{random.randint(1, 50):03d}',
        'quantity': random.randint(1, 5),
        'unit_price': round(random.uniform(10.0, 500.0), 2),  # This line was causing the error
        'order_date': (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
        'status': random.choice(['completed', 'pending', 'cancelled'])
    })

print(f"✅ Generated {len(sample_data)} sample records")
