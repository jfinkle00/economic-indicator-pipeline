# Usage Guide - AWS Economic Indicator ETL Pipeline

This guide explains how to use the Economic Indicator ETL Pipeline in your day-to-day workflow.

---

## Table of Contents

1. [Overview](#overview)
2. [Daily Usage](#daily-usage)
3. [Running the Pipeline Manually](#running-the-pipeline-manually)
4. [Querying and Analyzing Data](#querying-and-analyzing-data)
5. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
6. [Common Use Cases](#common-use-cases)
7. [Maintenance Tasks](#maintenance-tasks)

---

## Overview

The pipeline runs **automatically every day at 8:00 AM UTC**. You don't need to do anything for it to work - it will fetch, process, and load economic data automatically.

However, you can:
- Run it manually anytime
- Query the data for analysis
- Monitor execution logs
- Add new indicators
- Export data for reporting

---

## Daily Usage

### What Happens Automatically

Every day at 8:00 AM UTC (3:00 AM EST):
1. Lambda function wakes up
2. Fetches latest data from FRED API for 5 indicators
3. Saves raw JSON to S3 bucket
4. Processes and loads data into PostgreSQL
5. Logs execution results

**You don't need to do anything!** The data is always fresh and ready to query.

### Checking Today's Data

To see if today's run was successful:

```bash
# Check latest ETL logs
cd economic-indicator-pipeline
source venv/bin/activate  # Windows: venv\Scripts\activate
python verify_data.py
```

Expected output:
```
Most Recent ETL Runs:
------------------------------------------------------------
2026-01-16 16:55:29 | success  |   22 records | 1.58s
```

---

## Running the Pipeline Manually

### Option 1: Run Locally

Use this when you want to test changes or debug issues.

```bash
# Navigate to project
cd economic-indicator-pipeline

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run the pipeline
python lambda/lambda_function.py
```

**What happens:**
- Connects to FRED API
- Fetches data for all 5 indicators
- Uploads raw JSON to S3
- Loads data into RDS database
- Shows execution summary

**Expected output:**
```
============================================================
Running Lambda function locally...
============================================================

============================================================
Execution Result:
============================================================
Status Code: 200
Body: {'message': 'ETL pipeline executed successfully', 'records_processed': 22, 'execution_time_seconds': 1.58}
```

### Option 2: Run on AWS

Use this to trigger the Lambda function in AWS.

```bash
aws lambda invoke \
  --function-name economic-indicator-etl \
  --payload '{}' \
  response.json

# View the result
cat response.json
```

**Expected output:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "ETL pipeline executed successfully",
    "records_processed": 22,
    "execution_time_seconds": 1.58
  }
}
```

### Option 3: Test in AWS Console

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Select function: `economic-indicator-etl`
3. Click **Test** tab
4. Create test event (empty JSON: `{}`)
5. Click **Test**
6. View execution results

---

## Querying and Analyzing Data

### Method 1: Using psql (PostgreSQL CLI)

**Connect to database:**
```bash
psql -h economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d economic_indicators
```

Enter password when prompted: `EconData2024!`

**Run quick queries:**

```sql
-- View all indicators
SELECT * FROM indicators;

-- Latest unemployment rate
SELECT observation_date, value
FROM indicator_data
WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
ORDER BY observation_date DESC
LIMIT 1;

-- Latest 10-year treasury rates (last 7 days)
SELECT observation_date, value
FROM indicator_data
WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'DGS10')
ORDER BY observation_date DESC
LIMIT 7;
```

### Method 2: Using SQL Files

**Run pre-built analysis queries:**
```bash
psql -h economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d economic_indicators \
     -f sql/sample_analysis.sql
```

**Available query files:**
- `sql/queries.sql` - Common queries
- `sql/sample_analysis.sql` - Advanced analytics

### Method 3: Python Script

Create a Python script to query data:

```python
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT')
)

# Query unemployment data
query = """
    SELECT observation_date, value
    FROM indicator_data
    WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
    ORDER BY observation_date DESC
    LIMIT 12;
"""

df = pd.read_sql(query, conn)
print(df)

conn.close()
```

### Method 4: Database GUI Tools

Use tools like:
- **DBeaver** (Free) - https://dbeaver.io/
- **pgAdmin** (Free) - https://www.pgadmin.org/
- **DataGrip** (Paid) - https://www.jetbrains.com/datagrip/

**Connection details:**
- Host: `economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com`
- Port: `5432`
- Database: `economic_indicators`
- Username: `postgres`
- Password: `EconData2024!`

---

## Monitoring and Troubleshooting

### Check Pipeline Status

**1. Verify data was loaded:**
```bash
cd economic-indicator-pipeline
python verify_data.py
```

**2. Check S3 for raw data:**
```bash
aws s3 ls s3://economic-indicators-pipeline-jf/raw/ --recursive
```

**3. View CloudWatch Logs:**

```bash
# List recent log streams
aws logs describe-log-streams \
  --log-group-name /aws/lambda/economic-indicator-etl \
  --order-by LastEventTime \
  --descending \
  --max-items 5

# Or view in AWS Console:
# CloudWatch → Logs → Log groups → /aws/lambda/economic-indicator-etl
```

**4. Check scheduled runs:**
```bash
aws events list-rules --name-prefix economic-indicator
```

### Common Issues

#### Issue 1: No new data loaded

**Symptom:** `verify_data.py` shows same data count

**Cause:** Some indicators update monthly/quarterly (GDP, UNRATE, CPI)

**Solution:** This is normal! Only DGS10 (10-Year Treasury) updates daily.

#### Issue 2: Lambda timeout

**Symptom:** Error: "Task timed out after 300 seconds"

**Solution:**
```bash
# Increase timeout to 600 seconds
aws lambda update-function-configuration \
  --function-name economic-indicator-etl \
  --timeout 600
```

#### Issue 3: Database connection failed

**Symptom:** "Connection refused" or "Could not connect to server"

**Cause:** RDS instance may be stopped or security group issue

**Solution:**
```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier economic-indicators-db \
  --query "DBInstances[0].DBInstanceStatus"

# If stopped, start it
aws rds start-db-instance \
  --db-instance-identifier economic-indicators-db
```

#### Issue 4: FRED API rate limit

**Symptom:** "Rate limit exceeded" in logs

**Cause:** Too many API requests

**Solution:** Wait a few minutes and try again. FRED API allows 120 requests/minute.

---

## Common Use Cases

### Use Case 1: Daily Economic Briefing

Get a snapshot of key economic indicators:

```sql
-- Save this as daily_briefing.sql
SELECT
    i.series_id,
    i.title,
    d.value,
    d.observation_date,
    i.units
FROM indicators i
LEFT JOIN LATERAL (
    SELECT value, observation_date
    FROM indicator_data
    WHERE indicator_id = i.indicator_id
    ORDER BY observation_date DESC
    LIMIT 1
) d ON true
ORDER BY i.series_id;
```

Run it:
```bash
psql -h economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d economic_indicators \
     -f daily_briefing.sql
```

### Use Case 2: Export Data to CSV

Export unemployment data for the last year:

```bash
psql -h economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d economic_indicators \
     -c "COPY (
         SELECT observation_date, value
         FROM indicator_data
         WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
         AND observation_date >= CURRENT_DATE - INTERVAL '1 year'
         ORDER BY observation_date
     ) TO STDOUT WITH CSV HEADER" > unemployment_data.csv
```

### Use Case 3: Weekly Report

Create a Python script to generate weekly reports:

```python
# weekly_report.py
import psycopg2
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cursor = conn.cursor()

print("=" * 60)
print(f"Economic Indicators Report - {datetime.now().strftime('%Y-%m-%d')}")
print("=" * 60)
print()

# Get latest values
cursor.execute("""
    SELECT i.title, d.value, d.observation_date, i.units
    FROM indicators i
    LEFT JOIN LATERAL (
        SELECT value, observation_date
        FROM indicator_data
        WHERE indicator_id = i.indicator_id
        ORDER BY observation_date DESC
        LIMIT 1
    ) d ON true
    ORDER BY i.series_id;
""")

for title, value, date, units in cursor.fetchall():
    if value:
        print(f"{title:40s} {value:8.2f} {units:20s} (as of {date})")
    else:
        print(f"{title:40s} No data")

cursor.close()
conn.close()
```

Run it:
```bash
python weekly_report.py
```

### Use Case 4: Add New Indicator

To track a new indicator (e.g., "HOUST" - Housing Starts):

**1. Add to database:**
```sql
INSERT INTO indicators (series_id, title, units, frequency, seasonal_adjustment)
VALUES ('HOUST', 'Housing Starts', 'Thousands of Units', 'Monthly', 'Seasonally Adjusted Annual Rate');
```

**2. Update Lambda configuration:**
```python
# Edit lambda/lambda_function.py
INDICATORS = ['UNRATE', 'CPIAUCSL', 'GDP', 'FEDFUNDS', 'DGS10', 'HOUST']
```

**3. Redeploy:**
```bash
cd economic-indicator-pipeline
rm -rf lambda_package && mkdir lambda_package
cp lambda/*.py lambda_package/
pip install boto3 requests python-dotenv -t lambda_package/ --platform manylinux2014_x86_64 --only-binary=:all:
pip install psycopg2-binary -t lambda_package/ --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.11
cd lambda_package && zip -r ../lambda_deployment.zip . && cd ..
aws lambda update-function-code --function-name economic-indicator-etl --zip-file fileb://lambda_deployment.zip
```

---

## Maintenance Tasks

### Weekly Maintenance

**Check pipeline health:**
```bash
python verify_data.py
```

**Review CloudWatch logs for errors:**
```bash
# Via AWS Console: CloudWatch → Logs → /aws/lambda/economic-indicator-etl
```

### Monthly Maintenance

**Check data completeness:**
```sql
SELECT
    i.series_id,
    COUNT(d.data_id) as total_records,
    MIN(d.observation_date) as earliest_date,
    MAX(d.observation_date) as latest_date
FROM indicators i
LEFT JOIN indicator_data d ON i.indicator_id = d.indicator_id
GROUP BY i.series_id;
```

**Clean up old S3 data (optional):**
```bash
# Delete raw data older than 90 days
aws s3 ls s3://economic-indicators-pipeline-jf/raw/ --recursive | \
  awk '{if ($1 < "'$(date -d '90 days ago' +%Y-%m-%d)'") print $4}' | \
  xargs -I {} aws s3 rm s3://economic-indicators-pipeline-jf/{}
```

### Backup Recommendations

**1. Database backup (Manual):**
```bash
# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier economic-indicators-db \
  --db-snapshot-identifier economic-indicators-backup-$(date +%Y%m%d)
```

**2. Export full database:**
```bash
pg_dump -h economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com \
        -U postgres \
        -d economic_indicators \
        -f backup_$(date +%Y%m%d).sql
```

### Cost Monitoring

**Check AWS costs:**
```bash
# Via AWS Console: Cost Explorer or Billing Dashboard
# Expected: $0/month (Free Tier) or ~$17/month after
```

**To reduce costs:**
- Stop RDS when not needed: `aws rds stop-db-instance --db-instance-identifier economic-indicators-db`
- Delete old S3 data
- Reduce Lambda execution frequency

---

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run pipeline locally
python lambda/lambda_function.py

# Run pipeline on AWS
aws lambda invoke --function-name economic-indicator-etl --payload '{}' response.json

# Verify data
python verify_data.py

# Connect to database
psql -h economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com -U postgres -d economic_indicators

# Check S3 data
aws s3 ls s3://economic-indicators-pipeline-jf/raw/ --recursive

# View Lambda logs
# AWS Console → CloudWatch → Logs → /aws/lambda/economic-indicator-etl

# Check scheduled runs
aws events list-rules --name-prefix economic-indicator
```

---

## Getting Help

- **CloudWatch Logs:** Check `/aws/lambda/economic-indicator-etl` for errors
- **Database Logs:** Review `etl_logs` table for execution history
- **FRED API Docs:** https://fred.stlouisfed.org/docs/api/
- **AWS Lambda Docs:** https://docs.aws.amazon.com/lambda/

---

**Last Updated:** January 16, 2026
