# Career Wiki — instructions for the agent

**This is the canonical instruction file.** It is [AGENTS.md](https://agents.md/), the vendor-neutral
convention stewarded by the Agentic AI Foundation, so that this system works in whichever coding agent
you already use rather than only in one. `CLAUDE.md` is a one-line pointer at this file; other tools'
conventions should be the same.

**The schema, the operations and the rules live in [`SCHEMA.md`](SCHEMA.md).** Read it before writing
anything into the vault.

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
| A setting a tool reads | `vault/settings/` — the right file of the four |
| An API key | `vault/secrets/.env`, and nowhere else. **Never in a JSON file, never in a commit** |
| Anything regenerable | `vault/state/` — and it must be safe to delete |
| Something you cannot classify | 🔴 **Say so by name.** Do not invent a home for it |

## The rule that governs everything else

**Every instruction-shaped control in this repository has failed at least once. Every executable one has
held.** When something goes wrong twice, the fix is not a stronger warning — it is a check. And the
first version of a check usually cries wolf, which is how good checks get switched off, so **test the
false-positive case before shipping one.**
