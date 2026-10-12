# Security

## API Key

The YouTube API key is stored in the `.env` file and loaded through environment-based configuration.

The `.env` file is excluded from Git using `.gitignore`.

The API key should never be:

- Hardcoded in Python source code.
- Printed directly in logs.
- Committed to GitHub.
- Included in README files or public documentation.
- Shared publicly.

## API Error Handling

The API client has been updated to reduce the risk of exposing sensitive information when requests fail.

Custom API error messages avoid including the raw request URL or response body. This is important because request URLs may contain the API key.

Automated tests verify that a simulated network failure containing a secret value does not expose that value in the resulting custom API error.

## Database Credentials

PostgreSQL credentials are stored in `.env`.

The database password is not stored directly in source code or public documentation.

## Public Configuration

`.env.example` is maintained with configuration variable names and placeholder values. It must not contain real API keys or database passwords.

## Repository and Log Checks

The following checks have been performed:

- The current log files were searched for an exact match of the configured API key. No exact match was found.
- `git ls-files .env` returned no output, indicating that `.env` is not currently tracked in the Git index.

These checks cover the inspected logs and current Git index. They do not establish whether a credential was ever committed in earlier Git history or exposed in another location.

## Before GitHub Push

Before pushing changes, check that:

- `.env` is not tracked.
- API keys are not present in source files or documentation.
- Database passwords are not present in source files or documentation.
- Logs do not contain credentials.
- `.env.example` contains placeholders only.
- Previous Git history has been reviewed if there is a concern that a credential was committed previously.

If a credential is confirmed to have been exposed publicly, follow the provider's credential-rotation procedure.

