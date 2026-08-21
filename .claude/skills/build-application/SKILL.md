---
name: build-application
description: Build a bespoke CV, cover letter and ATS field pack for one specific role. Use when the user decides to apply for something.
---

# build-application

One role, one pack. **There is no master CV and there should not be one** — each CV is assembled on demand
from the wiki, which is the persistent raw material. A master CV is a document that is wrong for every
application instead of right for one.

## Step 0 — is the posting still open?

**Check before building anything.** Roles close. Twenty minutes of work on a dead requisition is twenty
minutes gone, and it happens more often than it should.

If a fetch fails, say what failed rather than concluding. **A 403 is not evidence of closure**, and a
careers site that will not render for an automated browser tells you nothing about the role. If you cannot
resolve it, ask the user to check while logged in.

## Step 1 — read the posting properly, then write it down

Create a role page in `wiki/roles/`. Capture the **requisition number and posting URL** — both are often
only on the employer's own site, and the aggregator listing will vanish.

Then work out what they are actually anxious about. A job description is a wish list; the role exists
because something is going wrong. Name it, then check what the wiki has against it.

**Score it** on the framework and place it in the table.

## Step 2 — pick the angle

**The angle is the whole job.** Ten CVs built from identical material should open in ten different places.
If two of them open the same way, one is not tailored.

Ask: what is the first bullet of the current role? That single choice is the application's argument.

| If the posting is about | Lead on |
|---|---|
| Scale and portfolio | What they own and how big it is |
| Process and control | Decision rights — what they personally sign off |
| People | Team shape, retention, who they have grown |
| Building | What they made themselves, and what it returned |
| Teaching or enablement | What they can transmit, not what they own |

## Step 3 — write it

🔴 **Read `WRITING.md` in this skill's folder first.** It carries the content rules, the cadence rules
that decide whether a document reads as generated, the banned constructions, and the pre-release
checklist. **Do not draft from memory of it — open it.**

**Ask once, early, whether the user has their own writing standard.** If they do, theirs wins and
`WRITING.md` is the fallback. Keep it in the wiki so it survives the session.

## Step 4 — the cover letter answers the hardest question first

Whatever a sceptical reader would object to, open on it. Do not bury it.

**Conceding a named requirement you fail is often the strongest move available**, especially where the
posting contradicts itself — a "reasonable technical fluency" overview against a hard skills list in the
minimums. Naming the gap forces the hiring manager to decide which role they are recruiting for, which is
the question that decides the application anyway. It is also the only version that survives an interview.

## Step 5 — the ATS pack

**Recruiters search structured fields, not attachment contents.** A form filled in thinly wastes the
application. Produce a paste-ready file, `<Employer> <Req> - ATS Notes.md`, with:

- **Every role as a discrete entry**, including promotions as separate entries — the form has no page
  limit, and two entries show a promotion that one entry hides
- **Description text unwrapped** — one unbroken line per paragraph. Hard line breaks survive a paste and
  look broken
- **The employer's spelling**, and the keyword cluster this specific role screens on
- **Skills tags: only things the user could do today.** A structured tag is an unqualified claim with
  nowhere to put the qualification that would make it true. Governing an estate is not fluency in it
- **An explicit do-not list** of anything the cover letter concedes. A tag contradicting the letter it is
  attached to is worse than an absent tag
- **A pre-submit checklist**, including: re-read every auto-parsed field, and check the current role did
  not merge with a previous one when the CV was parsed

## Step 6 — produce the actual document

**Write the CV as HTML using `templates/cv.html`**, then have the user print it to PDF from their browser
(Cmd/Ctrl+P → Save as PDF). The template carries print CSS with correct margins and page control.

**This route is deliberate.** It needs nothing installed, works identically on macOS, Windows and Linux,
and gives full typographic control. Generating .docx requires a library and converting it requires an
office suite — both are platform-specific and both fail on someone else's machine.

**If the employer's form demands .docx specifically**, say so and let the user decide: many accept PDF,
and a PDF parses more predictably in an ATS than a .docx built by a library.

Open the HTML yourself to check it before handing it over. **Confirm the page count rather than assuming
it** — a CV that silently runs to three pages is a real failure.

## Step 7 — the pre-release check

**Two passes, and they catch different things.**

**Mechanical first:**

```bash
pdftotext -layout "cv.pdf" - | python3 tools/cv_lint.py -
```

That checks characters, banned vocabulary, participial tails, round-number tells, US spelling and bullet
cadence, and it exits non-zero if anything is flagged. **Run it against the extracted PDF text, not the
source** — that is approximately what an applicant tracking system receives, and if the name is missing or
the dates have vanished, fix the source file before sending anything.

**Then judgement**, using Part 3 of `WRITING.md` — the audit prompt. **Run it in a fresh session.** A model
that just wrote the copy will defend it. It covers the things no script can check: the swap test, the
stranger test, the interview test, and whether every number sits on the right role.

Then file a **Deliverables** table on the role page linking every file, update `log.md`, and hand them
over. **Deliverables get no frontmatter and are not listed in `index.md`** — they are point-in-time
artefacts, not knowledge.
