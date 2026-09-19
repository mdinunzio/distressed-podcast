"""Shared fixtures: a small valid script and a temporary episodes directory."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from distressed_podcast import config


@pytest.fixture
def script_dict() -> dict:
    """A minimal valid script as a plain dict."""
    return {
        "company": "Example Co",
        "slug": "example-co",
        "title": "Example Co: A Test Episode",
        "deal_type": "prearranged Chapter 11",
        "segments": [
            {
                "name": "situation",
                "direction": "Calm and clear.",
                "turns": [
                    {"speaker": "Host", "text": "Welcome to the show."},
                    {"speaker": "Guest", "text": "Glad to be here."},
                ],
            },
            {
                "name": "watch",
                "direction": "Brisk wrap-up.",
                "turns": [
                    {"speaker": "Host", "text": "Watch the hearing on Friday."},
                ],
            },
        ],
    }


def _question(index: int, kind: str) -> dict:
    base = {
        "id": f"q{index:02d}",
        "type": kind,
        "level": 1 + index % 5,
        "concept_ids": ["fulcrum_security"],
        "prompt": f"Question {index}?",
        "explanation": "Because.",
    }
    if kind == "multiple_choice":
        base.update(choices=["A", "B", "C"], answer=1)
    elif kind == "numeric":
        base.update(answer=2.6, tolerance=0.2, unit="$ billions")
    elif kind == "short_text":
        base.update(accepted=["fulcrum", "fulcrum security"])
    else:
        base.update(items=["ABL", "First lien", "Unsecured", "Common"])
    return base


@pytest.fixture
def quiz_dict() -> dict:
    """A minimal valid 20-question quiz as a plain dict."""
    kinds = ["multiple_choice", "numeric", "short_text", "order"]
    return {
        "slug": "example-co",
        "episode": 1,
        "title": "Example Co quiz",
        "questions": [_question(i, kinds[i % 4]) for i in range(1, 21)],
    }


@pytest.fixture
def ledger_dict() -> dict:
    """A minimal valid ledger as a plain dict."""
    return {
        "concepts": [
            {
                "id": "fulcrum_security",
                "name": "Fulcrum security",
                "one_line": "The class where enterprise value runs out.",
                "tier": "valuation",
                "level": 2,
                "moyer": "Chapter 4",
                "introduced_in": "example-co",
                "episode": 1,
                "status": "introduced",
                "history": [
                    {
                        "slug": "example-co",
                        "episode": 1,
                        "event": "introduced",
                        "date": "2026-01-01",
                    }
                ],
            },
            {
                "id": "ebitda",
                "name": "EBITDA",
                "one_line": "Earnings before interest, tax, D and A.",
                "tier": "accounting",
                "level": 1,
                "introduced_in": "example-co",
                "episode": 1,
            },
        ]
    }


@pytest.fixture
def episodes_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point ``config.EPISODES_DIR`` at a temporary directory."""
    root = tmp_path / "episodes"
    root.mkdir()
    monkeypatch.setattr(config, "EPISODES_DIR", root)
    return root


@pytest.fixture
def script_path(episodes_dir: Path, script_dict: dict) -> Path:
    """Write ``script_dict`` to ``<episodes_dir>/example-co/script.json``."""
    folder = episodes_dir / script_dict["slug"]
    folder.mkdir()
    path = folder / "script.json"
    path.write_text(json.dumps(script_dict), encoding="utf-8")
    return path


@pytest.fixture
def site_tree(
    tmp_path: Path,
    episodes_dir: Path,
    script_path: Path,
    script_dict: dict,
    quiz_dict: dict,
    ledger_dict: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, Path]:
    """A template, ledger and one episode with script + quiz, wired into config."""
    script_dict["episode"] = 1
    script_path.write_text(json.dumps(script_dict), encoding="utf-8")
    (script_path.parent / "quiz.json").write_text(
        json.dumps(quiz_dict), encoding="utf-8"
    )
    ledger = tmp_path / "concepts" / "ledger.json"
    ledger.parent.mkdir()
    ledger.write_text(json.dumps(ledger_dict), encoding="utf-8")
    template = tmp_path / "quiz" / "index.html"
    template.parent.mkdir()
    template.write_text(
        '<title>T</title><script id="podcast-data" type="application/json">'
        '"__DISTRESSED_DATA__"</script>',
        encoding="utf-8",
    )
    output = tmp_path / "quiz" / "build" / "index.html"
    monkeypatch.setattr(config, "LEDGER_PATH", ledger)
    monkeypatch.setattr(config, "SITE_TEMPLATE", template)
    monkeypatch.setattr(config, "SITE_OUTPUT", output)
    return {
        "ledger": ledger,
        "template": template,
        "output": output,
        "quiz": script_path.parent / "quiz.json",
        "script": script_path,
    }


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every provider variable so each test sets only what it needs."""
    for name in (
        "GEMINI_API_KEY",
        "GEMINI_TTS_MODEL",
        "GEMINI_VOICE_HOST",
        "GEMINI_VOICE_GUEST",
        "S3_ENDPOINT_URL",
        "S3_REGION",
        "S3_BUCKET",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
