"""Compare the channel's reported video count with its uploads playlist."""

from src.config import load_settings
from src.youtube_api import YouTubeAPIClient


def main():
    settings = load_settings()

    # Use the same API client as the main ETL pipeline.
    client = YouTubeAPIClient(settings.youtube_api_key)

    # 1. Get the channel's reported video count.
    response = client._get(
        "channels",
        {
            "part": "statistics,snippet",
            "id": settings.youtube_channel_id,
        },
    )

    channels = response.get("items", [])

    if not channels:
        print("ERROR: No channel was returned. Check YOUTUBE_CHANNEL_ID.")
        return

    channel = channels[0]
    statistics = channel.get("statistics", {})

    print("\n=== CHANNEL INFORMATION ===")
    print("Channel title:", channel["snippet"]["title"])
    print("Channel ID:", channel["id"])
    print("Reported video count:", statistics.get("videoCount", "Unavailable"))

    # 2. Get the uploads playlist ID.
    playlist_id = client.get_uploads_playlist_id(
        settings.youtube_channel_id
    )

    print("\n=== UPLOADS PLAYLIST ===")
    print("Uploads playlist ID:", playlist_id)


    # Check the uploads playlist's own metadata.
    playlist_response = client._get(
        "playlists",
        {
            "part": "contentDetails,snippet",
            "id": playlist_id,
        },
    )

    playlist_items = playlist_response.get("items", [])

    if playlist_items:
        playlist = playlist_items[0]

        print("\n=== UPLOADS PLAYLIST METADATA ===")
        print("Playlist title:", playlist["snippet"]["title"])
        print(
            "Playlist item count:",
            playlist["contentDetails"]["itemCount"],
        )

    # 3. Count playlist items independently using pagination.
    total_items = 0
    unique_video_ids = set()
    page_count = 0
    page_token = None

    # Keep track of the first and last videos returned.
    first_video_id = None
    last_video = None

    # Keep the pagination information from the first page.
    first_page_info = {}

    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
        }

        if page_token:
            params["pageToken"] = page_token

        page = client._get("playlistItems", params)
        page_count += 1

        items = page.get("items", [])
        total_items += len(items)

        # Inspect the API's reported pagination information.
        page_info = page.get("pageInfo", {})

        if page_count == 1:
            first_page_info = page_info
            print("\n=== FIRST PAGE API INFORMATION ===")
            print("First page API total:", page_info.get("totalResults"))
            print(
                "First page results per page:",
                page_info.get("resultsPerPage"),
            )

        # Record the first video ID encountered.
        if items and first_video_id is None:
            first_video_id = (
                items[0].get("contentDetails", {}).get("videoId")
            )

        # Update the last video after every page.
        if items:
            last_video = items[-1]

        # Collect unique video IDs.
        for item in items:
            video_id = item.get("contentDetails", {}).get("videoId")

            if video_id:
                unique_video_ids.add(video_id)

        # Continue only if the API provides another page token.
        page_token = page.get("nextPageToken")

        if not page_token:
            break

    # 4. Display the pagination results.
    print("\n=== PAGINATION RESULTS ===")
    print("Pages retrieved:", page_count)
    print("Total playlist items:", total_items)
    print("Unique video IDs:", len(unique_video_ids))
    print("Next page token remaining:", bool(page_token))

    # 5. Display the first and last videos returned.
    print("\n=== PLAYLIST BOUNDARIES ===")
    print("First video ID:", first_video_id)

    if last_video:
        last_video_details = last_video.get("contentDetails", {})
        last_video_snippet = last_video.get("snippet", {})

        print("Last video ID:", last_video_details.get("videoId"))
        print("Last video title:", last_video_snippet.get("title"))
        print("Last video position:", last_video_snippet.get("position"))
    else:
        print("No videos were returned by the uploads playlist.")

    # 6. Compare the two counts.
    print("\n=== COMPARISON ===")
    print("Channel videoCount:", statistics.get("videoCount"))
    print("Playlist API totalResults:", first_page_info.get("totalResults"))
    print("Playlist item count:", total_items)
    print("Unique playlist video IDs:", len(unique_video_ids))


if __name__ == "__main__":
    main()
