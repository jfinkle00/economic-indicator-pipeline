"""
System Validation Tests
Tests all components before GitHub push
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv
import boto3
from datetime import datetime

# Load environment
load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"{status} {name}")
    if details:
        print(f"      {details}")

def test_environment_variables():
    """Test that all required environment variables are set"""
    print_header("Environment Variables")

    required_vars = [
        'FRED_API_KEY',
        'S3_BUCKET_NAME',
        'DB_HOST',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_PORT'
    ]

    all_passed = True
    for var in required_vars:
        value = os.getenv(var)
        passed = value is not None and value != ''
        all_passed = all_passed and passed

        if var in ['FRED_API_KEY', 'DB_PASSWORD']:
            display = '***' if passed else 'NOT SET'
        else:
            display = value if passed else 'NOT SET'

        print_test(f"{var}", passed, display)

    return all_passed

def test_database_connection():
    """Test database connectivity and schema"""
    print_header("Database Connection")

    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT', 5432))
        )
        print_test("Database connection", True, f"Connected to {os.getenv('DB_HOST')}")

        # Test tables exist
        cursor = conn.cursor()

        tables = ['indicators', 'indicator_data', 'etl_logs']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print_test(f"Table '{table}' exists", True, f"{count} rows")

        # Test data exists
        cursor.execute("SELECT COUNT(*) FROM indicator_data")
        data_count = cursor.fetchone()[0]
        print_test("Data loaded", data_count > 0, f"{data_count} total data points")

        conn.close()
        return True

    except Exception as e:
        print_test("Database connection", False, str(e))
        return False

def test_s3_bucket():
    """Test S3 bucket accessibility"""
    print_header("AWS S3 Bucket")

    try:
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BUCKET_NAME')

        # Check if bucket exists
        s3.head_bucket(Bucket=bucket)
        print_test("S3 bucket exists", True, bucket)

        # Check for raw data
        response = s3.list_objects_v2(Bucket=bucket, Prefix='raw/', MaxKeys=10)
        file_count = response.get('KeyCount', 0)
        print_test("Raw data files exist", file_count > 0, f"{file_count} files found")

        return True

    except Exception as e:
        print_test("S3 bucket access", False, str(e))
        return False

def test_lambda_function():
    """Test Lambda function exists"""
    print_header("AWS Lambda Function")

    try:
        lambda_client = boto3.client('lambda')

        response = lambda_client.get_function(
            FunctionName='economic-indicator-etl'
        )

        config = response['Configuration']
        print_test("Lambda function exists", True, f"Runtime: {config['Runtime']}")
        print_test("Lambda memory", True, f"{config['MemorySize']} MB")
        print_test("Lambda timeout", True, f"{config['Timeout']} seconds")

        return True

    except Exception as e:
        print_test("Lambda function", False, str(e))
        return False

def test_cloudwatch_schedule():
    """Test CloudWatch Events rule"""
    print_header("CloudWatch Events")

    try:
        events = boto3.client('events')

        response = events.list_rules(NamePrefix='economic-indicator')

        if response['Rules']:
            rule = response['Rules'][0]
            print_test("CloudWatch rule exists", True, rule['Name'])
            print_test("Schedule expression", True, rule.get('ScheduleExpression', 'N/A'))
            print_test("Rule state", rule['State'] == 'ENABLED', rule['State'])
            return True
        else:
            print_test("CloudWatch rule exists", False, "No rules found")
            return False

    except Exception as e:
        print_test("CloudWatch Events", False, str(e))
        return False

def test_python_modules():
    """Test that all required Python modules can be imported"""
    print_header("Python Modules")

    modules = [
        'boto3',
        'psycopg2',
        'requests',
        'dotenv',
        'pandas',
        'matplotlib',
        'plotly',
        'seaborn',
        'statsmodels',
        'prophet',
        'numpy',
        'scipy'
    ]

    all_passed = True
    for module in modules:
        try:
            if module == 'dotenv':
                __import__('dotenv')
            else:
                __import__(module)
            print_test(f"{module}", True)
        except ImportError as e:
            print_test(f"{module}", False, str(e))
            all_passed = False

    return all_passed

def test_project_structure():
    """Test that all required files and directories exist"""
    print_header("Project Structure")

    required_items = [
        ('lambda/lambda_function.py', 'file'),
        ('lambda/fred_client.py', 'file'),
        ('lambda/s3_handler.py', 'file'),
        ('lambda/db_handler.py', 'file'),
        ('sql/schema.sql', 'file'),
        ('visualizations/charts.py', 'file'),
        ('forecasting/models.py', 'file'),
        ('generate_report.py', 'file'),
        ('verify_data.py', 'file'),
        ('requirements.txt', 'file'),
        ('README.md', 'file'),
        ('.env', 'file'),
        ('outputs/charts/', 'dir')
    ]

    all_passed = True
    for item, item_type in required_items:
        if item_type == 'file':
            exists = os.path.isfile(item)
        else:
            exists = os.path.isdir(item)

        print_test(item, exists)
        all_passed = all_passed and exists

    return all_passed

def test_visualization_outputs():
    """Test that visualization outputs exist"""
    print_header("Visualization Outputs")

    expected_files = [
        'multi_indicator_dashboard.png',
        'interactive_dashboard.html',
        'unemployment_rate_timeseries.png',
        'consumer_price_index_timeseries.png',
        'unemployment_rate_forecast.png',
        'consumer_price_index_forecast.png',
        'correlation_heatmap.png'
    ]

    charts_dir = 'outputs/charts'
    if not os.path.exists(charts_dir):
        print_test("Charts directory", False, "Directory not found")
        return False

    all_passed = True
    for filename in expected_files:
        filepath = os.path.join(charts_dir, filename)
        exists = os.path.isfile(filepath)

        if exists:
            size = os.path.getsize(filepath)
            size_kb = size / 1024
            print_test(filename, True, f"{size_kb:.1f} KB")
        else:
            print_test(filename, False, "Not found")
            all_passed = False

    return all_passed

def main():
    """Run all validation tests"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"Economic Indicator Pipeline - System Validation")
    print(f"{'='*70}{Colors.END}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {}

    # Run all tests
    results['Environment'] = test_environment_variables()
    results['Database'] = test_database_connection()
    results['S3'] = test_s3_bucket()
    results['Lambda'] = test_lambda_function()
    results['CloudWatch'] = test_cloudwatch_schedule()
    results['Python Modules'] = test_python_modules()
    results['Project Structure'] = test_project_structure()
    results['Visualizations'] = test_visualization_outputs()

    # Print summary
    print_header("Validation Summary")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name:.<40} [{status}]")

    print(f"\n{Colors.BOLD}Overall: {passed_tests}/{total_tests} test suites passed{Colors.END}")

    if passed_tests == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] All systems operational - Ready for GitHub push!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}[WARNING] Some tests failed - Review issues before pushing{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
