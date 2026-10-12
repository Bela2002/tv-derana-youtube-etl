
from datetime import date
from unittest.mock import MagicMock, call

import pytest

import src.main as main_module


@pytest.fixture
def mocked_etl(monkeypatch):
    """Mock external dependencies so tests never call the real API or database."""

    logger = MagicMock()

    settings = MagicMock()
    settings.youtube_api_key = "TEST_API_KEY"
    settings.youtube_channel_id = "TEST_CHANNEL_ID"
    settings.max_videos_per_run = None

    client = MagicMock()
    connection = MagicMock()

    raw_videos = [
        {
            "id": "TEST_VIDEO_001",
            "snippet": {
                "title": "Test video",
                "description": "Test description",
                "channelId": "TEST_CHANNEL_ID",
                "channelTitle": "Test channel",
                "publishedAt": "2026-10-10T10:00:00Z",
            },
            "contentDetails": {"duration": "PT5M"},
            "statistics": {
                "viewCount": "100",
                "likeCount": "10",
                "commentCount": "2",
            },
        }
    ]

    video_records = [
        {
            "video_id": "TEST_VIDEO_001",
            "title": "Test video",
        }
    ]

    statistics_records = [
        {
            "video_id": "TEST_VIDEO_001",
            "views": 100,
            "likes": 10,
            "comments": 2,
        }
    ]

    # Create mocks for the individual ETL stages.
    extract_mock = MagicMock(return_value=raw_videos)
    transform_mock = MagicMock(
        return_value=(video_records, statistics_records)
    )
    database_connection_mock = MagicMock(return_value=connection)
    initialize_mock = MagicMock()
    load_videos_mock = MagicMock(return_value=1)
    load_statistics_mock = MagicMock(return_value=1)

    # Patch dependencies where main.py uses them.
    monkeypatch.setattr(main_module, "setup_logger", lambda: logger)
    monkeypatch.setattr(main_module, "load_settings", lambda: settings)
    monkeypatch.setattr(
        main_module, "YouTubeAPIClient", lambda api_key: client
    )
    monkeypatch.setattr(
        main_module, "extract_youtube_data", extract_mock
    )
    monkeypatch.setattr(
        main_module, "transform_videos", transform_mock
    )
    monkeypatch.setattr(
        main_module, "get_database_connection",
        database_connection_mock,
    )
    monkeypatch.setattr(
        main_module, "initialize_database", initialize_mock
    )
    monkeypatch.setattr(
        main_module, "load_videos", load_videos_mock
    )
    monkeypatch.setattr(
        main_module, "load_daily_statistics", load_statistics_mock
    )

    # Combine stage mocks to verify their execution order.
    pipeline = MagicMock()
    pipeline.attach_mock(transform_mock, "transform")
    pipeline.attach_mock(initialize_mock, "initialize")
    pipeline.attach_mock(load_videos_mock, "load_videos")
    pipeline.attach_mock(load_statistics_mock, "load_statistics")

    return {
        "logger": logger,
        "settings": settings,
        "client": client,
        "connection": connection,
        "raw_videos": raw_videos,
        "video_records": video_records,
        "statistics_records": statistics_records,
        "extract": extract_mock,
        "transform": transform_mock,
        "get_connection": database_connection_mock,
        "initialize": initialize_mock,
        "load_videos": load_videos_mock,
        "load_statistics": load_statistics_mock,
        "pipeline": pipeline,
    }


def test_main_returns_when_extraction_finds_no_videos(mocked_etl):
    """Empty extraction logs a warning and does not connect to PostgreSQL."""

    mocked_etl["extract"].return_value = []

    main_module.main()

    mocked_etl["logger"].warning.assert_called_once_with(
        "No videos were retrieved."
    )
    mocked_etl["get_connection"].assert_not_called()
    mocked_etl["transform"].assert_not_called()
    mocked_etl["connection"].close.assert_not_called()


def test_main_successfully_runs_pipeline(mocked_etl):
    """All ETL stages run in order and receive the expected records."""

    main_module.main()

    # Confirm the extraction arguments.
    mocked_etl["extract"].assert_called_once_with(
        client=mocked_etl["client"],
        channel_id="TEST_CHANNEL_ID",
        max_videos=None,
    )

    # Confirm transformation receives the extracted data and a date.
    mocked_etl["transform"].assert_called_once()
    transform_kwargs = mocked_etl["transform"].call_args.kwargs

    assert transform_kwargs["raw_videos"] == mocked_etl["raw_videos"]
    assert isinstance(transform_kwargs["snapshot_date"], date)

    # Confirm database initialization and both loads.
    mocked_etl["initialize"].assert_called_once_with(
        mocked_etl["connection"]
    )
    mocked_etl["load_videos"].assert_called_once_with(
        mocked_etl["connection"],
        mocked_etl["video_records"],
    )
    mocked_etl["load_statistics"].assert_called_once_with(
        mocked_etl["connection"],
        mocked_etl["statistics_records"],
    )

    # Verify the order of the main pipeline stages.
    assert mocked_etl["pipeline"].mock_calls == [
        call.transform(
            raw_videos=mocked_etl["raw_videos"],
            snapshot_date=transform_kwargs["snapshot_date"],
        ),
        call.initialize(mocked_etl["connection"]),
        call.load_videos(
            mocked_etl["connection"],
            mocked_etl["video_records"],
        ),
        call.load_statistics(
            mocked_etl["connection"],
            mocked_etl["statistics_records"],
        ),
    ]

    mocked_etl["connection"].close.assert_called_once()


def test_main_propagates_extraction_failure(mocked_etl):
    """Extraction errors are logged and propagated to the caller."""

    mocked_etl["extract"].side_effect = RuntimeError(
        "Simulated extraction failure"
    )

    with pytest.raises(
        RuntimeError, match="Simulated extraction failure"
    ):
        main_module.main()

    mocked_etl["logger"].exception.assert_called_once_with(
        "ETL process failed."
    )
    mocked_etl["get_connection"].assert_not_called()


def test_main_closes_connection_if_loading_fails(mocked_etl):
    """The database connection closes even if a load operation fails."""

    mocked_etl["load_videos"].side_effect = RuntimeError(
        "Simulated database load failure"
    )

    with pytest.raises(
        RuntimeError, match="Simulated database load failure"
    ):
        main_module.main()

    mocked_etl["logger"].exception.assert_called_once_with(
        "ETL process failed."
    )
    mocked_etl["connection"].close.assert_called_once()
