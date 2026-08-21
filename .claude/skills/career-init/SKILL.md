---
name: career-init
description: Bootstrap a new career wiki from scratch — read the user's CV, scaffold the wiki, run the first interview, and elicit their career anchors and salary floor. Run this once, first.
---

# career-init

Turns an empty repo and a CV into a working career wiki. **Run once.** Takes an hour, most of it
conversation.

## Before anything

Check `sources/` contains at least one CV or profile export. If it is empty, stop and ask for one — every
other step depends on it. **Ask for a LinkedIn export too** if they have one: the two documents disagree
surprisingly often, and the disagreements are findings.

## 1. Read, then say what you found

Read everything in `sources/`. Then, **before writing any files**, tell the user what you noticed:
gaps in the timeline, claims without numbers, roles described in a sentence that sound like they deserve
a page, anything that contradicts something else.

**This first response sets expectations.** If it reads like a summary of their CV, you have wasted it.
It should tell them something about their own document they did not know.

## 2. Scaffold

Copy `templates/` into `wiki/`, filling in what the sources support. Create `index.md`, `log.md`,
`Career.md`, `Operating Model.md`, `CV.md` and a `roles/` folder. OKF frontmatter on everything, per
`CLAUDE.md`.

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

## 5. Build the scoring framework

Instantiate `templates/Role Scoring Framework.md` with what they just told you: their anchors in WANT,
their salary floor in PAY, their geography as vetoes.

**Distinguish the two kinds of veto** — hard (no salary fixes a two-hour each-way commute) and priced (a
commute they would accept for enough money). Ask which their constraints are. Most people have both and
have never separated them.

## 6. Close the loop

Append to `log.md`. Then tell them:

- What the wiki now contains
- **The three most interesting things you learned** that were not in their CV
- What is still unknown, as a backlog on `Operating Model.md`
- That `/interview` is the thing to run next, and why

**Do not offer to write a CV yet.** There is not enough in the wiki, and a CV written from a
single interview round is a formatted version of the document they already had.
