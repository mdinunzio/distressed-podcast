---
name: quiz
description: Write the 20-question quiz (episodes/<slug>/quiz.json) for an episode from its script, research and the concept ledger. Use after the script skill, or as step four of /episode.
argument-hint: <slug>
---

# Write the episode quiz

Slug: `$ARGUMENTS`. If empty, ask for a slug and stop. Read, in this order:
`episodes/<slug>/script.json` (what the listener actually heard),
`episodes/<slug>/research.md` (the facts behind it), and
`concepts/ledger.json` (every concept explained so far and its status).
Write `episodes/<slug>/quiz.json` and nothing else.

## What the quiz is for

The listener takes it right after the episode, in the quiz app. Its job is
to find out which concepts landed. A concept missed here is marked
`needs_reteach` in the ledger by the progress skill, the next episode
re-explains it, and the next quiz re-tests it. So every question must be
tagged with the concept ids it really tests, and every question must be
answerable **from the audio alone**: the listener did not read the research.
Numbers must be the ones spoken on air, rounded the way they were spoken.
The `explanation` can add a line from the research; it is shown after the
answer and should teach, not just confirm.

## The 20 questions

- Exactly 20, ids `q01` to `q20`, in the order the episode covered the
  material (situation first, recap and watch last), so the quiz replays the
  arc.
- Types: at least ten `multiple_choice`; two to four `numeric` (a spoken
  figure, with a `tolerance` that forgives rounding, in a stated `unit`);
  two to four `short_text` (a term of art the episode defined: `accepted`
  lists the term, its acronym, hyphenated and spaced spellings); one to
  three `order` (rank instruments senior to junior, tiers of a waterfall,
  classes by recovery, or steps of a process: `items` are given in the
  correct order and the app shuffles them).
- `concept_ids`: one to three ids per question, all present in the ledger.
  Every concept tagged was either explained in this episode or is a
  `needs_reteach` concept this episode re-taught. Do not tag a concept the
  episode merely mentioned.
- Re-tests: for each ledger concept with status `needs_reteach` that the
  script re-explained, write one question with `retest: true` (two to four
  in a typical episode; zero if nothing was flagged). Make it a different
  question from the one the listener missed, testing the same idea.
- Include at least one question on the capital structure ladder (where an
  instrument sits and how it is paid) and at least one drawn from the
  `recap` segment (where value accumulated, who won, who was left in the
  dust).
- Multiple choice: three to five choices, one clearly correct on the
  episode's facts, distractors that are plausible misreadings (the wrong
  rung, the wrong party, the headline number instead of the creditor's
  number). No "all of the above".
- **No unintentional tells.** The listener must not be able to pick the
  answer without knowing the material. In particular:
  - Every distractor is as long, as specific and as expert-sounding as
    the correct choice, and cites a real detail from the episode used
    wrongly (a real number on the wrong instrument, a real party doing
    the wrong thing). Write the wrong answers with the same care as the
    right one. `podcast site` rejects a correct choice more than 1.25
    times the length of the longest distractor, or shorter than 0.7 of
    the shortest, and rejects a quiz where the correct choice is the
    single longest one in more than 60 percent of the questions: in
    about half of them a distractor should be the longest.
  - No throwaway distractors: never "Nothing", "There is no difference",
    "None of these", a joke, or an option a generalist could rule out
    without having listened.
  - The correct choice never reuses the prompt's wording or the term
    being tested more than the distractors do, and is never the only
    choice that hedges ("roughly", "about") or the only absolute one.
  - Spread the answer position across A–D; `podcast site` rejects a
    quiz where one position holds more than half the answers. (The app
    also shuffles choices on screen, but the file itself must be clean.)

## Difficulty

`level` is 1 (a generalist could answer) to 5 (a desk analyst would have to
think). The mix follows the episode number, so the series gets harder:

| Episode | Level 1 | Level 2 | Level 3 | Level 4–5 |
| --- | --- | --- | --- | --- |
| 1–3 | 5–7 | 8–10 | 3–5 | 0–1 |
| 4–8 | 2–4 | 6–8 | 6–8 | 2–4 |
| 9+ | 0–2 | 4–6 | 7–9 | 4–6 |

Re-test questions take the level of the concept in the ledger. A question's
level must not exceed the highest ledger `level` among its concept ids
plus one.

## Format

```json
{
  "slug": "…", "episode": 1, "title": "<the script title>",
  "questions": [
    {"id": "q01", "type": "multiple_choice", "level": 1, "concept_ids": ["working_capital"],
     "prompt": "…", "choices": ["…", "…", "…", "…"], "answer": 1, "explanation": "…"},
    {"id": "q02", "type": "numeric", "level": 2, "concept_ids": ["dip_financing"],
     "prompt": "…", "answer": 1.0, "tolerance": 0.05, "unit": "$ billions", "explanation": "…"},
    {"id": "q03", "type": "short_text", "level": 2, "concept_ids": ["pik"],
     "prompt": "…", "accepted": ["PIK", "payment in kind", "paid in kind"], "explanation": "…"},
    {"id": "q04", "type": "order", "level": 2, "concept_ids": ["payment_waterfall"],
     "prompt": "…", "items": ["first", "second", "third"], "explanation": "…"},
    {"id": "q05", "type": "multiple_choice", "level": 2, "retest": true, "concept_ids": ["ebitda"],
     "prompt": "…", "choices": ["…", "…", "…"], "answer": 0, "explanation": "…"}
  ]
}
```

`retest` defaults to false and may be omitted. No other keys.

## Check before finishing

Draft in the scratchpad, then validate the draft and its ledger references
by copying it into place and building the site:

```bash
cp <draft> episodes/<slug>/quiz.json && uv run podcast site
```

`podcast site` fails if the JSON is malformed, the slug or episode number
disagrees with `script.json`, or any `concept_ids` entry is missing from
the ledger. Fix and re-run until it passes. Then re-read the quiz as the
listener: is every question answerable from what the hosts said, is every
number the spoken one, does every explanation teach? Print the type and
level mix and the list of re-test questions when done.
