# temp/ — somewhere to put a file mid-thought

**Drop anything in here that you want the agent to read but not keep.** A prompt you drafted, a job
description you pasted, a screenshot, a document you want an opinion on. **Then point at it** — *"read
the file in temp"* — and it will.

## What makes this different from `migration/`

**They look similar and they are not.**

| | |
|---|---|
| **`migration/`** | *"File this into my vault."* A drop zone the agent **empties**, sorting what it recognises into `wiki/`, `roles/`, `sources/` and the rest |
| **`temp/`** | *"Read this, it is context, not a permanent record."* The agent **never files it and never writes here** |

🔴 **If a file in here turns out to be worth keeping, it does not stay here.** It becomes a wiki page, a
source, or a role page — and the copy in `temp/` stops mattering. **The whole point of the folder is that
nothing depends on anything in it.**

## The rules

- 🟢 **Empty it whenever you like.** Nothing in the system reads from here unless you ask it to, and
  nothing breaks when a file disappears.
- 🔴 **The agent reads it on request and never writes to it.** If it needs to save something, that goes
  where the thing belongs — not into a folder you might clear tomorrow.
- **It is not committed**, like everything else under `vault/`. Only this README ships.

## What not to put here

**Anything you would be upset to lose.** It is called `temp/` for a reason. If it is your only copy of
something, put it in [`sources/`](../sources/) instead — that folder is never edited and never emptied.
