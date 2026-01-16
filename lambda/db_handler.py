"""
Database Handler for PostgreSQL operations
"""
import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict, Tuple
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DatabaseHandler:
    """Handle PostgreSQL database operations"""

    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config.get('port', 5432)
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def get_indicator_id(self, series_id: str) -> int:
        """
        Get indicator_id for a given series_id

        Args:
            series_id: FRED series ID

        Returns:
            indicator_id from database
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT indicator_id FROM indicators WHERE series_id = %s",
                (series_id,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                raise ValueError(f"Indicator {series_id} not found in database")
        finally:
            cursor.close()

    def upsert_indicator_data(self, indicator_id: int, observations: List[Dict]) -> int:
        """
        Insert or update indicator data

        Args:
            indicator_id: ID from indicators table
            observations: List of observation dictionaries with 'date' and 'value'

        Returns:
            Number of records processed
        """
        cursor = self.conn.cursor()

        # Prepare data for batch insert
        data = [
            (indicator_id, obs['date'], float(obs['value']) if obs['value'] != '.' else None)
            for obs in observations
            if obs['value'] != '.'  # FRED uses '.' for missing values
        ]

        try:
            # Use INSERT ... ON CONFLICT to handle duplicates
            execute_batch(cursor, """
                INSERT INTO indicator_data (indicator_id, observation_date, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (indicator_id, observation_date)
                DO UPDATE SET value = EXCLUDED.value
            """, data)

            self.conn.commit()
            logger.info(f"Processed {len(data)} records for indicator_id {indicator_id}")
            return len(data)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting data: {str(e)}")
            raise
        finally:
            cursor.close()

    def update_indicator_last_updated(self, series_id: str):
        """
        Update the last_updated timestamp for an indicator

        Args:
            series_id: FRED series ID
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE indicators
                SET last_updated = CURRENT_TIMESTAMP
                WHERE series_id = %s
            """, (series_id,))
            self.conn.commit()
            logger.info(f"Updated last_updated timestamp for {series_id}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error updating last_updated: {str(e)}")
            raise
        finally:
            cursor.close()

    def log_etl_run(self, status: str, records_processed: int,
                    error_message: str = None, execution_time: float = None):
        """
        Log ETL run details

        Args:
            status: 'success' or 'failure'
            records_processed: Number of records processed
            error_message: Optional error message
            execution_time: Execution time in seconds
        """
        if not self.conn:
            logger.warning("Cannot log ETL run - no database connection")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO etl_logs (status, records_processed, error_message, execution_time_seconds)
                VALUES (%s, %s, %s, %s)
            """, (status, records_processed, error_message, execution_time))

            self.conn.commit()
            logger.info("ETL run logged to database")
        except Exception as e:
            logger.error(f"Error logging ETL run: {str(e)}")
            self.conn.rollback()
        finally:
            cursor.close()

    def get_latest_observation_date(self, series_id: str) -> str:
        """
        Get the most recent observation date for a series

        Args:
            series_id: FRED series ID

        Returns:
            Latest observation date as string (YYYY-MM-DD) or None
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT MAX(observation_date)
                FROM indicator_data
                WHERE indicator_id = (
                    SELECT indicator_id FROM indicators WHERE series_id = %s
                )
            """, (series_id,))
            result = cursor.fetchone()
            if result and result[0]:
                return result[0].strftime('%Y-%m-%d')
            return None
        finally:
            cursor.close()
