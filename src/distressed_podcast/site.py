"""Build the single-file quiz site from the ledger and every episode's quiz.

``quiz/index.html`` is the hand-written app with one JSON placeholder. This
module validates every ``episodes/<slug>/quiz.json`` against its script and
against ``concepts/ledger.json``, then embeds the data into a copy of the
template at ``quiz/build/index.html``. The result opens from disk and is what
gets published as the claude.ai artifact.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from distressed_podcast.models import Ledger, Quiz, Script

DATA_PLACEHOLDER = '"__DISTRESSED_DATA__"'
"""The JSON string literal in the template that the build replaces."""


class SiteError(RuntimeError):
    """A quiz, script or ledger is missing, invalid or inconsistent."""


@dataclass(frozen=True)
class EpisodeBundle:
    """One episode's metadata and quiz, ready to embed."""

    slug: str
    episode: int
    title: str
    company: str
    deal_type: str
    quiz: Quiz

    def as_payload(self) -> dict:
        """Plain-JSON form for the page."""
        return {
            "slug": self.slug,
            "episode": self.episode,
            "title": self.title,
            "company": self.company,
            "deal_type": self.deal_type,
            "quiz": self.quiz.model_dump(mode="json"),
        }


@dataclass(frozen=True)
class BuildResult:
    """What ``build`` produced."""

    output: Path
    episodes: int
    concepts: int
    bytes: int


def _load(model, path: Path):
    try:
        return model.load(path)
    except FileNotFoundError:
        raise SiteError(f"{path} not found")
    except ValidationError as exc:
        raise SiteError(f"{path} is not a valid {model.__name__}:\n{exc}")


def collect(episodes_dir: Path, ledger: Ledger) -> list[EpisodeBundle]:
    """Find every episode with a quiz and check it against script and ledger.

    Args:
        episodes_dir: The ``episodes/`` directory.
        ledger: The validated concept ledger.

    Returns:
        Bundles sorted by episode number.

    Raises:
        SiteError: If a quiz has no script, disagrees with it on slug or
            episode number, or tests a concept the ledger does not know.
    """
    bundles: list[EpisodeBundle] = []
    if not episodes_dir.is_dir():
        return bundles
    for quiz_path in sorted(episodes_dir.glob("*/quiz.json")):
        folder = quiz_path.parent
        quiz = _load(Quiz, quiz_path)
        script = _load(Script, folder / "script.json")
        if quiz.slug != folder.name or script.slug != folder.name:
            raise SiteError(
                f"{quiz_path}: slug {quiz.slug!r} / script slug {script.slug!r} "
                f"do not match directory {folder.name!r}"
            )
        if script.episode is None:
            raise SiteError(f"{folder / 'script.json'} has no episode number")
        if quiz.episode != script.episode:
            raise SiteError(
                f"{quiz_path}: episode {quiz.episode} but script says "
                f"{script.episode}"
            )
        unknown = sorted(quiz.concept_ids - ledger.ids)
        if unknown:
            raise SiteError(
                f"{quiz_path} tests concepts missing from the ledger: "
                + ", ".join(unknown)
            )
        bundles.append(
            EpisodeBundle(
                slug=script.slug,
                episode=script.episode,
                title=script.title,
                company=script.company,
                deal_type=script.deal_type,
                quiz=quiz,
            )
        )
    bundles.sort(key=lambda bundle: bundle.episode)
    numbers = [bundle.episode for bundle in bundles]
    if len(set(numbers)) != len(numbers):
        raise SiteError(f"duplicate episode numbers among quizzes: {numbers}")
    return bundles


def payload(ledger: Ledger, bundles: list[EpisodeBundle], now: dt.datetime) -> dict:
    """The JSON object embedded in the page."""
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "ledger": ledger.model_dump(mode="json"),
        "episodes": [bundle.as_payload() for bundle in bundles],
    }


def render(template: str, data: dict) -> str:
    """Embed ``data`` into ``template`` at the placeholder.

    Args:
        template: The page source containing ``DATA_PLACEHOLDER`` once.
        data: The payload to embed.

    Returns:
        The finished page.

    Raises:
        SiteError: If the placeholder is absent or appears more than once.
    """
    if template.count(DATA_PLACEHOLDER) != 1:
        raise SiteError(f"template must contain {DATA_PLACEHOLDER} exactly once")
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Keep the JSON safe inside a <script> element and on one logical line:
    # escape "<" (so "</script>" cannot appear) and the two Unicode line
    # separators, which are legal in JSON but break some JS parsers.
    for raw, escaped in (
        ("<", "\\u003c"),
        (chr(0x2028), "\\u2028"),
        (chr(0x2029), "\\u2029"),
    ):
        encoded = encoded.replace(raw, escaped)
    return template.replace(DATA_PLACEHOLDER, encoded)


def build(
    template_path: Path,
    ledger_path: Path,
    episodes_dir: Path,
    output: Path,
    now: dt.datetime | None = None,
) -> BuildResult:
    """Validate everything and write the finished page atomically.

    Args:
        template_path: ``quiz/index.html``.
        ledger_path: ``concepts/ledger.json``.
        episodes_dir: ``episodes/``.
        output: Where to write the built page.
        now: Timestamp to stamp into the payload; defaults to the current UTC
            time.

    Returns:
        A summary of what was written.

    Raises:
        SiteError: On any missing, invalid or inconsistent input. Nothing is
            written in that case.
    """
    try:
        template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SiteError(f"{template_path} not found")
    ledger = _load(Ledger, ledger_path)
    bundles = collect(episodes_dir, ledger)
    stamp = now or dt.datetime.now(dt.timezone.utc)
    page = render(template, payload(ledger, bundles, stamp))
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".site-", suffix=".html", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(page)
        os.replace(tmp, output)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return BuildResult(
        output=output,
        episodes=len(bundles),
        concepts=len(ledger.concepts),
        bytes=len(page.encode("utf-8")),
    )
