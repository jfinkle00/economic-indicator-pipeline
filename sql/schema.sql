-- Economic Indicators Database Schema
-- Drop existing tables if they exist
DROP TABLE IF EXISTS indicator_data;
DROP TABLE IF EXISTS indicators;
DROP TABLE IF EXISTS etl_logs;

-- Indicators metadata table
CREATE TABLE indicators (
    indicator_id SERIAL PRIMARY KEY,
    series_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    units VARCHAR(100),
    frequency VARCHAR(20),
    seasonal_adjustment VARCHAR(50),
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indicator data table
CREATE TABLE indicator_data (
    data_id SERIAL PRIMARY KEY,
    indicator_id INTEGER REFERENCES indicators(indicator_id),
    observation_date DATE NOT NULL,
    value DECIMAL(18, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(indicator_id, observation_date)
);

-- ETL logging table
CREATE TABLE etl_logs (
    log_id SERIAL PRIMARY KEY,
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    records_processed INTEGER,
    error_message TEXT,
    execution_time_seconds DECIMAL(10, 2)
);

-- Create indexes for better query performance
CREATE INDEX idx_observation_date ON indicator_data(observation_date);
CREATE INDEX idx_indicator_id ON indicator_data(indicator_id);
CREATE INDEX idx_series_id ON indicators(series_id);

-- Insert initial indicators
INSERT INTO indicators (series_id, title, units, frequency, seasonal_adjustment) VALUES
('UNRATE', 'Unemployment Rate', 'Percent', 'Monthly', 'Seasonally Adjusted'),
('CPIAUCSL', 'Consumer Price Index', 'Index 1982-1984=100', 'Monthly', 'Seasonally Adjusted'),
('GDP', 'Gross Domestic Product', 'Billions of Dollars', 'Quarterly', 'Seasonally Adjusted Annual Rate'),
('FEDFUNDS', 'Federal Funds Rate', 'Percent', 'Monthly', 'Not Seasonally Adjusted'),
('DGS10', '10-Year Treasury Rate', 'Percent', 'Daily', 'Not Applicable');

-- Verify setup
SELECT 'Schema created successfully!' AS status;
SELECT * FROM indicators;
