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

**A list this long is not a plan.** Three things about their state, then an order.

*(This said "twenty-five items" and had drifted — there are 27 open now. Counts written into prose go
stale silently, which this file already has an entry about: "The test count was written in three places
and wrong in all three". So the number is gone rather than corrected.)*

### 1. Nine of these are already fixed as *documented behaviour*, not as code

**Ported into `SCHEMA.md`, `templates/` and the skills on 2026-08-24.** The entry stays because the
reasoning is worth keeping — **but do not re-implement them:**

| Now a documented rule | Where |
|---|---|
| Fetch the employer's own posting, never the aggregator's | `build-application` Step 1 |
| Score the journey, not the address; a transit stop is not a commute | `templates/Role Scoring Framework.md` |
| Standing-gaps list; *not recorded* ≠ *recorded as absent* | `SCHEMA.md` |
| Three scores instead of one total; the requirement count | `templates/Role Scoring Framework.md` |
| Do not answer a tie by lengthening the ruler | same |
| Score against the user's baseline, not the field | same, plus `career-init` |
| The internal move as a third option | `SCHEMA.md` |
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
4. 🔴 **`vault/settings/employers.json` (yours) and `tools/radar/ats_registry.json` (the registry) are one
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
parses the outcome vocabulary out of both `SCHEMA.md` and the template and asserts they are the same set**,
so the two copies cannot drift again, and it fails if any prescribed table is removed from the framework
page. **This is the point: the audit found things no rule-reading could, so the audit became mechanical
rather than something someone has to remember to repeat.**

| | Rule | Verdict |
|---|---|---|
| 1 | Fetch the employer's own posting | ✅ **Fixed.** Was 🔴 **contradicted by another skill.** `role-radar` step 2 says *"read the cached description — already in `raw.json`, no refetch needed"*, then step 3 says score from it. For an aggregator row that cache **is** the truncated posting. **The truncation entry below is explicit that the employer's own posting must be fetched *before assessment*, because by packaging time the score has already been used to decide** |
| 2 | Score the journey, not the address | ✅ **Fixed** — a *Known locations* table now exists. Was 🟡 **prescribing two things with nowhere to put them.** *"Store employment clusters once and reuse them"* and scoring from where the user actually lives — **no template has a slot for either**, so both get re-derived per role, which is the failure the rule describes |
| 3 | Standing-gaps list | ✅ **Fixed** — the table is shipped empty. Was 🔴: **`SCHEMA.md` said to keep the table "on the framework page". The framework template has no such table.** A fresh vault starts with the instruction pointing at a section that does not exist — and this is the rule whose entire purpose is that an absence must be *recorded* rather than merely unfound |
| 4 | Three scores, and the requirement count | 🟢 Present and consistent |
| 5 | Do not lengthen the ruler | 🟢 Present and consistent |
| 6 | Score against the baseline | ✅ **Fixed** — the table's first row is the current job. Was 🟡: said *"the first row of the table is the current job"* — **the table has no baseline row and no status value that could describe one** |
| 7 | The internal move as a third option | ✅ **Fixed** — it is the table's second row, with the prompt. Was 🔴: **`SCHEMA.md` said "score it as a row in the table". The word *internal* does not appear in the framework template at all**, and nothing prompts for it — while `SCHEMA.md` itself says a user in a stable job will never raise it unprompted |
| 8 | "Remote" is country-scoped | ✅ Fixed in code 2026-08-25. It had been doing the reverse |
| 9 | Why-X answers, values with three examples | 🟢 Present and consistent |

## 🔴 Defects — things that behave wrongly

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

### 🟡 Example and template files are a leak vector — VERIFIED AND HALF-CLOSED 2026-08-28

🔴 **The rules below were rules and not checks, and testing them found three gaps.** The original
leak shape was replanted on 2026-08-28 — a real town, its county and a postal district — all lowercase — in
`templates/settings/search.example.json` — and **it passed the entire suite.** The substance check
matched only a PROPER NOUN, and a settings file's locations are conventionally lowercase. The job
titles beside it were caught; **the geography, which is what actually leaked, was not.**

🟢 **Closed: example settings values must now be `<placeholders>`, the repo's fiction, or one of 25
listed technical identifiers.** Every one of those 25 was read before being listed, which is the
point rather than a side effect. The original leak now fails the suite.

🟢 **Closed: `doctor`'s `settings leak` check** covers what the suite structurally cannot — a public
repo must not carry a denylist of its author's private details, so the comparison has to happen
where the private data is. It reports employers from the user's own watch and avoid lists appearing
in tracked files. 🔴 **The first draft scanned every settings value and reported 229 findings**,
because a signal vocabulary is generic by design; scoped to employer names it reports 12.

🟢 **Twelve became seven on 2026-08-28.** The excluded DIVISION — the one genuinely sensitive entry,
because refusing to work somewhere is a fact about a person rather than about a company — is gone
from every tracked file. `tools/radar/employers.py` and `tools/tests/test_employers.py` now carry
the repo's own fiction, and the test still proves the bug it was written for: **a division posting
under its own name escapes a parent-keyed exclusion**, which put 16 rows on a live shortlist.

🔴 **Genericising it exposed a wrapping bug in my own edit**, and it is the third time this week: a
line-by-line replacement left two occurrences intact because they wrapped across lines. **Sweep on
the flattened text, not the raw lines.**

🟡 **Seven remain and they are a different question.** All name a WATCHED employer, in ATS-mapping
code and in findings — `ats_registry.json` maps employers to their ATS and is contributed back
deliberately, which is a public fact about a company. **Whether being seen to watch an employer
matters is the user's call**, so the check WARNs and names files rather than gating.

---

### 🔴 The original entry, kept because the rules are still binding

**Status: happened 2026-08-24. Caught, remediated by history rewrite, and worth a permanent rule.**

`search.example.json` shipped with **one user's actual commuting geography — home county included — their
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

## 🟡 Gaps — things the system does not do yet

### ✅ test_boundary.py checked the FORM of the boundary, not the SUBSTANCE — TWO CHECKS ADDED

**Three violations found on 2026-08-26, none of which the boundary test could see.** All three had the
same shape: **content specific to one user, living in files the repo ships to everyone.**

| Found | What was shipped to every clone |
|---|---|
| 🔴 `tools/radar/radar.py` | One person's whole tiering vocabulary — a weight for the phrase that pre-answered their objection, a heavy negative for an industry that kept mismatching their words, a penalty for a commute they would not accept, and a list of trades to exclude by title |
| 🔴 `tools/cv_lint.py` | **One market's spelling, enforced with a non-zero exit and no flag.** A candidate in another market got a finding for every correctly-spelled word |
| 🟡 `templates/settings/search.example.json` | Two **real employers** in the `watch` list of a template that says *"REPLACE EVERY PLACEHOLDER"* |

🟢 **All three are fixed.** The vocabulary is `vault/settings/signal.json`, the spelling is
`vault/settings/profile.json`, and the template carries placeholders. **In each case the default when
the file is absent is to do NOTHING** — no tiering, no spelling enforcement — because falling back to
somebody's values is how each bug worked in the first place.

🔴 **The gap is that nothing would have caught any of them.** `test_boundary.py` asserts that no *file*
under `vault/` is tracked. **It says nothing about user-specific *content* in `tools/`, `templates/` or
`.claude/`** — and that is the direction the leaks actually went. **The same distinction let an editor's
workspace file name vault paths from the repository root** (see the `.obsidian/` entry): the guard covers
the form of the boundary and not its substance.

## ✅ What shipped, 2026-08-26

**Two of the three. Both were dry-run against the repo before being written**, and both were then
verified by putting the real leaks back and watching them fail.

| Check | Catches |
|---|---|
| 🟢 **No template carries a real organisation** | A capitalised multi-word phrase in a non-comment JSON value. `State Street` fires; `Acme Corp` does not |
| 🟢 **No tool ships a weighted preference table** | A module-level list of three or more `(string, number)` pairs — the exact shape the tiering vocabulary had |

🔴 **The false-positive case fired on the first draft, which is why it is a test of its own.** The
proper-noun rule flagged **`Acme Corp`, `Employer One`, `Employer Two`, `Employer Three`** — the repo's
own deliberately fictional stand-ins. **A rule that punishes a well-written template is worse than no
rule**, so the check now allows the established fiction and a second test pins that: the fictional names
must pass *and* the real ones must fail. **Both halves, or the allowlist silently swallows everything.**

🔴 **Locale enforcement — the third — is NOT done, and is not attempted.** A spelling list and a
vocabulary list are structurally identical; the only signal is *enforcement without configuration*, and
nothing found so far distinguishes that from a legitimate constant. **Two solid checks beat three where
one cries wolf.** It stays below as an open item.

**The original entry follows.**

---

**What a check could look for, in rough order of confidence:**

1. 🟢 **Real employer names in `templates/`.** A template is placeholders by definition; a capitalised
   multi-word proper noun outside a `_comment` is nearly always somebody's real answer. **Cheapest and
   most reliable.**
2. 🟡 **Weighted keyword tables or preference lists in `tools/`.** Structurally recognisable — a literal
   list of regex-and-number pairs is almost always a taste, not a mechanism.
3. 🔴 **Locale assumptions.** The hardest, because a spelling list looks exactly like a vocabulary list.
   **The signal is enforcement without configuration**: a check with no way to turn it off, in a repo
   used across markets.

🔴 **The false-positive case, and it is severe here.** `ats_registry.json` is *made of* real employer
names and is explicitly the one file a stranger may contribute to. `docs/` names real markets and
regulators deliberately, to teach. **A check that flags those fires on the repo's best content and gets
switched off in a week.** Any rule must be scoped to files whose *purpose* is to be generic — templates
and defaults — and never to registries, documentation or tests.

🟡 **Worth noting what was NOT a violation, because the distinction is the useful part.**
`build-application/WRITING.md` is a declared Ireland/UK profile with a *Localising this* section naming
the three parts that change elsewhere. **A documented default is not a hidden assumption.** The problem
was never that the repo had a default — it is that the code enforced one silently.


### ✅ The signal tier measured the advert, not the job — TIER DEMOTED TO A HINT, 2026-08-26

**Measured 2026-08-26 against a real run of 5,255 roles and 17 hand-scored assessments.** The keyword tally
renders as `HIGH` / `MED` / `LOW`, and **the tier carries no information about role quality.**

🔴 **The proof is a single contract advertised by three agencies on the same day:**

```
Berkley Group   tally 14  MED   -> surfaced
Stelfox         tally 14  MED   -> surfaced
IT Search       tally  9  LOW   -> never shown
```

**Same job. One write-up fell below the threshold entirely.** The same thing happens without agencies: one
employer's *Senior Engineering Manager, Developer Productivity* scores **20 (HIGH)** in its US listing and
**17 (MED)** in its Canadian one. **A tally over the advert text is a measure of the copywriting.**

🔴 **And the tier does not predict the framework score.** Across 17 roles assessed by hand against the
framework:

| Tally | Tier | FIT |
|---|---|---|
| 21 | HIGH | **12** |
| 21 | HIGH | **10** |
| 19 | HIGH | 14 |
| **15** *(nearest the HIGH cut)* | MED | **12** |
| **15** *(nearest the HIGH cut)* | MED | **10** |
| 13 | MED | 🟢 **15** — the best role assessed |
| 13 | MED | 🟢 **14** |
| 13 | MED | **6** |

**Tally 13 spans FIT 6 to 15.** 🔴 **The two roles nearest the HIGH threshold scored 12 and 10, below two
roles further from it.** *"Nearly HIGH"* is not a useful filter, and reading in tier order is reading in
copywriting order.

🟢 **This is not a defect in the tally.** A keyword count does what a keyword count does, and the skill
already says `SIGNAL` is not a score and to always read MED. **What is missing is the consequence of that
being true:** if the tier is uninformative, the system should stop using it as the gate on what a person
ever sees.

## ✅ What shipped, 2026-08-26

**Option 3 below, and it was the right one.** Everything that clears the real filters — location, title
shape, the avoid list — is now **listed in full** under *"Everything else that passed the filters"*,
**sorted by employer rather than by tally.** The tiers remain as a reading hint above it.

**On the first run after the change: 1,691 roles became visible that had been dropped.**

🟡 **Options 1 and 2 are now unnecessary rather than rejected.** *"Never drop a watched employer"* and
*"surface on a strong title match"* were both ways of rescuing individual roles from a gate. **With no
gate there is nothing to rescue from.**

🔴 **The floor stayed, and that was the point of the false-positive note below.** Roles still have to
clear location, title shape and the avoid list — 4,204 were dropped on location alone in that run. **What
changed is that the keyword count no longer decides what a person is allowed to see.**

**The original entry follows.**

---

**Three options, and they are not equivalent:**

1. 🟢 **Never drop a role from a WATCHED employer, whatever the tally.** A watched employer is an explicit
   statement of interest; **letting a keyword count veto it is the tail wagging the dog.** Cheapest change,
   and the one with the clearest rationale.
2. 🟡 **Surface LOW roles whose TITLE matches a query strongly**, even when the body scores low. The IT
   Search listing was terse, not irrelevant.
3. 🔴 **Report the tier but sort by something else** — employer, then title. **Sorting by tier actively
   misleads**, because it presents copywriting density as a ranking.

🔴 **The false-positive case to think about first:** the threshold exists because **1,347 roles passed the
location filter and the avoid list in one run.** Removing it entirely returns a pile nobody reads, which is
worse than a biased order. **Any fix has to keep a cut somewhere** — the argument above is only that the cut
should not fall on a watched employer, and that the surviving order should not pretend to be a ranking.

🟡 **Checked, so nobody re-checks it:** of those 1,347 dropped, 312 had a senior-sounding title, and the top
of that pile by tally was *.NET Technical Lead*, *Principal Software Engineer*, *Technical Team Lead*.
**Nothing strong was hiding below the line in that run** — the threshold is doing useful work. **The problem
is the tier order presented above it, not the existence of a floor.**


### ✅ Oracle identifies an employer by `site` alone, and the default site value is not unique — FIXED 2026-08-28

**Found 2026-08-25 while making the radar label rows with employer names instead of ATS slugs.** The
Oracle adapter carries `host` and `site` per employer, **but everything downstream keys on `site` only**
— the `names` map, and the company written onto each row. 🔴 **`CX_1001` is Oracle's default site
identifier and two shipped registry entries already use it.** `host` is what actually distinguishes
them and it is discarded.

**Three consequences, in increasing severity:**

| | |
|---|---|
| **Rows are unhelpfully labelled** | Both employers' roles appear as `CX_1001` |
| **A `names` label cannot be written for either** | `resolve()` now detects the collision and refuses — see below |
| 🔴 **Dedup may collapse across employers** | Two roles with the same title at two employers both labelled `CX_1001` look like one role to a `(company, title)` dedup. **Unconfirmed** — it needs a same-title collision to bite, so it would appear as a role silently missing rather than as an error |

🟢 **The labelling half is already handled and is not what this entry asks for.** `registry.resolve()`
drops the label when two employers share an identifier and says so on the run's report, because **a slug
is unhelpful but a confidently wrong employer name is worse — it gets believed.** That is a guard, not a
fix: it makes the collision visible instead of harmful.

**The fix is to key on `host` + `site` throughout** — in the `names` map, in the row's company field,
and anywhere else an employer is identified — so two tenants on the same default site stay distinct.

🔴 **The false-positive case to test first, and it is not obvious:** a compound key must not break the
employers that are *correctly* identified by site today. Several registry entries carry a genuinely
unique site value, and their rows and any hand-written `names` label are keyed on that value alone.
**Changing the key silently invalidates every existing label** — the map still loads, the lookup misses,
and rows quietly revert to showing the raw identifier. **Migrate the lookup to accept either form**, or
the fix for unhelpful labels produces no labels at all.

🟡 **Related, already documented in `adapters/oracle.py` and worth reading with this:** an unrecognised
site does not fail, it **widens** — Oracle ignores a `siteNumber` it does not know and returns the whole
tenant. So a wrong site value returns *more* roles, not none, and `sources_check.py` detects it by
asking for a deliberately nonsense site and comparing counts. **One employer in a real config is
currently answering with ~7,300 roles for exactly this reason.**


### ✅ Nothing checks what OTHER tools leave beside the code — BUILT 2026-08-27

**Status: `tools/foreign_state.py`, wired into `doctor.py` (warns) and `githooks/pre-commit` (blocks),
exactly as this entry specified.**

🟢 **The design followed the three traps named below, and the third one fired on the first run.** The check
flagged **itself** — its own docstring names a vault path as an example, and while it was still untracked it
looked like a leak. **Directories this repository maintains are now exempt**, because a new file under
`tools/` or `docs/` is the author writing the system and is already covered by `test_boundary` and by both
existing hook rules.

🔴 **The hole that leaves is stated in the code rather than hidden**: a foreign tool writing into `tools/`
would be missed. No editor or sync tool does — they write to dot-directories and the repository root — and
narrowing there is what keeps the check quiet enough to stay switched on.

**11 checks, including all three false-positive cases**: an ordinary new source file, a bare mention of
`vault/`, and the repo's own directories. **Verified against the real incident**, reproduced from the
original `.obsidian/workspace.json` shape.

🟡 **And the non-check half of this entry still stands and is worth saying to the user**: pointing Obsidian
at `vault/` rather than the repository root removes the symptom and the leak together.

**Original entry:**

**Found 2026-08-25.** `.obsidian/` sat at the repository root, **untracked but not ignored**. Its
`workspace.json` records open and recently-opened files **by path**, so it named
`vault/settings/employers.json`, `vault/AGENTS.md` and whichever pages had been read last. **Untracked is
not ignored** — one `git add -A` would have published a list of a user's private files to a public
remote. `.gitignore` now covers it. **The class it belongs to does not.**

🔴 **Both existing controls missed it, and neither was malfunctioning.**

| Control | Why it did not fire |
|---|---|
| `tools/tests/test_boundary.py` | Checks what **this repo** writes outside `vault/`. Obsidian wrote this. **The guard covers the agent, not the desk it works on** |
| `githooks/pre-commit` rule 1 | Blocks staged paths **under `vault/`**. `.obsidian/workspace.json` is not under `vault/` |
| `githooks/pre-commit` rule 2 | Content heuristics look for **emails, LinkedIn URLs and salary phrasing**. A JSON file listing vault *paths* matches none of them |

🟢 **Verified rather than reasoned about:** force-staged with `git add -f` and the hook run directly, it
was **allowed**.

**The class is every tool that drops state next to a repository** — `.idea/`, `.vscode/`, `.trash/`,
editor swap files, sync-tool conflict copies. Any of them can name a vault path, and the next one will
not be Obsidian.

**Closing it — and the false-positive case decides the design, so test it first:**

1. 🔴 **"Fail on any untracked, non-ignored file" is useless and will be switched off in a day.** Every
   new source file is untracked before it is added. That check fires during ordinary development, every
   time.
2. 🟢 **Narrow it to what actually indicates a leak:** a path that is **neither tracked nor ignored**
   *and* whose contents name a **specific file under `vault/`** — `vault/<folder>/<file>` — rather than
   the bare string `vault/`.
3. 🔴 **Matching the bare string `vault/` is the trap.** This repository refers to `vault/` constantly
   and legitimately: `tools/lib/paths.py`, `SCHEMA.md`, `AGENTS.md`, every skill file and this entry.
   **A check on the bare string flags its own documentation**, which has already happened twice to the
   content heuristic in `pre-commit` — see the comment in that file.

**Where it belongs:** `doctor.py` warns, because it runs per session and this is advisory; `pre-commit`
hard-fails, because staged is the last moment before history. **`test_boundary.py` is the wrong home** —
it tests the code's behaviour, and this is a property of the working tree.

🟡 **Also worth telling the user, and not a check at all:** `.obsidian/` at the repository root means
Obsidian indexes `tools/`, `templates/`, `docs/` and `examples/` as notes, so system files appear as
unlinked pages beside the user's own. **Pointing Obsidian at `vault/` scopes it to exactly the boundary
this repository already draws**, and removes the symptom and the leak together.


### ✅ No `.docx` route — BUILT 2026-08-27 as `tools/cv_docx.py`

**Status: built, and it turned out to be more urgent than this entry said.**

🔴 **The entry described a gap for agency applications. By the time it was built it was the DEFAULT case.**
`Application Mechanics` was reversed on 2026-08-26 — *"upload the `.docx` to an employer portal; send the
`.pdf` to a human"* — and `build-application` was still telling the user *"a PDF parses more predictably in
an ATS than a .docx built by a library"*. **The skill was arguing with the vault**, and every application
since the reversal followed a policy the tools could not support.

🟢 **The objection in this entry was right and shaped the design.** Generating `.docx` with a library IS
platform-specific — so the tool writes the ZIP-of-XML itself, from the standard library, with no
dependencies at all.

🟢 **It emits none of what breaks ATS parsing**: no tables, text boxes, columns, headers, footers, images or
Word list numbering. Contact details go in the body, because a header is where they go to be lost. Headings
use real Word styles, because an ATS finds sections by style name. **Verified against macOS `textutil` as
well as by unit test — a third-party parser reads it correctly, in order.**

**12 checks.**

**Original entry:**

**`build-application` Step 6 produces a PDF only** — the CV is written as HTML from `templates/cv.html`
and the user prints it from their browser. 🟢 **That choice is right and should not be undone casually:**
it needs nothing installed, behaves identically on macOS, Windows and Linux, and gives full typographic
control. Generating `.docx` with a library or converting via an office suite is platform-specific and
fails on somebody else's machine.

🔴 **But PDF-only cannot serve an agency recruiter, and the system does not say so anywhere.** A
recruitment consultant reformats a candidate's CV onto their own letterhead and strips the direct
contact details before forwarding it to the client. Handed a PDF they retype it or send it unchanged.
**In a real vault every direct-employer application carried both a PDF and a `.docx`, and the single
agency application carried a `.docx` and no PDF** — the user had worked this out for themselves, with a
previous toolchain the system has now replaced.

**The gap surfaces at submission time**, which is the worst moment to discover a missing artefact.

**Three ways to close it, in increasing cost:**

1. **Document the manual route and stop.** Step 6 gains a line: for an agency, paste the rendered HTML
   into a word processor and save as `.docx`. Honest, free, and puts the work on the user every time.
2. 🟢 **Write the `.docx` directly.** A `.docx` is a zip of XML — **no library and no office suite are
   actually required**, only `zipfile`, which is in the standard library. This keeps the cross-platform
   property that motivated the HTML route in the first place.
3. 🔴 **Take a dependency on `python-docx`.** Rejected unless 2 proves impractical. The whole document
   pipeline is currently dependency-free and that is worth more than the convenience.

**Two things any implementation must get right, and both have already gone wrong once elsewhere:**

- 🔴 **Strip the metadata.** `docProps/core.xml` and `app.xml` carry `dc:creator`, `cp:lastModifiedBy`,
  `Company` and the authoring application — a quiet leak of the author's name and their office install
  into every document a recruiter receives. **A real vault's fifteen `.docx` were checked and came back
  effectively empty, but that was the previous toolchain's behaviour, not a control.** Assert it in a
  test rather than inheriting it.
- 🔴 **Two artefacts, one lint.** Step 7 lints text extracted from the PDF, on the reasoning that this
  approximates what an ATS receives. **If a `.docx` is generated separately and the two ever diverge,
  the check runs on the file that was not sent.** Either generate both from one source and test that
  their extracted text matches, or lint both.


### 🟡 `Migrate` is a documented operation with no log prefix

**Found 2026-08-25, running `/career-migrate` on a real vault.** `SCHEMA.md` lists **Migrate** among the
operations under *Operations*, and every operation ends *"update `index.md`, append to `log.md`."* But the
prefix list — in `SCHEMA.md` under *Log format* and again in `templates/log.md` — is:

```
ingest · interview · radar · build · data · query · lint · fix
```

**There is no `migrate`.** The entry was written as `ingest`, which is the closest fit and is wrong: an
ingest is one source being read into the wiki, and a migration is a hundred files being sorted, three
deleted and one retyped. **The prefixes exist to be grepped**, and the one operation that reshapes the
whole vault is the one that cannot be found:

```bash
grep "^## \[" vault/wiki/log.md | grep migrate
```

**Two ways to close it, and they are not equivalent:**

1. **Add `migrate` to both prefix lists.** One line in each. But 🔴 **a prefix list in prose is exactly the
   class of control this repo has watched fail** — it drifted here because two files carry the same list and
   nothing compares them.
2. 🔴 **Better: make the list mechanical.** One definition, and a test that fails when `SCHEMA.md`,
   `templates/log.md` and the set of documented operations disagree. That catches this instance *and* the
   next operation added without a prefix.

**Check the false-positive case before shipping the test:** a user's own log will contain entries this
system never wrote, and a check that rejects unknown prefixes in *their* log rather than in *our* templates
would fire on every hand-written line. **It should compare the two shipped lists to each other, and say
nothing about the contents of any vault.**


### 🔴 "Track outcomes" was shipped as an instruction and ignored for six weeks

**Status: rule added 2026-08-24 with a trigger. The instruction alone had already failed.**

`SCHEMA.md` said *"record what happened to every application"* and *"if the user asks why nothing is
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
written to `vault/postings/<Employer> - <Title>.txt` before `seen.json` is updated and `raw.json` is
overwritten**, carrying the posting date, location, pay and source URL alongside the text. **Shortlisted
rather than everything fetched**, because the shortlist is by definition what an agent reads and the
standing rule is that everything read gets assessed — archiving all 130-odd fetched descriptions would keep
mostly roles nobody looked at.

🔴 **It never overwrites.** An archived posting is evidence of what was read *at the time*, and a later
fetch of the same URL returns either an edited posting or a 404 page — **which would replace the evidence
with nothing.**

🟡 **Still manual on the other two routes**: a link the user pastes, and a role assessed from an employer's
own site. The rule is in `SCHEMA.md` and both skills; nothing enforces it.

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

### 🔴 Read this before moving the user root — the paths that are load-bearing

**Compiled 2026-08-25 for the boundary work, from the code rather than from memory.** The move is
happening in a separate piece of work; this is the inventory it needs, and it is here because the person
doing it will be reading the entry below.

🔴 **`vault/postings/` is now load-bearing and it was not a week ago.** It is the **only durable copy of a
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
| `export_review.py` | `vault/oversight/` | User-side |
| `verify.py`, `known.py`, `wikilinks.py`, `template_drift.py` | `--wiki`, defaulting to `wiki` | 🟢 **Already parameterised.** These need nothing |

🟢 **The pattern worth keeping**: the four that take `--wiki` are the ones that will survive the move
untouched. **Anything that computes a path from `HERE` is what has to change.**

🟡 **And one schema change, not a path**: `seen.json` records now carry `requisition` and `posted`, so a
repost can be spotted on a later run. Older records have neither and the check degrades to silence. **A
migration does not need to do anything about this** — it is additive — but a validator that rejects
unknown keys would break it.

---

### 🟡 Taking an update: the code half works. The vault half is the gap

**Status: re-measured 2026-08-26, and the original entry was wrong.** It was written on 2026-08-25 and
claimed there was *no way* to take an update, resting on two premises that have both since evaporated:
`sync-to-vault.sh` **no longer exists**, and the user's queries and geography are no longer in a tracked
`config.json` — they are `vault/settings/search.json`, which is gitignored like everything else under
`vault/`. **The ambiguous column that was "the whole problem" has mostly collapsed.**

🔴 **So it was tested rather than argued about.** Clone the repo, rewind eight commits to simulate an old
install, populate a vault, `git pull`:

| | |
|---|---|
| Old install | 507 checks pass |
| `git status` before pulling | **empty — the vault is invisible to git, as designed** |
| `git pull` | exit 0 |
| The vault afterwards | **untouched** |
| After the update | 536 checks pass |

**`git pull` is the update mechanism, and it works.** That half of the entry is closed.

### What the test actually found instead

🔴 **The gap is not the code. It is that an update can require a vault file it cannot deliver.**

The tiering vocabulary moved into `vault/settings/signal.json` on 2026-08-26. A user who pulls that change
gets the new radar and **not the file it reads**. The radar still runs, still fetches, still writes a
shortlist — HIGH and MED are simply always empty and every role lands in the catch-all section. **That
reads as a quiet week, not as a broken install**, which is the worst failure this system can have.

🟢 **Two pieces of that are now covered**, both by executable checks rather than by a note:

- **`doctor.py` reports a missing or unedited `signal.json`** — and is scoped to installs that actually
  have a `search.json`, because it cried wolf on one that did not.
- **`tools/template_drift.py`** already does the equivalent for `wiki/` pages.

### 🔴 What is still open

- 🟢 **The settings case is now generalised — `tools/settings_drift.py`, built 2026-08-26.** Verified on a
  real pulled clone ten commits behind: it named the missing `linkedin` block and both missing location
  lists, and exited 1. It found a genuine gap on its first run, too — `profile.json` shipped with no
  example, so nobody cloning could discover the setting existed. **`doctor.py` and `settings_drift.py`
  split the job**: drift says *your file is missing a key the system reads*, doctor says *this specific
  absence will silently do nothing to you*.
- ~~**A tuned `.claude/skills/` or `SCHEMA.md` is still clobbered by a pull**, silently.~~ 🔴 **TESTED
  2026-08-28 AND IT IS NOT TRUE.** Cloned, rewound six commits, edited `SCHEMA.md` in the region the
  update also changes, pulled. **git refuses and says so:** *"error: Your local changes to the following
  files would be overwritten by merge: SCHEMA.md … Aborting."* A non-conflicting edit merges and
  survives. **Nothing is silently clobbered, and this entry was wrong for three days.**

  🔴 **But testing it found the real failure, which is the opposite one and IS quiet.** The pull ABORTS,
  so nothing updates — and `git pull` is step 1 of `runbook.py update`, whose four remaining steps read
  the code already on disk and all pass. **A user who does not read the git output concludes they are
  current when they are several versions behind.**

  🟢 **Built: `doctor`'s `updatable` check**, which reports tracked local modifications *before* the pull
  and names the files. It makes no network call, so it says whether an update *could* land, never whether
  one exists. **Third backlog entry this week that was fixed by testing its premise rather than its
  claim.**
- 🔴 **The rule from everywhere else on this page still applies: an update that silently drops a user's
  change is the same class of failure as an ignore rule that silently drops a file.** It must fail loudly
  and name what it could not merge.

🟢 **`career-ops` is solving the same problem publicly** — *"[Umbrella] User/System boundary: make
personalization legible and update-safe"* is their second-most-reacted issue, and their `update-system.mjs`
has a **"SAFETY VIOLATION on pre-existing dirty user file"** guard. Worth watching for the skills case.

---

### ✅ A requisition number in a title defeats dedup — FIXED 2026-08-27

**Status: fixed, and the false-positive case decided the design as predicted.**

🟢 **`strip_req()` only ever OPENS the question; the bodies then have to agree.** A trailing token that is mostly digits is stripped — `R-281578`, `JR354003`, `210768893`, `2026-6489` — and a merge happens only when the two descriptions overlap by 60%. **No body on either side means no evidence, and the conservative answer is two roles.**

🟢 **Measured on the live corpus: 3 title-pairs differ only by a requisition number. One merges because the bodies agree; two stay separate because they do not.** The body check is doing real work rather than rubber-stamping — which is exactly what the entry below said it had to prove.

🔴 **Two cry-wolf directions are tested**: real titles ending in `II`, `III`, `EMEA` or `2` are untouched, and two genuinely different requisitions under one title stay separate.

**Original entry, kept because the reasoning is the point:**

**Mastercard advertised one job twice**: `Director, Software Engineering` and `Director, Software
Engineering R-281578`, **identical bodies**. Both survived dedup, because `same_role()` requires normalised
titles to be **equal** and a trailing requisition number breaks equality. 🔴 **Both also sat below the tally
threshold**, so neither was ever tiered — only the full triage caught it, by eye.

🔴 **The obvious fix is the dangerous one.** Stripping requisition-shaped tokens from titles would merge these
two correctly and would also merge **two genuinely different requisitions posted under one title** — which is
routine at large employers, and is how a real vacancy disappears. **That is the same false positive the
location dedup already taught**, where intersecting on a shared country would have merged Dublin with Cork.

**So it needs a test before a fix**, and the test is the false-positive case: two postings, same title,
different requisition numbers, **different bodies** — these must stay separate. Only merge when the bodies
agree.

🟡 **Note the asymmetry that makes this safe to leave for now**: the failure duplicates a row rather than
hiding one. **A duplicate is visible; a wrongly merged role is not.**

---

### ✅ Settle the budget-ownership question once, instead of seven times — DONE 2026-08-28

**Status: raised 2026-08-26 after the seventh occurrence. Settled 2026-08-28** in one conversation,
written to `vault/wiki/Budget and Commercial Scope.md`, and the framework's standing-gaps table now
points there instead of restating the binary.

🔴 **The finding that made it worth doing: the prior record was true and misleading.** *"Budget / P&L
ownership — confirmed absent"* had survived two reconfirmations. **The budget in that organisation is
denominated in headcount rather than money** — so he builds the case for it, produces the estimates
that become it, and decides its shape, while correctly answering *no* to every question about owning
one. **A confirmed-absent gap is not a finished one.**

🟢 **What it changed:** not the seven roles — a bank asking for accountability for budgets still means
money. It changed which REQUIREMENTS he clears outright, because *capacity planning* and *resource
planning* had been conceded alongside budget ownership for arriving in the same sentence.

**Seven roles have now been decided by the same gap** — Citi Custody, Ingenio Global, AXA XL, EPAM, Slalom,
Mastercard VP and Mastercard Disputes. Each was scored, written up and reasoned about independently, and
**each reached the same conclusion by the same route.** *"Own the business case"*, *"budgets and commercial
performance"*, *"evaluate investment opportunities"*, *"influence investment planning"*.

🔴 **Seven separate assessments of one unresolved fact is waste**, and it will keep happening — it is one of
the most common phrases in director-level postings.

**What needs settling, once, on a page:**

- **What has he actually owned?** Forecasting, headcount, vendor spend and business cases contributed to are
  all different things, and *"no P&L"* may be flattening a more useful answer.
- **What does the phrase mean in practice at this level?** It appears in postings where the holder plainly
  does not own a P&L, so it is partly boilerplate — and partly not.
- **What is presentable without overclaiming?** 🔴 **This is a claim that would sit in front of a recruiter,
  so it is exactly the kind `/career-lint` flags as unverified doing external work.**

🟢 **The output is one wiki page, and then the scoring notes point at it** instead of re-deriving it.

---

### ✅ `--reset` is global even when the run is not — FIXED 2026-08-27

**Status: fixed by refusing the combination, which is the option this entry called probably right.**

🟢 **`--adapter X --reset` now errors** and names `--reset-adapter` as the flag that means what was intended. **Refused rather than silently rescoped**, because rescoping changes what a destructive flag means for anyone relying on today's behaviour — and doing that quietly is how the next person loses a baseline.

🟢 **And it says what it is about to destroy before destroying it**: *"--reset: forgetting all 6,534 seen role(s), from every source"*. The count was always known at that moment; printing it costs nothing.

🟢 **Verified against the real command that caused it.** `--adapter google --all-open --reset` now exits non-zero with the explanation; the scoped form would keep 6,486 rows and forget 48.

**Original entry:**

**`--adapter google --all-open --reset` wiped the memory of all 6,462 seen roles**, not just Google's. The
flag says *"forget everything seen before"* and means it — but it was typed on a run scoped to **one
adapter**, while testing that adapter, and the scoping of the run does not carry to the flag.

🔴 **The damage is quiet and total.** `seen.json` went from 6,462 entries to 48. Nothing assessed was lost —
the scoring table, the role pages and `vault/postings/` are all outside it — **but the radar's entire notion
of *new* was gone**, and the only way back is a full `--all-open` sweep whose output is, by definition,
entirely "new". One careless flag on a single-adapter test costs a full re-sweep and one meaningless run.

**Two candidate fixes, and the second is probably right:**

| | |
|---|---|
| **Scope `--reset` to `--adapter` when both are given** | Reads naturally — *reset this source* — but it is a **silent change of meaning** for anyone who currently relies on the global behaviour |
| 🟢 **Refuse the combination and make the user say which they meant** | `--reset` with `--adapter` errors, offering `--reset-adapter` for the narrow one. **Nothing silently does the wrong thing, and nothing silently changes** |

🔴 **And whichever is chosen, a destructive flag should say what it is about to destroy**: *"forgetting 6,462
seen roles"* before doing it, not after. **The count is known at that moment and printing it costs nothing.**

🟡 **Note what worked:** `seen.json` is regenerable state and lived in `vault/state/`, so this was recoverable
by re-running rather than being data loss. **The boundary did its job even though the flag did not.**

---

### ✅ `quotes.py` — DIAGNOSED AND GATING, 2026-08-27

**Status: 0 of 45 pages failing, wired into `doctor.py` and `pipeline.py`.**

🟢 **The 28 were diagnosed and none of them was a fabricated quote.** They were three things:

| Cause | Share | Fix |
|---|---|---|
| **The regex paired one quotation's closing mark with the next one's opening mark**, returning whole paragraphs of our own commentary as quotations | **14 pages** | Require emphasis markers around a quotation |
| **Quotations of the USER, of our own findings, and of application-form questions** — all correctly absent from an employer's advert | **12 pages** | Two tiers: a blockquote is a claim about the employer and gates; an inline quote is advisory |
| **Two genuine faults** | 2 pages | An employer's typo silently corrected inside a quotation, and Sacha's words quoted without attribution. Both fixed on the pages |

🔴 **And a seventh bug appeared only after the last fix**: quoting the employer's typo faithfully with
`[sic]` broke the match, so **quoting properly was the thing that made the check fail.** Editorial
insertions are now stripped before comparison.

🟢 **Coverage held through all of it**: 45 pages and 323 quotations checked. **Blockquote-only was tried
and checked 17 — the narrowing that made it quiet nearly made it useless, which is the trade to watch.**

**Original entry:**

**Status: built 2026-08-27, advisory, deliberately not wired into `doctor.py` or `pipeline.py`.**

🟢 **The asymmetry it closes is real.** `verify.py` checks an outgoing CV against the wiki, because a model
wrote the CV and a model reviewing its own work shares its failure modes. **But role pages are also
model-written and they rest entirely on quotation** — every score in this system is argued from a line
lifted out of a posting. **Nothing checked the quote**, and the error propagates: a misquote sets a score,
the score enters the shortlist, the shortlist decides where an evening goes.

🟢 **It has already found two genuine faults**: a posting reading *"manage i.t. related risks"* quoted as
*"manage IT related risks"*, and *"Set safe-AI standards **for agentic systems**:"* quoted with those three
words silently dropped.

🔴 **And it reports 28 of 56 pages, which is far too high to gate on.** It was narrowed four times, each on a
real bug in the check found by running it:

| Attempt | Reported | The bug |
|---|---|---|
| First | **69 of 71** | A blockquote's `>` prefix leaked into every multi-line quotation |
| Second | 63 of 71 | Fuzzy filename matching paired Guidewire's page with **Yuno's posting** |
| Third | 5 of 6 | A URL regex requiring `https://` found no URLs on the pages it was written to check |
| Fourth | 49 of 56 | A similarity ratio **cannot see an elision**, which is the commonest fault by far |
| Now | **28 of 56** | Unexplained |

🔴 **What is left is diagnosis, not more tuning.** The remaining 28 are a mix of at least three things and
nobody has separated them: **genuine misquotes**; pages quoting an **employer's own posting** where only the
aggregator's truncated copy was archived; and postings that **changed between being archived and being
read**. **Until those are told apart, a gate here would fail honest work about half the time — and a check
that does that is switched off in a week, which costs more than never having built it.**

🟡 **The likely fix for the second class** is to archive the employer's own text at score time rather than the
aggregator's, which `build-application` already does at packaging time. **That would shrink the problem
before any more tuning of the matcher.**

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

**Deliberate scope decision, recorded in `SCHEMA.md`.** Not covered: interview preparation, offer
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

### ✅ Oracle does not reject an unrecognised site. It widens the search — DETECTED AT RUN TIME 2026-08-28

**Status: found 2026-08-25 while building the source check, against three live tenants. Still not
fixable — Oracle offers no way to make it fail. 🟢 But detected where it matters, 2026-08-28.**

**`probe()` had caught it since the day it was found, and only when somebody ran `sources_check.py`.**
A real radar run never asked — so the one place the answer changes what you are looking at was the one
place it was not checked. `fetch()` now runs the same two-count comparison, **once per tenant rather than
per employer**, and says so on the run.

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

### 🟡 No application tracker — MOSTLY BUILT, corrected 2026-08-28

**This entry said status lives in the scoring table "with no dates, no next action, and no follow-up
cadence", and that a user with five live applications "has no prompt to chase anything". Two thirds of
that is no longer true**, and it was recommended as work before anyone checked.

🟢 **`tools/outcomes.py` built the cadence.** It reads submitted dates out of the table, asks after **7**
days and records silence as an outcome after **21**, and it is the `outcomes` stage of `pipeline.py` — so
a run is not finished while something is owed. On the vault it was written against it currently names
three applications at 7 days.

🔴 **What is still missing is the narrow part: a next action per application.** *"Chase"* and *"prepare
for a call on Thursday"* are different states and the table cannot tell them apart.

🟡 **Kept as a lesson, not just an item.** This is the second backlog entry to be recommended after the
thing it describes was built — which is why the rule is *check a backlog entry still applies before
acting on it*, and why entries now carry the date they were last checked.

### 🟡 No way to LOOK at the scored roles — a browser dashboard

**Added 2026-08-28 at Sacha's request.** *"Build a HTML UI where a user can view all the scored roles in a
browser and additional information. Create a dashboard?"*

**The problem is real and it showed up twice this week.** `Role Scoring Framework.md` now holds ~96 rows
across several tables, and answering *"what are my top 20?"* took a purpose-written script — which then
turned out to be reading **78 of 96 rows**, because the row regex could not see a decorated first cell.
🔴 **A table nobody can sort is a table whose ordering nobody checks.**

**Obsidian renders the markdown but will not sort, filter or total it**, and the questions that actually
get asked are all sorting questions: *what is unapplied above FIT 12 · what is remote · what clears the
floor · what have I not heard back on.*

#### The design constraints, which are most of the work

| | |
|---|---|
| 🔴 **One self-contained HTML file, no server, no CDN** | Same rule as `templates/cv.html`: needs nothing installed and behaves identically everywhere. Inline the CSS and JS; sorting and filtering are a few dozen lines of vanilla JS over a table that is already in the DOM |
| 🔴 **Generated into `vault/state/`, and it must be safe to delete** | It is a VIEW. Regenerate it from the vault; never let it become a place where anything is stored |
| 🔴 **It contains the user's entire search and must never be committed** | `vault/**` is gitignored and `test_boundary.py` enforces that. **Do not put it anywhere else**, and say plainly in the page that it is local |
| 🔴 **Read-only, and it must look read-only** | The moment a score can be edited in the browser there are two sources of truth and the markdown loses. **No inputs, no buttons that write** |
| 🟡 **N·D·E, FIT, LIFE and SEC all visible per row** | Sacha's standing rule: a total on its own hides which dimension is doing the work. Link each row to its role page and its archived posting |
| 🟡 **Show what is stale** | Submitted with no outcome past 7 days, unreviewed scores at FIT 10+, missing posting URLs. The pipeline already computes all of it |

#### 🔴 What would make it a mistake

- **If it re-derives anything.** It must read the same parser the checks read — `tools/scores.py` — or it
  becomes a second, disagreeing implementation of the table. **The top-20 bug is exactly what that looks
  like**, and it happened in a throwaway script that lived for ten minutes.
- **If it needs regenerating by hand to be trusted.** Stamp the generation time in the page and have
  `pipeline.py` report when it is older than the table it describes.
- **If it grows into an application tracker** without the entry above being done properly first.

### Nothing has been run end-to-end from a cold start

`/career-init` on an empty repo has never been exercised. The pieces work individually; the bootstrap is
untested.

---

## 🟢 Rules learned the hard way

**Moved to [`docs/LESSONS.md`](docs/LESSONS.md) on 2026-08-26.** They are settled rather than
outstanding, and a backlog is a list of work still to do. 🔴 **They are still binding** — the point of
recording them was that a later change should not quietly reverse a fix that cost something to find.

## ✅ Done — bodies removed 2026-08-26, kept in git

**This file's own rule: *delete an item when it is done — the log of what changed lives in git*.**
29 completed entries were carrying **1095 lines, 39% of the file**, and were not being deleted.

🔴 **Titles are kept and the reasoning is not, on purpose.** The reason someone needs this list is to
avoid re-implementing finished work; the reason someone needs the full write-up is rarer and git has
it. **To read one:**

```bash
git log --oneline -S'a phrase from the title' -- BACKLOG.md
```

🔴 **Then read the version BEFORE that commit** — `git show <sha>^:BACKLOG.md` — because the commit the
search finds is usually the one that *removed* the text.

- ✅ `migration/` — `migrate.py` BUILT 2026-08-25
- ✅ A radar run was twenty minutes of network wait — 1201s → 233s, BUILT 2026-08-25
- ✅ Workday reads the board once and filters locally — BUILT 2026-08-25
- ✅ The politeness delay was being paid on requests that never happened — FIXED 2026-08-25
- ✅ Templates evolve and vaults do not — `template_drift.py` BUILT
- ✅ Nothing answered "am I set up?" — `doctor.py` BUILT
- ✅ And one contradiction that was not on the list at all — FIXED
- ✅ The radar's SIGNAL number read like a framework score — MADE NON-NUMERIC
- ✅ The salary bonus in the radar tally measured the adapter, not the role — REMOVED
- ✅ Line-wrapped wikilinks silently do not resolve — CHECK BUILT
- ✅ Aggregator postings are truncated, and the system read them as the job — FIXED AT THE RIGHT MOMENT
- ✅ The verifier conflated a percentage with a count — FIXED
- ✅ A nearby transit stop is not a commute — KNOWN LOCATIONS TABLE SHIPPED
- ✅ "Not recorded" and "recorded as absent" are indistinguishable to a search — TOOL BUILT
- ✅ "Remote" is country-scoped, and the filter was waiving exclusions on the word — FIXED
- ✅ Greenhouse yield is low — PREFILTER FIXED, and it was a bug not a tuning problem
- ✅ The deterministic layer had no tests — BUILT, and it found three live bugs
- ✅ The system modelled "leave" and "stay" and missed the third option — NOW A ROW IN THE TABLE
- ✅ Scores had no personal baseline — THE CURRENT JOB IS NOW ROW ONE
- ✅ The oversight layer's independence was a comment in a config file — ENFORCED
- ✅ A shared employer registry — BUILT AND WIRED IN
- ✅ The personal-data heuristic fired on this repo's own subject matter — SCOPED
- ✅ Ghost jobs are 20-33% of listings and nothing here checked — BUILT
- ✅ Bound the expensive pass to the delta — BUILT, and the premise was wrong
- ✅ The boundary — BUILT. Everything the user owns is under `vault/`
- ✅ Oracle Cloud Recruiting adapter — BUILT
- ✅ Employer preference and exclusion lists — BUILT
- ✅ Source coverage is geography-dependent — `sources_check.py` BUILT
- ✅ The search only ever covered the last seven days — `--all-open` BUILT

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
