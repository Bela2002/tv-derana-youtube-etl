# ETL Workflow

## Overview

The project follows a three-stage ETL architecture:

Extract → Transform → Load

## 1. Extract

The extraction stage communicates with the YouTube Data API.

The channel ID is used to retrieve the channel's uploads playlist.
The uploads playlist is then paginated to retrieve video IDs.

The video IDs are processed in batches to retrieve video metadata
and statistics.

## 2. Transform

The raw API responses are converted into structured records.

The transformation process:

- Validates the video ID.
- Extracts video metadata.
- Converts YouTube timestamps into Python datetime values.
- Converts numeric statistics into integers.
- Handles missing values.
- Adds the ETL snapshot date.

## 3. Load

The transformed records are loaded into PostgreSQL.

Video metadata is stored in the `videos` table.

Daily statistics are stored in the `video_daily_stats` table.

## 4. Historical Data

Daily statistics are not overwritten across different dates.

The combination of:

video_id + snapshot_date

uniquely identifies a daily snapshot.

## Overall Flow

YouTube API
    ↓
Extract
    ↓
Transform
    ↓
Validate
    ↓
PostgreSQL
    ↓
Historical daily data