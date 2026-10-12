
from typing import Any
import time

import requests


YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
REQUEST_TIMEOUT_SECONDS = 30

MAX_RETRIES = 3
INITIAL_RETRY_DELAY_SECONDS = 1

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


class YouTubeAPIError(Exception):
    """Raised when a YouTube API request fails."""


class YouTubeAPIClient:
    """Client for the YouTube Data API v3."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        request_params = {
            **params,
            "key": self.api_key,
        }
        url = f"{YOUTUBE_API_BASE_URL}/{endpoint}"

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = requests.get(
                    url,
                    params=request_params,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            except requests.RequestException:
                if attempt < MAX_RETRIES:
                    delay = INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt)
                    time.sleep(delay)
                    continue

                raise YouTubeAPIError(
                    "YouTube API request failed after retries "
                    "because of a network error."
                ) from None

            if response.ok:
                try:
                    return response.json()
                except ValueError:
                    raise YouTubeAPIError(
                        "YouTube API returned invalid JSON."
                    ) from None

            status_code = response.status_code

            if status_code in RETRYABLE_STATUS_CODES:
                if attempt < MAX_RETRIES:
                    delay = INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt)
                    time.sleep(delay)
                    continue

                raise YouTubeAPIError(
                    "YouTube API request failed after retries. "
                    f"HTTP status: {status_code}."
                )

            # Do not include the raw response body or URL.
            raise YouTubeAPIError(
                "YouTube API request failed. "
                f"HTTP status: {status_code}. "
                "Check API credentials, permissions, and parameters."
            )

        raise YouTubeAPIError("YouTube API request failed.")

    def get_uploads_playlist_id(self, channel_id: str) -> str:
        data = self._get(
            "channels",
            {
                "part": "contentDetails",
                "id": channel_id,
            },
        )

        items = data.get("items", [])

        if not items:
            raise YouTubeAPIError(
                "No YouTube channel was found for the configured channel ID."
            )

        try:
            return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except (KeyError, TypeError):
            raise YouTubeAPIError(
                "Could not find the channel's uploads playlist."
            ) from None

    def get_playlist_video_ids(
        self,
        playlist_id: str,
        max_videos: int | None = None,
    ) -> list[str]:
        video_ids: list[str] = []
        page_token: str | None = None

        while True:
            params: dict[str, Any] = {
                "part": "contentDetails",
                "playlistId": playlist_id,
                "maxResults": 50,
            }

            if page_token:
                params["pageToken"] = page_token

            data = self._get("playlistItems", params)

            for item in data.get("items", []):
                content_details = item.get("contentDetails", {})
                video_id = content_details.get("videoId")

                if video_id:
                    video_ids.append(video_id)

                    if (
                        max_videos is not None
                        and len(video_ids) >= max_videos
                    ):
                        return video_ids[:max_videos]

            page_token = data.get("nextPageToken")

            if not page_token:
                break

        return video_ids

    def get_video_details(
        self,
        video_ids: list[str],
    ) -> list[dict[str, Any]]:
        all_videos: list[dict[str, Any]] = []

        for start in range(0, len(video_ids), 50):
            batch = video_ids[start:start + 50]

            data = self._get(
                "videos",
                {
                    "part": "snippet,contentDetails,statistics",
                    "id": ",".join(batch),
                },
            )

            all_videos.extend(data.get("items", []))

        return all_videos
