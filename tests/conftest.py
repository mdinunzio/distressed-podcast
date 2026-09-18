"""Shared fixtures: a small valid script and a temporary episodes directory."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from distressed_podcast import config


@pytest.fixture
def script_dict() -> dict:
    """A minimal valid script as a plain dict."""
    return {
        "company": "Example Co",
        "slug": "example-co",
        "title": "Example Co: A Test Episode",
        "deal_type": "prearranged Chapter 11",
        "segments": [
            {
                "name": "situation",
                "direction": "Calm and clear.",
                "turns": [
                    {"speaker": "Host", "text": "Welcome to the show."},
                    {"speaker": "Guest", "text": "Glad to be here."},
                ],
            },
            {
                "name": "watch",
                "direction": "Brisk wrap-up.",
                "turns": [
                    {"speaker": "Host", "text": "Watch the hearing on Friday."},
                ],
            },
        ],
    }


@pytest.fixture
def episodes_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point ``config.EPISODES_DIR`` at a temporary directory."""
    root = tmp_path / "episodes"
    root.mkdir()
    monkeypatch.setattr(config, "EPISODES_DIR", root)
    return root


@pytest.fixture
def script_path(episodes_dir: Path, script_dict: dict) -> Path:
    """Write ``script_dict`` to ``<episodes_dir>/example-co/script.json``."""
    folder = episodes_dir / script_dict["slug"]
    folder.mkdir()
    path = folder / "script.json"
    path.write_text(json.dumps(script_dict), encoding="utf-8")
    return path


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every provider variable so each test sets only what it needs."""
    for name in (
        "GEMINI_API_KEY",
        "GEMINI_TTS_MODEL",
        "GEMINI_VOICE_HOST",
        "GEMINI_VOICE_GUEST",
        "S3_ENDPOINT_URL",
        "S3_REGION",
        "S3_BUCKET",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
