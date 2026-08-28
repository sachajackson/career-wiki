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

- 🔴 **A test that reads the user's configuration is not testing the code.** Moving one user's tiering
  vocabulary out of shared code and into their vault was right — but the constants then loaded **at import**
  from whatever vault was present, and the suite imports the module. On the author's machine 530 checks
  passed; on a fresh clone five failed, because the vocabulary was empty. **Found by simulating an update
  rather than arguing about one**: clone, rewind, populate a vault, pull, run the tests. That simulation is
  now a check.

- 🔴 **An update can require a vault file it has no way to deliver.** `git pull` replaces the system and
  cannot touch `vault/` — that is the boundary and it is correct. The corollary is that a new required
  setting arrives with the code and **not** the file it reads, and the failure is silent: the radar runs,
  fetches, writes a shortlist, and nothing ever tiers. **`settings_drift.py` is the general check;
  `doctor.py` names the specific ones.**

- 🔴 **A settings file nobody can discover is a default nobody chose.** Two settings files existed in **no**
  documentation at all — not the schema, not a skill, not the setup flow — so a new vault silently ran with
  CV spelling checks off and no way to annualise a day rate. **A test now asserts every settings path the
  system knows about is named in `SCHEMA.md` and in `career-init`.**

- 🔴 **Never guess a number that is personal.** An agent annualised a contract day rate at 250 working days
  and reported €700–750/day as €175–190k when at the user's own 220 it is €154–165k — **14% high, on the one
  number deciding whether a contract cleared their floor.** *"How many days would you bill in a year?"* has
  one right answer per person. **Ask; do not pick a market convention.**

- 🔴 **A destructive flag must be scoped to the run it is typed on, or say what it will destroy.** `--reset`
  on a run restricted to a single adapter wiped the memory of all 6,462 seen roles, because the scoping of
  the run does not carry to the flag. **The count was known at that moment and printing it would have cost
  nothing.**

- 🔴 **Escape user-supplied text before putting it in a table.** A `|` in a job title splits the cell, and
  recruiters use them constantly — *"Barden | B Corp"*, *"Engineering Manager | Build & Lead a New Team"*.
  43 rows of one run rendered with every value shifted a column left and the link under the wrong heading.
  **The row still looks like a row**, which is why it survived weeks in a hand-maintained table too.

- 🔴 **A number without its unit can read as its own opposite.** A pay regex that searched only titles turned
  *"€400-650/day"* into *"€400"* — against a €130k floor that reads as catastrophic when it is roughly €150k.
  **And the guard must cover every path**: rejecting it as a rate simply let the salary pattern return the
  same bare number.

- 🔴 **Search prose for a value only when the value carries its own unit.** Searching adverts for a salary
  produced *"$1.1"* from *"$1.1 trillion in assets under management"*. A day rate is safe to look for because
  *"per day"* is part of it; a bare number in body text is not. **And benefits sections are full of per-day
  numbers** — a *"€18 daily lunch stipend"* became a role's pay until a magnitude floor and an
  allowance-word veto were added.

- 🟢 **When one field can hold several values, join them — never pick one.** An employer listing a role in
  London, Dublin and two more places renders them as separate spans; taking either end labelled Dublin roles
  as Warsaw and London. **The location filter runs before any description is read**, so the wrong pick drops
  a commutable role silently. This is the second adapter to hit it, which is why it is a lesson and not a
  bug fix.

- 🔴 **An exclusion verified against one source is not verified.** A watched employer's excluded division
  was filtered correctly on that employer's own ATS, where the company field carries the parent's name and
  the division sits in the title — which is what the check was written and measured against. **An
  aggregator labelled the same roles with the DIVISION as the company**, the parent name never matched, the
  division test never ran, and sixteen rows reached a shortlist. **It looked correct because it was
  correct, on the one source it had been tested against.** Test a filter against every source that can
  supply the field it reads.

- 🔴 **Never build a work batch from the unfiltered corpus.** The cache holds everything fetched; the
  shortlist holds what passed the filters. Reaching past the filter for a richer source handed three triage
  agents seventeen roles labelled as one city that were in eight others — **and the filter had been working
  correctly the entire time.** The agents caught it, independently, three times over; no computational check
  did, because the check had been bypassed rather than broken.

- 🟢 **An inferential reviewer catches what a deterministic one cannot see.** Every check in this repo reads
  files the pipeline produced. When a step *skips* the pipeline, those checks have nothing to look at. Three
  agents reading job descriptions noticed a geography error in seconds that no test could have found.
  **Guides and sensors are not enough on their own if a step can route around both.**

---


---

## 🟢 Moved out of `BACKLOG.md` on 2026-08-28 — the second pass

**Eleven more entries that were settled rather than outstanding.** Same reason as the 2026-08-26
split: a backlog is a list of work still to do, and none of these is work. **They are still
binding.**

🔴 **Why they accumulated again in two days, which is the meta-lesson:** a finding arrives *while*
something is being fixed, so it gets written where the fixing is happening. **The backlog is where
findings land, and it is the wrong place for them to stay.** Sweeping it is a recurring job, not a
one-off — and until it is swept, real outstanding work is buried under settled reasoning.

🔴 **And the move failed the suite again, in the same way and for the same reason.** The header of
this file already records that the 2026-08-26 move *"forced two corrections"* because the text had
been sitting outside two checks that apply to `docs/`. **This one forced exactly two more**: a
settings file named without its folder, and a lesson still written in the score-out-of-20 model
replaced on 2026-08-25.

🟢 **Twice is a pattern, and it is a useful one.** `BACKLOG.md` is not covered by the checks that
cover `docs/`, so **anything parked there rots unobserved for as long as it stays.** Moving settled
text out is not tidying; it is putting it somewhere the checks can reach it.

### 🔴 The first concurrency design was slower than serial, and the reason generalises

**A thread pool over all (adapter, query) pairs, with a lock per adapter.** It ran 48 minutes against a
20-minute baseline with 0.33s of CPU.

**`map` dispatches in order and the pairs are grouped by adapter, so the pool fills with units belonging
to one adapter and every worker but one blocks on that adapter's lock.** Effective concurrency of about 1,
plus the overhead of pretending otherwise.

🟢 **Interleaving the pairs would have hidden it. One thread per adapter removes the lock**, and satisfies
the `TRUNCATED` contract by construction rather than by mutex — which is what the lock was there for:
`TRUNCATED` is a module attribute set during `fetch()` and read straight after, so two concurrent calls
into one module would each read the other's answer.

🔴 **It was also silent for its entire duration**, because nothing printed until every adapter finished.
**That is worse than the slowness it was fixing.** Progress now prints as each adapter lands.

### 🔴 Two files, one letter apart, opposite privacy rules — know which is which

**`vault/settings/employers.json` and `tools/radar/ats_registry.json` are not variants of each other.**

| | `employers.json` | `ats_registry.json` |
|---|---|---|
| **Holds** | One user's **watch and avoid lists** — companies they will not work for, and why, some of it second-hand | **Public careers endpoints.** Host, tenant, token |
| **Same for every user?** | 🔴 **No.** It is a personal document | 🟢 **Yes.** Identical for everybody |
| **Ships?** | 🔴 **Never.** Ignored, and must stay ignored | 🟢 **Always.** A clone without it has tooling and no data |
| **Contributions** | 🔴 Unthinkable | 🟢 **The one file here a stranger can send a PR for** |

🔴 **They shared a name for a day and it cost the whole afternoon.** `ats_registry.json` was written as
`employers.json`, matched by the `tools/radar/*.json` ignore rule, and **never committed** — every
`git add -A` skipped it in silence while the resolver, the checker and the adapter that depend on it all
shipped. **A clone got the tooling and no data.**

🔴 **And the obvious fix was a trap.** Carving `employers.json` out of the ignore rule — exactly what was
done a day earlier for `templates/settings/search.example.json` — **would have published every user's private avoid list.**
The rule that correctly hides one file is what silently hid the other. **Renaming was the only fix; loosening the pattern was never available.**

**So, for anyone touching that directory:**

- **Do not "tidy" the carve-outs into `*.example.json` or a glob.** The hook's own comment explains why,
  and this is the second file that proves it.
- **Do not rename either file to bring them into line.** They are opposites; the names are load-bearing.
- 🟢 **`tools/tests/test_shipped.py` now fails if a required file stops being tracked, or a private one
  starts.** It is the only check that could have caught this — see below.

### 🔴 The suite got twelve times slower and the docs still promised a second — 2026-08-25

**Found on the first action of the next session: the handover said "305 checks, about a second" and it
took 11.9.**

🔴 **Two tests cost 9.2 of that.** They drive `registry_check.py` **as a subprocess**, pointed at a dead
port on purpose, so they pay its real retry backoff — 1.5s + 3.0s each — **and being a subprocess they
cannot stub `time.sleep` the way the in-process retry test does.**

🟢 **Fixed by making the backoff an environment variable**, set to zero by those two tests. Retries still
happen; only the waiting goes. **11.9s → 2.9s.** And because nothing then proved the wait happens at all,
the in-process test now asserts the backoff is **strictly increasing** — `[1.5, 1.5]` is sorted, and a flat
retry is what hammers a host that has just reset on you.

🔴 **Why this is a defect and not a nicety.** `CONTRIBUTING.md` tells every contributor to run the suite
before every push. **A slow suite gets run less often, and the suite is the one control in this repo that
has never failed.** Speed is not comfort here, it is whether the control gets used.

### 🔴 The test count was written in three places and wrong in all three — 2026-08-25

**`README.md` said 64. `CONTRIBUTING.md` said 65. A `BACKLOG.md` entry said 85. The real figure was past
300.** Nobody had lied; **nothing forces prose to move when code does.**

🟢 **Fixed by not writing it down.** The user-facing docs now describe the suite's *properties* — stdlib
only, no install step, runs in seconds — which are stable, rather than its *size*, which is not.
**And a test now fails if a fixed count reappears in either file.** `BACKLOG.md` is exempt: its counts are
dated records of what one piece of work shipped with, not claims about the suite as it stands.

🟢 **This is the same shape as everything else on this page.** *"Remember to update the count"* is an
instruction. Instructions here have a perfect record of failing. **The check took four lines.**

### 🔴 The backlog drifted again, inside the session that had just audited it — 2026-08-25

**Asked plainly: "is everything that was to be built now done?" The honest answer needed a read, not a
recollection — and the read found this file misreporting its own state in both directions.**

| | |
|---|---|
| 🔴 **One item appeared twice** | *Greenhouse yield is low* — once as `PREFILTER FIXED` near the top and once untouched, **1,160 lines away.** Whichever a reader found first decided whether they thought there was work to do |
| 🔴 **Worse: the wrong body was attached** | The fixed Greenhouse entry carried **the Remote entry's original write-up** under its *"the original write-up follows"* line. Two edits in one place, and the seam was invisible |
| 🔴 **Five entries read as open and were shipped** | The transit-stop table, the internal-move row, the baseline row, the aggregator refetch, and `sources_check.py` — **each verified against the code before being marked**, not from memory |
| 🔴 **Two headings disagreed with their own bodies** | Recording a fix in the text while the heading still read 🔴. **Nobody reads 1,900 lines; they skim headings, so the heading IS the entry** |

🔴 **"Delete an item when it is done" is the instruction, and it is written at the top of this file.** It
has now failed three times: twice caught by audits dated above, once by being asked a direct question.
**An instruction that has failed three times is not going to start working.**

🟢 **So the two mechanical halves are now a test** —
[`tools/tests/test_backlog.py`](tools/tests/test_backlog.py):

- **No two headings describe the same item**, by similarity, ignoring the continuation headings that
  legitimately repeat under fixed entries
- **A heading and its own body must agree** about whether the thing is done

🟢 **It found one on its first run** — an entry whose body said *"✅ Fixed, and made mechanical"* under a
🔴 heading. **Not by reading; by running.**

🟡 **What it deliberately does not check: whether an entry is ACCURATE.** That needs judgement and a test
claiming it would be worse than no test. **The check covers the two failures that are structural, and the
audit discipline above still covers the rest.**

🟢 **And `test_shipped.py` caught the new test file untracked, in the same run** — the second time in two
sessions that the check about untracked files has caught the person adding a check.

### 🔴 Mutation testing can be defeated by the bytecode cache — 2026-08-25

**Found while mutation-testing `doctor.py`, and it invalidates results rather than just wasting time.**

A mutation that **preserves the file's byte length** and is written **within the same second** as the
original is invisible to CPython's `.pyc` invalidation, which compares **mtime and size**. The stale
bytecode gets loaded and **the test runs against the unmutated code**.

🔴 **It reported `MISSED!` for a mutant that the tests do catch** — reversing a severity list, where
`[MISSING, PLACEHOLDER, WARN, OPTIONAL, OK]` and `[OK, OPTIONAL, WARN, PLACEHOLDER, MISSING]` are the
same length to the character. **The wrong conclusion is the dangerous one**: it says a check is weaker
than it is, and the natural response is to weaken the code to match.

🟢 **Fix: run mutation checks with `python3 -B` and `PYTHONDONTWRITEBYTECODE=1`.** Re-run that way, all
nine mutants were caught, including the one that had reported as missed.

🟡 **The general shape is worth keeping.** Any harness that rewrites a file in place and re-executes it is
exposed to this — **length-preserving edits are exactly the ones a careful mutation makes.**

### 🔴 Two dead anchor links, one of them in the README's first sentence — 2026-08-25

**Found by asking where a note had been logged, then checking the link resolved instead of assuming it.**

🔴 **The quietest link failure there is: the page still opens and lands at the top.** Nothing errors, the
prose reads correctly, and the reader silently arrives somewhere other than where the link said.

| Where | What happened |
|---|---|
| `BACKLOG.md` | An entry was renamed on being marked ✅ FIXED **earlier the same session**, and a link to it 900 lines away stopped landing anywhere |
| 🔴 `README.md`, line 6 | Pointed at `#-read-this-before-you-use-anything-here` — **a heading that does not exist and may never have.** The first sentence a stranger reads, in the file linked from job applications |

🔴 **A markdown link check already existed and passed both.** `test_shipped.py` resolved the *file* half of
every link and **split the `#fragment` off and threw it away** — so every anchor in the repo was unchecked
while a test reported the links fine. **A check that covers most of a thing reads exactly like one that
covers all of it.**

🟢 **Now checked**: every `](#anchor)` in every shipped markdown file must match a heading in that file,
slugged the way GitHub slugs them. Two mutations caught — renaming a linked heading, and pointing at one
that never existed.

🔴 **And the check cried wolf within a minute of shipping, on the entry describing it.** The prose above
contains a backticked example of a link, and the first version read it as a link. **Documentation about a
pattern contains the pattern** — the same shape as `_comment` blocks in the placeholder check. Code spans
are now stripped before scanning, with a test for the example case.

🔴 **Worse, that failure reached `main`.** The pre-push gate was
`python3 tools/tests/run.py 2>&1 | tail -2 && git push`, and **a pipe replaces the exit status with
`tail`'s**, so `&&` saw success and pushed a red suite. **The habit of piping test output to `tail` for
readability silently disarms every `&&` after it.** Fixed within two minutes, and recorded because the
gate was followed exactly and still let it through — which is the whole thesis of this file, arriving in
the one place that was supposed to be immune.

🟢 **The push gate is now a hook** — `githooks/pre-push`, which runs the suite and refuses a red push.
**No test could have caught the piped version**: by the time anything runs, the shell has already thrown
the status away, so the check had to move somewhere the shell cannot disarm. **That was the last
instruction-shaped control on the push path.**

🔴 **And the test guarding the hook had the same defect as the hook's own failure.** The first version
asserted that no line containing `run.py` is piped — **the hook invokes `"$suite"`, so the one line that
mattered was never checked**, and a mutation piping the suite passed. **Matching the literal and missing
the variable is the same shape as the anchor check that split the fragment off and threw it away.** Three
times in one session: a check that covers most of a thing reads exactly like one that covers all of it.

🟢 **Same failure `wikilinks.py` was built for on the wiki side**, where 40 section links in one vault all
still opened the right page and none went where they said. **It took eight days to arrive on the repo
side, and it arrived because somebody asked a question that made me look.**

### 🟢 What this audit teaches about auditing

🔴 **"The rule is written where it says" is the wrong question.** The previous audit asked it, passed
everything, and missed all of the above. **Ask instead: what would contradict this, and does what it
prescribes have somewhere to live?** Six of nine failed that question. Three ways:

- **Contradicted by another file** (1, and the outcome vocabulary)
- **Prescribes a structure that does not exist** (2, 3, 7)
- **Refers to a place that cannot hold it** (6)

🟢 **A rule that tells someone to write something on a page with no section for it is not a rule, it is a
hope.** Where a rule prescribes a table, **ship the empty table**.

### 🟢 A total that does not move can still be a total that lied

**Status: not a defect in the code. A defect in how results get reported. 2026-08-24.**

An employer research pass produced **the same total before and after** — while every component moved:
NEED 4→5, DELIVER 4→3, EDGE 4→5, and the fourth dimension 3→2. *(Recorded under the score-out-of-20
model this predates; that shape was replaced by N·D·E with LIFE and SEC on 2026-08-25. **The lesson is
about totals hiding movement and is unaffected by which scale is in use.**)*

🔴 **The naive report is "research complete, no change", and it is worse than useless** — it says the
research was not worth running, when in fact it rebuilt the entire basis of the decision.

**The framework already has a rule for this** (*read the row, not the sum*), and the rule was not enough,
because the reporting habit is to lead with the number.

**To do:** when re-scoring after research, **diff the components and lead with the diff**, not the total.
If any component moved by 2 or more, say so in the first line even when the total is unchanged.

### 🟢 One total hid the decision — split it, and count requirements instead of stretching the scale

**Status: designed and migrated 2026-08-24. Recommended as the default shape.**

The framework scored four dimensions 1-5 and summed them out of 20. **Two problems surfaced together.**

🔴 **1. A near-constant factor carries no ranking information.** The user's lifestyle constraint (a
contractual remote arrangement he is unlikely to match elsewhere) meant that dimension scored 2 or 3 for
almost every option. **Inside a total it depressed everything roughly equally — noise, not signal.**

🔴 **2. The total hid where the decision was actually being made.** **Seven roles tied on capability
(14/15) while their old totals spread from 15 to 18** — that entire spread was the personal-fit dimension.
**A role rejected outright scored exactly what the top recommendation scored on capability**, and the
single number made it look weaker rather than equal-but-worse-anchored.

🟢 **The fix, and it required no re-judging** because the composite dimension was already two things:

| | | |
|---|---|---|
| **FIT** | capability + differentiation | /15 |
| **LIFE** | lifestyle alone | /5 |
| **SEC** | employer stability alone | /5 |

**Keep the sub-scores visible.** Two roles both at 14 split into 5·5·4 (*would deliver it well, so would
others*) and 5·4·5 (*brings something rare, with real gaps*) — **a distinction the sum destroys.**

### 🔴 The related trap: do not answer a tie by lengthening the ruler

**The user asked whether scoring each dimension out of 20 — a total out of 100 — would discriminate
better. It would not, and the reasoning generalises.**

- **The anchors are defined by evidence, not degree.** *Strong and evidenced* vs *good with gaps that do
  not touch the core* is a defensible distinction. **16 vs 17 is not** — the digit gets generated rather
  than derived, which is the one thing a knowledge-based system must never do.
- 🔴 **It produces persuasive noise.** *16 versus 14* reads as a finding. It would be a coin flip.
- 🟢 **It would not even fix the tie**, which is a *ceiling* effect: the user only assesses roles that
  already look plausible, so everything clusters at the top of whatever scale exists. **A longer ruler
  moves the cluster, it does not spread it.**

🟢 **Precision has to come from decomposition.** Add a **requirements count** per role: take the
employer's own named requirements, mark each **cleared / partial / gap**, half a point for a partial, and
report the tally.

- One role: **9 cleared, 2 partial, 1 gap of 12 = 83%** → capability 4
- Another: **3 cleared, 3 partial, 1 gap of 7 = 64%** → capability 3

🟢 **Both landed on the score already assigned by judgment. That is the test** — a decomposition worth
trusting validates the judgment rather than replacing it, and it gives the user something checkable line by
line instead of a number to take on faith.

🔴 **Score it from the employer's own posting**, never an aggregator's — see the truncation defect above —
and **mark it TBC where no full posting was ingested.** Most rows will be TBC, which usefully flags which
scores came from a summary.
