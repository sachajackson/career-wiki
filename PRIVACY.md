# Sensitive data: what this holds, where it goes, and what you should decide

**Read this before your first interview session, not after.**

A career wiki ends up holding more sensitive material than almost anything else you would keep on a
laptop. Not because it is designed to, but because doing the job properly means recording your salary
floor, why you want to leave, what you are worried about, your employer's internal detail, and — unless
you are careful — information about people who never agreed to be in it.

None of this is a reason not to use the system. It is a reason to know what you are doing.

---

## 1. Where things physically live

**Everything of yours is under `vault/`. Nothing else in the repository is.** That is the whole boundary,
and it is enforced by three things that have to agree: the ignore rule, a pre-commit guard that inspects
what is actually staged — **so it holds even against `git add -f`** — and `tools/tests/test_boundary.py`,
which fails the build if either drifts.

| What | Where | Leaves your machine? |
|---|---|---|
| `vault/sources/` — your CV and documents | Your disk. **Never committed** | Only as part of a conversation, when the agent reads a file |
| `vault/wiki/`, `roles/`, `companies/`, `postings/` — everything the agent writes | Your disk. **Never committed** | Same |
| `vault/applications/` — the CVs and letters themselves | Your disk. **Never committed** | Same. **And to the employer, when you send them** |
| 🔴 `vault/AGENTS.md` — your standing instructions | Your disk. **Never committed** | Read at the start of every session, so **yes, every session** |
| 🔴 `vault/settings/employers.json` — employers you will not work for | Your disk. **Never committed** | Only when a search runs. **See below: this is more sensitive than it looks** |
| 🔴 `vault/secrets/.env` — your API key | Your disk. **Never committed** | **It authenticates you.** Treat a leak as a billing incident and revoke first |
| `vault/state/` — search results and history | Your disk. **Never committed** | No. Regenerable: delete it any time |
| `vault/oversight/<application>/` — export folders for review | Your disk | 🔴 **Yes, deliberately — to another vendor's model.** Allow-listed, so it carries only what a recruiter would receive |
| Conversation transcripts | `~/.claude/projects/`, **in plain text**, 30 days by default | See below |
| The repo itself | GitHub, if you forked it | **The system only.** Five README files ship under `vault/` to say what each folder is for. Nothing else there is tracked |

### 🔴 `employers.json` deserves its own line

**It names companies you will not work for, and usually why** — a bad interview, something a friend told
you, a reputation you have heard about and cannot evidence. **Some of it is second-hand, and some of it
would be awkward if the company read it.**

It is the file to check first, after `secrets/`, if you are ever sending your vault anywhere — and it is
excluded from an oversight export for exactly this reason.

**Change the local transcript retention** with `cleanupPeriodDays` in your Claude Code settings if 30 days
in plaintext on disk is longer than you want.

**Two practical points people miss:**

- **A gitignored file is not an encrypted file.** Anyone with access to your laptop or your backups can
  read the whole wiki. Turn on full-disk encryption (FileVault on macOS, BitLocker on Windows).
- **Think before putting this in a synced folder.** Dropbox, iCloud Drive, OneDrive and Google Drive will
  happily replicate your salary floor and your reasons for leaving to a cloud account, and possibly to a
  work-managed device. If you want sync, use a **private** repository, not a consumer sync folder.
- 🔴 **If you do sync or back up the vault, leave `secrets/` out of it.** The rest of `vault/` is yours to
  carry between machines. An API key in a backup is an API key in whatever that backup touches.

---

## 1a. There is no tier of this that is private from the model

🔴 **Claude Code runs locally, but to answer anything it sends the contents of the files it reads to
Anthropic's API.** Writing something into a file is not hiding it from the AI — **it is the opposite of
hiding it.** Local storage is not concealment, and this is the single most misunderstood thing about how
the system works.

**What that means in practice:** say "do not record this" whenever you want, and it will be respected in
what gets *written*. It cannot be unheard in the conversation where you said it.

---

## 2. What Anthropic receives

**The honest structural answer: there is no tier of this wiki that is private from the model.** Claude
Code runs locally, but to answer anything it sends your prompts and the contents of the files it reads to
Anthropic's API over TLS. **If the agent reads a page, that page is transmitted.** Writing something into
a file rather than saying it out loud changes nothing.

So the question is not *whether* it is sent, but what happens to it afterwards — and **that depends on
your plan**:

| | Used to train models? | Retention |
|---|---|---|
| **Free, Pro, Max** | **Only if you have the setting on.** Your choice, and it is on a per-account toggle | **5 years** if on, **30 days** if off |
| **Team, Enterprise, API** | **No**, unless your organisation opted into the Development Partner Program | 30 days standard. Zero Data Retention available to qualified Enterprise accounts |

🔴 **If you are on a consumer plan, go and look at your setting before you start**:
[claude.ai/settings/data-privacy-controls](https://claude.ai/settings/data-privacy-controls). A job search
wiki containing your employer's internal detail and your colleagues' circumstances is exactly the material
to make a deliberate decision about, rather than discovering the default later.

**Three other things that send data, all of which you control:**

- **`/feedback`, `/bug` and `/share`** send a copy of your conversation, including file contents.
  **Retained for five years.** Do not use them from a session where you have been discussing something
  confidential. Disable with `DISABLE_FEEDBACK_COMMAND=1`.
- **The "How is Claude doing this session?" survey** records only a rating. The **separate** follow-up
  asking to look at your transcript uploads the session and any subagent transcripts if you say yes.
  Nothing is uploaded unless you explicitly choose **Yes**.
- **Telemetry** — latency and usage patterns. **Never includes your prompts, code or file paths.** Error
  reports redact known secrets, paths and email addresses. Turn both off with
  `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`.

The authoritative and current version of all of this is at
[code.claude.com/docs/en/data-usage](https://code.claude.com/docs/en/data-usage). It changes; this file
may not.

---

## 3. Other people are the hard problem

**You consented to being in this wiki. Nobody else did.**

Your working life is full of other people, and an interview about what you do will naturally produce
information about them. The agent is instructed to record the *structure* and not the *identities*.

### Never recorded, at any point, in any form

- **Anything about a named or identifiable colleague in a personnel context**: performance, capability,
  discipline, grievance, redundancy selection, who was nominated, who is at risk.
- **Team composition that identifies someone by elimination** — "the only person in the team who…" names
  them just as effectively as writing it down.
- **Health, disability, family circumstances or personal difficulties** of anyone other than you.
- **Referees' contact details.** They do not go on a CV either.

**This material is never positioning content.** The agent will not draft CV bullets from it, mine it for
framing, or apply the usual "how does this help" lens to it. If you disclose something in this category,
expect it to be acknowledged and not written down.

### Recorded as a role, not a person

The useful version of "who else was involved" is almost always structural:

> ✅ *"A senior developer in the team built the automation platform."*
> ❌ *"[Name] built the automation platform."*

Roles are what a CV can use. Names add nothing and carry risk.

### One thing worth knowing, which is not legal advice

**In the EU, the UK and similar regimes, holding personal data about other people in a system you control
can make you a data controller for it**, with obligations attached. That is unlikely to be a practical
problem for a private wiki that records roles rather than identities — which is another reason the rule
above is the rule. If you are unsure, ask someone qualified. **Nothing in this repo is legal advice.**

---

## 4. Your employer's material

Your best CV evidence comes from work you did for someone else, some of which is theirs and not yours.

| Tier | Example | In the wiki | In a CV or profile |
|---|---|---|---|
| **Ordinary work detail** | Volumes, team size, tooling, what you built | ✅ Freely | ✅ Freely |
| **Internal names** | Project and system codenames | ✅ Useful, keeps pages readable | 🟡 **Describe generically** unless you have cleared the specific name |
| **Client-identifying** | A system named after a client; a client's name under NDA | 🟡 Record it, under an explicit never-share marker | 🔴 **Never**, and default to a generic reference even in conversation |
| **Personnel and confidential** | Anything in section 3; unpublished financials; security detail | 🔴 **Not at all** | 🔴 **Never** |

**Check your own contract.** Confidentiality clauses vary and this repo cannot know yours. The default the
agent applies is caution: **any name that sounds internal gets described generically in external documents
unless you say otherwise.** Commercial product names — the tools you used — are always fine.

---

## 5. Your own sensitive information

Some of the most useful material for choosing a role is material you would not want repeated.

**The system's approach: record the constraint, not the reason.**

> ✅ *"Cannot commit to travel at short notice. Hard constraint."*
> ❌ *"Cannot travel at short notice because of [personal circumstance]."*

The first is everything the scoring framework needs. The second is a medical or family record sitting in a
markdown file, and it buys nothing.

**Two categories get explicit protection:**

- **Decision context, never positioning.** The interview asks questions like *"what are you worried
  someone will find out?"*, because the answer usually governs which roles are a bad idea. That answer is
  used to steer role selection and is **never** used as CV or cover-letter material.
- **Anything you mark private stays excluded permanently.** If you say a piece of history is not to go on
  external documents, the agent records it if it is genuinely part of your history but will never propose
  re-including it. The exclusion is yours and it stands until you raise it again yourself.

**If you would rather something were not written down at all, say so.** "Do not record this" is always
respected, and the agent should tell you when it is declining to file something.

---

## 6. If something sensitive is already in there

1. **Say so.** The agent will find every occurrence, including in generated CVs and cover letters, which
   are the places people forget.
2. **Removing it from a file is not enough if the repo is tracked.** If you ever committed personal
   material, it stays in the git history and is recoverable. The reliable fix for a private repo is to
   rebuild the history; for anything already pushed publicly, treat it as public.
3. **Local transcripts are separate.** `~/.claude/projects/` holds the conversation in plain text
   independently of the wiki. Clearing it is a separate step.
4. **If it went to Anthropic in a conversation**, your plan's retention applies — and if you sent it via
   `/feedback` or `/share`, that is a five-year retention, so mention it.

---

## 7. The short version

- **Turn on disk encryption.** Do not put the wiki in a consumer sync folder.
- **Check your data-training setting** if you are on a consumer plan.
- **Do not use `/feedback` or `/share` from a session about anything confidential.**
- **Colleagues appear as roles, never as names**, and never in a personnel context at all.
- **Say "do not record this" whenever you want, and it will be respected.**
- **Nothing of yours is ever committed** — everything personal is under `vault/`, and a pre-commit guard
  refuses it even against `git add -f`.
- 🔴 **Your API key lives in `vault/secrets/.env` and nowhere else.** Never in a settings file, never in a
  backup you share. If you think it has leaked, revoke it first and work out how afterwards.
