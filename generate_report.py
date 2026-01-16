"""
Generate Economic Indicators Report
Creates visualizations and forecasts for all indicators
"""
import psycopg2
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add paths
sys.path.append('visualizations')
sys.path.append('forecasting')

from visualizations.charts import EconomicCharts
from forecasting.models import EconomicForecaster

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

# Indicators configuration
INDICATORS = {
    'UNRATE': 'Unemployment Rate',
    'CPIAUCSL': 'Consumer Price Index',
    'GDP': 'Gross Domestic Product',
    'FEDFUNDS': 'Federal Funds Rate',
    'DGS10': '10-Year Treasury Rate'
}


def fetch_indicator_data(conn, series_id):
    """
    Fetch indicator data from database

    Args:
        conn: Database connection
        series_id: FRED series ID

    Returns:
        DataFrame with observation_date and value columns
    """
    query = """
        SELECT d.observation_date, d.value
        FROM indicator_data d
        JOIN indicators i ON d.indicator_id = i.indicator_id
        WHERE i.series_id = %s
        ORDER BY d.observation_date ASC
    """

    df = pd.read_sql(query, conn, params=(series_id,))
    df['observation_date'] = pd.to_datetime(df['observation_date'])

    return df


def calculate_yoy_change(df):
    """Calculate year-over-year percentage change"""
    df = df.copy()
    df = df.sort_values('observation_date')
    df['yoy_pct_change'] = df['value'].pct_change(periods=12) * 100
    return df.dropna()


def generate_all_reports():
    """Generate comprehensive report with all visualizations and forecasts"""

    print("=" * 70)
    print("Economic Indicators Report Generator")
    print("=" * 70)
    print()

    # Connect to database
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connected successfully")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return

    # Initialize chart generator
    charts = EconomicCharts(output_dir='outputs/charts')
    print(f"[OK] Output directory: outputs/charts")
    print()

    # Fetch all data
    print("Fetching indicator data...")
    data_dict = {}
    for series_id, name in INDICATORS.items():
        df = fetch_indicator_data(conn, series_id)
        if len(df) > 0:
            data_dict[name] = df
            print(f"  [OK] {name}: {len(df)} data points")
        else:
            print(f"  [SKIP] {name}: No data available")

    print()

    # Generate visualizations
    print("Generating visualizations...")
    print("-" * 70)

    # 1. Multi-indicator dashboard
    print("Creating multi-indicator dashboard...")
    charts.plot_multiple_indicators(data_dict, title="Economic Indicators Dashboard")

    # 2. Interactive dashboard
    print("Creating interactive dashboard...")
    charts.plot_interactive_dashboard(data_dict)

    # 3. Individual time series plots
    for name, df in data_dict.items():
        if len(df) > 0:
            print(f"Creating time series plot for {name}...")
            charts.plot_time_series(df, name)

    # 4. Year-over-year change plots
    print()
    print("Generating year-over-year change plots...")
    for name, df in data_dict.items():
        if len(df) >= 12:  # Need at least 12 months for YoY
            print(f"Creating YoY plot for {name}...")
            yoy_df = calculate_yoy_change(df)
            if len(yoy_df) > 0:
                charts.plot_yoy_change(yoy_df, name)

    # 5. Correlation analysis
    print()
    print("Calculating correlations...")
    if len(data_dict) > 1:
        # Merge all data on common dates
        correlation_df = None
        for name, df in data_dict.items():
            df_temp = df.set_index('observation_date')[['value']].rename(columns={'value': name})
            if correlation_df is None:
                correlation_df = df_temp
            else:
                correlation_df = correlation_df.join(df_temp, how='inner')

        if len(correlation_df) > 0:
            corr_matrix = correlation_df.corr()
            print("Creating correlation heatmap...")
            charts.plot_correlation_heatmap(corr_matrix)

    # Generate forecasts
    print()
    print("=" * 70)
    print("Generating Forecasts (ARIMA)")
    print("=" * 70)

    forecaster = EconomicForecaster()

    for name, df in data_dict.items():
        if len(df) >= 24:  # Need sufficient data for forecasting
            print()
            print(f"Forecasting {name}...")
            try:
                # Fit ARIMA model
                forecaster.fit_arima(df, order=(1, 1, 1))

                # Generate 12-month forecast
                forecast_df = forecaster.forecast_arima(steps=12)

                # Plot forecast
                charts.plot_trend_with_forecast(df, forecast_df, name)

                print(f"  [OK] {name} forecast completed")
                print(f"  Next 3 months forecast:")
                for i in range(min(3, len(forecast_df))):
                    row = forecast_df.iloc[i]
                    print(f"    {row['date'].strftime('%Y-%m')}: {row['forecast']:.2f} "
                          f"(95% CI: {row['lower']:.2f} - {row['upper']:.2f})")

            except Exception as e:
                print(f"  [ERROR] Could not forecast {name}: {e}")

    # Close database connection
    conn.close()

    print()
    print("=" * 70)
    print("Report Generation Complete!")
    print("=" * 70)
    print()
    print("Output files saved to: outputs/charts/")
    print()
    print("Generated files:")
    output_dir = 'outputs/charts'
    if os.path.exists(output_dir):
        files = sorted(os.listdir(output_dir))
        for file in files:
            filepath = os.path.join(output_dir, file)
            size = os.path.getsize(filepath)
            print(f"  • {file} ({size:,} bytes)")

    print()
    print("To view interactive dashboard, open:")
    print(f"  outputs/charts/interactive_dashboard.html")
    print()


def generate_quick_summary():
    """Generate a quick summary report"""

    print("=" * 70)
    print("Economic Indicators - Quick Summary")
    print("=" * 70)
    print()

    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        query = """
            SELECT
                i.series_id,
                i.title,
                d.value,
                d.observation_date
            FROM indicators i
            LEFT JOIN LATERAL (
                SELECT value, observation_date
                FROM indicator_data
                WHERE indicator_id = i.indicator_id
                ORDER BY observation_date DESC
                LIMIT 1
            ) d ON true
            ORDER BY i.series_id
        """

        df = pd.read_sql(query, conn)

        print("Latest Economic Indicators:")
        print("-" * 70)
        for _, row in df.iterrows():
            if pd.notna(row['value']):
                print(f"{row['title']:40s} {row['value']:8.2f}  (as of {row['observation_date']})")
            else:
                print(f"{row['title']:40s} No data")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate Economic Indicators Report')
    parser.add_argument('--quick', action='store_true',
                       help='Generate quick summary only')
    parser.add_argument('--full', action='store_true',
                       help='Generate full report with visualizations and forecasts')

    args = parser.parse_args()

    if args.quick:
        generate_quick_summary()
    elif args.full or len(sys.argv) == 1:
        generate_all_reports()
    else:
        print("Usage:")
        print("  python generate_report.py --full    # Full report with charts and forecasts")
        print("  python generate_report.py --quick   # Quick summary only")
