"""Tests for folding quiz attempts into the ledger."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from distressed_podcast import config, progress
from distressed_podcast.cli import main
from distressed_podcast.models import Ledger


def _attempt(aid: str, when: str, results: dict[str, bool]) -> dict:
    return {
        "id": aid,
        "slug": "example-co",
        "episode": 1,
        "started_at": when,
        "finished_at": when,
        "score": sum(results.values()),
        "total": len(results),
        "answers": [
            {
                "q": f"q{i:02d}",
                "type": "multiple_choice",
                "correct": ok,
                "concept_ids": [cid],
            }
            for i, (cid, ok) in enumerate(results.items(), start=1)
        ],
    }


@pytest.fixture
def ledger_tree(
    tmp_path: Path, ledger_dict: dict, monkeypatch: pytest.MonkeyPatch
) -> dict[str, Path]:
    ledger = tmp_path / "concepts" / "ledger.json"
    ledger.parent.mkdir()
    ledger.write_text(json.dumps(ledger_dict), encoding="utf-8")
    state = tmp_path / "concepts" / "progress.json"
    monkeypatch.setattr(config, "LEDGER_PATH", ledger)
    monkeypatch.setattr(config, "PROGRESS_PATH", state)
    return {"ledger": ledger, "state": state, "root": tmp_path}


def test_wrong_then_right_updates_status_and_history(ledger_tree) -> None:
    attempts = ledger_tree["root"] / "attempts.json"
    attempts.write_text(
        json.dumps(
            [
                _attempt("a2", "2026-02-02T10:00:00Z", {"fulcrum_security": True}),
                _attempt(
                    "a1",
                    "2026-02-01T10:00:00Z",
                    {"fulcrum_security": False, "ebitda": False},
                ),
            ]
        )
    )
    result = progress.sync(attempts, ledger_tree["ledger"], ledger_tree["state"])
    assert result.applied == ["a1", "a2"]  # oldest first regardless of file order
    assert result.needs_reteach == ["ebitda"]
    assert result.mastered == ["fulcrum_security"]
    ledger = Ledger.load(ledger_tree["ledger"])
    fulcrum = ledger.get("fulcrum_security")
    assert fulcrum.status == "mastered"
    assert [h.event for h in fulcrum.history] == [
        "introduced",
        "tested_wrong",
        "tested_correct",
    ]
    assert fulcrum.history[-1].date == "2026-02-02"
    state = progress.ProgressState.load(ledger_tree["state"])
    assert state.synced_attempts == ["a1", "a2"] and state.updated == "2026-02-02"


def test_resync_is_idempotent(ledger_tree) -> None:
    attempts = ledger_tree["root"] / "attempts.json"
    attempts.write_text(
        json.dumps([_attempt("a1", "2026-02-01T10:00:00Z", {"ebitda": False})])
    )
    progress.sync(attempts, ledger_tree["ledger"], ledger_tree["state"])
    again = progress.sync(attempts, ledger_tree["ledger"], ledger_tree["state"])
    assert again.applied == [] and again.skipped == ["a1"]
    assert len(Ledger.load(ledger_tree["ledger"]).get("ebitda").history) == 1


def test_one_wrong_answer_marks_concept_for_reteach(ledger_tree) -> None:
    attempt = _attempt("a1", "2026-02-01T10:00:00Z", {"ebitda": True})
    attempt["answers"].append(
        {"q": "q02", "correct": False, "concept_ids": ["ebitda", "not_in_ledger"]}
    )
    attempts = ledger_tree["root"] / "attempts.json"
    attempts.write_text(json.dumps({"attempts": [attempt]}))
    result = progress.sync(attempts, ledger_tree["ledger"], ledger_tree["state"])
    assert result.needs_reteach == ["ebitda"]
    assert result.unknown_concepts == {"not_in_ledger"}


def test_directory_of_documents(ledger_tree) -> None:
    folder = ledger_tree["root"] / "export" / "attempts"
    folder.mkdir(parents=True)
    (folder / "a1.json").write_text(
        json.dumps(_attempt("a1", "2026-02-01T10:00:00Z", {"ebitda": False}))
    )
    (folder / "a2.json").write_text(
        json.dumps(_attempt("a2", "2026-02-03T10:00:00Z", {"ebitda": True}))
    )
    result = progress.sync(
        ledger_tree["root"] / "export", ledger_tree["ledger"], ledger_tree["state"]
    )
    assert result.applied == ["a1", "a2"] and result.mastered == ["ebitda"]


@pytest.mark.parametrize(
    "content, message",
    [
        ("not json", "not valid JSON"),
        ('[{"id": "a1"}]', "malformed attempt"),
        ("42", "expected an attempt"),
    ],
)
def test_bad_attempts_fail_and_write_nothing(ledger_tree, content, message) -> None:
    attempts = ledger_tree["root"] / "attempts.json"
    attempts.write_text(content)
    before = ledger_tree["ledger"].read_text()
    with pytest.raises(progress.ProgressError, match=message):
        progress.sync(attempts, ledger_tree["ledger"], ledger_tree["state"])
    assert ledger_tree["ledger"].read_text() == before
    assert not ledger_tree["state"].exists()


def test_progress_command(ledger_tree) -> None:
    attempts = ledger_tree["root"] / "attempts.json"
    attempts.write_text(
        json.dumps(
            [
                _attempt(
                    "a1",
                    "2026-02-01T10:00:00Z",
                    {"ebitda": False, "fulcrum_security": True},
                )
            ]
        )
    )
    result = CliRunner().invoke(main, ["progress", str(attempts)])
    assert result.exit_code == 0, result.output
    assert "applied 1 attempt(s)" in result.output
    assert "needs re-teaching: ebitda" in result.output
    assert "mastered: 1" in result.output
