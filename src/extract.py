from typing import Any

from src.youtube_api import YouTubeAPIClient


def extract_youtube_data(
    client: YouTubeAPIClient,
    channel_id: str,
    max_videos: int | None = None,
) -> list[dict[str, Any]]:
    """
    Extract TV Derana video information from YouTube.

    Workflow:

    1. Find the channel's uploads playlist.
    2. Retrieve video IDs from that playlist.
    3. Retrieve detailed information/statistics for those videos.

    Returns:
        Raw YouTube video resources.
    """

    uploads_playlist_id = client.get_uploads_playlist_id(
        channel_id
    )

    video_ids = client.get_playlist_video_ids(
        playlist_id=uploads_playlist_id,
        max_videos=max_videos,
    )

    if not video_ids:
        return []

    videos = client.get_video_details(video_ids)

    return videos