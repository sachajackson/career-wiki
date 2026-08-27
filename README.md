# Career Wiki

**An AI-maintained knowledge base for running a job search properly.**

> 👔 **Arrived here from a job application?** → **[Two minutes on what this is](docs/FOR-RECRUITERS.md)**.
> That page describes the tool, not the applicant.

> 🔴 **Here to *use* it?** Read **[what it does with your data](PRIVACY.md)** before your first session.
> It is not optional reading, and the surprising parts are near the top.

You put your CV in a folder. An AI agent interviews you about what you actually do, builds a structured
wiki about your working life, works out what you genuinely want from a job, turns that into a scoring
system, finds roles, ranks them against *your* values, and writes a bespoke CV for each application worth
making.

You never write the wiki. You answer questions and make the decisions.

> ### ⚠️ Every output is a draft you must read and stand over
>
> **Large language models produce fluent, confident, plausible text, and some of it will be wrong.** That
> is how the technology works, not a defect awaiting a fix. **If you cannot personally stand over a
> sentence in an interview, take it out.** The full warning — and what you are accepting by using this —
> is **[`docs/DISCLAIMER.md`](docs/DISCLAIMER.md)**.

## Where things are

| | |
|---|---|
| **[INSTALL.md](docs/INSTALL.md)** | Getting it running, and the first hour after that. **Start here if you are not technical — the desktop app needs no terminal** |
| **[JOB-SEARCH.md](docs/JOB-SEARCH.md)** | Configuring the search: naming employers rather than endpoints, and checking the sources actually answer |
| **[CHECKING.md](docs/CHECKING.md)** | **The three layers that check the output**, including how to run oversight through a different vendor's model |
| **[SCORING.md](docs/SCORING.md)** | How a role gets a number, and why the number is four numbers |
| **[PRIVACY.md](PRIVACY.md)** | What is held, where it goes, and what you should decide |
| **[DISCLAIMER.md](docs/DISCLAIMER.md)** | What it cannot do, and what it will decline to do |
| **[LESSONS.md](docs/LESSONS.md)** | **Rules learned by shipping the opposite** — kept with the failure that taught each one, so a later change does not quietly reverse it |
| **[BACKLOG.md](BACKLOG.md)** | What does not work yet, and what has gone wrong once |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Using it and developing it, in the same clone |
| **[SCHEMA.md](SCHEMA.md)** · **[AGENTS.md](AGENTS.md)** | The instructions the agent itself reads |

---

## The problem this solves

Most job-search tools optimise the wrong thing. CV builders make one document prettier. Job boards rank by
recency and keyword. AI cover-letter tools write fluent prose about someone they have never met.

None of that is the bottleneck. The bottleneck is that **nobody has written down what you actually do, or
what you actually want.** Without the first, every CV is a summary of a summary. Without the second, every
application is a guess about whether you would even take the job.

Two things follow, and they are the whole design:

**1. The interview is the product.** People stop noticing what they are good at. Ask someone for their key
achievements and you get a rehearsed answer; ask them to walk you through what happens when a release
fails at 4pm on a Friday and you get the truth. Ten years of doing something unusual every week gets
described as "the day job" and never reaches a CV.

So it asks constantly, using who / what / when / where / why on anything you claim — **and "why" twice,
because the first answer is the official reason and the second is usually the real one.** The more
questions, the more your memory is jogged. You cannot recall your own work on demand; you recall it when
something specific prompts you.

**2. A good role is not a general fact.** A role that suits one person is a bad trade for another with
different obligations, a different commute and a different tolerance for risk. So the scoring is built
around your stated values, elicited by interview, rather than a generic notion of prestige.

**3. It compounds.** You will apply for many roles over months, and everything learned along the way is
filed against *you* rather than against one job. The test applied constantly is: **does this belong to the
role, or to the person?** Material discovered while writing the seventh application goes in the wiki, not
in the seventh application's folder — which is why the twentieth application costs ten minutes instead of
an evening.

---

---

## What it actually does

**Nine commands**, run inside Claude Code. Each is a *skill* — a set of instructions the agent follows. 🔴 **Instructions are not the interesting half** — see [The checks](#the-checks-and-why-they-exist) below.

**The system covers everything up to the submit button and stops there.** Interview preparation, offers
and negotiation are not in it yet.

### `/career-init` — run once, first

Reads whatever you put in `vault/sources/`. Tells you what it noticed, including gaps and contradictions in your
own documents. Scaffolds the wiki. Runs the first interview round. Then elicits the two things nothing
else can work without: **your career anchors** and **your salary floor** — including what that floor is
actually for, which changes how it behaves.

About an hour, most of it conversation.

### `/career-migrate` — instead of `/career-init`, if you already have something

🔴 **An existing wiki, an export from another tool, or a folder of career material.** Drop it all in
`vault/migration/` and run this rather than `/career-init` — which assumes an empty vault, and would
scaffold templates over pages you already have while interviewing you about things you have already
recorded.

`tools/migrate.py` files what it recognises and **refuses four things on purpose**: a forked copy of the
tooling, regenerable state, a secret, and any filename already used elsewhere in the vault. Everything it
cannot place stays where it is and is named — a file quietly removed from a drop zone looks exactly like
a file that was dealt with.

### `/interview` — the core operation

Continues a standing backlog of questions about how your work really operates: reporting lines including
the dotted ones, what you can approve without asking, how work arrives and who prioritises it, what
happens when it breaks, what you have built yourself, who you have grown.

Rounds of six to eight questions. It files the answers, tells you what changed, and proposes the next
round. Everything else in the system is downstream of this.

### `/role-radar` — find roles

Searches job sources through pluggable adapters, filters on your location rules, reads the full
description of everything that survives, and marks each one `HIGH`, `MED` or `LOW`. A separate
`role-triage` agent does the reading, so your main session does not fill up with job adverts, and hands
back a ranked shortlist carrying the reasoning and the strongest objection for each role.

**Two kinds of run, and you want both.** A windowed run — the last week — gives dense coverage of what is
new. **An open run drops the date filter and sweeps everything still open**, which matters more than it
sounds: for a long time the search only ever looked at the last seven days, and a role posted a fortnight
earlier was invisible to it no matter how good it was. **Neither run is a superset of the other**, because
sources cap how much they will return per search, so the open sweep trades depth of one week for a thin
slice of three months. Ask for whichever you want — *"check the last week"* or *"sweep everything still
open"*.

**It tells you when it was cut off.** If a search hits the source's limit rather than running out of
results, the output says so, and the agent is told not to describe that run as everything that is open.

### `/build-application` — one role, one pack

Checks the posting is still open — roles close, and twenty minutes spent on a dead requisition is twenty
minutes gone. Writes a role page capturing the requisition number and posting URL. Picks the angle — **ten
CVs built from the same material should open in ten different places, and if two of them open the same
way, one is not tailored.** Then produces:

- **A tailored CV**, written against a documented writing standard rather than a house style
- **A cover letter** that opens on the hardest objection rather than on enthusiasm
- **A paste-ready pack for the application form** — which structured fields to fill, in the employer's
  vocabulary, and which skills tags *not* to claim

It writes the CV as HTML that you print to PDF from your browser. That needs nothing installed and looks
the same on every machine.

**The writing standard is the part that does the most work**, and it is worth knowing what is in it:

- **What actually gets a CV rejected** — inconsistency with your public profile, typos, and reading as
  generated. In that order.
- **Cadence rules.** Uniformity is the durable machine signal: a page of bullets all one and a half lines
  long reads as generated regardless of who wrote it. So bullet length and bullet openings are varied
  deliberately, and no more than 60% of bullets may share a grammatical pattern.
- **Banned characters and constructions.** ASCII only — no em dashes, curly quotes or emoji, all of which
  survive a paste badly. No participial tails (`, resulting in X`). No "spearheaded", "leveraged",
  "seamless", "proven track record".
- **Before-and-after pairs beat percentages.** `from eleven days to four` beats `a 64% reduction`.
- **Employer spelling matching.** An applicant tracking system matching literally does not match
  *programme management* against *program manager*.
- **Attribution discipline.** "My team built" and "I built" are different sentences, and the difference is
  the easiest thing to catch at interview.
- **Two checking passes.** `tools/cv_lint.py` mechanically flags characters, banned vocabulary,
  participial tails, round-number tells and uniform bullet cadence — run against the text an ATS would
  actually extract from your PDF, not against the source. Then an audit prompt, **run in a fresh session
  because a model that just wrote the copy will defend it**, covering what no script can check: could a
  stranger have written this bullet about someone else, and could you talk about it for ninety seconds?

**If you already have your own writing standard, it takes precedence** — the agent asks early and keeps
yours in the wiki.

### `/pre-submit` — the last check before the button

Run with the form open and everything filled in. **An application is the one thing here with no undo** —
the recruiter's first read is the only first read there is, and nobody writes back to say which line lost
it.

It checks the things that are unfixable afterwards: whether the decision still holds, whether the CV, the
form and your LinkedIn agree on titles, dates and team sizes, whether every claim is one you have actually
confirmed, whether a client name or a colleague's name has ended up in an outgoing document, whether the
right employer is named in the letter, and whether the sponsorship question was read twice. Then it does
the bookkeeping while it is fresh.

### `/profile-refresh` — LinkedIn and Indeed

Rewrites your public profiles from the wiki, as text you paste in. Run it **before** a batch of
applications: a live application creates a version of your history a recruiter can compare against your
profile, and a mismatch is exactly what gets noticed.

### Just paste a job link

**You do not need a command for this.** Paste a URL and it will read the posting, work out what the
employer is actually anxious about, score it against your framework, and file a role page.

**Then it interviews you about it**, and that half matters more:

- *What attracted you to this one?* — the most useful question in the system. A concrete posting surfaces
  your real priorities far better than being asked about your values in the abstract. If the honest answer
  is "the money" or "it is twenty minutes from my house", that is a finding, and it goes in the framework.
- *What experience do you have that applies here?* — you will name things that are not in your wiki yet.
  **That is the point.** All of it gets filed.
- *Which of their requirements do you tick, and which do you not?* — going through a real checklist jogs
  memory far more effectively than open reflection, and it produces the honest gap list a cover letter
  needs.
- *Have you done anything like their problem before?* — the problem, not the job title.
- *What would worry you about this role?*

**Everything you say about yourself gets filed against you, not against the job.** A fact learned while
looking at one role is available for every role after it. That is the whole design: **by the twentieth
application, the wiki writes a better CV in ten minutes than a fresh interview would in an hour.**

### `/market-standards` — what the market expects, for *you*

**Every other skill knows how a sentence should read. None of them knew how long a CV should be**, whether
education stays on it, whether a cover letter is expected at all, or which of those answers changes when you
move country. **A one-page résumé is a US convention, and applying it to a director-level application in
Europe is simply wrong.**

This researches those questions **against your own country, level, profession and target roles** — read out
of the vault, not assumed — and writes four reference pages that `/build-application`, `/profile-refresh` and
`/pre-submit` then read. It delegates to a deep-research skill rather than reimplementing one, runs each topic
separately because they reach different confidence levels, and **marks every claim with how well evidenced it
is.**

**It carries the debunked claims so each run does not rediscover them.** *"75% of résumés are auto-rejected"*
traces to a vendor that shut down in 2013 having published no study. The 7.4-second recruiter figure is one
survey of thirty people, run by a company selling résumé services. **Both are still quoted everywhere.**

🔴 **It never puts you into a search query.** It researches the category — *"senior delivery roles in
<country>"* — never the person.

**The skills that read these pages do not block when they are missing.** They say which page is absent, offer
to run this, and **proceed anyway on a stated assumption** if you decline. A skill that refuses to work until
research has run is one people route around.

### `/career-lint` — health check

**Two halves.** The mechanical one runs first and takes seconds: `doctor`, `wikilinks`, `template_drift`,
`registry_check`, and the test suite. The judgement half is what a script cannot do — contradictions
between pages, claims that have expired, unverified assertions that have found their way into a CV, the
same number attached to two different jobs across two application packs, roles with no posting link.
Ranked by what could actually cause damage.

🟡 **And it asks about every application you sent and never heard back on**, because nothing else in the
system ever will: an employer replying, or not replying, happens outside it.

---

---

## The checks, and why they exist

**One rule governs this repository, and it was learned the hard way:**

> 🔴 **Every instruction-shaped control here has failed at least once. Every executable one has held.**

A skill file can say *always archive the posting* in bold red text, and the archiving still gets skipped —
because prose is read by something that is trying to do a different job. So when something goes wrong
twice, **the fix is not a stronger warning. It is a check that fails.**

**`python3 tools/pipeline.py` runs eight of them and recomputes every one from the vault**, so a step
skipped in the moment surfaces before the work is called finished:

| | What it refuses to let pass |
|---|---|
| **`cv_lint` · `verify` · `known`** | A figure in an outgoing CV that traces to nothing in your wiki, or a real achievement attached to the wrong job |
| **`quotes`** | A line an assessment attributes to an employer that is **not in their posting** — plus a stated requisition number that appears in no archived copy, and a *"the source was truncated"* caveat over a posting that is complete |
| **`scores`** | A score that does not add up, and a role page that disagrees with its own row in the scoring table |
| **`batch`** | 🟢 **A refusal, not a warning** — it will not open a batch of roles on a stale corpus, because a warning is a thing you scroll past |
| **`doctor`** | A settings file copied from its example and never edited. **It looks configured and matches nothing** |
| **`settings_drift` · `template_drift`** | An update that needs a file it has no way to deliver into your vault |
| **`registry_check`** | An employer who changed recruiting system, so their board quietly returns nothing — **which looks exactly like a quiet week** |
| **`test_boundary`** | Any of your data written outside `vault/` |

**Those checks have their own test suite**, and `tools/tests/run.py` runs it. Most of them are not the success case: they are the *false
positive* that a first draft produced, kept as a test. 🔴 **A check that cries wolf gets switched off
within a day**, so the first version of one is not finished until it has been shown what a healthy vault
looks like.

### Two things the agent delegates to another agent

**Some work cannot be a string operation, and pretending otherwise is how a system quietly lies to you.**

- **`role-triage`** reads a batch of job adverts and returns a short ranked list. A week of postings is
  two to three hundred adverts; reading them in the main session destroys it with text nobody needs to
  keep.
- **`role-review`** is **adversarial**. It takes a finished, scored assessment and the employer's own
  posting and **tries to refute the score** — quoting the posting, never the assessment's summary of it.
  It exists because *"hands-on experience with agent frameworks"* can be quoted perfectly and read
  completely wrongly, and **no matcher will ever catch that.**

### 🔴 What none of it proves

**The chain is honest about where it stops:**

`quotes` proves the sentence was in the posting. `scores` proves the numbers hang together.
`role-review` proves the sentence was read correctly. **Nothing proves your wiki is true** — that part is
yours, and it is why every output is a draft you have to stand over.

---

## How it stores things

The wiki is plain markdown, so it is readable without this tool and will outlive it. Every page carries
structured metadata following
[Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

Two fields do most of the work:

```yaml
verified:
  - { by: "human:you", at: 2026-08-21T15:40:00Z }
stale_after: 2027-02-21
```

**`verified` separates what you confirmed from what the agent inferred.** A career wiki fills up with
sentences that look identical and are not: things you said, things the AI deduced from a document, and
things that used to be true. Conflating them is how a CV ends up carrying a confident claim nobody can
support. **A page with no `verified` entry never goes on a CV without being flagged to you first.**

**`stale_after` makes claims expire on a date** rather than rotting silently. Team sizes, job titles,
geography and tooling all describe a current state, and profiles are full of statements that were true two
years ago. `/career-lint` surfaces them.

---

**The full layout, and which folders are yours, is in [`vault/README.md`](vault/README.md).**

---

## Sensitive data

**[`PRIVACY.md`](PRIVACY.md) is the full version. Read it before your first interview session.**

🔴 **There is no tier of this wiki that is private from the model.** Claude Code runs locally, but to
answer anything it sends the contents of the files it reads to Anthropic's API. **Writing something into
a file is not hiding it from the AI — it is the opposite.** Local storage is not concealment.

🔴 **Everything of yours is under `vault/`, and none of it is ever committed.** Five README files ship
there to say what each folder is for; nothing else under it is tracked, the pre-commit guard refuses it
even against `git add -f`, and `tools/tests/test_boundary.py` fails the build if that ever stops being
true.

**Colleagues appear as roles, never as names** — and never at all in a personnel or redundancy context.

---

## Limits, and what it will decline to do

**[`docs/DISCLAIMER.md`](docs/DISCLAIMER.md) is the full list.** The one that matters most:

🔴 **It cannot tell you whether what it wrote is true.** The deterministic layer proves every figure
traces back to your wiki. **Nothing proves your wiki is right.** Only you can do that.

**And it will not invent anything** — no metric, title or achievement you did not provide. Ask it to
embellish and it will say so plainly and explain why the claim would not survive a follow-up question.

---

## Credits and licence

MIT licensed. See `LICENSE`.

The architecture — immutable sources, an AI-owned wiki, a co-evolved schema file, and the ingest / query /
lint operations — comes from **Andrej Karpathy's LLM Wiki pattern**, published as
[a gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). That document is deliberately
abstract and ends by inviting domain-specific instantiations. This is one, for careers.

The on-disk format is **Open Knowledge Format v0.2**, from Google Cloud's
[knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog).

The scoring lenses are the work of Clayton Christensen (Jobs-to-be-Done), Bradford Smart (Topgrading),
Alexander Osterwalder (Value Proposition Canvas), Edgar Schein (Career Anchors) and Gary Klein
(pre-mortem). All are cited, none are vendored, and none of these authors is affiliated with this project.
