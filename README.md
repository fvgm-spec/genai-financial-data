# Financial Data Pipeline and Analysis Dashboard

This project creates a comprehensive financial data pipeline and provides a Streamlit-based dashboard for data analysis and visualization. The system consists of two main components:

1. A data generation script that creates synthetic financial data
2. A Streamlit dashboard for analyzing and visualizing the generated data

## Data Generation

The data generation script (`src/datagen.py`) creates synthetic financial data with the following features:

- **Customers**: Generates customer profiles with unique IDs, personal information, risk profiles, and investment goals.
- **Assets**: Creates synthetic stock data including symbols, company names, exchange information, and key metrics like price, dividend yield, and P/E ratio.
- **Transactions**: Generates historical transaction data with realistic price variations around the current asset price.
- **Portfolios**: Creates portfolio holdings for each customer with multiple assets.

The data is organized to maintain referential integrity between different entities:

- Each transaction references valid customer_id and asset_id
- Portfolio entries link customers to their asset holdings
- All monetary values are realistic and properly rounded

## Installation

To set up the project, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/your-username/financial-data-pipeline.git
cd financial-data-pipeline
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install faker pandas streamlit plotly boto3
```

## Usage

### Generating Data

To generate synthetic financial data:

1. Set up your AWS credentials as environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_S3_BUCKET=your_s3_bucket_name
```

2. Run the data generation script:
```bash
python src/datagen.py
```

This will generate four CSV files in the `data/YYYY-MM-DD/` directory and upload them to the specified S3 bucket:

- customers_YYYY-MM-DD.csv
- assets_YYYY-MM-DD.csv
- transactions_YYYY-MM-DD.csv
- portfolios_YYYY-MM-DD.csv

You can modify the numbers in the `main()` function of `datagen.py` to generate more or fewer records as needed.

### Running the Dashboard

To run the Streamlit dashboard:

1. Ensure your AWS credentials are set up as environment variables (as described in the data generation section).

2. Run the Streamlit app:
```bash
streamlit run src/app.py
```

3. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

## Dashboard Features

The Streamlit dashboard (`src/app.py`) provides the following functionality:

1. **Data Loading**: Loads data from the specified Amazon S3 bucket, including datasets for customers, assets, transactions, and portfolios.

2. **Customer Filtering**: Allows users to filter the data by selecting specific customers in the sidebar.

3. **Key Metrics Display**: Shows total number of customers, total transactions, total portfolio value, and average portfolio value.

4. **Data Visualizations**:
   - Portfolio Value Distribution: Histogram showing the distribution of portfolio values across selected customers.
   - Asset Allocation: Pie chart displaying the distribution of assets in the portfolios.
   - Transaction History: Scatter plot of transactions over time, color-coded by transaction type.
   - Customer Risk Profile: Bar chart showing the distribution of risk tolerance among selected customers.

## AWS S3 Integration

The project uses Amazon S3 for data storage and retrieval. Here's how it's integrated:

1. **Data Generation**: The `datagen.py` script uploads generated CSV files to the specified S3 bucket using the `boto3` library.

2. **Dashboard**: The Streamlit app (`app.py`) reads data directly from the S3 bucket using `boto3`, allowing for real-time analysis of the most recent data.

To use the S3 integration:

1. Ensure you have an AWS account and have created an S3 bucket for this project.
2. Set up your AWS credentials as environment variables (as described in the Usage section).
3. The scripts will automatically use these credentials to interact with your S3 bucket.

Note: Make sure your AWS credentials have the necessary permissions to read from and write to the specified S3 bucket.