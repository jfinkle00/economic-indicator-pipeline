# SQL Scripts

This directory contains SQL scripts for database setup and analysis.

## Files

- `schema.sql` - Database schema and initial data setup
- `queries.sql` - Common analytical queries
- `sample_analysis.sql` - Example analytical queries for economic indicators

## Usage

To initialize the database:
```bash
psql -h <your-rds-endpoint> -U postgres -d economic_indicators -f schema.sql
```
