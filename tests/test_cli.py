"""Tests for the ``podcast`` command line with Gemini and ffmpeg mocked."""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from distressed_podcast import audio, stitch
from distressed_podcast.cli import main


def _audio_response(seconds: float):
    pcm = b"\x00\x00" * int(audio.PCM_SAMPLE_RATE * seconds)
    blob = SimpleNamespace(data=pcm, mime_type="audio/L16;codec=pcm;rate=24000")
    return SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(parts=[SimpleNamespace(inline_data=blob)])
            )
        ],
        usage_metadata=SimpleNamespace(
            prompt_token_count=50, candidates_token_count=500
        ),
    )


@pytest.fixture
def mocked_pipeline(monkeypatch: pytest.MonkeyPatch, clean_env: None):
    """Fake Gemini client and ffmpeg; returns the recorded ffmpeg commands."""
    monkeypatch.setenv("GEMINI_API_KEY", "key")

    class FakeModels:
        def generate_content(self, **kwargs):
            return _audio_response(2.0)

    class FakeClient:
        def __init__(self, api_key):
            self.models = FakeModels()

    monkeypatch.setattr(audio.genai, "Client", FakeClient)
    commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        commands.append(command)
        Path(command[-1]).write_bytes(b"ID3fake")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(stitch.subprocess, "run", fake_run)
    return commands


def test_audio_writes_mp3_and_log(script_path: Path, mocked_pipeline) -> None:
    result = CliRunner().invoke(main, ["audio", "example-co"])
    assert result.exit_code == 0, result.output
    folder = script_path.parent
    assert (folder / "episode.mp3").read_bytes() == b"ID3fake"
    log = (folder / "run.log").read_text()
    assert "audio example-co" in log
    assert "situation" in log and "watch" in log
    assert "seconds=4.0" in log
    assert "estimated_cost_usd=" in log
    assert "2 segments" in result.output
    assert "0.1 min" in result.output
    assert not [p for p in folder.iterdir() if p.name.startswith(".audio-")]
    command = mocked_pipeline[0]
    assert "title=Example Co: A Test Episode" in command
    assert "track=" not in " ".join(command)


def test_audio_sets_track_from_episode(
    script_path: Path, script_dict: dict, mocked_pipeline
) -> None:
    import json

    script_dict["episode"] = 7
    script_path.write_text(json.dumps(script_dict))
    result = CliRunner().invoke(main, ["audio", "example-co"])
    assert result.exit_code == 0, result.output
    assert "track=7" in mocked_pipeline[0]


def test_audio_failure_leaves_no_output(
    script_path: Path, mocked_pipeline, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, "", "ffmpeg exploded")

    monkeypatch.setattr(stitch.subprocess, "run", failing_run)
    result = CliRunner().invoke(main, ["audio", "example-co"])
    assert result.exit_code != 0
    assert "ffmpeg exploded" in result.output
    folder = script_path.parent
    assert not (folder / "episode.mp3").exists()
    assert not (folder / "run.log").exists()


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
