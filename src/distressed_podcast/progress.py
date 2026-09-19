"""Apply quiz attempts to the concept ledger.

The quiz page records one attempt per completed quiz. The ``progress`` skill
fetches those attempts (from the artifact's database, or from a JSON export
the listener pasted into the repo) and this module folds them into
``concepts/ledger.json``: a concept answered wrong in the listener's latest
attempt is marked ``needs_reteach``; answered right, ``mastered``. Which
attempts have already been applied is remembered in ``concepts/progress.json``
so a re-run is idempotent.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from distressed_podcast.models import SLUG_PATTERN, HistoryEntry, Ledger


class ProgressError(RuntimeError):
    """An attempts file is missing or malformed."""


class Answer(BaseModel):
    """One graded question inside an attempt; extra page fields are kept."""

    model_config = ConfigDict(extra="allow")

    q: str
    correct: bool
    concept_ids: list[str]


class Attempt(BaseModel):
    """One completed quiz, as the page stores it."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1)
    slug: str = Field(pattern=SLUG_PATTERN)
    episode: int = Field(ge=1)
    finished_at: str = Field(min_length=10)
    score: int = Field(ge=0)
    total: int = Field(ge=1)
    answers: list[Answer]


class ProgressState(BaseModel):
    """``concepts/progress.json``: which attempts the ledger already reflects."""

    model_config = ConfigDict(extra="forbid")

    synced_attempts: list[str] = Field(default_factory=list)
    updated: str | None = None

    @classmethod
    def load(cls, path: Path) -> "ProgressState":
        """Read the state file, or return an empty state if it does not exist."""
        if not path.exists():
            return cls()
        with path.open(encoding="utf-8") as handle:
            return cls.model_validate(json.load(handle))


@dataclass
class SyncResult:
    """What one sync did."""

    applied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    unknown_concepts: set[str] = field(default_factory=set)
    needs_reteach: list[str] = field(default_factory=list)
    mastered: list[str] = field(default_factory=list)


def _attempts_from_value(value, source: str) -> list[dict]:
    if isinstance(value, dict) and "attempts" in value:
        value = value["attempts"]
    if isinstance(value, dict):
        # A single ArtifactData document, or a {id: attempt} map.
        if "answers" in value:
            return [value]
        return [v for v in value.values() if isinstance(v, dict)]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, dict)]
    raise ProgressError(f"{source}: expected an attempt, a list or an object")


def load_attempts(path: Path) -> list[Attempt]:
    """Read attempts from a JSON file or a directory of JSON files.

    Accepts the page's export (a list), a ``{"attempts": [...]}`` wrapper, one
    attempt per file (as ``ArtifactData`` writes them with ``out_dir``), or an
    ``{id: attempt}`` map. Duplicate ids keep the first occurrence.

    Args:
        path: A ``.json`` file or a directory searched recursively.

    Returns:
        Validated attempts, oldest first.

    Raises:
        ProgressError: If nothing is found or an attempt is malformed.
    """
    files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
    if not files or not all(f.exists() for f in files):
        raise ProgressError(f"{path}: no attempts found")
    raw: list[dict] = []
    for file in files:
        try:
            with file.open(encoding="utf-8") as handle:
                raw.extend(_attempts_from_value(json.load(handle), str(file)))
        except json.JSONDecodeError as exc:
            raise ProgressError(f"{file}: not valid JSON ({exc})")
    attempts: dict[str, Attempt] = {}
    for item in raw:
        try:
            attempt = Attempt.model_validate(item)
        except ValidationError as exc:
            raise ProgressError(f"{path}: malformed attempt:\n{exc}")
        attempts.setdefault(attempt.id, attempt)
    return sorted(attempts.values(), key=lambda a: (a.finished_at, a.id))


def apply(ledger: Ledger, state: ProgressState, attempts: list[Attempt]) -> SyncResult:
    """Fold unsynced attempts into the ledger in place.

    Args:
        ledger: The ledger to update.
        state: The sync state; updated in place with the applied attempt ids.
        attempts: Attempts, oldest first.

    Returns:
        A summary; ``needs_reteach`` and ``mastered`` list the concept ids in
        each state after the sync, ledger order.
    """
    result = SyncResult()
    synced = set(state.synced_attempts)
    for attempt in attempts:
        if attempt.id in synced:
            result.skipped.append(attempt.id)
            continue
        outcome: dict[str, bool] = {}
        for answer in attempt.answers:
            for cid in answer.concept_ids:
                outcome[cid] = outcome.get(cid, True) and answer.correct
        for cid, correct in outcome.items():
            concept = ledger.get(cid)
            if concept is None:
                result.unknown_concepts.add(cid)
                continue
            concept.status = "mastered" if correct else "needs_reteach"
            concept.history.append(
                HistoryEntry(
                    slug=attempt.slug,
                    episode=attempt.episode,
                    event="tested_correct" if correct else "tested_wrong",
                    date=attempt.finished_at[:10],
                )
            )
        synced.add(attempt.id)
        state.synced_attempts.append(attempt.id)
        result.applied.append(attempt.id)
    if result.applied:
        state.updated = max(a.finished_at for a in attempts)[:10]
    result.needs_reteach = [
        c.id for c in ledger.concepts if c.status == "needs_reteach"
    ]
    result.mastered = [c.id for c in ledger.concepts if c.status == "mastered"]
    return result


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def sync(attempts_path: Path, ledger_path: Path, state_path: Path) -> SyncResult:
    """Load everything, apply, and write the ledger and state atomically.

    Args:
        attempts_path: JSON file or directory of attempts.
        ledger_path: ``concepts/ledger.json``.
        state_path: ``concepts/progress.json``.

    Returns:
        The sync summary.

    Raises:
        ProgressError: On malformed input; nothing is written in that case.
    """
    try:
        ledger = Ledger.load(ledger_path)
    except FileNotFoundError:
        raise ProgressError(f"{ledger_path} not found")
    except ValidationError as exc:
        raise ProgressError(f"{ledger_path} is not a valid ledger:\n{exc}")
    try:
        state = ProgressState.load(state_path)
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ProgressError(f"{state_path} is not valid:\n{exc}")
    attempts = load_attempts(attempts_path)
    result = apply(ledger, state, attempts)
    if result.applied:
        _write_json(ledger_path, ledger.model_dump(mode="json"))
        _write_json(state_path, state.model_dump(mode="json"))
    return result
