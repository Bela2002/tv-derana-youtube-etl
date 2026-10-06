from typing import Any

from psycopg2.extensions import connection as PostgreSQLConnection


UPSERT_VIDEO_SQL = """
INSERT INTO videos (
    video_id,
    channel_id,
    channel_title,
    title,
    description,
    published_at,
    duration
)
VALUES (
    %(video_id)s,
    %(channel_id)s,
    %(channel_title)s,
    %(title)s,
    %(description)s,
    %(published_at)s,
    %(duration)s
)
ON CONFLICT (video_id)
DO UPDATE SET
    channel_id = EXCLUDED.channel_id,
    channel_title = EXCLUDED.channel_title,
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    published_at = EXCLUDED.published_at,
    duration = EXCLUDED.duration,
    updated_at = CURRENT_TIMESTAMP;
"""


INSERT_DAILY_STATS_SQL = """
INSERT INTO video_daily_stats (
    video_id,
    snapshot_date,
    views,
    likes,
    comments
)
VALUES (
    %(video_id)s,
    %(snapshot_date)s,
    %(views)s,
    %(likes)s,
    %(comments)s
)
ON CONFLICT (video_id, snapshot_date)
DO UPDATE SET
    views = EXCLUDED.views,
    likes = EXCLUDED.likes,
    comments = EXCLUDED.comments;
"""


def load_videos(
    connection: PostgreSQLConnection,
    video_records: list[dict[str, Any]],
) -> int:
    """
    Insert or update video metadata.

    Returns:
        Number of processed records.
    """

    with connection.cursor() as cursor:
        for record in video_records:
            cursor.execute(
                UPSERT_VIDEO_SQL,
                record,
            )

    connection.commit()

    return len(video_records)


def load_daily_statistics(
    connection: PostgreSQLConnection,
    statistics_records: list[dict[str, Any]],
) -> int:
    """
    Insert or update daily statistics.

    Returns:
        Number of processed records.
    """

    with connection.cursor() as cursor:
        for record in statistics_records:
            cursor.execute(
                INSERT_DAILY_STATS_SQL,
                record,
            )

    connection.commit()

    return len(statistics_records)