from typing import Any

import requests


YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"

REQUEST_TIMEOUT_SECONDS = 30


class YouTubeAPIError(Exception):
    """Raised when a YouTube API request fails."""


class YouTubeAPIClient:
    """Small client for the YouTube Data API v3."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send a GET request to the YouTube Data API.

        The API key is added automatically.
        """

        request_params = {
            **params,
            "key": self.api_key,
        }

        url = f"{YOUTUBE_API_BASE_URL}/{endpoint}"

        try:
            response = requests.get(
                url,
                params=request_params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            raise YouTubeAPIError(
                f"Network error while calling YouTube API: {exc}"
            ) from exc

        if not response.ok:
            try:
                error_body = response.json()
            except ValueError:
                error_body = response.text

            raise YouTubeAPIError(
                f"YouTube API request failed "
                f"(HTTP {response.status_code}): {error_body}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise YouTubeAPIError(
                "YouTube API returned invalid JSON."
            ) from exc

    def get_uploads_playlist_id(self, channel_id: str) -> str:
        """
        Get the playlist ID containing all videos uploaded by a channel.
        """

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
                f"No YouTube channel found for channel ID: {channel_id}"
            )

        try:
            return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except KeyError as exc:
            raise YouTubeAPIError(
                "Could not find the channel's uploads playlist."
            ) from exc

    def get_playlist_video_ids(
        self,
        playlist_id: str,
        max_videos: int | None = None,
    ) -> list[str]:
        """
        Retrieve video IDs from an uploads playlist.

        Handles API pagination automatically.

        Args:
            playlist_id: YouTube uploads playlist ID.
            max_videos: Optional limit used during development/testing.
        """

        video_ids: list[str] = []
        page_token: str | None = None

        while True:
            params: dict[str, Any] = {
                "part": "contentDetails,snippet",
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
        """
        Retrieve details/statistics for a list of video IDs.

        YouTube accepts multiple video IDs in one videos.list request,
        so IDs are processed in batches of 50.
        """

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