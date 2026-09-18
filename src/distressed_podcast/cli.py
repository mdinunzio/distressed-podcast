"""``podcast`` command line: ``audio``, ``publish`` and ``url``.

Research and script writing are Claude Code skills, not Python. This CLI
only turns a validated ``script.json`` into audio and moves files to object
storage.
"""

from __future__ import annotations

import datetime as dt
import os
import sys
import tempfile
from pathlib import Path

import click
from pydantic import ValidationError

from distressed_podcast import audio, stitch
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


def _render_all(
    script: Script, settings: GeminiSettings, workdir: Path
) -> tuple[list[audio.SegmentAudio], list[Path]]:
    client = audio.build_client(settings)
    rendered: list[audio.SegmentAudio] = []
    wavs: list[Path] = []
    for index, segment in enumerate(script.segments, start=1):
        click.echo(
            f"[{index}/{len(script.segments)}] {segment.name}: "
            f"{segment.word_count} words ... ",
            nl=False,
        )
        item = audio.render_segment(client, settings, segment)
        wav = workdir / f"{index:02d}-{segment.name}.wav"
        stitch.write_wav(wav, item.pcm)
        rendered.append(item)
        wavs.append(wav)
        click.echo(f"{item.seconds:.1f}s")
    return rendered, wavs


def _write_run_log(
    log: Path,
    script: Script,
    settings: GeminiSettings,
    rendered: list[audio.SegmentAudio],
    cost: float,
) -> None:
    total_seconds = sum(item.seconds for item in rendered)
    lines = [
        f"== {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')} "
        f"audio {script.slug} model={settings.model} "
        f"voices={settings.voice_host}/{settings.voice_guest}",
    ]
    for item in rendered:
        lines.append(
            f"  {item.name:32s} chars={item.characters:6d} "
            f"prompt_tokens={item.prompt_tokens} audio_tokens={item.audio_tokens} "
            f"seconds={item.seconds:.1f}"
        )
    lines.append(
        f"  total chars={sum(i.characters for i in rendered)} "
        f"words={script.word_count} seconds={total_seconds:.1f} "
        f"({total_seconds / 60:.1f} min) estimated_cost_usd={cost:.4f}"
    )
    with log.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


@main.command()
@click.argument("slug")
def audio_command(slug: str) -> None:
    """Render episodes/SLUG/script.json to episodes/SLUG/SLUG.mp3."""
    script = _load_script(slug)
    try:
        settings = GeminiSettings.from_env()
    except ConfigError as exc:
        raise click.ClickException(str(exc))
    folder = episode_dir(slug)
    click.echo(
        f"{script.slug}: {len(script.segments)} segments, {script.word_count} words, "
        f"{script.character_count} characters (model {settings.model})"
    )
    final = folder / f"{slug}.mp3"
    with tempfile.TemporaryDirectory(prefix=".audio-", dir=folder) as tmp:
        workdir = Path(tmp)
        try:
            rendered, wavs = _render_all(script, settings, workdir)
            stitch.concat_to_mp3(
                wavs, workdir / f"{slug}.mp3", script.title, script.episode
            )
        except (audio.AudioError, stitch.StitchError) as exc:
            raise click.ClickException(str(exc))
        os.replace(workdir / f"{slug}.mp3", final)
    cost = audio.estimate_cost_usd(settings, rendered)
    _write_run_log(folder / "run.log", script, settings, rendered, cost)
    total = sum(item.seconds for item in rendered)
    click.echo(
        f"wrote {final} ({total / 60:.1f} min, estimated cost ${cost:.4f}); "
        f"log appended to {folder / 'run.log'}"
    )


main.add_command(audio_command, name="audio")


@main.command()
@click.argument("slug")
def publish(slug: str) -> None:
    """Upload episodes/SLUG/{SLUG.mp3,research.md,script.json} to the bucket."""
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
    """Print a pre-signed GET URL for episodes/SLUG/SLUG.mp3 in the bucket."""
    try:
        StorageSettings.from_env()
    except ConfigError as exc:
        raise click.ClickException(str(exc))
    raise click.ClickException("url is not implemented yet")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
