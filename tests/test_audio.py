"""Tests for the Gemini TTS wrapper, with ``genai.Client`` mocked."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from distressed_podcast import audio
from distressed_podcast.config import GeminiSettings
from distressed_podcast.models import Segment, Turn

SETTINGS = GeminiSettings(
    api_key="key", model="tts-model", voice_host="Charon", voice_guest="Puck"
)
SEGMENT = Segment(
    name="situation",
    direction="Calm.",
    turns=[Turn(speaker="Host", text="Hello."), Turn(speaker="Guest", text="Hi.")],
)


def _response(data: bytes | None, mime: str = "audio/L16;codec=pcm;rate=24000"):
    blob = SimpleNamespace(data=data, mime_type=mime)
    part = SimpleNamespace(inline_data=blob)
    return SimpleNamespace(
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))],
        usage_metadata=SimpleNamespace(
            prompt_token_count=40, candidates_token_count=1200
        ),
    )


class FakeModels:
    def __init__(self, response):
        self.response = response
        self.calls: list[dict] = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeClient:
    instances: list["FakeClient"] = []

    def __init__(self, api_key: str, response=None):
        self.api_key = api_key
        self.models = FakeModels(response)
        FakeClient.instances.append(self)


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch):
    FakeClient.instances.clear()
    monkeypatch.setattr(audio.genai, "Client", FakeClient)
    return FakeClient


def test_build_client_uses_placeholder_without_key(fake_client) -> None:
    settings = GeminiSettings(
        api_key=None, model="m", voice_host="Charon", voice_guest="Puck"
    )
    client = audio.build_client(settings)
    assert client.api_key == audio.PLACEHOLDER_API_KEY
    assert audio.build_client(SETTINGS).api_key == "key"


def test_generation_config_names_both_speakers() -> None:
    config = audio.generation_config(SETTINGS)
    assert config.response_modalities == ["AUDIO"]
    speakers = config.speech_config.multi_speaker_voice_config.speaker_voice_configs
    assert [
        (s.speaker, s.voice_config.prebuilt_voice_config.voice_name) for s in speakers
    ] == [
        ("Host", "Charon"),
        ("Guest", "Puck"),
    ]


def test_render_segment_sends_prompt_and_returns_pcm(fake_client) -> None:
    pcm = b"\x00\x01" * 24_000
    client = fake_client("key", response=_response(pcm))
    item = audio.render_segment(client, SETTINGS, SEGMENT)
    call = client.models.calls[0]
    assert call["model"] == "tts-model"
    assert call["contents"] == SEGMENT.as_prompt()
    assert call["config"].speech_config is not None
    assert item.pcm == pcm
    assert item.seconds == pytest.approx(1.0)
    assert item.characters == len(SEGMENT.as_prompt())
    assert (item.prompt_tokens, item.audio_tokens) == (40, 1200)


@pytest.mark.parametrize(
    "response",
    [
        _response(None),
        _response(b""),
        _response(b"x", mime="text/plain"),
        SimpleNamespace(candidates=[]),
    ],
    ids=["no-data", "empty", "wrong-mime", "no-candidates"],
)
def test_render_segment_rejects_bad_responses(fake_client, response) -> None:
    client = fake_client("key", response=response)
    with pytest.raises(audio.AudioError):
        audio.render_segment(client, SETTINGS, SEGMENT)


def test_estimate_cost() -> None:
    items = [
        audio.SegmentAudio("a", b"", 10, 1_000_000, 100_000),
        audio.SegmentAudio("b", b"", 10, None, None),
    ]
    settings = GeminiSettings(
        api_key="k",
        model="m",
        voice_host="a",
        voice_guest="b",
        usd_per_million_input_tokens=0.5,
        usd_per_million_audio_tokens=10.0,
    )
    assert audio.estimate_cost_usd(settings, items) == pytest.approx(0.5 + 1.0)
