-- Economic Indicators Analysis Queries
-- Sample queries for analyzing economic indicator data

-- =====================================================
-- 1. Latest values for all indicators
-- =====================================================
SELECT
    i.series_id,
    i.title,
    d.observation_date,
    d.value,
    i.units
FROM indicators i
LEFT JOIN LATERAL (
    SELECT observation_date, value
    FROM indicator_data
    WHERE indicator_id = i.indicator_id
    ORDER BY observation_date DESC
    LIMIT 1
) d ON true
ORDER BY i.series_id;

-- =====================================================
-- 2. Year-over-year change in unemployment
-- =====================================================
WITH current_data AS (
    SELECT
        observation_date,
        value as current_value,
        LAG(value, 12) OVER (ORDER BY observation_date) as year_ago_value
    FROM indicator_data
    WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
)
SELECT
    observation_date,
    current_value,
    year_ago_value,
    ROUND((current_value - year_ago_value)::numeric, 2) as yoy_change,
    ROUND(((current_value - year_ago_value) / year_ago_value * 100)::numeric, 2) as yoy_pct_change
FROM current_data
WHERE year_ago_value IS NOT NULL
ORDER BY observation_date DESC
LIMIT 12;

-- =====================================================
-- 3. Correlation between unemployment and GDP
-- =====================================================
WITH unemployment AS (
    SELECT
        DATE_TRUNC('quarter', observation_date) as quarter,
        AVG(value) as avg_unemployment
    FROM indicator_data
    WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
    GROUP BY DATE_TRUNC('quarter', observation_date)
),
gdp AS (
    SELECT
        DATE_TRUNC('quarter', observation_date) as quarter,
        value as gdp_value
    FROM indicator_data
    WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'GDP')
)
SELECT
    u.quarter,
    u.avg_unemployment,
    g.gdp_value,
    CORR(u.avg_unemployment, g.gdp_value) OVER (
        ORDER BY u.quarter
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) as rolling_correlation
FROM unemployment u
JOIN gdp g ON u.quarter = g.quarter
ORDER BY u.quarter DESC
LIMIT 20;

-- =====================================================
-- 4. ETL pipeline performance metrics
-- =====================================================
SELECT
    DATE(run_timestamp) as run_date,
    status,
    COUNT(*) as runs,
    AVG(records_processed) as avg_records,
    AVG(execution_time_seconds) as avg_execution_time,
    MAX(execution_time_seconds) as max_execution_time
FROM etl_logs
GROUP BY DATE(run_timestamp), status
ORDER BY run_date DESC;

-- =====================================================
-- 5. 10-Year Treasury Rate trends (last 30 days)
-- =====================================================
SELECT
    observation_date,
    value as treasury_rate,
    AVG(value) OVER (ORDER BY observation_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7day
FROM indicator_data
WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'DGS10')
ORDER BY observation_date DESC
LIMIT 30;

-- =====================================================
-- 6. Federal Funds Rate vs CPI (Inflation)
-- =====================================================
WITH fed_funds AS (
    SELECT
        DATE_TRUNC('month', observation_date) as month,
        AVG(value) as avg_fed_rate
    FROM indicator_data
    WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'FEDFUNDS')
    GROUP BY DATE_TRUNC('month', observation_date)
),
cpi AS (
    SELECT
        DATE_TRUNC('month', observation_date) as month,
        value as cpi_value
    FROM indicator_data
    WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'CPIAUCSL')
)
SELECT
    f.month,
    f.avg_fed_rate,
    c.cpi_value,
    ROUND((c.cpi_value - LAG(c.cpi_value, 12) OVER (ORDER BY f.month)) /
          LAG(c.cpi_value, 12) OVER (ORDER BY f.month) * 100, 2) as yoy_inflation
FROM fed_funds f
JOIN cpi c ON f.month = c.month
ORDER BY f.month DESC
LIMIT 24;

-- =====================================================
-- 7. Data completeness check
-- =====================================================
SELECT
    i.series_id,
    i.title,
    COUNT(d.data_id) as total_records,
    MIN(d.observation_date) as earliest_date,
    MAX(d.observation_date) as latest_date,
    MAX(i.last_updated) as last_updated
FROM indicators i
LEFT JOIN indicator_data d ON i.indicator_id = d.indicator_id
GROUP BY i.series_id, i.title, i.last_updated
ORDER BY i.series_id;

-- =====================================================
-- 8. Recent economic snapshot
-- =====================================================
SELECT
    'Unemployment Rate' as indicator,
    CONCAT(value, '%') as current_value,
    observation_date as as_of_date
FROM indicator_data
WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'UNRATE')
ORDER BY observation_date DESC
LIMIT 1

UNION ALL

SELECT
    'Federal Funds Rate' as indicator,
    CONCAT(value, '%') as current_value,
    observation_date as as_of_date
FROM indicator_data
WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'FEDFUNDS')
ORDER BY observation_date DESC
LIMIT 1

UNION ALL

SELECT
    '10-Year Treasury' as indicator,
    CONCAT(value, '%') as current_value,
    observation_date as as_of_date
FROM indicator_data
WHERE indicator_id = (SELECT indicator_id FROM indicators WHERE series_id = 'DGS10')
ORDER BY observation_date DESC
LIMIT 1;
