# TV Derana YouTube ETL — Development Log

## 1. Project Information

**Project:** TV Derana YouTube Data ETL Pipeline
**Project Type:** Data Engineering / Data Analysis Task
**Data Source:** YouTube Data API v3
**Target Database:** Local PostgreSQL
**Programming Language:** Python
**Automation:** Windows Task Scheduler
**Repository:** GitHub

---

## 2. Purpose of This Document

This document records the development progress of the TV Derana YouTube ETL project.

It is maintained throughout development to document:

* What was planned
* What was implemented
* Technical decisions made
* Challenges and design considerations encountered
* Solutions applied
* Testing and validation performed
* Current project status
* Future improvements and remaining work

This document will be updated whenever a meaningful development activity, technical decision, challenge, or improvement occurs.

---

# 3. Initial Project Plan

The initial objective was to develop a Python-based ETL pipeline that automatically retrieves TV Derana YouTube channel data and stores it in a local PostgreSQL database.

The planned workflow was:

```text
YouTube Data API
       ↓
Python Extraction
       ↓
Data Transformation
       ↓
PostgreSQL Loading
       ↓
Daily Historical Statistics
       ↓
Automated Daily Execution
```

The main requirements identified at the beginning were:

1. Retrieve TV Derana YouTube video information.
2. Retrieve video statistics such as views, likes, and comments.
3. Transform the API response into a database-friendly structure.
4. Store video metadata in PostgreSQL.
5. Store daily statistics separately so historical changes can be tracked.
6. Prevent duplicate database records.
7. Secure API and database credentials.
8. Test the individual components.
9. Automate the ETL process to run daily.
10. Maintain documentation throughout development.

---

# 4. Technology Stack

| Component               | Technology             |
| ----------------------- | ---------------------- |
| Programming Language    | Python                 |
| API                     | YouTube Data API v3    |
| HTTP Client             | Requests               |
| Database                | PostgreSQL             |
| Database Driver         | psycopg2               |
| Configuration           | python-dotenv          |
| Testing                 | pytest                 |
| Version Control         | Git / GitHub           |
| Automation              | Windows Task Scheduler |
| Execution Script        | Windows Batch Script   |
| Development Environment | VS Code                |
| Virtual Environment     | Python `.venv`         |

---

# 5. Project Structure

The project was organized into separate modules according to their responsibilities.

```text
tv-derana-youtube-etl/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── run_etl.bat
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── extract.py
│   ├── load.py
│   ├── logger.py
│   ├── main.py
│   ├── transform.py
│   └── youtube_api.py
│
├── tests/
│   ├── test_config.py
│   ├── test_extract.py
│   ├── test_load.py
│   ├── test_transform.py
│   └── test_youtube_api.py
│
├── logs/
│   └── etl.log
│
└── docs/
    └── DEVELOPMENT_LOG.md
```

The separation of modules was used to keep API communication, extraction, transformation, database operations, configuration, logging, and orchestration independent from one another.

---

# 6. Development Progress

## 6.1 Project Environment Setup

### Planned

Set up a Python development environment with a dedicated virtual environment and install the required dependencies.

### Completed

A Python virtual environment was created using `.venv`.

The required Python libraries were installed, including:

* `requests`
* `psycopg2`
* `python-dotenv`
* `pytest`

The project was configured to run from VS Code using the virtual environment.

### Result

The project can be executed in an isolated Python environment without depending on globally installed packages.

---

# 6.2 Secure Configuration Management

### Planned

API credentials and database credentials should not be hardcoded in Python source files or committed to GitHub.

### Design Consideration

The YouTube API key and PostgreSQL password are sensitive configuration values. Hardcoding these values would make the project less secure and could accidentally expose credentials through version control.

### Solution

Environment variables were used through a `.env` file.

The Python project uses `python-dotenv` to load the values and a centralized `Settings` dataclass to provide configuration to the application.

The `.gitignore` file prevents `.env` from being committed.

A `.env.example` file is maintained with placeholder values so that the required configuration structure can be understood without exposing real credentials.

### Result

Sensitive credentials are kept outside the source code and are not required to be stored in the GitHub repository.

---

# 6.3 YouTube API Integration

### Planned

Connect the Python application to the YouTube Data API v3 and retrieve TV Derana channel videos.

### Implementation

A dedicated `youtube_api.py` module was created to handle communication with the YouTube Data API v3.

The API client is responsible for:

1. Communicating with the YouTube API.
2. Adding the API key to requests through environment-based configuration.
3. Retrieving the channel's uploads playlist.
4. Retrieving video IDs from the uploads playlist.
5. Handling API pagination.
6. Retrieving detailed video information.
7. Handling HTTP, network, and invalid JSON errors.
8. Retrying temporary network failures and selected HTTP errors.
9. Raising custom API errors without including the raw request URL or response body in error messages.

### Retry Mechanism

The API client was improved to retry temporary request failures.

The implementation uses a maximum of three retries after the initial attempt, with exponential delays of approximately 1, 2, and 4 seconds. Retryable HTTP status codes are `429`, `500`, `502`, `503`, and `504`. Network-related request exceptions are also retried.

Permanent HTTP errors are not repeatedly retried. The current policy does not automatically retry every API error, including quota-related errors.

### API Key Error Handling

The error-handling logic was reviewed to reduce the risk of API-key exposure when requests fail. Custom error messages avoid including the raw request URL and response body, which may contain sensitive request details.

A dedicated test simulates a network exception containing a secret value and verifies that the value is not exposed in the resulting custom API error.

### API Batch Processing

Video details are requested in batches of up to 50 video IDs. This follows the API request structure and avoids sending unnecessarily large lists of IDs in a single request.

### Result

The API client now includes retry handling for selected temporary failures and tests for retry behaviour, permanent HTTP errors, and protection against exposing the API key in custom error messages.

---

# 6.4 Extraction Layer

### Planned

Create a separate extraction component responsible for defining what YouTube data should be retrieved.

### Implementation

The `extract.py` module coordinates the extraction process.

The extraction flow is:

```text
Channel ID
    ↓
Uploads Playlist ID
    ↓
Video IDs
    ↓
Video Details
    ↓
Raw YouTube Records
```

The extraction module does not directly implement HTTP requests. Instead, it uses the `YouTubeAPIClient`.

### Result

The extraction workflow is separated from the lower-level API communication logic.

---

# 6.5 Data Transformation

### Planned

Transform raw YouTube API responses into structures suitable for PostgreSQL.

### Implementation

The `transform.py` module was created to handle:

* Video ID validation
* Timestamp conversion
* Numeric conversion of statistics
* Metadata extraction
* Daily statistics extraction
* Invalid record handling

The raw YouTube API response is separated into two structures:

### Video Metadata

```text
video_id
channel_id
channel_title
title
description
published_at
duration
```

### Daily Statistics

```text
video_id
snapshot_date
views
likes
comments
```

### Result

The raw API response is converted into database-compatible records before loading.

---

# 6.6 PostgreSQL Database Design

### Planned

Store YouTube video information in PostgreSQL and preserve daily statistics for historical analysis.

### Implementation

Two tables were created.

### `videos`

Stores relatively stable information about each video.

```text
video_id
channel_id
channel_title
title
description
published_at
duration
updated_at
```

`video_id` is the primary key.

### `video_daily_stats`

Stores daily snapshots of video statistics.

```text
video_id
snapshot_date
views
likes
comments
created_at
```

The table uses:

```text
(video_id, snapshot_date)
```

as a composite primary key.

A foreign key connects `video_daily_stats.video_id` to `videos.video_id`.

### Reason for Separate Tables

Video metadata and changing statistics have different characteristics.

For example:

```text
Video title → usually remains unchanged
View count  → changes every day
Like count  → changes every day
```

Separating these allows historical statistics to be preserved without repeatedly duplicating the video metadata.

---

# 6.7 Duplicate Data Handling

### Design Consideration

Because the ETL pipeline is intended to run every day, the same videos will be encountered repeatedly.

Simply inserting every record could result in duplicate database records.

### Solution

PostgreSQL `ON CONFLICT` logic was used.

For the `videos` table:

```text
video_id
```

is used to identify an existing video.

For the `video_daily_stats` table:

```text
(video_id, snapshot_date)
```

is used to identify an existing daily snapshot.

The system therefore performs an upsert:

```text
If record does not exist
        ↓
Insert

If record already exists
        ↓
Update
```

### Result

Repeated ETL executions do not create duplicate video or same-day statistics records.

---

# 6.8 Database Loading

### Planned

Load transformed data into PostgreSQL.

### Implementation

The `load.py` module contains separate loading functions for:

* Video metadata
* Daily statistics

Database transactions are committed after the records are processed.

The database connection is created by `database.py` and passed to the loading functions.

### Result

The loading process is separated from extraction and transformation.

---

# 6.9 Logging

### Design Consideration

The ETL process will eventually run automatically through Windows Task Scheduler. In that situation, there may not be a visible VS Code terminal showing what happened.

A method was therefore required to record the execution status.

### Solution

A dedicated `logger.py` module was implemented.

The application writes logs to:

```text
logs/etl.log
```

The same messages are also displayed in the console when the ETL is run manually.

The logs include information such as:

```text
ETL started
Configuration loaded
Extraction started
Number of videos retrieved
Transformation completed
Database connection successful
Records loaded
ETL completed successfully
```

Errors are also recorded using exception logging.

### Result

ETL executions can be monitored and troubleshooting information can be reviewed later.

---

# 6.10 Main ETL Orchestration

### Planned

Create a single entry point that controls the complete ETL workflow.

### Implementation

`main.py` was created as the orchestration layer.

The current workflow is:

```text
Start
  ↓
Load configuration
  ↓
Create YouTube API client
  ↓
Extract YouTube data
  ↓
Transform data
  ↓
Connect to PostgreSQL
  ↓
Initialize database tables
  ↓
Load video metadata
  ↓
Load daily statistics
  ↓
Close database connection
  ↓
Complete
```

Exception handling is used to log failures, and a `finally` block ensures that the PostgreSQL connection is closed.

### Result

The entire ETL pipeline can be started using:

```powershell
python -m src.main
```

---

# 6.11 Automated Execution

### Planned

The ETL process should execute automatically once per day without requiring manual execution from VS Code.

### Solution

A Windows batch file was created:

```text
run_etl.bat
```

The batch file:

1. Changes to the project directory.
2. Activates the virtual environment.
3. Executes `src.main`.
4. Checks the Python exit status.
5. Reports whether the ETL completed successfully.

Windows Task Scheduler was then configured to execute the batch file daily at 8:00 AM.

### Result

The ETL pipeline can operate as a scheduled daily process instead of requiring manual execution.

---

# 7. Challenges and Solutions

The following items represent genuine implementation challenges or design considerations encountered during development.

## 7.1 Secure Handling of Credentials

### Challenge

The project requires a YouTube API key and PostgreSQL credentials. Storing these directly in source code would expose sensitive configuration.

### Solution

Environment variables were introduced using:

```text
.env
python-dotenv
.gitignore
```

A `.env.example` file was also created with placeholder values.

### Outcome

Credentials are separated from the application source code and are excluded from Git version control.

### Additional Security Validation

The current log files were checked for an exact match of the configured API key, and no exact match was found. The Git index was also checked, and `.env` was not listed as a tracked file.

These checks provide evidence that the key was not found in the inspected logs and is not currently tracked in the Git index. They do not, by themselves, prove that the key has never appeared in previous Git history or other files. A separate history review is required before making that broader claim.


---

## 7.2 Testing External API Communication

### Challenge

Testing YouTube API functionality by calling the real API for every test would:

* Depend on an internet connection.
* Consume API quota.
* Make tests slower.
* Make tests less predictable.

### Solution

`pytest` and `monkeypatch` were used to replace real HTTP requests with controlled fake responses during unit tests.

The tests simulate:

* Successful API responses
* Missing channels
* Pagination
* Maximum video limits
* API HTTP errors
* Network errors
* Invalid JSON responses

### Outcome

The YouTube API client can be tested without making real API requests.

---

## 7.3 Testing Database Loading Without Modifying the Real Database

### Challenge

Database loading code needs to be tested, but unit tests should not repeatedly insert or modify records in the actual PostgreSQL database.

### Solution

Fake database connection and cursor objects were created in the test suite.

These fake objects allow the tests to verify:

* SQL statements are executed.
* Correct parameters are passed.
* The expected number of records is processed.
* `commit()` is called.

### Outcome

Database loading logic can be tested safely without changing the production/local database.

---

## 7.4 Handling Repeated Daily ETL Runs

### Challenge

The same YouTube videos are expected to be retrieved repeatedly during daily ETL executions.

Without duplicate handling, the database could contain multiple copies of the same video.

### Solution

PostgreSQL primary keys and `ON CONFLICT` upsert operations were implemented.

### Outcome

Repeated executions can safely update existing records rather than creating duplicate records.

---

## 7.5 API Pagination and Request Limits

### Challenge

The YouTube API does not necessarily return all videos in a single response, and video details need to be requested in batches.

### Solution

The implementation:

* Uses `nextPageToken` for pagination.
* Retrieves video IDs page by page.
* Requests video details in groups of up to 50 IDs.

### Outcome

The extraction logic can handle more than a single page of YouTube videos.

---

## 7.6 Running the ETL Automatically

### Challenge

The ETL should run daily without requiring manual execution from the development environment.

### Solution

A Windows batch file was created and configured with Windows Task Scheduler.

### Outcome

The ETL pipeline is scheduled to run automatically at 8:00 AM each day.

---

## 7.7 Monitoring Automated Runs

### Challenge

A scheduled task may execute without an open VS Code terminal, making it difficult to know whether the ETL completed successfully.

### Solution

File-based logging was implemented using Python's `logging` module.

Execution details are written to:

```text
logs/etl.log
```

### Outcome

The execution history can be reviewed after an automated run.

## 7.8 Improving API Failure Recovery

### Challenge

A temporary network failure or server-side API error could interrupt an ETL execution. Because the pipeline is intended to collect data daily, repeated interruptions could affect collection reliability.

### Solution

A retry mechanism was added to `youtube_api.py`. It retries network-related request exceptions and selected temporary HTTP status codes, using exponential delays. Permanent HTTP errors are not repeatedly retried.

Automated tests were added to verify that temporary failures are retried, permanent HTTP errors are not unnecessarily retried, and sensitive information is not exposed through custom API error messages.

### Outcome

The API client has improved handling of selected temporary failures. Recovery is not guaranteed for permanent errors, quota issues, or failures outside the configured retry policy.

---

## 7.9 Testing Against a Real PostgreSQL Test Database

### Challenge

Mock database objects are useful for unit tests, but they cannot fully validate PostgreSQL behaviour, including actual table constraints, foreign keys, and transaction failures.

### Solution

A separate PostgreSQL database, `tv_derana_etl_test`, was created for database integration testing. A new test module, `tests/test_database_integration.py`, was added to exercise real database operations.

The integration tests cover:

- Database table initialization.
- Updating an existing video through an upsert.
- Inserting daily statistics.
- Rejecting statistics for a nonexistent video through the foreign-key constraint.
- Storing statistics for multiple snapshot dates for the same video.
- Verifying that a failed statistics batch does not leave partial rows committed.

The tests use dedicated test records and clean up test data where appropriate. They are configured to use the test database rather than the main database.

### Outcome

The new integration tests validate actual PostgreSQL behaviour instead of relying exclusively on mock database objects. Their final status should be recorded after the corrected test suite has been executed successfully.

---

## 8. Testing and Validation

Automated testing is implemented using `pytest`. The test suite includes unit tests, main-pipeline tests, and PostgreSQL database integration tests.

### Test Results

The complete test suite was executed successfully.

**Execution command:**

```powershell
pytest -v
```

**Result:**

```text
39 passed in 7.55s
```

All 39 tests passed without failures.

### Test Distribution

| Test File | Tests |
|---|---:|
| `test_config.py` | 7 |
| `test_database_integration.py` | 6 |
| `test_extract.py` | 2 |
| `test_load.py` | 4 |
| `test_main.py` | 4 |
| `test_transform.py` | 5 |
| `test_youtube_api.py` | 11 |
| **Total** | **39** |

### Tested Areas

The test suite validates:

- Configuration loading and validation.
- YouTube API pagination and video-detail batching.
- API HTTP errors, network errors, and invalid JSON responses.
- Retry handling for selected temporary API failures.
- Prevention of sensitive information appearing in custom API error messages.
- Avoiding unnecessary retries for permanent HTTP errors.
- Video extraction and empty extraction results.
- Data transformation and numeric/date conversion.
- Database loading operations.
- Main-pipeline success, empty extraction, extraction failure, and connection cleanup when loading fails.
- PostgreSQL table initialization, video upserts, daily-statistics upserts, foreign-key validation, multiple snapshot dates, and failed-batch transaction behaviour.

### Database Integration Testing

The six database integration tests use the separate PostgreSQL database `tv_derana_etl_test`. They verify actual PostgreSQL behaviour, including constraints and transaction handling, rather than relying exclusively on mocked database objects.

### Testing Principle

The project combines automated unit tests, main-pipeline tests, PostgreSQL integration tests, and manual end-to-end validation. Together, these approaches provide broader coverage of individual components, pipeline orchestration, and database behaviour.

---

# 9. End-to-End Validation

The ETL pipeline has also been executed manually using the actual project environment.

The validation confirmed that the application can:

1. Load configuration.
2. Connect to YouTube.
3. Retrieve YouTube video data.
4. Transform the retrieved data.
5. Connect to PostgreSQL.
6. Create the required database tables.
7. Load video metadata.
8. Load daily statistics.
9. Complete the ETL process successfully.

The scheduled execution was also configured and tested through Windows Task Scheduler.

---

# 10. Current Status

The following core components have been completed:

* [x] Python virtual environment
* [x] Project structure
* [x] YouTube API client
* [x] YouTube channel extraction
* [x] Pagination handling
* [x] Video detail retrieval
* [x] Data transformation
* [x] PostgreSQL connection
* [x] Database table creation
* [x] Video metadata loading
* [x] Daily statistics loading
* [x] Duplicate/upsert handling
* [x] Environment-based configuration
* [x] `.gitignore` security configuration
* [x] Logging
* [x] Error handling
* [x] Automated unit tests
* [x] Windows batch execution
* [x] Windows Task Scheduler configuration
* [x] Manual end-to-end validation
* [x] GitHub repository maintenance
* [x]Environment-based configuration
* [x] API error handling and retry mechanism for selected temporary failures
* [x] API-key exposure checks in current log files
* [x] Automated unit tests for API retry behaviour and safe custom errors
* [x] PostgreSQL test database created for integration testing
* [x] Database integration test module added

---

# 11. Current Operational Consideration

The `MAX_VIDEOS_PER_RUN` configuration was initially used during development to limit the number of videos processed during testing.

After successful testing, the limit was removed from the normal execution configuration so that the ETL can retrieve the complete available uploads playlist.

However, this means that each daily execution can traverse historical videos again.

Although database upserts prevent duplicate records, repeatedly processing the entire historical dataset may result in unnecessary API requests and processing time.

A possible future improvement is to introduce a more incremental extraction strategy that prioritizes newly published or recently changed videos while retaining the ability to perform historical backfills when required.

This is considered a future optimization rather than a current system failure.

---

# 12. Future Improvements

Potential improvements identified during development include:

# 12. Future Improvements

Potential improvements identified during development include:

1. Investigate the observed discrepancy between the playlist item count and the number of videos returned by the API.
2. Implement incremental extraction to reduce unnecessary API requests while retaining historical backfill capability.
3. Add dedicated automated tests for the complete main-pipeline orchestration.
4. Extend data-quality validation.
5. Improve monitoring of scheduled ETL runs and execution metrics.
6. Add automated database backup procedures if required.
7. Add data analysis and reporting capabilities using the collected historical statistics.
8. Review Git history and other relevant repository locations for any previous exposure of sensitive credentials.
9. Consider further improvements to API error classification and retry handling where appropriate.

---

The purpose of this document is to provide an accurate record of how the project evolved from the initial plan into the implemented system.
