# Running it

**What to type, and what to have ready before you type it.** [← back to README.md](../README.md)

**Type the command in Claude Code.** 🔴 **None of these takes arguments.** What they need is *context* —
from the conversation, or from your vault — and that is the part that decides whether a run is any good.

🔴 **You never have to remember an order.** `python3 tools/runbook.py` prints the sequences — `radar`,
`application`, `outcome`, `update`, `init`, `migrate` — each step with its command and one line on what
goes wrong when it is skipped.

---

## `/career-init` — once, at the start

🔴 **Have a CV in `vault/sources/` first. It stops without one.** Add a LinkedIn export too if you have
one: the two documents disagree surprisingly often, and **the disagreements are findings.**

```
/career-init
```

**Set aside an hour**, most of it conversation. It reads your sources, tells you what it noticed *before*
writing anything, scaffolds the wiki, runs the first interview round, and elicits the two career anchors
everything downstream is scored against.

🟡 **If `vault/wiki/` already has pages, use `/career-migrate` instead** — this one scaffolds over
whatever is there.

## `/career-migrate` — instead of the above, if you already have something

**Copy your existing material into `migration/` first.**

```
/career-migrate
```

🔴 **The first thing it asks is what else is in that folder**, and the question is not a formality: the
first real migration carried **118 files of an unrelated software project** into the drop zone, where they
sat looking like career material. **Copy those out before you start, not after.**

## `/interview` — the core operation

**Nothing to prepare. Twenty minutes and a willingness to be specific.**

```
/interview
```

It asks; you answer; the answers are filed before the next round. **Run it repeatedly over weeks** — one
round at a time. 🟡 **Do not stack rounds:** unfiled answers are answers you will be asked for twice.

## `/role-radar` — find roles

🔴 **`vault/settings/search.json` and `signal.json` must be filled in.** Without them the radar returns
nothing, and **that looks exactly like a quiet job market.** `python3 tools/doctor.py` tells you which are
still placeholders.

```
/role-radar
```

The work underneath is a script, and you can run it directly:

```bash
python3 tools/radar/radar.py --days 7        # dense recent coverage
python3 tools/radar/radar.py --all-open      # the standing backlog of everything still open
```

**About six minutes.** 🔴 **The two flags are not the same run and neither is a superset** — sources cap a
query at roughly 100 results, so `--days 7` is 100 results from one week and `--all-open` is 100 across
three months. Run the first often and the second periodically.

## `/build-application` — one role, one pack

🔴 **Name the role. It cannot guess which requisition you mean.**

```
/build-application
```
> *"Build the pack for the Citi AI Governance role"*
> *"Do the one at https://www.linkedin.com/jobs/view/…"*
> *"The Grant Thornton Associate Director one"*

**A posting URL, a role page, or a plain description all work** — what matters is that exactly one role is
identified. It re-checks the posting is still open before writing anything, because **twenty minutes on a
dead requisition is twenty minutes gone.**

🟡 **It will ask once whether to offer the repository link in the cover letter**, and record the answer in
`vault/settings/profile.json` so it is not asked every time.

## `/pre-submit` — the last check before the button

🔴 **Have the application form open in front of you.**

```
/pre-submit
```

It is the last gate, and **several of its findings are unfixable once sent** — which is the whole reason
it runs with the form open rather than after.

## `/profile-refresh` — LinkedIn and Indeed

**A populated wiki. Nothing else.**

```
/profile-refresh
```

Rewrites both profiles from what is already in the wiki, as paste-ready text. **Useful before a run of
applications**, since a recruiter who likes the CV looks at the profile next.

## `/market-standards` — what the market expects, for *you*

**Your country, level and industry need to be in the vault**, or it asks. 🔴 **A wrong country produces
four pages of confidently wrong advice** — a one-page US résumé convention applied to a director-level
application in Europe is simply wrong.

```
/market-standards
/market-standards --refresh cv
```

**Four deep-research passes, and it takes a while.** `--refresh` redoes one page instead of four; use it
on the page whose `stale_after` has passed rather than all of them.

## `/career-lint` — health check

**Nothing to prepare.**

```
/career-lint
```

Run it periodically, and 🔴 **always before a batch of applications.** It also asks about every
application you sent and never heard back on, **because nothing else in the system ever will** — an
employer replying, or not replying, happens outside it.

---

## Two that run themselves

**You do not invoke these.** The main session delegates to them.

| | |
|---|---|
| **`role-triage`** | Reads a batch of job adverts and returns a short ranked list. A week of postings is two to three hundred adverts; reading them in the main session destroys it with text nobody needs to keep |
| **`role-review`** | 🔴 **Adversarial.** Takes a finished, scored assessment and the employer's own posting and **tries to refute the score**, quoting the posting rather than the assessment. It exists because *"hands-on experience with agent frameworks"* can be quoted perfectly and read completely wrongly |

## When something looks wrong

```bash
python3 tools/doctor.py        # what is configured, and what will quietly do nothing
python3 tools/pipeline.py      # is the current stage of work actually finished
python3 tools/tests/run.py     # are the checks themselves still working
```

🔴 **`doctor`'s verdict that matters is `PLACEHOLDER`** — a settings file copied from its example and
never edited **looks configured and matches nothing.** `OPTIONAL` is not a fault: most of the setup is
optional, and being told to fix what you never wanted is how a check gets ignored.
