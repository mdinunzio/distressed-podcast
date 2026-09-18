"""Pydantic model for ``episodes/<slug>/script.json``.

The script is written by the ``script`` skill and validated here before any
audio is generated, so a malformed script fails loudly and never produces a
partial episode.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Speaker = Literal["Host", "Guest"]
"""The two speaker labels. They must match the Gemini speaker config names."""


class Turn(BaseModel):
    """One spoken line by one host."""

    model_config = ConfigDict(extra="forbid")

    speaker: Speaker
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def _strip_text(cls, value: str) -> str:
        """Reject whitespace-only lines."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("turn text must not be blank")
        return stripped

    @property
    def word_count(self) -> int:
        """Number of whitespace-separated words in this turn."""
        return len(self.text.split())


class Segment(BaseModel):
    """A 2-4 minute block of dialogue rendered as one TTS request."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    direction: str = Field(min_length=1, description="Pace/mood note for TTS.")
    turns: list[Turn] = Field(min_length=1)

    @property
    def word_count(self) -> int:
        """Total words spoken in this segment."""
        return sum(turn.word_count for turn in self.turns)

    def as_prompt(self) -> str:
        """Render the segment as the text sent to the TTS model.

        Returns:
            The direction line, a blank line, then one ``Speaker: text`` line
            per turn.
        """
        lines = [f"{turn.speaker}: {turn.text}" for turn in self.turns]
        return f"{self.direction}\n\n" + "\n".join(lines)


class Script(BaseModel):
    """A whole episode: metadata plus ordered segments."""

    model_config = ConfigDict(extra="forbid")

    company: str = Field(min_length=1)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1)
    deal_type: str = Field(min_length=1)
    episode: int | None = Field(
        default=None, ge=1, description="Episode number; becomes the ID3 track."
    )
    segments: list[Segment] = Field(min_length=1)

    @property
    def word_count(self) -> int:
        """Total words spoken in the episode."""
        return sum(segment.word_count for segment in self.segments)

    @property
    def character_count(self) -> int:
        """Characters that would be sent to the TTS model across all segments."""
        return sum(len(segment.as_prompt()) for segment in self.segments)

    @classmethod
    def load(cls, path: Path) -> "Script":
        """Read and validate a ``script.json`` file.

        Args:
            path: Path to the JSON file.

        Returns:
            The validated script.

        Raises:
            FileNotFoundError: If ``path`` does not exist.
            pydantic.ValidationError: If the JSON does not match the model.
        """
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        return cls.model_validate(data)
