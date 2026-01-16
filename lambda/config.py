"""
Configuration settings for the Economic Indicator ETL Pipeline
"""
import os

# FRED API Configuration
FRED_API_KEY = os.environ.get('FRED_API_KEY')
FRED_BASE_URL = "https://api.stlouisfed.org/fred"

# AWS Configuration
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Database Configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME', 'economic_indicators'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': int(os.environ.get('DB_PORT', 5432))
}

# Economic Indicators to Track
INDICATORS = ['UNRATE', 'CPIAUCSL', 'GDP', 'FEDFUNDS', 'DGS10']

# ETL Configuration
LOOKBACK_DAYS = 30  # Number of days of historical data to fetch
