# Fix for Databricks random import error

# Add this at the very top of your notebook cell
import random
from datetime import datetime, timedelta
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# Fixed sample data generation
sample_data = []
for i in range(1000):
    sample_data.append({
        'order_id': f'ORD-{i+1:06d}',
        'customer_id': f'CUST-{random.randint(1, 200):05d}',
        'product_id': f'PROD-{random.randint(1, 50):03d}',
        'quantity': random.randint(1, 5),
        'unit_price': round(random.uniform(10.0, 500.0), 2),  # This line was failing
        'order_date': (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
        'status': random.choice(['completed', 'pending', 'cancelled'])
    })

print(f"✅ Generated {len(sample_data)} sample records")

# Define schema
schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("order_date", StringType(), True),
    StructField("status", StringType(), True)
])

# Create DataFrame
df_orders = spark.createDataFrame(sample_data, schema)
display(df_orders.limit(10))
