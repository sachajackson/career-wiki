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

🔴 **And this file is FUTURE WORK ONLY — restructured 2026-08-28, from 1,917 lines to about 500.** Three
other kinds of content had accumulated here because a backlog is the file that happens to be open while
the work is happening. They now have homes:

| | |
|---|---|
| **What was built, and what building it taught** | [`docs/SHIPPED.md`](docs/SHIPPED.md) |
| **How a thing works now — schemas, contracts, load-bearing paths** | [`docs/DESIGN.md`](docs/DESIGN.md) |
| **What going wrong taught, settled and still binding** | [`docs/LESSONS.md`](docs/LESSONS.md) |

🟢 **And it is checked, not just written.** `test_backlog.py` fails the build if a heading here
announces completed work, and `BACKLOG.md` is no longer exempt from the two checks it used to be
exempt from — stale paths and the replaced scoring model. 🔴 **Both exemptions rested on this being
*a dated record of what was done*, which it no longer is**, and three sweeps out of this file each
found rot the moment the text landed somewhere a check could see it.

🔴 **The reason this matters, measured:** settled reasoning was accumulating here at roughly **250 lines a
day**, and real outstanding work was buried under it. **A lesson in a backlog reads as a task; a design
reads as a proposal.** Where a job is half done, **the finished half goes to `SHIPPED.md` and only the
remainder stays here.**

**Personal follow-ups are not less important — they are differently located.** Losing them is a real risk,
which is why every wiki page carries an *Open questions* section for exactly this purpose.

---

## 🔴 BLOCKING PUBLIC LAUNCH — republish the repository with clean history

**Raised 2026-08-28. Nothing else on this page is more important, and it is the one item with a deadline
set by an external event: the day this repo is announced to anybody.**

🔴 **Three commits in the public history contain material about the person using the system**, which the
charter directly above says must never be here:

| Commit | What |
|---|---|
| `bea1570` | **An avoid list** — an excluded division, its parent, and a second employer, in `tools/radar/employers.py` and its test |
| `330be61` | **A home county**, in a test asserting that home counties must not be in public tests |
| `7d82b1c` | **A real full name**, in a wikilinks fixture |

🟢 **The working tree is clean of all three as of 2026-08-28** and the checks that would have caught them
now exist — `doctor`'s `settings leak`, and the example-purity rule in `test_boundary.py`. **The tip is
fine. The history is not.**

### 🔴 Why a force-push is not the fix, and this is already recorded

**A history rewrite removes a commit from the branch, not from the server.** Verified on this repo, not
assumed: an earlier bad commit was rebased away and force-pushed within 25 minutes, and **the orphaned
commit stayed fetchable by its SHA**. For anything genuinely sensitive, the rewrite is not the remedy.

### 🟢 The remedy, and the constraint most people miss

**Delete the repository and recreate it under the same name, then push a clean history.** Deleting the
repo takes the old SHAs with it, which a force-push does not.

🔴 **The constraint: the repository URL may already be in a submitted application.** It was — a cover
letter sent 2026-08-24 carries it. **Deleting without recreating turns a live application's link into a
404 for a recruiter.** Same name, so the link survives; a few minutes' gap rather than an open-ended one.

🟡 **Exposure at the time of writing was low and that is not the argument.** Public 7 days, 0 forks, 0
stars. **The argument is that the charter is absolute** — nothing about the person, ever — and a
low-traffic breach of it is still a breach.

**Requires the `delete_repo` scope, which the working token deliberately does not have.** It is the
user's action, not the agent's.

## 🟢 Picking this up cold? Read this first

**A list this long is not a plan.** Three things about their state, then an order.

*(This said "twenty-five items" and had drifted — there are 27 open now. Counts written into prose go
stale silently, which this file already has an entry about: "The test count was written in three places
and wrong in all three". So the number is gone rather than corrected.)*

### 2. Do the cold-start run before building anything else

**It is the last item in this file and it should be the first thing done.** Half of what follows is
speculative — *designed, not built* — and a real run from a clean clone will re-rank it and add items that
are not here.

🔴 **And whoever wrote this system is the worst possible person to run that test.** They know every answer,
will fill gaps unconsciously, and will read ambiguous instructions correctly because they wrote them.
**Use a CV that is not theirs, answer only what is asked, and keep a note of every point where they had to
help it. That note is the real backlog.**

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

## 🟡 Gaps — things the system does not do yet

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


## What already exists, in the wrong shape

🔴 **In one week of real use, five employers' endpoints were found by hand and scattered across five
places** — two on a preferences page, one on a role page, one in a company research note, and **one used
and never recorded at all.**

**That is the registry, already built, in the wrong shape.** It is the strongest argument that it should be
one file.

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

### 🟡 Employer research — two details still outstanding

🟢 **Built 2026-08-24 as `build-application` Step 0.4.** The record and the original design are in
[`docs/SHIPPED.md`](docs/SHIPPED.md). **Two things from that design did not make it:**

- **`stale_after` on a company page.** Financial results age in months, and a reused company page is
  exactly the artefact that rots invisibly. **Twelve weeks is the sensible default.**
- **A scope rule.** Employer due diligence has a natural size and **padding it produces noise that gets
  skimmed**, which is worse than a shorter page that gets read.

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

## 🟢 Rules learned the hard way

**Moved to [`docs/LESSONS.md`](docs/LESSONS.md) on 2026-08-26.** They are settled rather than
outstanding, and a backlog is a list of work still to do. 🔴 **They are still binding** — the point of
recording them was that a later change should not quietly reverse a fix that cost something to find.

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
