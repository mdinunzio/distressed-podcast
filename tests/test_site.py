"""Tests for the quiz site builder and the ``podcast site`` command."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from distressed_podcast import config, site
from distressed_podcast.cli import main
from distressed_podcast.models import Ledger


def _build(tree: dict[str, Path]) -> site.BuildResult:
    return site.build(
        template_path=tree["template"],
        ledger_path=tree["ledger"],
        episodes_dir=config.EPISODES_DIR,
        output=tree["output"],
        now=dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc),
    )


def _embedded(page: str) -> dict:
    start = page.index('type="application/json">') + len('type="application/json">')
    end = page.index("</script>", start)
    return json.loads(page[start:end])


def test_build_embeds_ledger_and_quizzes(site_tree: dict[str, Path]) -> None:
    result = _build(site_tree)
    assert result.episodes == 1 and result.concepts == 2
    page = site_tree["output"].read_text(encoding="utf-8")
    assert site.DATA_PLACEHOLDER not in page
    data = _embedded(page)
    assert data["generated_at"] == "2026-01-02T00:00:00+00:00"
    assert [c["id"] for c in data["ledger"]["concepts"]] == [
        "fulcrum_security",
        "ebitda",
    ]
    episode = data["episodes"][0]
    assert episode["slug"] == "example-co" and episode["episode"] == 1
    assert episode["title"] == "Example Co: A Test Episode"
    assert len(episode["quiz"]["questions"]) == 20
    assert episode["quiz"]["questions"][0]["retest"] is False


def test_render_escapes_script_terminators() -> None:
    page = site.render(
        f"<script>{site.DATA_PLACEHOLDER}</script>",
        {"x": "</script><b>\u2028"},
    )
    assert page.count("</script>") == 1
    assert "\\u003c/script>\\u003cb>" in page
    assert "\u2028" not in page and "\\u2028" in page
    assert json.loads(page[len("<script>") : -len("</script>")]) == {
        "x": "</script><b>\u2028"
    }


def test_render_requires_single_placeholder() -> None:
    with pytest.raises(site.SiteError):
        site.render("no placeholder", {})
    with pytest.raises(site.SiteError):
        site.render(site.DATA_PLACEHOLDER * 2, {})


def test_episodes_without_quiz_are_skipped(
    site_tree: dict[str, Path], episodes_dir: Path
) -> None:
    other = episodes_dir / "other-co"
    other.mkdir()
    (other / "script.json").write_text("{}", encoding="utf-8")
    assert _build(site_tree).episodes == 1


@pytest.mark.parametrize(
    "break_it, message",
    [
        (lambda t: t["script"].unlink(), "script.json not found"),
        (
            lambda t: _rewrite(t["quiz"], lambda q: q.__setitem__("episode", 2)),
            "episode 2 but script says 1",
        ),
        (
            lambda t: _rewrite(t["quiz"], lambda q: q.__setitem__("slug", "wrong-co")),
            "do not match directory",
        ),
        (
            lambda t: _rewrite(
                t["quiz"],
                lambda q: q["questions"][0].__setitem__("concept_ids", ["priming"]),
            ),
            "missing from the ledger: priming",
        ),
        (
            lambda t: _rewrite(t["script"], lambda s: s.pop("episode")),
            "has no episode number",
        ),
        (lambda t: t["quiz"].write_text("{}", encoding="utf-8"), "not a valid Quiz"),
        (lambda t: t["ledger"].unlink(), "ledger.json not found"),
        (lambda t: t["template"].unlink(), "index.html not found"),
    ],
    ids=[
        "missing-script",
        "episode-mismatch",
        "slug-mismatch",
        "unknown-concept",
        "script-without-episode",
        "invalid-quiz",
        "missing-ledger",
        "missing-template",
    ],
)
def test_inconsistent_inputs_fail_and_write_nothing(
    site_tree: dict[str, Path], break_it, message: str
) -> None:
    break_it(site_tree)
    with pytest.raises(site.SiteError, match=message):
        _build(site_tree)
    assert not site_tree["output"].exists()
    build_dir = site_tree["output"].parent
    assert not build_dir.exists() or not list(build_dir.glob(".site-*"))


def _rewrite(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_duplicate_episode_numbers_are_rejected(
    site_tree: dict[str, Path], episodes_dir: Path
) -> None:
    other = episodes_dir / "other-co"
    other.mkdir()
    for name in ("script.json", "quiz.json"):
        data = json.loads((episodes_dir / "example-co" / name).read_text())
        data["slug"] = "other-co"
        (other / name).write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(site.SiteError, match="duplicate episode numbers"):
        _build(site_tree)


def test_site_command_builds_default_output(site_tree: dict[str, Path]) -> None:
    result = CliRunner().invoke(main, ["site"])
    assert result.exit_code == 0, result.output
    assert "1 quizzes, 2 ledger concepts" in result.output
    assert site_tree["output"].exists()
    Ledger.load(site_tree["ledger"])  # still valid after the build


def test_site_command_reports_errors(site_tree: dict[str, Path]) -> None:
    site_tree["ledger"].write_text('{"concepts": []}', encoding="utf-8")
    result = CliRunner().invoke(main, ["site"])
    assert result.exit_code != 0
    assert "missing from the ledger" in result.output
