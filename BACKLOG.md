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

**Rewritten 2026-08-28, and renumbered the same day as items 4 and 6 shipped.** The previous version listed two items as done and pointed at entries marked ✅
further down — which had all moved to [`docs/SHIPPED.md`](docs/SHIPPED.md), so it was directing a reader
at nothing.

| | Why here |
|---|---|
| 🔴 **1. Republish the repository** | Above. **Blocks the public launch and nothing else on this page outranks it** |
| 🔴 **2. Decide the cover-letter repo link** | Coupled to the item above: a letter already sent carries the URL, so the recreate has to keep the name **and** the policy has to be settled before the next application repeats it |
| **3. A browser dashboard** | The largest open piece, and the one the user asked for. ~96 scored rows that nothing can sort |
| **4. A next action per application** | Small. The cadence is built; the state is not |
| **5. Everything after the submit button** | Large and deliberately scoped out so far |
| **6. Email alerts as a universal source** | Designed, not built. Needs a dedicated account before any code |
| 🔴 **7. Nothing has been run end-to-end from a cold start** | Last only because it is a session of work, not a change. **It is the one that will find things nothing else can** |

🔴 **The sequencing is the user's, decided 2026-08-28**, and three of these are coupled rather than
merely ordered:

| | |
|---|---|
| **1 and 2 go together, and go LAST** | The repo is republished with the cover-letter policy already settled, so the recreate happens once and the next application does not repeat the question |
| **3 waits for them** | A dashboard built before the republish would be built against a repo that is about to be replaced |
| **4 and 5 go together** | Both are post-submit. Building the state without the process around it is guessing at what the state should hold |

🟡 **A user guide is deliberately absent from this order** — see its entry for the trigger that starts it.

## 🟢 Defects — none open, 2026-08-28

**Every entry that was under here has shipped.** Records in [`docs/SHIPPED.md`](docs/SHIPPED.md).
🔴 **That is a statement about this file, not about the system** — it means nothing is *recorded* as
behaving wrongly, which is only as good as the last time somebody looked.

## 🟡 Gaps — things the system does not do yet

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
