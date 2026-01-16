# 📊 AWS Economic Indicator ETL Pipeline

> Automated cloud-native ETL pipeline for fetching, processing, and analyzing Federal Reserve economic data

[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20RDS-FF9900?logo=amazon-aws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.3-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success)](https://github.com/yourusername/economic-indicator-pipeline)

---

## 🎯 Overview

A production-ready, fully automated ETL (Extract, Transform, Load) pipeline that fetches real-time economic indicator data from the Federal Reserve Economic Data (FRED) API, stores raw data in AWS S3, processes it, and loads it into an AWS RDS PostgreSQL database. The pipeline runs automatically on a daily schedule using AWS Lambda and CloudWatch Events.

**Perfect for:**
- Economic research and analysis
- Financial modeling and forecasting
- Data engineering portfolio projects
- Learning AWS cloud architecture
- Building data-driven applications

---

## ✨ Features

### Core Pipeline
- **🔄 Fully Automated**: Runs daily at 8:00 AM UTC via CloudWatch Events
- **☁️ Cloud-Native**: Built entirely on AWS serverless architecture
- **💰 Cost-Effective**: $0/month on AWS Free Tier, ~$17/month after
- **📈 Real-Time Data**: Fetches latest economic indicators from FRED API
- **🗄️ Structured Storage**: Organized PostgreSQL database with proper indexing
- **📦 Raw Data Backup**: All API responses stored in S3 for audit trail
- **🔍 Advanced Analytics**: Pre-built SQL queries for economic analysis
- **📊 Production Metrics**: Complete logging and monitoring via CloudWatch
- **🛡️ Secure**: IAM roles with least-privilege access
- **🔧 Maintainable**: Modular Python code with clear separation of concerns

### Data Visualization & Analysis
- **📊 Interactive Dashboards**: Plotly-based interactive HTML dashboards
- **📈 Time Series Plots**: Professional matplotlib visualizations
- **📉 Trend Analysis**: Year-over-year change plots
- **🔗 Correlation Heatmaps**: Visual correlation analysis between indicators
- **📱 Export Ready**: High-resolution PNG charts for reports and presentations

### Forecasting & Predictions
- **🔮 ARIMA Forecasting**: Statistical time series forecasting with confidence intervals
- **🧠 Prophet Models**: Facebook Prophet for robust trend forecasting
- **🎯 Auto-Selection**: Automatic model parameter optimization
- **📐 Backtesting**: Model validation with historical data
- **⚡ 12-Month Forecasts**: Future economic indicator predictions

---

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │   FRED API      │
                    │ (Federal Reserve)│
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │    AWS Lambda Function       │
              │  economic-indicator-etl      │
              │                              │
              │  • Fetch data from FRED      │
              │  • Store raw JSON in S3      │
              │  • Transform data            │
              │  • Load into PostgreSQL      │
              └──────┬───────────────┬───────┘
                     │               │
                     ▼               ▼
         ┌───────────────┐  ┌────────────────────┐
         │   AWS S3      │  │   AWS RDS          │
         │   Bucket      │  │   PostgreSQL 16.3  │
         │               │  │                    │
         │  raw/         │  │  • indicators      │
         │  └─UNRATE/    │  │  • indicator_data  │
         │  └─GDP/       │  │  • etl_logs        │
         │  └─...        │  │                    │
         └───────────────┘  └────────────────────┘
                 ▲
                 │
      ┌──────────┴──────────────┐
      │   CloudWatch Events     │
      │   cron(0 8 * * ? *)    │
      │   Daily at 8:00 AM UTC  │
      └─────────────────────────┘
```

---

## 📊 Economic Indicators Tracked

| Indicator | Description | Frequency | Series ID |
|-----------|-------------|-----------|-----------|
| 🏢 **Unemployment Rate** | Civilian unemployment rate | Monthly | `UNRATE` |
| 💵 **Consumer Price Index** | CPI for all urban consumers (Inflation) | Monthly | `CPIAUCSL` |
| 📈 **GDP** | Gross Domestic Product | Quarterly | `GDP` |
| 💰 **Federal Funds Rate** | Effective federal funds rate | Monthly | `FEDFUNDS` |
| 📊 **10-Year Treasury** | 10-Year Treasury constant maturity rate | Daily | `DGS10` |

---

## 🚀 Quick Start

### Prerequisites

- AWS Account ([Sign up for Free Tier](https://aws.amazon.com/free/))
- FRED API Key ([Get free key](https://fred.stlouisfed.org/docs/api/api_key.html))
- Python 3.11+
- AWS CLI configured
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/economic-indicator-pipeline.git
   cd economic-indicator-pipeline
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your FRED API key and AWS credentials
   ```

4. **Deploy to AWS** (Optional - for automated pipeline)
   ```bash
   # Create RDS database
   aws rds create-db-instance \
       --db-instance-identifier economic-indicators-db \
       --db-instance-class db.t3.micro \
       --engine postgres \
       --master-username postgres \
       --master-user-password YourSecurePassword123! \
       --allocated-storage 20

   # Create S3 bucket
   aws s3 mb s3://economic-indicators-pipeline-your-initials

   # Deploy Lambda (see full deployment guide in docs/)
   ```

---

## 💻 Usage

### Run Locally

```bash
# Activate environment
source venv/bin/activate

# Run the ETL pipeline
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

### Run on AWS

```bash
# Trigger Lambda function
aws lambda invoke \
  --function-name economic-indicator-etl \
  --payload '{}' \
  response.json

# View result
cat response.json
```

### Query the Data

```bash
# Connect to database
psql -h your-rds-endpoint.rds.amazonaws.com \
     -U postgres \
     -d economic_indicators

# Run queries
SELECT * FROM indicators;
```

**Or use Python:**
```python
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="your-rds-endpoint.rds.amazonaws.com",
    database="economic_indicators",
    user="postgres",
    password="your-password"
)

df = pd.read_sql("SELECT * FROM indicator_data LIMIT 10", conn)
print(df)
```

### Generate Reports & Visualizations

**Quick summary:**
```bash
python generate_report.py --quick
```

**Full report with charts and forecasts:**
```bash
python generate_report.py --full
```

**Output includes:**
- Multi-indicator dashboard
- Interactive HTML dashboard
- Individual time series plots
- Year-over-year change analysis
- Correlation heatmap
- 12-month ARIMA forecasts

**Example output:**
```
Economic Indicators Report Generator
======================================================================

Connecting to database...
✓ Connected successfully
✓ Output directory: outputs/charts

Fetching indicator data...
  ✓ Unemployment Rate: 1 data points
  ✓ Consumer Price Index: 1 data points
  ✓ 10-Year Treasury Rate: 19 data points

Generating visualizations...
Creating multi-indicator dashboard...
Saved: outputs/charts/multi_indicator_dashboard.png
Creating interactive dashboard...
Saved: outputs/charts/interactive_dashboard.html

Generating Forecasts (ARIMA)
======================================================================
Forecasting Unemployment Rate...
  ✓ Unemployment Rate forecast completed
  Next 3 months forecast:
    2026-02: 4.42 (95% CI: 3.95 - 4.89)
    2026-03: 4.44 (95% CI: 3.87 - 5.01)
    2026-04: 4.46 (95% CI: 3.81 - 5.11)
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[USAGE_GUIDE.md](USAGE_GUIDE.md)** | Complete guide on how to use the pipeline |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Detailed project documentation |
| **[sql/](sql/)** | Database schema and analysis queries |
| **[infrastructure/](infrastructure/)** | IAM policies and CloudWatch configs |

---

## 🗂️ Project Structure

```
economic-indicator-pipeline/
│
├── lambda/                          # Lambda function source code
│   ├── lambda_function.py          # Main ETL handler
│   ├── fred_client.py              # FRED API client
│   ├── s3_handler.py               # S3 operations
│   ├── db_handler.py               # Database operations
│   └── config.py                   # Configuration
│
├── visualizations/                  # Data visualization modules
│   ├── __init__.py
│   └── charts.py                   # Chart generation (matplotlib, plotly)
│
├── forecasting/                     # Forecasting modules
│   ├── __init__.py
│   └── models.py                   # ARIMA & Prophet models
│
├── sql/                             # SQL scripts
│   ├── schema.sql                  # Database schema
│   ├── queries.sql                 # Common queries
│   └── sample_analysis.sql         # Analytical queries
│
├── infrastructure/                  # Infrastructure configs
│   ├── lambda_execution_role_policy.json
│   └── trust-policy.json
│
├── tests/                           # Test files
│   └── test_lambda.py
│
├── docs/                            # Additional documentation
│
├── outputs/                         # Generated reports & charts
│   └── charts/                     # Visualization outputs
│
├── initialize_database.py          # Database setup script
├── verify_data.py                  # Data verification script
├── generate_report.py              # Generate visualizations & forecasts
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore
├── README.md                       # This file
├── USAGE_GUIDE.md                  # Usage instructions
├── PROJECT_SUMMARY.md              # Detailed documentation
├── QUICK_START.md                  # 10-minute setup guide
├── HOW_TO_USE.md                   # Simple usage reference
└── LICENSE
```

---

## 📊 Performance & Metrics

### Latest Execution Stats
- **Status**: ✅ Success
- **Records Processed**: 22 data points
- **Execution Time**: 1.58 seconds
- **Data Retrieved**:
  - Unemployment Rate: 4.4%
  - 10-Year Treasury: 19 daily observations
  - CPI, Fed Funds, GDP: Latest monthly/quarterly data

### Database Statistics
- **Total Indicators**: 5
- **Total Data Points**: 22+
- **Update Frequency**: Daily (automated)
- **Data Retention**: Unlimited

---

## 💰 Cost Breakdown

### Free Tier (First 12 months)
- **Lambda**: $0 (1M requests/month included)
- **S3**: $0 (5GB storage included)
- **RDS**: $0 (750 hours db.t3.micro included)
- **Total**: **$0/month** ✅

### After Free Tier
- **RDS db.t3.micro**: ~$15/month
- **S3 Storage**: <$1/month
- **Lambda Executions**: <$1/month
- **Total**: **~$17/month**

**Cost Optimization Tips:**
- Stop RDS when not in use: Save $15/month
- Delete old S3 data: Reduce storage costs
- Use RDS snapshots: Cheaper than running instance

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# FRED API Configuration
FRED_API_KEY=your_fred_api_key_here

# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET_NAME=economic-indicators-pipeline-your-initials

# Database Configuration
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_NAME=economic_indicators
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_PORT=5432
```

### Adding New Indicators

1. Add to database:
   ```sql
   INSERT INTO indicators (series_id, title, units, frequency, seasonal_adjustment)
   VALUES ('HOUST', 'Housing Starts', 'Thousands', 'Monthly', 'Seasonally Adjusted');
   ```

2. Update Lambda code:
   ```python
   # In lambda/lambda_function.py
   INDICATORS = ['UNRATE', 'CPIAUCSL', 'GDP', 'FEDFUNDS', 'DGS10', 'HOUST']
   ```

3. Redeploy Lambda function

---

## 🎓 Skills Demonstrated

### Cloud Engineering (AWS)
- ✅ Lambda serverless functions
- ✅ S3 object storage and lifecycle policies
- ✅ RDS managed PostgreSQL databases
- ✅ IAM roles and security policies
- ✅ CloudWatch Events scheduling
- ✅ CloudWatch Logs monitoring
- ✅ AWS CLI automation

### Data Engineering
- ✅ ETL pipeline architecture
- ✅ REST API integration (FRED)
- ✅ Data extraction and transformation
- ✅ Error handling and retry logic
- ✅ Data quality validation
- ✅ Automated scheduling
- ✅ Performance optimization

### Database (PostgreSQL)
- ✅ Schema design with normalization
- ✅ Indexing strategies
- ✅ UPSERT operations (INSERT ON CONFLICT)
- ✅ Complex analytical queries
- ✅ Window functions and CTEs
- ✅ Query optimization

### Python Development
- ✅ Object-oriented programming
- ✅ Modular architecture
- ✅ Exception handling
- ✅ Environment management
- ✅ Third-party integrations (boto3, psycopg2, requests)
- ✅ PEP 8 coding standards

---

## 🧪 Testing

### Run Tests Locally

```bash
# Activate environment
source venv/bin/activate

# Test Lambda function
python lambda/lambda_function.py

# Verify data loaded
python verify_data.py

# Run unit tests (if available)
pytest tests/
```

### Verify AWS Deployment

```bash
# Test Lambda in AWS
aws lambda invoke \
  --function-name economic-indicator-etl \
  --payload '{}' \
  response.json

# Check CloudWatch logs
# AWS Console → CloudWatch → Logs → /aws/lambda/economic-indicator-etl

# Verify data in RDS
python verify_data.py
```

---

## 📈 Sample Queries

### Get Latest Economic Snapshot

```sql
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

### Analyze Unemployment Trends

```sql
SELECT
    observation_date,
    value as unemployment_rate,
    AVG(value) OVER (
        ORDER BY observation_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as three_month_avg
FROM indicator_data
WHERE indicator_id = (
    SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE'
)
ORDER BY observation_date DESC
LIMIT 12;
```

More queries available in [`sql/sample_analysis.sql`](sql/sample_analysis.sql)

---

## 🛠️ Troubleshooting

### Common Issues

**Pipeline not running automatically:**
```bash
# Check CloudWatch Event Rule
aws events list-rules --name-prefix economic-indicator

# Verify Lambda has permission
aws lambda get-policy --function-name economic-indicator-etl
```

**Database connection failed:**
```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier economic-indicators-db \
  --query "DBInstances[0].DBInstanceStatus"

# Verify security group allows connection
```

**Lambda timeout:**
```bash
# Increase timeout to 600 seconds
aws lambda update-function-configuration \
  --function-name economic-indicator-etl \
  --timeout 600
```

See [USAGE_GUIDE.md](USAGE_GUIDE.md) for more troubleshooting tips.

---

## 🚀 Implemented Features & Future Enhancements

### ✅ Completed
- [x] Data visualization dashboard (matplotlib, Plotly)
- [x] Forecasting models (ARIMA, Prophet)
- [x] Interactive HTML dashboards
- [x] Automated report generation
- [x] Year-over-year analysis
- [x] Correlation analysis

### 🎯 Planned Enhancements
- [ ] Real-time Streamlit dashboard
- [ ] SNS alerts for pipeline failures
- [ ] REST API with API Gateway
- [ ] Add more economic indicators (Housing, Employment)
- [ ] Enhanced data quality checks
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Infrastructure as Code (Terraform)
- [ ] Comprehensive testing suite
- [ ] Jupyter notebook examples
- [ ] Email reports automation
- [ ] Machine learning anomaly detection

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Jason Finkle**

- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) for providing free economic data API
- [AWS Free Tier](https://aws.amazon.com/free/) for cloud infrastructure
- Inspired by real-world data engineering best practices

---

## 📚 Resources

- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/)

---

## ⭐ Star This Repository

If you found this project useful, please consider giving it a star! It helps others discover the project.

---

<div align="center">

**Built with ❤️ using AWS, Python, and PostgreSQL**

[Report Bug](https://github.com/yourusername/economic-indicator-pipeline/issues) · [Request Feature](https://github.com/yourusername/economic-indicator-pipeline/issues)

</div>
