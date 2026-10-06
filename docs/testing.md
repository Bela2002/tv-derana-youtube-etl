# Testing

## Unit Tests

The project uses pytest.

The transformation layer is tested independently.

Tests cover:

- valid integer conversion
- invalid integer conversion
- missing values
- YouTube timestamp conversion
- transformation of video records

## Manual Integration Testing

The complete ETL pipeline is tested using:

python -m src.main

The following are verified:

1. YouTube API connection.
2. Video extraction.
3. Data transformation.
4. PostgreSQL connection.
5. Table creation.
6. Data insertion.
7. Duplicate handling.
8. Logging.

## Duplicate Test

Running the ETL more than once on the same day should not
create duplicate records for the same video and snapshot date.

## Database Verification

The following SQL queries are used to verify loaded data:

SELECT COUNT(*) FROM videos;

SELECT COUNT(*) FROM video_daily_stats;