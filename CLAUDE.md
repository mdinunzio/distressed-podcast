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

## The cast of characters

Concepts stick when they're anchored to a person, not just a mechanism.
Every episode names the recurring players — management, the CRO, the lead
hedge funds and advisors on each side of the table — and sketches them the
way Michael Lewis would: a telling detail, a track record, a known
playbook, a rivalry from a prior case. If a fund is known for aggressive
uptiers, or for being the cooperative consensus-builder, or management has
a reputation the market talks about, say so and tie it to what they
actually do in this deal. This is a mnemonic, not decoration: a mechanism
remembered through a personality sticks longer than one remembered as an
abstraction. Same sourcing bar as every other fact in the episode — press
and filings only, cited in the research, economical on air (a sentence or
two per player), and never invented dialogue, motives, or gossip.

## Gentle first, then professional: the concept ledger

The listener got lost, in an early episode, not in the numbers but in the
instruments: what a preferred is next to a term loan next to a bond, and
who is paid before whom. So two rules govern how concepts are taught.

**The ladder.** Every episode places every instrument on the same seven-rung
capital structure ladder, out loud: super-senior (DIP, ABL) → first-lien
secured → second-lien secured → senior unsecured → subordinated → preferred
→ common. For each instrument: its rung and how it gets paid (cash coupon,
PIK, accreting preference, at maturity, from specific collateral).
Preferred stock gets its own sentence every time: equity, not debt; below
every lender; a liquidation preference ahead of common. The quiz app shows
the same ladder as a reference.

**The ledger.** `concepts/ledger.json` is the dictionary of every concept
the series has explained, one entry each (`id`, `name`, `one_line`, `tier`,
`level` 1–5, `moyer`, `aliases`, `introduced_in`, `episode`, `status`,
`history`). A concept is explained gently and in full **once**, the first
time an episode needs it (plain-English definition, one everyday analogy,
its rung if it is an instrument, then this case's number), and is added to
the ledger as `introduced`. Later episodes give an `introduced` concept a
one-clause reminder, use a `mastered` one without stopping, and re-explain
a `needs_reteach` one in full. Six to ten new concepts per episode, no
more; early episodes introduce level 1–2 concepts, later ones level 3 and
up, so the series climbs from beginner to expert. The ledger is also the
listener's lookup: the quiz app renders it as a searchable glossary.

## Quiz and progress

Every episode ends with a 20-question quiz, `episodes/<slug>/quiz.json`,
written by the `quiz` skill from the script and the ledger: multiple
choice plus numeric, short-text and ordering questions, each tagged with
the ledger concepts it tests and a level 1–5. The difficulty mix follows
the episode number. Every question must be answerable from the audio.

The quizzes ship in one small vanilla-JS web app, `quiz/index.html`.
`uv run podcast site` validates every quiz against its script and the
ledger and embeds them, with the ledger, into `quiz/build/index.html`, a
single self-contained file that opens from disk and is published as a
claude.ai artifact (URL in `quiz/artifact.json`) with the `db`
capability. Completed quizzes are stored as `attempts` documents in the
artifact's database (mirrored in the browser's localStorage, with a JSON
export as fallback). The `progress` skill fetches them and
`uv run podcast progress` folds them into the ledger: a concept answered
wrong in the latest attempt becomes `needs_reteach`, answered right
becomes `mastered`; `concepts/progress.json` records which attempts were
applied. The next episode re-teaches every `needs_reteach` concept the
story touches, and its quiz re-tests it (`retest: true`). That closed
loop is the point of the whole system.

## Episode shape (every episode follows this arc)

1. **The situation** (~3 min). Who the company is, what it does, why it is in
   trouble, what is happening right now and what the next dated events are,
   with a quick, vivid sketch of who's driving it. Plain English. No jargon
   yet beyond what a generalist would know.
2. **The concepts at high level** (~4 min). Name the three to six ideas this
   situation turns on (e.g. "where the fulcrum sits", "priming", "what a
   prepack is") and give each a one-paragraph intuition, tied to the
   company, and walk this company's instruments down the ladder.
3. **Unfurling** (~9 min). Take each concept in turn and go deeper: how it
   works mechanically, what the documents actually say in this case, what the
   numbers are and what they compare to, who wins and who loses, how a desk
   would trade or position around it, and what could go wrong. Where a
   player's known style or history explains the move, say so — that's how
   the mechanism gets remembered. This is where accounting, capital
   structure and legal detail get taught properly, always through the lens
   of the event at hand, and where new concepts get their gentle explainer.
4. **The trader's recap** (~2 min). Where the value accumulated, instrument
   by instrument and in what form; the twists, turns and risks along the
   way; who won, who lost, and who was left in the dust. "If I'd been on the
   desk, where did I want to be, round by round?"
5. **What to watch** (~2 min). The dated catalysts, the open questions, and
   two or three things the listener could now go read (the RSA, the 8-K, a
   docket entry) with the vocabulary to understand them. Then the quiz.

## Pipeline

```
quiz attempts → ledger → research.md → script.json → quiz.json → <slug>.mp3 → Oracle bucket
(progress)     (Claude)   (Claude)      (Claude)      (Claude)    (Python+Gemini)  (Python+boto3)
                                                           ↘ quiz/build/index.html → claude.ai artifact
                                                             (podcast site)
```

Research, script, quiz and progress are Claude Code skills. Audio, site
and publish are Python: `uv run podcast audio <slug>`, `uv run podcast
site`, `uv run podcast publish <slug>`. `/episode <company>` runs them all
in order (progress sync first, so the new episode knows what to re-teach)
and ends by printing a pre-signed URL for the MP3 and republishing the quiz
artifact.

### Research (skill: `.claude/skills/research/SKILL.md`)

Claude uses its own web search and fetch tools; **no Python makes HTTP calls
to research sources**. WebSearch runs server-side and only returns excerpts;
WebFetch goes through the VM, so it needs the environment's Full network
access. Research must fetch primary documents directly (the first-day
declaration, DIP orders, disclosure statement, plan) rather than rely on
search excerpts. When a fetch still fails (paywall, PACER, a blocked host),
cite the excerpt as such per the skill. For EDGAR, send a descriptive
User-Agent. Output: `episodes/<slug>/research.md` with these headings, in order:

1. Situation summary and timeline (dated, most recent first, with what is
   scheduled next)
2. Business overview and why it broke (operational and financial causes,
   Moyer-style)
3. Financials that matter to creditors: revenue, EBITDA, free cash flow,
   liquidity, leverage, with the accounting caveats a creditor would apply
4. Capital structure, senior to junior: instrument, size, rate, maturity,
   security, guarantors, key covenants, trading level if public, plus each
   instrument's ladder rung and how it is paid
5. The key documents and what they say (indenture / credit agreement /
   intercreditor / RSA / DIP / plan) with the specific provisions in play
6. Where the fulcrum security sits and why
7. The restructuring: what is proposed or done, mechanically, step by step
8. Who wins, who gets diluted or primed, and by how much, ending with the
   three recap paragraphs: where the value accumulated, twists and risks,
   winners / losers / left in the dust
9. Cast of characters: the people and firms driving it, and what they're
   known for (management, the CRO, the lead funds and advisors on each
   side — track record, style, reputation, rivalries, sourced to press or
   filings)
10. How a special situations desk would look at each part of the structure
11. Risks and what could derail it
12. Concepts to teach in this episode (the list step 2 of the episode will
    use, each with a one-line note on why this situation needs it, where
    applicable the Moyer chapter or idea it corresponds to, and its status
    in `concepts/ledger.json`: new, introduced, mastered or needs_reteach)
13. Glossary: every term of art used above, one sentence each
14. Sources: prefer primary (8-Ks, RSAs, indentures, credit agreements, the
    docket via Kroll/Epiq/PACER) over press; list every URL

If a section cannot be sourced, say so explicitly. Never invent numbers or
provisions. Research quality is the ceiling on episode quality.

### Script (skill: `.claude/skills/script/SKILL.md`)

Claude writes `episodes/<slug>/script.json` from `research.md` only, with
`concepts/ledger.json` deciding how deeply each concept is explained.
Nothing in the script that is not in the research; if the research is
silent, the hosts say so on air.

- Two hosts. **Host** is a senior special situations analyst who explains.
  **Guest** is the listener's proxy: smart, finance-literate, new to
  distressed, and unembarrassed about asking "wait, what does that actually
  mean?" Every term of art is defined the first time it is spoken in the
  series, by the guest asking or the host pausing to define it; the ledger
  says what the series has already defined.
- ~150 words per spoken minute. Target 20 minutes: 2,900–3,200 words. 7–9
  segments of 2–4 minutes each, following the five-part episode shape
  above; the last two are always `recap` and `watch`. The skill counts
  words and rewrites if out of band before writing the file, then appends
  the concepts it introduced to the ledger.
- Each segment has a one-sentence `direction` (pace, mood) for the TTS model.
- `episode` (optional integer) becomes the ID3 track number.
- Two framings, chosen from the research timeline: **live** (what is
  happening, what to watch) when the situation has dated events ahead;
  **closed** (how it played out, why) when the plan is effective or the
  deal is done. Same five-part didactic arc either way.
- Weave in the cast: brief, sourced personality color on the recurring
  players (research section 9) — a track record, a known playbook, a
  rivalry — used to make a mechanism memorable, in the style of Michael
  Lewis. Economical, and never invented.
- No number without a comparison that makes it meaningful. No concept without
  a concrete tie back to this company. Where Moyer covers it, say so.
- Format:

```json
{
  "company": "…", "slug": "…", "title": "…", "deal_type": "…",
  "episode": 1,
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
- Output: `episodes/<slug>/<slug>.mp3` (a descriptive filename, not the
  literal string `episode.mp3`). Log characters sent and estimated
  cost to `episodes/<slug>/run.log`.

### Quiz (skill: `.claude/skills/quiz/SKILL.md`)

Claude writes `episodes/<slug>/quiz.json`: exactly 20 questions, ids
`q01`–`q20`, types `multiple_choice` (3–5 `choices`, `answer` index),
`numeric` (`answer`, `tolerance`, `unit`), `short_text` (`accepted`
spellings) and `order` (`items` in the correct order; the app shuffles).
Each has `level` 1–5, `concept_ids` from the ledger, `prompt`,
`explanation`, and `retest: true` when it re-tests a `needs_reteach`
concept. Validated by the pydantic `Quiz` model and cross-checked against
the script and ledger by `podcast site`.

### Site (`podcast site`)

Reads `quiz/index.html`, `concepts/ledger.json` and every
`episodes/*/quiz.json` (each must sit next to a `script.json` with the
same slug and episode number, and reference only ledger concepts), embeds
the data at the JSON placeholder and writes `quiz/build/index.html`
atomically. Publish that file as the claude.ai artifact named in
`quiz/artifact.json` with `capabilities: {db: {}}`; the page uses
`claude.use("db")` when available and falls back to localStorage. The app
itself is plain HTML/CSS/JS with no build step and no framework.

### Progress (skill: `.claude/skills/progress/SKILL.md`, `podcast progress <attempts>`)

The skill lists the artifact's `attempts` collection with `ArtifactData`
into a scratch directory (or takes the app's JSON export at
`concepts/attempts.json`) and runs `podcast progress`, which updates
ledger statuses and history and records applied attempt ids in
`concepts/progress.json`. Idempotent; never deletes attempts.

### Publish (`podcast publish <slug>`)

- `boto3` against Oracle Object Storage's S3 Compatibility API:
  `endpoint_url=S3_ENDPOINT_URL`, `region_name=S3_REGION`,
  `Config(signature_version="s3v4", s3={"addressing_style": "path"},
  request_checksum_calculation="when_required",
  response_checksum_validation="when_required")`. The checksum settings are
  required; Oracle rejects `aws-chunked` uploads.
- Uploads `<slug>/<slug>.mp3`, `<slug>/research.md`, `<slug>/script.json`
  and `<slug>/quiz.json` if present. `put_object` overwrites on re-run.
  Never delete from code.
- `podcast url <slug>` prints a pre-signed GET URL (default 7 days).
- Storage may move to Cloudflare R2 later; keep `storage.py` provider-agnostic
  so that is an env-only change.

## Repo layout

```
.claude/
  skills/research/SKILL.md
  skills/script/SKILL.md
  skills/quiz/SKILL.md
  skills/progress/SKILL.md
  commands/episode.md          # /episode <company>: progress → research → script → quiz → audio → site → publish → url
  settings.json                # SessionStart hook: `uv sync` when CLAUDE_CODE_REMOTE=true
src/distressed_podcast/
  cli.py        # click: `podcast audio|site|progress|publish|url`
  models.py     # pydantic Script, Quiz and Ledger models
  config.py     # env settings and repo paths, validated per command
  audio.py      # Gemini calls, WAV wrapping
  stitch.py     # ffmpeg concat + mp3 + ID3
  site.py       # validates quizzes against ledger, embeds data into the quiz page
  progress.py   # folds quiz attempts into the ledger
  storage.py    # S3 client wrapper
  publish.py
concepts/
  ledger.json   # the concept dictionary (see above)
  progress.json # attempt ids already applied to the ledger
quiz/
  index.html    # the quiz app source, one JSON placeholder
  artifact.json # {"url": …} of the published artifact
  build/        # gitignored output of `podcast site`
episodes/       # generated; gitignored except research.md, script.json, quiz.json
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
  needs. No `.env` auto-loading: locally, run `uv run --env-file .env podcast
  …` (documented in the README). Provider keys are optional in config (a cloud environment may inject
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

- Network access: **Full**. WebSearch runs server-side; WebFetch goes through
  the VM, so primary documents (8-Ks, claims-agent dockets, company releases)
  are only reachable with open egress. Because of this, the only secrets in
  the environment's env vars are the bucket-scoped Oracle keys; the Gemini key
  stays an API credential. Never add other credentials as env vars here.
- Setup script: `apt-get update && apt-get install -y ffmpeg || true`.
- Do not add Python-side fetching of SEC, docket, or news hosts; research
  goes through Claude's own tools.
