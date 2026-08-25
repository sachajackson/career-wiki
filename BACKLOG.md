# Backlog

**Known gaps, deferred decisions, and things that have gone wrong once.** Anything found while using the
system that is worth fixing but not worth stopping for.

**Add to this rather than fixing in passing when the fix would derail what you are doing.** A gap that is
written down is a decision; a gap that is remembered is a risk.

Newest first within each section. Delete an item when it is done — the log of what changed lives in git.

## 🔴 What belongs here, and what does not

**This file is public. It records problems with the *system*, never anything about the *person* using it.**

| Belongs here | Belongs in the user's own wiki |
|---|---|
| A tool behaves wrongly | A question about their salary, notice, or references |
| A workflow has a gap | A role they have not assessed |
| A source turned out not to work | Anything they said about their employer or colleagues |
| A rule that has failed once and needs a structural fix | Anything with a name, a number, or a date attached to them |

**The test: could this be read by a stranger who does not know the user?** If not, it goes in the relevant
wiki page's *Open questions* section instead.

**Write findings generically.** *"A user obtained an Adzuna key and discovered Ireland is not covered"* is
a system finding. *"Sacha's key does not work"* is the same fact with a person attached to it, and it does
not belong in a public repository.

**Personal follow-ups are not less important — they are differently located.** Losing them is a real risk,
which is why every wiki page carries an *Open questions* section for exactly this purpose.

---

## 🟢 Picking this up cold? Read this first

**Twenty-five items is not a plan.** Three things about their state, then an order.

### 1. Nine of these are already fixed as *documented behaviour*, not as code

**Ported into `CLAUDE.md`, `templates/` and the skills on 2026-08-24.** The entry stays because the
reasoning is worth keeping — **but do not re-implement them:**

| Now a documented rule | Where |
|---|---|
| Fetch the employer's own posting, never the aggregator's | `build-application` Step 1 |
| Score the journey, not the address; a transit stop is not a commute | `templates/Role Scoring Framework.md` |
| Standing-gaps list; *not recorded* ≠ *recorded as absent* | `CLAUDE.md` |
| Three scores instead of one total; the requirement count | `templates/Role Scoring Framework.md` |
| Do not answer a tie by lengthening the ruler | same |
| Score against the user's baseline, not the field | same, plus `career-init` |
| The internal move as a third option | `CLAUDE.md` |
| "Remote" is country-scoped | `role-radar` |
| The why-X answers and values-with-three-examples | `build-application` Step 0.4 |

🔴 **A rule is not a control.** Several of these are the same class of thing as *"never wrap inside
`[[ ]]`"*, which failed three times in one session before it became a check. **Where a rule can be made
mechanical, that is still work outstanding** — it just is not *starting* work.

### 2. Do the cold-start run before building anything else

**It is the last item in this file and it should be the first thing done.** Half of what follows is
speculative — *designed, not built* — and a real run from a clean clone will re-rank it and add items that
are not here.

🔴 **And whoever wrote this system is the worst possible person to run that test.** They know every answer,
will fill gaps unconsciously, and will read ambiguous instructions correctly because they wrote them.
**Use a CV that is not theirs, answer only what is asked, and keep a note of every point where they had to
help it. That note is the real backlog.**

### 🔴 Audited 2026-08-24 before handover. Two entries were stale; both corrected

**Worth knowing that this was checked, and worth knowing what it found**, because a backlog that has
drifted is worse than a long one — it sends work at problems that no longer exist and leaves real ones
looking handled.

| Entry | Was | Actually |
|---|---|---|
| **The radar's SIGNAL number** | *"Done: the column is now `SIGNAL`"* | 🔴 **Never true of this repository.** That rename happened in a private copy. `radar.py` still writes `\| Score \|` — **the exact word that caused the confusion.** Corrected — and 🟢 **actually done 2026-08-25**, as `HIGH`/`MED`/`LOW` rather than as a second integer |
| **Employer research** | *"designed, not built"* | 🟢 **Built** as `build-application` Step 0.4. Retitled, with the two details that genuinely did not make it |

**Nothing else claims to be done that is not.** The nine rules listed above are documented rather than
mechanical, and say so.

🟢 **Two of those nine stopped being merely documented on 2026-08-25.** *"'Remote' is country-scoped"* and
the rest are still instructions; but the SIGNAL vocabulary and the search window are now code with tests
behind them. **The distinction this table exists to police is the one to keep applying: a rule is not a
control.**

### 3. Then, in this order

🟢 **The first two items on this list were done on 2026-08-25** — the seven-day window is now
`--all-open`, and the radar's number is now `HIGH`/`MED`/`LOW`. Both entries are marked ✅ below and kept
for the reasoning. **What follows is what is next.**

| | Why first |
|---|---|
| **The employer watchlist as data** | Preference and exclusion lists exist as a design. They are what turn *"watch these employers"* into something the radar does — **and the Workday adapter now needs a list of employers to point at**, which is the user's to give |
| 🟡 **Run the Workday adapter against a live tenant** | ✅ Built 2026-08-25 against verified endpoints and recorded responses, **but never yet run against a real employer from this repository.** Until it is, treat its field mapping as unproven |
| **The Oracle Cloud CX adapter** | The remaining large ATS written up in the aggregator entry. Same argument as Workday, one endpoint, `GET` rather than `POST` |
| **Everything after the submit button** | The system stops at submission and the process does not |

🟢 **Leave the rest until the cold run says which of them matter.**

---

## 🔴 Defects — things that behave wrongly

### ✅ The radar's SIGNAL number read like a framework score — MADE NON-NUMERIC

**Status: ✅ fixed 2026-08-25, with tests. The record of why follows, because the lesson generalises.**

`radar.py` produced an unbounded keyword tally. The Role Scoring Framework produces a score out of 15.
**Both were called "score", and a radar output of 21 was reported to the user as though it were a
framework score of 21 — which is impossible, and the user rightly caught it.**

**The first two attempts at this were both instructions**, and both failed: a warning line in every
shortlist header, then the same warning in the module docstring and the skill. **The confusion recurred
anyway**, which is the whole argument for the third attempt being structural.

**Now:** the column is `SIGNAL` and the value is `HIGH` / `MED` / `LOW`. 🟢 **A word cannot be mistaken for
a score out of 15 even by accident** — there is no reading of `HIGH` that produces a number. The raw tally
survives in `raw.json` for tuning and reaches nothing a human reads. Section headings, the stderr summary
and the skill all moved to the same vocabulary, because half a rename leaves two names for one thing.

🟢 **The per-row `SIGNAL` deliberately repeats its section heading.** Rows get lifted out of the shortlist
and pasted elsewhere, and a row separated from its heading has to carry its own label.

🔴 **A second reason the number was wrong, found afterwards while building a before-and-after fixture, and
worth more than the original one.** Two roles printed an identical `23`. They were not the same 23: one was
20 keyword points plus the **+3 the tally adds for a salary appearing in the title**, the other was 23
keyword points and no salary. **The number asserted the two roles were equal, which the tally cannot
support** — and it asserted it in a format that invites arithmetic nobody should be doing on a keyword
count. **`HIGH` and `HIGH` make the weaker, true claim: both are worth reading first.**

🟢 **That generalises past this repo.** A displayed value that sums a signal with a bonus implies a
precision it does not have, and **the display format is what decides whether anyone notices.** A word
cannot be averaged, differenced, or ranked to two significant figures.

**Checked at the same time, and clean:** `verify.py` and `cv_lint.py` print `N finding(s)`, which reads as
a count of problems rather than a rating. `verify.py` has an internal `score` used to rank coverage
suggestions; it is a sort key and is never printed.

🟢 **The generalisable rule: when a number and a different number share a name, renaming the column is the
smaller half of the fix.** Making one of them non-numeric is what ends it.

### 🟡 The salary bonus in the radar tally measures the adapter, not the role

**Status: found 2026-08-25 while building a before-and-after fixture for the SIGNAL change. Not fixed.**

The tally adds **+3 when a salary is visible** — either supplied by the feed or matched in the title.
Two problems, and the second is the one that makes it a defect rather than a design choice.

1. **It is a different dimension inside the same number.** Everything else in the tally measures whether
   the role's *content* matches. *"This posting disclosed a salary"* measures how actionable it is. Both
   are legitimate; adding them means neither can be read off the result.
2. 🔴 **It is source-dependent, so it scores the adapter.** Aggregator adapters return a structured salary
   field; employer-board and scraped adapters almost never do, and fall back to matching a figure in the
   title. **The same role fetched from two sources gets two different tallies** — one of them three points
   higher for a reason that has nothing to do with the role.

**Bounded but not harmless.** `HIGH`/`MED`/`LOW` absorbs small movements, but +3 is a third of the distance
between the two cut-points, so it can promote a role across a band on the strength of which adapter found
it first.

**Options, in rough order of preference:**

- **Carry salary-visible as a separate column**, not as points. The shortlist already has a `Pay` column
  doing exactly this, which makes the +3 largely redundant to a reader.
- **Normalise it at the adapter boundary** so every source reports salary-visible the same way, and the
  bonus at least stops depending on the route.
- **Drop it.** The framework scores PAY properly and treats an unpublished band as `TBC`; the radar does
  not need an opinion.

🟢 **The general shape is worth keeping in mind for any scoring tool here: a term that only some inputs can
earn is a measurement of the input pipeline.**

### ✅ Line-wrapped wikilinks silently do not resolve — CHECK BUILT

**Status: ✅ built 2026-08-24 as [`tools/wikilinks.py`](tools/wikilinks.py), wired into `/career-lint`,
with 20 tests. What follows is the record of why.****

**A wikilink broken across two lines is not a link.** Obsidian's parser does not match `[[ ]]` across a
newline, so `[[Some Page\nName]]` renders as literal text and resolves to nothing.

**In one vault this had broken 83 links across 26 files** — including the most-linked pages in the whole
knowledge base. It was introduced by a wrapping convention (keep prose under ~100 characters) applied
mechanically to lines that happened to contain a link.

🔴 **The reason it matters more than it sounds: it is invisible.** The prose still reads correctly. Nothing
errors. It shows only in graph view, or on hover, or when a link that should exist does not. **It was found
by accident while checking two new pages, not by looking for it** — which means the failure mode is
silence, and silence is exactly what a knowledge base cannot afford.

**Rule:** never wrap inside `[[ ]]`. Break the line before the link or after it, and let the line run long.

🔴 **A third variant, found the same day and worse: links to a heading that has since been renamed.** Those
do not look broken at all — **the page still opens, the reader just silently lands at the top** instead of
the section being cited. **40 were found in one vault. 31 were repairable mechanically** (most had only
gained a date suffix), **5 pointed at a section lost in an earlier rewrite**, and **7 were self-inflicted by
the un-wrapping fix above**, which pulled blockquote `>` markers into the link text. **A repair pass needs
its own verification pass.**

🔴 **And the rule failed three times in one session** — 83 links in the first sweep, 7 in the repair, 2
while writing the fix up. **An instruction that depends on remembering it mid-sentence is not a control.**
**Build the check.**

**To do:**
- Add a wikilink check to the deterministic layer: **flag every `[[ ]]` containing a newline, and every
  link whose target file does not exist.** Both are one regex and neither needs a model.
- The link-target check must ignore deliverables (`.pdf`, `.docx`) and paths outside the wiki, or it
  produces noise that gets ignored — which is how a check dies.

---

### 🟢 A total that does not move can still be a total that lied

**Status: not a defect in the code. A defect in how results get reported. 2026-08-24.**

An employer research pass produced a score of **15 before and 15 after** — while all four components moved:
NEED 4→5, DELIVER 4→3, EDGE 4→5, WANT 3→2.

🔴 **The naive report is "research complete, no change", and it is worse than useless** — it says the
research was not worth running, when in fact it rebuilt the entire basis of the decision.

**The framework already has a rule for this** (*read the row, not the sum*), and the rule was not enough,
because the reporting habit is to lead with the number.

**To do:** when re-scoring after research, **diff the components and lead with the diff**, not the total.
If any component moved by 2 or more, say so in the first line even when the total is unchanged.

### 🔴 Aggregator postings are truncated, and the system reads them as if they were the job

**Status: found 2026-08-24. This one changed a real score and should be fixed before the next pack.**

A role had been assessed from a LinkedIn posting and carried a red-flagged capability gap for three days.
Reading **the employer's own careers page** for the same requisition dissolved it:

| The aggregator carried | The employer actually wrote |
|---|---|
| *"Proficiency in SQL, Python, Power BI, Power Automate, Power Apps, Azure, Microsoft Fabric"* | *"Proficiency in **at least one**..."* — of **eleven** tools |
| *"Consulting or professional services experience preferred"* | *"...**or internal product delivery, or regulated, data-intensive environments**"* |
| *(absent)* | The **business driver** for the role — the single strongest match in the whole posting |
| A posting date | **Three weeks later than the real one** |

🔴 **The failure is asymmetric and that is what makes it dangerous.** Truncation removes qualifiers
(*"at least one"*), alternatives (*"or..."*), and context — all of which tend to be the parts that make a
candidate *more* eligible. **A system reading aggregators systematically under-scores its user**, and does
so invisibly, because the truncated text is perfectly coherent.

**Fix, in order of value:**

1. **Make "fetch the employer's own posting" a required step before assessment**, not before packaging.
   By packaging time the score has already been used to decide.
2. **Prefer the ATS JSON endpoint over the rendered page.** Every major ATS exposes one and the JSON
   carries fields the page does not — real posting date, requisition number, secondary locations, study
   level, requisition type:
   - **Oracle Cloud CX**: `GET /hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&finder=ById;Id="<jobId>",siteNumber="CX_1"` — the `jobId` is in the careers URL. Quotes around the values are required; without them it 400s.
   - **Workday CXS**: `POST /wday/cxs/<tenant>/<site>/jobs`
   - **Greenhouse**: `/v1/boards/<token>/jobs?content=true`
   - **Lever**: `/v0/postings/<company>?mode=json`
3. **Capture the requisition number at ingest.** It is usually only on the employer's site, and any
   sensible output-filename convention needs it.
4. 🔴 **Trust the employer's posting date over the aggregator's.** Aggregators re-date reposts, which makes
   an ageing requisition look fresh. A six-week-old senior role may already be at offer stage — **that is a
   prioritisation input, and the system currently cannot see it.**

---

### ✅ The verifier conflated a percentage with a count — FIXED

**Status: ✅ fixed 2026-08-24, with a test. Found by building a real application pack.**

`norm()` stripped the unit before comparing, so **`100%` and `100` became the same key.** A CV saying
*"over 100 staff consume the output"* under one employer was flagged against *"100% of emergency fixes
within SLA"* recorded under a different one — **a confident, specific, wrong ATTRIBUTION finding on a
correct document.**

🔴 **This is the failure mode that matters most in a deterministic layer.** A missed error is bad; **a
false positive is worse, because a check that cries wolf gets switched off**, and the attribution check is
the one that catches a real achievement attached to the wrong job.

**Fixed by keeping the unit in the key** — `100%`, `3x` and `100` are three different claims. **The same
percentage written two ways still matches.** Two tests added: one that a percentage and a count no longer
collide, one that the intended equivalences still do.

🟡 **A related gap, not fixed.** The figure regex matches `30%` but not `30 per cent`, so a claim spelled
out in words is invisible to the check. **Silent, and the writing standard actively prefers words in some
positions.**

---

### 🔴 A nearby transit stop is not a commute

**Status: found 2026-08-24, after the system made this exact error and the user corrected it.**

An employer research pass found the office was a four-minute walk from a light-rail stop, concluded that a
previous "this is a drive" note had been wrong, and **raised the score.** The user corrected it: from where
he lives, that journey is **two hours each way across three legs.** It is a drive.

🔴 **The system had reasoned from a map rather than from a journey.** Distance from the office to a station
is trivially checkable and almost irrelevant. **What matters is the number of legs and the total door-to-
door time from one specific home address** — and a metro or tram network is intra-city, so for anyone
commuting *into* a city it usually adds a leg rather than removing one.

**Fix:**

- **Location scoring needs the user's origin, not just the office's postcode.** Store it once.
- **Score the journey, not the address**: legs, total time, and whether the time is usable (a train where
  you can work) or lost (driving).
- 🔴 **Never raise a location score on the existence of a transit stop without a door-to-door time.** Mark
  it `TBC` and ask.
- 🟢 **Employment clusters are worth storing as first-class entities.** One postcode in this case held four
  major employers, so the finding was not about one job — it was a standing filter that will apply to
  dozens. **A "known locations" table, scored once and reused, beats re-deriving it per role and getting
  it wrong differently each time.**

### ✅ "Not recorded" and "recorded as absent" are indistinguishable to a search — TOOL BUILT

**Status: ✅ [`tools/known.py`](tools/known.py) built 2026-08-24, with 11 tests and a hard rule in
`CLAUDE.md`. It recurred three times in one session before it was built, which is the argument for it.**

**What it does:** finds every mention of a term and sorts them into settled decisions, negatives and plain
assertions, then returns **SETTLED / PRESENT / NEGATIVE ONLY / NOT FOUND** — and prints the lines it judged
on, because a verdict trusted without being read adds confidence to the same mistake.

🟢 **The question it answers is not *"is this true"*, which needs judgement. It is *"should I ask the user
about this"*, which is decidable — and which is the one that was got wrong.**

**Validated against the three real failures:** the budget question returns SETTLED with *"stop asking"* as
the first line of evidence; the work pattern returns PRESENT; a genuinely unknown term returns NOT FOUND.

**The original write-up follows, because the reasoning is what generalises.**

### The defect it was built for

**Status: found 2026-08-24, after the system asked the user a question its own knowledge base had already
closed with the words "stop asking."**

A role's requirements named a capability. The system searched the knowledge base for evidence of it, found
none, marked it **"unknown rather than absent"**, and put the question to the user.

🔴 **The knowledge base had resolved it three days earlier, in two separate places, as a confirmed
absence** — with an explicit instruction not to raise it again.

**The mechanism is general and will recur in any wiki-backed system.** Searching for *evidence of X* and
finding nothing returns the same empty result whether X was never investigated or X was investigated and
found not to hold. **They mean opposite things**: one is a question, the other is an input.

🔴 **The cost is not just a wasted question.** A confirmed absence is a *scored fact* — it should lower a
capability score at assessment time. Treating it as unknown leaves the score optimistic and defers the
correction to whenever someone happens to ask.

**Fix:**

1. **Maintain an explicit standing-gaps list**: capability, status (confirmed absent / unknown / present),
   the date it was resolved, where it has been demanded, and **the substitute claim if one exists**.
   Cheap to maintain, and it is the only structure that makes "confirmed absent" searchable.
2. **Before asking the user anything, search for the resolution, not the evidence.** Terms like *"stop
   asking"*, *"resolved"*, *"confirmed"*, *"none"*, *"does not"* — the answer is usually phrased as a
   negation, which is exactly what an evidence search misses.
3. 🔴 **Never surface a question the knowledge base has marked closed.** If a page says stop asking, that is
   a hard instruction, and re-asking costs credibility that the whole system depends on.
4. 🟢 **Count how many times each gap has been demanded across postings.** Two is a coincidence, three is a
   decision to put to the user — *is this worth going and acquiring?* — asked **once**, rather than
   conceded repeatedly in cover letters.

---

### 🟡 Near-miss facts need an explicit "does not apply" note

**Status: found 2026-08-24. Related to the above but a distinct failure.**

The user was asked whether he had ever commercialised internal tooling. He said no — **and the knowledge
base contains a page about six years spent selling custom software to enterprise clients.**

🔴 **On a keyword search that page looks like a direct contradiction.** It is not: that software was built
to sell from the outset, and the requirement was about productising something built for internal use.
**Adjacent, and different.**

🔴 **Left unmarked, a future pass will "discover" that page and either re-ask the question or, worse, write
the stretched claim into an application** — where it dies at the first follow-up question.

**Fix:** when a user's answer conflicts on its face with existing content, **write the distinction onto the
near-miss page itself**, not only onto the page where the question arose. The correction has to live where
the next search will land.

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

### 🔴 "Remote" is country-scoped almost everywhere, and reading it as location-free widens the search wrongly

**Status: found 2026-08-24 against a real employer board.**

An employer advertising 354 roles listed **11 as remote — and every one was bounded to a country or a US
state**: *Remote - UK*, *Remote - Luxembourg*, *Remote - Texas*, *Remote - Arizona*, *Remote, Australia*.
**None was globally open, and there was no remote posting for the user's own country.**

🔴 **The failure this invites is expensive rather than merely wrong.** A user asking *"does remote mean I
can stop limiting myself to my own country?"* gets a yes, the search geography widens, and **a batch of
roles gets assessed that were never open to them.** Right-to-work, tax residency and payroll entity all sit
behind that word and none of them appear in the listing.

**Fix:**

- **Parse the location string, do not just match on "remote".** *Remote - X* means *X*, and the suffix is
  the whole meaning.
- **Treat an unqualified "Remote" as `TBC`, not as global.** It usually means "remote within the country
  the requisition is raised in".
- 🔴 **Never widen the search geography on the strength of the word alone.** Confirm against the
  requisition's country, and flag right-to-work as an open question rather than assuming it.

### 🔴 Example and template files are a leak vector, because they get made by copying a real one

**Status: happened 2026-08-24. Caught, remediated by history rewrite, and worth a permanent rule.**

`config.example.json` shipped with **one user's actual commuting geography — home county included — their
real target job titles, and their geographic exclusions.** In a public repository, under their own name,
alongside a README explaining the repo runs a job search.

🔴 **Nobody wrote that file. It was a working config with `.example` in the name**, which is how almost
every example file in every project gets made.

**Three failures stacked, and the middle one is the serious one:**

1. **The file was force-added to fix a broken clone — without being read.** *"It's just an example config"*
   is precisely the assumption that makes this class of leak work.
2. 🔴 **The pre-commit hook blocked it, correctly, saying it looked like personal material — and the rule
   was carved out rather than the file being opened.** **The control fired and was overridden.** A
   safety check that gets exempted whenever it is inconvenient is decoration.
3. **`.gitignore` had been hiding the problem, not solving it.** The pattern `tools/radar/*.json` matched
   the example too, so it was never committed — and therefore never reviewed, while sitting in the author's
   working tree looking like part of the repo.

**Rules that follow:**

- 🔴 **Never commit a file you have not read.** Especially one being added to fix something else.
- 🔴 **When a safety hook objects, read the file before deciding it is a false positive.** If an exemption
  is genuinely right, it should be justified by the file's contents, not by the inconvenience.
- 🟢 **Write example files as explicit placeholders, not as sanitised real ones.** `"<your city>"` cannot
  leak, and it documents the field better than a plausible value does — a reader cannot tell whether
  `"dublin"` is a default or an example.
- 🟡 **Audit every `*.example.*`, `*.sample.*` and `templates/` file in a repo that is about to go public**,
  and check them against the same rules as the ignore list. **They are the files most likely to have been
  derived from something real.**
- 🔴 **Add `tools/tests/` to that list.** Fixtures are example files under another name and were missed by
  this entry for exactly that reason — the audit that eventually ran found a real first name, a real
  city, and two fixtures built from the user's own history. **The naming convention is what made them
  invisible: nothing in a filename ending `_test.py` says "read this before publishing".**

🔴 **And a caveat on the remediation, because it is widely misunderstood.** The bad commit was removed by
rebase and force-push within 25 minutes, with 0 forks and 0 stars — **and the orphaned commit remained
fetchable from the host by its SHA afterwards.** Verified, not assumed. **A history rewrite removes a
commit from the branch, not from the server.** For anything genuinely sensitive — a key, a credential —
**rotate it and ask the host to garbage-collect; do not treat the force-push as the fix.**

---

### ✅ The deterministic layer had no tests — BUILT, and it found three live bugs

**Status: ✅ 2026-08-24. [`tools/tests/`](tools/tests/) — 85 tests, stdlib only, under a second.**

**`verify.py` and `cv_lint.py` are the safety-critical parts of this repo and had zero tests.** They are
pure functions over text, so they are trivially testable, and everything else leans on them.

🔴 **Writing the tests found three defects that were live in the shipped version:**

1. **`cv_lint` reported `0 findings — clean` on empty input** and exited 0. It defaulted to stdin, read
   nothing, and passed. **A checker that says clean when it checked nothing is worse than no checker**, and
   it directly contradicted the README's own line about what a clean run means. Now refuses, with a usage
   message.
2. **It crashed** — `IndexError` on `Counter.most_common` — **on any document with four or more bullets
   that had no words**, which is what a partially-converted PDF looks like.
3. **One word produced two identical findings**, because two spelling patterns matched it.

🟢 **The tests that matter are the ones encoding a bug someone actually hit**, and they say so in their
docstrings: the circular-sourcing guard (a figure "existed in the wiki" because it existed in the CV being
checked), the attribution check announcing loudly when it cannot run rather than passing silently, and the
blockquote-marker case in the wikilink repair.

**Still to do:**

- **No tests for `export_review.py` or the radar adapters.** The adapters hit live third-party endpoints,
  so they need recorded fixtures rather than network calls.
- **Nothing tests the agent hook end to end** — that a write actually triggers the verifier and that a
  failure reaches the agent's context.

---

## 🟡 Gaps — things the system does not do yet

### 🔴 The system models "leave" and "stay" and misses the third option entirely

**Status: raised by the user 2026-08-24. The system had never considered it.**

Every role was being scored against *staying put*, as though those were the only two outcomes. **There is a
third: moving within the current employer** — and on the dimensions this user actually cares about it is
structurally advantaged, before any specific role is compared:

| | External move | Internal move |
|---|---|---|
| **Unvested equity** | Forfeited on resignation | **Retained** |
| **Vesting-date timing** | Governs the whole search timeline | **Dissolves as a constraint** |
| **Notice period** | The binding constraint on every plan | **Does not apply** |
| **Continuous service** | Resets to zero | **Preserved** |
| **Probation, reference risk** | Both real | **Neither** |
| 🔴 **Pay** | The user's stated floor | 🔴 **Will not reach it. Internal moves pay less** |

🔴 **The consequence is a scoring one, not just a missing feature.** An external role in the middle of the
table is not competing against nothing — **it is competing against an option that costs none of the above.**
**Every external score should be read against that baseline**, which means the internal option has to be in
the table rather than in the user's head.

**To do:**

1. **Model "internal move" as a first-class option**, scored like any other, with the retained-value items
   computed rather than described.
2. 🔴 **Fetch the employer's *internal* board, not just its external careers site.** Most large employers
   run a separate internal job site carrying **internal-only requisitions** and a different application
   route. **The external site is a floor, not the picture** — and the agent should say so rather than
   presenting external listings as the employer's full hiring.
3. **Prompt for it.** A user in a stable job will not raise this unprompted; this one did, and the system
   had nothing to say.

---

### 🔴 Scores have no personal baseline, so "good" gets confused with "better than what I have"

**Status: found 2026-08-24 after a top-ranked role was scored wrongly for three days.**

A role offering **two office days a week at a rail-accessible office** was scored **5/5 on lifestyle** and
described as *"the best lifestyle position available anywhere."*

🔴 **The user is contractually fully remote.** Two days a week is a **downgrade**. The score was measuring
*best of the options assessed* and reporting it as *best available* — and the user's own knowledge base had
recorded the remote arrangement months earlier.

🔴 **It was not one bad row. Every lifestyle score in a 41-role table had been set against no reference
point at all.**

**Fix:**

1. **Record the user's current position explicitly as a scored baseline** — work pattern, commute, pay,
   stability, notice — and **put it in the table as a row.** A comparison table without the status quo in
   it cannot show a downgrade.
2. **Anchor each scale to that baseline**: top of the scale means *no worse than today*, not *best of what
   we found*.
3. 🔴 **Distinguish "contractual" from "current practice"** on anything that forms a baseline. A remote
   arrangement in writing is a floor; a custom the employer could reverse is not, **and the difference
   changes what every alternative is worth.**
4. 🟢 **Where the baseline makes a factor near-constant across all options** — this user is unlikely to
   match a contractual remote arrangement anywhere — **that factor belongs outside the total**, per the
   score-splitting entry above. **It is a price, not a differentiator.**

---

### ✅ The oversight layer's independence was a comment in a config file — ENFORCED

**Status: ✅ 2026-08-24, with 9 tests.**

The whole value of the review layer is that the reviewer is **not** the model that wrote the documents: a
model that invented a number while writing will find that number plausible while reviewing. **That
guarantee was expressed as a comment in `config.example.json` and enforced by nothing.** The authoring
vendor's adapter was selectable, and **a self-review would have printed output identical to a real one.**

🔴 **Worse than useless, because it converts an absence into false assurance.** A missing review is
visibly missing. A self-review looks like a passed check.

**Now:** `authored_by` goes in `application.json`; `export_review.py` stamps `AUTHORED-BY.txt` into the
export telling that vendor's model to refuse; `OVERSIGHT.md` makes it the reviewer's first check, before
even the fresh-conversation test; and `review.py` **refuses** rather than warns — with `--same-vendor-anyway`
available and the output stamped **DEGRADED REVIEW -- NOT INDEPENDENT** if it is used.

🟢 **The refusal names the free way round it**: `--dry-run` prints the prompt to paste into any other
vendor's chat interface, which works just as well and costs nothing.

🟡 **An honest limit, now stated in the docs rather than implied.** Different vendor **reduces** correlated
blind spots; it does not eliminate them. **The stronger property is the fresh context** — the reviewer has
not seen the reasoning that produced the document, so it cannot be anchored by an argument it never heard.
**A different vendor with stale context is worth less than the same vendor with none.** Both together is
the design.

---

### 🔴 "Track outcomes" was shipped as an instruction and ignored for six weeks

**Status: rule added 2026-08-24 with a trigger. The instruction alone had already failed.**

`CLAUDE.md` said *"record what happened to every application"* and *"if the user asks why nothing is
landing, you should already have the data to answer."* **Across seven applications and six weeks, one
outcome was recorded.**

🔴 **The reason is structural, not carelessness. Nothing inside the system happens when an employer
replies, or fails to.** Every other operation has a trigger — a document arrives, a role is found, a
document is written. **An outcome arrives in somebody's inbox and the system never hears about it.**

**Two failures, and the second is worse:**

1. **Six of seven applications have no outcome recorded** — which is indistinguishable from *"nothing has
   come back"*, and those mean different things.
2. 🔴 **The one outcome that *was* captured was filed under the wrong prefix**, so a later search for
   outcomes found nothing and concluded none existed. **The record existed and could not be found**, which
   for every practical purpose is the same as not existing. **This is the "not recorded versus recorded as
   absent" defect again, in a third form.**

**Fixed by giving it a trigger:** `/career-lint` now checks for submitted applications with no recorded
outcome and **asks about each by name** — over 7 days, ask; over 21 days, **record `no response`, because
silence is data and a blank field looks unasked rather than unanswered.**

### 🔴 "Rejected" meant both directions at once

**Status: fixed 2026-08-24 by closing the vocabulary.**

A scoring table used **"Rejected"** for both *the employer turned them down* and *they assessed it and
chose not to apply*. **Two rows four days apart carried the same word for opposite facts.**

🔴 **It makes the table unable to answer the single most important question about a search** — how many
applications has an employer turned down? — **and that number is the one that tells you whether the level
is right.**

**Closed set:** `Submitted` · `Rejected by employer` · `Withdrew` · `Declined` · `Closed` · `Vetoed` ·
`Not applied`.

---

### 🟡 Offer the repo link in the cover letter — ask, never assume

**Status: raised by a user 2026-08-24. Not built.**

**A user who has run their search through this asked whether to reference it in the cover letter** — a
one-line pointer at the repository, so a hiring manager can see the process rather than just its output.

🟢 **For a technical or AI-adjacent role it is a strong differentiator.** The hard thing to prove in that
market is having *built and governed* something rather than talked about it, and a public system with a
deterministic verification layer, cross-vendor review and an honest defect log is exactly that.

🔴 **But it must be offered, never added silently, and the reasoning has to travel with the offer:**

| | |
|---|---|
| 🔴 **Never publish the score** | A bare number means nothing to a reader, and *"DELIVER 4/5"* invites *"so what is the missing 1?"* before they have read the CV |
| 🔴 **The framework also scores the employer** | A manager who follows the link and reads how it works will reasonably wonder what *their* company scored on stability. **Some readers find that impressive and some presumptuous, and the applicant cannot control which** |
| 🟢 **The requirement count works as prose** | *"Nine of your twelve outright, two partially, one not at all"* proves they read the posting, gives a concrete number, and **sets up the concession the letter needs anyway.** The concession is what makes it disarming rather than boastful |
| 🟡 **The first reader is usually a recruiter or an ATS** | Links do not get clicked at that stage. **It belongs in the closing line, where it costs nothing if ignored** |
| 🔴 **It advertises that the application is AI-assisted** | For most technical roles that is a positive — **but only if the framing leads with what they built, not with what it produced** |

**To do:**

- **`build-application` should ask once**, at the point the cover letter's closing is written, and record
  the answer so it is not asked again every application.
- **Never for a role where it would read as odd** — the decision is the user's, but the prompt should say
  which way it leans and why.
- 🟢 **The README already carries an *"if you have arrived here from a job application"* section** for the
  reader who follows the link. **Anything that changes what that section claims has to keep it true for
  every user of the repo, not just the author** — it describes the tool, deliberately, and not the
  applicant.

---

### Everything after the submit button

**Deliberate scope decision, recorded in `CLAUDE.md`.** Not covered: interview preparation, offer
evaluation and negotiation, follow-up cadence, rejection debriefs.

**Interview prep is the largest and the wiki is already sitting on everything it needs** — every claim with
a verification status, the role page's pre-mortem which is the interviewer's objection list, the gaps the
cover letter conceded, and the user's own phrasing preserved verbatim. **A STAR bank built from
human-verified claims only would be the single highest-value addition.**

Negotiation is second: the framework already holds the salary floor, the anchors and the priced-vs-hard
veto distinction, so **comparing two offers is a scoring problem it can already do.**

### Job search is LinkedIn-only in practice

The adapter architecture exists and Adzuna, Greenhouse and Lever are written. **Only LinkedIn has been
exercised.** Indeed is confirmed unavailable — `401` on job pages, `403` on search, tested 2026-08-23.
**Adzuna needs a real key and a real run before the adapter can be called working.**

### 🟡 Employer research — BUILT as `build-application` Step 0.4, two details outstanding

🟢 **Delivered 2026-08-24.** Company and division as separate questions, the two triggers, what to cover,
the read-the-transaction and what-is-the-local-office habits, rescoring if the research moves the number,
and both extra sections — the three "why this employer" drafts and the values-with-three-examples. **All of
it is in the skill.**

🔴 **Two things from the design below did not make it and are still worth adding:**

- **`stale_after` on a company page.** Financial results age in months, and a reused company page is
  exactly the artefact that rots invisibly. **Twelve weeks is the sensible default.**
- **A scope rule.** Employer due diligence has a natural size and **padding it produces noise that gets
  skimmed**, which is worse than a shorter page that gets read.

**The original design follows, because the reasoning is what generalises.**

#### The design

**Proven valuable in use 2026-08-24, and it changed a decision.** A user ran deep research on an employer
before applying. It moved the role's score down by a point and surfaced an **acquisition agreed three
weeks earlier** — 1,200 people at 0.12x revenue — that no reading of the job description would have found.

**Nothing in the system currently requires this.** `/build-application` checks the posting is live and
goes straight to writing.

**The design, as it worked in practice:**

- **Two artefacts, because employers recur and divisions differ.** A company page written once and reused
  for every role at that employer, and division-level research per division. **In the case that proved it,
  the group was mid-turnaround with a declining core business while the division doing the hiring grew
  52%.** Judging either by the other would have been wrong, and applicants routinely apply to the same
  company twice.
- **Two triggers**: before building a pack — **it must run while it can still change the decision**, not
  after — and before an interview, refreshing anything stale.
- **Staleness matters here more than elsewhere.** Financial results age in months. A company page wants
  `stale_after` about twelve weeks out.
- **Do not run it below the build threshold.** Research is expensive and the initial assessment has
  already rejected those roles.
- **What to cover**: financial trend, revenue by division, share price direction, whether the core
  business is structurally threatened and the response, what the division actually is and how it performs,
  **acquisitions**, restructuring and headcount, leadership changes, employee reviews on management and
  job security, **the pay signal**, and the local office — size, history, and whether it came via
  acquisition.

🟢 **Two findings worth encoding in whatever gets built, because they generalise:**

**Read the transaction, not the statement.** The CEO said AI was growing the industry; the company then
paid £22.4m for a business with £182m of revenue. **The price said what the commentary would not. Look for
what a company has done with money.**

**Find out what the local office actually is.** It turned out to be a company acquired three years
earlier, which explained its size, its suburban address, and why engineering sat elsewhere. **A question
about an office is often really a question about an acquisition.**

#### The research output should also answer the two questions every process asks

**Added 2026-08-24, proven on a second employer.** The research produces the facts. **Two more sections
turn those facts into things the user can say**, and both are nearly free once the research exists.

**1. "Why do you want to work for X?"** — three drafted answers.

**The constraint is what makes this hard and what makes it worth automating.** The honest reasons are
usually money, security and location, and **none of those can be said out loud.** So the answers have to
be specific, checkable, and true of that employer alone.

> **The test: could this sentence be said about a different company?** If yes, it is flattery, and it is
> what the other forty candidates said. *"I admire your commitment to innovation"* is the failure mode.

**What produced a good one in practice:**

- **Name something specific and non-obvious from the research** — proves the user looked without
  announcing it. *(In the proving case: a platform the local practice built that the global firm then
  adopted. Nobody puts that in a cover letter because nobody finds it.)*
- **Connect it to something the user has actually done**, with a number
- **End on what they want from the employer**, not what they admire about it
- **Concede something true.** It makes the rest credible
- **Draft three, use one** — a second interviewer asks the same question

**2. The employer's published values, with three examples each.**

Most large firms publish values or behaviours, and **in a values-led firm the competency questions come
straight from them.** The wiki already holds the evidence; this maps it.

**Three per value, not one** — the same story cannot be reused across two interviewers, and the third
forces a search of the wiki rather than reaching for the obvious.

🟢 **The design note worth encoding: prefer the awkward examples.** *"I brought in the vendor because my
team did not have the expertise"* beats any success story for a collaboration value, and *"testing is not
my expertise"* beats a testimonial for a respect value. **Values questions reward candour that costs
something**, and a wiki that records limitations honestly has more of that material than a CV ever does.

🔴 **Store them as raw material, not as answers.** In the room they need situation, action and outcome —
the value is what is scored, the story is what is remembered.

**Note on scope**: this looks like interview preparation, which is out of scope. **It is not** — *"why do
you want to work here"* appears in cover letters and application form free-text boxes, so it is needed
before submission. The values examples are the part that also serves an interview later.

#### Open question for the build: what to lift from a general-purpose research skill

**The proving run used Anthropic's `deep-research` skill.** It works, but it is built for open-ended
research and employer due diligence is not open-ended — **the questions are the same every time, and the
scope has a natural edge.** So the answer is probably a dedicated `/research-employer` that **borrows the
depth-and-rigour machinery and drops the breadth machinery.**

**Worth lifting, because each of these produced something the run would otherwise have missed:**

| From `deep-research` | Why it earned its place |
|---|---|
| 🟢 **The Layer 3 "depth dive" discipline** | Layers 1-2 give financials and stop. **Every finding that changed the decision came from Layer 3** — employee reviews, an industry blog relaying insider testimony, the acquisition nobody had connected to the role |
| 🟢 **Its Layer 3 source list** | Explicitly points at negative reviews, forums, job postings and enforcement records. **That is what sent the run to Glassdoor and to a critical industry blog** rather than to more press releases |
| 🟢 **The red-team protocol, especially "steel man the opposition"** | Forced a section arguing the employer is *fine* — audited profit growth, a doubled share price, the role sitting in the growing division. **Without it the output would have been a one-sided bear case that read as authoritative** |
| 🟢 **Confidence calibration** | The most useful single element. One source was detailed, specific and hostile. **Marking it LOW-MEDIUM against HIGH-confidence audited figures is what makes the whole document usable** rather than something to be argued with |
| 🟢 **The absence test** | *"What should be here and is not?"* — surfaced that no Irish redundancy filings and no local pay data could be found, which is itself a finding |
| 🟢 **Fact → insight elevation** | *"They paid £22.4m for £182m of revenue"* is a fact. *"The acquisition price is the disruption evidence"* is the insight, and it is what the reader needs |

**Worth dropping:**

- **The 7x-15x delivery rule.** Employer due diligence has a natural scope. **Padding it produces noise
  that buries the three findings that matter.**
- **Layers 4 and 5 — adjacent opportunities and horizon pointers.** Largely irrelevant here. *(The one
  genuine adjacency is "what else is this employer hiring for", which the scoring table already handles.)*
- **Framework selection.** PESTEL and Porter's are overkill for a single employer. **A fixed checklist
  replaces them, because the questions really are the same every time** — financials, divisions,
  structural threat, acquisitions, restructuring, leadership, reviews, pay signal, local office.
- **Mode detection and clarifying questions.** The brief is always the same shape.

**So the build is: a fixed question set, executed with Layer 3 depth, red-teamed, and confidence-marked.**
Roughly a page of skill instructions rather than a research methodology.

### 🟢 Employer preference and exclusion lists — designed, not built

**A user's idea, 2026-08-24, and it makes two existing features work better rather than adding a third.**

**The system currently evaluates every role on its own merits.** But candidates have standing positions
about employers that no scoring framework captures: **"I will not work for that company because they do
not pay for sick leave"** is not a NEED, DELIVER, EDGE or WANT score — it is a prior, and it should never
have to be re-derived.

**Two lists, and they do different jobs:**

| | What it does |
|---|---|
| 🔴 **Will not work for** | **Filters the radar before scoring.** An excluded employer's roles get dropped with a one-line note rather than assessed. Without it, the *assess-every-role-immediately* rule burns effort on something already decided |
| 🟢 **Would like to work for** | **Becomes the employer-board watchlist.** Greenhouse and Lever adapters watch whole boards, which gives complete and immediate coverage of an employer rather than whatever they syndicate. **That is only worth doing for employers the user actually cares about** |

**The second one is the more valuable half** and it is easy to miss. In the proving case the board
watchlist had been chosen by the agent, essentially arbitrarily. **It should be the user's list.**

#### Design points that need to be in the build

- **Each exclusion needs a reason AND a basis.** *"Their published policy says X"* and *"someone who
  worked there told me X"* are both legitimate reasons to decline an employer and **completely different
  kinds of claim.** The basis decides how durable the exclusion is.
- **Category exclusions matter more than name lists**, because a category catches employers the user has
  never heard of. Gambling, tobacco, arms, payday lending, or a documented employment-practices record.
  **Ask whether the objection is to the company or to the sector** — in the proving case a single bookmaker
  was named and it was genuinely unclear which.
- **Separate hard exclusions from "assessed and declined".** A principled exclusion is permanent; a role
  declined on commute or timing can return. **Recording both, differently, means a re-appearance is
  decided in seconds rather than researched again.**
- **Exclusions go stale.** Companies change ownership, policy and management. Date them.

#### Two refinements from first use, 2026-08-24

**1. "Watch everywhere", not "add to one adapter."** The first draft said a preferred employer joins the
Greenhouse watchlist. **That was too narrow and the user corrected it.** The point is complete coverage of
that employer, and which route achieves it varies: Greenhouse or Lever if they use one, **their own
careers API if not**, a named query as the fallback. **The list says who to watch; the adapter is an
implementation detail.**

🟢 **Worth knowing for the build: Workday careers sites are machine-readable.** Many large employers front
Workday on a custom domain, and the underlying endpoint takes a POST and returns JSON with no key:

```
POST https://<tenant>.wd1.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs
     {"appliedFacets":{},"limit":20,"offset":0,"searchText":"Dublin"}
```

**Verified working against a large financial employer.** Note the `wd1`/`wd5` numbering varies by tenant —
a `422` usually means the wrong shard, not a wrong request.

🔴 **There is a second hosting style and an adapter that assumes the first will silently miss employers:**

```
POST https://wd1.myworkdaysite.com/wday/cxs/<tenant>/<site>/jobs      # shared host
POST https://<tenant>.wd1.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs   # per-tenant subdomain
```

🟢 **Both resolve to the same API shape, so one adapter covers both — provided it takes host, tenant and
site as three separate inputs** rather than deriving the host from the tenant. **Verified against two
different employers, one on each style.**

🟢 **And there is a detail endpoint worth having**: `GET /wday/cxs/<tenant>/<site><externalPath>` returns
the full description, requisition id, posting date and — **the part the listing hides — the additional
locations.** A role advertised as one city is often open in four.

**A Workday adapter would cover a large share of enterprise employers** and is probably the highest-value
adapter still unbuilt.

✅ **Built 2026-08-25 as [`tools/radar/adapters/workday.py`](tools/radar/adapters/workday.py), with 22
tests against recorded response shapes.** Host, tenant and site are three separate config inputs, so both
hosting styles work; a `422` reports itself as a wrong shard rather than a generic failure; pagination
compares what it fetched against the API's own `total`, so `TRUNCATED` is a known gap rather than a
heuristic; and the requisition number is captured at ingest from `bulletFields`.

🟢 **The hidden-locations detail call earns its place, and it is measurable.** A listing saying
*"3 Locations"* is dropped by the location filter; expanded, the same posting keeps the city that saves
it. **Verified as an A/B against `location_ok`, not asserted** — the filter runs before any description is
read, so this is the only point at which the role can be rescued.

🔴 **Two limitations, both stated in the code rather than discovered later:**

- **It has never been run against a live tenant from this repository.** The endpoints were verified
  against two real employers when they were written up above; the field mapping has not been. Every read
  is guarded so an unfamiliar shape yields a thin row rather than a traceback, **but a thin row is a
  silent failure and this should be watched on its first real run.**
- 🟡 **Workday will only say "30+ Days Ago".** A role six months old and one exactly thirty days old
  produce the same string, so the derived date is a **floor**. It is rendered with a trailing `+` and the
  raw text is kept on the row — because a date that looks exact and is not is the aggregator-re-dating
  problem arrived at from the other direction.

🟢 **A contract change came with it, and it is the better design.** `fetch_body` now takes the whole row
rather than an id: a Workday posting is addressed by four values, and packing those into the id field to
fit a narrower signature is how an id stops being an id.

**2. 🔴 Exclusions have to work at division level, not just company level.**

**Found immediately in real use.** A user named a preferred employer *and* a division inside it he would
not work for. **Roughly a third of that employer's local postings turned out to belong to the excluded
division** — so a company-level filter would have surfaced them all, every run, forever.

**So the exclusion list needs entries at both levels**, and the filter has to read the division out of the
job title, since that is usually where it appears (*"Full Stack Engineer, <Division>, Vice President"*).

#### 🔴 The safety rule this needs, and it is not optional

**This list contains factual assertions about named companies, some from word of mouth.** That is entirely
legitimate as a private note and **completely unusable anywhere else.**

**It must never reach a CV, a cover letter, an oversight export, or anything a third party reads.** The
`export_review.py` allowlist already prevents this by construction — the exclusion list is not one of the
four reviewable file kinds — **but the rule should be stated explicitly rather than left to the file
filter.**

**And the agent should never suggest the user repeat it.** If asked why they are not interested in an
employer, the answer is *"it is not the right fit for me"* and nothing further. **Nothing is gained by
explaining, and a repeated second-hand allegation about a named employer is a real risk to the person
repeating it.**

### 🟢 The system treats every employer as a stranger, and often they are not

**Three related gaps, all surfaced in one conversation 2026-08-24.** The scoring framework and the
research step both assume no prior relationship with the employer. **In practice a candidate frequently
has one, and it is worth more than anything research can find.**

#### 1. Record the relationship, and use it

**A field on every employer page**: *worked there* · *works with them now* · *interviewed there before* ·
*knows people there* · *no relationship*.

**Why it changes things:**

- 🟢 **Pay becomes known rather than TBC.** In the proving case the user could state the employer's band
  for the grade he would target, from having worked there. **PAY is currently scored only where a band is
  published — personal knowledge of an employer's bands is a legitimate high-confidence source and the
  framework has no slot for it.**
- 🟢 **Research is partly redundant**, and the parts that remain are different. Culture, management and
  pay structure are already known; what is worth researching is what has changed since.
- 🟢 **It is the strongest possible answer to "why do you want to work here"**, and the honest one.
- 🔴 **A previous rejection is the same data structure.** The proving case included an employer the user
  interviewed with, was offered a job by, and declined over a contract term. **That belongs in the same
  field, not in a separate memory.**

#### 2. 🔴 Check for contractual restrictions on applying — nobody thinks of this

**If the user works for a supplier, consultancy, agency or outsourcer, their employer's contract with a
client may restrict them from being hired by that client.** Non-solicitation and non-hire clauses between
the parties are ordinary in vendor agreements.

**The proving case: a user who is customer-facing to a client every day, considering applying to that
client.** Their prior employment there and existing relationship make it an unusually strong application
— **and none of that matters if a clause blocks it.**

🔴 **This is discovered at offer stage or not at all**, which is the worst possible time. **A one-line
prompt when a target employer is a current client, customer or partner of the user's employer** would
catch it. **The system should flag it and say to read the contract — never assess the clause itself,
which is a solicitor's job.**

#### 3. The advertised location may not be the only option

**Large employers have satellite offices.** A role advertised for the head office may be workable from a
site much closer to the candidate — and **the posting will never say so, because it is advertising the
main location.**

**In the proving case an employer has an office in the user's own town, twenty-five miles from the
advertised location, and none of their postings mention it.**

**The scoring currently reads Lifestyle off the advertised location alone.** It should ask: *does this
employer have a site nearer than the one advertised, and can the role be worked from it?* **Treat the
answer as a question to ask, not an assumption** — but the upside is the difference between a two-hour
round trip and none.

### Source coverage is geography-dependent and nothing says so up front

**Found the hard way 2026-08-23.** A user obtained an Adzuna key, and it turned out **Adzuna does not
cover Ireland** — `404` on the `ie` endpoint while `gb`, `us`, `nl` and `de` all returned results. The
README had claimed *"good UK/Ireland/US coverage"*, which was simply wrong. **Corrected**, and the adapter
now carries the check to run before wiring anything up.

**The general problem remains**: a user picks an adapter, spends time on a key, and discovers the coverage
gap afterwards. **Nothing in the repo states which adapter covers which country.**

Tested for Ireland, and recorded so nobody repeats it:

| Source | Status |
|---|---|
| LinkedIn guest endpoint | 🟢 Works |
| Greenhouse employer boards | 🟢 Works, no key, whole boards with descriptions |
| **Adzuna** | 🔴 **No Ireland coverage** |
| **Indeed** | 🔴 Blocked — `401` on job pages, `403` on search |
| **IrishJobs.ie, Jobs.ie** | 🔴 HTML only, no feed. Same territory as Indeed, not pursued |
| **Careerjet** | 🔴 Connection refused |

**Worth building**: a `sources check` command that probes every configured adapter for the user's country
and reports what actually works, before they invest in any of it.

### ✅ The search only ever covered the last seven days — `--all-open` BUILT

**Status: ✅ fixed 2026-08-25 as `--all-open`, with the cap now reported and 17 tests.
The record of why follows, because the lesson at the end is worth more than the flag.**

**What was built:**

- **`--all-open` passes `days=None` to every adapter**, and the adapter contract now says an adapter with
  a recency parameter must **omit** it rather than substitute a large number — a big `--days` asks the
  source a different question and gets a differently-wrong answer. Documented in `adapters/__init__.py`.
- 🔴 **Truncation is detected and reported.** Every adapter sets `TRUNCATED` on each call: true when it
  exhausted its own page budget *or* a page failed, false only when the source itself ran dry — **which is
  the only thing that proves a result set is complete.** The shortlist and the console both say
  `NOT THE COMPLETE SET` when it fires, and the skill tells the agent not to describe such a run as
  everything that is open.
- **The batch problem is answered by the triage route, not by an exemption.** An `--all-open` run prints
  *"this is a backlog sweep, not a weekly shortlist"* and points at the `role-triage` agent. The
  assess-every-role-immediately rule stands; the batch goes through triage first.
- **Employer-board adapters were never affected** — they return whole boards and ignore `days` — and now
  say so in their own docstrings rather than leaving the next reader to work it out.

**The original write-up follows.**

#### The defect it was built for

**Found 2026-08-24 because a user asked. The most consequential defect found so far.**

Every radar run passed a posted-within filter of seven days. **Roles still open but posted earlier were
never looked at.** Tested on a single query:

| Window | Results | Oldest posting |
|---|---|---|
| **7 days** | 100 (capped) | **17 August** |
| **No filter** | 100 (capped) | **21 May** |

🔴 **What it cost, concretely.** The highest-scoring unapplied role in that user's table had been posted
**fourteen days** before the run. **The radar never saw it — the user found it by hand and sent the link.**
The tool built to find roles was structurally incapable of finding the best one available.

#### The fix is not "drop the filter"

**The endpoint caps every query at roughly 100 results regardless of window**, so no-filter is **not a
superset** of a windowed run. It is a different trade:

| | |
|---|---|
| **Windowed** | Dense recent coverage — 100 results from one week |
| **No filter** | Sparse historical sweep — 100 results across three months |

**Both are needed.** A frequent windowed run for freshness, and a periodic unfiltered sweep for the
standing backlog of still-open roles. **Dedup handles the overlap and already works.**

**The generalisable fixes, all three now built:**

- ✅ **Any adapter with a recency parameter needs the same treatment.** Employer boards return everything
  open by default and are unaffected; a search API with a `posted_within` filter has this bug latent.
- ✅ 🔴 **Where a source caps results, the cap is the real constraint and the tool should say so.** A run
  reporting "100 results" when the true match count is higher is silently truncating. **Detect it — a page
  returning exactly the cap means there is more — and report it rather than presenting a truncated set as
  complete.**
- ✅ **A first unfiltered sweep produces a backlog, not a shortlist.** In the proving case, **51 roles
  above the read-threshold that no previous run could have surfaced.** The
  *assess-every-role-immediately* rule assumes a handful arriving continuously and **does not survive a
  fifty-one item catch-up**. *Resolved in favour of a triage step rather than a batch exemption* — the
  rule is load-bearing and carving an exception into it costs more than routing the batch.

🟡 **One thing the fix cannot do, and it is worth knowing.** The tool can say a query *was* capped; it
cannot say what was behind the cap. **More pages do not help — the cap ignores them.** Narrower queries are
the only way to see past it, which is an odd inversion of the usual advice and is now in the skill.

#### 🟢 The wider lesson, which is worth more than the fix

**This is the second time a search-quality problem turned out not to be about search terms.** Doubling the
query list from 20 to 40 produced **one** additional strong result. **Fixing the time window produced
fifty-one.**

**When coverage feels thin, check the filters before adding queries.** Breadth is the intuitive lever and
it was the wrong one twice.

### Greenhouse yield is low, and the filter is the wrong shape

**Eleven boards produced 756 roles in one country and one role worth reading.** These employers post
everything — sales, support, legal — and the relevance filter is tuned for the LinkedIn corpus.

🟢 **This is not an argument against the source.** LinkedIn shows what an employer chose to syndicate; the
board shows everything, immediately, so a role at a watched employer can no longer be missed.
**Completeness is the point, not hit rate.** But the noise makes the shortlist harder to read, and a
board-specific prefilter would help.

### 🟢 Email alerts as a universal source — designed, not built

**The best idea for source coverage so far, and it comes from a user rather than the design.**

**The problem it solves.** Several boards cannot be read programmatically — Indeed blocks it outright,
IrishJobs and Jobs.ie have no feed, Adzuna does not cover every country. Every one of them will happily
**email a saved-search alert**.

**The design.** A dedicated mail account, saved searches on every board that offers them, and the radar
reading that mailbox over **IMAP** — `imaplib` is in the Python standard library, so there is no
dependency and no connector required. *(Checked 2026-08-23: no email connector is available in the MCP
registry from any provider, which is why IMAP rather than a connector.)*

🟢 **It is not a workaround for one site. It inverts the problem.** *"We cannot scrape X"* becomes
*"anything that will email us is a source"* — Indeed, IrishJobs, Jobs.ie, LinkedIn's own alerts (which
reach further than the guest endpoint's ~40 per query), employer career sites not on Greenhouse, and
recruiter mailshots. **And it works with the sites' cooperation rather than against their terms**, which
makes it strictly better than a scraper rather than merely safer.

**Design decisions to carry into the build:**

- **Triage from the email body, not by following links.** Digests carry title, company, location and
  usually a snippet — enough to filter. Follow through to the posting only for the shortlist. Faster, and
  it keeps the volume of requests to any one site in ordinary-use territory.
- **The user sets the app password themselves.** A job-board API key is a lookup; a mail app password is
  access to a mailbox. Ship a config template with a placeholder.
- **Dedup will do four times the work.** The same role arrives via LinkedIn, Greenhouse and two alerts.
  Title-plus-location should hold, but it is now load-bearing.
- **Start with five or six searches, not fifty.** Same lesson as query breadth: volume is not the
  constraint and it makes the output unreadable.
- **Provider**: any IMAP host. Gmail or Zoho free, Fastmail cleanest. **Avoid Outlook.com** — Microsoft is
  squeezing basic auth toward OAuth-only and it would need rebuilding.

**A dedicated account is part of the design, not an optional nicety**: it holds job alerts and nothing
else, so it carries no personal correspondence and nothing tied to the user's identity.

### No application tracker

Status lives in the scoring table with no dates, no next action, and no follow-up cadence. **A user with
five live applications has no prompt to chase anything**, and "when do I conclude this one is dead" has no
answer.

### Nothing has been run end-to-end from a cold start

`/career-init` on an empty repo has never been exercised. The pieces work individually; the bootstrap is
untested.

---

## 🟢 Rules learned the hard way — already applied, recorded so they are not undone

- **`employer:` belongs only on single-subject pages.** Applying it to discursive pages produced six false
  attributions immediately, because a page discussing four employers claims every figure on it for one.
  Narrow `Achievements - <Employer> <Years>` pages carry the attributable numbers instead.
- **Assess a role the moment it is found**, in the same turn, even an obvious rejection. An unassessed role
  occupies attention, looks like an option, and decays.
- **Read the full requisition title before scoring work pattern.** Employers often state it there
  (*"(Hybrid, IRE)"*) and aggregator listings truncate it. It is worth up to two points of WANT and is TBC
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
  written for `config.example.json` and never carried across. An audit found a real first name in one
  fixture's example address, a real city in another, and two fixtures built from the user's actual
  history — one of them restating incidents `BACKLOG.md` already describes, so the pair could be read
  back together. **Nobody wrote those as personal files; they were written by starting from something
  true**, which is the same mechanism as the `.example` config. 🟢 **Where a fixture must stay realistic
  to be a valid test — a well-written CV, for the cadence checks — rewrite it as invented rather than
  replacing it with placeholder text, and check the measurements it exercises are unchanged.**
- 🟢 **Mutation-test a checker before believing it.** All 22 Workday tests passed first run; deliberately
  breaking the code found one that passed for the wrong reason, because **two code paths set the same
  flag and removing either changed nothing.** Collapsing them to one made the test meaningful and the
  code shorter. **A green suite proves the tests ran, not that they would have caught anything.**
- 🔴 **A source that caps results is reporting the cap, not the match count.** Detect the difference
  between *the source ran dry* and *we hit our own limit*, and say which. Only the first proves a result
  set is complete, and **presenting a capped run as complete is the same silent failure as a filter nobody
  knew was on.**

---

## Deferred — considered and consciously not done

- **Adopting this repo's directory layout in an existing wiki.** Measured on a real vault: it would break
  94 wikilinks and bend two unrelated sections around a career-only schema, for no gain. **Adopt the
  mechanisms, not the format.**
- 🔴 **Driving a browser to search sites that block automated access.** Considered 2026-08-23 for Indeed.
  **Technically possible and declined.** Using a browser changes whether the access is detected, not
  whether the terms permit it. It would also stall on a CAPTCHA within a few pages — which cannot be
  solved — and the account risk lands on the user mid-search. **The email-alert design above solves the
  same problem with the site's own mechanism**, which is why this stays declined rather than parked.
- **Backfilling `verified:` wholesale.** A claim marked verified for convenience is worse than one honestly
  marked unverified. It accumulates as the user confirms things, or not at all.
