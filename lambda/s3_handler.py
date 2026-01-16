"""
S3 Handler for storing raw economic indicator data
"""
import boto3
import json
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class S3Handler:
    """Handle S3 operations for raw data storage"""

    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def save_raw_data(self, series_id: str, data: Dict) -> str:
        """
        Save raw FRED API response to S3

        Args:
            series_id: FRED series ID
            data: Raw API response data

        Returns:
            S3 object key
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f"raw/{series_id}/{timestamp}.json"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            logger.info(f"Saved raw data to s3://{self.bucket_name}/{key}")
            return key
        except Exception as e:
            logger.error(f"Error saving to S3: {str(e)}")
            raise

    def list_raw_files(self, series_id: str = None) -> List[str]:
        """
        List raw data files in S3

        Args:
            series_id: Optional filter by series ID

        Returns:
            List of S3 object keys
        """
        prefix = f"raw/{series_id}/" if series_id else "raw/"

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logger.error(f"Error listing S3 objects: {str(e)}")
            raise

    def get_raw_data(self, key: str) -> Dict:
        """
        Retrieve raw data from S3

        Args:
            key: S3 object key

        Returns:
            Dictionary containing the raw data
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            data = json.loads(response['Body'].read())
            logger.info(f"Retrieved data from s3://{self.bucket_name}/{key}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving from S3: {str(e)}")
            raise
