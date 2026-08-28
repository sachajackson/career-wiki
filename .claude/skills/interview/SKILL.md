---
name: interview
description: Interview the user about what they actually do at work, and file the answers into the wiki. The core operation of this system — run it early, run it often, and run it before writing any CV.
---

# Interview

## 🔴 Before the first question: read `Operating Model.md` IN FULL

**All of it, every time, however long it is** — not the *Interview backlog* section, not a grep, not a
skim of the headings. **An interview happens at any point in the life of a vault**, not at the start, and
by the second one that page is the densest record of the user's working life that exists.

🔴 **This rule is here because it was broken.** A round of seven questions was drafted on 2026-08-28 after
reading only the backlog section. **Four of the seven were already answered in full** — one of them with a
before-and-after pair the questioner then asked for. The page it should have read was 897 lines and named
a second page, [[Delivery Tooling]], devoted entirely to the subject being asked about.

**Read the pages it links to as well.** `Operating Model.md` is an index as much as a record: the answer
is often one link away, on a page written specifically because the topic outgrew this one.

🟢 **Every wiki page carries its own *Open questions* section, and those are the real round.** They were
written by whoever last knew the most about the subject. **Start there rather than composing from
scratch** — a question the page already asks of itself is guaranteed not to be redundant.

## 🟡 Then run the guard, and know what it cannot do

```
python3 tools/known.py "<the thing>"
```

**Every question has a cost. A question the user has already answered has a much larger one** — it tells
them the system does not retain what they say, which is the one thing it exists to do.

🔴 **`SETTLED` or `PRESENT` means do not ask.** Read the lines, use what is there, and if it needs
extending, **ask the narrower question the existing record raises** rather than the broad one it already
answered. See [[SCHEMA.md]] for the verdicts and what each obliges.

🔴 **`NOT FOUND` DOES NOT MEAN NOT RECORDED, and this is the trap.** The guard matches wording. On
2026-08-28 `"applications built with AI"` returned `NOT FOUND` while **two pages** described exactly that,
because they use the words *delivery tooling*. **Try the user's vocabulary and the wiki's, and if a
`NOT FOUND` is surprising, believe the page and not the tool.** The guard narrows a round; reading is
what makes it safe.

**This is the most valuable thing in the repo.** Everything else — the scoring, the CVs, the profiles —
is downstream of how well this is done.

## The premise

**A CV records projects. The strongest material is usually capability, and capability never gets written
down.** People stop noticing what they are good at. They describe the thing that had a project code and
omit the thing they do every week that nobody else in the building can do.

You will not find it by reading their CV. You find it by asking narrow, concrete questions and listening
to what comes out sideways.

> The pattern to expect: you ask a narrow question about how something routine gets done, and the answer
> arrives with a second thing attached — a tool they built, a process they invented, a crisis they ran —
> mentioned in a subordinate clause because they assume everyone does it. **That aside is frequently the
> best material in the entire history, and it is written down nowhere.** Stop and pull on it.

## How to run it

**Rounds of six to eight questions.** Not one at a time — that is an interrogation. Not twenty — that is
a form. Ask, listen, file, then ask the next round informed by the answers.

**After each round**: update `Operating Model.md` and any pages the answers touch, append to `log.md`,
and tell the user what changed and what it unlocked. Then propose the next round.

**Keep a standing backlog** in an `## Interview backlog` section on `Operating Model.md`. Questions you
did not get to, questions the answers raised, and questions you thought of later. It should never be
empty.

## Question design

**Ask about mechanics, not achievements.** "What are you proud of?" produces a rehearsed answer. "Walk me
through what happens when a release fails on the day" produces the truth.

| Bad question | Better question |
|---|---|
| What are your key achievements? | What did you do last week that nobody else could have done? |
| Do you manage a budget? | Who has to say yes before you can spend money or hire? |
| How big is your team? | Draw me the reporting line, including people who don't report to you but whose work you depend on |
| Are you technical? | When was the last time you opened an editor, and what for? |
| Do you use AI at work? | What have you tried with AI that didn't work? |

**Follow the numbers.** Any time a number appears, ask what it was before. Before-and-after pairs beat
percentages: *"from eleven days to four"* is more convincing than *"a 64% reduction"*, harder to fake, and
invites a follow-up the user can answer for as long as anyone wants to listen.

**Follow the boredom.** When someone describes something as routine, probe it. Routine to them is often
rare in the market.

## Rounds that have worked

Adapt these; do not read them out.

**Round 1 — shape.** Reporting lines including dotted ones. Who decides what. What they can approve alone.
What the actual product is and who uses it. Headcount, locations, time zones.

**Round 2 — flow.** How work arrives and how much. Who prioritises. How capacity is decided. What happens
when it goes wrong, and who makes the call. What gets reported upward, to whom, how often.

**Round 3 — tools and craft.** What they have built themselves. What they have automated. Where the
current toolchain stops working. What they have tried that failed. Anything with a number attached.

**Round 4 — people.** Turnover. Graduates, placements, apprenticeships, mentoring. Cross-training. Who
they have promoted. What they do when someone is struggling.

**Round 5 — the awkward ones.** Save these until there is trust, and ask them once:

- If you had to choose between more money and less exposure, which way do you go?
- What is the best job you have ever had, and why?
- What would have to be true for you to stay where you are?
- What are you worried someone will find out?

**The last one is the most useful question in this file.** It surfaces the constraint that should govern
role selection, and it is almost never in a CV. Record the answer, treat it as decision context, and
**never use it as positioning material.**

## Filing the answers

**Follow the maintenance discipline in `SCHEMA.md`** — file in the same turn, reconcile against what is
already there before writing, recompute anything derived, and flag anything that contradicts a document
already submitted. **An interview that produces good answers and files them badly is worse than no
interview**, because it creates confident-looking pages nobody reconciled.

**Mark everything the user says directly as human-verified**, per the schema:

```yaml
verified:
  - { by: "human:<user-id>", at: <ISO8601> }
```

**Anything describing a current state gets `stale_after`** — team size, geography, tooling, title.

**Preserve good phrasing verbatim.** When someone says something crisp about their own work, quote it
rather than paraphrasing. It is usually better than anything you would write, and it is interview
material as it stands.

**File contradictions rather than resolving them.** If an answer conflicts with a source document, record
both and flag it. Two of the user's own documents disagreeing is a finding, not an error to smooth over.

## 🔴 An artefact is not a source. Check it against `Operating Model.md`, every time

**A CV, a LinkedIn profile or an old application pack is a SNAPSHOT of what was true when somebody wrote
it.** `Operating Model.md` is maintained. **When they disagree, the wiki is usually right and the artefact
is usually just old** — and the artefact is the one that goes to an employer.

🔴 **The gap is routinely years.** One vault's CV is dated **July 2023** while its Operating Model carries
2026 material — a second AI build in the org, an apprenticeship programme run personally, a capacity model
with a before-and-after pair, a team that has changed size by attrition. **A round composed from that CV
would ask about a job the user stopped doing.**

**So, whenever an artefact is in play — read for an interview, quoted in a question, or about to be
rewritten:**

| | |
|---|---|
| 🔴 **Reconcile before asking** | Anything the artefact asserts that the wiki contradicts is a QUESTION, and often the best one in the round: *"your CV says X, the wiki says Y — which is current?"* |
| 🔴 **Never let the artefact silently win** | It is older and it is the one that leaves the building. A stale claim in front of a recruiter is the failure this whole system exists to prevent |
| 🟢 **The wiki being AHEAD is the normal case** | It is not an error to report. It means the interviews have been working, and it tells you what the next CV rewrite has to pick up |
| 🟡 **File the contradiction, do not smooth it** | Two of the user's own documents disagreeing is a finding. Record both and flag it — see *Filing the answers* below |

🟢 **Say what you found, in one line, before the round starts.** *"Your CV predates four things the wiki
now records — I am not going to ask about those."* It proves the system retained what they said, which is
the whole point of running this before asking anything.

## Getting it wrong

**You will under-read their scope.** Assume the wiki understates what they do, and ask rather than
concluding from silence. If the user says you have missed something, they are right — do not defend the
earlier reading, just find out what you missed.

**Do not resolve their doubts for them.** If they express uncertainty about their own job security, the
fairness of a process, or whether they are good enough — take it seriously, record it, and do not offer
reassurance. False comfort is worse than none, and it is not this system's call to make.

**Stop when they are done.** A backlog is better than an exhausted user. Say what is still unasked and
leave it there.
