import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import boto3
import io

# Set page config
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_layout="wide",
    initial_sidebar_state="expanded"
)

# Add title and description
st.title("Data Analysis Dashboard")
st.markdown("### Analysis and Visualization of Data from Buckets")

# Function to load data from S3
@st.cache_data
def load_data(bucket_name):
    s3 = boto3.client('s3')
    dfs = {}
    
    # Load all datasets
    for file_name in ['customers.csv', 'assets.csv', 'transactions.csv', 'portfolios.csv']:
        try:
            response = s3.get_object(Bucket=bucket_name, Key=file_name)
            dfs[file_name.replace('.csv', '')] = pd.read_csv(io.BytesIO(response['Body'].read()))
        except Exception as e:
            st.error(f"Error loading {file_name}: {str(e)}")
    
    return dfs

# Input for S3 bucket name
bucket_name = st.sidebar.text_input("Enter S3 Bucket Name", "financial-data-bucket")

# Load the data
try:
    dfs = load_data(bucket_name)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Customer filter
    selected_customers = st.sidebar.multiselect(
        "Select Customers",
        options=dfs['customers']['customer_id'].unique(),
        default=dfs['customers']['customer_id'].unique()[:5]
    )
    
    # Filter data based on selection
    filtered_transactions = dfs['transactions'][
        dfs['transactions']['customer_id'].isin(selected_customers)
    ]
    filtered_portfolios = dfs['portfolios'][
        dfs['portfolios']['customer_id'].isin(selected_customers)
    ]
    
    # Data Overview
    st.header("Portfolio Analysis Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(selected_customers)
        st.metric("Total Customers", total_customers)
    
    with col2:
        total_transactions = len(filtered_transactions)
        st.metric("Total Transactions", total_transactions)
    
    with col3:
        total_portfolio_value = filtered_portfolios['total_value'].sum()
        st.metric("Total Portfolio Value", f"${total_portfolio_value:,.2f}")
    
    with col4:
        avg_portfolio_value = total_portfolio_value / total_customers
        st.metric("Avg Portfolio Value", f"${avg_portfolio_value:,.2f}")
    
    # Create visualization columns
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Portfolio Value Distribution")
        fig1 = px.histogram(
            filtered_portfolios,
            x="total_value",
            nbins=30,
            title="Distribution of Portfolio Values"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        st.subheader("Asset Allocation")
        asset_allocation = filtered_portfolios.groupby('asset_type')['value'].sum()
        fig2 = px.pie(
            values=asset_allocation.values,
            names=asset_allocation.index,
            title="Asset Allocation Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with chart_col2:
        st.subheader("Transaction History")
        fig3 = px.scatter(
            filtered_transactions,
            x="transaction_date",
            y="amount",
            color="transaction_type",
            title="Transaction History Over Time"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        st.subheader("Customer Risk Profile")
        risk_distribution = dfs['customers'][
            dfs['customers']['customer_id'].isin(selected_customers)
        ]['risk_tolerance'].value_counts()
        fig4 = px.bar(
            x=risk_distribution.index,
            y=risk_distribution.values,
            title="Risk Tolerance Distribution"
        )
        st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.write("Please make sure your data source is correctly configured.")