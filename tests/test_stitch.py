"""Tests for WAV wrapping and the ffmpeg call, with ``subprocess`` mocked."""

from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import pytest

from distressed_podcast import stitch


def test_write_wav_roundtrip(tmp_path: Path) -> None:
    pcm = bytes(range(256)) * 4
    path = tmp_path / "a.wav"
    stitch.write_wav(path, pcm)
    with wave.open(str(path), "rb") as handle:
        assert handle.getnchannels() == 1
        assert handle.getsampwidth() == 2
        assert handle.getframerate() == 24_000
        assert handle.readframes(handle.getnframes()) == pcm


def test_concat_invokes_ffmpeg_with_mp3_and_tags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wavs = [tmp_path / "01.wav", tmp_path / "02.wav"]
    for wav in wavs:
        stitch.write_wav(wav, b"\x00\x00" * 10)
    output = tmp_path / "episode.mp3"
    seen: dict = {}

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["kwargs"] = kwargs
        Path(command[-1]).write_bytes(b"ID3")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(stitch.subprocess, "run", fake_run)
    stitch.concat_to_mp3(wavs, output, "Saks: Test", 3)

    command = seen["command"]
    assert command[0] == "ffmpeg"
    assert command[-1] == str(output)
    assert ["-b:a", "128k"] == command[
        command.index("-b:a") : command.index("-b:a") + 2
    ]
    assert ["-ac", "1"] == command[command.index("-ac") : command.index("-ac") + 2]
    metadata = [command[i + 1] for i, v in enumerate(command) if v == "-metadata"]
    assert metadata == ["title=Saks: Test", "album=Distressed Explainers", "track=3"]
    assert seen["kwargs"]["capture_output"] is True
    list_file = Path(command[command.index("-i") + 1])
    assert list_file.read_text().splitlines() == [
        f"file '{wavs[0].resolve()}'",
        f"file '{wavs[1].resolve()}'",
    ]


def test_concat_omits_track_when_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wav = tmp_path / "01.wav"
    stitch.write_wav(wav, b"\x00\x00")
    seen: dict = {}

    def fake_run(command, **kwargs):
        seen["command"] = command
        Path(command[-1]).write_bytes(b"ID3")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(stitch.subprocess, "run", fake_run)
    stitch.concat_to_mp3([wav], tmp_path / "e.mp3", "T", None)
    assert not any(v.startswith("track=") for v in seen["command"])


def test_concat_raises_with_ffmpeg_stderr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wav = tmp_path / "01.wav"
    stitch.write_wav(wav, b"\x00\x00")

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, "", "boom")

    monkeypatch.setattr(stitch.subprocess, "run", fake_run)
    with pytest.raises(stitch.StitchError, match="boom"):
        stitch.concat_to_mp3([wav], tmp_path / "e.mp3", "T", 1)
    assert not (tmp_path / "e.mp3").exists()


def test_concat_requires_segments(tmp_path: Path) -> None:
    with pytest.raises(stitch.StitchError):
        stitch.concat_to_mp3([], tmp_path / "e.mp3", "T", 1)
