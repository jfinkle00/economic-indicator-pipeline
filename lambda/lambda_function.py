"""
Main Lambda Function for Economic Indicator ETL Pipeline
"""
import os
import logging
from datetime import datetime, timedelta
from fred_client import FREDClient
from s3_handler import S3Handler
from db_handler import DatabaseHandler

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Indicators to track
INDICATORS = ['UNRATE', 'CPIAUCSL', 'GDP', 'FEDFUNDS', 'DGS10']

def lambda_handler(event, context):
    """
    Main Lambda handler function

    This function:
    1. Fetches data from FRED API for configured indicators
    2. Saves raw data to S3
    3. Processes and loads data into RDS PostgreSQL
    4. Logs execution details
    """
    start_time = datetime.now()
    total_records = 0

    # Load configuration from environment variables
    fred_api_key = os.environ.get('FRED_API_KEY')
    s3_bucket = os.environ.get('S3_BUCKET_NAME')
    db_config = {
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'port': int(os.environ.get('DB_PORT', 5432))
    }

    # Initialize clients
    fred_client = FREDClient(fred_api_key)
    s3_handler = S3Handler(s3_bucket)
    db_handler = DatabaseHandler(db_config)

    try:
        # Connect to database
        db_handler.connect()

        # Calculate start date (fetch last 10 years of data for historical analysis)
        start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')

        # Process each indicator
        for series_id in INDICATORS:
            logger.info(f"Processing indicator: {series_id}")

            try:
                # Fetch data from FRED
                data = fred_client.get_series_data(series_id, start_date=start_date)

                # Save raw data to S3
                s3_handler.save_raw_data(series_id, data)

                # Get indicator ID from database
                indicator_id = db_handler.get_indicator_id(series_id)

                # Extract observations
                observations = data.get('observations', [])

                # Load data into database
                records_processed = db_handler.upsert_indicator_data(
                    indicator_id,
                    observations
                )

                # Update last_updated timestamp
                db_handler.update_indicator_last_updated(series_id)

                total_records += records_processed
                logger.info(f"Successfully processed {records_processed} records for {series_id}")

            except Exception as e:
                logger.error(f"Error processing {series_id}: {str(e)}")
                # Continue with next indicator
                continue

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()

        # Log successful run
        db_handler.log_etl_run('success', total_records, execution_time=execution_time)

        return {
            'statusCode': 200,
            'body': {
                'message': 'ETL pipeline executed successfully',
                'records_processed': total_records,
                'execution_time_seconds': execution_time
            }
        }

    except Exception as e:
        logger.error(f"ETL pipeline error: {str(e)}")

        # Log failed run
        execution_time = (datetime.now() - start_time).total_seconds()
        db_handler.log_etl_run(
            'failure',
            total_records,
            error_message=str(e),
            execution_time=execution_time
        )

        return {
            'statusCode': 500,
            'body': {
                'message': 'ETL pipeline failed',
                'error': str(e)
            }
        }

    finally:
        # Clean up
        db_handler.close()

# For local testing
if __name__ == "__main__":
    # Load environment variables from .env file for local testing
    from dotenv import load_dotenv
    import os
    # Load .env from parent directory
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)

    # Debug: Check environment variables
    print("=" * 60)
    print("Environment Variables Check:")
    print(f"DB_HOST: {os.environ.get('DB_HOST')}")
    print(f"S3_BUCKET_NAME: {os.environ.get('S3_BUCKET_NAME')}")
    print(f"FRED_API_KEY: {'SET' if os.environ.get('FRED_API_KEY') else 'NOT SET'}")
    print("=" * 60)

    # Mock event and context for local testing
    print("=" * 60)
    print("Running Lambda function locally...")
    print("=" * 60)
    print()

    result = lambda_handler({}, None)

    print()
    print("=" * 60)
    print("Execution Result:")
    print("=" * 60)
    print(f"Status Code: {result['statusCode']}")
    print(f"Body: {result['body']}")
