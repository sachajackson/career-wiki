---
name: market-standards
description: Research how CVs, cover letters and profiles should be built for THIS user's country, level, industry and target roles, and write the findings into the vault as reference pages the artefact skills read. Run once, then refresh every six months.
---

# market-standards

**The system has a writing standard and no market standard.** `build-application` knows how a sentence
should read; nothing knows **how long a CV should be, whether education stays on it, whether a cover
letter is expected at all, or what a regulator requires of an accurate one.**

🔴 **All four of those answers change with country, level, industry and target role.** A US one-page
résumé convention applied to a director-level application in Europe is simply wrong, and until this skill
runs, nothing in the system knows that.

## What it writes

**Four pages in `vault/wiki/`.** `type: synthesis`, `section: career`, `stale_after` six months out.

| Page | Covers |
|---|---|
| `CV Layout and ATS Standards.md` | Length, structure, section order, typography, PDF vs DOCX, what each ATS actually does with the file, layout by level |
| `Cover Letter Standards.md` | Whether one is expected at all, length, structure, tone, the form-field variant |
| `LinkedIn Profile Standards.md` | Headline, About, skills, visibility settings, what is searchable |
| `<Board> Profile and Sourcing Standards.md` | The boards that matter **in this user's country** — see below |

🟡 **These are reference pages, not deliverables.** They live in the vault, they are never committed, and
they are read by other skills rather than by the user. **Cross-link all four to each other** so they
resolve as a set.

🔴 **Filenames must not collide with the user's own pages.** A vault may already hold `LinkedIn.md` and
`Indeed.md` describing *their profile as it stands*. **These pages describe the market, not the person**,
and the `... Standards` suffix is what keeps the two apart. Say which is which when you write them.

## 0. Gather the dimensions first — from the vault, not from assumptions

**Read before searching.** `vault/wiki/`, `vault/AGENTS.md`, `vault/roles/`, the scoring framework.

| Dimension | Where it comes from | Why it changes the answer |
|---|---|---|
| **Country** | Location constraints, employer history | 🔴 **The biggest single swing.** One page is a US convention; two is the UK and Irish norm. Photo and date-of-birth conventions differ across Europe. Some markets expect a personal statement |
| **Level** | Their most recent roles | Length, what leads, whether education stays, whether a competencies block sits above or below experience |
| **Industry** | Employer history and target roles | Education permanence, register, what counts as a metric, whether a cover letter is expected |
| **Target roles** | `vault/roles/` and the scoring table | The vocabulary a recruiter would actually search on |
| 🔴 **Regulatory exposure** | **Derive from industry + country** | Ireland's Central Bank fitness-and-probity regime makes CV accuracy a regulatory matter for pre-approved controlled functions; the UK's SM&CR is the analogue. **Where it applies it is a hard constraint in the CV page, not a footnote** |

🔴 **If the vault does not say what industry or level they are at, ask. Do not infer it from one employer
name.** A wrong country or level produces four pages of confidently wrong advice, and those pages then
get used to build documents.

🔴 **Ask as numbered plain text in the message body, never as a picker** — see `vault/AGENTS.md`. A
question the user cannot see is a question that gets answered by assumption.

### Which boards to research

**Do not hardcode Indeed.** LinkedIn is near-universal and Indeed is broad, **but a market may have a
dominant local board that matters more than either.** Work out which from the vault's own search settings
and role history, research those, and **name the file after what was actually researched.**

## 1. Use the deep-research skill. Do not reimplement it

**Invoke `anthropic-skills:deep-research` once per topic, passing the dimensions in the arguments.**

🔴 **Check it is available first.** If it is not, say so, explain what the pages would have contained, and
**stop** — do not half-produce a page from a plain web search and present it as researched.

🔴 **Four separate runs, not one.** The topics have different evidence bases and reach different
confidence levels, and merging them hides exactly that difference.

🟡 **Say how long it will take before starting**, and checkpoint between runs. Four deep-research passes
is a long job and silence reads as a hang.

## 2. 🔴 Never put the user into a search query

**This skill runs web searches.** The natural way to write a personalised query is to personalise it with
personal data, and that is the one thing it must not do.

**Never search their name, employer, salary floor, requisition numbers, or anything else identifying.
Research the category:** *"senior delivery roles in <country> financial services"* — never the person.

## 3. Weight the sources, or the research returns marketing

🔴 **This field is dominated by vendors selling the anxiety they describe.** A plain search returns ten
résumé-optimiser blogs before anything primary. **Instruct each run to weight toward:**

| Source | Why |
|---|---|
| **ATS vendor help documentation** — Greenhouse Support, Workday, Lever | Where the real mechanics are actually written down |
| **Platform help and privacy pages** — LinkedIn Help, board privacy FAQs | 🟢 **Settings documentation is primary source**, and it is where the genuinely useful findings were |
| **Regulators** | Anything about accuracy obligations |
| **Employer-side review sites** — Capterra, G2, Software Advice | 🟢 **People who paid for a product complain candidly about it** — the closest thing to practitioner testimony available |

🔴 **Reddit is blocked to the search tool. Do not plan around it.**

## 4. 🔴 Known-false claims — carry these so every run does not relearn them

**Each of these will resurface. Name them in the finished pages as false, with the reason:**

- 🔴 **"75% of résumés are auto-rejected by an ATS."** Traces to **Preptel**, a vendor that shut down in
  August 2013 and never published a study. The number drifts between 70, 75 and 88% as it is recopied.
- 🔴 **"The LinkedIn headline is indexed at 5× weight."** and **"verified skills rank 30% higher."**
  **LinkedIn publishes no ranking factors at all.** Both are vendor invention.
- 🔴 **"Posting weekly lifts you in recruiter search."** Unsourced everywhere it appears, and it conflates
  feed reach with search ranking.
- 🟡 **The 7.4-second eye-tracking figure** is one 2018 study of **30 recruiters**, never peer-reviewed,
  published by a company selling résumé services. **The F-pattern is sound; the stopwatch is decoration.**

## 5. Confidence marking is load-bearing here

🔴 **The four topics differ enormously in evidence quality.** ATS mechanics rest on vendor documentation
and are solid. **LinkedIn ranking is undocumented and nearly everything written about it is inference.**

**Every page carries a confidence level and a *where this could be wrong* section, and the LinkedIn page
must be visibly the most hedged of the four.** A page that sounds equally certain about both is lying
about one of them.

## 6. Page structure that worked

**In order. Each of these earns its place; the last four are what stop the page being a blog post:**

| Section | Why it is there |
|---|---|
| **TL;DR** | The page is read by a skill mid-task, not by a person with an afternoon |
| 🔴 **Context and scope** | **What was researched, against which dimensions, and as at what date.** This is what makes the page re-judgeable when the user's country or level changes — without it, a stale page is indistinguishable from a current one |
| **The three jobs, and why they conflict** | An artefact is hired to do several jobs at different moments and they want different documents. **Most advice optimises one and silently breaks the others** |
| **The mechanics** | Topic-specific: what an ATS does with the file, how a recruiter actually reaches you, what the privacy default is |
| **By level** | Which job dominates changes with seniority, so the layout should too |
| **Industry comparison** | Two named industries, side by side. Generic advice is the average of markets that disagree |
| **What conventional advice is now wrong about** | Explicitly, with the reason |
| 🔴 **Competing perspectives, and where this could be wrong** | **The red team. Not optional** — see §5 |
| **Decisions this leaves open** | What the research could not settle, handed back rather than papered over |
| **Sources and confidence** | Per source, with its weighting and why |

**Also state what is out of scope**, and point at whatever owns it — the market page covers the document,
the writing standard covers what goes in it, and neither should duplicate the other.

## 7. Close

- **Append a `research` entry to `log.md`** naming what was researched and **the dimensions used** — the
  dimensions are what make the pages re-judgeable when the user's situation changes.
- **Tell them the pages are read by other skills**, not by them.

## Refreshing one page

```
/market-standards --refresh cv
/market-standards --refresh cover-letter
/market-standards --refresh linkedin
/market-standards --refresh boards
```

**Redoes one topic without redoing four.** 🔴 **Refresh the page whose `stale_after` has passed, not all
of them** — re-running four when one expired burns an hour and produces three pages identical to the ones
already there.

## What this does not do

- **It does not write a CV.** It writes what a CV in this market should look like. `build-application`
  reads it.
- 🔴 **It does not override the writing standard.** **The market standard decides structure; the writing
  standard decides sentences.** Where they conflict, that split is the answer — see `SCHEMA.md`.
- 🔴 **It does not produce the same pages for everybody, and that is the test.** A US junior candidate in
  tech should get materially different pages from a director in a regulated industry elsewhere. **If two very
  different users get near-identical pages, the personalisation is not working** — and that is the first
  thing to check, before any individual claim in them.
