---
name: script
description: Write a ~20-minute two-host teaching podcast script (episodes/<slug>/script.json) from episodes/<slug>/research.md. Use when asked to write or rewrite an episode script, or as step two of /episode.
argument-hint: <slug>
---

# Write the episode script

Slug: `$ARGUMENTS`. If empty, ask for a slug and stop. Read
`episodes/<slug>/research.md` in full before writing a word. Write
`episodes/<slug>/script.json` and nothing else.

## The one hard rule

**Nothing in the script that is not in the research.** No number, date,
provision, name or claim that does not appear in `research.md`. If the
research is silent on something the conversation naturally reaches, the
hosts say so on air ("the filings don't break that out", "we couldn't find
the intercreditor"). If the research marks something as press-reported or
unsourced, the hosts say that too. Do not fill gaps from memory.

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

Every term of art is defined the first time it is spoken, either by the
Guest asking or the Host pausing to define it. Keep a running list while
you write; if a term appears before its definition, fix it.

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
the final segment's content change. Name the final segment `watch` in
both cases.

## Episode shape (six to eight segments, each 2 to 4 minutes)

Follow this arc. Segment `name` values are lowercase snake_case; the
first, second and last names are fixed so the audio log is comparable
across episodes.

1. `situation` (~3 min, ~450 words). Who the company is, what it does, why
   it is in trouble, what is happening right now and the next dated
   events. Plain English; no jargon beyond what a generalist knows.
2. `concepts` (~4 min, ~600 words). Name the three to six ideas from
   research section 11 and give each a one-paragraph intuition tied to
   the company. This is a map of the rest of the episode.
3. to 7. `unfurl_<concept>` segments (~11 min total, ~1,650 words, three
   to five segments). Take each concept in turn and go deeper: how it
   works mechanically, what the documents actually say in this case, what
   the numbers are and what they compare to, who wins and who loses, how a
   desk would trade or position around it, and what could go wrong. This
   is where accounting, capital structure and legal detail get taught
   properly, always through the lens of the event at hand.
8. `watch` (~2 min, ~300 words). Live: dated catalysts, open questions,
   and two or three things the listener could now go read (the RSA, the
   8-K, a docket entry), named with the vocabulary to understand them.
   Closed: the outcome by class, the loose ends, and the same reading
   list.

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

Finally, re-read once as the Guest: is every term defined before it is
used, does every number have a comparison, does every concept come back to
the company, and is every Moyer connection said out loud? Fix, re-count,
then write the file and print the per-segment word counts.
