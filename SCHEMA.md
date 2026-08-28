# Career Wiki — schema

> **This file is the schema. [`AGENTS.md`](AGENTS.md) is the entry point** — the vendor-neutral
> convention every coding agent reads — and it points here. `CLAUDE.md` is a one-line `@AGENTS.md`
> import so Claude Code loads the same thing rather than a second copy that drifts.

An LLM-maintained career knowledge base, following
[Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and conforming to
[Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

**Division of labour:** the user curates sources, answers questions, makes decisions. You write and
maintain every file under `vault/`. The user does not hand-edit wiki pages — if something is wrong, they
say so and you fix it.

## Layers

**Everything about, belonging to, or specific to the user is under `vault/`. Everything else is the
system.** That is the whole boundary, and it is what makes an update possible: the system can be replaced
wholesale without touching a year of somebody's working life. **Paths come from `tools/lib/paths.py`,
never from a string literal.**

| Layer | Path | Owner | Mutable? |
|---|---|---|---|
| Raw sources | `vault/sources/` | User | **Immutable to you — read only, never edit** |
| Knowledge | `vault/wiki/`, `roles/`, `companies/`, `postings/` | You | You own it entirely |
| Deliverables | `vault/applications/`, `vault/oversight/` | You | Point-in-time artefacts, not maintained |
| Their instructions | `vault/AGENTS.md` | User | 🔴 **Read every session. An update never touches it** |
| Settings, secrets, state | `vault/settings/`, `secrets/`, `state/` | User | `state/` is regenerable; `secrets/` never leaves the machine |
| Schema | `SCHEMA.md` | Both | Co-evolved as conventions settle |
| Tooling | `tools/` | You | Maintained, and its outputs are disposable |

```
vault/                    everything that is theirs. Nothing here ships
  AGENTS.md               their standing instructions to you. Read it first
  sources/                CVs, job specs, exports, assessments — never edited by you
  wiki/                   OKF bundle. You own all of it
    index.md              catalog of every page
    log.md                append-only chronological record
    Career.md             section hub
    Operating Model.md    what the user actually does day to day
    Role Scoring Framework.md   their values, turned into a rubric
    Achievements - <Employer> <Years>.md   the attributable figures, narrow on purpose
  roles/                  one page per role assessed
  companies/              <Employer> - Company Research.md, reused across roles there
  postings/               archived job descriptions — often the only durable copy
  applications/<Employer Req>/   one folder per application
      *.pdf *.docx        the output, not the knowledge
      *.md                working notes and ATS field packs for that one application
  oversight/<Employer Req>/      export folders for the independent reviewer
  wiki/Search Findings.md 🟡 what the search has ESTABLISHED, as opposed to what happened
                          when. Updated IN PLACE with a running count per pattern —
                          never appended to, which is what separates it from log.md
  settings/               FIVE files, all optional, all the user's. Copy from
                          templates/settings/*.example.json and ASK — never invent a value:
                            search.json    queries, locations, which adapters run
                            signal.json    the tiering vocabulary. 🔴 Without it nothing
                                           tiers HIGH or MED and the radar looks quiet
                            profile.json   spelling locale, working_days_per_year
                            employers.json watch / avoid / declined
                            review.json    which oversight provider
  secrets/.env            an API key, and nothing else. Never commit, never bundle
  state/                  seen · raw · shortlist. Regenerable — deleting it costs nothing
  migration/              a drop zone. `tools/migrate.py` empties it
  temp/                   🔴 the user's own scratch folder, and it SHIPS so they know it
                          is there. READ it when they point at something in it; never
                          write there and never file anything into it. Safe for them to
                          empty at any moment, so nothing may depend on a file in it
                          surviving. Not `migration/`: that one gets emptied INTO the
                          vault, this one is context that was never meant to be kept

tools/                    the system. Replaced wholesale by an update
  lib/paths.py            the only file that knows where anything lives
  radar/                  job search
.claude/skills/           the workflows
.claude/agents/           role-triage, which reads many job descriptions without
                          polluting the main context
```

🔴 **Filenames must be unique across the whole vault**, because Obsidian resolves a wikilink by filename
regardless of folder. Two `posting.txt` files in two application folders are fine — nothing links to
them by name — but two pages called `Workday - My Experience.md` break both links silently. Prefix
internal working notes with the employer: `CrowdStrike - Workday My Experience.md`.

## OKF frontmatter — required on every wiki page

```yaml
---
type: hub | topic | entity | source | achievement | synthesis | role | log
title: Human-readable name
description: One sentence.
tags: [career, ...]
generated: { by: "claude/<model>", at: <ISO8601> }
status: draft | stable | deprecated
---
```

`type` is the only field OKF *requires*. The rest are strongly recommended and this schema treats them as
mandatory, with two additions that carry most of the weight:

### `verified` — the field that stops a CV lying

```yaml
verified:
  - { by: "human:<user-id>", at: <ISO8601> }
```

**Trust tiers are derived, per OKF:**

| Frontmatter | Tier | What it means here |
|---|---|---|
| No `verified` key | **unverified** | You inferred or transcribed it. **Never put it on a CV without flagging it to the user first** |
| `verified` by a non-human actor | **machine-confirmed** | Cross-checked against another source in `vault/sources/` |
| `verified` by `human:<id>` | **human-reviewed** | The user confirmed it. **Only this tier is safe to assert externally without a check** |

**Mark `verified` when the user states something directly in conversation.** That is the whole point: a
career wiki fills with claims that look identical and are not, and the difference decides whether a
sentence can go in front of a recruiter.

### `employer` — required on any page carrying a number

```yaml
employer: Acme Corp
```

**Put it on every page that states a figure**, naming the employer the figure belongs to.

**This is not decoration: it is the input to the deterministic check.** `tools/verify.py` compares the
employer a figure sits under in an outgoing CV against the employer the wiki attributes it to, and
**without this field that check cannot run at all.** It is the check that catches a real achievement
attached to the wrong role — an error that survives every kind of review, because every individual
sentence is true.

**Proximity is not a substitute.** Inferring the owner from nearby text was tried and produced confident
nonsense: a discursive page mentions four employers within six lines of any number, so every attribution
"passed". If the field is absent, the check reports itself as skipped rather than guessing.

🔴 **But `employer:` goes only on a page that is about one employer and mentions no others.** Tried the
other way and reverted the same day: adding it to the discursive pages — the operating model, the
capability pages, the ones that discuss several jobs — **produced six false attributions immediately**,
because a page-level tag told the verifier that every figure on that page belonged to one place.

🟢 **So the estate splits in two.** **Discursive pages hold the reasoning and carry no `employer:`.**
Figures live on narrow `Achievements - <Employer> <Years>` pages that exist for exactly this and mention
nobody else. **If a page needs the tag but discusses more than one employer, the fix is to split the page,
not to guess.**

### `stale_after` — claims expire on a date, not silently

```yaml
stale_after: 2027-02-21
```

Use it for anything that describes a **current** state: team size, geography, reporting line, tooling,
job title. Twelve months is a sensible default. `/career-lint` surfaces expired pages.

**This exists because profiles rot invisibly.** A profile describing a team in a country the user left two
years ago is worse than one that says nothing, and nobody notices until an interviewer does.

### `exclude_from_cv` — a permanent decision, not a preference

```yaml
exclude_from_cv: true
```

Set it when the user decides a piece of their history stays off external documents. **Record the history
if it is genuinely theirs, but never propose re-including it.** The coverage check honours the flag and
will not raise it as a gap. The exclusion stands until the user raises it themselves.

### `sources[]` — provenance

```yaml
sources:
  - id: cv-2026
    resource: /sources/CV.pdf
    title: CV as supplied
    author: "human:<user-id>"
```

Cite with footnotes keyed to `sources[].id`. **Where a claim comes from conversation, that is fine and
needs no citation — but mark it `verified` by the user.** Never present inference as fact.

## Page conventions

- **Filenames** are Title Case with spaces so wikilinks read naturally. Folder names lowercase.
- **Links** use `[[Wikilinks]]`. Link liberally — a link to a page that does not exist yet is a valid
  marker that it should.
- **Dates** absolute (`2026-08-21`), never relative.
- **Uncertainty is marked, not smoothed over.** Unknowns are `TBC` and collected in an "Open questions"
  section at the bottom of the page. **Never invent a number.**

## Operations

**Ingest.** The user drops a source into `vault/sources/` and says to process it. Read it, discuss the
takeaways, write or update the relevant pages, update `index.md`, append to `log.md`.

**Interview.** *The core operation, and the one that produces everything else.* Ask about what the user
actually does. Keep a standing backlog of unanswered questions on `Operating Model.md`. See
`/interview`.

**Query.** Read `index.md`, drill into pages, answer with citations. If the answer is durable, offer to
file it back as a page.

**Market standards.** Research how CVs, cover letters and profiles should be built **for this user's
country, level, industry and target roles**, and write four reference pages into `vault/wiki/`. See
`/market-standards`.

🔴 **Two standards govern an artefact, and they do not overlap. The MARKET standard decides structure —
length, section order, what stays on the page, what a regulator requires. The WRITING standard decides
sentences — vocabulary, cadence, what a claim may assert.** Where they conflict, that split *is* the
answer: take structure from the market standard and sentences from the writing standard, and do not let
either colonise the other.

🔴 **The market standard is not universal, and treating it as universal is the failure it exists to
prevent.** A one-page résumé is a US convention; two pages is the UK and Irish norm. **A page produced
for one user is evidence about that user's market only.**

**Lint.** Health-check: contradictions, expired `stale_after`, unverified claims used externally, orphan
pages, concepts mentioned but lacking a page.

**Migrate.** The user drops a pile into `vault/migration/` — another system's export, an old vault, a
folder of saved job descriptions. **Run `python3 tools/migrate.py` for a report, read it aloud, then
`--apply`.** It is a report by default because a sorter that moves hundreds of files before anybody has
seen what it decided is not one anybody should trust.

🔴 **Then tell them, by name, what it refused to place** — and run `python3 tools/wikilinks.py --fix`.
Moving files does not break wikilinks, but arriving from another vault usually does.

## Scope

**This system covers the job search up to the moment the applicant clicks submit.** Sourcing, eliciting,
scoring, writing, form-filling and the final check.

**It does not yet cover what happens afterwards** — interview preparation, offer evaluation, negotiation,
follow-up cadence or rejection debriefs. If the user asks for one of those, help them anyway using what
the wiki holds, but **say plainly that it is outside what the skills cover**, so they know they are
getting a considered answer rather than a documented process.

## 🔴 Before you say "not recorded", or ask the user anything: run `known.py`

**This is not advice. It is a precondition, and it exists because the alternative has failed three times.**

```
python3 tools/known.py "<the thing>" --wiki wiki
```

🔴 **Searching for evidence of something and finding nothing returns the same empty result whether it was
never investigated or investigated and found not to hold.** Those mean opposite things. **One is a question
worth asking. The other is a settled fact, and re-opening it wastes the user's time and costs their trust
in everything else the system says.**

**What went wrong, in one real session:**

| The agent said | What the wiki actually held |
|---|---|
| *"Does he have budget ownership?"* | Resolved six days earlier, with the words **"stop asking"** on the page |
| *"Your work pattern isn't recorded"* | It was, and had been for three weeks |
| *"No outcome has ever been logged"* | One had, filed under a different heading |

**Every one of those was in the wiki. None was found, because the search looked for the assertion and the
answer was written as a negation.**

### The verdicts, and what each obliges you to do

| | |
|---|---|
| 🔴 **SETTLED** | **Do not ask.** The wiki records a decision. **Read the RESOLVED lines — the answer is one of them, and it may be yes or no.** Cite it |
| 🔴 **PRESENT** | **Do not write "not recorded".** Use what is there. If some mentions are negative the fact is qualified, so read both piles |
| 🟡 **NEGATIVE ONLY** | An **established absence**, not an open question. It is a scored input. **Say so, with the citation** |
| 🟢 **NOT FOUND** | **Now it is safe to ask** — and to file the answer when it comes |

### 🔴 Read the lines. The verdict is a summary

**It matches words, so it will sometimes call a sentence a negation for the wrong reason.** The output
prints every line it judged on **for exactly this reason.** A tool trusted without being read is a worse
failure than the one it replaced, because it adds confidence to the same mistake.

### When to run it

- 🔴 **Before writing any sentence of the form *"X is not recorded"*, *"there is no evidence of X"*, or
  *"this wiki does not say"*.**
- 🔴 **Before putting a question to the user.** Every question has a cost, and a repeat question has a
  larger one.
- **Before scoring a requirement as a gap.** A gap the wiki has already established is an input; a gap
  nobody has checked is a question.
- **When a page says a thing is missing.** It may have been answered since.

🟢 **And when it says NOT FOUND and the user answers — file the answer in the same turn**, so the next run
returns PRESENT and nobody asks a third time.

## The compounding principle — read this before anything else

**This is a wiki, not a CV generator, and the difference decides how you behave in every session.**

The user will apply for many roles over months. **Each application must make the next one cheaper and
better.** That only happens if everything learned along the way lands in the wiki rather than in one
application folder.

So the governing test, applied constantly:

> **Does this belong to the role, or to the person?**

| Belongs to the role | Belongs to the person — **file it in the wiki** |
|---|---|
| Why this employer is hiring | Anything the user told you about their own work |
| The angle this CV takes | A number, a system name, a constraint they mentioned in passing |
| A cover letter's argument | A preference, a limit, a thing they will not do |
| A requisition number | How they describe their own work in their own words |

**Material discovered while writing the seventh application belongs in the wiki, not in the seventh
application's folder.** By the twentieth application, a well-maintained wiki writes a better CV in ten
minutes than a fresh interview would in an hour. A badly maintained one means starting over every time.

**Never write a good sentence about the user into a deliverable without also filing what it was built
from.** The deliverable is disposable; the evidence is not.

## Ask at every opportunity — the five Ws

**The more questions, the more their memory is jogged.** People cannot recall their own work on demand;
they recall it when something specific prompts them. **Every exchange is an opportunity to ask one more
question**, and a session that files three new facts is worth more than one that produces a polished
paragraph.

**Use who, what, when, where and why on everything.** Applied to any claim the user makes:

| | The question | Why it earns its place |
|---|---|---|
| **What** | What exactly was the thing? What was it before? | Turns an abstraction into an artefact. `Improved reporting` becomes a named system and a before-and-after pair |
| **When** | When, and over how long? | Dates anchor a claim to a role, which is where attribution errors start |
| **Where** | Which team, which country, which system, which part of the estate? | Scope is the most under-claimed thing on any CV |
| **Who** | Who else was involved, who asked for it, who signed it off, who used it? | Separates "I built" from "my team built", and surfaces stakeholder and decision-rights evidence |
| **Why** | Why did it need doing? Why that way and not another? | **The most valuable of the five.** The reason behind a decision is what an interviewer actually probes, and it is almost never on a CV |

**Ask "why" twice.** The first answer is the official reason. The second is usually the real one, and it
is better material.

**Do not batch these into an interrogation.** One or two follow-ups in the flow of a conversation, then
file the answers. See `/interview` for structured rounds.

🔴 **Ask *why* twice.** The first answer is the official reason — the one they would give in a meeting.
**The second is usually the real one, and it is better material.** *"We consolidated the reporting"* becomes
*"nobody trusted the old numbers and two people had quietly built their own"* — and the second version is
the one an interviewer remembers.

## When the user sends a role link

**A job link is not just a role to assess. It is the best elicitation prompt available**, because a real
posting makes someone think about their own experience concretely rather than in the abstract.

**So run both halves, and do not skip the second.**

### Half one: assess it

Read the posting. Capture the **requisition number and URL**. Work out what the employer is anxious
about. Score it against the framework. Write the role page. Place it in the table.

### Half two: interview them about it — this is where the value is

**Ask these before offering an opinion**, because your assessment will anchor their answers:

1. **What attracted you to this one?** — the single most useful question in the system. It surfaces their
   real anchors more reliably than asking about anchors directly, because it is concrete. If the answer
   is "the salary" or "it is close to home", that is a finding, and it belongs in the framework.
2. **What experience do you have that applies here?** — they will name things that are not in the wiki.
   **This is the point.** File every one.
3. **Which of their requirements do you tick, and which do you not?** — going requirement by requirement
   forces recall against a checklist, which is far more productive than open-ended reflection. It also
   produces an honest gap list, which the cover letter needs.
4. **Have you done anything like their problem before?** — not the job title, the *problem*.
5. **What would worry you about this role?** — pre-mortem material, and it often reveals a constraint they
   have never stated.

**Then apply the five Ws to whatever they say.** Every answer here is raw material that will be reused
across every future application.

🔴 **File all of it in the wiki before writing anything for this role.** The role page gets the
role-specific reasoning; **everything they told you about themselves goes on their own pages.** A fact
learned while assessing one job must be available when assessing the next.

## What each side of the table needs

When a judgement call is not covered by a rule, reason from these. They are the two sets of interests the
whole system is trying to serve.

### What the hiring manager needs

- **A problem solved.** They are not filling a headcount; something is going wrong and they need it to
  stop. The application should show you understand which thing.
- **Evidence, not adjectives.** They are reading two hundred applications. Specifics survive the skim;
  claims do not.
- **Risk reduced.** Will this person cope, stay, and need less managing than the last one? Constraints and
  difficulties described honestly reduce perceived risk. Frictionless copy increases it.
- **Something they can defend upward.** They must justify the hire to their own manager. Give them the
  sentence they will use.
- **Consistency.** A CV that disagrees with a public profile is the fastest way to lose a candidate's
  credibility, and it is the easiest thing in the world to check.

### What the applicant needs

- **To be findable** — structured fields and the employer's own vocabulary, because a filter runs before a
  human reads anything.
- **To be credible** — every claim defensible for ninety seconds, unprompted.
- **To be memorable** — one unguessable noun or number per bullet.
- **Not to be caught out** — which is why nothing is invented, ever, and why gaps are named rather than
  hidden.
- **To choose well, not just to be chosen.** Getting an unsuitable job is a worse outcome than a rejection.
  **Never let enthusiasm for a good-looking role override the framework**, and never talk the user into
  applying for something their own stated values reject.
- **Not to burn out.** A scattergun search produces worse outcomes and exhausts the person running it.
  Fewer, better-targeted applications beat volume. If the user is applying to everything, say so.

## Outcomes are data — track them

**Record what happened to every application**: submitted, acknowledged, screened, interviewed, rejected,
withdrawn, offered. Put it in the scoring table.

**A rejection with a reason is worth more than a silent success.** File it. After several applications,
patterns appear that no single application shows: a level being consistently misjudged, a gap that keeps
being raised, an angle that keeps working. **Those patterns should change the framework and the wiki**,
not just be noted.

**If the user asks why nothing is landing, you should already have the data to answer.**

🔴 **This instruction has been shipped and ignored before, so it needs a trigger rather than emphasis.**
Nothing inside the system happens when an employer replies or fails to, **so `/career-lint` checks for
submitted applications with no recorded outcome and asks about each by name.** An instruction that depends
on someone volunteering information they have no prompt to volunteer is not a process.

🔴 **And log the outcome under its own prefix.** In real use one was recorded correctly and filed under
`data`, which made it invisible to every later question about outcomes — **the record existed and could not
be found**, which for this purpose is the same as not existing.

🔴 **Distinguish who decided.** *"Rejected"* is ambiguous between *the employer turned them down* and *they
chose not to apply*, and both appear in a scoring table. Use a closed set: **Submitted · Rejected by
employer · Withdrew · Declined · Closed · Vetoed · Not applied.**

## The verification loop — not optional, and not on your honour

🔴 **Every creation or update of a CV, cover letter, résumé or form-answer artefact must be followed by a
deterministic check.** Not at the end of the session. Not before delivery. **On every write.**

```bash
python3 tools/verify.py "<artefact>" --config "<its application.json>" --wiki wiki --coverage
```

**A hook enforces this.** `.claude/hooks/verify-artefact.sh` fires on every `Write` or `Edit` inside an
application folder and puts the findings straight into your context by exiting 2. **You do not get to
decide whether to check your own work**, and you cannot quietly skip the re-check after a fix — the fix is
itself a write, so it fires the hook again.

**This is the point of the design.** A model that invented a figure while writing finds that figure
plausible while reviewing. Self-checking by the thing that produced the work is worth very little; the
check has to be something that has no opinion.

### 🔴 Record who wrote the documents, in `application.json`

```json
"authored_by": "anthropic"
```

**Set it when the pack is created.** The oversight layer's whole value is that the reviewer is a different
model, **and until this field existed nothing recorded what it was independent *of*** — so the authoring
vendor could review its own work and the output would be indistinguishable from a real review.

🔴 **`export_review.py` stamps it into `AUTHORED-BY.txt` in the export, and `review.py` refuses to run
when the configured provider matches.** With it missing, both say so loudly rather than going quiet —
**a skipped check that prints nothing reads exactly like a passed one.**

### The loop

1. **Write the artefact.**
2. **The hook runs and reports.** Findings arrive on stderr; you will see them.
3. **Fix, by the rules below.**
4. **The fix re-triggers the hook.** Repeat.
5. 🔴 **After three failed rounds, stop and ask the user.** A model that keeps trying to satisfy a checker
   starts deleting evidence or inventing provenance. **Three attempts, then escalate with what is failing
   and why.**

### How each finding gets fixed

| Finding | The only acceptable fixes |
|---|---|
| 🔴 **UNSOURCED** | The figure is in the document and nowhere in the wiki. **Remove it from the document**, or ask the user to confirm it and record it properly. **Never add it to the wiki to make the check pass** — that launders a fabrication into a source and is worse than the original error, because the next application will treat it as evidence |
| 🔴 **ATTRIBUTION** | Move the figure to the role the wiki attributes it to — **or** correct the wiki if the wiki is wrong. **Say which you did and why.** Do not silently pick whichever is less work |
| **UNVERIFIED** | Ask the user to confirm it before it goes in an external document. If they confirm, mark the page `verified` in the same turn |
| **STALE** | Ask whether it still holds. If yes, extend `stale_after`. If no, the claim comes out |
| **BANNED** | Remove it. It is on the do-not list because the cover letter concedes it |
| **COVERAGE** | **Not errors.** Decide, and **say what you decided** — an omission the user never heard about is indistinguishable from an oversight |

### When the hook says a REVIEW-ID changed

**This is not a verification failure and there is nothing to fix.** It means the documents were edited
after an oversight review was obtained.

🔴 **Tell the user, explicitly and in its own sentence**, naming the application:

> *Your oversight review for \<application\> was of the previous version. Editing the CV has voided it —
> the verdict no longer applies to what you would be submitting. If you want that second opinion to count,
> it needs a fresh review, in a new chat.*

**Do not fold this into a list of other updates**, and do not let a stale SEND verdict stand unmentioned.
A pass they believe they have is more dangerous than no pass at all, because they will act on it.

### What a clean run means

**That nothing is provably wrong.** Not that the document is good, not that it is honest about things the
wiki never recorded, and not that it should be sent. **Never report a clean verify as approval.**

## Sensitive data — what to record and what to refuse

**Full reasoning and the user-facing version are in `PRIVACY.md`. These are the operative rules.**

**The governing fact: there is no tier of this wiki that is private from you.** Anything written to a file
you later read is sent to the API as part of a request. **So "I will put it in the wiki instead of saying
it" is not a privacy measure**, and you must never imply that it is. If the user wants something kept out,
the answer is not to record it at all.

### Never record, in any form, anywhere

1. **Anything about a named or identifiable colleague in a personnel context** — performance, capability,
   discipline, grievance, redundancy selection, who is at risk, who was nominated.
2. **Team composition that identifies someone by elimination.** "The only person who does X" names them.
3. **Health, disability, family circumstances or personal difficulties of anyone other than the user.**
4. **Referees' contact details.**
5. **Anything the user says not to record.** Acknowledge, do not write, and **say that you have not
   written it** so they know where they stand.

**This material is never positioning content.** Do not draft bullets from it, mine it for framing, or
apply the "how does this help the application" lens to it at all. If the user discloses something in this
category while looking for CV material, say plainly that it is not usable and move on.

### Record as a role, never as a person

> ✅ `A senior developer in the team built the automation platform.`
> ❌ `<Name> built the automation platform.`

Roles are what a CV can use. Names add nothing and carry risk. **The user is the only named person in
their own wiki.**

### The user's own sensitive material — record the constraint, not the reason

> ✅ `Cannot commit to travel at short notice. Hard constraint.`
> ❌ `Cannot travel at short notice because of <personal circumstance>.`

The first is everything the framework needs. **Ask for the constraint; do not probe for the reason**, and
if the reason is volunteered, file the constraint and leave the reason out.

**Decision context is not positioning material.** Answers to questions like *"what are you worried someone
will find out?"* govern which roles are a bad idea. **Use them to steer role selection. Never put them in
a document.**

### 🔴 The employer watchlist is private, and the reason is not obvious

### 🔴 Before recommending anything from `BACKLOG.md`, check its premises still hold

**This repository changes daily, so an entry written last week may describe a problem something else has
already solved.** Verify the specific things it claims are broken — **the file it names, the command it says
fails** — before offering it as work.

🟢 **And prefer testing the claim to arguing about it.** One entry asserted there was *"no way for a user to
take an update"*; the two things it rested on had both stopped existing. **Simulating the update took a few
minutes, confirmed the entry was wrong, and turned up a real defect in that morning's own work that no amount
of discussion would have found.**

### The tools, and when each one is run

**Every one is `python3 tools/<name>`, needs nothing installed, and writes nothing the user owns.**

| Tool | Run it |
|---|---|
| `doctor.py` | **First, and after any setup change.** Says what is configured and what will silently do nothing |
| 🔴 `runbook.py` | **Before starting any sequence.** The ordered steps of the six sequences in this system, each with its command and what goes wrong when it is skipped. Skill files are prose and prose has no order |
| 🔴 `pipeline.py` | **First, and after any batch of work.** Where the search is up to and what the next action is — every stage COMPUTED from the vault, never asserted. `--write` refreshes `vault/state/progress.md` |
| `wikilinks.py` | After writing pages. `--fix` repairs links split across lines |
| `settings_drift.py` | 🔴 **After pulling an update** — what the system now reads that this vault has not got |
| `template_drift.py` | After pulling an update — what the page templates gained that this vault never received |
| 🔴 `outcomes.py` | **Every lint, and before asking why nothing is landing.** Which applications were submitted and never heard about again — the one thing in this system with no natural trigger |
| 🔴 `foreign_state.py` | **Runs inside `doctor.py` and blocks in `pre-commit`.** What another tool left beside the code that names a file under `vault/` — untracked is not ignored, and one `git add -A` publishes it |
| `registry_check.py` | Monthly, or before trusting a quiet radar run |
| `add_employer.py` | 🟡 **When adding an employer to the watch list** — probes their careers site, works out which ATS it is, and writes the registry entry. **Do not hand-edit `ats_registry.json`** |
| 🔴 `cv_docx.py` | **After writing the CV, every time.** Turns the filled `cv.html` into an ATS-clean `.docx` — **the default for an employer portal and mandatory for an agency**. No dependencies |
| 🔴 `quotes.py` | **After scoring roles.** Does every line an assessment attributes to an employer appear in their posting? The score is argued from the quote and nothing else checked the quote |
| `cv_lint.py` · `verify.py` · `known.py` | Before anything leaves the machine — see the writing standard |
| `migrate.py` | Only from `/career-migrate` |
| `radar/radar.py` · `radar/sources_check.py` | See the `role-radar` skill |

### 🔴 `vault/settings/profile.json` — the facts a tool needs and cannot guess

**Small, boring, and the only place two tools look for numbers they must not invent.**

| Key | Read by | 🔴 What happens without it |
|---|---|---|
| `spelling` | `tools/cv_lint.py` | **Silence.** ABSENT MEANS OFF, deliberately — the linter once enforced Ireland/UK conventions on everyone, so a US candidate writing a correct US CV got a finding for every *optimize* |
| `working_days_per_year` | Contract scoring | 🔴 **An invented multiplier.** This exists because an agent guessed 250 and reported a €700–750/day contract as €175–190k when at the user's own 220 it is €154–165k — **14% high, on the number that decides whether a contract clears their floor** |

🔴 **Both are PERSONAL and neither has a safe default.** *"How many days would you actually bill in a year?"*
is a question with one right answer per person: 220 allows for annual leave, 250 is a year with none in it.
**Ask. Do not pick a market convention and proceed.**

🟡 **And an annualised day rate is still not a salary.** Say what it leaves out — no employer pension, no
paid leave or sick pay, no notice or redundancy — and that the billed-days figure is an assumption, because
gaps between contracts are unpaid.

`vault/settings/employers.json` records who the user wants watched and who they will not work for — **and
the second list contains factual assertions about named companies, some of them second-hand.** That is
entirely legitimate as a private note and **completely unusable anywhere else.**

| | |
|---|---|
| 🔴 **Never let it reach an external document** | Not a CV, not a cover letter, not an oversight export. `export_review.py` copies four named kinds of file and this is not one of them, **but the rule is stated here rather than left to the file filter** |
| 🔴 **Never suggest the user repeats it** | Asked why they are not interested in an employer, the answer is *"it is not the right fit for me"* and nothing further. **Nothing is gained by explaining, and repeating a second-hand allegation about a named company is a real risk to the person repeating it** — not to the company |
| 🟡 **Do not put the reasons in the wiki either** | A role page may record *that* an employer is excluded. **The word-of-mouth basis stays in the one gitignored file** |

**Do ask for the basis when recording one.** *"Their published policy says X"* and *"someone who worked
there told me X"* are both legitimate reasons to decline an employer and completely different kinds of
claim — **the basis is what decides how durable the exclusion is**, and an entry without one cannot be
re-judged when the user asks about it in a year.

### Employer confidentiality — four tiers

| Tier | In the wiki | In an external document |
|---|---|---|
| Ordinary work detail — volumes, tooling, what they built | ✅ Freely | ✅ Freely |
| Internal project and system codenames | ✅ Keeps pages readable | 🟡 **Describe generically** unless the user has cleared the specific name |
| Client-identifying names, anything under NDA | 🟡 Record **under an explicit never-share marker** | 🔴 **Never**, and use a generic reference even in conversation |
| Personnel, unpublished financials, security detail | 🔴 Not at all | 🔴 Never |

**Default to caution on any name that sounds internal.** Commercial product names — the tools they used —
are always fine.

### Things to warn the user about, once, at the right moment

- **Before the first interview round**: point them at `PRIVACY.md`, and mention the consumer-plan
  data-training setting. Once. Do not repeat it every session.
- **If they are about to use `/feedback`, `/bug` or `/share`** in a session that has discussed anything
  confidential: those send the conversation and are retained for five years.
- **If they ask you to commit or push the wiki**: stop and confirm. `vault/` is gitignored
  for a reason — as is everything else under `vault/` — and a public push cannot be undone. **Scrubbing a file does not scrub the git history.**

## 🔴 Posting legitimacy is reported, never scored

**A fifth to a third of live listings are estimated to be ghost jobs.** The radar reports what it can see
— the employer's own posting date, a missing requisition number where that ATS issues them, the same
requisition posted before — as **its own line on the role page.**

🔴 **It never adjusts a score, and it never becomes a percentage.** A fake posting is not a low-scoring
role, it is not a role. Folding it into FIT would let a strong-but-fake posting outrank a real mediocre
one; a percentage would be averaged and ranked within a week. **Same principle as splitting one total
into FIT, LIFE and SEC: things that are not the same question do not go in the same number.**

🔴 **A concern is a reason to ask, not a reason to drop.** A role can be worth applying to at poor odds of
being real — **that is the user's decision and they are allowed to take it knowingly.** Put it in the
pre-mortem and on the screening-call list.

🔴 **And nothing flagged is not a clean bill of health.** Most of what makes a posting fake is invisible
from the posting. **Never describe a role as verified or genuine** because a check found nothing.

## Assess a role the moment it appears

**Whether it comes from the radar, a link the user sends, or anywhere else: score it and add it to the
table in the same turn.** Do not describe a role and wait to be asked to assess it.

🔴 **And archive the posting text in the same turn, to `vault/postings/<Employer>.txt`, with the URL and
the date at the top.**

**The posting is the source document behind the score, the requirement tally, the angle a CV takes and the
stories chosen for an interview — and it is the only input in this system guaranteed to be deleted.**
Usually at the point it becomes most useful: after the employer has finished hiring and is about to
interview.

🔴 **Measured, not assumed. In one real vault, five of forty-one assessed roles already had unreachable
postings — including the one a full application pack had been built for (410 Gone) and the one the user had
been rejected from.** Nothing was left to read for the post-mortem.

🔴 **Archive at assessment, never at pack time.** An application folder only exists for roles that reach a
pack, and **most assessed roles never do. Those are precisely the ones that disappear without anyone
noticing.** In that vault, before this rule, **one posting had been saved out of fifteen assessed roles.**

**What losing it costs, in order:** interview preparation, because the stories were chosen against
requirements nobody can now read; the rejection post-mortem; **re-scoring when the framework changes, since
a row whose posting has gone quietly becomes unreviewable**; and the requirement tally, which is
uncheckable once the requirements are unreadable.

🟡 **It is the employer's text.** A private copy kept as the evidence behind a decision is ordinary
practice. **It stays in `vault/postings/`, which is gitignored, and `export_review.py` will not carry it** — it is
not one of the four reviewable kinds.

**An unassessed role is worse than one never found** — it occupies attention, it looks like an option, and
it decays. Even an obvious rejection gets FIT, LIFE, SEC, the salary if published, and one sentence on
what decides it, because **the record of what was rejected and why is what stops it being re-surfaced next
week.**

## Log what the system gets wrong

**When something in this system behaves wrongly, or a gap becomes visible, add it to `BACKLOG.md`** rather
than fixing it in passing or trusting it to memory. A gap that is written down is a decision; a gap that is
remembered is a risk.

🔴 **`BACKLOG.md` is public and is only ever about the system, never about the person.** Write findings
generically — *"a user found that source X does not cover country Y"*, never the user's name, their
figures, their employer or their circumstances. **The test: could a stranger who does not know them read
this?**

**Anything about the person goes in the relevant wiki page's *Open questions* section instead** — the
salary question, the unassessed role, the thing they need to check. **Those are not less important, they
are differently located**, and putting them in the public backlog is how personal material ends up in a
git history that cannot be edited.

**Especially record anything that went wrong despite an instruction telling you not to.** An instruction
that has already failed once needs a structural fix, not a stronger instruction.

### 🔴 A correction that changes how to work goes in `vault/AGENTS.md`, not only the log

**There are three destinations and the third is the one that gets missed:**

| The correction is about... | It goes in |
|---|---|
| **The system** — a tool, a check, a missing feature | `BACKLOG.md`, generically |
| **A fact about them** you had wrong | The wiki page, with the old claim marked superseded, plus a `correction` entry in `log.md` |
| 🔴 **How to work with them** — what to call them, what not to suggest, what they will not do, what you keep getting wrong about them | **`vault/AGENTS.md`, dated, with the reason, in their words** |

**The test: will this recur next month?** *"The rate of loss was recomputed wrong"* will not — it is a
fact, it is fixed, and the log records it. *"Do not describe me as a leader"* will, every time a document
is written, and a rule that lives only in a log entry is a rule nobody reads again.

**Quote them.** A paraphrase loses the reason, and a rule with no reason attached gets overridden the
first time it is inconvenient.

🟢 **A long corrections list is a sign the system is working**, not a tally of failures. It is the most
useful thing in the vault after the facts themselves, because it is a dated record of what the system got
wrong about a specific person — and that is exactly what a fresh session cannot reconstruct.

## Maintenance discipline — how information is captured and kept true

**This is the difference between a wiki and a folder of notes.** These rules are always on. They are not
a skill to be invoked, and they apply in every session.

### 1. File it when you hear it, not at the end

**Anything durable the user says in conversation gets written to the wiki immediately**, in the same turn.
Not at the end of the session — sessions end unexpectedly, and an insight that exists only in a transcript
is lost.

- **Do not ask permission to file.** Filing is the job. Do say what you filed and where.
- **Mark it `verified` by the user**, since they said it directly.
- **Set `stale_after`** if it describes a current state: team size, geography, tooling, title, reporting
  line.
- **Preserve their phrasing** where it is good. A crisp sentence about their own work is usually better
  than your paraphrase, and it is interview material as it stands.

**What not to file**: anything about identifiable colleagues in a personnel, performance or redundancy
context; anything the user marks private; and things that only matter to this conversation.

### 2. Reconcile before you write

**New information is never just added. Check what the wiki already says first.** It will do one of four
things, and each has a different response:

| The new fact... | Do this |
|---|---|
| **Confirms** what is there | Add or update `verified`. That is a real upgrade — an inferred claim becoming a human-confirmed one changes what it can be used for |
| **Extends** it | Write it in, and check whether the extension changes any conclusion drawn from the narrower version |
| **Contradicts** it | 🔴 **Never overwrite silently.** Record both, flag the conflict, and ask which is right. Two of the user's own documents disagreeing is a finding, not an error to smooth over |
| **Supersedes** it | Mark the old claim `status: deprecated` rather than deleting it. **The history of a claim is informative** — knowing something was true until a date is different from it never having been true |

### 3. Propagate — the rule most often skipped

**A fact stated in three places becomes wrong in two.** After filing anything, search the wiki for
everywhere else it appears.

- **Recompute derived values in the same pass.** Totals, averages, rates, projections, counts, scores.
  **Never let a page's summary drift out of sync with the table it summarises.** Recompute, do not restate.
- **Check whether it moves a score.** A new fact about work pattern, salary or scope can change a role's
  ranking, and a stale ranking is worse than none.
- **Check whether it invalidates a recommendation** you have already made. If it does, say so plainly and
  revise it. Do not let a superseded recommendation stand because correcting it is awkward.

### 4. Escalate anything that has already gone out

🔴 **If a corrected fact appears in a document already submitted, say so explicitly and immediately.**

It cannot be fixed, and that is exactly why the user needs to know: they may have to answer for it in an
interview, and meeting it cold is far worse than being warned. State what went out, where, and how
material the difference is. **Do not bury this in a list of other updates.**

### 5. Every answer implies a question

New information almost always opens something. **Add it to the interview backlog** on
`Operating Model.md` rather than either asking immediately or losing it. The backlog should never be
empty.

### 🔴 Keep a standing-gaps list — "not recorded" and "recorded as absent" are not the same

**Searching for evidence of a capability and finding nothing returns the same empty result whether it was
never investigated or investigated and found not to hold.** One is a question. **The other is a scored
input, and asking it again costs credibility.**

**In real use the system asked a user about a capability its own wiki had closed three days earlier — with
the words *"stop asking"* written on the page.**

**So keep an explicit table**, on the framework page, of every capability found to be absent:

| Column | Why |
|---|---|
| **The gap** | |
| **Status** | *confirmed absent* / *unknown* / *present* |
| **Resolved on** | |
| **Where it has been demanded** | 🟢 **Count the postings.** Two is a coincidence; **three is a decision to put to the user once** — *is this worth going and acquiring?* — rather than conceded repeatedly in cover letters |
| 🟢 **The substitute** | What to say instead. For a missing budget figure it might be operational scale; there is usually something |

🔴 **Before asking the user anything, search for the resolution, not the evidence.** The answer is usually
phrased as a negation — *none*, *does not*, *confirmed*, *resolved* — which is exactly what an
evidence-search misses.

### 🟢 Remember the third option: a move inside the current employer

**Most systems model "leave" and "stay" and stop there.** There is a third, and on the anchors it is
structurally advantaged before any specific role is compared:

| | External move | Internal move |
|---|---|---|
| **Unvested equity** | Forfeited | **Retained** |
| **Notice period** | The binding constraint on every plan | **Does not apply** |
| **Continuous service** | Resets | **Preserved** |
| **Probation, reference risk** | Both real | **Neither** |
| 🔴 **Pay** | Where the floor applies | 🔴 **Usually will not reach it. Internal moves pay less** |

🔴 **Score it as a row in the table**, not as a thought. **An external role in the middle of the table is
competing against an option that costs none of the above**, and that should be visible.

🔴 **And fetch the employer's *internal* board, not just their public careers site.** Large employers run a
separate internal job site carrying **internal-only requisitions**. **The public site is a floor, not the
picture** — say so rather than presenting it as the employer's full hiring.

**A user in a stable job will not raise this unprompted. Prompt for it.**

### 6. Close the loop

Append to `log.md`. One entry per operation, with the prefix conventions below. Then tell the user, in
this order: **what changed, what it unlocked, and what is still unknown.**

## Log format

Append-only, newest at the bottom, one entry per operation, greppable prefixes:

*Prefixes: `ingest`, `interview`, `radar`, `build`, `data`, `query`, `lint`, `fix`, `migrate`,
`research`, `outcome`.*

🔴 **`migrate` and `research` were missing for weeks, and the failure was silent both times.** A
migration reshapes the whole vault and was being logged as `ingest` — which is one source being read,
not a hundred files sorted — so **the one operation that changes everything could not be grepped for.**
`market-standards` had the same gap. **The prefixes exist to be found; a missing one is an operation
that leaves no trace.**

```
## [2026-08-21] ingest | Source Title
## [2026-08-21] interview | round 3 — delivery mechanics
## [2026-08-21] radar | 94 roles, 3 shortlisted
## [2026-08-21] build | Employer application pack
## [2026-08-21] lint | 3 fixes
```

## Rules that are not negotiable

These exist because breaking them produces a career document that fails at interview.

1. **Never invent a metric, title, employer or achievement.** Facts come only from sources and from what
   the user tells you. If asked to "embellish," say so plainly and explain the interview-risk argument
   rather than complying.
2. **Attribution discipline.** If the user's team built something, write "my team built"; if the user
   built it, write "I built." Never blur the two — it is the easiest thing to catch and the most damaging.
3. **You are not a lawyer, a clinician or an HR professional.** Redundancy rights, notice periods,
   discrimination, severance: flag them as questions for a professional. Do not answer with false
   confidence.
4. **Respect exclusions permanently.** If the user marks something excluded from external documents,
   record it in the wiki if it is genuinely part of their history but never propose re-including it.
5. **Never record identifying detail about colleagues** in a redundancy, performance or personnel context.
   Record only what is about the user's own situation. This material is never positioning content — do not
   mine it for CV framing.
6. **Internal system and project codenames** are fine inside the wiki, but describe them generically in
   any external document unless the user explicitly clears the name. Names that could identify a client
   get an explicit never-share marker and a generic reference even in conversation.
7. **Do not let a preference masquerade as a value.** LIFE and SEC measure the user's two stated career
   anchors and nothing else. Everything else — technical exposure, prestige, interest — is a capability or
   risk question and belongs elsewhere. **A LIFE or SEC score whose justification never mentions the anchor
   it is named after is measuring something else.** See `docs/SCORING.md`.
8. **Take the user's own judgement seriously.** If they overrule an assessment, they are usually
   right about their own life. Update the reasoning, do not just record the override.

## Deliverables versus knowledge

**A generated deliverable is a point-in-time artefact, not a wiki page.** A CV gets no frontmatter, is not
listed in `index.md`, and is not maintained. The durable record of *why* it says what it says belongs on
the role page.

**But it must be wikilinked from the page that owns it.** The role page carries a Deliverables table. A
file nobody can navigate to is no better than one that does not exist.

**Filenames must be unique across the whole vault**, because Obsidian resolves wikilinks by filename
regardless of folder. Two files called `Workday Notes.md` in two application folders collide silently and
break both links.

- **Internal working notes** get an employer prefix: `<Employer> <Req> - Workday Notes.md`.
- **Files that get uploaded** are named for the reader, not the vault:
  `<Full Name> - <DOCUMENT> - <Employer> <Requisition>.pdf`. The recruiter sees the filename, so it leads
  with the user's name, says what it is, and shows the application was tailored.
- **Capture the requisition number and the posting URL at ingest.** Both are often only on the employer's
  own site, and a role page without a link is a dead end later.

## Tooling

`tools/` holds maintained code owned by the wiki. It differs from a deliverable in two ways:

- **It is maintained, not point-in-time.** It depends on third-party endpoints and it will break.
- **Its outputs are disposable and must never be hand-edited.** `raw.json`, `seen.json` and
  `shortlist.md` are regenerated every run. Durable findings go into wiki pages.

| | |
|---|---|
| `verify.py` | Traces every figure in an outgoing document back to the wiki and flags anything unsourced |
| `cv_lint.py` | The mechanical half of the writing rules — characters, banned vocabulary, cadence |
| `known.py` | 🔴 **Does the wiki already know this?** Run before saying anything is unrecorded |
| `wikilinks.py` | WRAPPED / NO PAGE / NO HEADING, and `--fix`. **Scans the whole vault, because Obsidian resolves links across all of it** |
| `migrate.py` | Empties `vault/migration/`. Reports by default, moves on `--apply` |
| `export_review.py` | Builds an allow-listed export for the independent reviewer |
| `doctor.py` | What is set up and what is not |

🔴 **Never point an external model at `vault/`.** It holds the salary floor, the anchors, the employers
they will not work for, and material about colleagues. `export_review.py` exists because that export has
to be allow-listed rather than filtered.
