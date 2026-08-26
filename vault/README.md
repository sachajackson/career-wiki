# vault/ — everything that is yours

## Start here: put your CV in [`sources/`](sources/)

**That is the whole first step.** Drop it in, in whatever state it is in, and start the agent. If you
have a pile of other material and no idea what is worth keeping, put all of it in
[`migration/`](migration/) and ask the agent to sort it.

**Four folders ship with this repo — the four you put things into.** The rest are created as they are
first written to, so an empty vault does not present you with ten folders and ten decisions before you
have done anything.

**Nothing in here ships. Nothing in here is replaced by an update.** That is the whole point of the
split: the system lives outside this folder and can be swapped wholesale, and your working life lives
inside it and never gets touched.

**You can move this folder.** Zip it, carry it to another machine, drop it into a fresh clone, and you
are running again. Set `CAREER_VAULT=/path/to/vault` if you would rather keep it somewhere else
entirely — outside the repo, in a synced folder, wherever.

## What is in here, and which parts travel

| | | Carry it? |
|---|---|---|
| **`sources/`** | What you dropped in — CVs, LinkedIn exports, old documents. **Never edited by the agent** | **Yes** |
| `wiki/` | About you: history, how you work, achievements, what you want | **Yes.** This is the part that compounds |
| `roles/` | One page per role assessed | **Yes** |
| `companies/` | Employer and division research | **Yes** |
| `postings/` | Archived job descriptions | 🔴 **Yes — and this is the one nobody expects to need.** A posting is deleted the moment hiring finishes, which is right before you interview |
| `applications/` | One folder per application, with its interview pack | **Yes** |
| `oversight/` | Folders you open in another vendor's tool for review | Yes |
| **`settings/`** | What the tools read: search rules, employers, review | **Yes.** 🔴 But read [its README](settings/README.md) before sharing one |
| **`secrets/`** | An `.env`, and nothing else | 🔴 **Never.** Not in a zip, not in a backup you share, not in a message |
| `state/` | `seen.json`, `raw.json`, `shortlist.md` | 🔴 **No. Regenerable — delete it any time and nothing is lost** |
| **`migration/`** | A drop zone. See below | — |
| **`temp/`** | 🔴 **Yours.** Somewhere to drop a file mid-thought — a prompt, a note, a paste. **The agent reads it when you point at something; it never writes there.** Empty it whenever you like: nothing depends on anything in it | — |
| **`AGENTS.md`** | 🔴 **Your standing instructions to the agent** — tone, lines you will not cross, corrections it must not repeat. Created by `/career-init` | **Yes.** This one above all |

## `migration/` — where to put things when you do not know where they go

**Drop anything in here and ask the agent to sort it.** A career-ops export, a folder of old CVs, a
LinkedIn archive, notes from a previous system. You should not have to learn a directory structure
before you can start.

🔴 **It is a drop zone, not a home.** The agent empties it, files what it recognises, and **tells you
what it could not classify** rather than leaving it to rot. A file still sitting here after a session is
a question nobody answered.

## The one rule worth knowing

**If a tool writes something about you, it belongs in here.** If you find user data anywhere else in
this repository, that is a bug — `tools/tests/test_boundary.py` exists to catch it, and it will fail
the build rather than let it drift back.
