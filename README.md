# distressed-podcast

Given a company name, produce a ~20-minute two-host podcast that teaches how
a special situations desk thinks, using that company's restructuring as the
story. `CLAUDE.md` is the spec.

## Pipeline

```
quiz attempts → ledger → research.md → script.json → quiz.json → <slug>.mp3 → Oracle bucket
(progress)     (Claude)   (Claude)      (Claude)      (Claude)    (Python+Gemini)  (Python+boto3)
                                                           ↘ quiz/build/index.html → claude.ai artifact
```

- `/episode <company>` in Claude Code runs every step and prints a
  pre-signed URL.
- The `progress` skill folds the listener's quiz results into
  `concepts/ledger.json`, the dictionary of every concept explained so far,
  so the next episode re-teaches what was missed.
- The `research`, `script` and `quiz` skills write
  `episodes/<slug>/research.md`, `script.json` and `quiz.json`.
- `uv run podcast audio <slug>` renders the script to
  `episodes/<slug>/<slug>.mp3` with Gemini TTS and appends characters,
  tokens, duration and estimated cost to `episodes/<slug>/run.log`.
- `uv run podcast site` validates every quiz against the ledger and builds
  `quiz/build/index.html`, a single-file quiz app (open it from disk, or
  publish it as the claude.ai artifact named in `quiz/artifact.json`).
- `uv run podcast progress <attempts.json|dir>` applies quiz attempts to
  the ledger (the `progress` skill fetches them for you).
- `uv run podcast publish <slug>` uploads the MP3, research, script and quiz.
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
