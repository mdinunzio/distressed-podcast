---
description: Build a full episode for a company: progress → research → script → quiz → audio → site → publish → pre-signed URL
argument-hint: <company name>
---

Build a complete Distressed Explainers episode for: $ARGUMENTS

Run these steps in order. Stop at the first failure and report it; never
skip a step or continue past an error.

0. Invoke the `progress` skill. It pulls the listener's quiz attempts into
   `concepts/ledger.json` so this episode knows which concepts to re-teach.
   If the quiz artifact has not been published yet it says so; continue.
1. Invoke the `research` skill with the company name. It writes
   `episodes/<slug>/research.md` and prints the slug. Use that slug for
   every step below.
2. Invoke the `script` skill with the slug. It writes
   `episodes/<slug>/script.json` after validating and word-counting it, and
   appends the concepts it introduced to the ledger.
3. Invoke the `quiz` skill with the slug. It writes
   `episodes/<slug>/quiz.json` and validates it with `uv run podcast site`.
4. Run `uv run podcast audio <slug>`. It renders `episodes/<slug>/<slug>.mp3`
   and appends character counts and estimated cost to `episodes/<slug>/run.log`.
5. Run `uv run podcast site` and republish `quiz/build/index.html` to the
   artifact URL in `quiz/artifact.json` with the Artifact tool (same URL,
   `capabilities` omitted so the `db` grant carries over). If
   `quiz/artifact.json` does not exist, publish it as a new artifact with
   `capabilities: {db: {}}`, icon `quiz`, and write the URL to that file.
6. Run `uv run podcast publish <slug>`. It uploads the MP3, research,
   script and quiz to the object storage bucket.
7. Run `uv run podcast url <slug>` and print the pre-signed URL it returns
   as the last line of your reply, together with the episode title, the
   total word count, the audio duration and the estimated TTS cost from
   `run.log`, the concepts introduced and re-taught, and the quiz artifact
   URL.
