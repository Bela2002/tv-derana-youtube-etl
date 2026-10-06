from src.load import (
    INSERT_DAILY_STATS_SQL,
    UPSERT_VIDEO_SQL,
    load_daily_statistics,
    load_videos,
)


class FakeCursor:
    """Fake database cursor for testing SQL execution."""

    def __init__(self):
        self.executed_statements = []

    def execute(self, sql, parameters):
        self.executed_statements.append(
            (sql, parameters)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeConnection:
    """Fake database connection for testing database loading."""

    def __init__(self):
        self.cursor_object = FakeCursor()
        self.commit_called = False

    def cursor(self):
        return self.cursor_object

    def commit(self):
        self.commit_called = True


def test_load_videos():
    connection = FakeConnection()

    video_records = [
        {
            "video_id": "VIDEO_1",
            "channel_id": "CHANNEL_1",
            "channel_title": "TV Derana",
            "title": "Test Video 1",
            "description": "Description 1",
            "published_at": None,
            "duration": "PT10M",
        },
        {
            "video_id": "VIDEO_2",
            "channel_id": "CHANNEL_1",
            "channel_title": "TV Derana",
            "title": "Test Video 2",
            "description": "Description 2",
            "published_at": None,
            "duration": "PT5M",
        },
    ]

    result = load_videos(
        connection,
        video_records,
    )

    assert result == 2

    assert len(
        connection.cursor_object.executed_statements
    ) == 2

    assert (
        connection.cursor_object.executed_statements[0][0]
        == UPSERT_VIDEO_SQL
    )

    assert (
        connection.cursor_object.executed_statements[0][1]
        == video_records[0]
    )

    assert (
        connection.cursor_object.executed_statements[1][1]
        == video_records[1]
    )

    assert connection.commit_called is True


def test_load_videos_with_empty_list():
    connection = FakeConnection()

    result = load_videos(
        connection,
        [],
    )

    assert result == 0

    assert (
        connection.cursor_object.executed_statements
        == []
    )

    assert connection.commit_called is True


def test_load_daily_statistics():
    connection = FakeConnection()

    statistics_records = [
        {
            "video_id": "VIDEO_1",
            "snapshot_date": "2026-10-07",
            "views": 10000,
            "likes": 500,
            "comments": 25,
        },
        {
            "video_id": "VIDEO_2",
            "snapshot_date": "2026-10-07",
            "views": 20000,
            "likes": 800,
            "comments": 40,
        },
    ]

    result = load_daily_statistics(
        connection,
        statistics_records,
    )

    assert result == 2

    assert len(
        connection.cursor_object.executed_statements
    ) == 2

    assert (
        connection.cursor_object.executed_statements[0][0]
        == INSERT_DAILY_STATS_SQL
    )

    assert (
        connection.cursor_object.executed_statements[0][1]
        == statistics_records[0]
    )

    assert (
        connection.cursor_object.executed_statements[1][1]
        == statistics_records[1]
    )

    assert connection.commit_called is True


def test_load_daily_statistics_with_empty_list():
    connection = FakeConnection()

    result = load_daily_statistics(
        connection,
        [],
    )

    assert result == 0

    assert (
        connection.cursor_object.executed_statements
        == []
    )

    assert connection.commit_called is True