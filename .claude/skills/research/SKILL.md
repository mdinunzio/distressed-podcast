---
name: research
description: Research a company's live restructuring for a distressed-debt teaching podcast and write episodes/<slug>/research.md. Use when asked to research a company for an episode, or as step one of /episode.
argument-hint: <company name>
---

# Research a distressed situation for an episode

You are the research analyst on a special situations desk. Your output,
`episodes/<slug>/research.md`, is the **only** source the script skill may
use. Nothing you leave out can be taught. Nothing you get wrong can be
caught later. Research quality is the ceiling on episode quality.

Company: `$ARGUMENTS`. If empty, ask for a company name and stop.

## Ground rules

- **Public information only.** Use your own web search and fetch tools.
  Never write Python that fetches SEC, docket or news hosts, and never
  ingest, reference or store non-public or employer data. If you cannot
  find a document, say so; do not reconstruct it from memory.
- **Never invent numbers or provisions.** Every figure and every
  contractual term must trace to a source in section 13. If a section
  cannot be sourced, write "Not sourced:" and explain what is missing.
  Prefer to say less than to guess.
- **Prefer primary sources** over press, in this order: 8-Ks and 10-Q/10-K
  filings on EDGAR; the docket via the claims agent (Kroll, Epiq, Stretto,
  Verita, Omni) or PACER, especially the first-day declaration, the DIP
  motion, the disclosure statement and the plan; the RSA, indentures, credit
  agreements and intercreditor agreements (often 8-K exhibits); court
  opinions. Then trade press (Reorg, 9fin, Petition, Bloomberg, Reuters, WSJ,
  FT, Law360, CreditSights) and law-firm client alerts. Blogs and
  aggregators are last resort and must be marked as such.
- **Say how you saw each source.** If the fetch tool cannot open a
  document (the egress proxy blocks many docket, EDGAR and press hosts in
  cloud sessions) and you only have a search-result excerpt of it, cite it
  as "(docket, via search excerpt)" or "(press)" and never quote it
  verbatim. Put a sourcing caveat block under the title saying which
  hosts were blocked, so the script skill and the listener know the
  provenance.
- **Date everything.** A live situation moves. Record the "as of" date at
  the top and put a date on every event.
- **Educational, not investment advice.** No recommendations.

## Who the reader of this research is

The script will be a ~20-minute two-host podcast for a listener who has
worked in finance (markets, quant or data), is comfortable with rates,
spreads, yields and a Bloomberg screen, but is **new to distressed
investing and to how a special situations group operates**. They need
ground-up explanations of what a credit desk takes for granted:

- accounting as it matters to creditors (EBITDA vs. cash flow, working
  capital, leases, off-balance-sheet obligations, going-concern language)
- capital structure (secured vs. unsecured, first vs. second lien,
  guarantees, structural and contractual subordination, covenants, baskets)
- the legal machinery (indentures, credit agreements, intercreditor
  agreements, Chapter 11 basics, absolute priority, the automatic stay, DIP
  financing, 363 sales, plans of reorganization, RSAs, out-of-court
  exchanges, LMEs such as drop-downs and uptiers)

The listener is reading Stephen G. Moyer, *Distressed Debt Analysis:
Strategies for Speculative Investors*. Where something you find maps to
Moyer's framework, say so in the research so the script can name it:
causes of distress; the capital structure and where value breaks; valuing
the reorganized firm; the fulcrum security; the Chapter 11 process and the
plan; out-of-court vs. in-court; how distressed claims trade. Do not assume
they have finished the book.

**The episode is didactic first.** The company is the vehicle. So your
research must surface not just what happened but *which concepts the story
forces a newcomer to learn*, with the concrete numbers, document language
and dates that let the script teach each concept through this case.

## The episode shape your research feeds

1. **The situation** (~3 min): who, what, why in trouble, what is happening
   now, next dated events. Plain English.
2. **The concepts at high level** (~4 min): three to six ideas the
   situation turns on, each with a one-paragraph intuition tied to the
   company. Section 11 of your research is this list.
3. **Unfurling** (~11 min): each concept in depth: mechanics, what the
   documents say here, the numbers and what they compare to, who wins and
   loses, how a desk trades or positions, what could go wrong. Sections 3
   to 10 must contain enough specifics for this.
4. **What to watch** (~2 min): dated catalysts, open questions, two or
   three documents the listener could go read. Sections 1, 10 and 13.

## How to work

1. **Slug.** Lowercase the company's common name, replace non-alphanumerics
   with hyphens, collapse repeats, strip suffixes like Inc/Corp/Holdings
   (`saks-global`, `spirit-airlines`). Create `episodes/<slug>/`.
2. **Orient (breadth first).** Search for the company plus "Chapter 11",
   "restructuring support agreement", "8-K", "DIP", "exchange offer",
   "plan of reorganization", "docket". Find the claims-agent site and the
   EDGAR filing index if the company or its notes are registered. Establish
   the timeline before reading anything deeply.
3. **Primary documents (depth).** Fetch the first-day declaration (it is
   the best single summary of the capital structure and the causes),
   the DIP motion and order, the RSA and its term sheet, the disclosure
   statement (valuation, recoveries by class, liquidation analysis, plan
   mechanics), and the plan. For pre-petition documents, fetch the 8-K
   exhibit list and read the indenture or credit agreement sections that
   matter (liens, guarantees, restricted payments, permitted debt baskets,
   amendment thresholds, sacred rights).
4. **Numbers.** For every figure, capture value, unit, date and source.
   Pair each with a comparison the script can use: leverage vs. EBITDA,
   DIP size vs. liquidity burn, recovery vs. trading price, claim size vs.
   enterprise value. Note the accounting caveats a creditor applies
   (add-backs, leases, factoring, off-balance-sheet obligations, going-
   concern language, restricted vs. unrestricted subsidiaries).
5. **Cross-check.** Where two sources disagree, record both and say which
   you trust and why. Where the press reports a number without a document,
   label it as press-reported.
6. **Write `research.md`** with exactly the headings below, in order.
   Dense prose and tables, not bullets of adjectives. Cite inline as
   `[S3]` referring to the numbered list in section 13.

## Required headings, in order

```
# <Company>: <one-line description of the situation>
As of: <date>. Slug: <slug>. Deal type: <e.g. prearranged Chapter 11 / prepack / out-of-court LME / Chapter 22>

## 1. Situation summary and timeline
## 2. Business overview and why it broke
## 3. Financials that matter to creditors
## 4. Capital structure, senior to junior
## 5. The key documents and what they say
## 6. Where the fulcrum security sits and why
## 7. The restructuring, step by step
## 8. Who wins, who gets diluted or primed, and by how much
## 9. How a special situations desk would look at each part of the structure
## 10. Risks and what could derail it
## 11. Concepts to teach in this episode
## 12. Glossary
## 13. Sources
```

What each section must contain:

1. Dated timeline, most recent first, ending with what is scheduled next
   (hearing dates, milestones under the RSA or DIP, maturities, votes).
2. What the company does, how it makes money, the operational and financial
   causes of distress in Moyer's terms (leverage from an LBO or acquisition,
   secular decline, cyclical shock, mismanagement or fraud, liquidity
   events), and the sequence that led to the current event.
3. Revenue, EBITDA (reported and adjusted, with the add-backs named), free
   cash flow, liquidity (cash plus revolver availability) and leverage,
   with dates and the creditor's caveats. Table where possible.
4. One table, senior to junior: instrument, size, rate, maturity,
   security and ranking, guarantors, key covenants, and trading level or
   price with date if public. Then prose on structural points: which
   entities issue and guarantee, unrestricted subsidiaries, intercreditor
   terms, where trade and lease claims sit.
5. For each governing document actually in play (indenture, credit
   agreement, intercreditor, RSA, DIP credit agreement, plan): what it is,
   who the parties are, and the specific provisions that matter here,
   quoted or closely paraphrased with the section number where you have it.
6. The class where value runs out, with the valuation and claims math that
   puts it there, and who holds it.
7. The transaction mechanics in order: what is exchanged for what, new
   money, roll-ups, priming, releases, milestones, conditions.
8. A recovery table by class (plan or estimated), pre- and post-deal
   ownership, and who was primed, subordinated or diluted.
9. Instrument by instrument, how a desk would think about it: what you
   would own to express which view, the asymmetry, the trade that already
   happened, what the price implies.
10. Legal challenges, valuation fights, operational risks, financing
    conditions, regulatory approvals, and what happens if the deal fails.
11. Three to six concepts, each with: one-line definition, why this
    situation needs it, the specific fact from this case that teaches it,
    and the Moyer chapter or idea it corresponds to (or "not in Moyer").
12. Every term of art used above, one sentence each, alphabetical.
13. Numbered list `[S1]`… of every URL used, primary sources first, each
    with document title and date.

## Before you finish

- Every number in sections 3, 4, 6 and 8 has a citation.
- Section 11 has three to six concepts and each has a concrete fact.
- Section 1 ends with the next dated event, or says none is scheduled.
- You have stated explicitly what you could not source.
- The file is at `episodes/<slug>/research.md` and nothing else was
  written to the repo.

Print the slug and a five-line summary (situation, fulcrum, deal type,
next catalyst, biggest gap in the research) when done.
