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

## The four dimensions

Each scored 1-5. **Shape matters more than total** — see the rules.

| | Based on | Asks |
|---|---|---|
| **NEED** | Jobs-to-be-Done | What is this employer actually anxious about, and is that this person's ground? A job description is a wish list; the role exists because something is going wrong |
| **DELIVER** | Topgrading Scorecard | Reverse-engineer the outcomes they will be measured on. Can this person point at having done each one? |
| **EDGE** | Value Proposition Canvas | Against the field who will apply, what is rare here? Not what is good — what is *rare* |
| **WANT** | Schein's Career Anchors | **Scores this person's stated anchors and nothing else** |

Plus two modifiers, tracked separately because they behave differently:

- **PAY** — scored only where a figure is published. `TBC` otherwise, resolved by asking on the first call.
- **WIN** — realistic odds. A perfect role with no chance is worth less than a good role with a real one.

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

## Five rules that stop the number lying

**1. Shape beats total.** Two roles at 15 are not the same role. Read the dimensions.

**2. Anything scoring ≤2 is a veto candidate.** Ask whether the total is hiding it.

**3. There are two kinds of veto and they are not alike.**

| Type | Example | Reversible? |
|---|---|---|
| **Hard** | A location not commutable at any salary | No |
| **Priced** | A commute that is tolerable for enough money | **Yes, at a number** |

Conflating them either kills good roles or keeps dead ones alive.

**4. Do not let a preference masquerade as an anchor.** WANT measures the stated anchors. Interest,
prestige, technical exposure and curiosity are not anchors — they belong in DELIVER or the pre-mortem.

**5. Count a risk once, in the place it belongs.**

| Concern | Belongs in |
|---|---|
| Employer stability, work pattern, commute, hours, travel, on-call | **WANT** |
| Can they actually do it — depth, domain, scale, named minimums | **DELIVER** |
| Will it wear them down; what failure looks like at eighteen months | **Pre-mortem** |

**The tell: a WANT score whose justification never names one of the anchors is measuring something else.**
Double-counting does not make the framework cautious, it makes it wrong — and it suppresses good roles on
an error rather than a judgement.

## Before building anything for a role

**Step 0: confirm the posting is live.** A 403 or an unrenderable careers site is not evidence of closure.
If you cannot resolve it, ask the user to check while logged in.

## The table

| # | Role | NEED | DEL | EDGE | WANT | **Tot** | PAY | **Status** | Posting | Note |
|---|---|---|---|---|---|---|---|---|---|---|

*Status: 🟢 submitted, ⚪ not applied, 🔴 closed or vetoed. **Capture the posting URL at ingest** — a role
page without a link is a dead end three weeks later.*

## Screening-call checklist

**Ask the decisive question on the first call, not the third.** For each live application, the one fact
that would change the decision:

| Role | The question | Why it cannot wait |
|---|---|---|

**Always ask, on every call:** base salary separately from bonus, equity and pension; the office pattern
in days per week; and volunteer the notice period early rather than at offer stage.
