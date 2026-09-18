"""Tests for the ``podcast`` command line (stubs in this version)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from distressed_podcast.cli import main


def test_audio_reports_counts_then_stops(
    script_path: Path, clean_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "key")
    result = CliRunner().invoke(main, ["audio", "example-co"])
    assert result.exit_code != 0
    assert "2 segments" in result.output
    assert "not implemented" in result.output


def test_audio_missing_script(episodes_dir: Path, clean_env: None) -> None:
    result = CliRunner().invoke(main, ["audio", "nope"])
    assert result.exit_code != 0
    assert "script.json" in result.output
    assert "run the script skill" in result.output


def test_audio_invalid_script(script_path: Path, clean_env: None) -> None:
    script_path.write_text('{"company": "x"}', encoding="utf-8")
    result = CliRunner().invoke(main, ["audio", "example-co"])
    assert result.exit_code != 0
    assert "not a valid script" in result.output


def test_publish_requires_storage_env(script_path: Path, clean_env: None) -> None:
    result = CliRunner().invoke(main, ["publish", "example-co"])
    assert result.exit_code != 0
    assert "S3_ENDPOINT_URL is required" in result.output


def test_url_requires_storage_env(clean_env: None) -> None:
    result = CliRunner().invoke(main, ["url", "example-co"])
    assert result.exit_code != 0
    assert "S3_ENDPOINT_URL is required" in result.output
