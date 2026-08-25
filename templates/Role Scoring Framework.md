---
type: synthesis
title: Role Scoring Framework
description: How roles get scored against what this person actually wants, and the table of everything assessed so far.
tags: [career, framework]
generated: { by: "claude/<model>", at: <ISO8601> }
status: draft
---

# Role Scoring Framework

**Template. `/career-init` fills the slots.** Until the `{{...}}` markers are replaced this framework is
not usable — a generic rubric ranks roles by how good they sound, which is not the question.

## Three scores, not one total

**Reported separately and never summed**, because they answer different questions and a single number lets
one hide the others.

| | What it is | Scale |
|---|---|---|
| **FIT** | **NEED + DELIVER + EDGE.** Could they do the job, and would this employer want them? | **/15** |
| **LIFE** | **Lifestyle alone.** Commute, work pattern, hours, travel, on-call | **/5** |
| **SEC** | **Security alone.** Employer stability, and how exposed this particular function is | **/5** |
| **REQS** | **How many of the posting's own named requirements they clear** | **counted** |

**The three FIT components, each from an established method rather than invented:**

| | Based on | Asks |
|---|---|---|
| **NEED** | Jobs-to-be-Done | What is this employer actually anxious about, and is that this person's ground? **A job description is a wish list; the role exists because something is going wrong** |
| **DELIVER** | Topgrading Scorecard | Reverse-engineer the outcomes they will be measured on. Can this person point at having done each one? |
| **EDGE** | Value Proposition Canvas | Against the field who will apply, what is rare here? **Not what is good — what is *rare*** |

**LIFE and SEC are [[#The user's own values — filled at init|the two anchors]]**, scored apart. Plus two
modifiers, tracked separately because they behave differently:

- **PAY** — scored only where a figure is published. `TBC` otherwise, resolved by asking on the first call.
- **WIN** — realistic odds. A perfect role with no chance is worth less than a good role with a real one.

### 🔴 Why LIFE is not inside the total

**Whichever anchor is near-constant across the options carries no ranking information.** If someone's
commute constraint scores 2 or 3 for almost every role available to them, then inside a total it depresses
everything roughly equally — noise, not signal. **Separated, it is what it actually is: a price paid on
every move, visible and comparable.**

**And a total hides where the decision is being made.** In real use, several roles tied on FIT while their
old totals spread by three points — **all of it the personal-fit dimension.** A role that had been rejected
outright scored exactly what the top recommendation scored on capability. **The total made it look weaker
rather than equal-but-worse-anchored.**

### 🔴 Do not answer a tie by lengthening the ruler

**Scoring each dimension out of 20 for a total out of 100 is the obvious idea and it is wrong.**

- **The anchors are defined by evidence, not degree.** *Strong and evidenced* against *good, with gaps that
  do not touch the core* is a defensible distinction. **16 against 17 is not** — the digit gets generated
  rather than derived, which is the one thing a knowledge-based system must never do.
- 🔴 **It produces persuasive noise.** *16 versus 14* reads as a finding when it is a coin flip.
- 🟢 **It does not even fix the tie**, which is a *ceiling* effect: only plausible roles get assessed, so
  everything clusters at the top of whatever scale exists. **A longer ruler moves the cluster; it does not
  spread it.**

### 🟢 REQS — where the extra precision actually comes from

**Precision comes from decomposition, not from stretching the scale.**

**Take the employer's own named requirements**, mark each **🟢 cleared / 🟡 partial / 🔴 gap**, count a
partial as a half, and report the tally on the role page. **DELIVER then becomes a judgement that can be
checked line by line rather than asserted.**

> *"Nine of your twelve outright, two partially, one not at all."*

🟢 **The test of a decomposition is whether it validates the judgement or replaces it.** If the tally lands
somewhere far from the DELIVER score already given, one of the two is wrong — **find out which before
writing anything.**

🔴 **Score it from the employer's own posting, never an aggregator's copy** — see
[[#Before building anything for a role]]. 🔴 **And a role with no ingested posting gets `TBC`, not a
guess.** Most of the table will be TBC, which usefully flags which rows were scored from a summary.

## The user's own values — filled at init

```
Anchors (WANT scores these two, and only these):
  1. {{PRIMARY_ANCHOR}}
  2. {{SECONDARY_ANCHOR}}

Salary floor: {{SALARY_FLOOR}} base
  What it is for: {{WHAT_THE_FLOOR_IS_FOR}}
  Deadline, if any: {{FUNDING_DEADLINE}}

Base location: {{HOME_LOCATION}}
  Hard vetoes (no salary fixes these):    {{HARD_VETOES}}
  Priced vetoes (a number changes these): {{PRICED_VETOES}}
```

**Why "what the floor is for" is recorded.** A floor tied to a dated obligation behaves differently from a
preference: **starting salary dominates progression**, because a rise arrives too late and is taxed on the
way. It also makes illiquid equity a poor substitute for cash.

## 🔴 The baseline: score against where they are now, not against the field

**Added because it was got wrong in real use.** A role offering two office days a week at a rail-accessible
office was scored **5/5 on lifestyle** and described as *"the best lifestyle position available anywhere."*
**The user was contractually fully remote.** Two days a week was a downgrade.

🔴 **The score was measuring *best of the options assessed* and reporting it as *best available*** — and it
was not one bad row. **Every lifestyle score in the table had been set against no reference point at all.**

**So the first row of the table is the current job:**

| | Record | Why |
|---|---|---|
| **Work pattern** | Days in an office, and **whether it is contractual or custom** | 🔴 **A pattern in writing is a floor. A custom the employer could reverse is not** — and the difference changes what every alternative is worth |
| **Commute** | Door to door, and whether the time is usable | |
| **Pay, notice, unvested equity, service** | | These are what leaving *costs*, and they are what an external offer has to beat |
| **Stability** | How exposed the current function is | |

🟢 **Top of each scale means *no worse than today*, not *best of what we found*.** A comparison table
without the status quo in it cannot show a downgrade.

## 🔴 Standing gaps — capabilities established as ABSENT

🔴 **"Not recorded" and "recorded as absent" are the same empty search result and they mean opposite
things.** One is a question worth asking. **The other is a scored input, and re-asking it costs
credibility.** In real use the system asked about a capability its own wiki had closed three days earlier,
with the words *"stop asking"* on the page.

**Run `python3 tools/known.py "<the thing>" --wiki wiki` before adding a row, and before asking anything.**

| The gap | Status | Resolved on | Demanded by | The substitute |
|---|---|---|---|---|
| | *confirmed absent / unknown / present* | | *count the postings* | *what to say instead* |

🟢 **Count the postings that demand it.** Two is a coincidence. **Three is a decision to put to the user
once** — *is this worth going and acquiring?* — rather than conceded repeatedly in cover letters.

🟢 **Always fill the substitute.** There is usually something: for a missing budget figure, operational
scale. A gap with a substitute is a sentence; a gap without one is a silence.

## 🔴 Known locations — score a place once, not once per role

🟢 **An employment cluster is a standing filter, not a fact about one job.** One postcode in the case below
held four major employers, so getting it wrong got dozens of roles wrong — differently each time, because
it was re-derived per role.

**Record the origin once** (the town they commute *from*, not their address — see `PRIVACY.md`), then each
destination once.

| Place | Legs from origin | Door to door | Time usable? | Employers there | Verdict |
|---|---|---|---|---|---|
| | | | *train they can work on / lost to driving* | | *fine / priced / hard no* |

🔴 **No row goes in without a door-to-door time.** Mark it `TBC` and ask. **A nearby transit stop is not a
commute** — see below.

## 🔴 Score the journey, not the address

**"Hybrid, <city>" is not a location.** Two roles described identically can differ by an hour a day and by
whether the time is usable.

1. **Where exactly** — which building, which side of the city?
2. **How many legs** from where they actually live, and **is the time usable** (a train they can work on)
   or lost (driving)?
3. **How many days a week**, which multiplies whatever the first two give?

🔴 **A nearby transit stop is not a commute.** In real use the system found an office four minutes from a
light-rail stop, concluded a previous *"this is a drive"* note was wrong, and **raised the score.** The
actual journey from the user's home was two hours each way across three legs. **Metro and tram networks are
intra-city: for anyone commuting *in*, they usually add a leg rather than removing one.**

🟢 **Store employment clusters once and reuse them.** One postcode in that case held four major employers.
**The finding was not about one job — it was a standing filter applying to dozens**, and re-deriving it per
role got it wrong differently each time.

## Five rules that stop the number lying

**1. Shape beats total.** Two roles at 15 are not the same role. Read the dimensions.

**2. Anything scoring ≤2 is a veto candidate.** Ask whether the total is hiding it.

**3. There are two kinds of veto and they are not alike.**

| Type | Example | Reversible? |
|---|---|---|
| **Hard** | A location not commutable at any salary | No |
| **Priced** | A commute that is tolerable for enough money | **Yes, at a number** |

Conflating them either kills good roles or keeps dead ones alive.

**4. Do not let a preference masquerade as an anchor.** LIFE and SEC measure the stated anchors and nothing else. Interest,
prestige, technical exposure and curiosity are not anchors — they belong in DELIVER or the pre-mortem.

**5. Count a risk once, in the place it belongs.**

| Concern | Belongs in |
|---|---|
| Employer stability | **SEC** |
| Work pattern, commute, hours, travel, on-call | **LIFE** |
| Can they actually do it — depth, domain, scale, named minimums | **DELIVER** |
| Will it wear them down; what failure looks like at eighteen months | **Pre-mortem** |

**The tell: a LIFE or SEC score whose justification never names the anchor it is scoring is measuring something else.**
Double-counting does not make the framework cautious, it makes it wrong — and it suppresses good roles on
an error rather than a judgement.

## Before building anything for a role

**Step 0: confirm the posting is live.** A 403 or an unrenderable careers site is not evidence of closure.
If you cannot resolve it, ask the user to check while logged in.

## The table

🔴 **The first two rows are not jobs, and the table is wrong without them.**

| Role | N·D·E | **FIT** | **LIFE** | **SEC** | REQS | PAY | **Status** | Posting | Note |
|---|---|---|---|---|---|---|---|---|---|
| **Staying put — the current job** | — | — | | | — | | `Not applied` | — | 🔴 **The baseline. Top of each scale means *no worse than this*** |
| **An internal move** | | | | | | | `Not applied` | | 🔴 **Costs none of: forfeited equity, notice, reset service, probation, reference risk. 🔴 Usually will not reach the pay floor** |
| | | | | | | | | | |

🔴 **Keep N·D·E visible, not just FIT.** Two roles at 14 split into `5·5·4` — *would deliver it well, but
so would others* — and `5·4·5` — *brings something rare, with real gaps*. **Same sum, different candidate.**

🔴 **Why the second row exists.** Most searches model *leave* and *stay* and stop there. **There is a
third option and on these dimensions it is structurally advantaged before any specific role is compared** —
it keeps unvested equity, dissolves the notice period as a constraint, preserves continuous service, and
carries no probation or reference risk. **An external role in the middle of this table is competing against
that**, and it should be visible rather than left in the user's head. **A user in a stable job will not
raise it unprompted, so ask.** And **fetch the employer's *internal* job site, not just their public
careers page** — large employers run a separate one carrying internal-only requisitions.

### Status — a closed set

**Use exactly these. `CLAUDE.md` is the authority and this list must match it.**

| | Meaning |
|---|---|
| `Submitted` | Sent, no reply yet |
| 🔴 `Rejected by employer` | **They turned it down.** Never merge this with the two below |
| `Withdrew` | Applied, then pulled out |
| `Declined` | They offered, the user said no |
| `Closed` | The requisition closed or went quiet |
| `Vetoed` | Ruled out on a hard constraint before applying |
| `Not applied` | Assessed and not pursued |

🔴 **The distinction that matters is who decided.** *"Rejected"* alone is ambiguous between *the employer
turned them down* and *they chose not to apply* — and **it makes the table unable to answer the one
question that says whether the level is right: how many applications has an employer turned down?**

**Capture the posting URL at ingest** — a role page without a link is a dead end three weeks later.

## Screening-call checklist

**Ask the decisive question on the first call, not the third.** For each live application, the one fact
that would change the decision:

| Role | The question | Why it cannot wait |
|---|---|---|

**Always ask, on every call:** base salary separately from bonus, equity and pension; the office pattern
in days per week; and volunteer the notice period early rather than at offer stage.
