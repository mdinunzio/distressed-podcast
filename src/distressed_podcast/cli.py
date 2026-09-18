"""``podcast`` command line: ``audio``, ``publish`` and ``url``.

Research and script writing are Claude Code skills, not Python. This CLI
only turns a validated ``script.json`` into audio and moves files to object
storage.
"""

from __future__ import annotations

import sys

import click
from pydantic import ValidationError

from distressed_podcast.config import ConfigError, GeminiSettings, StorageSettings
from distressed_podcast.config import episode_dir
from distressed_podcast.models import Script


def _load_script(slug: str) -> Script:
    path = episode_dir(slug) / "script.json"
    try:
        return Script.load(path)
    except FileNotFoundError:
        raise click.ClickException(f"{path} not found; run the script skill first")
    except ValidationError as exc:
        raise click.ClickException(f"{path} is not a valid script:\n{exc}")


@click.group()
def main() -> None:
    """Build and publish distressed-debt explainer episodes."""


@main.command()
@click.argument("slug")
def audio(slug: str) -> None:
    """Render episodes/SLUG/script.json to episodes/SLUG/episode.mp3."""
    script = _load_script(slug)
    try:
        settings = GeminiSettings.from_env()
    except ConfigError as exc:
        raise click.ClickException(str(exc))
    click.echo(
        f"{script.slug}: {len(script.segments)} segments, "
        f"{script.word_count} words, {script.character_count} characters "
        f"(model {settings.model})"
    )
    raise click.ClickException("audio rendering is not implemented yet")


@main.command()
@click.argument("slug")
def publish(slug: str) -> None:
    """Upload episodes/SLUG/{episode.mp3,research.md,script.json} to the bucket."""
    _load_script(slug)
    try:
        StorageSettings.from_env()
    except ConfigError as exc:
        raise click.ClickException(str(exc))
    raise click.ClickException("publish is not implemented yet")


@main.command()
@click.argument("slug")
@click.option("--days", default=7, show_default=True, help="URL validity.")
def url(slug: str, days: int) -> None:
    """Print a pre-signed GET URL for episodes/SLUG/episode.mp3 in the bucket."""
    try:
        StorageSettings.from_env()
    except ConfigError as exc:
        raise click.ClickException(str(exc))
    raise click.ClickException("url is not implemented yet")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
