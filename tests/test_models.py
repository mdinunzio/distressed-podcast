"""Tests for the Script model."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from distressed_podcast.models import Ledger, Quiz, Script, Segment, Turn


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


def test_episode_number_is_optional_and_positive(script_dict: dict) -> None:
    assert Script.model_validate(script_dict).episode is None
    script_dict["episode"] = 3
    assert Script.model_validate(script_dict).episode == 3
    script_dict["episode"] = 0
    with pytest.raises(ValidationError):
        Script.model_validate(script_dict)


def test_text_is_stripped(script_dict: dict) -> None:
    script_dict["segments"][0]["turns"][0]["text"] = "  padded  "
    script = Script.model_validate(script_dict)
    assert script.segments[0].turns[0].text == "padded"


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Script.load(tmp_path / "missing.json")


# --- Ledger -------------------------------------------------------------------


def test_ledger_loads_and_defaults(ledger_dict: dict) -> None:
    ledger = Ledger.model_validate(ledger_dict)
    assert ledger.ids == {"fulcrum_security", "ebitda"}
    ebitda = ledger.get("ebitda")
    assert ebitda is not None
    assert ebitda.status == "introduced"
    assert ebitda.moyer is None and ebitda.history == []
    assert ledger.get("nope") is None


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["concepts"].append(dict(d["concepts"][0])),
        lambda d: d["concepts"][0].__setitem__("id", "Fulcrum-Security"),
        lambda d: d["concepts"][0].__setitem__("status", "forgotten"),
        lambda d: d["concepts"][0].__setitem__("level", 6),
        lambda d: d["concepts"][0].__setitem__("tier", "vibes"),
        lambda d: d["concepts"][0]["history"][0].__setitem__("date", "Jan 1"),
        lambda d: d["concepts"][0].__setitem__("extra", 1),
    ],
    ids=["duplicate-id", "id-format", "status", "level", "tier", "date", "extra"],
)
def test_invalid_ledgers_are_rejected(ledger_dict: dict, mutate) -> None:
    mutate(ledger_dict)
    with pytest.raises(ValidationError):
        Ledger.model_validate(ledger_dict)


# --- Quiz ---------------------------------------------------------------------


def test_quiz_loads_all_four_types(quiz_dict: dict) -> None:
    quiz = Quiz.model_validate(quiz_dict)
    assert len(quiz.questions) == 20
    assert {q.type for q in quiz.questions} == {
        "multiple_choice",
        "numeric",
        "short_text",
        "order",
    }
    assert quiz.concept_ids == {"fulcrum_security"}
    assert quiz.questions[0].retest is False


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["questions"].pop(),
        lambda d: d["questions"].__setitem__(1, dict(d["questions"][0])),
        # Fixture order: q01 numeric, q02 short_text, q03 order, q04 multiple_choice.
        lambda d: d["questions"][3].__setitem__("answer", 3),
        lambda d: d["questions"][3].__setitem__("choices", ["A", "A", "B"]),
        lambda d: d["questions"][3].update(
            choices=["Short", "A much longer and more detailed answer", "Brief"],
            answer=1,
        ),
        lambda d: d["questions"][3].update(
            choices=["A long distractor here", "A", "Another long distractor"],
            answer=1,
        ),
        lambda d: [
            q.__setitem__("answer", 1)
            for q in d["questions"]
            if q["type"] == "multiple_choice"
        ],
        lambda d: [
            q.update(choices=["Alpha", "Bravo", "Delta plus"], answer=2)
            for q in d["questions"]
            if q["type"] == "multiple_choice"
        ],
        lambda d: d["questions"][0].__setitem__("tolerance", -1),
        lambda d: d["questions"][1].__setitem__("accepted", [" "]),
        lambda d: d["questions"][2].__setitem__("items", ["A", "B", "A"]),
        lambda d: d["questions"][0].__setitem__("type", "essay"),
        lambda d: d["questions"][0].__setitem__("concept_ids", []),
        lambda d: d["questions"][0].__setitem__("concept_ids", ["Bad Id"]),
        lambda d: d["questions"][0].__setitem__("id", "question1"),
        lambda d: d["questions"][0].__setitem__("level", 0),
    ],
    ids=[
        "nineteen-questions",
        "duplicate-question-id",
        "answer-out-of-range",
        "duplicate-choices",
        "answer-longest-by-far",
        "answer-shortest-by-far",
        "answers-all-in-one-position",
        "answer-always-longest",
        "negative-tolerance",
        "blank-accepted",
        "duplicate-order-items",
        "unknown-type",
        "no-concepts",
        "bad-concept-id",
        "question-id-format",
        "level-zero",
    ],
)
def test_invalid_quizzes_are_rejected(quiz_dict: dict, mutate) -> None:
    mutate(quiz_dict)
    with pytest.raises(ValidationError):
        Quiz.model_validate(quiz_dict)
