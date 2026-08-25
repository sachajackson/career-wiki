# Career Wiki

**An AI-maintained knowledge base for running a job search properly.**

*If you came here to **use** this software rather than to evaluate an application made with it, read
[what it does with your data](#sensitive-data) first — it is not optional reading.*

## If you have arrived here from a job application

**Two minutes, then you can stop reading.** Someone has linked you here because their application was
built using this. It is open source and anyone may use it for any purpose, so **this page describes the
tool, not the applicant** — what it does, what it checks, and therefore what an application that came
through it has been put through.

### It is a knowledge base first, and a document generator only at the end

The applicant does not fill in a template. An agent **interviews them** about what they actually did,
files each answer as a page with its source, and the CV for your role is assembled from those pages on
demand. **There is deliberately no master CV** — a standing document drifts, and every claim in it stops
being traceable to anything.

**Which means each figure in the document you received can be traced back to a specific page, and to who
confirmed it.** Pages carry a trust tier: **generated** (a model wrote it and nobody has checked),
**machine-confirmed** (cross-checked against a second source), or **human-reviewed** — the applicant
confirmed it personally. 🔴 **Only the last tier is treated as safe to assert to you without a check.**

### Three checking layers, and the first one contains no AI

**This is the part worth two minutes if any of it is.** Large language models write fluent, confident,
wrong text. Every layer here exists because of that.

| | |
|---|---|
| **[`tools/verify.py`](tools/verify.py)** — deterministic | Extracts **every number** from an outgoing CV or letter, traces it back to a sourced page, **checks it is attributed to the right employer**, and fails on anything unsourced. **No model is involved.** The reasoning: a model is probabilistic, so the check on it must not be. It also runs a `--coverage` pass against the job posting itself |
| **[`tools/cv_lint.py`](tools/cv_lint.py)** — mechanical | Catches the tells: **banned AI vocabulary, participial tails, suspiciously round numbers, repetitive cadence,** non-ASCII punctuation that breaks applicant tracking systems |
| **[`tools/known.py`](tools/known.py)** — against the agent itself | Answers *"does this knowledge base already know this?"* in **three ways rather than two**: settled, present, established absence, or genuinely nothing. **Searching for evidence and finding none returns the same result whether a thing was never investigated or investigated and ruled out** — and those mean opposite things. It exists because an agent got that wrong three times in one session, and re-asked questions the user had already answered |
| **[`tools/wikilinks.py`](tools/wikilinks.py)** — structural | Finds links that go nowhere: **split across two lines** by a wrapping convention, **pointing at a missing page**, or **pointing at a heading that has been renamed.** None of the three looks broken while you are reading, and a knowledge base whose failure mode is silence is one you stop being able to trust |
| **[`oversight/`](oversight/)** — independent | The document is reviewed by **a different vendor's model**, in a fresh session, working from a restricted export. **Cross-model review rather than self-review** — and the export is allow-listed, so the reviewer only ever sees what you would see |

🟢 **And the checkers have their own checks.** [`tools/tests/`](tools/tests/) is **several hundred tests,
stdlib only, and it runs in seconds** — `python3 tools/tests/run.py`. Several encode bugs that were live in a shipped version:
the linter reporting *"clean"* on empty input, a crash on bullets with no words, and figures being sourced
from the very document under review, so a fabrication proved itself.

🔴 **None of it runs on memory.** An [agent hook](.claude/hooks/verify-artefact.sh) fires the verifier
**every time a CV or cover letter is written or edited**, and puts the findings straight back into the
agent's context so they have to be dealt with. **A control that depends on someone remembering to run it
is not a control.**

### Roles are scored against four named frameworks, not a vibe

Each posting is assessed on four dimensions, each drawn from an established method rather than invented:

| | Framework | The question |
|---|---|---|
| **NEED** | **Jobs-to-be-Done** | Is the thing this employer is most anxious about the thing the applicant is best at? *Read the spec for its underlying worry, not its requirements list* |
| **DELIVER** | **Topgrading Scorecard** | Reverse-engineer the outcomes the hiring manager should have written, then assess against those |
| **EDGE** | **Value Proposition Canvas** | Differentiated, or one of many? A capability every applicant has scores low |
| **WANT** | **Schein's Career Anchors** | Does it match what they will not trade away? |

**Reported as three separate scores rather than one total** — capability, lifestyle and employer stability
— because a single number lets a good commute hide a weak match, or the reverse. **The sub-scores stay
visible**, since *would deliver it well but so would others* and *brings something rare, with real gaps*
can sum to the same figure and are not the same candidate.

🟢 **And every assessed posting carries a requirement count**: the employer's own stated requirements, each
marked **cleared, partial or gap**, with the tally. *"Nine of your twelve outright, two partially, one not
at all."* **You can check that line by line instead of taking a claim about fit on trust.**

### It researches the employer before it writes anything

**Not the posting — the company.** Financial trend and profitability, revenue by division, whether the core
business is under structural threat, acquisitions, restructuring and headcount, leadership changes,
employee sentiment, and what the local office actually is. **Company-level and division-level separately**,
because a group can be struggling while the division hiring is growing, or the reverse. Research pages
carry an expiry date and are flagged when stale.

**A practical consequence you may notice:** the applicant will have read your last set of results, and
their questions will be about your division rather than your homepage.

### The rest of it

- **Job search across multiple sources** — [adapters](tools/radar/adapters/) for Workday, Oracle, Greenhouse, Lever, Adzuna
  and LinkedIn, plus direct Workday and Oracle recruiting endpoints, which return more than the aggregators
  do — the real posting date, the requisition number, and the additional locations a listing hides
- **The employer's own posting is fetched in preference to any job board's copy**, because aggregators
  truncate — and they truncate the qualifiers, which is the half that decides eligibility
- **[`BACKLOG.md`](BACKLOG.md)** — the system's own defects, written up honestly: what broke, what it cost,
  what would prevent it. **Including the occasions it was wrong about the person using it**
- 🔴 **Nothing personal is in this repository.** A [`PRIVACY.md`](PRIVACY.md), a
  [pre-commit hook](githooks/pre-commit) that blocks personal paths and content **even when someone forces
  the add**, and an allow-listed oversight export. **The private knowledge base and the public tool are
  separate by construction, not by care**

### "Did the applicant build this, or just use it?"

**A fair question, and this page cannot answer it — which is the point of saying so.** The repository is
public and anyone may use it. **If they claim to have written it, they should say so themselves, and you
can check:**

- **The commit history** shows who wrote what and when, and GitHub marks a forked repository as a fork.
- 🟢 **[`BACKLOG.md`](BACKLOG.md) is the part that cannot be copied.** Anyone can clone a codebase. **A
  defect log written in first-person operational detail — dated, with what it cost — is a record of
  running the thing rather than possessing it.**
- 🟢 **Or just ask.** *Why are the scores split into three? What broke, and what changed as a result? Why
  is the verifier deliberately not an AI?* **The answers are more interesting than the code, and only
  someone who has actually used this has them.**

### It was built with AI, and says so

**Every commit records it.** The system is written and maintained by an AI coding agent. 🟢 **That is the
demonstration rather than the admission:** building quickly with a model, then wrapping its output in
deterministic verification, mechanical linting and independent cross-vendor review **because the model
cannot be trusted unexamined**, is the whole design. **The warning immediately below this section is not
boilerplate — it is the premise the rest of the repository is built on.**

---

> # ⚠️ Read this before you use anything here
>
> **This system is built on large language models. They produce fluent, confident, plausible text, and
> some of it will be wrong.** That is not a defect awaiting a fix — it is how the technology works. A
> model can invent a number, attach a real achievement to the wrong job, misread a date, misstate a
> qualification, or write a sentence you cannot support, and it will do all of that in the same assured
> tone as everything it gets right.
>
> ### You must read and verify every single output, in full, before it leaves your hands
>
> **Every CV, cover letter, profile, form answer and assessment this produces is a draft for you to
> check.** Not a finished document. Read it line by line against what you actually know to be true:
> dates, job titles, employers, figures, technologies, qualifications, and which role each achievement
> belongs to. **If you cannot personally stand over a sentence in an interview, take it out.**
>
> ### You are solely responsible for what you submit
>
> **The person whose name is on the application is accountable for its contents.** Not this software, not
> its authors, not the model provider. If something inaccurate reaches an employer, that is your
> submission and your consequence.
>
> **Those consequences are real.** An unsupportable claim can lose you an application, an offer, or a job
> after you have started. In many places a material misstatement in a job application is grounds for
> summary dismissal, and depending on the claim and the jurisdiction it can amount to fraud or
> misrepresentation with legal consequences beyond employment. **Answers about right to work, visa status,
> sponsorship, qualifications and professional registration are legally significant. Verify them
> yourself.**
>
> ### The checks in this repo reduce risk. They do not remove it
>
> There is a deterministic verifier, a lint pass and an independent review layer, and they exist precisely
> because model output cannot be trusted unexamined. **They are not a guarantee.** A clean run means
> *nothing was provably wrong by the checks that ran* — it does not mean the document is accurate, and it
> never means you can skip reading it.
>
> ### No warranty, no liability, no advice
>
> **This software is provided "as is", without warranty of any kind**, express or implied, per the MIT
> licence in `LICENSE`. **The authors and contributors accept no liability for any loss or damage arising
> from its use**, including lost opportunities, withdrawn offers, terminated employment, reputational harm
> or any other consequence, however caused.
>
> **Nothing here is legal, immigration, employment, financial or career advice.** It is not a substitute
> for a solicitor, an employment adviser, an immigration adviser or a qualified professional. If a
> question is genuinely legal — redundancy rights, notice, discrimination, visa eligibility, contractual
> obligations — take it to someone qualified.
>
> **Third parties are outside anyone's control here.** Job boards, applicant tracking systems, employers
> and any other AI vendor you choose to use have their own terms, their own data practices and their own
> behaviour. **Read their terms. Using the optional job-search or review integrations is your decision and
> your responsibility.**
>
> ### Using it means you accept all of the above
>
> **If you are not willing to check the output yourself, do not use this.** An unchecked AI-written CV is
> worse than no CV, because it is confident, specific and wrong in ways you will be asked about out loud.

---

You put your CV in a folder. An AI agent interviews you about what you actually do, builds a structured
wiki about your working life, works out what you genuinely want from a job, turns that into a scoring
system, finds roles, ranks them against *your* values, and writes a bespoke CV for each application worth
making.

You never write the wiki. You answer questions and make the decisions.

---

## Contents

- [If you have arrived here from a job application](#if-you-have-arrived-here-from-a-job-application) — the sixty-second version
- [The problem this solves](#the-problem-this-solves)
- [What it actually does](#what-it-actually-does) — including just pasting a job link
- [Checking the output](#checking-the-output) — **the three layers, and how to run oversight**
- [The scoring framework](#the-scoring-framework)
- [Installing it](#installing-it) — start here if you are not technical; **the desktop app needs no terminal**
- [Your first hour](#your-first-hour)
- [Setting up job search](#setting-up-job-search)
- [How it stores things](#how-it-stores-things)
- [Sensitive data](#sensitive-data) — **read before your first session**
- [Honest limits](#honest-limits)
- [Credits and licence](#credits-and-licence)

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

## What it actually does

Seven commands, run inside Claude Code. Each is a *skill* — a set of instructions the agent follows.

**The system covers everything up to the submit button and stops there.** Interview preparation, offers
and negotiation are not in it yet.

### `/career-init` — run once, first

Reads whatever you put in `sources/`. Tells you what it noticed, including gaps and contradictions in your
own documents. Scaffolds the wiki. Runs the first interview round. Then elicits the two things nothing
else can work without: **your career anchors** and **your salary floor** — including what that floor is
actually for, which changes how it behaves.

About an hour, most of it conversation.

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

### `/career-lint` — health check

Contradictions between pages, claims that have expired, unverified assertions that have found their way
into a CV, the same number attached to two different jobs across two application packs, roles with no
posting link. Ranked by what could actually cause damage.

---

## Checking the output

**The disclaimer at the top is the rule: you check everything.** This section is about what the system
does to make that job smaller, and what it deliberately does not claim to do.

Everything that writes here is a language model, **including whichever model would review its own work.**
A model that found a figure plausible enough to write finds it plausible enough to approve. So the checks
are built on the assumption that the writer cannot audit itself, and there are three of them, asking three
different questions.

| | Asks | What it is |
|---|---|---|
| **`verify.py`** | **Is it true?** | Arithmetic and string matching against your wiki. No model, no network |
| **`oversight/`** | **Does it convince?** | A different vendor's model, reading only what a recruiter reads |
| **`--coverage`** | **What did you leave out?** | Your wiki and the job advert, compared against the CV |

---

### 1. The deterministic layer — `verify.py`

**No model is involved.** It reads your wiki, reads the outgoing document, and proves four things:

| Finding | What it means |
|---|---|
| 🔴 **UNSOURCED** | A figure appears in the CV and **nowhere in your wiki**. Treat it as invented until you prove otherwise |
| 🔴 **ATTRIBUTION** | A real figure is sitting on the **wrong employer**. Every sentence is true and the document still misleads. This is the error that survives every kind of review, because nothing in it reads as false |
| **UNVERIFIED** | The figure is in your wiki, but you have never confirmed it |
| **STALE** | It traces to a page whose review date has passed |

**It refuses to guess.** Attribution is read from an explicit field, never inferred from nearby text —
inference was built, tested, and produced confident nonsense, so when the data is missing the check
**reports itself as skipped** rather than quietly passing. **Read the SKIPPED lines**: a clean run with two
checks disabled means very little.

**You never run it.** A hook fires on every write or edit of a CV or cover letter, and the findings go
straight to the agent, which fixes them and triggers the check again. One rule governs the fixing, and it
matters: **an UNSOURCED figure is never resolved by adding it to the wiki.** That would launder an
invention into a source, and every future application would then treat it as evidence. It comes out of the
document, or you confirm it.

### 2. The oversight layer — a second opinion from a different AI

**Why a different one:** the point is not that another model is better. It is that its mistakes are not
*the same* mistakes. Two passes from the same model share the same blind spots.

#### How to use it

There is a folder called **`oversight`**. Open it in Gemini, ChatGPT or anything else, and say:

> **"Read OVERSIGHT.md and follow it. Review Acme R-12345."**

That is the whole procedure. The folder rebuilds itself every time a document changes, so it is never out
of date, and it contains one subfolder per application:

```
oversight/
    OVERSIGHT.md          <- the reviewer's instructions
    Acme R-12345/         posting, CV, cover letter, REVIEW-ID
    Globex R-4471/        posting, CV, cover letter, REVIEW-ID
```

#### What it gives you

Not a proofread. A structured, adversarial read in a fixed order: **fatal problems** that get an
application binned unread, **unsupported claims** with the follow-up question an interviewer would ask,
**generic lines** that would read identically on someone else's CV, **mismatches** between what the advert
asks for and what your documents lead on, **passages that read as machine-written**, and finally **the
strongest objection a hiring manager could make.** It ends with one line: `SEND`, `FIX FIRST` or
`DO NOT SEND`.

It is told not to rewrite anything, not to open with encouragement, and not to comment on whether claims
are *believable* — that is the deterministic layer's job and it is a different question from whether they
are *specific*.

#### Two rules, and neither is fussiness

> 🔴 **Open `oversight`. Never open your wiki.**
>
> Your wiki holds your salary floor, why you are leaving, and things you have said about colleagues.
> `oversight` holds only what the employer is going to receive anyway — so showing it to another company's
> AI costs you nothing at all.
>
> The brief also tells the reviewer to stay out of everything else, but **telling a model not to read
> something is not the same as it being unable to**, which is why the folder exists separately in the
> first place.

> 🔴 **Start a new chat for every review — including after you fix something.**
>
> Suppose it says a bullet is vague, you fix it, and you ask the same chat again. **It now knows what that
> bullet was meant to say, so the new version reads clearly to it — because it is completing the sentence
> from memory.** It approves something a recruiter would reject.
>
> **Its entire value is that it knows nothing about you.** Every turn of conversation spends some of that,
> which is why it also refuses explanations: *"that number is real, it's from the X project"* is context
> the recruiter will never have.

#### When it goes wrong, you are told

**No model can clear its own memory or start a new chat** — those are things only you can do. So instead
the system makes the failure visible.

Every folder carries a **`REVIEW-ID`**, a fingerprint of exactly those documents that changes the instant
any of them does. The reviewer must open its review with that line. Which means:

- **If it has already reviewed in that chat**, it finds its own earlier ID and refuses, instead of quietly
  doing a worse job.
- **If you edit anything afterwards**, hand the review back here and it gets filed — then the next time
  you touch that CV you are told by name: *your oversight review for this application was of the previous
  version, and its verdict no longer applies.*

**That second one is the failure most worth catching, because it is the comfortable one.** A genuine
verdict, from a real review, of a document you have since changed. **A pass you believe you have is more
dangerous than no pass**, because you will act on it.

### 3. Coverage — what you left out

`verify.py --coverage --posting` reads three things — your CV, your wiki and the job advert — and reports
the achievements **this employer's own language points at** that your CV does not carry.

**Most omissions are correct.** A two-page CV cannot hold everything, and it is reported separately from
the findings for that reason. The question it forces is **decision or oversight** — and the second kind is
how the best thing you have ever done stays invisible for years, because no single application happened to
ask for it and nobody ever looked at the set.

It matches words, not meaning: it cannot see that *"shipping cadence"* in an advert and *"release
management"* in your wiki are the same idea. So the agent is told to repeat the exercise itself
afterwards, with comprehension the script does not have. Anything you have marked as permanently excluded
stays excluded and is never raised.

### What none of this does

**It cannot tell you whether the document is good**, whether it is honest about things your wiki never
recorded, or whether you should send it. **A clean run means nothing was provably wrong by the checks that
ran.** Read it yourself. That is not a formality — it is the only step that actually establishes the
document is true.

---

## The scoring framework

Roles are scored on four dimensions, each borrowed from an established framework, plus two modifiers. The
point is not the total — it is that four different lenses disagree in useful ways.

### NEED — *Jobs-to-be-Done*

Clayton Christensen's idea that customers "hire" a product to get a job done. Applied to hiring, it
inverts: **an employer hires a role to solve a problem.**

A job description is a wish list written by committee. The role exists because something is going wrong
right now. So the question is not "am I qualified" but **"what are they anxious about, and is that my
ground?"** You find it in the ratios — four bullets on delivery predictability and one on technology means
they are missing dates and cannot explain why.

### DELIVER — *Topgrading Scorecard*

Bradford Smart's method: replace the job description with a **mission and a short list of measurable
outcomes** the hire must achieve.

Reverse-engineer that scorecard from the posting — what will this person be judged on in eighteen months?
Then, for each outcome, ask the harder question: **can you point at having done it before?** Not "could
I", but "have I, and can I describe it". This is where optimistic applications fall apart.

### EDGE — *Value Proposition Canvas*

Alexander Osterwalder's tool for matching what a customer needs against what only you relieve.

The key move is that it is **comparative**. The question is not whether you are good at something, but
**what is rare about you against the field who will actually apply for this role.** Twenty years in
regulated finance is unremarkable at a bank and highly unusual at a consumer tech company.

### WANT — *Schein's Career Anchors*

Edgar Schein's finding that people have one thing they will not give up, and usually cannot name it until
asked. There are eight:

| Anchor | In one sentence |
|---|---|
| Technical / Functional | You want to get better at the thing itself and be known for it |
| General Management | You want to run larger and larger parts of an organisation |
| Autonomy / Independence | You want to decide how you work without anyone's permission |
| Security / Stability | You want to know the job will still be there, and the pay predictable |
| Entrepreneurial Creativity | You want to build something that is yours |
| Service / Dedication | You want the work to be in aid of something you believe in |
| Pure Challenge | You want problems that look impossible |
| Lifestyle | You want work to fit around the rest of your life, not the reverse |

`/career-init` asks you to pick the one or two that actually govern, then pressure-tests the answer by
asking what you would have said three years ago.

**WANT scores those anchors and nothing else.** That constraint is deliberate, and it is the rule most
often broken — see below.

### The two modifiers

**PAY** is scored only where a figure is published, and left as `TBC` otherwise, to be resolved by asking
on the first call rather than guessed. **WIN** is your realistic odds: a perfect role you will not get is
worth less than a good role you might.

### And a pre-mortem

Gary Klein's technique: assume it is eighteen months later and the job went badly, then write down why.
Done before applying, it surfaces the objection you would otherwise meet at interview.

### Five rules that stop the number lying

1. **Shape beats total.** Two roles scoring 15 are not the same role. Read the dimensions.
2. **Anything scoring 2 or below is a veto candidate.** Check the total is not hiding it.
3. **There are two kinds of veto.** *Hard* — no salary fixes a three-hour commute. *Priced* — a commute
   you would accept for enough money. Confusing them either kills good roles or keeps dead ones alive.
4. **Do not let a preference masquerade as an anchor.** Interest, prestige and curiosity are not anchors.
5. **Count each risk once, in the right place.** Employer stability and work pattern belong in WANT.
   Whether you can do the job belongs in DELIVER. Whether it will wear you down belongs in the pre-mortem.
   The tell: **a WANT score whose justification never mentions one of your anchors is measuring something
   else.**

---

## Installing it

**If you have never used a terminal, this section is for you.** About fifteen minutes.

### 1. Get an Anthropic account

Sign up at [claude.ai](https://claude.ai). A paid plan or API credit is needed — this is not free to run,
and a full init plus a few applications uses a meaningful amount of usage.

### 2. Install Claude Code

Claude Code is the agent that reads and writes the files. **There are two ways to run it, and the desktop
app is the easier one if you are not comfortable in a terminal.** Both use the same engine and both work
identically with this repo.

The authoritative instructions, which stay correct if anything below changes, are at
**[code.claude.com/docs](https://code.claude.com/docs)**.

#### Option A — the desktop app (recommended if you are not technical)

Download and install:

- **[macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect)** — universal build,
  Intel and Apple Silicon
- **[Windows](https://claude.ai/api/desktop/win32/x64/setup/latest/redirect)** — x64. **Install
  [Git for Windows](https://git-scm.com/downloads/win) first**, then restart the app
- **Linux** — apt or .deb, see [the Linux guide](https://code.claude.com/docs/en/desktop-linux)

Then launch Claude, sign in, and **click the `Code` tab**.

> 🔴 **The `Code` tab, not `Chat`.** The desktop app has three tabs — Chat, Cowork and Code. Only **Code**
> can read your files and run the tools this repo needs. If you are typing into the ordinary chat window,
> none of this will work.

#### Option B — the terminal

**macOS or Linux** — open Terminal (on a Mac: press Command+Space, type "Terminal", press Enter) and
paste:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows** — open PowerShell and paste:

```powershell
irm https://claude.ai/install.ps1 | iex
```

**You can use both**, on the same folder, at the same time. They keep separate conversation histories but
share the same `CLAUDE.md` and the same wiki. To move a terminal session into the desktop app, type
`/desktop`.

### 3. Check you have Python

The job-search tool needs Python 3. macOS and most Linux systems already have it:

```bash
python3 --version
```

If that prints a version number you are fine. If it says "command not found", install it from
[python.org/downloads](https://www.python.org/downloads/). **On Windows, tick "Add Python to PATH"** in
the installer — it is easy to miss and nothing works without it.

### 4. Get this repo

**If you use git:**

```bash
git clone <this-repo-url> career-wiki
cd career-wiki
```

**If you do not:** click the green **Code** button on the GitHub page, choose **Download ZIP**, unzip it
somewhere sensible such as your Documents folder, and rename the folder to `career-wiki`. Then, in your
terminal:

```bash
cd ~/Documents/career-wiki
```

### 5. Add your CV

Copy your CV into the `sources` folder inside `career-wiki`. Dragging and dropping is fine.

**It does not need tidying up first.** A messy CV is more useful than a polished one, because the gaps are
informative. If you can also export your LinkedIn profile and drop that in, do — the two disagree
surprisingly often, and every disagreement is worth knowing about.

Nothing in `sources` is ever uploaded anywhere or committed to git. It stays on your machine.

### 6. Start

**In the desktop app:** open the `Code` tab, and before typing anything set the two things that matter in
the prompt area:

| Setting | Choose |
|---|---|
| **Environment** | **Local** — it needs to reach files on your own machine |
| **Project folder** | the `career-wiki` folder you just downloaded |

Then type `/career-init` and press Enter. Typing `/` at any point lists every command in this repo — they
are picked up automatically from the project folder, with nothing to install.

**In the terminal:** navigate to the folder and run `claude`, then type:

```
/career-init
```

#### Running the job search

Once you get to `/role-radar`, **just ask** — "run the radar for the last week" — and the agent runs the
script itself. You never need to type a command.

If you would rather watch it run, the desktop app has a built-in terminal: **Views → Terminal**, or press
**Ctrl+`**. It opens in your project folder already, so this works directly:

```bash
python3 tools/radar/radar.py --days 7
```

Or, to sweep everything still open rather than only the last week:

```bash
python3 tools/radar/radar.py --all-open
```

### 7. Check it is all set up

```bash
python3 tools/doctor.py
```

**It reads your files and says what is ready, what is optional, and what needs doing.** Most of it is
optional and says so — an unconfigured thing has not been tried, which is different from broken.

🔴 **The one it is really for**: a config file you copied from the example and never filled in. That
**looks configured and matches nothing** — the search runs, finds no roles, and reports a quiet week that
never happened. A missing file would have been louder.

It makes no network calls, so it is instant and works offline. To find out whether the job sources
actually answer, run `python3 tools/radar/sources_check.py`.

### 8. Optional but recommended — read the wiki in Obsidian

[Obsidian](https://obsidian.md) is a free app for reading interlinked markdown files. Open the
`career-wiki` folder as a vault and you can click through the wiki as it is written, follow the links, and
see how it all connects. The agent writes; you browse.

---

## Your first hour

**Expect a lot of questions.** That is the product, not a delay before it.

Roughly:

1. It reads your CV and tells you what it noticed. **If that reads like a summary of your own document,
   push back** — it should tell you something you did not know about it.
2. It scaffolds the wiki.
3. First interview round: reporting lines, decision rights, what the product is, who uses it.
4. Career anchors, then your salary floor and what it is for.
5. It builds your scoring framework from your answers.
6. It tells you the three most interesting things it learned that were not in your CV, and what it still
   does not know.

**It will not offer to write you a CV at the end of this, and that is deliberate.** There is not enough in
the wiki yet, and a CV written after one interview round is a reformatted version of the document you
already had. Run `/interview` a few more times first.

---

## Setting up job search

Search runs through adapters in `tools/radar/adapters/`. Copy `config.example.json` to `config.json` and
fill in what you have. `config.json` is ignored by git, so your settings stay on your machine.

| Adapter | What it needs | Notes |
|---|---|---|
| **adzuna** | A free API key from [developer.adzuna.com](https://developer.adzuna.com/) | Documented and supported. 🔴 **Check your country is covered before relying on it** — GB, US, NL, DE and others work; **Ireland is not covered and returns 404** |
| **greenhouse** | Employer board names | Public data, no key. Best for watching specific target employers |
| **lever** | Employer handles | Public data, no key. Same idea |
| **oracle** | Host and site, both read off the employer's careers URL | Public data, no key. The other large enterprise ATS. **Gives an exact posting date**, the requisition number, and a description in the listing itself. Verified against three live employers |
| **workday** | Host, tenant and site, read off the employer's careers URL | Public data, no key. **A large share of big employers run Workday**, including where the careers site looks bespoke. Returns the requisition number and the real posting date, and expands roles advertised in one city that are open in several. Verified against two live employers, one of each hosting style |
| **linkedin** | Nothing | **Off by default.** Uses an undocumented endpoint, is against LinkedIn's terms of service, and will break without warning. Enable knowingly or not at all |

You also set your location rules in the same file: which places are acceptable, which are not, and which
are borderline.

### 🟢 Name employers, not endpoints

**You should not have to know that watching Stripe means writing a Greenhouse board token and watching
State Street means writing a host, a tenant and a site.** So you do not:

```json
"watch": ["Stripe", "State Street", "Deel"]
```

**A shipped registry — [`tools/radar/ats_registry.json`](tools/radar/ats_registry.json) — knows which ATS each
employer uses**, and the endpoint is looked up at run time. **Fifteen employers, around 13,000 live roles,
every entry verified by calling it.**

**To see who is on it:**

```bash
python3 tools/radar/registry.py --list
```

Names, ATS, how many roles each had when last checked, and which employers publish a salary band. **It
reads the file and calls nothing**, so it costs nothing to look.

🔴 **Anything it cannot resolve is reported at the start of the run, by name.** An employer you thought you
were watching, quietly not searched, looks exactly like a quiet week — which is the worst thing a job
search tool can do to you.

**Adding one is a line:**

```bash
python3 tools/add_employer.py "Monzo" https://monzo.com/careers
```

It reads their careers page, works out which ATS is behind it, **calls the endpoint to prove it works**,
and writes the entry. If the page is JavaScript-rendered it tries the company name as a board token and
**asks you to confirm before trusting it** — a guess that verifies is still a guess.

🟢 **Then `--contribute` offers it upstream**, staging that one file and refusing if anything else in your
working copy has changed. **Everyone who adds an employer saves everyone else finding it.** It is the only
file here that is the same for everybody.

**And because endpoints die quietly:**

```bash
python3 tools/registry_check.py
```

**Every entry, called.** It fails on an endpoint that has gone empty, and **asks you to look** when a known
requisition has vanished — because it cannot tell a moved endpoint from a filled vacancy and does not
pretend to.

### Check the sources actually work — before you invest in any of them

```bash
python3 tools/radar/sources_check.py
```

**This exists because of a wasted hour.** Someone got an API key for a job board, wired it up, and only
then discovered the board does not cover their country at all — it returned "not found" there while
serving four other countries perfectly well. The hour went on debugging a key that was never broken.

So the check asks each source one question — *would you work, for this config, right now* — and it is
careful about two answers that look the same and mean opposite things. **"Not configured" is not
"broken"**: most of these sources watch employers you name, so an empty list means nobody is being
watched, which is a fact about your setup rather than a fault. And **"does not cover your country" is not
"your key is wrong"** — which cannot be told apart from a single request, so where it matters the check
also asks about a country the source is known to serve, and compares.

It runs no searches and reads no results, so it costs a request or two per source. It will tell you a
source answers; it cannot tell you it has *good* coverage where you live. That part is a judgement.

### Employers you want watched, and employers you do not

Copy `employers.example.json` to `employers.json` — it is optional, and without it nothing changes.

**Two lists doing different jobs.** The **watch** list gives you complete coverage of an employer rather
than whatever they choose to syndicate to job boards; you name the employer and give it whichever route
reaches them, and if there is no route the run tells you they are not being watched rather than quietly
implying they are. The **avoid** list filters before anything is scored, so an employer you ruled out
months ago costs nothing — and it works at division level too, because a company you would happily join
can contain a part of it you would not.

**Two smaller distinctions that turn out to matter.** An exclusion carries a *reason* and a *basis* —
"their published policy says so" and "someone who worked there told me" are both fair reasons and very
different kinds of claim, and the basis is what lets you re-judge it later. And a role you assessed and
turned down is **not** the same as an employer you rule out on principle: the first can come back, so it
marks the row with a dagger instead of hiding it.

🔴 **This file stays on your machine.** It names companies and says why you will not work for them, some
of it second-hand. It is gitignored, it is outside what the oversight export can carry, and the agent is
told never to suggest you repeat any of it. If anyone asks, "it is not the right fit for me" is the whole
answer.

**One thing worth knowing about Workday**, because it is the difference between a source that works and
one that silently misses employers: **host, tenant and site are three separate values and you cannot work
one out from another.** There are two hosting styles — `<tenant>.wd1.myworkdayjobs.com` and the shared
`wd1.myworkdaysite.com` — and all three values are visible in the employer's own careers URL. If a
configured employer returns a `422`, that means the tenant sits on a different shard: try `wd3` or `wd5`
in the host rather than changing anything else. The adapter says so when it happens.

**Oracle Cloud Recruiting needs two values, not three**, and both sit in the careers URL:
`https://<host>/hcmUI/CandidateExperience/en/sites/<site>/jobs`. Take them verbatim — some tenants carry a
region in the host and some do not, so there is no pattern to derive it from.

🟢 **And if an employer's careers site clearly is not Workday, check anyway.** Big employers often put a
different front end over a Workday back end, and the *Apply* links give it away — search the page source
for `myworkdayjobs` or `myworkdaysite`, and the host, tenant and site are all in the link.

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

## Sensitive data

**[`PRIVACY.md`](PRIVACY.md) is the full version. Read it before your first interview session.** The parts
that surprise people:

**There is no tier of this wiki that is private from the model.** Claude Code runs locally, but to answer
anything it sends the contents of the files it reads to Anthropic's API. Writing something into a file
rather than saying it out loud changes nothing. **If you want something kept out, the answer is not to
record it** — say so, and it will not be written.

**Check your data-training setting if you are on a Free, Pro or Max plan.** Consumer conversations are
used to improve models *only if that setting is on*, and retention is five years when it is, thirty days
when it is not. Team, Enterprise and API are not trained on. A wiki holding your employer's internal
detail deserves a deliberate decision rather than a default:
[claude.ai/settings/data-privacy-controls](https://claude.ai/settings/data-privacy-controls).

**Other people never consented to being in this.** Colleagues are recorded as roles — *"a senior developer
in the team"* — never as names, and **never at all** in a performance, capability or redundancy context.
That material is not CV content and the agent will not draft from it.

**Your own difficult material is handled as a constraint, not a reason.** *"Cannot commit to travel at
short notice"* is everything the scoring needs. Why is nobody's business, including this file's.

**A gitignored file is not an encrypted file.** Turn on FileVault or BitLocker, and think twice before
putting the wiki in Dropbox, iCloud or OneDrive — those will replicate your salary floor and your reasons
for leaving to a cloud account, possibly a work-managed one.

**`/career-lint` audits for all of this**, and ranks anything it finds above every other kind of problem.

---

## Honest limits

- **It cannot update your LinkedIn or Indeed profile.** Those require logging in. It writes the text and
  you paste it.
- **It cannot apply for jobs.** It builds the pack and prepares the form answers. You submit.
- **Salary is usually missing** from listings. Unknown is recorded as unknown, and you are told to ask on
  the first call rather than guess.
- **The search ranking is triage, not judgement.** A keyword tally decides what is worth reading, nothing
  more. Good roles do land low in it, which is why the shortlist gets read rather than trusted.
- 🔴 **It cannot tell you whether what it wrote is true.** The deterministic layer proves figures trace
  to your wiki; nothing proves your wiki is right. **Only you can do that**, and the disclaimer at the top
  is not boilerplate.
- **It cannot make anything private from the model.** See above. Local storage is not concealment.
- **It will not invent anything.** No metric, title or achievement you did not provide. Ask it to
  embellish and it will decline and explain why the claim would not survive a follow-up question.
- **It is not a lawyer, a doctor or an HR professional.** Redundancy rights, notice periods and
  discrimination get flagged as questions for a professional.

---

## Known gaps

**[`BACKLOG.md`](BACKLOG.md) records what does not work yet, what has gone wrong once, and what was
deliberately not done.** Worth reading before you rely on something: the largest gap is that **the system
stops at the submit button** — interview preparation, offers and negotiation are not covered.

## Using it and developing it at the same time

**Do not do both in the same directory.** The repo is public and holds only scaffolding; your vault is
private and holds your actual career. Keeping them apart means personal material has **no path** to the
public remote, rather than being ignored on the way out.

If you fork this to work on it, run once per clone:

```bash
git config core.hooksPath githooks
```

That installs two guards. A **commit** guard that refuses personal material **even if you force-add it** —
`.gitignore` alone does not survive `git add -f`, and a public git history is permanent. And a **push**
guard that runs the test suite and refuses the push if it is failing, because `main` is published the
moment it is pushed.

Full detail, including how to carry tool updates into your vault and how to migrate an existing wiki, is
in [CONTRIBUTING.md](CONTRIBUTING.md).

**And after any update, ask what your vault missed:**

```bash
python3 tools/template_drift.py --wiki wiki
```

Your wiki was built from the templates **once**, when you first set it up, and nothing revisits it
afterwards. When the templates gain a section — a new table the agent is told to keep, a row it is told to
score — **your pages do not get it**, and the agent ends up looking for something that is not there. This
says what is missing. It never edits your pages: putting a new section into a page that already holds your
history is a judgement, and that is the agent's job, not a script's.

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
