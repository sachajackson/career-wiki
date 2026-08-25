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
| ~~"Remote" is country-scoped~~ 🟢 **now a control, 2026-08-25** | `radar.py`, and it was doing the *reverse* |
| The why-X answers and values-with-three-examples | `build-application` Step 0.4 |

🔴 **A rule is not a control.** Several of these are the same class of thing as *"never wrap inside
`[[ ]]`"*, which failed three times in one session before it became a check. **Where a rule can be made
mechanical, that is still work outstanding** — it just is not *starting* work.

🔴 **And one of these nine turned out to be worse than merely undocumented in code.** *"Remote is
country-scoped"* was listed here as handled while `location_ok` was **waiving every location exclusion
whenever the word appeared** — the reverse of the rule. Found 2026-08-25 by reading the code rather than
the list. **Check the rest against their code before trusting this table.**

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

### 🟢 What changed on 2026-08-25 while the dev session was working — read before picking anything up

**A registry and its tooling were built alongside your radar work. Five new files, and two of them change
how `config.json` behaves:**

| File | What it does to you |
|---|---|
| **`tools/radar/ats_registry.json`** | **15 employers, ~13,000 roles**, every entry verified by calling it. Not code — a contributor adds an object |
| **`tools/radar/registry.py`** | 🔴 **`config.json` now supports `"watch": ["Stripe"]`**, expanded into the shapes your adapters already expect. **`load_config()` calls it.** No adapter was changed |
| **`tools/radar/adapters/custom.py`** | A sixth adapter, for employers running their own API. **Registered in `ADAPTERS`.** Driven by a field map in the registry, not by code per employer |
| **`tools/registry_check.py`** | Calls every entry. Wired into `/career-lint` |
| **`tools/add_employer.py`** | Verifies an employer, writes the entry, offers it upstream one file at a time |
| 🔴 **`tools/tests/test_shipped.py`** | **The one most likely to fail on you.** Asserts every file the tools open is *tracked*, every private one is not, **every adapter in `ADAPTERS` has a tracked module**, and every test file is tracked. **Add an adapter and forget to `git add` it and this is what tells you** |

🔴 **Three things that will bite if you do not know them:**

1. **`radar.py`'s `load_config()` gained six lines** — it resolves `watch` and prints a report to stderr
   before the run. **If you are mid-edit in that function, that is the collision.**
2. **`adapters/__init__.py` gained `custom`** in the import line and in `ADAPTERS`.
3. 🔴 **Two of your resolver tests were repointed, not deleted.** They encoded Deel as *"the ATS nothing
   speaks"*, which stopped being true when `custom.py` shipped. **The `NO ADAPTER` branch keeps its
   coverage via a fictional employer** — do not remove the stand-in thinking it is dead weight.
4. 🔴 **`tools/radar/employers.json` (yours) and `tools/radar/ats_registry.json` (the registry) are one
   letter apart and have opposite privacy rules.** Yours must never ship; the registry must always ship.
   **Do not tidy the `.gitignore` carve-outs into a glob and do not rename either to match the other** —
   see [the note below](#-two-files-one-letter-apart-opposite-privacy-rules--know-which-is-which). The
   obvious tidy-up publishes a user's private avoid list.
5. **`python3 tools/radar/registry.py --list`** shows who is in the registry without calling anything.
   `registry_check.py` shows the same names but makes fifteen requests to do it.

🟢 **Three findings from building it that generalise to the adapters you own:**

- 🔴 **Oracle fails open, Workday fails closed.** A wrong Oracle `siteNumber` returns **200 and the
  tenant's whole unfiltered list**; a wrong Workday site 404s with a named error. **That asymmetry decides
  where probing is honest** — `add_employer.py` probes Workday site names and refuses to probe Oracle.
- 🔴 **A first-of-many field is not the field.** Deel carries `location_name` (*"Israel"*, the first of
  thirty) beside `all_locations`. **Mapping the obvious one would have dropped all 66 roles open to
  Ireland and said nothing.**
- 🔴 **`registry_check.py` shipped without retries and cried wolf within the hour** — one employer
  reported `UNREACHABLE!` on a connection reset and answered fine a second later. **Anything that calls a
  live endpoint needs retries before it is allowed to call something dead.**

### 🔴 Two files, one letter apart, opposite privacy rules — know which is which

**`tools/radar/employers.json` and `tools/radar/ats_registry.json` are not variants of each other.**

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
done a day earlier for `config.example.json` — **would have published every user's private avoid list.**
The rule that correctly hides one file is what silently hid the other. **Renaming was the only fix; loosening the pattern was never available.**

**So, for anyone touching that directory:**

- **Do not "tidy" the carve-outs into `*.example.json` or a glob.** The hook's own comment explains why,
  and this is the second file that proves it.
- **Do not rename either file to bring them into line.** They are opposites; the names are load-bearing.
- 🟢 **`tools/tests/test_shipped.py` now fails if a required file stops being tracked, or a private one
  starts.** It is the only check that could have caught this — see below.

### 🟢 On checklists: yes, but only the executable kind — 2026-08-25

**Raised after the above: would a commit checklist have caught it?**

🔴 **There already was one, it was followed, and the bug went straight through it.** `CONTRIBUTING.md`
says *"Before every push: `git status --porcelain` — anything unexpected staged?"* **Status was clean.**
The file was not unexpectedly *present*; it was expectedly *absent*, **and those look identical.**

🔴 **Every instruction-shaped control in this repo has failed at least once.** *"Never wrap inside
`[[ ]]`"* — three times in a day. *"Track outcomes"* — six weeks. *"Stop asking"* — ignored. **Every
executable one has held.** A written checklist is an instruction with more steps.

**And the second half of the question answers itself the same way:** a checklist that must be updated when
functionality changes will not be, because nothing forces it. **A test lives beside the code and fails
when the code moves.**

🟢 **So the answer is a test that asks what a clone would contain, not what this machine has** —
`tools/tests/test_shipped.py`, built 2026-08-25:

- Every file the tools open by name **is tracked**
- 🔴 Every file that must never ship **is not** — `employers.json`, `config.json`, `seen.json`, the radar's
  working files
- Every registered adapter has a tracked module; **every test file is tracked**, because an untracked test
  is a check that only ever runs for its author
- Every shipped `.json` under `tools/radar/` has **both** a `!` line in `.gitignore` **and** a carve-out in
  the pre-commit hook — the two places that have to agree and did not

🟢 **It caught something on its first run: itself.** `test_shipped.py` was not yet tracked. **The check
that exists because of one untracked file found the next one immediately.**

🟡 **Where a written checklist still earns its place: the things no test can reach.** The oversight pass,
reading a document aloud before sending it, deciding whether a concession is honest. **Those are few, and
they should be marked as the exception rather than the mechanism.**

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

### ✅ Templates evolve and vaults do not — `template_drift.py` BUILT

**Status: ✅ 2026-08-25, 11 tests. Found by being asked what is missing to make this a platform rather
than one person's tool, and it is the gap that grows every time a template improves.**

🔴 **`/career-init` copies `templates/` into `wiki/` ONCE and nothing ever revisits it.**
`sync-to-vault.sh` refuses to touch `wiki/` deliberately — that directory is the person, not the tool. So
`CLAUDE.md` and the skills move forward, and the pages they give instructions about do not.

**Demonstrated on the same day it was found.** The framework template gained a standing-gaps table, a
known-locations table, a baseline row, an internal-move row and a seven-value outcome vocabulary — **and
`CLAUDE.md`, which IS synced, was updated to instruct the agent to use all five.** Every vault created
before that morning has an agent looking for tables that are not there. **A vault reconstructed from
yesterday's templates reports all five.**

🔴 **Two of the five were ROWS INSIDE A TABLE THE VAULT ALREADY HAD.** A section-level check walks
straight past that, so seeded rows are compared as well — a row the template ships filled in is content
the page is supposed to carry, distinct from a blank row, which is only a place to write. **Ship the empty
table; ship the row that is not empty.**

🟢 **The tolerance decides whether anyone keeps it switched on.** A vault has its placeholders filled and
its own rows added, and the agent may phrase a heading its own way. Ratio alone was too strict — *"standing
gaps"* against *"standing gaps (capabilities)"* scores 0.67 — so containment counts too. **Verified clean
against a filled-in vault, which is the case that matters more than the detections.**

🔴 **It never writes.** Merging a section into a page holding a real person's history is a judgement —
where it goes, what carries over, whether an existing note belongs under it. **The agent owns wiki pages;
a script editing them would be touching the one thing in this repo it does not own**, and a bad merge
there costs somebody their notes. A test asserts the file is byte-identical after a run.

🟡 **And it says what a clean run does not prove**: that the structure matches, not that a section's
contents are current.

### ✅ Nothing answered "am I set up?" — `doctor.py` BUILT

**Status: ✅ 2026-08-25, 19 tests.** Setup is three config files copied from examples, a `git config`
line, a CV in a folder and up to two API keys. `sources_check.py` answered a third of it, and only about
job sources.

🔴 **The finding it exists for is the placeholder config.** A file copied from its example and never
filled in **looks configured and returns nothing.** `config.example.json` says so in its own first line.
**Demonstrated rather than argued**: with an untouched example config the radar reports *"3 fetched,
HIGH 0, MED 0"* and exits successfully. **A missing file would have been louder than a filled one.**

🟢 **`OPTIONAL` is not `MISSING`** — the distinction this repo has now needed in four separate places.
Most of the setup is optional; reporting an unconfigured thing as a fault sends someone to fix what they
never wanted. Only `MISSING` and `PLACEHOLDER` exit non-zero.

🟡 **It makes no network calls**, so it is instant, works offline, and cannot tell anyone a source
*answers* — it says so and points at `sources_check.py`. **A test asserts the module imports nothing that
could make a request**, because a promise in a docstring that can be checked should be.

🟢 **It also names the free way round the oversight key** — `review.py --dry-run` prints the prompt to
paste into any other vendor's chat window. Without that, a paid second-vendor key reads as a requirement
and most users will simply skip the review.

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

🟢 **Same failure `wikilinks.py` was built for on the wiki side**, where 40 section links in one vault all
still opened the right page and none went where they said. **It took eight days to arrive on the repo
side, and it arrived because somebody asked a question that made me look.**

### 3. Then, in this order

🟢 **The first two items on this list were done on 2026-08-25** — the seven-day window is now
`--all-open`, and the radar's number is now `HIGH`/`MED`/`LOW`. Both entries are marked ✅ below and kept
for the reasoning. **What follows is what is next.**

| | Why first |
|---|---|
| 🔴 **Ask the user for their actual lists** | ✅ The mechanism is built and empty. **`employers.json` is the user's to write and nobody has been asked** — which employers they want watched, which they will not work for, and on what basis |
| **Email alerts as a universal source** | Designed below, not built. Inverts the problem: *"we cannot scrape X"* becomes *"anything that will email us is a source"*, and it works with the sites' cooperation rather than against their terms |
| **Everything after the submit button** | The system stops at submission and the process does not. **Interview prep is the largest piece and the wiki already holds what it needs** |
| 🔴 **Nothing has been run end-to-end from a cold start** | `/career-init` on an empty repo has never been exercised, and the top of this file says it should be the first thing done |

🟢 **Leave the rest until the cold run says which of them matter.**

🔴 **If the work is the user/system boundary — moving user data out of `tools/` — read
[the path inventory](#-read-this-before-moving-the-user-root--the-paths-that-are-load-bearing) FIRST.**
It is near the bottom of this file, beside the entry it supersedes, and it lists every place a path is
pinned and to what. **This pointer exists because a handover naturally sends the next session to these
first two sections, and an inventory 1,300 lines further down is one nobody reaches** — which is the same
shape as everything else on this page: the note existed, and existing is not the same as being found.

---

## 🔴 Audited 2026-08-25: the nine "documented rules" checked against their code

**Prompted by finding that one of the nine — *"Remote is country-scoped"* — was listed as handled while
the code did the reverse. That is a bad enough hit rate to check the rest, and the rest were worse.**

🔴 **All eight remaining rules ARE present where this file says they are.** The claim was not false, which
is what the previous audit checked for. **That is not the same as the rule being in force**, and this pass
asked the second question instead: *is there anything that contradicts it, and does the thing it
prescribes have somewhere to live?*

✅ **All six fixed 2026-08-25, and the audit itself is now a test** —
[`tools/tests/test_templates.py`](tools/tests/test_templates.py), 8 checks, all six mutants caught. **It
parses the outcome vocabulary out of both `CLAUDE.md` and the template and asserts they are the same set**,
so the two copies cannot drift again, and it fails if any prescribed table is removed from the framework
page. **This is the point: the audit found things no rule-reading could, so the audit became mechanical
rather than something someone has to remember to repeat.**

| | Rule | Verdict |
|---|---|---|
| 1 | Fetch the employer's own posting | ✅ **Fixed.** Was 🔴 **contradicted by another skill.** `role-radar` step 2 says *"read the cached description — already in `raw.json`, no refetch needed"*, then step 3 says score from it. For an aggregator row that cache **is** the truncated posting. **The truncation entry below is explicit that the employer's own posting must be fetched *before assessment*, because by packaging time the score has already been used to decide** |
| 2 | Score the journey, not the address | ✅ **Fixed** — a *Known locations* table now exists. Was 🟡 **prescribing two things with nowhere to put them.** *"Store employment clusters once and reuse them"* and scoring from where the user actually lives — **no template has a slot for either**, so both get re-derived per role, which is the failure the rule describes |
| 3 | Standing-gaps list | ✅ **Fixed** — the table is shipped empty. Was 🔴: **`CLAUDE.md` said to keep the table "on the framework page". The framework template has no such table.** A fresh vault starts with the instruction pointing at a section that does not exist — and this is the rule whose entire purpose is that an absence must be *recorded* rather than merely unfound |
| 4 | Three scores, and the requirement count | 🟢 Present and consistent |
| 5 | Do not lengthen the ruler | 🟢 Present and consistent |
| 6 | Score against the baseline | ✅ **Fixed** — the table's first row is the current job. Was 🟡: said *"the first row of the table is the current job"* — **the table has no baseline row and no status value that could describe one** |
| 7 | The internal move as a third option | ✅ **Fixed** — it is the table's second row, with the prompt. Was 🔴: **`CLAUDE.md` said "score it as a row in the table". The word *internal* does not appear in the framework template at all**, and nothing prompts for it — while `CLAUDE.md` itself says a user in a stable job will never raise it unprompted |
| 8 | "Remote" is country-scoped | ✅ Fixed in code 2026-08-25. It had been doing the reverse |
| 9 | Why-X answers, values with three examples | 🟢 Present and consistent |

### ✅ And one contradiction that was not on the list at all — FIXED

**The outcome vocabulary exists twice, and the copy the user sees is the broken one.**

| | Values |
|---|---|
| `CLAUDE.md` | **Submitted · Rejected by employer · Withdrew · Declined · Closed · Vetoed · Not applied** |
| `templates/Role Scoring Framework.md` | *submitted, not applied, closed or vetoed* |

🔴 **The template is missing exactly the three values that were added to fix the ambiguity** — *Rejected by
employer*, *Withdrew*, *Declined* — and merges two that `CLAUDE.md` deliberately separates. **So a fresh
vault's scoring table cannot express "the employer turned me down"**, which `CLAUDE.md` calls the single
most important question about a search and the number that says whether the level is right.

**This is the SIGNAL failure in another place: one concept, two vocabularies, and the authoritative one is
not the one in front of the user.**

✅ **Fixed, and made mechanical.** The template now carries the full closed set, and a test parses both
files and asserts the two sets are identical — **because writing the same list in two places and hoping is
what produced this.**

### 🟢 What this audit teaches about auditing

🔴 **"The rule is written where it says" is the wrong question.** The previous audit asked it, passed
everything, and missed all of the above. **Ask instead: what would contradict this, and does what it
prescribes have somewhere to live?** Six of nine failed that question. Three ways:

- **Contradicted by another file** (1, and the outcome vocabulary)
- **Prescribes a structure that does not exist** (2, 3, 7)
- **Refers to a place that cannot hold it** (6)

🟢 **A rule that tells someone to write something on a page with no section for it is not a rule, it is a
hope.** Where a rule prescribes a table, **ship the empty table**.

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

### ✅ The salary bonus in the radar tally measured the adapter, not the role — REMOVED

**Status: ✅ fixed 2026-08-25 by dropping the bonus, with 4 tests. The record of why follows.**

**The fix was the first of the three options below: the tally now counts what the role is *about* and
nothing else, and the `Pay` column carries the salary — which was always the better answer, because it
shows the reader the actual figure rather than three anonymous points.**

🔴 **Nothing broke when the bonus was removed, and 208 existing tests still passed** — which is exactly
why the defect survived as long as it did. **A term that quietly shifts a score is invisible to a suite
that never asserts the score.** The four tests added pin it: two identical roles, one with a salary,
score identically; and a role sitting just below a cut-point no longer crosses it because its title
mentions money.

🟡 **Option two is still open and is a different job**: normalising salary at the adapter boundary, so
every source reports salary-visible the same way. Worth doing only if something is going to *use* it —
and **not by scraping figures out of descriptions**, where a currency amount is as likely to be a budget,
a contract value or a revenue number as a salary. **A wrong figure in a Pay column is worse than an empty
one**, and this repo's first rule is never to invent a number.

**The original write-up follows.**

#### The defect

**Found 2026-08-25 while building a before-and-after fixture for the SIGNAL change.**

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

### ✅ Aggregator postings are truncated, and the system read them as the job — FIXED AT THE RIGHT MOMENT

**Status: ✅ 2026-08-25.** 🔴 **The fix that mattered was moving it earlier.** `build-application` already
said to fetch the employer's own posting — but by then the score has already been used to decide.
`role-radar` now says it **before scoring**, and says why the truncation is dangerous: it strips
qualifiers and alternatives, **the parts that make a candidate more eligible**, so a system reading
aggregators systematically under-scores its user, invisibly. It also names the sources that need **no**
refetch — Workday, Oracle, Greenhouse, Lever are the employer's own text — because a rule that is wrong
half the time gets dropped entirely. A test pins both halves.

🟢 **The ATS-JSON half is built too**: Workday and Oracle adapters read the employer's own API directly,
returning the real posting date, the requisition number and hidden secondary locations.

**The original write-up follows.**

#### The original entry

**Found 2026-08-24. This one changed a real score.**

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
   - **Oracle Cloud CX**: ✅ **built 2026-08-25 as [`adapters/oracle.py`](tools/radar/adapters/oracle.py)**, verified against three live tenants. Detail: `GET .../recruitingCEJobRequisitionDetails?expand=all&finder=ById;Id="<jobId>",siteNumber="<site>"`. Search: `GET .../recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations&finder=findReqs;siteNumber=<site>,limit=25,offset=N,sortBy=POSTING_DATES_DESC,keyword="..."`. 🟡 **The "quotes are required or it 400s" note was not reproducible** — unquoted worked on every tenant tried, so it is either version-specific or was only ever true of a non-numeric id. Quoting is kept because it costs nothing, but **an instruction nobody can reproduce stops being followed**, so the claim is softened rather than repeated.
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

### ✅ A nearby transit stop is not a commute — KNOWN LOCATIONS TABLE SHIPPED

**Status: ✅ 2026-08-25.** `templates/Role Scoring Framework.md` now ships an empty **Known locations**
table — place, legs from origin, door to door, whether the time is usable, employers there, verdict —
with the rule that **no row goes in without a door-to-door time; mark it `TBC` and ask.** A test fails if
that table leaves the page. **The origin is recorded once**, as the town they commute from rather than an
address.

🟡 **What is still not mechanical**: nothing stops a location score being raised on the existence of a
transit stop. The rule is written; the check would need the journey data the table now has somewhere to
live. **Revisit once a real vault has filled one in.**

**The original write-up follows.**

#### The original entry

**Found 2026-08-24, after the system made this exact error and the user corrected it.**

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

### ✅ "Remote" is country-scoped, and the filter was waiving exclusions on the word — FIXED

**Status: ✅ fixed 2026-08-25 in code, with 11 tests. Until then it was one of the "nine documented
rules" at the top of this file — and it was not only undone by the code, the code did the opposite.**

🔴 **What was actually happening.** `location_ok` skipped the exclusion list entirely whenever the word
*remote* appeared **anywhere in the location or the title**:

| Location | Config | Was | Now |
|---|---|---|---|
| `Remote - <excluded city>` | that city on `bad` | **kept** | dropped |
| `<excluded city>`, title *"Remote Delivery Lead"* | same | **kept** | dropped |
| `Remote` | — | kept, silently as though global | kept, **marked `(scope TBC)`** |

**A role advertised as remote *within* an excluded geography is still in that geography** — and that is
precisely the case the word was supposed to help with.

🟢 **Now**: `parse_location()` splits the string into *is remote* and *scope*, exclusions are judged on the
scope, and an unqualified `Remote` is carried as **unknown rather than global** and shown as `(scope TBC)`
in the shortlist. **Not dropped** — that loses real roles — **and not trusted either.**

🔴 **The lesson is the one at the top of this file, proved again: a rule is not a control.** This rule was
written down, listed as *documented behaviour*, and the code underneath it was doing the reverse the whole
time. **A documented rule with contradicting code is worse than no rule**, because the file says it is
handled.

**The original write-up follows.**

#### The original entry

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

### ✅ Greenhouse yield is low — PREFILTER FIXED, and it was a bug not a tuning problem

**Status: ✅ fixed 2026-08-25 as [`adapters/_titles.py`](tools/radar/adapters/_titles.py), shared by
Greenhouse and Lever, with 6 tests.**

**Eleven boards produced 756 roles in one country and one role worth reading.** The prefilter was
`query.split()[0] in title` — **the FIRST word of the query**, which is almost always the least
informative one:

| Query | Title | Old | New |
|---|---|---|---|
| *head of delivery* | **Delivery Manager** | 🔴 dropped | ✅ kept |
| *head of delivery* | Head of Legal | 🔴 kept | ✅ dropped |
| *delivery manager* | Account Manager | ✅ dropped | ✅ dropped |
| *senior manager* | Senior Accountant | 🔴 kept | ✅ dropped |

**Wrong in both directions at once**, which is why the yield looked like a tuning problem and was not.

🟢 **What discriminates on a board is the domain word, not the seniority word.** Boards are full of
Managers, Leads and Directors; they are not full of *Delivery*. So a query is split into generic role
nouns and distinctive ones and a title must match something distinctive — **falling back to requiring
every word where a query is nothing but role nouns**, since *"senior manager"* has nothing distinctive to
ask for and deserves to be strict.

**The original write-up follows.**

#### The original entry

**Eleven boards produced 756 roles in one country and one role worth reading.** These employers post
everything — sales, support, legal — and the relevance filter is tuned for the LinkedIn corpus.

🟢 **This is not an argument against the source.** LinkedIn shows what an employer chose to syndicate; the
board shows everything, immediately, so a role at a watched employer can no longer be missed.
**Completeness is the point, not hit rate.** But the noise makes the shortlist harder to read, and a
board-specific prefilter would help.

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

### ✅ The system modelled "leave" and "stay" and missed the third option — NOW A ROW IN THE TABLE

**Status: ✅ 2026-08-25.** *An internal move* is the **second row of the scoring table** in
`templates/Role Scoring Framework.md`, carrying what it costs nothing of — forfeited equity, notice, reset
service, probation, reference risk — and 🔴 **that it usually will not reach the pay floor.** The section
says to ask, because a user in a stable job will not raise it unprompted, and to fetch the employer's
**internal** job site rather than only their public careers page. A test fails if the row is removed.

**The original write-up follows.**

#### The original entry

**Raised by the user 2026-08-24. The system had never considered it.**

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

### ✅ Scores had no personal baseline — THE CURRENT JOB IS NOW ROW ONE

**Status: ✅ 2026-08-25.** *Staying put — the current job* is the **first row of the scoring table**, and
the section states that top of each scale means *no worse than this* rather than *best of what we found*.
A test fails if the row is removed. The record-what table beside it already distinguished **contractual
from custom**, which is the part that decides what an alternative is worth.

**The original write-up follows.**

#### The original entry

**Found 2026-08-24 after a top-ranked role was scored wrongly for three days.**

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

### ✅ A shared employer registry — BUILT AND WIRED IN

**Status: complete 2026-08-25.** `ats_registry.json` (15 employers, ~13,000 roles) · `registry.py` (name an
employer, get the endpoint) · `adapters/custom.py` (employers running their own API) · `registry_check.py`
(every entry called, canaries checked) · `add_employer.py` (verify, add, contribute one file).

**What remains is seeding, not building.** Fifteen is a proof, not a starter set — and
`python3 tools/add_employer.py "Name" <careers-url>` makes each one a line.

🟢 **Every entry was verified by calling it**, not copied from a page. **Roughly 13,000 roles now reachable
from one file that previously lived in five places and one person's memory.**

**How it was built, in order:**

- ✅ **A resolver — built 2026-08-25** as `tools/radar/registry.py`, 14 tests. `"watch": ["State Street"]`
  expands into the `host`/`tenant`/`site` shape the Workday adapter wants, **merging with hand-written
  config rather than replacing it**, and 🔴 **printing a line for every watched employer including the ones
  it could not resolve** — an employer dropped for want of an adapter looks exactly like a quiet week.
  **Ambiguity refuses rather than guessing**, and a substring match says what it matched on.
- ✅ **`tools/registry_check.py` — built 2026-08-25**, wired into `/career-lint`, 11 tests. **All five entries pass.**
- **Seed more.** Five is a proof, not a starter set.
- ✅ **An adapter for `custom` — built 2026-08-25**, 18 tests. **All five shipped employers now resolve
  and fetch.** The adapter walks JSON by dotted paths and **the registry says where this employer's fields
  live**, so the next bespoke API needs a map rather than a module.

  🔴 **Building it found the trap that would have made it useless.** Deel carries `location_name` — the
  **first** of thirty countries, *"Israel"* — alongside `all_locations`. **Mapping the obvious-looking
  field would have filtered out all 66 roles open to Ireland for a user eligible for every one of them,
  and said nothing.** Lists are joined rather than truncated, and the registry entry carries a note saying
  why.

  🟡 **One more shape worth knowing: a detail response often unwraps what the list response wrapped.**
  Deel returns `attributes.full_job_description` in the listing and `full_job_description` alone in the
  detail. The adapter tries the leaf before giving up, rather than making the registry carry two paths for
  one field.

**The adapters know how to speak Greenhouse, Lever, Workday and Oracle. What nobody has is the list of
which employer uses which, and under what identifier.** Every user starts from
`"greenhouse": {"boards": []}` and rediscovers the same public facts.

### 🔴 Why this belongs in the repo when nothing else does

**Everything else here is per-user by construction.** The wiki is one person's career. The config is one
person's geography and salary floor. **None of it can be shared and most of it must not be.**

🟢 **An employer's careers endpoint is public, non-personal, and identical for everyone who looks it up.**
That makes it **the only artefact in this project a stranger can contribute to with zero privacy risk** —
and a repo that invites contributions needs somewhere safe for them to land.

### Prior art: adapters are a commodity, the maintained list is the gap

| | |
|---|---|
| **Open source** | `plibither8/jobber` and similar wrap Ashby, Greenhouse, Lever, BambooHR. **Adapter libraries — the same category as `tools/radar/adapters/`, not a registry** |
| **Commercial** | Apify sells *ATS company discovery* actors. **That is the genuinely hard half** — finding which of five hundred employers use Ashby — and it is a paid product |
| **Registries** | Marketing blog posts. *"Companies using Greenhouse include Stripe, GitLab, Figma…"* **Undated, unverified, unmaintained** |

🟡 **Know the boundary: this does not solve discovery.** It records what somebody already found. That is
still worth doing, because right now what somebody found is lost the moment their session ends.

## The schema

**`tools/radar/ats_registry.json`. Data, not code — contributing means adding an object, never touching
Python.**

```json
{
  "version": 1,
  "employers": [
    {
      "employer": "Stripe",
      "ats": "greenhouse",
      "params": { "token": "stripe" },
      "careers_url": "https://stripe.com/jobs",
      "publishes_salary": false,
      "last_verified": "2026-08-25",
      "verified_returned": 214
    },
    {
      "employer": "State Street",
      "ats": "workday",
      "params": {
        "host": "statestreet.wd1.myworkdayjobs.com",
        "tenant": "statestreet",
        "site": "Global"
      },
      "careers_url": "https://careers.statestreet.com/global/en",
      "publishes_salary": false,
      "last_verified": "2026-08-24",
      "verified_returned": 34
    },
    {
      "employer": "Grant Thornton Ireland",
      "ats": "oracle",
      "params": { "host": "ehzq.fa.us2.oraclecloud.com", "site": "CX_1" },
      "careers_url": "https://ehzq.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/GrantThorntonIrelandExperiencedHires",
      "publishes_salary": false,
      "last_verified": "2026-08-24",
      "verified_returned": 1
    },
    {
      "employer": "Deel",
      "ats": "custom",
      "params": {
        "list": "https://www.deel.com/api/deel-ats/jobs/",
        "detail": "https://www.deel.com/api/deel-ats/jobs/{id}/",
        "note": "Ashby underneath -- every row carries ashby_id -- but the public Ashby board returns empty, so this must target deel.com"
      },
      "careers_url": "https://www.deel.com/careers/",
      "publishes_salary": true,
      "last_verified": "2026-08-25",
      "verified_returned": 300
    }
  ]
}
```

**Field notes, each of which exists for a reason:**

| Field | Why |
|---|---|
| `ats` + `params` | **A common core with per-protocol parameters.** Greenhouse needs a token; Workday needs host, tenant and site as three separate values, because [there are two hosting styles](#) and deriving the host from the tenant silently misses employers |
| 🔴 `last_verified` | **Non-negotiable.** An employer changes ATS and the entry returns nothing — **which looks exactly like "no jobs this week"** |
| 🔴 `verified_returned` | **How many roles it returned when last checked.** *Returned 0* and *returned 214* are different health states and a date alone cannot tell them apart. 🔴 **Compare it as an order of magnitude, never for equality** — measured an hour apart, three of five entries had already moved (1347→1351, 7354→7357, 300→299). **A verifier testing equality would cry wolf on every run and be switched off within a week** |
| 🟢 `publishes_salary` | Rare and valuable. Deel publishes a band on every role, which takes PAY out of `TBC` before any call happens |
| 🔴 `careers_url` | **Always the company's own page — `stripe.com/careers/search`, never `boards.greenhouse.io/stripe`.** It is what a person actually pastes, and **it is the recovery key: when an employer switches ATS the endpoint dies and the careers page does not**, so that URL is how the replacement gets found. The ATS address belongs in `params` |

🔴 **Seeded, not comprehensive. Twenty verified entries beat five hundred guessed.** Board tokens are
frequently just the company name, which makes guessing work *often enough to be dangerous* — it produces
an entry that looks verified and is not.

## Where the entries come from: ask at the moment the user cares

🔴 **Do not ask users to go and compile a list. Ask once, about one employer, at the moment they are
already interested in it.**

**The trigger:** a role scores at or above the build threshold, or the user says they like one.

> *"Before I build this — can you find their own careers page and paste me the link? It takes a minute and
> it is worth more than it sounds."*

### 🟢 Explain why, because the reason is real and it changes behaviour

**The employer's own posting is materially better than the aggregator's copy, and this has been measured
twice:**

| | What the aggregator carried | What the employer's own site carried |
|---|---|---|
| **A professional services role** | *"Proficiency in [eight named tools]"* | 🟢 *"Proficiency in **at least one**…"* of eleven. **Two flagged capability gaps dissolved on one line** |
| | *"Consulting experience preferred"* | 🟢 *"…**or internal product delivery, or regulated environments**"* |
| | *(absent)* | 🔴 **The business driver for the role** — the strongest match in the whole posting |
| | Posted "roughly three weeks ago" | 🔴 **Three weeks older than stated** |
| **A remote SaaS role** | No salary | 🔴 **$80,000–$130,000 published — below the user's floor.** The application was never viable and the aggregator could not show it |
| | Posted "yesterday" | 🔴 **Ten weeks old** |

**The pitch to the user is not "help us build a list". It is:**

> **"Aggregators truncate, and they truncate the qualifiers — which is the half that decides whether you
> are eligible. They also re-date reposts, so a ten-week-old requisition looks like it went up yesterday.
> One link and I read the real thing. As a side effect it gets recorded, so nobody using this has to find
> it again."**

🟢 **The user benefit is immediate and personal; the registry entry is a by-product.** That ordering is the
whole design — a request framed as *"contribute to our database"* gets ignored.

## ✅ Contributing it back — BUILT as `tools/add_employer.py`

**2026-08-25, 12 tests.** `python3 tools/add_employer.py "Stripe" https://stripe.com/careers/search`

🟢 **It verifies before the contribution exists**, which is the whole design: read the careers page, work
out which ATS is behind it, **call the endpoint**, and only then write the entry and offer to send it.
**Somebody has to merge these by hand, and a maintainer who has to verify contributions stops merging
them.** A PR that arrives already checked is a thirty-second read.

🔴 **Running it against the registry it was written to extend found a trap in itself.** Its sniffer
reproduced three of five entries exactly — and on Grant Thornton it picked
`sites/GrantThorntonIrelandExperiencedHires` from the careers page. **That is not a `siteNumber`. Oracle
does not recognise it, falls back to the tenant's whole unfiltered list, and the entry verifies
successfully while claiming a filter it is not applying.** Now it prefers a `CX_` number and says so
loudly when it can only find a friendly name.

🟢 **Workday is probed, Oracle is not.** Workday 404s on a wrong site, so trying `Global`, `External`,
`Careers` in turn is honest — **State Street's site was recovered that way.** Oracle returns 200 for
anything, so guessing there would manufacture a wrong entry that looks right. **The asymmetry decides
where probing is allowed.**

### The original design

## Contributing it back: one file, and only one file

🔴 **This is the part that needs care, because the contribution flow runs from a working copy that contains
the user's private wiki.** The pre-commit hook exists for exactly this reason and must not be the only
thing standing between a helpful impulse and a published CV.

**The design, in order of strictness:**

1. 🔴 **Stage exactly one path — `tools/radar/ats_registry.json` — and refuse if anything else is staged.**
   Not "warn": refuse. `git status --porcelain` must show that file and nothing else before the flow
   proceeds.
2. 🔴 **Show the user the exact diff and get a yes**, before anything leaves the machine. It is four lines
   of JSON; there is no excuse for not showing it.
3. **Then, by what the user actually has:**

| Available | Route |
|---|---|
| `gh` CLI, authenticated | `gh repo fork` then `gh pr create` — **the only route that produces a real PR without the user understanding forks** |
| A browser and nothing else | **Open a pre-filled GitHub issue URL** with the JSON in the body. Zero git knowledge, works from a phone |
| Neither, or offline | **Print the JSON block and say where to paste it.** Still a contribution |

4. 🔴 **Never attempt to push to a repository the user does not own.** It fails, and failing at a git remote
   is exactly the moment a non-technical user concludes the whole system is broken.

🟢 **And run the same personal-data check the pre-commit hook runs**, on the file being contributed. An
employer name and a URL cannot leak anything — **but that is an argument for the check being cheap, not for
skipping it.**

## 🔴 Can you actually reach the listings from the careers URL? Four of five, and testing it found a bug

**Asked 2026-08-25, and worth having asked** — the recovery-key claim above was an assertion until it was
tested.

| From `careers_url` alone | |
|---|---|
| **SS&C** | 🟢 **Complete** — `myworkdaysite.com/recruiting/ssctech/SSCTechnologies` is in the page, host, tenant and site together |
| **Grant Thornton** | 🟢 **Complete** — host plus `sites/GrantThorntonIrelandExperiencedHires` |
| **JPMorganChase** | 🟢 **Complete** — host plus `sites/CX_1001` |
| **State Street** | 🟡 **Host only.** The tenant is inferable from the host and the site still has to be probed |
| 🔴 **Deel** | 🔴 **Nothing.** No ATS marker anywhere in the HTML — **the endpoint was only ever visible in network traffic from a live browser** |

🔴 **So the recovery key works for employers who front a third-party ATS and fails for employers who proxy
their own.** That is a real limit and the schema should carry a `discovery` note for the second kind,
recording *how* the endpoint was found so nobody has to rediscover it from a network tab.

### 🔴 And testing it found a wrong entry, because Oracle fails open

**The Grant Thornton entry was seeded as `siteNumber: CX_1` — a 200 response returning 152 jobs. It was
wrong.**

| siteNumber | Returns | Contains their Data & AI role? |
|---|---|---|
| `CX_1` | 152 | 🔴 **No** |
| **`CX_1001`** | **55** | 🟢 **Yes — this is the experienced-hires site** |
| `GrantThorntonIrelandExperiencedHires` | 258 | *(the friendly name is not a valid siteNumber)* |
| 🔴 **`CX_9999`, pure nonsense** | **258** | **Returns 200 and the tenant's whole unfiltered list** |

🔴 **An unrecognised Oracle siteNumber does not error. It returns a plausible number.** So does the detail
endpoint — which is how the wrong value survived being used to fetch a real job successfully.

🟢 **Workday behaves the opposite way**: a wrong site 404s with an explicit `Job_Posting_Site_ID=` message.
**Two platforms, opposite behaviour on a wrong identifier, and only one of them tells you.**

**The rule this produces, and it governs the verifier below:**

> 🔴 **Verify by known-job presence, never by status code or job count.** A check that cannot fail is not a
> check — and both this registry and the ICON/aggregator work have now produced the same lesson from
> different directions.

## ✅ The verifier — BUILT

**`tools/registry_check.py`, 2026-08-25.** Verdicts: `OK`, `EMPTY!`, `COLLAPSED!`, `UNREACHABLE!` are the
tool's own judgement; **`CANARY GONE` and `UNPROVEN` are handed to a human** because the check cannot tell
a wrong endpoint from a filled vacancy.

🔴 **It cried wolf on its first run and that was the most useful thing it did.** The canary check scanned
the first page of results — and a board with **7,357 jobs** does not carry a given requisition in its first
200, so a healthy JPMorganChase entry reported as broken. **Fixed by asking the source for the canary
specifically** rather than scanning. **A false alarm on run one is exactly how a checker earns the
reputation that gets it ignored**, and it has its own test.

**The original design follows.**

### The design

🔴 **A registry without a checker rots into the silent-zero failure the `role-radar` skill already
documents** — every query returns nothing and the run reports a quiet week.

**`tools/registry_check.py`:** hit every entry, record what came back, update `last_verified` and
`verified_returned`, and **fail loudly on any entry that returned zero when it previously returned
something.**

🔴 **And check a known requisition id is present, not just that something came back.** Each entry should
carry one — the `verified_by` field — because on Oracle a wrong site returns 200 and a plausible count.
**Without that check the verifier would have confirmed the wrong Grant Thornton entry every time it ran.** Run it in CI if there is CI, and from `/career-lint` if there is not.

## What already exists, in the wrong shape

🔴 **In one week of real use, five employers' endpoints were found by hand and scattered across five
places** — two on a preferences page, one on a role page, one in a company research note, and **one used
and never recorded at all.**

**That is the registry, already built, in the wrong shape.** It is the strongest argument that it should be
one file.

---

### 🔴 The posting is the evidence for everything, and it is the one input that reliably disappears

**Status: found 2026-08-25 by testing the links, not by reasoning about them.**

**A job posting is the source document behind the score, the requirement tally, the angle the CV takes and
the stories chosen for the interview. It is also the only input in the whole system that is guaranteed to
be deleted**, usually at the exact moment it becomes most useful: when the employer has finished hiring
and is about to interview.

🔴 **Tested against four assessed roles in a real vault:**

| | |
|---|---|
| A role scored 14 with a full application pack built | **410 Gone.** The requirements it was scored against no longer exist anywhere |
| The role the user was **rejected from** | **401.** There is nothing left to read for a post-mortem |
| Two others | 200, and 429 rate-limited |

**Half were unrecoverable, including the two that mattered most.**

🔴 **And in that vault, one posting had been saved out of fifteen assessed roles** — the one where a pack
happened to be built. **Everything else is a URL and a score with no working behind it.**

**What this breaks, in order of how much it hurts:**

1. 🔴 **Interview prep.** Stories were chosen against named requirements. **Weeks later the requirements
   are gone and the reasoning cannot be reconstructed.**
2. 🔴 **The rejection post-mortem.** *"Why did this one fail?"* is unanswerable without the thing that was
   applied to — and a rejection with a reason is the most valuable outcome there is.
3. **Re-scoring.** When the framework changes — and it has, twice in a week — **old rows cannot be
   re-scored because the evidence is gone.** They quietly become unreviewable.
4. **The requirement tally.** *"Nine of twelve"* is uncheckable once the twelve are unreadable.

✅ **Automated on the radar path 2026-08-25** — `radar.archive()`, 10 tests. **Everything shortlisted is
written to `wiki/postings/<Employer> - <Title>.txt` before `seen.json` is updated and `raw.json` is
overwritten**, carrying the posting date, location, pay and source URL alongside the text. **Shortlisted
rather than everything fetched**, because the shortlist is by definition what an agent reads and the
standing rule is that everything read gets assessed — archiving all 130-odd fetched descriptions would keep
mostly roles nobody looked at.

🔴 **It never overwrites.** An archived posting is evidence of what was read *at the time*, and a later
fetch of the same URL returns either an edited posting or a 404 page — **which would replace the evidence
with nothing.**

🟡 **Still manual on the other two routes**: a link the user pastes, and a role assessed from an employer's
own site. The rule is in `CLAUDE.md` and both skills; nothing enforces it.

**The original design follows.**

**The fix is small and belongs at ingest, not at pack time:**

- **Save the employer's own posting text** — not the aggregator's copy, which is
  [truncated anyway](#-aggregator-postings-are-truncated-and-the-system-read-them-as-the-job--fixed-at-the-right-moment)
  — **the moment a role is assessed**, with the fetch date.
- **Beside the role page, not in an application folder.** An application folder only exists for roles that
  reach a pack; **most assessed roles never do, and those are the ones that vanish silently.**
- **Record the requisition number and the real posting date with it**, since those are what let anyone find
  the thing again on the employer's site if it is still there.

🟡 **It is somebody else's text.** A private copy kept as the evidence behind a personal decision is
ordinary practice; **publishing it is not.** `wiki/` is gitignored, which already handles it — but a system
that starts archiving postings should say so out loud rather than leave it implicit.

---

### ✅ The personal-data heuristic fired on this repo's own subject matter — SCOPED

**Status: ✅ fixed 2026-08-25 by scoping the content scan out of the three system directories, with a test
that fails if that exemption grows. The record of why follows.**

**The pre-commit hook blocked a skill file** on a line of generic advice telling a user **not** to disclose
what they are currently paid. **No number, no person, no employer** — guidance in a system file.

🟢 **The rule itself is well built.** It matches four specific phrases rather than bare words, which is why
it has produced only one false positive in a repo that discusses pay constantly.

🔴 **But this repo's whole subject is job applications**, so guidance about pay disclosure keeps being
written — **and to a regex, advice telling someone not to state a figure is indistinguishable from someone
stating one.** The negation is invisible.

🔴 **And then it happened again immediately, on this entry.** Writing up the false positive meant quoting
the phrase that caused it, which tripped the same rule a second time. **The hook already anticipates
exactly this** — its own comment says *"this file, and the docs describing it, necessarily contain the
patterns they look for"*, which is why the hook, `CONTRIBUTING.md` and `PRIVACY.md` are skipped.

**Both were fixed by rewording rather than overriding.** The skill line reads better for it; this entry
describes the pattern instead of reproducing it. 🟢 **That is the right first response** — and **it does
not scale.** The next person hits the wall, reaches for `--no-verify`, and **routine overriding is how a
good check stops being one.**

**Three options, none obviously right:**

| | |
|---|---|
| **Leave it** | One reword every few months. **Cheapest, and it depends on whoever hits it reading the flagged line rather than overriding** |
| **Require a figure nearby** | Would miss *"mine is well above market"*, which is genuinely personal and carries no number |
| ✅ **Skip the content heuristic in the system directories** | **Chosen.** `.claude/skills/`, `templates/` and `tools/` are written *about* users, never *by* them. **A user's own material never lands there** — the risk this rule guards is `wiki/` and `sources/`, which are still scanned. **The same reasoning the hook already applies to itself, one step wider** |

🔴 **The exemption is now under test.** `test_shipped.py` asserts the skip list is exactly what it should
be and **fails on any addition**, with the message *"every addition needs a reason written beside it, and a
filename is not one"*. **It caught one on its first run** — the binary-file skip, which is there because
grep cannot read a PDF rather than because PDFs are trusted, and now says so.

🟢 **Verified both directions:** the reworded skill line is accepted, and a deliberately personal line
added to `README.md` is still blocked. **The guard holds everywhere a user actually writes.**

🔴 **Do not widen this by filename.** That was tried once, on `config.example.json`, and the file it waved
through turned out to contain a real person's home county.

---

### ✅ Ghost jobs are 20-33% of listings and nothing here checked — BUILT

**Status: ✅ 2026-08-25 as [`tools/radar/legitimacy.py`](tools/radar/legitimacy.py), 17 tests, wired into
the shortlist and the posting archive. Measured against 240 live postings before shipping.**

🟢 **The design decision held: it never touches a score, and there is no percentage.** A test asserts the
line contains no `%`, no `n/m`, and none of the words *score*, *rating* or *confidence* — because a
percentage is a score by another name and would be averaged, compared and ranked within a week. A mutation
that replaces the concern count with *"87% likely real"* is caught.

🟢 **False-positive rate measured, not assumed**, because a check that cries wolf gets switched off: on
600 live Oracle postings it flags **0%**; on 40 live Workday postings it flags **7%**, and every one of
those is the source refusing to say how old the posting is.

#### 🔴 And measuring it found a defect in our own adapter

**The first version compared every posting's age against a 45-day threshold. It could never have fired on
Workday at all.**

**Workday stops counting at 30 days — and does not always print the `+`.** Verified across two live
tenants: 13 distinct *posted* strings, the highest number **30**, appearing as bare *"Posted 30 Days
Ago"*, nothing above it. So `date_is_floor` was false for a posting that could be a year old, the computed
age was exactly 30, and **the threshold was unreachable on the source where age is hardest to see.**

🟢 **Fixed in `workday.py`: reaching the cap is the signal, not the `+`.** And in the check, a floor is its
own finding — *"age unknown: the source stops at 30 days"* — rather than a number compared against a
threshold.

#### 🔴 The listing censors the date and the detail endpoint does not

**Found in the same run, and it is the strongest evidence for bounding the expensive pass.** One real
posting:

| | |
|---|---|
| What the **listing** said | `Posted 30+ Days Ago` |
| What the **detail endpoint** said | `startDate` 2026-06-08 — **78 days** |

**Same employer, same source, two different answers.** That role only carried the true date because it had
hidden locations, so the adapter fetched its detail for an unrelated reason. **Every other capped posting
kept the censored 30.**

🟢 **So a detail fetch buys the single best ghost-job predictor**, and that is exactly the trade the next
entry is about: cheap pass over everything, expensive pass over what matters.



**`career-ops` runs a posting-legitimacy check as a separate block, and the design decision worth copying
is this one: it *"never affects the score."***

🟢 **A fake posting is not a low-scoring role. It is not a role.** Folding it into a fit number would make
a scam look like a mediocre opportunity, and would let a strong-but-fake posting outrank a real mediocre
one. **Same principle as splitting one total into FIT, LIFE and SEC: things that are not the same question
do not go in the same number.**

**The numbers are not marginal:**

| | |
|---|---|
| Live listings estimated to be ghost jobs | **20–33%**, with one count putting **27% of LinkedIn listings** in that bracket |
| Hiring managers admitting to posting one in the past year | **40%** — and **30%** had one live at the time of asking |
| US postings never filled | **At least 1 in 5** (Greenhouse). BLS: 7.4m openings against 5.2m hires — **roughly one in three never produces a hire** |

🟢 **The signals are already in this system and are not being used as signals:**

- 🔴 **The employer's real posting date, from their own API.** In real use an aggregator showed a
  ten-week-old requisition as *"posted yesterday"*, and another was three weeks out. **Age is the single
  best ghost-job predictor and it is already being fetched.**
- **Whether the requisition is still live on the employer's own site**, rather than only on an aggregator.
  `registry_check.py` already knows how to ask that question about one job — it is what a canary is.
- **Repeated reposting of the same requisition id**, which `seen.json` already records.
- **A posting with no requisition number at all**, on an employer known to use an ATS that issues them.

**Report it as its own line on the role page, never as a score adjustment**, and let the user decide. **A
role can be worth applying to even at 30% odds of being real, and that is their call, not the tool's.**

---

### ✅ Bound the expensive pass to the delta — BUILT, and the premise was wrong

**Status: ✅ 2026-08-25 as [`tools/radar/refresh.py`](tools/radar/refresh.py), 19 tests.**

🔴 **It was already bounded, and nobody had measured it.** This entry said the radar fetches a description
for everything surviving the filter on every run. **It does not.** `seen.json` is consulted at **fetch**
time, so a role found last week never reaches the description fetch again.

**Measured, twice against one live board:**

| | |
|---|---|
| Run 1 | `read 10 descriptions`, 20 rows |
| Run 2, same query | **`0 fetched`**, empty shortlist, `raw.json` **2 bytes** |

**The 132 in the original note must have been a first run or a `--reset`.**

🔴 **So the real failure was the other one this entry warned about: nothing is ever re-read.** A
description changes after posting — a band added, a requirement softened, the role quietly withdrawn — and
none of it is ever noticed, because the row never comes back.

🟢 **And measuring it found a second defect: `raw.json` is not a cache.** It is overwritten each run with
**that run's new rows only**, so the `role-radar` instruction *"read the cached description, no refetch
needed"* stops being true the moment another run happens. Corrected in the skill, and the archive in
`wiki/postings/` is the durable copy.

#### What was built instead

**`refresh.py` re-reads one archived posting** — the expensive pass, invoked deliberately at the moment
somebody is about to act, which is what keeps it bounded. Wired into `build-application` Step 0.

🔴 **The stronger of its two reasons is the date.** A listing censors the posting date and the detail
endpoint does not. Demonstrated on live data: an archived posting carried **2026-07-26**, the listing's
30-day cap; its detail said **2026-07-16**. **9 of 20 postings from that tenant arrived capped.** Age is
the best ghost-job predictor and the shortlist could not see it.

🟢 **It reconstructs adapter coordinates from the public URL**, because by re-read time `raw.json` is
gone. Both Workday hosting styles and Oracle, with the requisition taken off the URL — **not faked.**
Passing a placeholder there would have silently disabled the missing-requisition check and reported a
clean result it never ran, and a mutation doing exactly that is caught.

🟡 **It never writes to the archive.** That file is evidence of what the assessment was based on; today's
text is a different document, and a fetch can return a 404 page that would replace the evidence with
nothing. A mutation that clobbers the file is caught.



**`career-ops` splits its scan in two: trust the ATS feed for everything, then run a browser liveness check
*"only against new offers (after dedup), so the cost stays bounded."***

🔴 **This radar fetches a description for everything that survives filtering, every run** — 132 of them in
one real run. **Most of those were fetched last week and the week before.**

**Cheap pass over everything, expensive pass over the delta.** It is the same principle already applied one
layer up — *"do not research an employer below the build threshold"* — moved earlier in the pipeline.

🟡 **The thing to be careful of, and the reason this is not a two-line change:** a description that was
fetched once is cached in `raw.json`, but **a role's description can change after posting** — a salary band
added, a requirement softened. **Never re-fetching is a different failure from re-fetching everything.** A
sensible rule is to re-read anything the user is about to act on, and trust the cache for triage.

---

### 🔴 Read this before moving the user root — the paths that are load-bearing

**Compiled 2026-08-25 for the boundary work, from the code rather than from memory.** The move is
happening in a separate piece of work; this is the inventory it needs, and it is here because the person
doing it will be reading the entry below.

🔴 **`wiki/postings/` is now load-bearing and it was not a week ago.** It is the **only durable copy of a
posting** — `raw.json` is overwritten every run with that run's new rows, so nothing else survives.
`radar.archive()` writes it, defaulting to `HERE/../../wiki/postings` with a `postings_dir` override in
`config.json`, and **`refresh.py` reads it by path** when someone is about to apply. It is already on the
user's side of the line, but two tools now agree on where it is, and a third (`build-application` Step 0)
names the path in prose.

**Where a path is currently pinned, and to what:**

| | Holds | Note |
|---|---|---|
| `radar.py` | `CONFIG`, `RAW`, `SEEN`, `OUT`, and `archive()`'s default | **The four the handover asked to be told about.** Untouched this session |
| `radar/employers.py` | `employers.json` | 🔴 The private avoid list. **Never ships** |
| `doctor.py` | `sources/`, `wiki/`, `.git/`, both `config.json`s, `employers.json`, `ats_registry.json` | **Seven paths in one file** — the most concentrated place the move will show up, and the one that will silently report `OPTIONAL` for everything if a root changes under it |
| `registry.py`, `registry_check.py`, `add_employer.py` | `ats_registry.json` | 🟢 System-side. Ships, and stays where it is |
| `export_review.py` | `oversight/` | User-side |
| `verify.py`, `known.py`, `wikilinks.py`, `template_drift.py` | `--wiki`, defaulting to `wiki` | 🟢 **Already parameterised.** These need nothing |

🟢 **The pattern worth keeping**: the four that take `--wiki` are the ones that will survive the move
untouched. **Anything that computes a path from `HERE` is what has to change.**

🟡 **And one schema change, not a path**: `seen.json` records now carry `requisition` and `posted`, so a
repost can be spotted on a later run. Older records have neither and the check degrades to silence. **A
migration does not need to do anything about this** — it is additive — but a validator that rejects
unknown keys would break it.

---

### 🔴 There is no way for a user to take an update — and every day makes it worse

**Status: designed 2026-08-25, not built. Architectural, and the one that compounds.**

**A user clones this, fills `wiki/` and `sources/` with a year of their working life, and then cannot take
an improvement.** `sync-to-vault.sh` moves things the other way. **The honest current answer to *"how do I
get the new verifier?"* is *"hand-merge it, good luck."***

🔴 **That is fine at fifteen users and fatal at fifty**, and it gets worse every time this repo improves —
which is daily.

**The shape of the problem is a boundary nobody has drawn:**

| Clearly the system's | Clearly the user's | 🔴 **Genuinely ambiguous** |
|---|---|---|
| `tools/`, `.claude/skills/`, `githooks/` | `wiki/`, `sources/`, `oversight/<employer>/` | **`config.json`** — the user's queries and geography, in a file whose *schema* is the system's |
| `templates/` | `tools/radar/employers.json` | **`CLAUDE.md`** — the schema, which the user is invited to co-evolve |
| `ats_registry.json` | | **`.claude/skills/`** if a user has tuned one |

**The ambiguous column is the whole problem.** A naive `git pull` clobbers a tuned skill; a naive "never
touch user files" means the schema can never be improved.

🟢 **`career-ops` is solving this publicly right now** — *"[Umbrella] User/System boundary: make
personalization legible and update-safe"* is their second-most-reacted issue, and their `update-system.mjs`
already has a **"SAFETY VIOLATION on pre-existing dirty user file"** guard. **Watch how they land it before
building ours.** This is the one place where being second is an advantage.

🔴 **Whatever is built, the rule from everywhere else in this file applies: an update that silently drops a
user's change is the same class of failure as an ignore rule that silently drops a file.** It must fail
loudly and name what it could not merge.

---

### 🟡 A user guide — not yet, and the trigger is specific

**Status: raised 2026-08-25. Deliberately deferred.**

**The README is over 700 lines and already doing four jobs**: the disclaimer, a page for employers arriving
from an application, a pitch, and a reference. **A guide is a real need.**

🔴 **But writing one now would be guessing.** Nobody has run this system from a clean clone as a
first-time user. **Every sentence of a guide written today would be an assumption about where a beginner
gets stuck**, written by people who cannot get stuck because they built it.

🟢 **The trigger is the cold-start run**, which is the last item in this file. **That run is the guide's
source material** — the note of *"where I had to help it"* is the table of contents, and the questions the
agent failed to ask are the sections.

**What a guide should be, when it exists:** the first hour, in order, with the decisions called out —
**not** a second copy of the reference. If it repeats the README, one of them will drift and a reader will
believe the wrong one.

**Until then**, keep the README's *Your first hour* section honest, and fix it the moment the cold run
proves it wrong.

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

### 🟡 Everything after the submit button — FIRST PIECE BUILT

**Status: the interview pack ships 2026-08-25 as `build-application` Step 6.2. The rest of this entry
stands.**

🟢 **Written while the posting is open and the research is fresh, not the night before**: four STAR
stories chosen against this employer's own requirements, **each one taken from a 🟢 row in the REQS tally
so the citation is already there**; a Reflection line, because it is the half candidates skip and the half
that separates a rehearsed anecdote from someone who has thought about it; **the gap answer drafted before
it is needed**, since an improvised answer becomes a defence and a prepared one becomes a position;
questions pulled from the role page's own open questions; and a negotiation position **drafted only for a
role that clears the bar**, from the wiki's own numbers rather than from imagination.

🔴 **Two rules in it are there to stop a specific failure.** *"One story per requirement, not one story
reused"* — because the same incident told to three interviewers who compare notes is worse than three
weaker ones. And **never invent a competing offer**: it is the commonest negotiation advice online, it is
checkable, and a floor with a reason behind it does the same work and is true.

🟡 **What remains, and it is most of the entry:** outcomes after the interview, the decision itself, the
first ninety days, and the fact that **a rejection with a reason is worth more than a silent success** and
nothing yet asks for one.

### The rest of what happens after the submit button

**Deliberate scope decision, recorded in `CLAUDE.md`.** Not covered: interview preparation, offer
evaluation and negotiation, follow-up cadence, rejection debriefs.

**Interview prep is the largest and the wiki is already sitting on everything it needs** — every claim with
a verification status, the role page's pre-mortem which is the interviewer's objection list, the gaps the
cover letter conceded, and the user's own phrasing preserved verbatim. **A STAR bank built from
human-verified claims only would be the single highest-value addition.**

Negotiation is second: the framework already holds the salary floor, the anchors and the priced-vs-hard
veto distinction, so **comparing two offers is a scoring problem it can already do.**

### Job search source coverage — CORRECTED 2026-08-25, this entry had gone stale

🔴 **This said "only LinkedIn has been exercised" and that is no longer true**, which is the drift this
file warns about: an entry that has gone stale sends work at a problem that no longer exists.

| Source | Exercised? |
|---|---|
| **Workday** | 🟢 Verified against two live tenants, one of each hosting style |
| **Oracle Cloud CX** | 🟢 Verified against three live tenants |
| **Greenhouse** | 🟢 A real board resolved live via `sources_check` |
| **LinkedIn** | 🟢 The original, and still the only one exercised at volume |
| **Lever** | 🟡 Written and unit-tested; **no live board has been read** |
| **Adzuna** | 🔴 **Still needs a real key and a real run.** The only remaining unexercised adapter that needs credentials |

**The original entry follows.**

The adapter architecture exists and Adzuna, Greenhouse and Lever are written. Indeed is confirmed unavailable — `401` on job pages, `403` on search, tested 2026-08-23.
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

### ✅ Oracle Cloud Recruiting adapter — BUILT

**Status: ✅ 2026-08-25, 20 tests, verified against three live tenants** — a numbered site, a named site,
and a host with no region in it.

🟢 **Two values, not three, and both are in the careers URL:**
`https://<host>/hcmUI/CandidateExperience/en/sites/<site>/jobs`. **The site segment works directly as the
API's `siteNumber`** — confirmed on all three. The host is taken verbatim and not derived, because tenants
appear both with a region (`<pod>.fa.us2.oraclecloud.com`) and without (`<pod>.fa.oraclecloud.com`).

🟢 **It is the richest source in the repo.** An **exact ISO posting date** rather than Workday's
*"30+ days ago"*, the requisition number as the employer prints it, secondary locations, and a short
description **in the listing itself** — so a failed description fetch degrades to something real instead
of to nothing, which everywhere else makes a good role signal low for a reason unrelated to the role.

🔴 **It forced a correction to the `TRUNCATED` contract that applies to the whole package.** This adapter
has no window parameter but does have exact dates and a newest-first sort, so it filters exactly, in the
adapter, and **stops paging at the first row outside the window.** In every other adapter stopping early
means the source had more to give. **Here it means the opposite — everything in the window was seen** —
and reporting truncation would send the reader hunting for roles that do not exist.

🟢 **The rule now in `adapters/__init__.py`: set `TRUNCATED` from *why* the loop ended, never from
*whether* it ended early.** And an adapter may set `HONOURS_DAYS` true while filtering client-side, **as
long as the module says which** — *"the API filters"* and *"the adapter filters"* are different claims and
only one of them can be checked against the source.

🟡 **Not tiered on the short description, deliberately.** It would save a request per role and
systematically under-score this source against ones that give full text — **the same defect as a scoring
term only some inputs can earn**, which is already logged below about the salary bonus.

### ✅ Employer preference and exclusion lists — BUILT

**Status: ✅ 2026-08-25 as [`tools/radar/employers.py`](tools/radar/employers.py), with 29 tests, and
verified against two live employer boards. The design follows, because the reasoning generalises.**

**Every design point below is implemented**: reason *and* basis, with entries missing either reported;
category exclusions separate from name lists; hard exclusions separate from *assessed and declined*,
which marks a row rather than filtering it; and dated exclusions, with anything over two years or undated
raised for review.

🟢 **Both refinements from first use are in.** The list says who to watch and the adapter is an
implementation detail — `route()` folds a watch entry into whichever of Workday, Greenhouse, Lever or a
named query reaches that employer. **And exclusions work at division level**, matched against the job
title where division names actually appear.

🔴 **A watch entry with no route is reported as NOT watched**, in the shortlist and on the console. That
was not in the design and it should have been: the failure it prevents is silent, because an employer
nobody can reach simply never appears, which is indistinguishable from an employer with nothing open.

🟢 **The exclusion passes are split, and the split is the interesting part.** Employer and division
exclusions run **before** descriptions are fetched, so a settled question costs nothing. Sector exclusions
run **after**, because a category is the half that catches employers the user has never heard of and that
cannot be judged from a company name. Pinned by a test that asserts the excluded row never reaches
`fetch_body`.

🔴 **The safety rule is now in `CLAUDE.md` rather than implied by the file filter**, as this entry asked.

🟡 **One defect found while building it, worth repeating elsewhere.** Whole-word matching was written as
`\b` + keyword + `\b`, which **silently never matches a keyword that begins or ends with punctuation** —
there is no word boundary against a non-word character. The user would believe a sector was filtered and
it would not be. Found by a placeholder in a test fixture, of all things.

### 🟢 The original design

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

🟢 **Run against two live tenants the same day, one of each hosting style. It found two defects that no
recorded fixture could have**, which is the argument for doing this to every adapter:

| Found | Why a fixture could not catch it |
|---|---|
| 🔴 **The public URL differs by hosting style.** Shared-host needs a `/recruiting/<tenant>/<site>` segment the per-tenant form does not | **The fixture asserted the shape the code produced.** Both styles now verified as HTTP 200, and where the detail is fetched the employer's own `externalUrl` is used in preference to any construction |
| **Descriptions arrive with HTML entities intact**, so a company name with an ampersand in it came through as `Acme&amp;Co` | Invented fixture text had no entities in it |

🟢 **And it confirmed two design guesses cheaply.** `searchText` really does filter server-side
(352 → 127 → 0 on a nonsense term), so the query is worth sending rather than discarding as the board
adapters do. And **14 of 40 postings in one sample had hidden locations** — 35%, far more than expected,
which settles whether the extra call earns its place.

🟢 **One of those expansions is the "remote is country-scoped" defect, caught in the wild by a different
mechanism**: a posting listed as one city expanded to four entries, three of them of the form
*Remote - \<US state\>*. **State-scoped remote, invisible in the listing** — and a scope that decides
right-to-work and payroll before anything else about the role matters.

🟡 **The remaining limitation: Workday will only say "30+ Days Ago".** A role six months old and one exactly thirty days old
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

### ✅ Source coverage is geography-dependent — `sources_check.py` BUILT

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

✅ **Built 2026-08-25 as [`tools/radar/sources_check.py`](tools/radar/sources_check.py)**, with a
`probe(cfg)` contract on every adapter and 22 tests.

🟢 **The design centre is the control probe, and it is the part worth copying.** The incident above is not
"the API returned 404" — it is that **404-for-your-country and 401-for-a-bad-key are indistinguishable
from one request**, and the two point in opposite directions: one says get a new key, the other says no
key will ever help. So the adapter probes a **known-good control country** alongside the user's own and
diagnoses from the pair. One probe cannot answer this. Two can.

🔴 **And the second distinction, which is this repo's oldest theme in a new place.**
**`NOT CONFIGURED` is not `FAILED`.** Most sources here watch named employers rather than searching, so an
empty list means nobody is being watched — a fact about the config, not a fault in the source. Reported as
broken it sends someone to debug a source they never wanted; reported as fine it claims coverage that does
not exist. *Not recorded versus recorded as absent*, for the fourth time.

**It also reports**: an employer on the watch list with no route, a Workday `422` as a wrong shard rather
than a bad request, and — loudest — **"0 usable", because a radar run with no working source is silent,
and a silent run looks exactly like a quiet week.**

🟡 **What it deliberately does not claim.** It proves a source answers. It cannot prove the source covers
a country *well*, which is a judgement, and saying otherwise would recreate the README line that started
this.

### 🔴 Oracle does not reject an unrecognised site. It widens the search

**Status: found 2026-08-25 while building the source check, against three live tenants. Detected, not
fixable.**

A mistyped or wrong `site` value in the Oracle config **does not fail.** Oracle ignores a `siteNumber` it
does not know and answers with the tenant's default set instead, so the search **silently widens to
everything that tenant posts** — on a multi-brand tenant, other employers' roles under the name the user
gave. Measured on one tenant: a real site scoped to **152** postings while a nonsense value returned
**258**.

🔴 **Nothing in a single response distinguishes that from a correct config**, which is the same shape as
the coverage-versus-key ambiguity above, arrived at from the other end. **`sources_check.py` detects it the
same way** — it asks for a deliberately nonsense site and compares the counts.

🟡 **The detection is honest about its own false positive.** An employer that genuinely runs a single site
will match the control legitimately, so the warning says so rather than asserting a fault.

**Not fixable in the adapter**, because there is no validation endpoint to call: the public careers page
returns `200` for a nonsense site too. **Verified, not assumed.**

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
