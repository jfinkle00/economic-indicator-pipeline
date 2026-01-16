"""
Initialize the RDS PostgreSQL database with schema
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

def initialize_database():
    """Create database schema and insert initial data"""

    print("Connecting to database...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Database: {DB_CONFIG['database']}")

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        print("Connected successfully!")
        print("\nReading schema.sql file...")

        # Read and execute schema file
        with open('sql/schema.sql', 'r') as f:
            schema_sql = f.read()

        print("Executing schema...")
        cursor.execute(schema_sql)

        print("\n[SUCCESS] Database schema created successfully!")

        # Verify the setup
        print("\nVerifying indicators table:")
        cursor.execute("SELECT series_id, title FROM indicators;")
        indicators = cursor.fetchall()

        for series_id, title in indicators:
            print(f"  - {series_id}: {title}")

        # Check table counts
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM indicators) as indicators_count,
                (SELECT COUNT(*) FROM indicator_data) as data_count,
                (SELECT COUNT(*) FROM etl_logs) as logs_count;
        """)
        counts = cursor.fetchone()

        print(f"\nTable statistics:")
        print(f"  - Indicators: {counts[0]} records")
        print(f"  - Indicator Data: {counts[1]} records")
        print(f"  - ETL Logs: {counts[2]} records")

        cursor.close()
        conn.close()

        print("\n[SUCCESS] Database initialization complete!")
        return True

    except psycopg2.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False
    except FileNotFoundError:
        print("\n[ERROR] Error: sql/schema.sql file not found!")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Economic Indicator Pipeline - Database Initialization")
    print("=" * 60)
    print()

    success = initialize_database()

    if success:
        print("\n" + "=" * 60)
        print("You can now proceed with the ETL pipeline!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Database initialization failed. Please check the error above.")
        print("=" * 60)
