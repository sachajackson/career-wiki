---
name: pre-submit
description: The last check before clicking submit on an application. Run it with the form open. Catches the things that are unfixable once sent.
---

# pre-submit

**Run this with the form open and everything filled in, before the button.**

Everything here is unfixable afterwards. An application is the one artefact in this system with no undo:
the recruiter's first read is the only first read there is, and nobody writes back to say which line lost
it.

**Work through it in order. Report what passes as well as what fails** — a check that only ever produces
problems stops being run.

---

## 1. Is it still the right decision?

**Ask once, plainly, and accept the answer.**

- **Does it still clear the threshold?** If the score moved since the pack was built — a work pattern
  confirmed, a salary discovered — say so now. **A role that dropped below the bar is worth ten minutes of
  awkwardness, not three weeks of process.**
- **Is anything still unknown that would decide it?** If the deciding fact is unresolved, applying is
  usually still right, but they should know they are applying to find it out.
- 🔴 **Is the posting still open?** Check again if the pack was built more than a few days ago.

## 2. Consistency across every surface

**This is the check with the highest catch rate, because a recruiter can do it in thirty seconds.**

Compare the CV, the form, LinkedIn and any other public profile on:

| | Common failure |
|---|---|
| **Job titles** | The form takes the **title of record**; the friendlier translation belongs in descriptions. Title fields can feed employment verification |
| **Dates** | Month and year on every role, matching across surfaces. **A parser that merged two roles at one employer silently claims a title held years longer than it was** |
| **Team sizes and scope** | The stale figure on a profile against the current one on the CV |
| **Geography** | Countries no longer relevant, still listed |
| **Headline achievements** | The same number attached to different roles in different documents |

**Anything that disagrees gets fixed now, or the profile gets fixed before submitting.** Which one is
correct is the applicant's call, not yours.

## 3. Claims

- 🔴 **Every claim human-verified?** Anything unverified in the CV or the free-text answers gets flagged
  **now**, by name, with the sentence it appears in. Ask directly: *can you defend this in an interview?*
- **Every number on the right role?** Attribution drift is invisible until two documents are read side by
  side.
- **"I built" versus "my team built"** — checked in every sentence.
- **Nothing claimed that the cover letter concedes.** A skills tag contradicting the letter it is attached
  to is worse than no tag.

## 3.5 Run the deterministic layer

```bash
pdftotext -layout "<the CV>.pdf" - | python3 tools/verify.py - \
    --wiki wiki --employer "<Employer>" --employers "<all past employers, comma separated>" \
    --ban "<anything the cover letter concedes>" --spelling us|uk
```

**Every model in this pipeline is probabilistic, including whichever one wrote the CV and whichever one
reviews it.** A model that invented a figure while writing will find that figure plausible while
checking. So the last check on the way out is arithmetic and string matching against the wiki, which has
no opinion.

It proves four things a reader cannot:

| Finding | Means |
|---|---|
| **UNSOURCED** | A figure in the document exists nowhere in the wiki. **Treat as fabricated until proven otherwise** |
| **ATTRIBUTION** | A real figure is sitting on the wrong employer. **Every sentence is true and the document still lies** |
| **UNVERIFIED** | The figure is in the wiki but nobody has confirmed it |
| **STALE** | It traces to a page whose `stale_after` has passed |

🔴 **Read the SKIPPED lines.** If the wiki lacks `employer:` or `verified:` fields, the two most valuable
checks silently do not run, and a clean result means nothing. **Fix the wiki rather than accepting the
pass.**

**A clean run is not approval.** It means nothing is provably wrong. Judgement is still yours.

**Add `--coverage`** to also list wiki achievements absent from the document. **These are not findings** —
a two-page CV cannot carry everything and leaving things out is usually correct. The question it forces is
whether each omission was **a decision or an oversight**, and the second kind is how good material stays
invisible for years. It respects `exclude_from_cv: true` and skips anything past its `stale_after`.

## 3.6 Optional: an independent second opinion

```bash
python3 tools/review/review.py --posting job.txt --cv cv.txt --letter letter.txt
```

**A second model, preferably from a different vendor**, reads the posting and the outgoing documents and
reports what is unsupported, generic, mismatched or machine-sounding. **It is not about one model being
better — it is about the failure modes not being correlated.** A model that found a phrasing natural
enough to write will find it natural enough to approve.

🔴 **The reviewer never sees the wiki, and this is deliberate.** It gets only what the recruiter will get.
A reviewer who has read the wiki judges the CV against what it knows to be true, which is the wrong test —
and sending the wiki to a third-party API would be a serious privacy escalation for a marginal gain.

### Reviewing in another vendor's tool

**The portable route, and the one to prefer** — no API key, and the applicant sees the review happen:

```bash
python3 tools/export_review.py "<the application folder>"
```

That builds a folder **outside the wiki** containing only the posting, the outgoing documents and
`OVERSIGHT.md`. Open **that folder** in Gemini, ChatGPT or anything else and say:

> *Read OVERSIGHT.md and follow it.*

🔴 **Export rather than pointing the other tool at the application folder directly.** `OVERSIGHT.md` tells
the reviewer not to read the wiki, but **an instruction to a model is not a boundary** — an application
folder inside the wiki is one `cd ..` away from the applicant's salary floor and their notes about
colleagues. The export makes containment a property of the filesystem instead. `application.json` is
withheld deliberately: `do_not_claim` is a list of their gaps.

**Bring the review back here. Do not let the other tool edit anything.**

**No API key? Use `--dry-run`**, which prints the prompt and sends nothing. Paste it into any chat
interface. That works just as well and costs nothing.

**Its verdict is an opinion from something that has never met the applicant.** Weigh it; do not obey it.
Where it contradicts the deterministic layer, **the deterministic layer wins** — it is checking facts,
the reviewer is checking impressions.

## 4. Confidentiality

Run the sensitive-data rules from `CLAUDE.md` over **the outgoing documents**, not the wiki:

- **No named individuals** other than the applicant.
- **No client-identifying names**, and no internal codenames left un-genericised.
- **Nothing from a personnel or redundancy context**, in any form.

**This is the last point at which any of it can be stopped.**

## 5. The documents themselves

- **Correct employer and role named** — in the letter, in the filename, everywhere. **Naming the previous
  employer you applied to is fatal and it happens constantly.**
- **Filenames are for the reader**: `<Full Name> - <Document> - <Employer> <Requisition>`.
- **Right files, right slots.** Upload the PDF. **Confirm the second attachment actually uploaded** — the
  additional-documents slot fails silently far more often than the CV slot.
- **Pre-release check clean**: `python3 tools/cv_lint.py`, plus spelling matched to the employer.
- **Page count** as intended.

## 6. The form's own answers

- **Knockout questions answered exactly as asked** — right to work, sponsorship, notice, salary. **Read
  the sponsorship question twice.**
- **Free-text answers within the character limit**, and not the cover letter pasted in.
- **Every auto-parsed field re-read.** The parser is mediocre and it ships whatever it mangled under the
  applicant's name.
- **Salary field** consistent with `Standing Answers.md`. A single base figure if mandatory; blank if not.

## 7. Route

- **No duplicate submission.** Has an agency sent them to this employer recently? See
  `/build-application` step 0.5.
- **Referral attached if there is one** — after the fact is usually too late.
- **Applying as themselves**, not through an agency who has not been given per-employer permission.

---

## Then, and only then

Tell them it is ready, and say what you checked rather than just "looks good."

**Immediately after they submit**, do the bookkeeping while it is fresh:

- Update the status and **the date** in the scoring table.
- Record the **decisive question to ask on the first call** — the work pattern, the salary band, whichever
  fact the assessment left open.
- 🔴 **Flag anything already known to be wrong in what just went out.** It cannot be fixed, which is
  exactly why they need to know before an interviewer raises it.
- Append to `log.md`.
