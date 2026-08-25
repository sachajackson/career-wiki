---
name: role-radar
description: Search job sources for new roles, filter and rank them against the user's own scoring framework, and report only what they have not already seen. Use when asked to look for jobs or check for new roles.
---

# role-radar

Finds roles and ranks them against `Role Scoring Framework.md`. **Triage, not judgement** — the script
produces a `SIGNAL` of HIGH/MED/LOW from a keyword tally; you produce the assessment.

🔴 **`SIGNAL` counts what the role is *about* and nothing else.** It is not affected by salary, by source,
or by how much detail a posting happens to carry. **So it is comparable across sources** — which it was
not until 2026-08-25, when a bonus for a visible salary meant the same role scored differently depending
on which adapter found it.

## Run it

```bash
python3 tools/radar/radar.py --days 7
```

```bash
python3 tools/radar/radar.py --all-open
```

| Flag | Effect |
|---|---|
| `--days N` | Posting window. **7 is the right default for a routine run** — one day returns a handful, mostly noise. **Applies only to searched sources; watched boards ignore it** |
| 🔴 `--all-open` | **No recency filter: everything still open.** Overrides `--days`. See below — it is not a bigger `--days` |
| `--adapter NAME` | Restrict to one source. Default: whatever `config.json` enables |
| `--reset` | Forget what has been seen and rebuild |
| `--retier` | Re-tier the cached corpus without re-fetching. **Use when tuning** (`--score-only` still works) |

### 🔴 Run both, and know which one you ran

**For a year the radar only ever looked at the last seven days, and nobody noticed.** Roles still open but
posted earlier were never fetched at all. On one query: 7 days returned 100 results with the oldest posted
17 August; unfiltered returned 100 with the oldest posted 21 May. **The highest-scoring unapplied role in
that user's table had been posted fourteen days before the run — the radar could not have found it, and the
user sent the link by hand.**

🔴 **But `--all-open` is not a superset of `--days`, and treating it as one is the next version of the same
mistake.** Sources cap a query at roughly 100 results whatever the window, so the two are a trade:

| | |
|---|---|
| `--days 7` | **Dense recent coverage** — 100 results from one week |
| `--all-open` | **Sparse historical sweep** — 100 results across three months |

**So: a frequent windowed run for freshness, and a periodic unfiltered sweep for the standing backlog of
still-open roles.** Dedup handles the overlap and already works.

🔴 **An `--all-open` run produces a backlog, not a shortlist.** The first one surfaced **51 roles above the
read-threshold** in one go. **The assess-every-role-immediately rule does not survive that** — send the
batch to the `role-triage` agent, then assess what comes back. The output says which kind of run it was.

### 🔴 Read the header before reporting the run

**It tells you what the file actually contains, and the three wordings mean different things:**

| Header | What it means |
|---|---|
| `(7-day window)` | Every row came from a searched source that honoured the window |
| `(7-day window on searched sources)` | **Watched boards also contributed, and boards return everything open at any age.** A row here can be months old. The note below the header names which |
| `(watched boards only — the 7-day window applied to nothing)` | `--days` did nothing this run. Do not describe the result as recent |
| `(all open postings)` | An `--all-open` sweep |

🔴 **Never restate the window from the command you typed. Restate it from the header**, which is derived
from the rows that are actually in the file.

### 🔴 When the output says NOT THE COMPLETE SET

**The run hit the source's cap rather than the end of its results, so there is more behind those queries.**
It is not a failure and there is nothing broken. **It means you must not report the run as the complete set
of open roles** — say the search was capped, and either raise `pages` for that adapter in `config.json` or
narrow the query and run it again.

### 🔴 Before trusting a quiet run, check the sources answer

```bash
python3 tools/radar/sources_check.py
```

**Run it when a run comes back thin or empty, and once before relying on a newly configured source.** It
makes no search — it asks each adapter whether it would work at all, and it keeps two distinctions that
a glance collapses:

| Verdict | What it means |
|---|---|
| `NOT CONFIGURED` | **Not a failure.** Nobody set that source up. Most of these watch named employers, so empty means nobody is being watched |
| `NO COVERAGE` | The source works and **does not cover that country**. No key will ever fix it |
| `BAD CREDENTIALS` | The key is wrong. **Told apart from the row above by probing a known-good control** — one probe cannot distinguish them |
| `BLOCKED` / `FAILED` | Reachable but refusing us, or unreachable. The detail says which |

🔴 **"0 usable" means a radar run would be silent — and a silent run looks exactly like a quiet week.**
Report that, rather than reporting no new roles.

🟡 **Read the Oracle warning if it appears.** An unrecognised site value does not fail there, it **widens**:
Oracle answers with the whole tenant's postings instead, so a typo returns *more* roles rather than none.
The check spots it by asking for a deliberately nonsense site and comparing counts.

### The watchlist — who to watch, and who to skip

`tools/radar/employers.json` (copy `employers.example.json`) holds the user's standing positions. **It is
optional; without it nothing changes.** With it:

| List | What it does |
|---|---|
| `watch` | **Complete coverage of an employer**, not whatever they syndicate. The list says *who*; the route — Workday, Greenhouse, Lever, or a named query — is an implementation detail, and one employer may need a different one from the next |
| `avoid` | **Filters before scoring**, so the assess-every-role-immediately rule never spends effort on a settled question. Works at **division** level too: a good employer can contain a division the user will not work in, and it is usually named in the job title |
| `avoid_sectors` | Catches employers the user has never heard of. **Runs after descriptions arrive**, because a sector cannot be judged from a company name |
| `declined` | **Not a filter.** Marks a row with † and the reason. A role turned down on a commute or a start date can legitimately come back |

🔴 **Read what the run says about the list, and act on it:**

- **"no route … NOT watched"** — that employer is on the list and is not being watched. **Say so**; do not
  report coverage the run did not have.
- **"on the watch list AND the avoid list"** — whichever won was an accident. Ask which is right.
- **Console questions about stale or unbased exclusions** — an exclusion older than two years, or one
  with no basis recorded. **Raise them once, when they appear**, not every session.

🔴 **The contents never leave the machine.** Not into a CV, a cover letter or an oversight export, and
**never suggest the user repeats a reason to anyone.** *"It is not the right fit for me"* is the whole
answer. See `CLAUDE.md`.

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
3. **Score properly** on the framework's dimensions. 🔴 **`SIGNAL` is a keyword tally rendered as a
   word and has no relationship to the framework's score. It is a word precisely so it cannot be
   reported as one** — the column used to print the raw tally under the heading *Score*, and a radar
   output of 21 was duly reported to a user as a framework score of 21, which is impossible.
4. **Report with reasoning**, then update the role pages, the scoring table, and `log.md`.

**Capture the posting URL and requisition number for anything worth tracking.** A role page without a
link is a dead end three weeks later.

## Known failure modes — check every run

Real defects, found by running it. Two of them silently discarded good roles.

| Failure | Looks like | What to do |
|---|---|---|
| 🔴 **Silent zero** | Every query returns nothing | **The source has changed or started blocking.** If the script reports no fetch failures and still found nothing, be suspicious rather than reporting a quiet week — **run `sources_check.py`, which exists to answer exactly this** |
| 🔴 **Silent truncation** | A round result count, and the output says NOT THE COMPLETE SET | **The cap is the constraint, not the match count.** Never describe a capped run as everything that is open |
| 🔴 **Good role, low signal** | A strong role sitting in MED | **Expected, and the most important one.** A title-thin posting signals low. **Always read MED** |
| 🔴 **Location field contradicts the title** | A commutable role filed under a distant city | Handled, but check — location fields are employer-entered and often wrong |
| 🔴 **Vocabulary false positive** | Platform or infrastructure roles signalling HIGH on shared jargon | **Read before believing the signal** |
| 🟡 **Pay is missing far more often than it is absent** | A blank `Pay` column | **It is read from the job title only**, so it is blank for most roles whatever they pay. **Blank means unknown, never unpaid or low** — leave PAY as `TBC` rather than inferring anything from it |
| **Agency reposts** | Same role, two companies | Deduped, but recruiters hide the employer, which makes employer-stability unscoreable until named |

## What it cannot do

- **Sites behind bot protection.** Some large aggregators cannot be fetched, and no workaround should be
  attempted. Use their own saved-search email alerts and paste anything interesting in for scoring.
- **Salary.** Rarely in the feed. The script checks the *title* for a figure, which does catch some.
  Otherwise PAY stays TBC until a screening call.
- 🔴 **Tell you how much it did not fetch, beyond the cap.** It can tell you a query *was* capped, not what
  was behind it. **Narrower queries are the only way to see past a cap** — not more pages, which the cap
  ignores.
- **Roles posted only on employer sites** not covered by an enabled adapter.
- 🔴 **"Remote" is country-scoped almost everywhere.** *Remote - UK*, *Remote - Texas*, *Remote -
  Luxembourg*. **Parse the suffix; it is the whole meaning.** Treat an unqualified *"Remote"* as `TBC`, not
  as global, and **never widen the search geography on the word alone** — right to work and tax residency
  sit behind it and appear in no listing.
- 🟢 **Miss an employer that runs Workday.** It covers a large share of enterprise careers sites, including
  ones that look bespoke. **It also carries three things no aggregator does**: the requisition number, the
  employer's own posting date, and the extra locations behind a listing that says *"4 Locations"* — which
  matters because the location filter runs *before* any description is read, so a role open in the user's
  city but advertised elsewhere would otherwise be dropped unseen.
- 🟢 **Miss an employer that runs Oracle Cloud Recruiting.** The other large enterprise ATS, and the
  richest source here: **an exact posting date**, the requisition number, secondary locations and a
  description in the listing. Two values, both in the careers URL.
- 🟡 **Read a date ending in `+` as a floor, not a date.** Workday will only say *"30+ days ago"*, so the
  posting is **at least** that old and may be far older. **A six-week-old senior requisition may already be
  at offer stage** — that is a reason to deprioritise it, and the `+` is the only thing telling you.
- 🔴 **A shortlist is not an assessment.** Whatever the radar surfaces, **score it in the same turn it is
  found.** An unassessed role occupies attention, looks like an option, and decays. **Even an obvious no
  gets the dimensions and one sentence on what decided it** — the record of what was rejected and why is
  what stops it being re-surfaced next week.
- 🟢 **Watch preferred employers everywhere, by whatever route each one offers** — their own ATS endpoint
  if they have one, a named query if not. **The point is complete coverage of that employer**, not one
  adapter. And **filter exclusions at division level**: a preferred employer can contain a division the
  user will not work for, and it is usually named in the job title.
