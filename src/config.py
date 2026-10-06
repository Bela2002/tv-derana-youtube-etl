import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load values from the .env file into environment variables.
load_dotenv()


def get_required_env(name: str) -> str:
    """
    Read a required environment variable.

    Raises:
        ValueError: If the variable is missing or empty.
    """
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Required environment variable '{name}' is missing."
        )

    return value


def get_optional_int_env(name: str) -> int | None:
    """
    Read an optional integer environment variable.

    Returns:
        None if the variable is empty/not provided.
        Integer value otherwise.
    """
    value = os.getenv(name)

    if value is None or value.strip() == "":
        return None

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable '{name}' must be an integer."
        ) from exc


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    youtube_api_key: str
    youtube_channel_id: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    max_videos_per_run: int | None


def load_settings() -> Settings:
    """Load and validate application settings."""

    return Settings(
        youtube_api_key=get_required_env("YOUTUBE_API_KEY"),
        youtube_channel_id=get_required_env("YOUTUBE_CHANNEL_ID"),
        db_host=get_required_env("DB_HOST"),
        db_port=int(get_required_env("DB_PORT")),
        db_name=get_required_env("DB_NAME"),
        db_user=get_required_env("DB_USER"),
        db_password=get_required_env("DB_PASSWORD"),
        max_videos_per_run=get_optional_int_env("MAX_VIDEOS_PER_RUN"),
    )