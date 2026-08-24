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

## 🔴 Defects — things that behave wrongly

### The radar's SIGNAL number reads like a framework score

**Status: partially fixed 2026-08-22. The confusion is real and recurred in practice.**

`radar.py` produces an unbounded keyword tally. The Role Scoring Framework produces a score out of 20.
**Both were called "score", and a radar output of 21 was reported to the user as though it were a
framework score of 21 — which is impossible, and the user rightly caught it.**

Done: the column is now `SIGNAL`, and every shortlist carries a header explaining it is not the framework
score.

**Still to do:**
- The `role-radar` skill says the two must never be conflated, and it happened anyway. **An instruction
  that has already failed once needs a structural fix**, not a stronger instruction. Consider a
  non-numeric signal — `HIGH`/`MED`/`LOW` — so the two cannot be confused even by accident.
- `verify.py` and `cv_lint.py` also print counts. Check nothing else looks like a score.

---

## 🟡 Gaps — things the system does not do yet

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

### 🟢 Employer research should be a step, not an afterthought — designed, not built

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
  produced one more Tier A. **Frequency beats breadth.**

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
