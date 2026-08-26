# Developing this while using it

**Do not do both in the same directory.** That is the whole of the advice, and everything below is why and
how.

## The two places

| | What it is | Git remote | Contains |
|---|---|---|---|
| **This repo** | The tool | 🔴 **Public** | Scaffolding, skills, scripts, fictional examples |
| **Your vault** | Your career | Private, or no git at all | Your CV, your history, your salary floor, your applications |

**Keeping them apart means personal material has no path to the public remote.** Not "is ignored on the
way out" — has no path. Every other arrangement relies on a rule holding every time, and rules that must
hold every time eventually do not.

```
Documents/
    career-wiki/        <- this repo. public. you develop here
    my-career/          <- your vault. private. you job-hunt here
```

## Why `.gitignore` is not enough on its own

It stops accidents of omission — `git add -A` skipping what it should skip. It does not survive
`git add -f`, an edited ignore rule, a tool that stages files directly, or a path nobody thought to list.

**And the failure is permanent.** The remote is public and git history keeps what it is given: a personal
file committed and pushed is not fixed by deleting it in the next commit. It stays in the history, in
every clone, and in GitHub's cache.

So there is a second line:

```bash
git config core.hooksPath githooks      # run once, per clone
```

`githooks/pre-commit` inspects what is actually staged, at the last moment before it becomes history, and
refuses anything under `vault/`, bar the five README files the system itself ships — **including a forced
add** — plus anything that reads as a personal email address, a real LinkedIn URL, or a salary line
wherever it sits. It is deliberately noisy: a false positive costs one `--no-verify`, a false negative is
public forever.

**Run that command now.** Hooks live in `.git/`, which is not itself tracked, so a fresh clone has no
protection until you point git at the tracked `githooks/` directory.

## Carrying improvements across

**There is nothing to carry.** The vault lives inside the clone, so `git pull` updates the system and
does not touch a single file under `vault/`. That is the entire reason the boundary exists.

> **`tools/sync-to-vault.sh` was deleted on 2026-08-25.** It copied skills, hooks, `tools/` and
> `templates/` from the repo into a separate private vault, one direction, refusing to look at
> `sources/` or `wiki/`. It was a careful script and it was solving a problem the layout created:
> **the vault was somewhere else, so improvements had to be walked across by hand.** Under one root,
> the copy is the bug — a script whose job is to put system files inside a user's folder is the exact
> shape of the mistake `vault/` was built to make impossible.

🔴 **`vault/AGENTS.md` is never overwritten by anything.** Your standing instructions to the agent — what
to call you, what not to suggest, what it keeps getting wrong — are yours, and an update that replaced
them would discard the most expensive thing in the vault: months of corrections.

Nothing goes the other way. When your vault teaches you something worth keeping — a rule that stopped a
mistake, a failure mode worth naming — bring the *lesson* back here by hand, written generically.
🔴 **Never copy a file from the vault into the repo.**

## Migrating an existing wiki

**Adopt the conventions in place. Do not restructure and move at once.** Two changes at the same time
means a mistake in one looks like a mistake in the other.

1. **Copy the tooling in** with the sync script, and enable the hook so verification starts running.
2. **Add `employer:` to every page that states a figure.** Nothing else unlocks the attribution check, and
   it is the check that catches a real achievement attached to the wrong role.
3. **Add `verified:` as you go.** Do not backfill it wholesale — a claim marked verified because it was
   convenient is worse than one honestly marked unverified. Mark it when the person confirms it.
4. **Add `stale_after:` to anything describing a current state** — team size, geography, title.
5. **Then run `/career-lint`.** It will tell you what is unverified, expired, or contradictory.

**Keep whatever your vault already does that this repo does not.** If it covers more than careers, that
is a superset, not a deviation — this schema is career-shaped because the repo is, not because the pattern
requires it.

## Before every push

```bash
python3 tools/tests/run.py      # stdlib only, no install step, seconds
git status --porcelain          # anything unexpected staged?
git log --oneline origin/main..HEAD
```

🟢 **`githooks/pre-push` now runs the suite for you and refuses the push if it is red**, so the first
line above is a belt to the hook's braces rather than the only thing standing between a broken `main` and
a stranger. **It needs `git config core.hooksPath githooks`, the same one line as the commit guard** — a
fresh clone has no hooks until you point git at the tracked directory.

🔴 **Do not pipe the suite into anything before `&&`.** The three lines above are a gate only if the
first one's exit status survives:

```bash
python3 tools/tests/run.py && git push              # the suite gates the push
python3 tools/tests/run.py | tail -2 && git push    # 🔴 it does not — tail always succeeds
```

**A pipe replaces the exit status with the last command's.** Piping test output to `tail` or `grep` for
readability is the natural thing to do and it **silently disarms every `&&` after it**. That pushed a red
suite to `main` here, from a gate that was followed exactly — which is the same failure as the line below,
in a different disguise: **a control that looked like it ran.** If you want the short output, run the
suite twice, or check `$?` yourself.

🔴 **`git status` answers the wrong half of the question.** It shows what is unexpectedly *there*. It
cannot show what is expectedly *missing* — and twice a file was written, used and pushed while an ignore
rule kept it out of the repository, with a clean status the whole time. **`test_shipped.py` is the half
that asks git what a clone would actually get**, which is why it runs in the suite rather than living
here as another line to remember.

🔴 **Treat `main` as published, because for some users it is.** People who run their search through this
may reference the repository in an application, so **a stranger can arrive at `main` at any moment** —
including mid-repair. Local edits are private; **the push is the publication.**

**Two habits follow.** Run the tests before pushing, not after. And **if something is half-finished at the
end of a session, leave it uncommitted or on a branch** rather than pushing a broken `main` and fixing it
in the morning.

The hook covers the commit. **Nothing covers a repository you make public later**, so if this ever becomes
a private repo that you flip to public, audit the whole history first — not the working tree.

## Before you open a pull request

```
python3 tools/tests/run.py
```

**Stdlib only, no install step, and it runs in seconds — keep it that way.** A slow suite gets run less
often, and this is the one control in the repo that has never failed. If a test needs to wait for
something, give it a way not to: `registry_check.py`'s retry backoff is an environment variable for
exactly that reason, and two tests that drive it as a subprocess were costing 4.5 seconds each.

🔴 **The count is deliberately not written down here.** It was, in three places, and it was wrong in all
three — 64, 65 and 85, against a real figure that had moved past 300. **A number in prose that nothing
updates is a number that lies.** If you changed `verify.py`, `cv_lint.py` or
`wikilinks.py`, **add a test for the behaviour you changed** — those three are the layer everything else
leans on, and a regression in them is silent by construction.

🔴 **If you mutation-test, disable the bytecode cache.**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B tools/tests/test_thing.py
```

A mutation that keeps the file the same length and is written in the same second is invisible to
CPython's `.pyc` invalidation, which compares **mtime and size** — so the stale bytecode loads and the
test runs against the *unmutated* code. It reported a caught mutant as missed here, and **the wrong
conclusion is the dangerous one**: it says a check is weaker than it is, and the natural response is to
weaken the code to match. **Length-preserving edits are exactly the ones a careful mutation makes.**

🟢 **A test that encodes a bug someone actually hit is worth three that cover the happy path.** Several of
the existing ones are exactly that, and they say so in their docstrings.

---

## Using it and developing it in the same clone

🔴 **This reversed on 2026-08-25, and the old advice is still worth knowing why.** It used to say *do not
do both in the same directory*: the repo was public and held only scaffolding, your vault was private and
somewhere else, and keeping them apart meant personal material had **no path** to the public remote rather
than being ignored on the way out.

**That was right, and it made an update impossible.** Improvements had to be walked across by hand by a
script, and user data had already crept into `tools/` — a config, a watch list, three files of state and
an API key — because there was nowhere better for it to live.

**Now there is one root and one rule.** Everything of yours is under `vault/`; everything else is the
system. `git pull` updates the system and cannot touch a file of yours. The separation is a *path*
now rather than a *place*, which is the part that made it testable:

| | |
|---|---|
| `.gitignore` | One pattern, plus five exact README paths that the system itself ships |
| `githooks/pre-commit` | Inspects what is actually **staged** — so it holds against `git add -f`, which `.gitignore` never did |
| `tools/tests/test_boundary.py` | Fails the build if either drifts, and runs the hook for real rather than checking that a rule appears in it |

**The commit guard installs itself** at the start of an agent session. If you are working without one:

```bash
git config core.hooksPath githooks
```

That also installs a **push** guard, which runs the suite and refuses the push if it is failing — `main`
is published the moment it is pushed.

### After any update, ask what your vault missed

```bash
python3 tools/template_drift.py
```

Your wiki was built from the templates **once** and nothing revisits it. When a template gains a section —
a new table the agent is told to keep, a row it is told to score — **your pages do not get it**, and the
agent ends up looking for something that is not there. This says what is missing.

```bash
python3 tools/settings_drift.py
```

**The same failure, in the half nobody was checking.** An update can ship a system that needs a settings
file, and it cannot put that file in your vault. When the radar's tiering vocabulary moved into
`vault/settings/signal.json`, anyone who pulled got the new radar and **not the file it reads** — and
nothing errored. The radar still ran, still fetched, still wrote a shortlist, and HIGH and MED were simply
always empty. **A broken install that reads as a quiet week is the worst failure this system can have.**

It compares **keys, never values**, so it cannot leak a query or an employer into its output. A key that is
present but still says `<your city>` is `doctor.py`'s finding, not this one.

**It never edits your pages.** Putting a new section into a page that already holds your history is a
judgement, and that is the agent's job rather than a script's.
