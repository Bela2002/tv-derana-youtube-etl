from datetime import date, datetime, timezone
from typing import Any


def safe_int(value: Any) -> int | None:
    """
    Convert a value to integer safely.

    Returns None for missing/invalid values.
    """

    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_youtube_datetime(value: str | None) -> datetime | None:
    """
    Convert an ISO 8601 YouTube timestamp into a timezone-aware datetime.
    """

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def parse_duration(duration: str | None) -> str | None:
    """
    Keep YouTube's ISO 8601 duration representation.

    Example:
        PT12M35S
    """

    if not duration:
        return None

    return duration


def transform_video(
    raw_video: dict[str, Any],
    snapshot_date: date,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Transform one raw YouTube API video resource.

    Returns:
        (
            video_metadata,
            daily_statistics
        )
    """

    snippet = raw_video.get("snippet", {})
    content_details = raw_video.get("contentDetails", {})
    statistics = raw_video.get("statistics", {})

    video_id = raw_video.get("id")

    if not video_id:
        raise ValueError("Video record does not contain a video ID.")

    published_at = parse_youtube_datetime(
        snippet.get("publishedAt")
    )

    video_metadata = {
        "video_id": video_id,
        "channel_id": snippet.get("channelId"),
        "channel_title": snippet.get("channelTitle"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "published_at": published_at,
        "duration": parse_duration(
            content_details.get("duration")
        ),
    }

    daily_statistics = {
        "video_id": video_id,
        "snapshot_date": snapshot_date,
        "views": safe_int(statistics.get("viewCount")),
        "likes": safe_int(statistics.get("likeCount")),
        "comments": safe_int(statistics.get("commentCount")),
    }

    return video_metadata, daily_statistics


def transform_videos(
    raw_videos: list[dict[str, Any]],
    snapshot_date: date,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Transform all extracted YouTube videos.

    Invalid records are skipped rather than crashing the entire
    transformation.
    """

    video_records: list[dict[str, Any]] = []
    statistics_records: list[dict[str, Any]] = []

    for raw_video in raw_videos:
        try:
            metadata, statistics = transform_video(
                raw_video,
                snapshot_date,
            )

            video_records.append(metadata)
            statistics_records.append(statistics)

        except ValueError:
            continue

    return video_records, statistics_records