from datetime import date, datetime, timezone

from src.transform import (
    parse_youtube_datetime,
    safe_int,
    transform_video,
)


def test_safe_int_with_valid_value():
    assert safe_int("12345") == 12345


def test_safe_int_with_invalid_value():
    assert safe_int("not-a-number") is None


def test_safe_int_with_none():
    assert safe_int(None) is None


def test_parse_youtube_datetime():
    result = parse_youtube_datetime(
        "2026-10-06T10:30:00Z"
    )

    assert result == datetime(
        2026,
        10,
        6,
        10,
        30,
        tzinfo=timezone.utc,
    )


def test_transform_video():
    raw_video = {
        "id": "ABC123",
        "snippet": {
            "channelId": "CHANNEL123",
            "channelTitle": "TV Derana",
            "title": "Test Video",
            "description": "Test description",
            "publishedAt": "2026-10-01T10:00:00Z",
        },
        "contentDetails": {
            "duration": "PT10M",
        },
        "statistics": {
            "viewCount": "10000",
            "likeCount": "500",
            "commentCount": "25",
        },
    }

    metadata, statistics = transform_video(
        raw_video,
        date(2026, 10, 6),
    )

    assert metadata["video_id"] == "ABC123"
    assert metadata["title"] == "Test Video"

    assert statistics["video_id"] == "ABC123"
    assert statistics["snapshot_date"] == date(2026, 10, 6)
    assert statistics["views"] == 10000
    assert statistics["likes"] == 500
    assert statistics["comments"] == 25