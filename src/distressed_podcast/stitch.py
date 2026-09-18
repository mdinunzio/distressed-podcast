"""Wrap PCM as WAV, concatenate with ffmpeg, encode MP3, write ID3 tags."""

from __future__ import annotations

import subprocess
import wave
from pathlib import Path

from distressed_podcast.audio import PCM_CHANNELS, PCM_SAMPLE_RATE, PCM_SAMPLE_WIDTH

ALBUM = "Distressed Explainers"
MP3_BITRATE = "128k"


class StitchError(RuntimeError):
    """ffmpeg failed; the message carries its stderr."""


def write_wav(path: Path, pcm: bytes) -> None:
    """Write raw 16-bit little-endian mono 24 kHz PCM as a WAV file."""
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(PCM_CHANNELS)
        handle.setsampwidth(PCM_SAMPLE_WIDTH)
        handle.setframerate(PCM_SAMPLE_RATE)
        handle.writeframes(pcm)


def ffmpeg_command(
    list_file: Path, output: Path, title: str, track: int | None
) -> list[str]:
    """Build the ffmpeg invocation: concat demuxer -> 128 kbps mono MP3 + ID3."""
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-ac",
        str(PCM_CHANNELS),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        MP3_BITRATE,
        "-id3v2_version",
        "3",
        "-metadata",
        f"title={title}",
        "-metadata",
        f"album={ALBUM}",
    ]
    if track is not None:
        command += ["-metadata", f"track={track}"]
    command.append(str(output))
    return command


def concat_to_mp3(
    wav_paths: list[Path], output: Path, title: str, track: int | None
) -> None:
    """Concatenate WAV files in order into one tagged MP3.

    Args:
        wav_paths: Segment WAVs in playback order.
        output: Destination MP3 path (written only on success).
        title: ID3 title.
        track: ID3 track number, or ``None`` to omit it.

    Raises:
        StitchError: If ffmpeg exits non-zero or produces no file.
    """
    if not wav_paths:
        raise StitchError("no segments to concatenate")
    list_file = output.with_suffix(".txt")
    list_file.write_text(
        "".join(f"file '{path.resolve()}'\n" for path in wav_paths), encoding="utf-8"
    )
    result = subprocess.run(
        ffmpeg_command(list_file, output, title, track),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise StitchError(
            f"ffmpeg failed ({result.returncode}): {result.stderr.strip()}"
        )
    if not output.exists():
        raise StitchError("ffmpeg reported success but wrote no file")
