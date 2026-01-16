-- Common queries for Economic Indicator Database

-- View all indicators
SELECT * FROM indicators ORDER BY series_id;

-- View all data for a specific indicator
SELECT
    i.series_id,
    i.title,
    d.observation_date,
    d.value
FROM indicators i
JOIN indicator_data d ON i.indicator_id = d.indicator_id
WHERE i.series_id = 'UNRATE'
ORDER BY d.observation_date DESC;

-- Get record counts by indicator
SELECT
    i.series_id,
    i.title,
    COUNT(d.data_id) as record_count
FROM indicators i
LEFT JOIN indicator_data d ON i.indicator_id = d.indicator_id
GROUP BY i.series_id, i.title
ORDER BY i.series_id;

-- View ETL execution logs
SELECT
    run_timestamp,
    status,
    records_processed,
    execution_time_seconds,
    error_message
FROM etl_logs
ORDER BY run_timestamp DESC
LIMIT 10;

-- Get latest data point for each indicator
SELECT
    i.series_id,
    i.title,
    MAX(d.observation_date) as latest_date,
    (SELECT value
     FROM indicator_data
     WHERE indicator_id = i.indicator_id
     ORDER BY observation_date DESC
     LIMIT 1) as latest_value
FROM indicators i
LEFT JOIN indicator_data d ON i.indicator_id = d.indicator_id
GROUP BY i.series_id, i.title, i.indicator_id
ORDER BY i.series_id;
