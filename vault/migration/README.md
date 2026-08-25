# migration/ — drop anything here

**You do not need to know where things go.** Put whatever you have in this folder and ask the agent to
sort it: a career-ops export, a pile of old CVs, a LinkedIn data export, notes from another tool, a
folder of job descriptions you saved.

## What the agent does with it

1. **Reads everything**, and works out what each file is
2. **Files what it recognises** into `sources/`, `wiki/`, `roles/`, `companies/` or `postings/`
3. 🔴 **Tells you what it could not classify, by name** — and leaves those here rather than guessing

**Point 3 is the one that matters.** A file quietly left in a drop zone looks identical to a file that
was dealt with. If something cannot be placed, it should be a sentence in the conversation, not a
surprise in six weeks.

## Migrating from another system

**Bring the raw material, not the derived documents.** Your history, your notes, the job descriptions
you kept — those are worth having. Generated CVs from another tool are worth less than the facts
behind them: this system rebuilds documents from the wiki each time, so an old output is only useful
as a source of claims to verify.

🟡 **Anything with a number in it is worth keeping**, even in a form nobody can read. A figure you can
no longer source is a figure that cannot go on a CV, and the whole point of the wiki is that every
number has somewhere it came from.
