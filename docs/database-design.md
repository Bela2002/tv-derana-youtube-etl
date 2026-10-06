# Database Design

## Database

Database name:

tv_derana_youtube

PostgreSQL is used as the local relational database.

## Table 1: videos

The `videos` table stores relatively stable metadata about each
YouTube video.

Important columns:

- video_id
- channel_id
- channel_title
- title
- description
- published_at
- duration

`video_id` is the primary key.

## Table 2: video_daily_stats

The `video_daily_stats` table stores daily snapshots of changing
YouTube statistics.

Important columns:

- video_id
- snapshot_date
- views
- likes
- comments

The combination of `video_id` and `snapshot_date` uniquely
identifies one daily snapshot.

This allows historical analysis instead of overwriting
previously collected statistics.

## Relationship

One video can have many daily statistic records.

videos (1) -------- (many) video_daily_stats