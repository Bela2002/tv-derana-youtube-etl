import pytest

from src.config import (
    Settings,
    get_optional_int_env,
    get_required_env,
    load_settings,
)


def test_get_required_env_returns_value(monkeypatch):
    monkeypatch.setenv("TEST_VARIABLE", "hello")

    result = get_required_env("TEST_VARIABLE")

    assert result == "hello"


def test_get_required_env_raises_error_when_missing(monkeypatch):
    monkeypatch.delenv("TEST_VARIABLE", raising=False)

    with pytest.raises(
        ValueError,
        match="Required environment variable 'TEST_VARIABLE' is missing.",
    ):
        get_required_env("TEST_VARIABLE")


def test_get_optional_int_env_returns_integer(monkeypatch):
    monkeypatch.setenv("TEST_NUMBER", "100")

    result = get_optional_int_env("TEST_NUMBER")

    assert result == 100


def test_get_optional_int_env_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("TEST_NUMBER", raising=False)

    result = get_optional_int_env("TEST_NUMBER")

    assert result is None


def test_get_optional_int_env_returns_none_when_empty(monkeypatch):
    monkeypatch.setenv("TEST_NUMBER", "   ")

    result = get_optional_int_env("TEST_NUMBER")

    assert result is None


def test_get_optional_int_env_raises_error_for_invalid_integer(
    monkeypatch,
):
    monkeypatch.setenv("TEST_NUMBER", "abc")

    with pytest.raises(
        ValueError,
        match="Environment variable 'TEST_NUMBER' must be an integer.",
    ):
        get_optional_int_env("TEST_NUMBER")


def test_load_settings(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-api-key")
    monkeypatch.setenv("YOUTUBE_CHANNEL_ID", "test-channel-id")

    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "test-password")

    monkeypatch.setenv("MAX_VIDEOS_PER_RUN", "100")

    settings = load_settings()

    assert isinstance(settings, Settings)

    assert settings.youtube_api_key == "test-api-key"
    assert settings.youtube_channel_id == "test-channel-id"

    assert settings.db_host == "localhost"
    assert settings.db_port == 5432
    assert settings.db_name == "test_db"
    assert settings.db_user == "postgres"
    assert settings.db_password == "test-password"

    assert settings.max_videos_per_run == 100