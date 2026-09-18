"""Tests for the Script model."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from distressed_podcast.models import Script, Segment, Turn


def test_load_valid_script(script_path: Path) -> None:
    script = Script.load(script_path)
    assert script.slug == "example-co"
    assert [segment.name for segment in script.segments] == ["situation", "watch"]
    assert script.segments[0].turns[1].speaker == "Guest"


def test_word_and_character_counts(script_dict: dict) -> None:
    script = Script.model_validate(script_dict)
    assert script.segments[0].word_count == 4 + 4
    assert script.word_count == 8 + 5
    assert script.character_count == sum(
        len(segment.as_prompt()) for segment in script.segments
    )


def test_segment_prompt_has_direction_then_labelled_lines() -> None:
    segment = Segment(
        name="situation",
        direction="Slow.",
        turns=[Turn(speaker="Host", text="Hi."), Turn(speaker="Guest", text="Hey.")],
    )
    assert segment.as_prompt() == "Slow.\n\nHost: Hi.\nGuest: Hey."


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.__setitem__("slug", "Bad Slug"),
        lambda d: d.__setitem__("segments", []),
        lambda d: d["segments"][0]["turns"].append(
            {"speaker": "Narrator", "text": "x"}
        ),
        lambda d: d["segments"][0]["turns"].append({"speaker": "Host", "text": "   "}),
        lambda d: d["segments"][0].__setitem__("direction", ""),
        lambda d: d.__setitem__("extra", 1),
        lambda d: d.pop("deal_type"),
    ],
    ids=[
        "slug-format",
        "no-segments",
        "unknown-speaker",
        "blank-text",
        "empty-direction",
        "extra-key",
        "missing-deal-type",
    ],
)
def test_invalid_scripts_are_rejected(script_dict: dict, mutate) -> None:
    mutate(script_dict)
    with pytest.raises(ValidationError):
        Script.model_validate(script_dict)


def test_text_is_stripped(script_dict: dict) -> None:
    script_dict["segments"][0]["turns"][0]["text"] = "  padded  "
    script = Script.model_validate(script_dict)
    assert script.segments[0].turns[0].text == "padded"


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Script.load(tmp_path / "missing.json")
