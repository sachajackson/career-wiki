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
- **Backfilling `verified:` wholesale.** A claim marked verified for convenience is worse than one honestly
  marked unverified. It accumulates as the user confirms things, or not at all.
