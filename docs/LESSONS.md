# Lessons

**Rules learned the hard way, already applied, recorded so they are not undone.**
[← back to README.md](../README.md)

**These are not the schema.** [`SCHEMA.md`](../SCHEMA.md) says how the system works and is replaced by an
update; [`BACKLOG.md`](../BACKLOG.md) records what is still wrong. This file records what going wrong
*taught*, so a later change does not quietly reverse a fix that cost something to find.

🔴 **Each of these was learned by shipping the opposite.** A rule with the reason removed is one somebody
overrides the first time it is inconvenient, so the failure is kept next to the rule.

🟢 **Split out of `BACKLOG.md` on 2026-08-26.** It sat there because that is where the findings arrived,
but a backlog is a list of work outstanding and none of this is outstanding — it is settled, and it was
the only settled thing left in the file after the completed entries were pruned.

---

🔴 **Moving this file forced two corrections, and that is itself the lesson.** In `BACKLOG.md` this text
sat outside two checks that apply to `docs/`. One line still scored work pattern against the single
dimension that was split into LIFE and SEC on 2026-08-25; another named a settings template without its
folder. **Neither was visible while the text lived in a file those checks did not read.** Where a
document sits decides what is allowed to rot in it.

🟡 **Wording this note took two attempts**, for the same reason the commit guard has fired on its own
postmortems twice: a check that looks for a stale term finds it in the sentence explaining that it is
stale. Reworded rather than overridden — routine overriding is how a good check stops being one.

- **`employer:` belongs only on single-subject pages.** Applying it to discursive pages produced six false
  attributions immediately, because a page discussing four employers claims every figure on it for one.
  Narrow `Achievements - <Employer> <Years>` pages carry the attributable numbers instead.
- **Assess a role the moment it is found**, in the same turn, even an obvious rejection. An unassessed role
  occupies attention, looks like an option, and decays.
- **Read the full requisition title before scoring work pattern.** Employers often state it there
  (*"(Hybrid, IRE)"*) and aggregator listings truncate it. It is worth up to two points of **LIFE** and is TBC
  on most roles.
- **Never resolve an UNSOURCED finding by adding the figure to the wiki.** That launders an invention into
  a source, and every future application then treats it as evidence.
- **Query breadth is not how the radar improves.** Doubling from 20 to 40 terms fetched 65% more roles and
  produced one more HIGH-signal role. **Frequency beats breadth** — and **check the filters before adding
  queries**: fixing the time window produced fifty-one where doubling the query list produced one.
- 🔴 **When two different numbers share a name, renaming the column is the smaller half of the fix.**
  Making one of them non-numeric is what ends it. A keyword tally and a framework score were both called
  *score*; two rounds of warning text failed before the tally became `HIGH`/`MED`/`LOW`. **A word cannot be
  mistaken for a score out of 15 even by accident.**
- 🔴 **Never display a value that sums a signal with a bonus as a bare number.** It implies a precision it
  does not have — two roles showed an identical `23` where one was 20 points plus a salary bonus.
  **Coarse labels state the weaker, true claim.**
- 🔴 **Guard on the sentinel, not on truthiness.** `if days:` instead of `if days is not None:` made a
  window of 0 silently become an unfiltered sweep — **the exact failure the None handling had just been
  written to prevent, reintroduced two files away by the shorter spelling, in the same change that
  documented the contract.** Found in review. A contract stated in one file and spelled loosely in
  another is not a contract.
- 🔴 **A header that describes a run must be true of every row under it.** The shortlist was headed
  *"7-day window"* while board adapters contributed postings of any age. **Pre-existing and invisible
  until the header was rewritten** — the reader had no way to know how old a row could be. Adapters now
  declare `HONOURS_DAYS` and the header narrows itself when they disagree.
- 🔴 **Test fixtures are example files, and the placeholder rule applies to them too.** The rule was
  written for `templates/settings/search.example.json` and never carried across. An audit found a real first name in one
  fixture's example address, a real city in another, and two fixtures built from the user's actual
  history — one of them restating incidents `BACKLOG.md` already describes, so the pair could be read
  back together. **Nobody wrote those as personal files; they were written by starting from something
  true**, which is the same mechanism as the `.example` config. 🟢 **Where a fixture must stay realistic
  to be a valid test — a well-written CV, for the cadence checks — rewrite it as invented rather than
  replacing it with placeholder text, and check the measurements it exercises are unchanged.**
- 🟢 **A careers site that is not Workday may still be a Workday tenant underneath, and the apply links
  say so.** One employer's site was Phenom People — 82 platform tells — and looked like a dead end for
  every ATS adapter. **Its apply links pointed at `<tenant>.wd1.myworkdayjobs.com/<site>/job/…`, which is
  the host, tenant and site the adapter needs.** A front end is not the ATS. **Grep a careers page for
  `myworkdayjobs|myworkdaysite|wday/cxs` before concluding an employer cannot be watched.**
- 🟢 **Run a new adapter against a real endpoint the same day it is written.** Two employers and four
  minutes found two defects that recorded fixtures could not, because **a fixture asserts the shape the
  code already produces.** The fixtures are still worth having — they are what keeps the fix from
  regressing — but they cannot be the first contact with reality.
- 🔴 **Ship the empty table.** A rule that says *"keep a table of X on page Y"* is not in force until page
  Y has an empty table of X on it. Three of the nine documented rules prescribed a structure that existed
  nowhere, and a fourth pointed at a table with no column that could hold its answer.
- 🔴 **A documented rule with contradicting code is worse than no rule.** *"Remote is country-scoped"* was
  written down here as handled — and the filter underneath it was waiving every exclusion whenever the
  word appeared, which is the reverse of the rule. **Because the file said it was handled, nobody looked.**
  When listing a rule as documented behaviour, check the code agrees with it.
- 🟡 **A filter that is wrong in both directions looks like a tuning problem.** A board prefilter matching
  the first word of the query kept the irrelevant and dropped the relevant, and the symptom — poor yield —
  reads as "the thresholds need work". **Check what a filter actually matches on before tuning it.**
- 🔴 **A scoring term only some inputs can earn is a measurement of the input pipeline.** The radar's
  tally added 3 for a visible salary — and only one of six adapters returns a structured salary field, so
  the same role fetched two ways scored two different ways, by enough to cross a band. **Ask of any term:
  can every input earn this? If not, it is scoring the route, not the thing.**
- 🟡 **A term that quietly shifts a score is invisible to a suite that never asserts the score.** 208
  tests passed both with the bonus and without it. **Where a number decides something, assert the number,
  not just that the code runs.**
- 🔴 **One probe cannot diagnose an ambiguous failure. Add a control.** *"404 because that country is not
  covered"* and *"404 because the key is wrong"* look identical alone and point opposite ways. Probing a
  **known-good control** alongside the real target turns a guess into an answer, and it has now paid for
  itself twice — once for country coverage, once for an ATS that answers a nonsense site with the whole
  tenant's jobs. **Where a wrong config returns plausible data rather than an error, a control probe is
  the only thing that will ever catch it.**
- 🟢 **Mutation-test a checker before believing it.** All 22 Workday tests passed first run; deliberately
  breaking the code found one that passed for the wrong reason, because **two code paths set the same
  flag and removing either changed nothing.** Collapsing them to one made the test meaningful and the
  code shorter. **A green suite proves the tests ran, not that they would have caught anything.**
- 🔴 **A source that caps results is reporting the cap, not the match count.** Detect the difference
  between *the source ran dry* and *we hit our own limit*, and say which. Only the first proves a result
  set is complete, and **presenting a capped run as complete is the same silent failure as a filter nobody
  knew was on.**

---
