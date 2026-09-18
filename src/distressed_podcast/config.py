"""Settings, read only from environment variables.

Each CLI command validates just the settings it needs, so ``podcast audio``
does not require S3 credentials and ``podcast publish`` does not require a
Gemini key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

EPISODES_DIR = Path("episodes")

DEFAULT_TTS_MODEL = "gemini-3.1-flash-tts-preview"
DEFAULT_VOICE_HOST = "Charon"
DEFAULT_VOICE_GUEST = "Puck"


class ConfigError(RuntimeError):
    """A required environment variable is missing or malformed."""


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"{name} is required but not set")
    return value


def _optional(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or default


@dataclass(frozen=True)
class GeminiSettings:
    """What ``podcast audio`` needs.

    ``api_key`` is optional: a cloud environment may inject the credential at
    an HTTP proxy, in which case the code sends no key and a missing one
    surfaces as an authentication error at call time.
    """

    api_key: str | None
    model: str
    voice_host: str
    voice_guest: str

    @classmethod
    def from_env(cls) -> "GeminiSettings":
        """Build from ``GEMINI_*`` environment variables."""
        return cls(
            api_key=_optional("GEMINI_API_KEY"),
            model=_optional("GEMINI_TTS_MODEL", DEFAULT_TTS_MODEL),
            voice_host=_optional("GEMINI_VOICE_HOST", DEFAULT_VOICE_HOST),
            voice_guest=_optional("GEMINI_VOICE_GUEST", DEFAULT_VOICE_GUEST),
        )


@dataclass(frozen=True)
class StorageSettings:
    """What ``podcast publish`` and ``podcast url`` need."""

    endpoint_url: str
    region: str
    bucket: str
    access_key_id: str
    secret_access_key: str

    @classmethod
    def from_env(cls) -> "StorageSettings":
        """Build from ``S3_*`` and ``AWS_*`` environment variables.

        Raises:
            ConfigError: If any required variable is missing.
        """
        return cls(
            endpoint_url=_require("S3_ENDPOINT_URL"),
            region=_require("S3_REGION"),
            bucket=_require("S3_BUCKET"),
            access_key_id=_require("AWS_ACCESS_KEY_ID"),
            secret_access_key=_require("AWS_SECRET_ACCESS_KEY"),
        )


def episode_dir(slug: str) -> Path:
    """Directory holding one episode's research, script, audio and log."""
    return EPISODES_DIR / slug
