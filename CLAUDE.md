# distressed-podcast

Given a company name, produce a ~20-minute two-host podcast that teaches how a
special situations / distressed debt desk thinks, using that company's live
restructuring as the story. Claude Code does the research and writes the script
inside the repo. Python only turns the script into audio (Google Gemini TTS)
and stores it (Oracle Object Storage, S3-compatible).

Personal learning project. Public information only. Never ingest, reference,
or store non-public or employer data. Educational, not investment advice.

## Who this is for, and what "good" means

The listener has worked in finance for a while (markets, quant, or data
roles), so they are comfortable with rates, spreads, yields, and reading a
Bloomberg screen. They are **new to distressed investing and to how a special
situations group operates**, and they need ground-up explanations of the
things a credit desk takes for granted:

- accounting as it matters to creditors (EBITDA vs. cash flow, working
  capital, leases, off-balance-sheet obligations, going-concern language)
- capital structure (secured vs. unsecured, first vs. second lien, guarantees,
  structural and contractual subordination, covenants, baskets)
- the legal machinery (indentures, credit agreements, intercreditor
  agreements, Chapter 11 basics, absolute priority, the automatic stay, DIP
  financing, 363 sales, plans of reorganization, RSAs, out-of-court exchanges,
  LMEs such as drop-downs and uptiers)

**The primary goal is didactic.** Every episode exists to get a newcomer up to
speed on the desk as fast as possible. The company's situation is the vehicle:
concepts are introduced *because* the current events demand them, and each
concept is taught at the moment the story needs it. Storytelling about the
real, in-progress situation is the delivery mechanism, not the point.

The listener is reading *Distressed Debt Analysis: Strategies for Speculative
Investors* by Stephen G. Moyer. Where a concept maps to Moyer's framework —
causes of distress, the capital structure and where value breaks, valuation
of the reorganized firm, the fulcrum security, the Chapter 11 process and the
plan, out-of-court vs. in-court, how distressed claims trade — name the
connection explicitly ("this is the fulcrum-security idea from Moyer") so the
book and the episodes reinforce each other. Do not assume they have finished
the book.

## Episode shape (every episode follows this arc)

1. **The situation** (~3 min). Who the company is, what it does, why it is in
   trouble, what is happening right now and what the next dated events are.
   Plain English. No jargon yet beyond what a generalist would know.
2. **The concepts at high level** (~4 min). Name the three to six ideas this
   situation turns on (e.g. "where the fulcrum sits", "priming", "what a
   prepack is") and give each a one-paragraph intuition, tied to the company.
3. **Unfurling** (~11 min). Take each concept in turn and go deeper: how it
   works mechanically, what the documents actually say in this case, what the
   numbers are and what they compare to, who wins and who loses, how a desk
   would trade or position around it, and what could go wrong. This is where
   accounting, capital structure and legal detail get taught properly,
   always through the lens of the event at hand.
4. **What to watch** (~2 min). The dated catalysts, the open questions, and
   two or three things the listener could now go read (the RSA, the 8-K, a
   docket entry) with the vocabulary to understand them.

## Pipeline

```
company name → research.md → script.json → episode.mp3 → Oracle bucket
               (Claude)       (Claude)       (Python+Gemini)  (Python+boto3)
```

The first two steps are Claude Code skills. The last two are `uv run podcast
audio <slug>` and `uv run podcast publish <slug>`. `/episode <company>` runs
all four in order and ends by printing a pre-signed URL for the MP3.

### Research (skill: `.claude/skills/research/SKILL.md`)

Claude uses its own web search and fetch tools; **no Python makes HTTP calls
to research sources**, because cloud sessions only reach allowlisted domains.
Output: `episodes/<slug>/research.md` with these headings, in order:

1. Situation summary and timeline (dated, most recent first, with what is
   scheduled next)
2. Business overview and why it broke (operational and financial causes,
   Moyer-style)
3. Financials that matter to creditors: revenue, EBITDA, free cash flow,
   liquidity, leverage, with the accounting caveats a creditor would apply
4. Capital structure, senior to junior: instrument, size, rate, maturity,
   security, guarantors, key covenants, trading level if public
5. The key documents and what they say (indenture / credit agreement /
   intercreditor / RSA / DIP / plan) with the specific provisions in play
6. Where the fulcrum security sits and why
7. The restructuring: what is proposed or done, mechanically, step by step
8. Who wins, who gets diluted or primed, and by how much
9. How a special situations desk would look at each part of the structure
10. Risks and what could derail it
11. Concepts to teach in this episode (the list step 2 of the episode will
    use, each with a one-line note on why this situation needs it and, where
    applicable, the Moyer chapter or idea it corresponds to)
12. Glossary: every term of art used above, one sentence each
13. Sources: prefer primary (8-Ks, RSAs, indentures, credit agreements, the
    docket via Kroll/Epiq/PACER) over press; list every URL

If a section cannot be sourced, say so explicitly. Never invent numbers or
provisions. Research quality is the ceiling on episode quality.

### Script (skill: `.claude/skills/script/SKILL.md`)

Claude writes `episodes/<slug>/script.json` from `research.md` only. Nothing
in the script that is not in the research; if the research is silent, the
hosts say so on air.

- Two hosts. **Host** is a senior special situations analyst who explains.
  **Guest** is the listener's proxy: smart, finance-literate, new to
  distressed, and unembarrassed about asking "wait, what does that actually
  mean?" Every term of art is defined the first time it is spoken, by the
  guest asking or the host pausing to define it.
- ~150 words per spoken minute. Target 20 minutes: 2,900–3,200 words. 6–8
  segments of 2–4 minutes each, following the four-part episode shape above.
  The skill counts words and rewrites if out of band before writing the file.
- Each segment has a one-sentence `direction` (pace, mood) for the TTS model.
- No number without a comparison that makes it meaningful. No concept without
  a concrete tie back to this company. Where Moyer covers it, say so.
- Format:

```json
{
  "company": "…", "slug": "…", "title": "…", "deal_type": "…",
  "segments": [
    {"name": "situation", "direction": "…",
     "turns": [{"speaker": "Host", "text": "…"}, {"speaker": "Guest", "text": "…"}]}
  ]
}
```

### Audio (`podcast audio <slug>`)

Delegated entirely to Google's Gemini TTS; Claude does not voice anything.

- `google-genai`, model `gemini-3.1-flash-tts-preview` (`GEMINI_TTS_MODEL`
  overrides). Multi-speaker config: two `SpeakerVoiceConfig`s named `Host`
  and `Guest` with prebuilt voices from `GEMINI_VOICE_HOST` /
  `GEMINI_VOICE_GUEST` (defaults `Charon` / `Puck`). Speaker names in the
  config must match the labels in the prompt text.
- One request per segment: the segment's `direction`, then the dialogue as
  `Host: …` / `Guest: …` lines. Never the whole script in one call.
- Response audio is raw 16-bit little-endian PCM, 24 kHz, mono at
  `response.candidates[0].content.parts[0].inline_data.data`. Wrap as WAV,
  concatenate with ffmpeg, encode MP3 128 kbps mono, write ID3 tags (title,
  album "Distressed Explainers", track number).
- Output: `episodes/<slug>/episode.mp3`. Log characters sent and estimated
  cost to `episodes/<slug>/run.log`.

### Publish (`podcast publish <slug>`)

- `boto3` against Oracle Object Storage's S3 Compatibility API:
  `endpoint_url=S3_ENDPOINT_URL`, `region_name=S3_REGION`,
  `Config(signature_version="s3v4", s3={"addressing_style": "path"},
  request_checksum_calculation="when_required",
  response_checksum_validation="when_required")`. The checksum settings are
  required; Oracle rejects `aws-chunked` uploads.
- Uploads `<slug>/episode.mp3`, `<slug>/research.md`, `<slug>/script.json`.
  `put_object` overwrites on re-run. Never delete from code.
- `podcast url <slug>` prints a pre-signed GET URL (default 7 days).
- Storage may move to Cloudflare R2 later; keep `storage.py` provider-agnostic
  so that is an env-only change.

## Repo layout

```
.claude/
  skills/research/SKILL.md
  skills/script/SKILL.md
  commands/episode.md          # /episode <company>: research → script → audio → publish → url
  settings.json                # SessionStart hook: `uv sync` when CLAUDE_CODE_REMOTE=true
src/distressed_podcast/
  cli.py        # click: `podcast audio|publish|url`
  models.py     # pydantic Script model (validates script.json before audio)
  config.py     # env settings, validated per command
  audio.py      # Gemini calls, WAV wrapping
  stitch.py     # ffmpeg concat + mp3 + ID3
  storage.py    # S3 client wrapper
  publish.py
episodes/       # generated; gitignored except research.md and script.json
tests/          # fixtures + mocked genai / boto3 / subprocess
```

Keep the Python small. If a feature needs a frontier model, it is a skill,
not a Python module.

## Conventions

- Python 3.12, `uv`, `click`, `pydantic`, `google-genai`, `boto3`. Nothing
  else unless justified in a PR.
- black, flake8, Google-style docstrings, pytest with fixtures; never live
  API calls in tests.
- Settings only from env via `config.py`; each command validates only what it
  needs. Provider keys are optional in config (a cloud environment may inject
  them at the proxy); a missing key surfaces as an auth error at call time.
- Fail loudly; never write a partial output file.

## Environment

| Variable | Delivery in cloud sessions | Notes |
| --- | --- | --- |
| `GEMINI_API_KEY` | API credential on `generativelanguage.googleapis.com`, header `x-goog-api-key` (env var locally) | code sends the header only if the env var is set |
| `GEMINI_TTS_MODEL`, `GEMINI_VOICE_HOST`, `GEMINI_VOICE_GUEST` | env var | optional |
| `S3_ENDPOINT_URL` | env var | `https://<namespace>.compat.objectstorage.<region>.oraclecloud.com` |
| `S3_REGION` | env var | must match the endpoint, e.g. `us-ashburn-1` |
| `S3_BUCKET` | env var | |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | env var | Oracle customer secret key; SigV4 needs the secret in-process, so the proxy cannot inject it |

No Anthropic API key is needed: Claude Code itself does the research and
script work.

## Cloud environment requirements

- Network access: **Custom**, with `*.oraclecloud.com` added and "also
  include default list of common package managers" checked.
  `*.googleapis.com` is already on the default list.
- Setup script: `apt-get update && apt-get install -y ffmpeg || true`.
- Research reaches the web through Claude's own tools, which are not subject
  to the VM's allowlist. Do not add Python-side fetching of SEC, docket, or
  news hosts.
