# Testing

## Unit Tests

The project uses `pytest` to test individual components independently.

The unit tests cover:

- Configuration loading and validation.
- YouTube API response handling.
- API pagination and video-detail batching.
- Data transformation and missing-value handling.
- Database loading logic using mock database objects.
- Retry behaviour for selected temporary API failures.
- Avoiding exposure of sensitive information in custom API error messages.
- Avoiding unnecessary retries for permanent HTTP errors.

Mock responses are used for API unit tests to avoid unnecessary external API calls and quota consumption.

## Database Integration Tests

The project includes `tests/test_database_integration.py`, which uses a separate PostgreSQL database named `tv_derana_etl_test`.

The tests cover:

1. Database table initialization.
2. Updating an existing video through an upsert.
3. Inserting daily statistics.
4. Rejecting statistics for a nonexistent video.
5. Storing multiple snapshot dates for the same video.
6. Checking that a failed statistics batch does not leave partial rows committed.

These tests exercise actual PostgreSQL operations, including constraints and transaction behaviour, rather than relying only on mocked database objects.

The test database must be configured before running the integration tests. It should not silently fall back to the main project database.

## Running the Tests

Run the complete test suite from the project root:

```powershell
pytest -v
```

Run only the database integration tests:

```powershell
pytest -v tests/test_database_integration.py
```

The integration tests require a working PostgreSQL connection and the correct test database configuration.

## Manual End-to-End Testing

The complete ETL pipeline can be run using:

```powershell
python -m src.main
```

The following are verified during end-to-end execution:

1. Configuration loading.
2. YouTube API communication.
3. Video extraction.
4. Data transformation.
5. PostgreSQL connection.
6. Table initialization.
7. Video metadata loading.
8. Daily-statistics loading.
9. Duplicate handling.
10. Logging and execution completion.

## Duplicate Test

Running the ETL more than once on the same day should not create duplicate records for the same video and snapshot date.

The database uses `video_id` as the primary key for the `videos` table and `(video_id, snapshot_date)` as the composite primary key for `video_daily_stats`.

## Database Verification

The following SQL queries can be used to verify the stored data:

```sql
SELECT COUNT(*) FROM videos;

SELECT COUNT(*) FROM video_daily_stats;
```

To inspect recent daily snapshots:

```sql
SELECT video_id, snapshot_date, views, likes, comments
FROM video_daily_stats
ORDER BY snapshot_date DESC
LIMIT 20;
```

## Test Results

The complete test suite was executed using:

```powershell
pytest -v
```

The execution completed successfully with the following result:

```text
39 passed in 7.55s
```

All 39 tests passed, covering configuration, extraction, transformation, loading, API error handling and retries, main-pipeline orchestration, and PostgreSQL integration.

The database integration tests were run against the separate `tv_derana_etl_test` database.



