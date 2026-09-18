# distressed-podcast

Given a company name, produce a ~20-minute two-host podcast that teaches how
a special situations desk thinks, using that company's restructuring as the
story. `CLAUDE.md` is the spec.

## Pipeline

```
company name → research.md → script.json → <slug>.mp3 → Oracle bucket
               (Claude)       (Claude)       (Python+Gemini)  (Python+boto3)
```

- `/episode <company>` in Claude Code runs all four steps and prints a
  pre-signed URL.
- The `research` and `script` skills write `episodes/<slug>/research.md` and
  `episodes/<slug>/script.json`.
- `uv run podcast audio <slug>` renders the script to
  `episodes/<slug>/<slug>.mp3` with Gemini TTS and appends characters,
  tokens, duration and estimated cost to `episodes/<slug>/run.log`.
- `uv run podcast publish <slug>` uploads the MP3, research and script.
- `uv run podcast url <slug>` prints a pre-signed GET URL.

## Local setup

```
uv sync
cp .env.example .env   # fill in the values
uv run --env-file .env podcast audio saks-global
```

`.env` is not loaded automatically; pass it with `uv run --env-file .env`.
`ffmpeg` must be on the path for `podcast audio`.

## Checks

```
uv run black --check .
uv run flake8
uv run pytest
```
