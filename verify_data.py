"""
Verify data was loaded into RDS database
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def verify_data():
    """Verify data was loaded successfully"""

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("=" * 60)
        print("Economic Indicator Pipeline - Data Verification")
        print("=" * 60)
        print()

        # Check table counts
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM indicators) as indicators_count,
                (SELECT COUNT(*) FROM indicator_data) as data_count,
                (SELECT COUNT(*) FROM etl_logs) as logs_count;
        """)
        counts = cursor.fetchone()

        print("Table Statistics:")
        print(f"  - Indicators: {counts[0]} records")
        print(f"  - Indicator Data: {counts[1]} records")
        print(f"  - ETL Logs: {counts[2]} records")
        print()

        # Show latest data for each indicator
        print("Latest Data by Indicator:")
        print("-" * 60)
        cursor.execute("""
            SELECT
                i.series_id,
                i.title,
                MAX(d.observation_date) as latest_date,
                COUNT(d.data_id) as total_records
            FROM indicators i
            LEFT JOIN indicator_data d ON i.indicator_id = d.indicator_id
            GROUP BY i.series_id, i.title
            ORDER BY i.series_id;
        """)

        for row in cursor.fetchall():
            print(f"  {row[0]:12s} | {row[2]} | {row[3]:4d} records | {row[1]}")

        print()

        # Show most recent ETL run
        print("Most Recent ETL Runs:")
        print("-" * 60)
        cursor.execute("""
            SELECT
                run_timestamp,
                status,
                records_processed,
                execution_time_seconds
            FROM etl_logs
            ORDER BY run_timestamp DESC
            LIMIT 5;
        """)

        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]:8s} | {row[2]:4d} records | {row[3]:.2f}s")

        print()

        # Show sample data (latest unemployment rate)
        print("Sample Data - Latest Unemployment Rates:")
        print("-" * 60)
        cursor.execute("""
            SELECT
                observation_date,
                value
            FROM indicator_data
            WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
            ORDER BY observation_date DESC
            LIMIT 5;
        """)

        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]}%")

        cursor.close()
        conn.close()

        print()
        print("=" * 60)
        print("[SUCCESS] Data verification complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")

if __name__ == "__main__":
    verify_data()
