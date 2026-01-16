# Visualization & Forecasting Guide 📊🔮

Complete guide to generating visualizations and forecasts for your economic indicator data.

---

## Quick Start

### Generate Full Report

```bash
cd economic-indicator-pipeline
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install visualization dependencies
pip install pandas matplotlib plotly seaborn statsmodels prophet numpy scipy

# Generate report
python generate_report.py --full
```

**Output**: All charts saved to `outputs/charts/`

---

## Available Visualizations

### 1. Multi-Indicator Dashboard
**File**: `multi_indicator_dashboard.png`

Shows all economic indicators in a single view with stacked time series plots.

**When to use**: Quick overview of all indicators

### 2. Interactive Dashboard
**File**: `interactive_dashboard.html`

Plotly-based interactive dashboard. Open in browser for:
- Hover for exact values
- Zoom and pan
- Toggle indicators on/off

**To view**:
```bash
# Open in default browser
open outputs/charts/interactive_dashboard.html  # Mac
start outputs/charts/interactive_dashboard.html  # Windows
xdg-open outputs/charts/interactive_dashboard.html  # Linux
```

### 3. Individual Time Series
**Files**: `unemployment_rate_timeseries.png`, etc.

High-resolution plots for each indicator showing:
- Historical values
- Trend lines
- Date-formatted x-axis

**When to use**: Presentations, reports, publications

### 4. Year-over-Year Change
**Files**: `unemployment_rate_yoy_change.png`, etc.

Bar charts showing percentage change from same month last year.
- Green bars = increase
- Red bars = decrease

**When to use**: Analyzing growth rates and trends

### 5. Correlation Heatmap
**File**: `correlation_heatmap.png`

Shows relationships between economic indicators.
- Red = positive correlation
- Blue = negative correlation
- Numbers show correlation coefficient (-1 to 1)

**When to use**: Understanding indicator relationships

### 6. Forecast Charts
**Files**: `unemployment_rate_forecast.png`, etc.

Shows:
- Historical data (blue line)
- 12-month forecast (orange dashed line)
- 95% confidence interval (shaded area)

**When to use**: Predicting future trends

---

## Forecasting Methods

### ARIMA (AutoRegressive Integrated Moving Average)

**Best for**: Short to medium-term forecasts, stable trends

**How it works**:
- Analyzes historical patterns
- Models trend, seasonality, and random fluctuations
- Provides statistical confidence intervals

**Example**:
```python
from forecasting.models import EconomicForecaster
import pandas as pd

# Load data
df = pd.read_sql("SELECT observation_date, value FROM indicator_data WHERE ...", conn)

# Fit model
forecaster = EconomicForecaster()
forecaster.fit_arima(df, order=(1, 1, 1))

# Generate forecast
forecast_df = forecaster.forecast_arima(steps=12)

print(forecast_df)
# Output:
#         date  forecast    lower    upper
# 0 2026-02-01      4.42     3.95     4.89
# 1 2026-03-01      4.44     3.87     5.01
# ...
```

### Prophet (Facebook Prophet)

**Best for**: Long-term forecasts, complex seasonality

**How it works**:
- Handles multiple seasonal patterns
- Robust to missing data
- Captures holiday effects

**Example**:
```python
# Fit Prophet model
forecaster.fit_prophet(df, yearly_seasonality=True)

# Generate forecast
forecast_df = forecaster.forecast_prophet(periods=12, freq='MS')
```

### Auto-ARIMA

**Best for**: When you don't know optimal parameters

**How it works**:
- Tests multiple parameter combinations
- Selects best model using AIC (Akaike Information Criterion)

**Example**:
```python
# Automatically find best ARIMA order
best_order, model = forecaster.auto_arima(df, max_p=5, max_d=2, max_q=5)
print(f"Best order: {best_order}")  # e.g., (2, 1, 1)
```

---

## Customizing Visualizations

### Using Python API

```python
from visualizations.charts import EconomicCharts
import pandas as pd
import psycopg2

# Connect to database
conn = psycopg2.connect(...)

# Fetch data
df = pd.read_sql("""
    SELECT observation_date, value
    FROM indicator_data
    WHERE indicator_id = 1
    ORDER BY observation_date
""", conn)

# Initialize chart generator
charts = EconomicCharts(output_dir='my_custom_charts')

# Generate time series plot
charts.plot_time_series(
    df,
    indicator_name='Unemployment Rate',
    title='US Unemployment Rate - Custom Title',
    save=True
)

# Don't save, just display
charts.plot_time_series(df, 'Unemployment Rate', save=False)
```

### Create Custom Multi-Indicator Plot

```python
# Fetch multiple indicators
indicators = {
    'Unemployment': df_unemployment,
    'Inflation': df_inflation,
    'GDP Growth': df_gdp
}

# Create dashboard
charts.plot_multiple_indicators(
    indicators,
    title="My Custom Economic Dashboard"
)
```

### Interactive Plot with Custom Data

```python
# Create interactive Plotly dashboard
charts.plot_interactive_dashboard(
    indicators,
    save=True  # Saves as HTML
)
```

---

## Advanced Forecasting

### Backtesting

Test your model on historical data:

```python
forecaster = EconomicForecaster()
forecaster.fit_arima(df)

# Test on last 20% of data
metrics = forecaster.backtest(df, train_size=0.8, steps=12)

print(f"MAPE: {metrics['mape']:.2f}%")
print(f"MAE: {metrics['mae']:.2f}")
print(f"RMSE: {metrics['rmse']:.2f}")
```

**Metrics explained**:
- **MAPE** (Mean Absolute Percentage Error): Average error as percentage
- **MAE** (Mean Absolute Error): Average difference between actual and forecast
- **RMSE** (Root Mean Square Error): Penalizes large errors more

### Checking Stationarity

Before ARIMA, check if data is stationary:

```python
result = forecaster.check_stationarity(df['value'])

if result['is_stationary']:
    print("Data is stationary - good for ARIMA!")
else:
    print(f"Data not stationary (p-value: {result['p_value']:.4f})")
    print("Consider differencing (increase d parameter)")
```

### Seasonal ARIMA (SARIMA)

For data with seasonal patterns:

```python
# Seasonal ARIMA with yearly seasonality
forecaster.fit_arima(
    df,
    order=(1, 1, 1),           # Non-seasonal: (p, d, q)
    seasonal_order=(1, 1, 1, 12)  # Seasonal: (P, D, Q, s) where s=12 months
)

forecast_df = forecaster.forecast_arima(steps=24)  # 2-year forecast
```

---

## Report Scheduling

### Automate Weekly Reports

Create `generate_weekly_report.sh`:

```bash
#!/bin/bash
cd /path/to/economic-indicator-pipeline
source venv/bin/activate
python generate_report.py --full
# Optionally email the results
```

**Schedule with cron** (Linux/Mac):
```bash
# Run every Monday at 9 AM
0 9 * * 1 /path/to/generate_weekly_report.sh
```

**Schedule with Task Scheduler** (Windows):
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly, Monday, 9:00 AM
4. Action: Start program `python.exe`
5. Arguments: `generate_report.py --full`
6. Start in: `C:\path\to\economic-indicator-pipeline`

---

## Exporting Data

### Export Forecast to CSV

```python
forecast_df = forecaster.forecast_arima(steps=12)
forecast_df.to_csv('outputs/unemployment_forecast.csv', index=False)
```

### Export All Charts to PDF

```bash
# Install img2pdf
pip install img2pdf

# Convert all PNGs to single PDF
python -c "
import img2pdf
import os

images = [f'outputs/charts/{f}' for f in os.listdir('outputs/charts') if f.endswith('.png')]
with open('economic_report.pdf', 'wb') as f:
    f.write(img2pdf.convert(images))
"
```

---

## Troubleshooting

### Issue: "prophet not installed"

```bash
pip install prophet

# If that fails on Windows:
conda install -c conda-forge prophet
```

### Issue: Charts look pixelated

Increase DPI in `charts.py`:
```python
plt.savefig(filepath, dpi=600)  # Higher resolution
```

### Issue: Forecast has huge confidence intervals

This indicates:
1. Not enough historical data
2. High volatility in the data
3. Model may not be appropriate

**Solutions**:
- Collect more historical data
- Try different ARIMA orders
- Use Prophet instead
- Consider data transformation (log, sqrt)

### Issue: "No data available" for indicator

Check database:
```sql
SELECT COUNT(*) FROM indicator_data
WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE');
```

If 0 records:
1. Run ETL pipeline: `python lambda/lambda_function.py`
2. Check if FRED has data for that indicator
3. Verify indicator is in `INDICATORS` list

---

## Best Practices

### 1. Regular Updates
- Run `generate_report.py` weekly
- Track forecast accuracy over time
- Adjust models as needed

### 2. Model Selection
- **Monthly data**: Use ARIMA with order (1,1,1) or (2,1,2)
- **High seasonality**: Use SARIMA or Prophet
- **Volatile data**: Use larger confidence intervals

### 3. Data Requirements
- **Minimum**: 24 observations for basic forecast
- **Recommended**: 36+ observations for reliable forecasts
- **Ideal**: 60+ observations for seasonal models

### 4. Interpretation
- Always show confidence intervals
- Don't forecast too far ahead (max 12-24 periods)
- Update forecasts monthly as new data arrives
- Document assumptions and limitations

---

## Sample Outputs

### Unemployment Rate Forecast

```
ARIMA(1,1,1) Model:
Next 12 months forecast:

2026-02: 4.42% (95% CI: 3.95% - 4.89%)
2026-03: 4.44% (95% CI: 3.87% - 5.01%)
2026-04: 4.46% (95% CI: 3.81% - 5.11%)
2026-05: 4.48% (95% CI: 3.76% - 5.20%)
...

Interpretation:
- Unemployment expected to remain stable around 4.4%
- Low confidence in later months (wider intervals)
- Model suggests slight upward trend
```

### Correlation Analysis

```
Economic Indicator Correlations:

                    UNRATE  CPIAUCSL    GDP  FEDFUNDS  DGS10
UNRATE                1.00     -0.23  -0.45     -0.12   0.15
CPIAUCSL            -0.23      1.00   0.67      0.89   0.72
GDP                 -0.45      0.67   1.00      0.45   0.34
FEDFUNDS            -0.12      0.89   0.45      1.00   0.91
DGS10                0.15      0.72   0.34      0.91   1.00

Key Insights:
- Strong positive correlation between CPI and Fed Funds Rate (0.89)
- Negative correlation between unemployment and GDP (-0.45)
- Treasury rates closely follow Fed Funds Rate (0.91)
```

---

## Resources

- **statsmodels docs**: https://www.statsmodels.org/
- **Prophet docs**: https://facebook.github.io/prophet/
- **matplotlib gallery**: https://matplotlib.org/stable/gallery/
- **Plotly examples**: https://plotly.com/python/

---

**Last Updated**: January 16, 2026
