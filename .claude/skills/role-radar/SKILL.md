---
name: role-radar
description: Search job sources for new roles, filter and rank them against the user's own scoring framework, and report only what they have not already seen. Use when asked to look for jobs or check for new roles.
---

# role-radar

Finds roles and ranks them against `Role Scoring Framework.md`. **Triage, not judgement** — the script
produces a keyword score; you produce the assessment.

## Run it

```bash
python3 tools/radar/radar.py --days 7
```

| Flag | Effect |
|---|---|
| `--days N` | Posting window. **7 is the right default** — one day returns a handful, mostly noise |
| `--adapter NAME` | Restrict to one source. Default: whatever `config.json` enables |
| `--reset` | Forget what has been seen and rebuild |
| `--score-only` | Re-score the cached corpus without re-fetching. **Use when tuning** |

Needs `tools/radar/config.json` — copy `config.example.json` and add an Adzuna key from
[developer.adzuna.com](https://developer.adzuna.com/). Without it, only the employer-board adapters run.

Writes `shortlist.md`, `raw.json` (cached descriptions) and `seen.json` in `tools/radar/`. All three are
gitignored and regenerated.

## Then do the part the script cannot

For anything beyond a handful of promising roles, **delegate the reading to the `role-triage` agent** —
it reads many descriptions and returns a compact shortlist, instead of filling this session's context with
job adverts.

Then:

1. **Drop anything already in the scoring table.** The script only remembers what *it* has seen, not what
   was ingested by hand.
2. **Read the cached description** of anything promising — already in `raw.json`, no refetch needed.
3. **Score properly** on the framework's dimensions. **The script's number has no relationship to the
   framework's number and must never be reported as one.**
4. **Report with reasoning**, then update the role pages, the scoring table, and `log.md`.

**Capture the posting URL and requisition number for anything worth tracking.** A role page without a
link is a dead end three weeks later.

## Known failure modes — check every run

Real defects, found by running it. Two of them silently discarded good roles.

| Failure | Looks like | What to do |
|---|---|---|
| 🔴 **Silent zero** | Every query returns nothing | **The source has changed or started blocking.** If the script reports no fetch failures and still found nothing, be suspicious rather than reporting a quiet week |
| 🔴 **Good role, low score** | A strong role in the lower tier | **Expected, and the most important one.** A title-thin posting scores badly. **Always read the second tier** |
| 🔴 **Location field contradicts the title** | A commutable role filed under a distant city | Handled, but check — location fields are employer-entered and often wrong |
| 🔴 **Vocabulary false positive** | Platform or infrastructure roles scoring high on shared jargon | **Read before believing the score** |
| **Agency reposts** | Same role, two companies | Deduped, but recruiters hide the employer, which makes employer-stability unscoreable until named |

## What it cannot do

- **Sites behind bot protection.** Some large aggregators cannot be fetched, and no workaround should be
  attempted. Use their own saved-search email alerts and paste anything interesting in for scoring.
- **Salary.** Rarely in the feed. The script checks the *title* for a figure, which does catch some.
  Otherwise PAY stays TBC until a screening call.
- **Roles posted only on employer sites** not covered by an enabled adapter.
- 🔴 **"Remote" is country-scoped almost everywhere.** *Remote - UK*, *Remote - Texas*, *Remote -
  Luxembourg*. **Parse the suffix; it is the whole meaning.** Treat an unqualified *"Remote"* as `TBC`, not
  as global, and **never widen the search geography on the word alone** — right to work and tax residency
  sit behind it and appear in no listing.
- 🔴 **A shortlist is not an assessment.** Whatever the radar surfaces, **score it in the same turn it is
  found.** An unassessed role occupies attention, looks like an option, and decays. **Even an obvious no
  gets the dimensions and one sentence on what decided it** — the record of what was rejected and why is
  what stops it being re-surfaced next week.
- 🟢 **Watch preferred employers everywhere, by whatever route each one offers** — their own ATS endpoint
  if they have one, a named query if not. **The point is complete coverage of that employer**, not one
  adapter. And **filter exclusions at division level**: a preferred employer can contain a division the
  user will not work for, and it is usually named in the job title.
