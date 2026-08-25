---
name: career-migrate
description: Move an existing career wiki, or a pile of career material from another tool, into this vault. Run instead of /career-init when the user already has something.
---

# career-migrate

**Run this instead of `/career-init` when the user already has a wiki, an export, or a folder of career
material.** `/career-init` interviews from zero and scaffolds templates — on a populated vault it writes
over pages that already exist and asks an hour of questions already answered.

**`tools/migrate.py` does the mechanical half. This skill is the judgement it deliberately refuses to
make**, and every step below comes from a real migration of 166 files, not from imagining one.

## 0. Before anything: what should not come at all

**Ask what else lives in that folder.** A vault directory usually accumulates things that are not the
vault — a side project, a client folder, a downloads dump. **The first real migration carried 118 files
of an unrelated software project** into the drop zone, where they sat looking like unclassified career
material.

🔴 **Have them copy it out first, not after.** Sorting around it wastes the report.

## 1. Report first. Do not apply.

```bash
python3 tools/migrate.py
```

**Read the verdicts to the user before anything moves.** They know what their files are and you do not;
this is the one moment where a wrong guess is cheap to correct.

**Then apply, then repair links — in that order, every time:**

```bash
python3 tools/migrate.py --apply
python3 tools/wikilinks.py --fix
```

## 2. The four kinds of leftover, and what each one means

**Everything the sorter would not file is still in `migration/`, on purpose.** 🔴 **Name every one of
them to the user.** A file quietly removed from a drop zone looks exactly like a file that was dealt with.

| Verdict | What to do |
|---|---|
| 🔴 **SYSTEM — a forked copy of the tooling** | **Do not migrate it, and say why.** Their `radar.py` is behind on the scoring model, the adapters and the registry. Carrying it reinstates every bug fixed since they forked. **If they customised it, the customisation is the thing worth keeping** — read it, and either bring the change back as a proper contribution or tell them it is already covered |
| 🔴 **SYSTEM — an old `CLAUDE.md` or schema file** | **It splits, and this is the highest-value step in the whole migration.** The general conventions are `SCHEMA.md` and are replaced by an update. Anything about *the person* — how to address them, what not to suggest, what the system keeps getting wrong — goes in `vault/AGENTS.md`, which an update never touches. **Read it and do the split with them** |
| **DROP — regenerable state** | Confirm, then delete. `seen.json` and a description cache are the heaviest thing in a vault and worth nothing on the far side. **A fresh `seen.json` means the first radar run reports everything as new** — warn them, or it looks broken |
| 🔴 **UNKNOWN** | **Ask. Do not guess.** Markdown with no frontmatter is genuinely ambiguous: a note from another tool, a pasted job ad and a page of their history are indistinguishable, and they belong in three different folders |

## 3. Reconcile the frontmatter — the silent one

**Their vault predates this schema, so its types will not match.** In the first real migration **every
role page was typed `source`**, so `vault/roles/` came out empty and forty role assessments landed in
`wiki/`. Nothing was lost and nothing looked wrong.

- **Check `vault/roles/` is not empty** when they said they had assessed roles. If it is, retype and move
  them.
- 🔴 **`type: source` means a page ABOUT a source, not a source file.** The words are identical and the
  things are opposites — the sorter nearly moved a `CV.md` into `sources/`, the one folder that is never
  edited.
- **A type this schema does not have is a finding, not an error.** Tell them what it was and what you
  retyped it to.

## 4. Repoint what pointed at the refused files

**`wikilinks.py` finds these.** Links to a forked tool or an old `CLAUDE.md` now resolve to nothing —
repoint them at `SCHEMA.md`, `vault/AGENTS.md`, or the tool's new home.

**Run it until it reports zero.** Anything left is a decision somebody has to make.

## 5. Settings, extracted — never invented

**Their old configuration is usually not a config file.** In the first migration the search queries were
a Python list inside their fork and the location filters were three compiled regexes.

**Extract, do not guess.** 🔴 **Never write a location, a salary floor or a job title into
`vault/settings/search.json` that they have not stated.** An invented geography produces a filter that
silently matches nothing, and a radar that reports a quiet week is indistinguishable from one that is
broken.

**Say what you extracted and where it came from**, so they can correct it.

## 6. The key is theirs to place

**Tell them to put it in `vault/secrets/.env` themselves.** Never handle it, never read it out, never
copy it from an old config into the new one for them.

## 7. Close

- **Run `python3 tools/doctor.py`** and read it out. It says what is set up and what is not.
- **Append to `log.md`**: what was filed, what was refused, what was retyped, what is still unplaced.
- **Tell them the vault is theirs and the rest is not** — `git pull` updates the system and cannot touch
  a file under `vault/`.
- 🔴 **Then stop.** Do not offer to write a CV. **Do not run `/career-init`.** The right next step is
  `/career-lint`, which reads what they actually brought and reports contradictions, stale claims and
  gaps — and it is a far better use of the first session than an interview about things already recorded.

## What this does not do

- **It does not restructure and migrate at once.** Adopt the conventions in place first. Two changes at
  the same time means a mistake in one looks like a mistake in the other.
- **It does not verify anything they brought.** Their old wiki's claims arrive with whatever trust they
  had. **`/career-lint` is the pass that checks them**, and it is a separate job.
