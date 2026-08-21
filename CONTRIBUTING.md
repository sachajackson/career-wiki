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
refuses anything under `sources/`, `wiki/` or an application's `oversight/` folder — **including a forced
add** — plus anything that reads as a personal email address, a real LinkedIn URL, or a salary line
wherever it sits. It is deliberately noisy: a false positive costs one `--no-verify`, a false negative is
public forever.

**Run that command now.** Hooks live in `.git/`, which is not itself tracked, so a fresh clone has no
protection until you point git at the tracked `githooks/` directory.

## Carrying improvements across

One direction, tool only:

```bash
tools/sync-to-vault.sh ~/Documents/my-career --dry-run   # see what would change
tools/sync-to-vault.sh ~/Documents/my-career
```

It copies skills, agents, hooks, `tools/`, `templates/` and the oversight brief. **It does not read or
write `sources/`, `wiki/` or `oversight/<application>/`** — nothing in it looks at your content.

**`CLAUDE.md` is never overwritten.** A working vault's schema gets customised — other life sections,
house rules, your own writing standard — and copying over it would silently discard all of that. The
script reports the differences and leaves the merge to you. **Your vault's version is authoritative for
anything you have changed.**

Nothing syncs the other way. When your vault teaches you something worth keeping — a rule that stopped a
mistake, a failure mode worth naming — bring the *lesson* back here by hand, written generically. **Never
copy a file from the vault into the repo.**

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
git status --porcelain          # anything unexpected staged?
git log --oneline origin/main..HEAD
```

The hook covers the commit. **Nothing covers a repository you make public later**, so if this ever becomes
a private repo that you flip to public, audit the whole history first — not the working tree.
