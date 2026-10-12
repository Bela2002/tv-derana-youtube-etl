
import os

import psycopg2
import pytest
from dotenv import load_dotenv

from src.database import initialize_database
from src.load import load_daily_statistics, load_videos


load_dotenv()


@pytest.fixture
def test_db_connection():
    """Connect only to the dedicated PostgreSQL test database."""
    database_name = os.getenv("TEST_DB_NAME")

    if database_name != "tv_derana_etl_test":
        pytest.skip(
            "Configure TEST_DB_NAME=tv_derana_etl_test "
            "to enable PostgreSQL integration tests."
        )

    connection = psycopg2.connect(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=int(os.getenv("TEST_DB_PORT", "5432")),
        database=database_name,
        user=os.getenv("TEST_DB_USER"),
        password=os.getenv("TEST_DB_PASSWORD"),
    )

    try:
        initialize_database(connection)
        yield connection
    finally:
        # Ensure no unfinished transaction remains.
        connection.rollback()
        connection.close()


def make_video_record(video_id, title="Integration test video"):
    """Create a reusable test video record."""
    return {
        "video_id": video_id,
        "channel_id": "TEST_CHANNEL",
        "channel_title": "Test Channel",
        "title": title,
        "description": "Integration test",
        "published_at": None,
        "duration": "PT5M",
    }


def make_stats_record(video_id, snapshot_date, views=100):
    """Create a reusable daily statistics record."""
    return {
        "video_id": video_id,
        "snapshot_date": snapshot_date,
        "views": views,
        "likes": 10,
        "comments": 2,
    }


def delete_test_video(connection, video_id):
    """Delete a test video and its dependent statistics."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM videos WHERE video_id = %s",
                (video_id,),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def test_database_tables_can_be_initialized(test_db_connection):
    with test_db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('videos', 'video_daily_stats')
            """
        )
        tables = {row[0] for row in cursor.fetchall()}

    assert tables == {"videos", "video_daily_stats"}


def test_video_upsert_updates_existing_record(test_db_connection):
    video_id = "TEST_VIDEO_001"

    try:
        first_record = make_video_record(
            video_id,
            title="Original title",
        )
        updated_record = {
            **first_record,
            "title": "Updated title",
        }

        load_videos(test_db_connection, [first_record])
        load_videos(test_db_connection, [updated_record])

        with test_db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT title FROM videos WHERE video_id = %s",
                (video_id,),
            )
            result = cursor.fetchone()

        assert result == ("Updated title",)

    finally:
        delete_test_video(test_db_connection, video_id)


def test_daily_statistics_upsert(test_db_connection):
    video_id = "TEST_VIDEO_002"
    snapshot_date = "2026-10-11"

    try:
        load_videos(
            test_db_connection,
            [make_video_record(video_id, "Statistics test")],
        )

        first_stats = make_stats_record(
            video_id,
            snapshot_date,
            views=100,
        )
        updated_stats = {
            **first_stats,
            "views": 150,
        }

        load_daily_statistics(test_db_connection, [first_stats])
        load_daily_statistics(test_db_connection, [updated_stats])

        with test_db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT views, likes, comments
                FROM video_daily_stats
                WHERE video_id = %s AND snapshot_date = %s
                """,
                (video_id, snapshot_date),
            )
            result = cursor.fetchone()

        assert result == (150, 10, 2)

    finally:
        delete_test_video(test_db_connection, video_id)


def test_statistics_reject_nonexistent_video(test_db_connection):
    """The foreign key must reject statistics without a parent video."""
    missing_video_id = "MISSING_003"

    try:
        with pytest.raises(psycopg2.errors.ForeignKeyViolation):
            load_daily_statistics(
                test_db_connection,
                [make_stats_record(missing_video_id, "2026-10-11")],
            )
    finally:
        # PostgreSQL marks the transaction as failed after the FK error.
        test_db_connection.rollback()

    with test_db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM video_daily_stats
            WHERE video_id = %s
            """,
            (missing_video_id,),
        )
        count = cursor.fetchone()[0]

    assert count == 0


def test_video_can_have_multiple_snapshot_dates(test_db_connection):
    """One video should be allowed one statistics row per date."""
    video_id = "TEST_VIDEO_004"

    try:
        load_videos(
            test_db_connection,
            [make_video_record(video_id, "Multiple snapshots test")],
        )

        load_daily_statistics(
            test_db_connection,
            [
                make_stats_record(video_id, "2026-10-10", views=100),
                make_stats_record(video_id, "2026-10-11", views=150),
            ],
        )

        with test_db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT snapshot_date, views
                FROM video_daily_stats
                WHERE video_id = %s
                ORDER BY snapshot_date
                """,
                (video_id,),
            )
            rows = cursor.fetchall()

        assert len(rows) == 2
        assert [row[1] for row in rows] == [100, 150]

    finally:
        delete_test_video(test_db_connection, video_id)


def test_failed_statistics_batch_does_not_commit_partial_rows(
    test_db_connection,
):
    """
    A failed batch must not leave its earlier rows committed.

    The first record is valid; the second violates the foreign key.
    """
    video_id = "TEST_VIDEO_005"
    missing_video_id = "MISSING_005"
    snapshot_date = "2026-10-11"

    try:
        load_videos(
            test_db_connection,
            [make_video_record(video_id, "Transaction test")],
        )

        with pytest.raises(psycopg2.errors.ForeignKeyViolation):
            load_daily_statistics(
                test_db_connection,
                [
                    make_stats_record(
                        video_id,
                        snapshot_date,
                        views=100,
                    ),
                    make_stats_record(
                        missing_video_id,
                        snapshot_date,
                        views=200,
                    ),
                ],
            )

        # Recover from the failed transaction before querying.
        test_db_connection.rollback()

        with test_db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM video_daily_stats
                WHERE video_id = %s AND snapshot_date = %s
                """,
                (video_id, snapshot_date),
            )
            count = cursor.fetchone()[0]

        assert count == 0

        # Confirm the connection can execute queries again.
        with test_db_connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone() == (1,)

    finally:
        test_db_connection.rollback()
        delete_test_video(test_db_connection, video_id)
