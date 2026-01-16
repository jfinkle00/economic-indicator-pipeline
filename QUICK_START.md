# Quick Start Guide 🚀

Get the Economic Indicator ETL Pipeline running in 10 minutes!

---

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] AWS Account (Free Tier) - [Sign up here](https://aws.amazon.com/free/)
- [ ] FRED API Key - [Get free key here](https://fred.stlouisfed.org/docs/api/api_key.html)
- [ ] Python 3.11+ installed
- [ ] AWS CLI installed and configured
- [ ] Git installed

---

## Step 1: Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/economic-indicator-pipeline.git
cd economic-indicator-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure Environment (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your credentials
# You need: FRED_API_KEY
```

Your `.env` should look like:
```bash
FRED_API_KEY=your_fred_api_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=economic-indicators-pipeline-your-initials
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_NAME=economic_indicators
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_PORT=5432
```

---

## Step 3: Run Locally (Test Mode) - 1 minute

You can test the pipeline locally without AWS:

```bash
# Just run it!
python lambda/lambda_function.py
```

**Expected Output:**
```
============================================================
Running Lambda function locally...
============================================================

Status Code: 200
Body: {'message': 'ETL pipeline executed successfully',
       'records_processed': 22,
       'execution_time_seconds': 1.58}
```

**🎉 Congratulations!** Your ETL pipeline is working!

---

## Step 4: Deploy to AWS (Optional) - 5 minutes

Want it to run automatically every day? Deploy to AWS:

### 4a. Create S3 Bucket

```bash
aws s3 mb s3://economic-indicators-pipeline-jf --region us-east-1
```

### 4b. Create RDS Database

```bash
aws rds create-db-instance \
    --db-instance-identifier economic-indicators-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 16.3 \
    --master-username postgres \
    --master-user-password EconData2024! \
    --allocated-storage 20 \
    --storage-type gp2 \
    --publicly-accessible \
    --backup-retention-period 1 \
    --no-multi-az

# Wait for it to be ready (5-10 minutes)
aws rds wait db-instance-available --db-instance-identifier economic-indicators-db
```

### 4c. Initialize Database

```bash
# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier economic-indicators-db \
  --query "DBInstances[0].Endpoint.Address" --output text

# Update .env with the endpoint
# Then run:
python initialize_database.py
```

### 4d. Deploy Lambda Function

```bash
# Package Lambda
mkdir lambda_package
cp lambda/*.py lambda_package/
pip install boto3 requests python-dotenv -t lambda_package/ --platform manylinux2014_x86_64 --only-binary=:all:
pip install psycopg2-binary -t lambda_package/ --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.11

# Zip it
cd lambda_package && zip -r ../lambda_deployment.zip . && cd ..

# Create IAM role
aws iam create-role \
  --role-name EconomicIndicatorLambdaRole \
  --assume-role-policy-document file://infrastructure/trust-policy.json

# Attach policy
aws iam put-role-policy \
  --role-name EconomicIndicatorLambdaRole \
  --policy-name LambdaExecutionPolicy \
  --policy-document file://infrastructure/lambda_execution_role_policy.json

# Deploy Lambda
aws lambda create-function \
  --function-name economic-indicator-etl \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/EconomicIndicatorLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment "Variables={
    FRED_API_KEY=your_api_key,
    S3_BUCKET_NAME=your_bucket,
    DB_HOST=your_rds_endpoint,
    DB_NAME=economic_indicators,
    DB_USER=postgres,
    DB_PASSWORD=your_password,
    DB_PORT=5432
  }"
```

### 4e. Schedule Daily Runs

```bash
# Create CloudWatch Event Rule
aws events put-rule \
  --name economic-indicator-daily-run \
  --schedule-expression "cron(0 8 * * ? *)"

# Add Lambda as target
aws events put-targets \
  --rule economic-indicator-daily-run \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:economic-indicator-etl"

# Grant permission
aws lambda add-permission \
  --function-name economic-indicator-etl \
  --statement-id AllowCloudWatchInvoke \
  --action 'lambda:InvokeFunction' \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:YOUR_ACCOUNT_ID:rule/economic-indicator-daily-run
```

---

## Step 5: Verify Everything Works

### Test Lambda in AWS

```bash
aws lambda invoke \
  --function-name economic-indicator-etl \
  --payload '{}' \
  response.json

cat response.json
```

### Verify Data

```bash
python verify_data.py
```

Expected output:
```
============================================================
Economic Indicator Pipeline - Data Verification
============================================================

Table Statistics:
  - Indicators: 5 records
  - Indicator Data: 22 records
  - ETL Logs: 1 records
```

---

## What's Next?

### Query Your Data

```bash
# Connect to database
psql -h your-rds-endpoint.rds.amazonaws.com \
     -U postgres \
     -d economic_indicators

# Run queries
\i sql/sample_analysis.sql
```

### View Latest Economic Data

```sql
SELECT * FROM indicators;

SELECT
    i.title,
    d.value,
    d.observation_date
FROM indicators i
JOIN indicator_data d ON i.indicator_id = d.indicator_id
WHERE i.series_id = 'UNRATE'
ORDER BY d.observation_date DESC
LIMIT 1;
```

### Monitor CloudWatch Logs

Go to AWS Console → CloudWatch → Logs → `/aws/lambda/economic-indicator-etl`

---

## Troubleshooting

### Issue: Lambda timeout
```bash
aws lambda update-function-configuration \
  --function-name economic-indicator-etl \
  --timeout 600
```

### Issue: Can't connect to database
```bash
# Check RDS is running
aws rds describe-db-instances \
  --db-instance-identifier economic-indicators-db \
  --query "DBInstances[0].DBInstanceStatus"
```

### Issue: FRED API rate limit
Wait a few minutes and try again. FRED allows 120 requests/minute.

---

## Important Notes

### Cost
- **Free Tier (12 months):** $0/month ✅
- **After Free Tier:** ~$17/month
- **Cost Savings:** Stop RDS when not in use

### Security
- Never commit `.env` file to Git
- Use strong passwords
- Rotate credentials regularly
- Enable MFA on AWS account

### Next Steps
- Read [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed usage
- Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete docs
- Check [README.md](README.md) for full project info

---

## Need Help?

- Check CloudWatch Logs for errors
- Review `etl_logs` table in database
- See [USAGE_GUIDE.md](USAGE_GUIDE.md) for troubleshooting
- Open an issue on GitHub

---

**🎉 You're all set! Your pipeline will now run daily at 8:00 AM UTC.**

**Last Updated:** January 16, 2026
