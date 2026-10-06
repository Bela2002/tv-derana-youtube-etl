# YouTube API Notes

## API

YouTube Data API v3.

## Authentication

The project uses an API key for accessing public YouTube data.

The API key is stored in an environment variable and is never
hardcoded in source code.

## API Workflow

1. Retrieve the channel's uploads playlist ID.
2. Retrieve playlist items using pagination.
3. Extract video IDs.
4. Retrieve video details using videos.list.
5. Extract metadata and statistics.

## Important API Fields

### Video metadata

- id
- snippet.channelId
- snippet.channelTitle
- snippet.title
- snippet.description
- snippet.publishedAt
- contentDetails.duration

### Statistics

- statistics.viewCount
- statistics.likeCount
- statistics.commentCount

## Pagination

The API can return a `nextPageToken`.

The extraction code continues requesting pages until
`nextPageToken` is no longer provided.

## Quota

The YouTube Data API uses quotas.

The implementation avoids unnecessary search requests and
uses the channel uploads playlist and batched video requests.