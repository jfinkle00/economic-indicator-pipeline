"""
FRED API Client for fetching economic indicator data
"""
import requests
from typing import Dict, List
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class FREDClient:
    """Client for interacting with FRED API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"

    def get_series_data(self, series_id: str, start_date: str = None) -> Dict:
        """
        Fetch time series data for a given indicator

        Args:
            series_id: FRED series ID (e.g., 'UNRATE')
            start_date: Optional start date in YYYY-MM-DD format

        Returns:
            Dictionary containing series observations
        """
        endpoint = f"{self.base_url}/series/observations"

        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }

        if start_date:
            params['observation_start'] = start_date

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            logger.info(f"Successfully fetched data for {series_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {series_id}: {str(e)}")
            raise

    def get_series_info(self, series_id: str) -> Dict:
        """
        Fetch metadata about a series

        Args:
            series_id: FRED series ID

        Returns:
            Dictionary containing series metadata
        """
        endpoint = f"{self.base_url}/series"

        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            logger.info(f"Successfully fetched metadata for {series_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching metadata for {series_id}: {str(e)}")
            raise
