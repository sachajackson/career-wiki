---
name: career-lint
description: Health-check the career wiki — contradictions, expired claims, unverified assertions used externally, orphan pages, and gaps worth filling.
---

# career-lint

Run periodically, and **always before a batch of applications**.

## What to check

**1. Expired claims.** Every page whose `stale_after` has passed. Report them; do not silently refresh a
date without confirming the underlying fact still holds.

**2. Unverified claims doing external work.** Cross-reference: anything with no `verified` key that
appears in a CV, cover letter or profile draft. **These are the dangerous ones** — a confident sentence
nobody has confirmed, sitting in front of a recruiter.

**3. Contradictions between sources.** Two of the user's own documents disagreeing is a finding, not an
error. Record both, flag it, and let them settle it. **Check the deliverables too** — the same claim
attached to different roles across application packs is the classic version of this, and it is invisible
until someone reads two of them side by side.

**4. Numbers on the wrong role.** Every quantified claim should trace to a specific role in a specific
period. Attribution drift happens when a bullet is written from the angle rather than from the page.

**5. Orphans and gaps.** Pages nothing links to. Concepts mentioned repeatedly with no page. Open
questions that have been open a long time — some are answerable in one message.

**6. The scoring table.** Roles with no posting URL. Statuses that have not been updated. Scores whose
justification no longer matches the reasoning on the role page.

## How to report it

**Ranked by what could actually cause damage**, not by how many there are. An unverified claim in a
submitted CV outranks fifty missing cross-references.

For each: what it is, where, why it matters, and the specific fix. Then apply the ones that are
unambiguous and ask about the rest.

**Do not fabricate work.** If the wiki is healthy, say so in a sentence. A lint that always finds ten
things is a lint nobody trusts.
