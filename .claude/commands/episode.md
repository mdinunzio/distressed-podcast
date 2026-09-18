---
description: Build a full episode for a company: research → script → audio → publish → pre-signed URL
argument-hint: <company name>
---

Build a complete Distressed Explainers episode for: $ARGUMENTS

Run these steps in order. Stop at the first failure and report it; never
skip a step or continue past an error.

1. Invoke the `research` skill with the company name. It writes
   `episodes/<slug>/research.md` and prints the slug. Use that slug for
   every step below.
2. Invoke the `script` skill with the slug. It writes
   `episodes/<slug>/script.json` after validating and word-counting it.
3. Run `uv run podcast audio <slug>`. It renders `episodes/<slug>/episode.mp3`
   and appends character counts and estimated cost to `episodes/<slug>/run.log`.
4. Run `uv run podcast publish <slug>`. It uploads the MP3, research and
   script to the object storage bucket.
5. Run `uv run podcast url <slug>` and print the pre-signed URL it returns
   as the last line of your reply, together with the episode title, the
   total word count, the audio duration and the estimated TTS cost from
   `run.log`.
