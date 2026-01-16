# How to Use the Economic Indicator Pipeline

**TL;DR:** The pipeline runs automatically every day. You can query the data anytime or run it manually when needed.

---

## 📅 Daily Automatic Runs

**What happens:** Every day at 8:00 AM UTC (3:00 AM EST), the pipeline automatically:
1. Fetches latest economic data from FRED
2. Saves raw JSON to S3
3. Loads data into PostgreSQL database
4. Logs execution results

**You don't need to do anything!** The data is always fresh.

---

## 🔍 Checking Today's Data

### Quick Check
```bash
cd economic-indicator-pipeline
source venv/bin/activate  # Windows: venv\Scripts\activate
python verify_data.py
```

You'll see:
- How many indicators are tracked
- Total data points
- Latest ETL run status
- Sample data from each indicator

---

## 📊 Generate Visualizations & Forecasts

### Quick Summary Report
```bash
python generate_report.py --quick
```

**Shows**:
- Latest values for all indicators
- Last update times

### Full Report with Charts & Forecasts
```bash
python generate_report.py --full
```

**Generates**:
- Multi-indicator dashboard
- Interactive HTML dashboard
- Individual time series plots
- Year-over-year change charts
- Correlation heatmap
- 12-month ARIMA forecasts

**Output**: All files saved to `outputs/charts/`

**To view interactive dashboard**:
```bash
# Open in browser
start outputs/charts/interactive_dashboard.html  # Windows
open outputs/charts/interactive_dashboard.html   # Mac
```

---

## 🎯 Common Use Cases

### 1. Get Latest Economic Snapshot

**Query the database:**
```bash
psql -h economic-indicators-db.cwtumgo4650t.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d economic_indicators
```

**Run this query:**
```sql
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
) d ON true;
```

**Result:**
```
 series_id |          title           | value | observation_date
-----------+--------------------------+-------+------------------
 CPIAUCSL  | Consumer Price Index     | 314.9 | 2025-12-01
 DGS10     | 10-Year Treasury Rate    |  4.55 | 2026-01-14
 FEDFUNDS  | Federal Funds Rate       |  4.33 | 2025-12-01
 GDP       | Gross Domestic Product   | NULL  | NULL
 UNRATE    | Unemployment Rate        |  4.40 | 2025-12-01
```

### 2. Export Data to CSV

**Export unemployment data:**
```bash
psql -h your-rds-endpoint \
     -U postgres \
     -d economic_indicators \
     -c "COPY (
         SELECT observation_date, value
         FROM indicator_data
         WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
         ORDER BY observation_date
     ) TO STDOUT WITH CSV HEADER" > unemployment.csv
```

### 3. Run Pipeline Manually

**Run locally:**
```bash
cd economic-indicator-pipeline
source venv/bin/activate
python lambda/lambda_function.py
```

**Run on AWS:**
```bash
aws lambda invoke \
  --function-name economic-indicator-etl \
  --payload '{}' \
  response.json
```

### 4. Query with Python

**Create a simple script:**
```python
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

# Get unemployment rate
df = pd.read_sql("""
    SELECT observation_date, value
    FROM indicator_data
    WHERE indicator_id = (
        SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE'
    )
    ORDER BY observation_date DESC
    LIMIT 12
""", conn)

print(df)
conn.close()
```

### 5. View Raw S3 Data

**List raw JSON files:**
```bash
aws s3 ls s3://economic-indicators-pipeline-jf/raw/ --recursive
```

**Download a file:**
```bash
aws s3 cp s3://economic-indicators-pipeline-jf/raw/UNRATE/20260116_110556.json ./
```

---

## 📊 Pre-Built Analysis Queries

Run comprehensive analysis:
```bash
psql -h your-rds-endpoint \
     -U postgres \
     -d economic_indicators \
     -f sql/sample_analysis.sql
```

**Available queries:**
- Latest values for all indicators
- Year-over-year changes
- Trend analysis
- ETL performance metrics
- Data completeness checks

---

## 🔧 Maintenance

### Weekly

**Check pipeline health:**
```bash
python verify_data.py
```

### Monthly

**Clean up old S3 data (optional):**
```bash
# Delete files older than 90 days
aws s3 ls s3://economic-indicators-pipeline-jf/raw/ --recursive | \
  awk '{if ($1 < "'$(date -d '90 days ago' +%Y-%m-%d)'") print $4}' | \
  xargs -I {} aws s3 rm s3://economic-indicators-pipeline-jf/{}
```

### As Needed

**Stop RDS to save costs:**
```bash
# Stop database
aws rds stop-db-instance --db-instance-identifier economic-indicators-db

# Start it again when needed
aws rds start-db-instance --db-instance-identifier economic-indicators-db
```

---

## 🚨 Troubleshooting

### Pipeline Failed?

**Check CloudWatch Logs:**
- Go to AWS Console → CloudWatch → Logs
- Select: `/aws/lambda/economic-indicator-etl`
- Look for error messages

**Check ETL logs in database:**
```sql
SELECT * FROM etl_logs ORDER BY run_timestamp DESC LIMIT 5;
```

### No New Data?

**This is normal!** Most indicators update monthly or quarterly:
- **UNRATE** (Unemployment): Monthly (1st week of month)
- **CPIAUCSL** (CPI): Monthly (mid-month)
- **GDP**: Quarterly
- **FEDFUNDS**: Monthly
- **DGS10** (Treasury): Daily (weekdays)

Only DGS10 updates every weekday.

### Database Connection Issues?

**Check if RDS is running:**
```bash
aws rds describe-db-instances \
  --db-instance-identifier economic-indicators-db \
  --query "DBInstances[0].DBInstanceStatus"
```

---

## 📚 Full Documentation

For more details, see:
- **[QUICK_START.md](QUICK_START.md)** - Setup guide
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed usage instructions
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete documentation
- **[README.md](README.md)** - GitHub overview

---

## 🎓 Common Commands Reference

```bash
# Activate environment
source venv/bin/activate

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

# Check scheduled runs
aws events list-rules --name-prefix economic-indicator

# View CloudWatch logs
# AWS Console → CloudWatch → Logs → /aws/lambda/economic-indicator-etl
```

---

**That's it!** The pipeline runs automatically, and you can query the data whenever you need it.

**Questions?** Check [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed help.

**Last Updated:** January 16, 2026
