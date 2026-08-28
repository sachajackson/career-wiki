# Shipped

**What was built, and what building it taught.** [← back to README.md](../README.md)

**Split out of [`BACKLOG.md`](../BACKLOG.md) on 2026-08-28**, because a backlog is a list of work
outstanding and none of this is outstanding. It is kept rather than deleted for one reason: **most of
these entries record a defect that was found by shipping the opposite**, and the reasoning is worth more
than the diff.

🔴 **This file is not the changelog and it is not the spec.** `git log` says what changed;
[`docs/DESIGN.md`](DESIGN.md) says how a thing works now. **This says why it was built, and what was
wrong before it existed** — which is the thing that gets lost, and the thing that stops a later change
quietly reintroducing the same fault.

🟡 **Entries that were only PARTLY finished keep a stub in the backlog** naming what is still open. The
record of the finished half lives here.

---

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

---

## ✅ What shipped, 2026-08-26

**Two of the three. Both were dry-run against the repo before being written**, and both were then
verified by putting the real leaks back and watching them fail.

| Check | Catches |
|---|---|
| 🟢 **No template carries a real organisation** | A capitalised multi-word phrase in a non-comment JSON value. `Northwind Traders` fires; `Acme Corp` does not |
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

---

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

---

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

---

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

---

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

---

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

---

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
`Careers` in turn is honest — **one employer's site was recovered that way.** Oracle returns 200 for
anything, so guessing there would manufacture a wrong entry that looks right. **The asymmetry decides
where probing is allowed.**

---

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

---

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

---

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


---

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


---

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


---

### ✅ The posting is the evidence, and it disappears — BUILT 2026-08-28

🟢 **`tools/radar/archive_posting.py`** fetches the employer's own copy and archives it; runbook step 7
names the command. **Record in [`docs/SHIPPED.md`](docs/SHIPPED.md).**


---

### 🟡 Example and template files are a leak vector — the seven are now one

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

🟢 **The seven were cleared on 2026-08-28.** Every one was avoidable: a test asserting that REAL
organisations get flagged had named three actual employers to prove it, a registry fixture used a
live entry, and two measurements named the board they were taken from. **All now fiction**, and the
substring-collision test that needed two names sharing a prefix uses *Stateline Capital* and
*Statesman Bank*.

🟢 **The registry was settled on 2026-08-28 by seeding it.** It held 18 employers whose composition
reflected who one person had looked up; it now holds **24**, and the added six — Airbnb, Coinbase,
Duolingo, Pinterest, Spotify, Vercel — were chosen to be recognisable and unconnected to any one
search. **Every endpoint answered and every canary was present** on a full `registry_check.py` run.

🔴 **Every addition was verified BY CONTENT, never by name**, and one probe shows why that rule is
not ceremony: `greenhouse/wise` answers with 21 roles and is **not Wise** — it belongs to *National
Teachers Associates, a subsidiary of Horace Mann*. **A token guessed from a company name is a
different company's board that looks identical from the outside**, and `add_employer.py` refuses to
write one without a human saying so.

🟡 **What seeding does and does not fix.** The three sensitive entries are still there — they are
real ATS facts and removing them would break the coverage they provide. **What changed is the
inference**: three names among 24 household ones read as a resource, where three among 18 read as
somebody's shortlist. `doctor` still reports the count rather than excluding the file silently.

🟡 **The old wording, kept because the reasoning still applies:** All name a WATCHED employer, in ATS-mapping
code and in findings — `ats_registry.json` maps employers to their ATS and is contributed back
deliberately, which is a public fact about a company. **Whether being seen to watch an employer
matters is the user's call**, so the check WARNs and names files rather than gating.

---


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


---

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


---

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


---

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


---

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

---

## ✅ CLOSED 2026-08-28 — and it was two operations, not one

**Both prefix lists now carry `migrate`, and the check is mechanical rather than prose.**
`tools/tests/test_log_prefixes.py` compares `SCHEMA.md` and `templates/log.md` to each other and to the
operations the schema documents.

🔴 **Building it found a second instance immediately: `market standards` had the same gap**, logging as
`research` with no prefix documented anywhere. **So the drift was never about `migrate` — it was the
absence of anything comparing the lists**, exactly as the entry predicted when it said option 2 was
better than option 1.

🟢 **The false-positive case the entry named was the whole design.** A real log carries `tools`,
`framework` and `correction` — one user's words for one user's work. **The check reads only the two
shipped files and never opens a vault**, and there is a test asserting those three must NOT be added to
the shipped list.

🟡 An operation whose prefix is not its name is declared, not guessed: `market standards` → `research`.


---

### 🟡 Employer research — two details still outstanding

🟢 **Built 2026-08-24 as `build-application` Step 0.4.** The record and the original design are in
[`docs/SHIPPED.md`](docs/SHIPPED.md). **Two things from that design did not make it:**

- **`stale_after` on a company page.** Financial results age in months, and a reused company page is
  exactly the artefact that rots invisibly. **Twelve weeks is the sensible default.**
- **A scope rule.** Employer due diligence has a natural size and **padding it produces noise that gets
  skimmed**, which is worse than a shorter page that gets read.

## ✅ CLOSED 2026-08-28 — and one of the two is now a check

**`stale_after`, twelve weeks.** Instructed in `build-application` Step 0.4, **and enforced by `doctor`**,
because instructing it was what failed the first time: **five of seven company pages had none.**

🔴 **The reason it needed a check rather than a reminder: `/career-lint` reports an EXPIRED page and
cannot report one that never claimed an expiry.** An undated research page is permanently fresh and
permanently wrong — the worst of both, and completely invisible.

🟡 **The false-positive case is the interesting half.** `vault/companies/` also holds the user's OWN
employers — where they worked, not who they investigated. Four of the seven are that, and demanding an
expiry on them would be asking somebody to date their own career. **Scoped by tag, and there is a test
for it.**

**The scope rule** is prose in the skill, and honestly so — it is a judgement, not a threshold. It carries
the measurement (**2,350–4,500 words, 10–15 sections across three real pages**) and the test that decides
inclusion: *would this change whether he applies, what he asks on the call, or what he writes?*


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

## ✅ MECHANISM BUILT 2026-08-28

`build-application` Step 4 reads `repo_link_in_cover_letter` and asks once when it is unset. **The
practice was already right** — the sent letter offers it in the closing, as prose, with no score:
*"If it is of interest, the process I used to assess this role, including the requirement-by-requirement
scoring, is open source at …"* **What was missing was that nothing recorded the decision**, so it was
being made again on every application, which is how something gets added silently.

---

## ✅ `verify-artefact.sh` tested — and it had been broken for days, 2026-08-28

**The only control in the repo that gated everything and was checked by nothing.** It fires on **every
Write and Edit**, and its whole design is that *"the agent does not get to decide whether to check its own
work"*. `install-guard.sh`, sitting beside it, had three behavioural tests. This had one assertion that
the file exists.

### 🔴 What writing the first test found, before the test even ran

**It passed `--wiki "$root/wiki"`, and that folder had moved to `vault/wiki`.** So on every artefact
write:

```
DETERMINISTIC LAYER FAILED on CV.html. Fix these before doing anything else.

no wiki at /…/career-wiki/wiki
```

🔴 **`verify.py` exited 1 having indexed nothing — 0 pages where there are 31, 0 figures where there are
399.** The hook then announced a failure of a layer that never ran.

🔴 **That is worse than the check being absent.** A control that fails for a reason unrelated to the
document trains whoever reads it to ignore the output — and the message gave no way to tell the two
apart.

🟢 **The proof is a test that fails against the old version:** a CV containing the fabricated figure
`9,412` produced `DETERMINISTIC LAYER FAILED` **without the number appearing anywhere in the output**,
because nothing had looked at it. It appears now.

### The rule it broke, which the repo already had

**"Paths come from `tools/lib/paths.py`, never from string literals."** `verify.py` defaults `--wiki` to
`paths.WIKI` and was correct. **The one place that broke the rule was a shell script nothing ran** — and
`test_boundary`'s stale-path check already scanned `.sh` files; it simply did not know that name had
moved. It does now.

**Nine behavioural tests**, covering what it skips (no path, ordinary text, DOCX left to `/pre-submit`),
the wrapped-link check, the missing `application.json` message, a fabricated figure, and the regression —
asserted on **behaviour**, by pointing the hook at a vault in the environment and checking it indexed
*that* one.


---

## ✅ The watch list had two incompatible schemas — FIXED 2026-08-28

**Found the moment somebody first tried to use it.** `watch` had been empty for the life of the repo, and
it was unusable in **both** directions:

| Shape | `employers.excluded()` | `registry.resolve()` |
|---|---|---|
| `watch: ["Name"]` — `registry.py`'s own docstring | 🔴 **AttributeError** — it reads entries as dicts | 🟢 routes it |
| `watch: [{...}]` — what `templates/settings/employers.example.json` ships | 🟢 fine | 🔴 **skipped** — `not isinstance(name, str)` |

🔴 **So a config written from the template named employers and watched nobody, silently**, and one written
from the docstring crashed the filter. **There was no correct way to write it.**

🟢 Both readers accept both shapes now, with the object canonical — it is the only one that can carry a
route and an `avoid_divisions` list. Five tests, including the comment-strings-in-a-JSON-array case.

🟡 **The lesson is about empty containers.** Nothing was wrong with either file in isolation; they had
simply never been asked to agree. **A feature nobody has used is not a feature that works** — it is one
whose first user finds the bug.



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

### 🟡 The repo link in a cover letter — mechanism built, one answer owed

🟢 **Built 2026-08-28.** `build-application` Step 4 now reads `repo_link_in_cover_letter` from
`vault/settings/profile.json` — `ask` · `always` · `never`, **absent means ask** — and records the answer
so it is not re-decided every application. The reasoning and the wording that worked are in the skill;
the record is in [`docs/SHIPPED.md`](docs/SHIPPED.md).

🔴 **The URL question is settled and was the smaller half.** Deleting and recreating under the same name
keeps `github.com/<owner>/<repo>` working, so the letter already sent stays live. **What was never
settled is the policy**, and the setting is deliberately unset: *never invent a value.*

🟡 **The answer is owed by the user, not derivable.** They used the link once, which says *yes for that
role* — it does not say *always*, and the entry's own rule is that it must be offered rather than
assumed. **`settings_drift.py` reports the missing key until it is answered.**

### 🟡 Everything after the submit button — the rest of it

🟢 **The interview pack shipped 2026-08-25** as `build-application` Step 6.2; the design is in
[`docs/SHIPPED.md`](docs/SHIPPED.md). **The rest of the entry stands** and is the section below.

### The rest of what happens after the submit button

**Deliberate scope decision, recorded in `SCHEMA.md`.** Not covered: interview preparation, offer
evaluation and negotiation, follow-up cadence, rejection debriefs.

**Interview prep is the largest and the wiki is already sitting on everything it needs** — every claim with
a verification status, the role page's pre-mortem which is the interviewer's objection list, the gaps the
cover letter conceded, and the user's own phrasing preserved verbatim. **A STAR bank built from
human-verified claims only would be the single highest-value addition.**

Negotiation is second: the framework already holds the salary floor, the anchors and the priced-vs-hard
veto distinction, so **comparing two offers is a scoring problem it can already do.**

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

### 🟡 A next action per application

🟢 **The cadence is built** — `tools/outcomes.py` asks after 7 days and records silence at 21, and it
gates `pipeline.py`. Record in [`docs/SHIPPED.md`](docs/SHIPPED.md).

🔴 **What is missing is narrow:** *"chase"* and *"prepare for a call on Thursday"* are different states
and the table cannot tell them apart.

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
