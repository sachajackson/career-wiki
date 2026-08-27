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

🔴 **Google is the one source with NO posting date at all.** Not Workday's *"30+ days"* floor — **none**.
Its rows show an empty Posted column and **may be any age**. **Never report a Google role as new**, and treat
a long-open requisition as a live possibility. It reads Google's own **server-rendered** careers page, then
fetches each matching role's detail page for the full description — **the listing alone carries only the
minimum-qualifications bullets**, which tallied a maximum of 4 against a MED threshold of 10, so **not one
Google role could ever have tiered without it.**
| `--help` | **Works before anything is configured.** Lists every flag and every adapter name |
| `--adapter NAME` | Restrict to one source. Default: whatever `vault/settings/search.json` enables |
| `--reset` | Forget what has been seen and rebuild |
| `--retier` | Re-tier the cached corpus without re-fetching. **Use when tuning** (`--score-only` still works) |

### How long it takes, measured

🔴 **About thirty minutes for a full `--all-open` sweep, measured 2026-08-26** — not the six minutes
recorded below, which was a smaller search. **Say thirty before starting one.**

The six-minute figure was 41 queries and three watched employers. It is now **47 queries and
eleven watched employers**: Workday alone covers four boards totalling 5,276 open roles, Oracle returns
7,315, and Google adds a detail fetch per matching role. **The measured run was 924s of fetching plus
description reading — 6,486 roles, 1,580 requests, 15,044 served from the within-run cache.**

The older measurements below are kept because the *shape* of the trade still holds. Three runs of the
same config — 41 queries, three watched employers — on 2026-08-25:

| | Wall | Roles reaching the filter | Requests |
|---|---|---|---|
| Serial, no cache | **1201s** | 87 | ~600 |
| Cache + one thread per adapter | **233s** | 93 | 225 |
| **+ Workday reading its whole board** | **358s** | **479** | 313, plus 3,598 from cache |

🔴 **The last step is slower than the one before it, and that is the right trade.** It costs 125 seconds
and buys **386 more roles** — Workday alone went from 781 rows to 3,255, because the previous shape only
ever saw about 7% of that board. **A faster run that cannot see the roles is not a better run.**

🟡 **Say six minutes before starting it, not after.** Six minutes of near-silence still reads as a hang.
The run prints each adapter as it lands, which is the thing to watch.

🔴 **Workday is the slowest adapter and will stay that way**: its board is the largest, and every row that
hides its locations needs a second call to expand them. Name it if somebody asks why a run is not instant.

### 🔴 `--days` does nothing at all for most configurations

**Only three adapters honour it** — Adzuna, LinkedIn and Oracle. **Greenhouse, Workday, Lever and custom
boards return the entire board**, every open role at any age, because that is the only call those
endpoints offer.

**A config with no Adzuna key and LinkedIn disabled has no date-filtered source**, and `--days 7` then
filters nothing whatsoever. The shortlist header says so in as many words — *"the 3-day window applied to
nothing"* — 🔴 **and that line is easy to skim past while believing a window was applied.**

**Read the header before reporting anything as new.**

### 🔴 Run both, and know which one you ran

**For a year the radar only ever looked at the last seven days, and nobody noticed.** Roles still open but
posted earlier were never fetched at all. On one query: 7 days returned 100 results with the oldest posted
17 August; unfiltered returned 100 with the oldest posted 21 May. **The highest-scoring unapplied role in
that user's table had been posted fourteen days before the run — the radar could not have found it, and the
user sent the link by hand.**

🔴 **But `--all-open` is not a superset of `--days`, and treating it as one is the next version of the same
mistake.** A run has a fixed page budget per query, so spreading it across months makes it sparser:

| | |
|---|---|
| `--days 7` | **Dense recent coverage** — the whole budget spent on one week |
| `--all-open` | **Sparse historical sweep** — the same budget spread across months |

🔴 **Corrected 2026-08-26. This used to say "sources cap a query at roughly 100 results whatever the
window", and for LinkedIn that was wrong by about seven times.** Measured on one query over a 7-day
window: `pages=4` returned 40 rows and reported capped, `pages=40` returned 400 and still reported
capped, and **`pages=80` returned 710 and finally ran dry.**

🔴 **So "capped" in the output usually means OUR budget ran out, not that the source stopped answering** —
and those read identically while meaning opposite things. **The lever is `pages` for that adapter in
`vault/settings/search.json`**, which is why the cap notice says to raise it.

🟡 **Depth is not free, and check the adapter before spending it.** The tail is **mixed, not junk** — one
query's rows past 260 held an unrelated Compliance Manager *and* a precisely on-target senior role. But
**only the board adapters (`greenhouse`, `workday`, `lever`) title-filter their rows**; `linkedin`,
`oracle` and `custom` do not, on the assumption that a search API already matched. **LinkedIn's guest
search matches loosely**, so on that source every extra page reaches scoring unfiltered.

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
of open roles** — say the search was capped, and either raise `pages` for that adapter in `vault/settings/search.json` or
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

### 🔴 The Legitimacy block — report it, never fold it into a score

**Between a fifth and a third of live listings are estimated to be ghost jobs**, 40% of hiring managers
admit to posting one in the past year, and roughly one opening in three never produces a hire.

🔴 **A fake posting is not a low-scoring role. It is not a role.** Folding this into FIT would let a
strong-but-fake posting outrank a real mediocre one, and make a scam read as a mediocre opportunity.
**So it never touches a score, and there is no percentage** — a percentage is a score by another name and
would be ranked within a week.

**Put the line on the role page as its own line.** Then:

- 🔴 **A concern is a reason to ask, never an answer.** *"Ageing: 78 days old"* is worth a sentence in the
  pre-mortem and a question on the first call. **It is not a reason to drop a role** — that is the user's
  call and they may take poor odds knowingly.
- 🔴 **An empty result is not a clean bill of health.** Most of what makes a posting fake is invisible from
  the posting. **Never report a role as verified or genuine** on the strength of nothing being flagged.
- 🟡 **`age unknown` means the source refused to say**, not that the role is fresh. Workday stops counting
  at 30 days and does not always print the `+`.
- 🟢 **Liveness is already covered where it matters** — `build-application` Step 0 confirms the posting is
  still open before anyone spends an evening on it.

### The watchlist — who to watch, and who to skip

`vault/settings/employers.json` (copy `templates/settings/employers.example.json`) holds the user's standing positions. **It is
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
answer. See `SCHEMA.md`.

Needs `vault/settings/search.json` — copy `templates/settings/search.example.json` and add an Adzuna key from
[developer.adzuna.com](https://developer.adzuna.com/). Without it, only the employer-board adapters run.

Writes `shortlist.md`, `raw.json` (cached descriptions) and `seen.json` in `tools/radar/`. All three are
gitignored and regenerated.

## 🔴 The order, before anything else

```bash
python3 tools/pipeline.py --runbook
```

**Ten steps, in order, each with its command.** 🔴 **This file is 323 lines across eighteen sections and
everything below is a caveat, not a sequence** — which is how the `role-triage` delegation, named twice in
this very file, went unused for the life of the repo. **Read the runbook first; read the rest when a step
raises a question.**

## 🔴 Before and after: run the pipeline check

```bash
python3 tools/pipeline.py
```

**It says which stage the search is on and what the next action is**, computed from the vault rather than
remembered. **Run it before starting and again when you think you are finished** — the second run is the one
that matters.

🔴 **It exists because two things failed silently in one session.** A cluster page said *"recorded so the
radar does not re-surface them"* and shipped without the posting URLs, so it re-surfaced all ten — **written
twice, the same way, an hour apart.** And the `role-triage` delegation below **had never once been used** in
the life of this repo, because nothing was looking.

🟡 **`--write` leaves `vault/state/progress.md`** behind, which is regenerable and safe to delete. Useful
when a batch spans more than one sitting.

## Then do the part the script cannot

For anything beyond a handful of promising roles, **delegate the reading to the `role-triage` agent** —
it reads many descriptions and returns a compact shortlist, instead of filling this session's context with
job adverts.

Then:

1. **Drop anything already in the scoring table.** The script only remembers what *it* has seen, not what
   was ingested by hand.
2. **Read the cached description** of anything promising — already in `raw.json`, no refetch needed.
   🔴 **Within this run only.** `raw.json` is overwritten every run with that run's NEW roles, and
   `seen.json` drops everything already known before it gets there — so after the next run it is empty.
   **Measured: run the radar twice against one board and the second run reads zero descriptions and
   writes a 2-byte `raw.json`.** The archive in `vault/postings/` is the durable copy, and
   `tools/radar/refresh.py` re-reads one when somebody is about to act on it.
   🔴 **But an aggregator's cached description is not the posting.** LinkedIn and Adzuna truncate, and the
   truncation is asymmetric: it removes qualifiers (*"at least one of"*), alternatives (*"or internal
   product delivery"*) and the business driver — **the parts that make a candidate more eligible.** A
   system scoring from that text systematically under-scores its user, invisibly, because what is left
   reads perfectly coherently. **Employer-board sources — Workday, Oracle, Greenhouse, Lever, Google — are the
   employer's own text and need no refetch.**
3. 🔴 **Fetch the employer's own posting before scoring anything that came from an aggregator** — not
   before packaging. **By packaging time the score has already been used to decide.** In real use this
   dissolved a red-flagged capability gap that had stood for three days: the aggregator said *"proficiency
   in"* eleven tools, the employer had written *"proficiency in **at least one**"*.
4. **Score properly** on the framework's dimensions. 🔴 **`SIGNAL` is a keyword tally rendered as a
   word and has no relationship to the framework's score. It is a word precisely so it cannot be
   reported as one** — the column used to print the raw tally under the heading *Score*, and a radar
   output of 21 was duly reported to a user as a framework score of 21, which is impossible.
5. **Report with reasoning**, then update the role pages, the scoring table, and `log.md`.

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
- 🔴 **Judge an unqualified `Remote` for you.** *Remote - UK*, *Remote - Texas*, *Remote - Luxembourg* —
  the suffix is the whole meaning, and the radar now parses it: a remote role scoped to an excluded
  place is dropped like any other. **What it cannot resolve is `Remote` with nothing after it**, which is
  shown as **`(scope TBC)`** in the Location column. **That means unknown, never global.** It usually
  means remote within whatever country the requisition was raised in. **Never widen the search geography
  on the word alone, and never report such a role as being in the user's country** — right to work, tax
  residency and payroll entity all sit behind it and appear in no listing. Confirm against the
  requisition, or leave it open.
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

🔴 **And archive the posting text when you score it**, to `vault/postings/<Employer>.txt`. **The cached description is already in `raw.json` and that file is regenerated every run** — so a role assessed today and looked at again in six weeks has nothing behind it unless the text was saved at the time.
  found.** An unassessed role occupies attention, looks like an option, and decays. **Even an obvious no
  gets the dimensions and one sentence on what decided it** — the record of what was rejected and why is
  what stops it being re-surfaced next week.
- 🟢 **Watch preferred employers everywhere, by whatever route each one offers** — their own ATS endpoint
  if they have one, a named query if not. **The point is complete coverage of that employer**, not one
  adapter. And **filter exclusions at division level**: a preferred employer can contain a division the
  user will not work for, and it is usually named in the job title.
