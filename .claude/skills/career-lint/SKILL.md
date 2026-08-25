---
name: career-lint
description: Health-check the career wiki — contradictions, expired claims, unverified assertions used externally, orphan pages, and gaps worth filling.
---

# career-lint

Run periodically, and **always before a batch of applications**.

## Run the mechanical half first — it takes seconds and needs no judgement

**If anything looks unconfigured, or the user is new, start here:**

```
python3 tools/doctor.py
```

🔴 **`PLACEHOLDER` is the finding that matters.** A config copied from its example and never filled in
**looks configured and matches nothing** — the radar runs, finds nothing and reports a quiet week that
never happened. **`OPTIONAL` is not a fault** and must not be reported as one: most of the setup is
optional, and telling someone to fix what they never wanted is how a check gets ignored.

```
python3 tools/wikilinks.py wiki
```

🔴 **Three ways a link fails without looking broken**, and the checker finds all three: **split across two
lines** by a wrapping convention, so it renders as literal text; **pointing at a page that does not exist**;
and **pointing at a heading that has since been renamed** — the quietest of the three, because the link
still opens the right page and silently lands at the top.

**`--fix` repairs the wrapped ones.** The other two need judgement: a missing page usually wants writing,
and a renamed heading wants repointing at whatever replaced it.

**And after pulling any update to the tools:**

```
python3 tools/template_drift.py --wiki wiki
```

🔴 **`/career-init` copies `templates/` into `wiki/` once and nothing ever revisits it**, and
`sync-to-vault.sh` refuses to touch `wiki/` on purpose — that directory is the person, not the tool. So
the tool improves and the vault does not. **In one real change the framework template gained two tables,
two seeded rows and a longer status vocabulary, and `SCHEMA.md` was updated to instruct the agent to use
all of them** — leaving every older vault with an agent looking for tables that are not there.

🔴 **Two of those five were rows inside a table the vault already had**, which is why the check compares
seeded rows and not just sections. **A section-level check walks straight past that case.**

🟢 **Findings here are not errors and the tool will not fix them.** Merging a new section into a page that
holds a real person's history is a judgement — where it goes, what carries over, whether an existing note
belongs under it. **You own these pages; do the merge, and say what you added.** 🟡 And a clean run means
the *structure* matches, **not** that a section's contents are current.

**And monthly, or before relying on a quiet radar run:**

```
python3 tools/registry_check.py
```

🔴 **An employer changes ATS and their entry starts returning nothing — which looks exactly like a quiet
week.** That is the worst failure a job search can have, because the tool reports success and the user
concludes the market is dead. **`EMPTY!` and `COLLAPSED!` are failures. `CANARY GONE` and `UNPROVEN` are
asked of a human**, because the check cannot tell a wrong endpoint from a filled vacancy and does not
pretend to.

**And once, after any change to the tools:**

```
python3 tools/tests/run.py
```

**If those fail, stop.** The checks being tested are the ones that catch a fabricated figure and a real
achievement attached to the wrong job.

## 🔴 Check the outcomes first, because nothing else in the system will

**Every application with a `Submitted` status and no recorded outcome. Ask about each one by name.**

🔴 **This is the check most likely to be skipped, because nothing triggers it.** An employer replying, or
not replying, happens outside the system. Nobody logs it unless asked, and **an instruction to "track
outcomes" has been shipped and ignored before** — the applications get recorded, the results do not.

| Submitted | Then |
|---|---|
| **Over 7 days ago, nothing recorded** | Ask: any acknowledgement, rejection, or silence? |
| **Over 21 days, still nothing** | **Record `no response` as an outcome.** Silence is data, and leaving it blank makes it look unasked rather than unanswered |
| **Any outcome at all** | Log it with the `outcome` prefix, and put the reason on the role page if one was given |

🔴 **Use a status vocabulary that distinguishes who decided.** *"Rejected"* meaning both *the employer
turned them down* and *they chose not to apply* makes the table unable to answer the single most important
question about the search:

**Submitted · Rejected by employer · Withdrew · Declined · Closed · Vetoed · Not applied**

🟢 **A rejection with a reason is worth more than a silent success**, and **patterns only appear across
several.** If three applications sharing one weakness all fail at screening, that changes the framework
rather than being three separate disappointments.

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

**5. Sensitive data.** 🔴 **Rank this first when it finds anything.** Scan for material that should not
be there under `SCHEMA.md`:

- **Named individuals other than the user.** Any proper noun in a personnel, performance or team-structure
  context. Rewrite to the role, or remove.
- **Identification by elimination** — a description narrow enough to name one person without naming them.
- **Client-identifying names** appearing in a generated CV, cover letter or form pack rather than only in
  the wiki. **Check the deliverables, not just the pages.**
- **Reasons where a constraint would do** — personal circumstances recorded alongside a limit that stands
  on its own.
- **Referee contact details** anywhere.

Report these before anything else, with the exact file and line, and offer to fix each one. **Do not
"tidy" them silently** — the user needs to know what was recorded and where it went.

**6. Orphans and gaps.** Pages nothing links to. Concepts mentioned repeatedly with no page. Open
questions that have been open a long time — some are answerable in one message.

**7. The scoring table.** Roles with no posting URL. Statuses that have not been updated. Scores whose
justification no longer matches the reasoning on the role page.

## How to report it

**Ranked by what could actually cause damage**, not by how many there are. An unverified claim in a
submitted CV outranks fifty missing cross-references.

For each: what it is, where, why it matters, and the specific fix. Then apply the ones that are
unambiguous and ask about the rest.

**Do not fabricate work.** If the wiki is healthy, say so in a sentence. A lint that always finds ten
things is a lint nobody trusts.
