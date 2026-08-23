# Backlog

**Known gaps, deferred decisions, and things that have gone wrong once.** Anything found while using the
system that is worth fixing but not worth stopping for.

**Add to this rather than fixing in passing when the fix would derail what you are doing.** A gap that is
written down is a decision; a gap that is remembered is a risk.

Newest first within each section. Delete an item when it is done — the log of what changed lives in git.

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
