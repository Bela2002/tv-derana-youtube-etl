# TV Derana YouTube ETL

A Python-based ETL pipeline that retrieves TV Derana YouTube
video data using the YouTube Data API and stores historical
daily statistics in PostgreSQL.

## Objective

The objective is to create a secure and maintainable ETL
process for collecting TV Derana YouTube data on a daily basis.

## Technologies

- Python
- YouTube Data API v3
- PostgreSQL
- Git
- GitHub
- pytest
- Windows Task Scheduler

## Architecture

YouTube Data API
        ↓
    Extract
        ↓
    Transform
        ↓
      Load
        ↓
   PostgreSQL

## Features

- YouTube API integration
- Pagination handling
- Batch video retrieval
- Data transformation
- Data validation
- Historical daily snapshots
- PostgreSQL storage
- Duplicate prevention
- Logging
- Error handling
- Secure environment variables
- Automated daily execution
- Unit tests

## Project Structure

```text
src/
    config.py
    logger.py
    youtube_api.py
    extract.py
    transform.py
    database.py
    load.py
    main.py

tests/
docs/
logs/
```
## Setup

1. Clone the repository

```
git clone https://github.com/Bela2002/tv-derana-youtube-etl.git
cd tv-derana-youtube-etl
```

2. Create virtual environment

```
python -m venv .venv
```

   - Activate it on Windows:

   ```
   .venv\Scripts\activate
   ```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Configure environment variables
   
   Create  `.env` from `.env.example`.
  
   Add:

    - YouTube API key
    - YouTube channel ID
    - PostgreSQL credentials

   Never commit `.env`.

5. Create PostgreSQL database
  
   Create:

   ```
   tv_derana_youtube
   ```

   The application creates the required tables automatically.

6. Run

```
python -m src.main
```

7. Run tests

```
pytest
```
## Security

API keys and database passwords are stored in `.env`.

The `.env` file is excluded from GitHub using `.gitignore`.

## Daily Execution

The pipeline can be executed daily using Windows Task Scheduler and the provided `run_etl.bat` script.

## Historical Data

Daily YouTube statistics are stored using:

```
video_id + snapshot_date
```

This allows changes in views, likes and comments to be analysed over time.

## Execution Evidence

The ETL pipeline was tested through both manual and scheduled execution.

### Manual Execution
- Python ETL executed successfully through the VS Code terminal.
- Extracted YouTube data was transformed and loaded into PostgreSQL.

<img width="747" height="478" alt="01_manual_etl_run (MAX_VIDEOS_PER_RUN=100)" src="https://github.com/user-attachments/assets/8ab7dde7-30c4-47ed-b603-103c9fba0885" />

<img width="767" height="427" alt="06_manual_etl_run (MAX_VIDEOS_PER_RUN=)" src="https://github.com/user-attachments/assets/29d82a7c-d41a-4df8-85f0-667674aa12d3" />

### Database Validation
- PostgreSQL queries were used to verify the number of records and stored video data.

<img width="1790" height="947" alt="database_video_count" src="https://github.com/user-attachments/assets/2b4967c3-fedf-4a28-b337-c09df3983be3" />

<img width="1782" height="941" alt="database_video_data" src="https://github.com/user-attachments/assets/102e6784-911f-415c-b520-d3910fa0da3c" />

<img width="1792" height="945" alt="daily_stats_query" src="https://github.com/user-attachments/assets/70d31bad-1eb5-4162-b2ef-d802680d38bd" />

<img width="1793" height="942" alt="daily_stats_data" src="https://github.com/user-attachments/assets/892767ca-6f06-4a53-9be0-e52d6d7ebd15" />

### Automated Execution
- Windows Task Scheduler was configured to execute the ETL pipeline daily at 8:00 AM.

<img width="857" height="607" alt="05_task_scheduler_configuration" src="https://github.com/user-attachments/assets/c148c54a-27bd-4f7e-864d-d20bec0a281a" />
