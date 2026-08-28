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
