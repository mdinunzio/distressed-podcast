---
name: script
description: Write a ~20-minute two-host teaching podcast script (episodes/<slug>/script.json) from episodes/<slug>/research.md. Use when asked to write or rewrite an episode script, or as step two of /episode.
argument-hint: <slug>
---

# Write the episode script

Slug: `$ARGUMENTS`. If empty, ask for a slug and stop. Read
`episodes/<slug>/research.md` in full, then `concepts/ledger.json`, before
writing a word. Write `episodes/<slug>/script.json`, then update
`concepts/ledger.json` as described at the end, and nothing else.

## The one hard rule

**Nothing in the script that is not in the research.** No number, date,
provision, name or claim that does not appear in `research.md`. If the
research is silent on something the conversation naturally reaches, the
hosts say so on air ("the filings don't break that out", "we couldn't find
the intercreditor"). If the research marks something as press-reported or
unsourced, the hosts say that too. Do not fill gaps from memory. This
includes character color: a reputation, a track record, a prior fight — if
research.md didn't source it, it doesn't go in the script, however good
the line would sound.

## Who is listening and why

The listener has worked in finance (markets, quant or data), is fluent in
rates, spreads, yields and a Bloomberg screen, and is **new to distressed
investing and to how a special situations group operates**. The episode
exists to get them up to speed on the desk as fast as possible. The
company's situation is the vehicle; concepts are introduced because the
story demands them and taught at the moment the story needs them.

They are reading Stephen G. Moyer, *Distressed Debt Analysis: Strategies
for Speculative Investors*. Where a concept maps to Moyer (causes of
distress, capital structure and where value breaks, valuing the
reorganized firm, the fulcrum security, the Chapter 11 process and the
plan, out-of-court vs. in-court, how distressed claims trade), name the
connection out loud ("this is the fulcrum-security idea from Moyer").
Do not assume they have finished the book.

Ground-up explanations are required for: accounting as it matters to
creditors (EBITDA vs. cash flow, working capital, leases, off-balance-sheet
obligations, going-concern language); capital structure (secured vs.
unsecured, first vs. second lien, guarantees, structural and contractual
subordination, covenants, baskets); the legal machinery (indentures, credit
agreements, intercreditors, Chapter 11 basics, absolute priority, the
automatic stay, DIP financing, 363 sales, plans, RSAs, out-of-court
exchanges, LMEs such as drop-downs and uptiers).

## The two hosts

- **Host** is a senior special situations analyst. Explains clearly,
  concretely, from the desk's point of view. Never lectures for more than
  about 120 words without the Guest coming back in.
- **Guest** is the listener's proxy: smart, finance-literate, new to
  distressed, and unembarrassed about asking "wait, what does that actually
  mean?" The Guest asks the question the listener is thinking, restates
  ideas to check understanding, and pushes on "so who loses?" and "how
  would you actually trade that?"

Every term of art is defined the first time it is spoken *in the series*,
either by the Guest asking or the Host pausing to define it. The ledger
says which terms the series has already defined. Keep a running list while
you write; if a term appears before its definition, fix it.

## The ledger: how deep to explain each concept

`concepts/ledger.json` is the dictionary of everything earlier episodes
have explained, with a status per concept. It decides how much air time a
term gets, so the series starts gentle and gets more professional without
re-teaching what already landed:

| Status | What the hosts do |
| --- | --- |
| not in the ledger (**new**) | The full gentle explainer: the Guest asks; the Host gives a plain-English definition, one everyday analogy, where it sits on the ladder if it is an instrument, then the number or clause from this case. 60 to 120 words. |
| `introduced` (explained before, not yet tested) | One clause of reminder on first use ("the DIP, the loan a company takes inside Chapter 11"), then use it freely. |
| `mastered` (answered right on a quiz) | Use the term without stopping, the way the desk would. |
| `needs_reteach` (missed on a quiz) | Re-explain it fully, at the moment the story needs it, and say so lightly: "we covered this in episode two and it's worth a second pass". The quiz skill will re-test it. |

Budget: an episode introduces **six to ten new concepts** in full, no more.
If the research's section 12 supporting list is longer, pick the ones this
story cannot be told without and let the others wait for a later episode
(name them plainly, without a full explainer, only if unavoidable). Every
`needs_reteach` concept the research flagged in section 12 gets its
re-explanation. Progression: episodes one to three should introduce
concepts of ledger level 1–2, later episodes level 3 and up, so the series
climbs from beginner to expert.

## The capital structure ladder

The listener's hardest problem is holding the instruments in their head at
once. Every episode uses the same mental model, out loud, and the quiz app
shows the same picture. When the structure is first laid out (usually in
`concepts` or the first `unfurl_*` segment), the Host walks the rungs top
to bottom and places each of this company's instruments on one:

1. super-senior: DIP loans, the ABL revolver
2. first-lien secured: term loans, secured notes
3. second-lien secured
4. senior unsecured: bonds, trade, rejected leases, litigation
5. subordinated debt
6. preferred stock
7. common equity

For each instrument, two things: its rung, and how it gets paid (cash
coupon, PIK, accreting preference, at maturity, from specific collateral).
Say explicitly that "senior" and "secured" are about where the money comes
from in a bad outcome, not about the size of the coupon. **Preferred stock
gets its own sentence every time it appears**: equity, not debt; no
maturity and no default if the dividend is skipped; a liquidation
preference ahead of the common; below every lender. Guarantees pull a
claim up a rung at another entity; structural subordination pushes it
down. Then, whenever a number or a recovery is quoted later, name the
rung it belongs to ("the second-lien, rung three, at forty cents"). The
research's section 4 table has the rung and payment form for each
instrument; if it doesn't, say on air where you are placing it and why.

## Characters and color

Pull from research section 9 (cast of characters). A mechanism remembered
through a person sticks longer than one remembered as an abstraction —
that is the point, not decoration. Write it the way Michael Lewis would:
a telling detail or a track record stated plainly, not a pile of
adjectives.

- Introduce the two to four players who actually matter with a quick,
  vivid line each in the `situation` segment: who they are and what
  they're known for, in a sentence or two.
- Call a player back in whichever `unfurl_<concept>` segment covers the
  move they made, when their known style or history explains *why* they
  did it that way ("this is exactly the kind of uptier this fund is
  known for"). Let the Guest's reaction carry some of the color —
  surprise, a raised eyebrow, "wait, the same firm that—?" — rather than
  stacking adjectives onto the Host's lines.
- Only what research section 9 sourced. No invented quotes, no guessed
  motives or inner thoughts, no characterization the research didn't back
  with a citation. If the research has no sourced angle on someone, name
  them plainly and move on rather than inventing one.
- Economical: a sentence or two per beat. This teaches the desk's
  vocabulary for how players behave — aggressive, cooperative, a repeat
  player, a known rivalry — it is not a profile piece, and it never
  displaces a number, a mechanism, or a definition.

## Two framings, one arc

Read the framing from the research header and section 1 timeline:

- **Live**: dated events remain. The situation segment ends on "what is
  happening right now and what is scheduled next"; the unfurling
  segments explain what each side is trying to do and how a desk would
  position *now*; the closing segment is "what to watch": catalysts,
  open questions, documents to read before the next hearing.
- **Closed**: the plan is effective or the deal is done. The situation
  segment ends on how it played out; the unfurling segments explain why
  each step happened and what a desk would have done at the time,
  including where the market got it right or wrong; the closing segment
  is "what it taught": the outcome by class, the post-closing loose ends
  (trusts, litigation, the new capital structure), and documents to read
  to see the whole case.

The didactic arc below is identical in both framings; only the tense and
the final segment's content change. Name the last two segments `recap`
and `watch` in both cases.

## Episode shape (seven to nine segments, each 2 to 4 minutes)

Follow this arc. Segment `name` values are lowercase snake_case; the
first, second and last two names are fixed so the audio log is comparable
across episodes.

1. `situation` (~3 min, ~450 words). Who the company is, what it does, why
   it is in trouble, what is happening right now and the next dated
   events, plus a quick, vivid introduction of who's driving it (research
   section 9). Plain English; no jargon beyond what a generalist knows.
2. `concepts` (~4 min, ~550 words). Name the three to six ideas from
   research section 12 and give each a one-paragraph intuition tied to
   the company, and walk the capital structure ladder for this company.
   This is a map of the rest of the episode.
3. to 6. `unfurl_<concept>` segments (~9 min total, ~1,350 words, three
   or four segments). Take each concept in turn and go deeper: how it
   works mechanically, what the documents actually say in this case, what
   the numbers are and what they compare to, who wins and who loses, how a
   desk would trade or position around it, what could go wrong, and —
   where a player's known style or history explains the move — a beat of
   character color tying the mechanism to the person. This is where
   accounting, capital structure and legal detail get taught properly,
   always through the lens of the event at hand. Gentle explainers for
   new concepts live here, at the moment the story needs them.
7. `recap` (~2 min, ~300 words). The trader's recap, from research
   section 8's closing paragraphs. Three beats, in this order, each tied
   to a rung and a number: **where the value accumulated** (which
   instruments ended up holding the enterprise value, and in what form);
   **the twists, turns and risks** (the two or three moments it could have
   gone the other way, and what a desk would have been watching); and
   **winners, losers, and who was left in the dust** (by class and by
   named player). The Guest asks "so if I'd been on the desk, where did I
   want to be?" and the Host answers for each round of the deal. In a
   live framing, say what is still in play.
8. `watch` (~2 min, ~300 words). Live: dated catalysts, open questions,
   and two or three things the listener could now go read (the RSA, the
   8-K, a docket entry), named with the vocabulary to understand them.
   Closed: the loose ends and the same reading list. End with one line
   pointing the listener to the quiz.

## Writing rules

- **~150 words per spoken minute. Target 20 minutes: 2,900 to 3,200 words
  total**, counted over all `text` fields. Each segment 300 to 600 words.
- **No number without a comparison** that makes it meaningful, in the
  same turn ("$2.6 billion of DIP, which is more than the company's
  entire EBITDA for the last three years combined"). A number with only
  a date or a label is not enough. Round for the ear: "about two point six
  billion", not "$2,612.4 million". Spell out units.
- **No concept without a concrete tie back to this company** within the
  same segment.
- **Character color is seasoning, not substance.** It only earns its
  place when it's sourced in the research and it explains a mechanism.
  If a segment runs over budget, cut a color beat before cutting a
  definition, a number, or a comparison.
- **Gentle beats clever.** For a new concept, the everyday analogy comes
  before the mechanism and the number comes after both. The Guest
  restates it in their own words once. Never define two new terms in the
  same turn.
- Write for the ear: short sentences, contractions, no lists, no
  parentheticals, no citations or bracketed source tags, no URLs. Say
  "eight-K" and "three sixty-three sale" the way people say them. Expand
  acronyms on first use.
- Each turn is one speaker and 15 to 120 words. Alternate naturally; the
  Guest speaks at least a quarter of the time.
- Each segment has a one-sentence `direction` for the text-to-speech
  model describing pace and mood ("Measured and warm, like two colleagues
  at a whiteboard; slow down on the numbers.").
- `deal_type` is the value from the research header. `title` is short and
  specific ("Saks Global: When the Vendors Stop Shipping").
- Educational, not investment advice; the hosts can say so once, lightly.

## Format

```json
{
  "company": "…",
  "slug": "…",
  "title": "…",
  "deal_type": "…",
  "episode": 1,
  "segments": [
    {
      "name": "situation",
      "direction": "…",
      "turns": [
        {"speaker": "Host", "text": "…"},
        {"speaker": "Guest", "text": "…"}
      ]
    }
  ]
}
```

Speakers are exactly `Host` and `Guest`. `episode` is an optional
positive integer that becomes the MP3's track number; use the next number
after the highest `episode` in `episodes/*/script.json`. No other keys.

## Check before writing the file

Draft the script in the scratchpad first. Then validate it against the
Pydantic model and count words:

```bash
uv run python -c "
import sys
from pathlib import Path
from distressed_podcast.models import Script
s = Script.load(Path(sys.argv[1]))
print('total', s.word_count)
for seg in s.segments:
    print(f'{seg.name:24s} {seg.word_count:5d}')
" <path-to-draft>
```

If the total is outside 2,900 to 3,200, or any segment is outside 300 to
600, or validation fails, **rewrite and re-check before writing**
`episodes/<slug>/script.json`. Cutting is usually better than padding:
remove repeated framing, not definitions or numbers.

Finally, re-read once as the Guest: is every new term defined before it is
used, does every number have a comparison, does every concept come back to
the company, is every instrument placed on the ladder, and is every Moyer
connection said out loud? Fix, re-count, then write the file and print the
per-segment word counts.

## Update the ledger

After writing the script, edit `concepts/ledger.json`:

- Append one entry for each concept the episode explained in full for the
  first time: `id` (snake_case, the id research section 12 proposed),
  `name`, `one_line` (a dictionary definition the listener can look up,
  not the analogy), `tier` (`accounting`, `capital_structure`, `legal`,
  `process`, `valuation`, `trading`), `level` 1–5, `moyer` (chapter or
  idea, or null), `aliases` (acronyms and alternative spellings),
  `introduced_in` (this slug), `episode`, `status: "introduced"`, and one
  `history` entry `{"slug", "episode", "event": "introduced", "date"}`.
- For each `needs_reteach` concept the script re-explained, leave its
  status alone (the next quiz decides) and append a history entry with
  `"event": "retaught"`.
- Do not change anything else. Then run `uv run podcast site`; it
  validates the ledger and fails loudly if an entry is malformed.

Print the ids added and retaught.
