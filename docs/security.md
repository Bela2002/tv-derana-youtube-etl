# Security

## API Key

The YouTube API key is stored in the `.env` file.

The `.env` file is excluded from Git using `.gitignore`.

The API key is never:

- hardcoded in Python source code
- printed in logs
- committed to GitHub
- included in README files
- shared publicly

## Database Credentials

PostgreSQL credentials are also stored in `.env`.

The database password is not stored in source code.

## Public Configuration

`.env.example` is included in GitHub.

It contains variable names and example structure,
but no real credentials.

## Before GitHub Push

The repository should be checked to ensure that:

- `.env` is not tracked
- API keys are not present
- database passwords are not present
- logs do not contain secrets