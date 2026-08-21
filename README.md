# Career Wiki

**An AI-maintained knowledge base for running a job search properly.**

You put your CV in a folder. An AI agent interviews you about what you actually do, builds a structured
wiki about your working life, works out what you genuinely want from a job, turns that into a scoring
system, finds roles, ranks them against *your* values, and writes a bespoke CV for each application worth
making.

You never write the wiki. You answer questions and make the decisions.

---

## Contents

- [The problem this solves](#the-problem-this-solves)
- [What it actually does](#what-it-actually-does) — including just pasting a job link
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
description of everything that survives, and tiers them. A separate `role-triage` agent does the reading,
so your main session does not fill up with job adverts, and hands back a ranked shortlist carrying the
reasoning and the strongest objection for each role.

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

### Two checking layers that are not models

**Everything above is probabilistic, including whichever model wrote your CV.** A model that invented a
figure while writing will find it plausible while reviewing. So the last two passes are built on the
assumption that the writer cannot be trusted to check itself.

**`tools/verify.py` — the deterministic layer.** No model, no network. It reads your wiki and proves four
things about an outgoing document:

| | |
|---|---|
| **UNSOURCED** | A figure appears in the CV and nowhere in the wiki. **Treat as fabricated** |
| **ATTRIBUTION** | A real figure is sitting on the wrong employer. **Every sentence is true and the document still lies.** This is the error that survives every kind of review |
| **UNVERIFIED** | It is in the wiki, but nobody confirmed it |
| **STALE** | It traces to a page whose `stale_after` has passed |

It refuses to guess. Attribution is read from an explicit `employer:` field, never inferred from nearby
text — inference was tried and produced confident nonsense, so when the field is missing the check
**reports itself as skipped** rather than passing.

**A second opinion from a different AI — and you do not have to set anything up.**

Every time a CV or cover letter is written, a folder appears at:

```
review-exports/<Employer Requisition>/
```

It holds three things and nothing else: the job advert, the documents being submitted, and `OVERSIGHT.md`
— a brief telling a reviewer what it may read, what it must not, and what to report. **Open that folder in
Gemini, ChatGPT or whatever you like and say:**

> **"Read OVERSIGHT.md and follow it."**

That is the whole procedure. Nothing to run, nothing to remember. The folder is rebuilt on every edit, so
it is never out of date.

> 🔴 **Open the `review-exports` folder, never your wiki folder.**
>
> This is the one thing worth being careful about. Your wiki holds your salary floor, why you are leaving,
> and things you have said about colleagues. `review-exports` holds only what the recruiter is going to
> receive anyway, so showing it to another company's AI costs you nothing.
>
> The brief also *tells* the reviewer not to go looking — but telling a model not to read something is not
> the same as it being unable to, which is why the folder exists separately at all.

**`tools/review/` — the same review, automated.** An optional second model, ideally from a different vendor,
reads the posting and your documents and reports what is unsupported, generic or mismatched. **It never
sees your wiki** — it gets exactly what a recruiter gets, which is both the point and the privacy
position. No API key needed to use it: `--dry-run` prints the prompt for you to paste anywhere.

**Where the two disagree, the deterministic layer wins.** It checks facts; the reviewer checks
impressions.

**And a third question neither of those asks: what did you leave out?** `verify.py --coverage --posting`
reads all three — your CV, your wiki and the job spec — and reports the achievements this employer's own
language points at that your CV does not carry. Most omissions are correct — a two-page CV
cannot hold everything. But it forces the question **decision or oversight**, and the second kind is how
the best thing you have done stays invisible for years because no single application happened to call for
it. Anything marked `exclude_from_cv: true` stays excluded permanently.

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

### 7. Optional but recommended — read the wiki in Obsidian

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
| **adzuna** | A free API key from [developer.adzuna.com](https://developer.adzuna.com/) | Documented and supported, with good UK/Ireland/US coverage. **Start here** |
| **greenhouse** | Employer board names | Public data, no key. Best for watching specific target employers |
| **lever** | Employer handles | Public data, no key. Same idea |
| **linkedin** | Nothing | **Off by default.** Uses an undocumented endpoint, is against LinkedIn's terms of service, and will break without warning. Enable knowingly or not at all |

You also set your location rules in the same file: which places are acceptable, which are not, and which
are borderline.

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
- **It cannot make anything private from the model.** See above. Local storage is not concealment.
- **It will not invent anything.** No metric, title or achievement you did not provide. Ask it to
  embellish and it will decline and explain why the claim would not survive a follow-up question.
- **It is not a lawyer, a doctor or an HR professional.** Redundancy rights, notice periods and
  discrimination get flagged as questions for a professional.

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
