# YouTube API Notes

## API

YouTube Data API v3.

## Authentication

The project uses an API key to access public YouTube data.

The API key is stored in the `.env` file and loaded through environment-based configuration. It is not hardcoded in the Python source code.

The API client adds the key to outgoing requests but avoids including the raw request URL or response body in its custom error messages. This helps reduce the risk of exposing the key when an API request fails.

## API Workflow

1. Retrieve the channel's uploads playlist ID.
2. Retrieve playlist items using pagination.
3. Extract video IDs.
4. Retrieve video details using `videos.list`.
5. Extract metadata and statistics.

## Important API Fields

### Video metadata

- `id`
- `snippet.channelId`
- `snippet.channelTitle`
- `snippet.title`
- `snippet.description`
- `snippet.publishedAt`
- `contentDetails.duration`

### Statistics

- `statistics.viewCount`
- `statistics.likeCount`
- `statistics.commentCount`

## Pagination

The API can return a `nextPageToken`.

The extraction code continues requesting pages while a `nextPageToken` is provided. This allows the pipeline to process multiple pages rather than stopping after the first response.

## Retry Mechanism

The API client includes a retry mechanism for temporary request failures.

- The maximum number of retries is configured as three, in addition to the initial request.
- Temporary HTTP errors with status codes `429`, `500`, `502`, `503`, and `504` are retryable.
- Network-related request exceptions are also retried.
- The retry delay increases exponentially, using delays of approximately 1, 2, and 4 seconds.
- Permanent HTTP errors, such as `400`, are not repeatedly retried.
- Custom API errors are raised without including the raw request URL or response body in the error message.

This mechanism helps the pipeline recover from temporary failures without immediately stopping after a single unsuccessful request. It does not guarantee recovery from every API failure. For example, quota-related errors are not automatically retried by the current retry policy.

## Quota

The YouTube Data API uses quotas.

The implementation uses the channel's uploads playlist and requests video details in batches of up to 50 video IDs. These choices help avoid unnecessary API requests compared with retrieving videos individually.

