"""Gemini multi-speaker text-to-speech, one request per segment.

Claude does not voice anything: every segment's ``direction`` and dialogue
are sent to Gemini, which returns raw 16-bit little-endian PCM at 24 kHz,
mono. Wrapping, concatenation and encoding live in :mod:`stitch`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from google import genai
from google.genai import types

from distressed_podcast.config import GeminiSettings
from distressed_podcast.models import Segment

PLACEHOLDER_API_KEY = "proxy-injected"
"""Used when ``GEMINI_API_KEY`` is unset so the SDK builds a client; a proxy
in front of ``generativelanguage.googleapis.com`` then supplies the real key.
"""

PCM_SAMPLE_RATE = 24_000
PCM_SAMPLE_WIDTH = 2
PCM_CHANNELS = 1
BYTES_PER_SECOND = PCM_SAMPLE_RATE * PCM_SAMPLE_WIDTH * PCM_CHANNELS


class AudioError(RuntimeError):
    """Gemini returned something other than one audio part."""


@dataclass(frozen=True)
class SegmentAudio:
    """PCM audio for one segment plus what it cost to make."""

    name: str
    pcm: bytes
    characters: int
    prompt_tokens: int | None
    audio_tokens: int | None

    @property
    def seconds(self) -> float:
        """Duration implied by the PCM byte count."""
        return len(self.pcm) / BYTES_PER_SECOND


def build_client(settings: GeminiSettings) -> genai.Client:
    """Create the Gemini client, with a placeholder key if none is configured."""
    # The SDK warns about automatic function calling on every generate_content
    # call; it does not apply to TTS and it breaks the CLI's progress lines.
    logging.getLogger("google_genai.models").setLevel(logging.ERROR)
    return genai.Client(api_key=settings.api_key or PLACEHOLDER_API_KEY)


def generation_config(settings: GeminiSettings) -> types.GenerateContentConfig:
    """Two-speaker audio config; speaker names must match the prompt labels."""
    voices = {"Host": settings.voice_host, "Guest": settings.voice_guest}
    return types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker=speaker,
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        ),
                    )
                    for speaker, voice in voices.items()
                ]
            )
        ),
    )


def render_segment(
    client: genai.Client, settings: GeminiSettings, segment: Segment
) -> SegmentAudio:
    """Send one segment to Gemini and return its PCM audio.

    Args:
        client: A Gemini client.
        settings: Model and voice names.
        segment: The segment to voice.

    Returns:
        The segment's audio and token counts.

    Raises:
        AudioError: If the response carries no inline audio.
    """
    prompt = segment.as_prompt()
    response = client.models.generate_content(
        model=settings.model, contents=prompt, config=generation_config(settings)
    )
    try:
        part = response.candidates[0].content.parts[0]
        blob = part.inline_data
        data = blob.data
    except (AttributeError, IndexError, TypeError) as exc:
        raise AudioError(f"segment {segment.name!r}: no audio in response") from exc
    if not data:
        raise AudioError(f"segment {segment.name!r}: empty audio in response")
    mime = getattr(blob, "mime_type", "") or ""
    if mime and not mime.startswith("audio/"):
        raise AudioError(f"segment {segment.name!r}: unexpected mime type {mime}")
    usage = getattr(response, "usage_metadata", None)
    return SegmentAudio(
        name=segment.name,
        pcm=bytes(data),
        characters=len(prompt),
        prompt_tokens=getattr(usage, "prompt_token_count", None),
        audio_tokens=getattr(usage, "candidates_token_count", None),
    )


def estimate_cost_usd(settings: GeminiSettings, rendered: list[SegmentAudio]) -> float:
    """Estimate the TTS bill from token counts and the configured prices.

    Segments without token counts contribute nothing; the log shows the
    counts so the gap is visible.
    """
    prompt = sum(item.prompt_tokens or 0 for item in rendered)
    audio = sum(item.audio_tokens or 0 for item in rendered)
    return (
        prompt * settings.usd_per_million_input_tokens
        + audio * settings.usd_per_million_audio_tokens
    ) / 1_000_000
