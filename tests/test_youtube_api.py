import pytest
import requests

from src.youtube_api import (
    REQUEST_TIMEOUT_SECONDS,
    YouTubeAPIClient,
    YouTubeAPIError,
)


class FakeResponse:
    """Fake requests.Response object for testing."""

    def __init__(
        self,
        json_data=None,
        status_code=200,
        ok=True,
        text="",
    ):
        self._json_data = json_data
        self.status_code = status_code
        self.ok = ok
        self.text = text

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data

        return self._json_data


def test_get_uploads_playlist_id(monkeypatch):
    client = YouTubeAPIClient("TEST_API_KEY")

    captured = {}

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout

        return FakeResponse(
            json_data={
                "items": [
                    {
                        "contentDetails": {
                            "relatedPlaylists": {
                                "uploads": "UPLOADS_123"
                            }
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    result = client.get_uploads_playlist_id(
        "CHANNEL_123"
    )

    assert result == "UPLOADS_123"

    assert captured["params"]["part"] == "contentDetails"
    assert captured["params"]["id"] == "CHANNEL_123"
    assert captured["params"]["key"] == "TEST_API_KEY"

    assert (
        captured["timeout"]
        == REQUEST_TIMEOUT_SECONDS
    )


def test_get_uploads_playlist_id_when_channel_not_found(
    monkeypatch,
):
    client = YouTubeAPIClient("TEST_API_KEY")

    def fake_get(url, params, timeout):
        return FakeResponse(
            json_data={"items": []}
        )

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    with pytest.raises(
        YouTubeAPIError,
        match="No YouTube channel found",
    ):
        client.get_uploads_playlist_id(
            "INVALID_CHANNEL"
        )


def test_get_playlist_video_ids_handles_pagination(
    monkeypatch,
):
    client = YouTubeAPIClient("TEST_API_KEY")

    responses = [
        FakeResponse(
            json_data={
                "items": [
                    {
                        "contentDetails": {
                            "videoId": "VIDEO_1"
                        }
                    },
                    {
                        "contentDetails": {
                            "videoId": "VIDEO_2"
                        }
                    },
                ],
                "nextPageToken": "PAGE_2",
            }
        ),
        FakeResponse(
            json_data={
                "items": [
                    {
                        "contentDetails": {
                            "videoId": "VIDEO_3"
                        }
                    }
                ]
            }
        ),
    ]

    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        return responses.pop(0)

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    result = client.get_playlist_video_ids(
        playlist_id="UPLOADS_123"
    )

    assert result == [
        "VIDEO_1",
        "VIDEO_2",
        "VIDEO_3",
    ]

    assert len(calls) == 2

    assert calls[0]["playlistId"] == "UPLOADS_123"
    assert "pageToken" not in calls[0]

    assert calls[1]["pageToken"] == "PAGE_2"


def test_get_playlist_video_ids_respects_max_videos(
    monkeypatch,
):
    client = YouTubeAPIClient("TEST_API_KEY")

    def fake_get(url, params, timeout):
        return FakeResponse(
            json_data={
                "items": [
                    {
                        "contentDetails": {
                            "videoId": "VIDEO_1"
                        }
                    },
                    {
                        "contentDetails": {
                            "videoId": "VIDEO_2"
                        }
                    },
                    {
                        "contentDetails": {
                            "videoId": "VIDEO_3"
                        }
                    },
                ],
                "nextPageToken": "PAGE_2",
            }
        )

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    result = client.get_playlist_video_ids(
        playlist_id="UPLOADS_123",
        max_videos=2,
    )

    assert result == [
        "VIDEO_1",
        "VIDEO_2",
    ]


def test_get_video_details_batches_ids(
    monkeypatch,
):
    client = YouTubeAPIClient("TEST_API_KEY")

    video_ids = [
        f"VIDEO_{number}"
        for number in range(1, 53)
    ]

    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)

        return FakeResponse(
            json_data={
                "items": [
                    {
                        "id": "TEST_RESULT"
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    result = client.get_video_details(
        video_ids
    )

    assert len(calls) == 2

    assert len(
        calls[0]["id"].split(",")
    ) == 50

    assert len(
        calls[1]["id"].split(",")
    ) == 2

    assert result == [
        {"id": "TEST_RESULT"},
        {"id": "TEST_RESULT"},
    ]


def test_api_http_error(monkeypatch):
    client = YouTubeAPIClient("TEST_API_KEY")

    def fake_get(url, params, timeout):
        return FakeResponse(
            json_data={
                "error": {
                    "message": "Invalid API key"
                }
            },
            status_code=400,
            ok=False,
        )

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    with pytest.raises(
        YouTubeAPIError,
        match="HTTP 400",
    ):
        client.get_uploads_playlist_id(
            "CHANNEL_123"
        )


def test_api_network_error(monkeypatch):
    client = YouTubeAPIClient("TEST_API_KEY")

    def fake_get(url, params, timeout):
        raise requests.ConnectionError(
            "Connection failed"
        )

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    with pytest.raises(
        YouTubeAPIError,
        match="Network error",
    ):
        client.get_uploads_playlist_id(
            "CHANNEL_123"
        )


def test_api_invalid_json(monkeypatch):
    client = YouTubeAPIClient("TEST_API_KEY")

    def fake_get(url, params, timeout):
        return FakeResponse(
            json_data=ValueError(
                "Invalid JSON"
            )
        )

    monkeypatch.setattr(
        "src.youtube_api.requests.get",
        fake_get,
    )

    with pytest.raises(
        YouTubeAPIError,
        match="invalid JSON",
    ):
        client.get_uploads_playlist_id(
            "CHANNEL_123"
        )