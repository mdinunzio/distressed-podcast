"""Pydantic models for the files Claude writes: script, quiz and ledger.

``episodes/<slug>/script.json`` is validated before any audio is generated,
``episodes/<slug>/quiz.json`` and ``concepts/ledger.json`` before the quiz
site is built, so a malformed file fails loudly and never produces a partial
output.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Speaker = Literal["Host", "Guest"]
"""The two speaker labels. They must match the Gemini speaker config names."""

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
CONCEPT_ID_PATTERN = r"^[a-z0-9]+(?:_[a-z0-9]+)*$"
QUESTIONS_PER_QUIZ = 20


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


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
    slug: str = Field(pattern=SLUG_PATTERN)
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
        return cls.model_validate(_load_json(path))


# --- Concept ledger -----------------------------------------------------------

Tier = Literal[
    "accounting", "capital_structure", "legal", "process", "valuation", "trading"
]
"""Which part of the desk's toolkit a concept belongs to."""

ConceptStatus = Literal["introduced", "mastered", "needs_reteach"]
"""Where a concept stands with the listener; a concept absent from the ledger
is ``new`` and gets a full gentle explanation the first time it comes up."""

HistoryEvent = Literal["introduced", "retaught", "tested_correct", "tested_wrong"]


class HistoryEntry(BaseModel):
    """One dated event in a concept's life: taught, retaught, or tested."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(pattern=SLUG_PATTERN)
    episode: int = Field(ge=1)
    event: HistoryEvent
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class Concept(BaseModel):
    """A term the podcast has explained on air, and how well it landed."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=CONCEPT_ID_PATTERN)
    name: str = Field(min_length=1)
    one_line: str = Field(min_length=1, description="Dictionary definition.")
    tier: Tier
    level: int = Field(ge=1, le=5, description="1 beginner … 5 expert.")
    moyer: str | None = Field(default=None, description="Where Moyer covers it.")
    aliases: list[str] = Field(default_factory=list)
    introduced_in: str = Field(pattern=SLUG_PATTERN)
    episode: int = Field(ge=1, description="Episode that first explained it.")
    status: ConceptStatus = "introduced"
    history: list[HistoryEntry] = Field(default_factory=list)


class Ledger(BaseModel):
    """``concepts/ledger.json``: every concept explained so far."""

    model_config = ConfigDict(extra="forbid")

    concepts: list[Concept] = Field(default_factory=list)

    @field_validator("concepts")
    @classmethod
    def _unique_ids(cls, value: list[Concept]) -> list[Concept]:
        """Reject duplicate concept ids."""
        seen: set[str] = set()
        for concept in value:
            if concept.id in seen:
                raise ValueError(f"duplicate concept id {concept.id!r}")
            seen.add(concept.id)
        return value

    @property
    def ids(self) -> set[str]:
        """The set of concept ids in the ledger."""
        return {concept.id for concept in self.concepts}

    def get(self, concept_id: str) -> Concept | None:
        """Return the concept with ``concept_id`` or ``None``."""
        for concept in self.concepts:
            if concept.id == concept_id:
                return concept
        return None

    @classmethod
    def load(cls, path: Path) -> "Ledger":
        """Read and validate a ``ledger.json`` file.

        Args:
            path: Path to the JSON file.

        Returns:
            The validated ledger.
        """
        return cls.model_validate(_load_json(path))


# --- Quiz ---------------------------------------------------------------------


class _QuestionBase(BaseModel):
    """Fields every question type shares."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^q\d{2}$")
    level: int = Field(ge=1, le=5, description="1 beginner … 5 expert.")
    concept_ids: list[str] = Field(min_length=1)
    retest: bool = Field(
        default=False, description="Re-tests a concept the listener missed before."
    )
    prompt: str = Field(min_length=1)
    explanation: str = Field(min_length=1, description="Shown after answering.")

    @field_validator("concept_ids")
    @classmethod
    def _concept_ids_well_formed(cls, value: list[str]) -> list[str]:
        """Concept ids must be ledger-style ids, without duplicates."""
        for item in value:
            if not re.fullmatch(CONCEPT_ID_PATTERN, item):
                raise ValueError(f"bad concept id {item!r}")
        if len(set(value)) != len(value):
            raise ValueError("duplicate concept ids")
        return value


class MultipleChoice(_QuestionBase):
    """Pick one of three to five choices."""

    type: Literal["multiple_choice"]
    choices: list[str] = Field(min_length=3, max_length=5)
    answer: int = Field(ge=0, description="Index into ``choices``.")

    @model_validator(mode="after")
    def _answer_in_range(self) -> "MultipleChoice":
        """The answer must point at a choice."""
        if self.answer >= len(self.choices):
            raise ValueError("answer index out of range")
        if len(set(self.choices)) != len(self.choices):
            raise ValueError("duplicate choices")
        return self


class Numeric(_QuestionBase):
    """Type a number; correct within ``tolerance`` of ``answer``."""

    type: Literal["numeric"]
    answer: float
    tolerance: float = Field(ge=0)
    unit: str = Field(min_length=1, description="Shown next to the input.")


class ShortText(_QuestionBase):
    """Type a word or phrase; matched case-insensitively against ``accepted``."""

    type: Literal["short_text"]
    accepted: list[str] = Field(min_length=1)

    @field_validator("accepted")
    @classmethod
    def _non_blank(cls, value: list[str]) -> list[str]:
        """Every accepted answer must have content."""
        cleaned = [item.strip() for item in value]
        if any(not item for item in cleaned):
            raise ValueError("blank accepted answer")
        return cleaned


class Order(_QuestionBase):
    """Put ``items`` (given here in the correct order) into order."""

    type: Literal["order"]
    items: list[str] = Field(min_length=3, max_length=8)

    @field_validator("items")
    @classmethod
    def _unique_items(cls, value: list[str]) -> list[str]:
        """Items must be distinct or the order is ambiguous."""
        if len(set(value)) != len(value):
            raise ValueError("duplicate items")
        return value


Question = Annotated[
    MultipleChoice | Numeric | ShortText | Order, Field(discriminator="type")
]


class Quiz(BaseModel):
    """``episodes/<slug>/quiz.json``: the 20 questions for one episode."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(pattern=SLUG_PATTERN)
    episode: int = Field(ge=1)
    title: str = Field(min_length=1)
    questions: list[Question] = Field(
        min_length=QUESTIONS_PER_QUIZ, max_length=QUESTIONS_PER_QUIZ
    )

    @field_validator("questions")
    @classmethod
    def _unique_question_ids(cls, value: list) -> list:
        """Question ids must be unique within a quiz."""
        ids = [question.id for question in value]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate question ids")
        return value

    @property
    def concept_ids(self) -> set[str]:
        """Every concept id any question tests."""
        return {cid for question in self.questions for cid in question.concept_ids}

    @classmethod
    def load(cls, path: Path) -> "Quiz":
        """Read and validate a ``quiz.json`` file.

        Args:
            path: Path to the JSON file.

        Returns:
            The validated quiz.
        """
        return cls.model_validate(_load_json(path))
