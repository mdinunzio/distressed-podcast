"""Tests for environment-driven settings."""

from __future__ import annotations

import pytest

from distressed_podcast.config import (
    DEFAULT_TTS_MODEL,
    DEFAULT_VOICE_GUEST,
    DEFAULT_VOICE_HOST,
    ConfigError,
    GeminiSettings,
    StorageSettings,
)


def test_gemini_defaults_without_key(clean_env: None) -> None:
    settings = GeminiSettings.from_env()
    assert settings.api_key is None
    assert settings.model == DEFAULT_TTS_MODEL
    assert (settings.voice_host, settings.voice_guest) == (
        DEFAULT_VOICE_HOST,
        DEFAULT_VOICE_GUEST,
    )


def test_gemini_overrides(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "key")
    monkeypatch.setenv("GEMINI_TTS_MODEL", "other-model")
    monkeypatch.setenv("GEMINI_VOICE_HOST", "Kore")
    monkeypatch.setenv("GEMINI_VOICE_GUEST", "Fenrir")
    settings = GeminiSettings.from_env()
    assert settings == GeminiSettings("key", "other-model", "Kore", "Fenrir")


def test_blank_env_counts_as_unset(
    clean_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "   ")
    assert GeminiSettings.from_env().api_key is None


STORAGE_ENV = {
    "S3_ENDPOINT_URL": "https://ns.compat.objectstorage.us-ashburn-1.oraclecloud.com",
    "S3_REGION": "us-ashburn-1",
    "S3_BUCKET": "episodes",
    "AWS_ACCESS_KEY_ID": "id",
    "AWS_SECRET_ACCESS_KEY": "secret",
}


def test_storage_requires_every_variable(
    clean_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in STORAGE_ENV.items():
        monkeypatch.setenv(name, value)
    settings = StorageSettings.from_env()
    assert settings.bucket == "episodes"
    assert settings.region == "us-ashburn-1"

    monkeypatch.delenv("S3_BUCKET")
    with pytest.raises(ConfigError, match="S3_BUCKET"):
        StorageSettings.from_env()
