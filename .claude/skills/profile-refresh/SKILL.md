---
name: profile-refresh
description: Rewrite the user's LinkedIn and Indeed profiles from the wiki, as paste-ready text. Use when profiles are stale or before a run of applications.
---

# profile-refresh

**Profiles cannot be updated automatically** — they need authentication. You write the text; the user
pastes it.

## Why this matters more than it seems

**A live application creates a version of someone's history that a recruiter can compare against their
profile.** If the profile says a different team size, a different geography or a different job title, the
recruiter notices — and a discrepancy between a parsed CV and a public profile is precisely what gets
looked at.

**So run this *before* a batch of applications, not after.** Fixing it afterwards means the inconsistency
was live for the ones that matter.

## What to check first

Read every page with an expired `stale_after`, plus anything describing a current state. The usual rot:

- **Team size** stated as a number that was true once. Use "a peak of N" if the team has shrunk — accurate
  and does not require explanation
- **Geography** listing countries the user no longer has people in
- **Job title** differing between the profile, the CV and what the employer would confirm
- Achievements attached to the wrong role

**Where two of the user's own documents disagree, the profile usually wins for external work** — not
because it is more likely to be true, but because it is the one a recruiter can open in the next tab. Flag
the conflict and let them settle which is actually correct.

## Writing it

- **One unbroken line per paragraph.** Hard wraps survive a paste into a web form and look broken. This is
  the single most common way pasted text goes wrong.
- **The title field takes the title of record**, not a friendlier translation. Title fields can feed
  employment verification. Put the readable version in the headline and the description, where it is
  presented as scope rather than asserted as fact.
- **Check keyword coverage for implied-but-unstated terms.** Some pairs are searched together and listing
  one without the other loses half the matches.
- **A profile is general-purpose.** Do not tailor it to one employer's vocabulary the way a CV is tailored.

## Tone

**Match the user's own register.** Someone averse to self-promotion will not paste text that reads as
self-promotional, and a profile they will not publish is worthless. Ask before adding anything that
requires an ongoing habit — posting cadence, personal brand work — and do not pitch it unprompted.
