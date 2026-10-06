import psycopg2
from psycopg2.extensions import connection as PostgreSQLConnection

from src.config import Settings


CREATE_VIDEOS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS videos (
    video_id VARCHAR(20) PRIMARY KEY,
    channel_id VARCHAR(50),
    channel_title TEXT,
    title TEXT,
    description TEXT,
    published_at TIMESTAMPTZ,
    duration VARCHAR(50),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


CREATE_DAILY_STATS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS video_daily_stats (
    video_id VARCHAR(20) NOT NULL,
    snapshot_date DATE NOT NULL,

    views BIGINT,
    likes BIGINT,
    comments BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (video_id, snapshot_date),

    CONSTRAINT fk_video
        FOREIGN KEY (video_id)
        REFERENCES videos(video_id)
        ON DELETE CASCADE
);
"""


def get_database_connection(
    settings: Settings,
) -> PostgreSQLConnection:
    """
    Create and return a PostgreSQL database connection.
    """

    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


def initialize_database(
    connection: PostgreSQLConnection,
) -> None:
    """
    Create required database tables if they do not already exist.
    """

    with connection.cursor() as cursor:
        cursor.execute(CREATE_VIDEOS_TABLE_SQL)
        cursor.execute(CREATE_DAILY_STATS_TABLE_SQL)

    connection.commit()