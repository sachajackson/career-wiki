# Career Wiki — instructions for the agent

**This is the canonical instruction file.** It is [AGENTS.md](https://agents.md/), the vendor-neutral
convention stewarded by the Agentic AI Foundation, so that this system works in whichever coding agent
you already use rather than only in one. `CLAUDE.md` is a one-line pointer at this file; other tools'
conventions should be the same.

**Three files, and the split is the point:**

| | | Replaced by an update? |
|---|---|---|
| **This file** | The boundary and where things go | Yes |
| **[`SCHEMA.md`](SCHEMA.md)** | The schema, the operations, the rules that hold for everybody. **Read it before writing anything into the vault** | Yes |
| 🔴 **`vault/AGENTS.md`** | **The user's own standing instructions.** Read it at the start of every session and follow it. **If it is missing, create it from [`templates/vault-AGENTS.md`](templates/vault-AGENTS.md)** — it is untracked, because it is the one file in the vault the user writes and `git add -A` would publish it | **Never** |

**`vault/AGENTS.md` is the one file in this repository that belongs to the user**, and it exists because
the two kinds of instruction were mixed for months. A rule like *"never call me a leader"* and a rule
like *"frontmatter goes at the top of the page"* look identical on the page and behave nothing alike: one
is personal and permanent, the other is system detail that changes when the tools change. Mixed together,
an update either destroys the first or refuses to touch the second.

🔴 **When the user corrects you, write it into `vault/AGENTS.md` with the date and the reason** — not
into your reply, and not into `SCHEMA.md`. A correction you do not record is one you will need again next
week. Where the two disagree, `vault/AGENTS.md` wins on style, tone and emphasis; `SCHEMA.md` wins on
structure; and the rules under *Rules that are not negotiable* are overridable by neither.

## The boundary, in one paragraph

**Everything about, belonging to, or specific to the user lives under `vault/`.** Everything else is the
system and can be replaced wholesale by an update. **Never write user data outside `vault/`** — not into
`tools/`, not into `.claude/`, not into a working file beside the code. `tools/tests/test_boundary.py`
fails the build if you do, and it exists because user data sat inside `tools/` for months and made an
update mechanism impossible.

**Paths come from `tools/lib/paths.py`, never from string literals.** One file knows where things are,
so moving the vault touches one file.

## Where to put what

| | |
|---|---|
| Something the user gave you | `vault/sources/` |
| Something you learned about the user | `vault/wiki/` |
| A role you assessed | `vault/roles/`, and archive the posting to `vault/postings/` |
| Research about an employer | `vault/companies/` |
| A CV, a letter, an interview pack | `vault/applications/<Employer Req>/` |
| A setting a tool reads | `vault/settings/` — **the right one of the five**, listed in [`SCHEMA.md`](SCHEMA.md). 🔴 **Ask for the value; never invent one** |
| An API key | `vault/secrets/.env`, and nowhere else. **Never in a JSON file, never in a commit** |
| Anything regenerable | `vault/state/` — and it must be safe to delete |
| Something you cannot classify | 🔴 **Say so by name.** Do not invent a home for it |

## The rule that governs everything else

**Every instruction-shaped control in this repository has failed at least once. Every executable one has
held.** When something goes wrong twice, the fix is not a stronger warning — it is a check. And the
first version of a check usually cries wolf, which is how good checks get switched off, so **test the
false-positive case before shipping one.**
