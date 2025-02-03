import boto3
from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
import uuid
import os

# Initialize Faker
fake = Faker()

class FinancialDataGenerator:
    def __init__(self, min_customers=1000, max_customers=5000, min_assets=100, max_assets=500, min_transactions=10000, max_transactions=50000):
        self.min_customers = min_customers
        self.max_customers = max_customers
        self.min_assets = min_assets
        self.max_assets = max_assets
        self.min_transactions = min_transactions
        self.max_transactions = max_transactions
        self.fake = Faker()
        # List of major stock exchanges
        self.exchanges = ['NYSE', 'NASDAQ', 'LSE', 'TSE']
        # List of sectors for diversification
        self.sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 
                       'Consumer Goods', 'Industrial', 'Utilities']

    def generate_customers(self, num_customers):
        customers = []
        for _ in range(num_customers):
            customer = {
                'customer_id': str(uuid.uuid4()),
                'name': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'address': fake.address(),
                'registration_date': fake.date_between(start_date='-3y'),
                'risk_profile': random.choice(['Conservative', 'Moderate', 'Aggressive']),
                'annual_income': round(random.uniform(50000, 500000), 2),
                'investment_goal': random.choice(['Retirement', 'Growth', 'Income', 'Preservation'])
            }
            customers.append(customer)
        return pd.DataFrame(customers)

    def generate_assets(self, num_assets):
        assets = []
        for _ in range(num_assets):
            asset = {
                'asset_id': str(uuid.uuid4()),
                'symbol': fake.unique.lexify(text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                'company_name': fake.company(),
                'exchange': random.choice(self.exchanges),
                'sector': random.choice(self.sectors),
                'current_price': round(random.uniform(10, 1000), 2),
                'dividend_yield': round(random.uniform(0, 0.05), 3),
                'pe_ratio': round(random.uniform(5, 50), 2),
                'market_cap': round(random.uniform(1e6, 1e12), 2),
                'last_updated': fake.date_time_this_month()
            }
            assets.append(asset)
        return pd.DataFrame(assets)

    def generate_transactions(self, customers_df, assets_df, num_transactions):
        transactions = []
        customer_ids = customers_df['customer_id'].tolist()
        asset_ids = assets_df['asset_id'].tolist()
        
        for _ in range(num_transactions):
            transaction_date = fake.date_time_between(start_date='-1y')
            asset_id = random.choice(asset_ids)
            asset_price = float(assets_df[assets_df['asset_id'] == asset_id]['current_price'].iloc[0])
            
            transaction = {
                'transaction_id': str(uuid.uuid4()),
                'customer_id': random.choice(customer_ids),
                'asset_id': asset_id,
                'transaction_type': random.choice(['BUY', 'SELL']),
                'quantity': random.randint(1, 1000),
                'price_per_unit': round(asset_price * random.uniform(0.95, 1.05), 2),
                'transaction_date': transaction_date,
                'status': random.choice(['COMPLETED', 'PENDING', 'CANCELLED']),
                'fee': round(random.uniform(1, 50), 2)
            }
            transactions.append(transaction)
        return pd.DataFrame(transactions)

    def generate_portfolios(self, customers_df, assets_df):
        portfolios = []
        customer_ids = customers_df['customer_id'].tolist()
        asset_ids = assets_df['asset_id'].tolist()
        
        for customer_id in customer_ids:
            # Generate 3-10 random assets for each customer's portfolio
            num_assets = random.randint(3, 10)
            selected_assets = random.sample(asset_ids, num_assets)
            
            for asset_id in selected_assets:
                portfolio = {
                    'portfolio_id': str(uuid.uuid4()),
                    'customer_id': customer_id,
                    'asset_id': asset_id,
                    'shares_owned': random.randint(10, 1000),
                    'purchase_price_avg': round(random.uniform(10, 1000), 2),
                    'last_updated': fake.date_time_this_month()
                }
                portfolios.append(portfolio)
        return pd.DataFrame(portfolios)

def upload_to_s3(file_path, bucket_name, s3_path, region_name):
    """Upload a file to S3 bucket"""
    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )
    try:
        s3_client.upload_file(file_path, bucket_name, s3_path)
        print(f"Successfully uploaded {file_path} to {bucket_name}/{s3_path}")
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")

def main():
    import yaml
    
    # Load configuration
    with open('config/data_generation.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize the generator
    generator = FinancialDataGenerator()
    
    # Set up output directory and file naming
    timestamp = datetime.now().strftime(config['s3']['storage']['date_format'])
    output_dir = os.path.join(config['s3']['storage']['local_output_dir'], timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the data using configuration
    # Generate random numbers within specified ranges
    import random
    num_customers = random.randint(generator.min_customers, generator.max_customers)
    num_assets = random.randint(generator.min_assets, generator.max_assets)
    num_transactions = random.randint(generator.min_transactions, generator.max_transactions)

    # Generate data with random counts
    customers = generator.generate_customers(num_customers=num_customers)
    assets = generator.generate_assets(num_assets=num_assets)
    transactions = generator.generate_transactions(customers, assets, num_transactions=num_transactions)
    portfolios = generator.generate_portfolios(customers, assets)
    
    # Define file paths using configuration pattern
    s3_config = config['s3']
    file_pattern = s3_config['storage']['file_pattern']
    bucket_name = os.environ.get(s3_config['bucket_name'].replace('${', '').replace('}', ''))
    
    data_frames = {
        'customers': customers,
        'assets': assets,
        'transactions': transactions,
        'portfolios': portfolios
    }
    
    for name, df in data_frames.items():
        # Generate local file path
        local_filename = file_pattern.replace('${name}', name).replace('${timestamp}', timestamp)
        file_path = os.path.join(output_dir, local_filename)
        
        # Save locally
        df.to_csv(file_path, index=False)
        print(f"Saved {file_path} locally")
        
        # Upload to S3 using configured paths
        s3_path = os.path.join(s3_config['paths'][name], local_filename)
        region = os.environ.get(s3_config['region'].replace('${', '').replace('}', ''))
        upload_to_s3(file_path, bucket_name, s3_path, region)
    
    print("Data generation and upload completed successfully!")
    print(f"Generated {len(customers)} customers")
    print(f"Generated {len(assets)} assets")
    print(f"Generated {len(transactions)} transactions")
    print(f"Generated {len(portfolios)} portfolio entries")

if __name__ == "__main__":
    main()
