# You arrived here from a job application

*This page describes the tool. [The README](README.md) is for people who want to use it.*

**Two minutes, then you can stop reading.** Someone linked you here because their application was built
using this. It is open source and anyone may use it for any purpose, so **this page describes the
tool, not the applicant** — what it does, what it checks, and therefore what an application that came
through it has been put through.

### It is a knowledge base first, and a document generator only at the end

The applicant does not fill in a template. An agent **interviews them** about what they actually did,
files each answer as a page with its source, and the CV for your role is assembled from those pages on
demand. **There is deliberately no master CV** — a standing document drifts, and every claim in it stops
being traceable to anything.

**Which means each figure in the document you received can be traced back to a specific page, and to who
confirmed it.** Pages carry a trust tier: **generated** (a model wrote it and nobody has checked),
**machine-confirmed** (cross-checked against a second source), or **human-reviewed** — the applicant
confirmed it personally. 🔴 **Only the last tier is treated as safe to assert to you without a check.**

### Three checking layers, and the first one contains no AI

**This is the part worth two minutes if any of it is.** Large language models write fluent, confident,
wrong text. Every layer here exists because of that.

| | |
|---|---|
| **[`tools/verify.py`](tools/verify.py)** — deterministic | Extracts **every number** from an outgoing CV or letter, traces it back to a sourced page, **checks it is attributed to the right employer**, and fails on anything unsourced. **No model is involved.** The reasoning: a model is probabilistic, so the check on it must not be. It also runs a `--coverage` pass against the job posting itself |
| **[`tools/cv_lint.py`](tools/cv_lint.py)** — mechanical | Catches the tells: **banned AI vocabulary, participial tails, suspiciously round numbers, repetitive cadence,** non-ASCII punctuation that breaks applicant tracking systems |
| **[`tools/known.py`](tools/known.py)** — against the agent itself | Answers *"does this knowledge base already know this?"* in **three ways rather than two**: settled, present, established absence, or genuinely nothing. **Searching for evidence and finding none returns the same result whether a thing was never investigated or investigated and ruled out** — and those mean opposite things. It exists because an agent got that wrong three times in one session, and re-asked questions the user had already answered |
| **[`tools/wikilinks.py`](tools/wikilinks.py)** — structural | Finds links that go nowhere: **split across two lines** by a wrapping convention, **pointing at a missing page**, or **pointing at a heading that has been renamed.** None of the three looks broken while you are reading, and a knowledge base whose failure mode is silence is one you stop being able to trust |
| **`vault/oversight/`** — independent | The document is reviewed by **a different vendor's model**, in a fresh session, working from a restricted export. **Cross-model review rather than self-review** — and the export is allow-listed, so the reviewer only ever sees what you would see |

🟢 **And the checkers have their own checks.** [`tools/tests/`](tools/tests/) is **several hundred tests,
stdlib only, and it runs in seconds** — `python3 tools/tests/run.py`. Several encode bugs that were live in a shipped version:
the linter reporting *"clean"* on empty input, a crash on bullets with no words, and figures being sourced
from the very document under review, so a fabrication proved itself.

🔴 **None of it runs on memory.** An [agent hook](.claude/hooks/verify-artefact.sh) fires the verifier
**every time a CV or cover letter is written or edited**, and puts the findings straight back into the
agent's context so they have to be dealt with. **A control that depends on someone remembering to run it
is not a control.**

### Roles are scored against named frameworks, not a vibe

**Capability is assessed on three dimensions, each drawn from an established method rather than invented:**

| | Framework | The question |
|---|---|---|
| **NEED** | **Jobs-to-be-Done** | Is the thing this employer is most anxious about the thing the applicant is best at? *Read the spec for its underlying worry, not its requirements list* |
| **DELIVER** | **Topgrading Scorecard** | Reverse-engineer the outcomes the hiring manager should have written, then assess against those |
| **EDGE** | **Value Proposition Canvas** | Differentiated, or one of many? A capability every applicant has scores low |

**Then a fourth figure that is not a score at all**: the employer's **own named requirements**, counted —
each marked cleared, partial or gap. *"Nine of your twelve outright, two partially, one not at all."*
🟢 **It exists so that a judgement about capability can be checked line by line rather than asserted**, and
where the count and the judgement disagree, one of them is wrong and gets found out before anything is
written.

🔴 **Never summed.** Capability, lifestyle and employer stability are reported side by side, because a
single number lets a good commute hide a weak match, or the reverse. *Would deliver it well but so would
others* and *brings something rare, with real gaps* reach the same total and are not the same candidate.

🟢 **And every assessed posting carries a requirement count**: the employer's own stated requirements, each
marked **cleared, partial or gap**, with the tally. *"Nine of your twelve outright, two partially, one not
at all."* **You can check that line by line instead of taking a claim about fit on trust.**

### It researches the employer before it writes anything

**Not the posting — the company.** Financial trend and profitability, revenue by division, whether the core
business is under structural threat, acquisitions, restructuring and headcount, leadership changes,
employee sentiment, and what the local office actually is. **Company-level and division-level separately**,
because a group can be struggling while the division hiring is growing, or the reverse. Research pages
carry an expiry date and are flagged when stale.

**A practical consequence you may notice:** the applicant will have read your last set of results, and
their questions will be about your division rather than your homepage.

### The rest of it

- **Job search across multiple sources** — [adapters](tools/radar/adapters/) for Workday, Oracle, Greenhouse, Lever, Adzuna
  and LinkedIn, plus direct Workday and Oracle recruiting endpoints, which return more than the aggregators
  do — the real posting date, the requisition number, and the additional locations a listing hides
- **The employer's own posting is fetched in preference to any job board's copy**, because aggregators
  truncate — and they truncate the qualifiers, which is the half that decides eligibility
- **[`BACKLOG.md`](BACKLOG.md)** — the system's own defects, written up honestly: what broke, what it cost,
  what would prevent it. **Including the occasions it was wrong about the person using it**
- 🔴 **Nothing personal is in this repository.** A [`PRIVACY.md`](PRIVACY.md), a
  [pre-commit hook](githooks/pre-commit) that blocks personal paths and content **even when someone forces
  the add**, and an allow-listed oversight export. **The private knowledge base and the public tool are
  separate by construction, not by care**

### "Did the applicant build this, or just use it?"

**A fair question, and this page cannot answer it — which is the point of saying so.** The repository is
public and anyone may use it. **If they claim to have written it, they should say so themselves, and you
can check:**

- **The commit history** shows who wrote what and when, and GitHub marks a forked repository as a fork.
- 🟢 **[`BACKLOG.md`](BACKLOG.md) is the part that cannot be copied.** Anyone can clone a codebase. **A
  defect log written in first-person operational detail — dated, with what it cost — is a record of
  running the thing rather than possessing it.**
- 🟢 **Or just ask.** *Why are the scores split into three? What broke, and what changed as a result? Why
  is the verifier deliberately not an AI?* **The answers are more interesting than the code, and only
  someone who has actually used this has them.**

### It was built with AI, and says so

**Every commit records it.** The system is written and maintained by an AI coding agent. 🟢 **That is the
demonstration rather than the admission:** building quickly with a model, then wrapping its output in
deterministic verification, mechanical linting and independent cross-vendor review **because the model
cannot be trusted unexamined**, is the whole design. **The warning immediately below this section is not
boilerplate — it is the premise the rest of the repository is built on.**

---

**The warning that governs all of this is [`DISCLAIMER.md`](DISCLAIMER.md)**, and it is the premise the
repository is built on rather than boilerplate at the bottom: **every output is a draft its author must
read and stand over.** The checks reduce risk. They do not remove it.
