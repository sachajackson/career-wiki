---
name: career-init
description: Bootstrap a new career wiki from scratch — read the user's CV, scaffold the wiki, run the first interview, and elicit their career anchors and salary floor. Run this once, first.
---

# career-init

> ## 🔴 THE ORDER COMES FIRST
>
> ```bash
> python3 tools/runbook.py init
> ```
>
> **Everything else in this file is a caveat, not a sequence.** 🔴 **Read the order, then read the rest when a step raises a question** — the reverse is how the `role-triage` delegation, named twice in the radar skill, went unused for the life of this repo. **An agent reading prose picks up whatever it happens to land on.**

Turns an empty repo and a CV into a working career wiki. **Run once.** Takes an hour, most of it
conversation.

## Before anything

🔴 **If `vault/wiki/` already has pages, stop and run `/career-migrate` instead.** This skill assumes an
empty vault: it scaffolds templates over whatever is there and interviews from zero. On somebody who
already has a wiki that means **overwritten pages and an hour of questions they have already answered**.

Check `vault/sources/` contains at least one CV or profile export. If it is empty, stop and ask for one — every
other step depends on it. **Ask for a LinkedIn export too** if they have one: the two documents disagree
surprisingly often, and the disagreements are findings.

## 1. Read, then say what you found

Read everything in `vault/sources/`. Then, **before writing any files**, tell the user what you noticed:
gaps in the timeline, claims without numbers, roles described in a sentence that sound like they deserve
a page, anything that contradicts something else.

**This first response sets expectations.** If it reads like a summary of their CV, you have wasted it.
It should tell them something about their own document they did not know.

🔴 **Then file them, in the same session.** This repo has already lost work exactly here — assessments that
existed only in a reply and were never written down get re-derived from scratch weeks later. **A finding you
say out loud is not recorded.**

| Finding | Where it goes |
|---|---|
| A gap, a contradiction, a CV-versus-LinkedIn disagreement | **`CV.md`**, on the timeline, with which source you followed and why |
| A number with nothing behind it | **`CV.md`**, recorded as the claim **and** as unsourced. 🔴 **Never resolve it by writing the figure in as fact** |
| A role compressed into one sentence | **`Operating Model.md`** as an open question, and ask about it in round 1 |

🟡 **Ask about the disagreements rather than resolving them.** The user knows which document is right, and
which one they would rather a recruiter saw.

## 2. Scaffold

**Place `templates/vault-AGENTS.md` at `vault/AGENTS.md` first, unedited.** It is the user's standing
instructions to you — tone, lines they will not cross, corrections you must not repeat — and it is the
one file in the vault an update never touches.

🔴 **Do not try to fill it in from the sources.** Every section is deliberately empty: its content comes
from corrections the user makes over months, and a plausible guess written in on day one reads like a
rule they set and will be followed as one. Say the file exists and what it is for. That is all.

**From then on, when the user corrects you, write the rule into `vault/AGENTS.md` with the date and the
reason** — in their words, not a paraphrase.

Then copy the rest of `templates/` into `vault/wiki/`, filling in what the sources support:
`index.md`, `log.md`, `Career.md`, `Operating Model.md`, `CV.md`, `Standing Answers.md`,
`Role Scoring Framework.md` and `Search Findings.md` — **plus a `roles/` folder.** OKF frontmatter on
everything, per `SCHEMA.md`.

🟡 **`Search Findings.md` starts empty and that is correct.** It fills up once roles are being scored, and it is the page that stops the same conclusion being re-derived from scratch every few weeks.

**Mark everything drawn from a document as unverified** — no `verified` key. It becomes human-reviewed
only when the user confirms it in conversation. Most of it will turn out to be slightly wrong.

## 3. Interview — round 1

Run the first round from `/interview`. Six to eight questions about shape: reporting lines, decision
rights, what the product is, who uses it, headcount and geography.

**File the answers before moving on.** Do not stack rounds.

## 4. Elicit the anchors — the part that makes this system yours

Everything downstream depends on this and it cannot be inferred from a CV.

**Use Schein's career anchors.** Give one plain sentence each and ask them to pick the one or two that
actually govern, not the ones that sound best:

| Anchor | One sentence |
|---|---|
| Technical/Functional | You want to get better at the thing itself and be known for it |
| General Management | You want to run larger and larger parts of an organisation |
| Autonomy/Independence | You want to decide how you work without anyone's permission |
| **Security/Stability** | You want to know the job will still be there, and the pay predictable |
| Entrepreneurial Creativity | You want to build something that is yours |
| Service/Dedication | You want the work to be in aid of something you believe in |
| Pure Challenge | You want problems that look impossible |
| **Lifestyle** | You want work to fit around the rest of your life, not the other way round |

**Then pressure-test the answer.** Ask what they would have said three years ago. If it has not changed,
it is probably real. If it has, ask what changed.

**Then ask the questions that put a number on it:**

- What is the minimum base salary that makes a move worth doing, and what is that number *for*?
- Where do you live, and what commute is genuinely tolerable — most days, not on a good day?
- Is there a deadline on any of this?

**The "what is that number for" question matters more than the number.** A floor tied to a concrete
obligation with a date behaves completely differently from a floor that is a preference: it makes
starting salary dominate progression, and it makes illiquid equity a poor substitute for cash.

## 5. 🔴 Capture the baseline — the step most easily skipped, so it is no longer last

**Before any role can be scored, record what the user has now.** 🔴 **This used to sit after *Close the
loop*, at the bottom of the file — the skill called it the most easily skipped step and then placed it
where it was guaranteed to be skipped.** It is a numbered step now, and it comes before the framework
because the framework scores against it. Every LIFE and SEC score is measured
against it, and without it the framework reports *"best of what we found"* as *"best available"*.

| Ask | Why it matters |
|---|---|
| **Days in an office now, and is that contractual or custom?** | 🔴 **A pattern in writing is a floor. A custom the employer could reverse is not** — and the difference changes what every alternative is worth |
| **The commute today** — door to door, and is the time usable? | The unit every other commute is compared against |
| **Notice period** | The binding constraint on every timeline. **Volunteer it early in a process, never at offer stage** |
| **Unvested equity, and what leaving forfeits** | This is the price of an external move, and **it is what an internal move does not cost** |
| **Length of service** | Redundancy entitlement and notice reset on a move |
| **How exposed is the current function?** | The SEC score of staying put |

🟢 **Put the current job in the table as a row.** A comparison table without the status quo in it cannot
show a downgrade.

## 6. Build the scoring framework

Instantiate `templates/Role Scoring Framework.md` with what they just told you: **their two anchors as
LIFE and SEC** — rename those dimensions if their anchors are not lifestyle and security — their salary
floor in PAY, their geography as vetoes.

**Distinguish the two kinds of veto** — hard (no salary fixes a two-hour each-way commute) and priced (a
commute they would accept for enough money). Ask which their constraints are. Most people have both and
have never separated them.

## 7. 🔴 Configure what the tools read — the step that decides whether anything works

**Five files under `vault/settings/`, all optional, all copied from
[`templates/settings/`](../../../templates/settings/) and then EDITED.** 🔴 **Every one of them fails
silently when it is absent or left as the example.** A radar that finds nothing looks exactly like a quiet
job market, and it will be believed.

| File | Ask for | 🔴 What silence looks like without it |
|---|---|---|
| **`search.json`** | **Job titles they would actually take**, and how their boards write locations — *Dublin*, *Dublin, Ireland*, the county | **The radar returns nothing at all.** Its own location field once matched only the country and dropped 71 real roles |
| **`signal.json`** | **The vocabulary of the work they want** — technologies, practices, the phrases that would only appear in a role for them — and what to exclude | 🔴 **Nothing ever reaches HIGH or MED.** The radar runs, fetches, writes a shortlist, and every role lands in the catch-all |
| **`profile.json`** | **Spelling locale** (`ie-uk` \| `us` \| `off`) and 🔴 **`working_days_per_year`** | CV spelling checks silently off; **no way to annualise a contract day rate** |
| **`employers.json`** | Employers to watch by name; any they will not work for, and why | Nobody watched, nothing filtered before scoring |
| **`review.json`** | Only if they want automated oversight | Nothing — `review.py --dry-run` works without it |

🔴 **`working_days_per_year` is the one with no safe default, so ask it as a question:** *"How many days
would you actually bill in a year?"* **220 allows for annual leave; 250 is a year with none in it.** An agent
guessed 250 once and reported a €700–750/day contract as €175–190k when at the user's own 220 it is
€154–165k — **14% high, on the single number that decides whether a contract clears their floor.**

🔴 **Never invent a value for any of these.** An invented geography or vocabulary produces a filter that
matches nothing, and — unlike a wrong wiki page — **nobody ever reads it to notice.**

🟡 **They do not have to fill in all five today.** `search.json` and `signal.json` are what make the radar
work; the rest can wait. **But say which are missing rather than leaving it to be discovered.**

## 8. Start the standing answers

Instantiate `templates/Standing Answers.md`. **Do not try to fill it all now** — most of it is `TBC` until
there is a real application. But get the three that block everything:

- **Right to work and sponsorship.** Knockout questions on every form, and a careless answer is an
  automatic rejection nobody reviews.
- **Notice period**, and the earliest realistic start.
- 🔴 **"Why are you leaving?"** — the most-asked question in any process, and the one that must be
  identical in the cover letter, the form, the phone call and the interview. **Do not accept the first
  answer as final.** Ask what they would say out loud, then read it back. It reads differently spoken.

**If the reason is redundancy, being at risk, or something that went wrong**: record the plain fact, help
them find the shortest true framing, and **do not push for detail.** It is common, it is not a mark against
them, and over-explaining is the only real risk.

## 9. Close the loop

Append to `log.md`. Then tell them:

- What the wiki now contains
- **The three most interesting things you learned** that were not in their CV
- What is still unknown, as a backlog on `Operating Model.md`
- That `/interview` is the thing to run next, and why
- 🔴 **That `vault/AGENTS.md` exists and is theirs.** Give one concrete example of what belongs in it —
  *"if you tell me not to describe you as a leader, that is where it goes and it survives every update"*

🔴 **Then run it, and read the result out:**

```bash
python3 tools/doctor.py
```

**It is the only thing that says what is configured and what will quietly do nothing.** `PLACEHOLDER` is
the verdict that matters — a file copied from its example and never edited **looks configured and matches
nothing.** `OPTIONAL` is not a fault and must not be reported as one.

**Do not offer to write a CV yet.** There is not enough in the wiki, and a CV written from a
single interview round is a formatted version of the document they already had.
