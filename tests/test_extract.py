from src.extract import extract_youtube_data


class FakeYouTubeClient:
    """Fake YouTube client used to test the extraction workflow."""

    def __init__(self):
        self.uploads_playlist_called_with = None
        self.playlist_called_with = None
        self.video_details_called_with = None

    def get_uploads_playlist_id(self, channel_id):
        self.uploads_playlist_called_with = channel_id
        return "UPLOADS_PLAYLIST_123"

    def get_playlist_video_ids(
        self,
        playlist_id,
        max_videos=None,
    ):
        self.playlist_called_with = (
            playlist_id,
            max_videos,
        )

        return ["VIDEO_1", "VIDEO_2"]

    def get_video_details(self, video_ids):
        self.video_details_called_with = video_ids

        return [
            {"id": "VIDEO_1"},
            {"id": "VIDEO_2"},
        ]


def test_extract_youtube_data():
    client = FakeYouTubeClient()

    result = extract_youtube_data(
        client=client,
        channel_id="CHANNEL_123",
        max_videos=100,
    )

    assert result == [
        {"id": "VIDEO_1"},
        {"id": "VIDEO_2"},
    ]

    assert client.uploads_playlist_called_with == "CHANNEL_123"

    assert client.playlist_called_with == (
        "UPLOADS_PLAYLIST_123",
        100,
    )

    assert client.video_details_called_with == [
        "VIDEO_1",
        "VIDEO_2",
    ]


def test_extract_youtube_data_returns_empty_list_when_no_videos():
    class EmptyYouTubeClient:
        def get_uploads_playlist_id(self, channel_id):
            return "UPLOADS_PLAYLIST_123"

        def get_playlist_video_ids(
            self,
            playlist_id,
            max_videos=None,
        ):
            return []

        def get_video_details(self, video_ids):
            raise AssertionError(
                "get_video_details should not be called "
                "when there are no video IDs."
            )

    client = EmptyYouTubeClient()

    result = extract_youtube_data(
        client=client,
        channel_id="CHANNEL_123",
    )

    assert result == []