# Design

**How the parts that needed a decision actually work.** [← back to README.md](../README.md)

**Split out of [`BACKLOG.md`](../BACKLOG.md) on 2026-08-28.** These are functional specifications — the
ATS registry's schema, how an employer entry is contributed back, which paths are load-bearing, what a
verifier does. **They describe the system as it is**, so they were never backlog items; they had simply
been written where the thinking happened.

🔴 **A design that lives in a backlog is read as a proposal.** Somebody picking the file up cold cannot
tell a specification of what exists from a sketch of what might, and both were sitting under the same
headings.

🟡 **Where a design has an outstanding piece, the outstanding piece is in the backlog and the design is
here.** Neither file should hold both halves.

---

### 🔴 Why this belongs in the repo when nothing else does

**Everything else here is per-user by construction.** The wiki is one person's career. The config is one
person's geography and salary floor. **None of it can be shared and most of it must not be.**

🟢 **An employer's careers endpoint is public, non-personal, and identical for everyone who looks it up.**
That makes it **the only artefact in this project a stranger can contribute to with zero privacy risk** —
and a repo that invites contributions needs somewhere safe for them to land.

---

### Prior art: adapters are a commodity, the maintained list is the gap

| | |
|---|---|
| **Open source** | `plibither8/jobber` and similar wrap Ashby, Greenhouse, Lever, BambooHR. **Adapter libraries — the same category as `tools/radar/adapters/`, not a registry** |
| **Commercial** | Apify sells *ATS company discovery* actors. **That is the genuinely hard half** — finding which of five hundred employers use Ashby — and it is a paid product |
| **Registries** | Marketing blog posts. *"Companies using Greenhouse include Stripe, GitLab, Figma…"* **Undated, unverified, unmaintained** |

🟡 **Know the boundary: this does not solve discovery.** It records what somebody already found. That is
still worth doing, because right now what somebody found is lost the moment their session ends.

---

## The schema

**`tools/radar/ats_registry.json`. Data, not code — contributing means adding an object, never touching
Python.**

```json
{
  "version": 1,
  "employers": [
    {
      "employer": "Stripe",
      "ats": "greenhouse",
      "params": { "token": "stripe" },
      "careers_url": "https://stripe.com/jobs",
      "publishes_salary": false,
      "last_verified": "2026-08-25",
      "verified_returned": 214
    },
    {
      "employer": "Northwind Traders",
      "ats": "workday",
      "params": {
        "host": "statestreet.wd1.myworkdayjobs.com",
        "tenant": "statestreet",
        "site": "Global"
      },
      "careers_url": "https://careers.statestreet.com/global/en",
      "publishes_salary": false,
      "last_verified": "2026-08-24",
      "verified_returned": 34
    },
    {
      "employer": "Grant Thornton Ireland",
      "ats": "oracle",
      "params": { "host": "ehzq.fa.us2.oraclecloud.com", "site": "CX_1" },
      "careers_url": "https://ehzq.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/GrantThorntonIrelandExperiencedHires",
      "publishes_salary": false,
      "last_verified": "2026-08-24",
      "verified_returned": 1
    },
    {
      "employer": "Deel",
      "ats": "custom",
      "params": {
        "list": "https://www.deel.com/api/deel-ats/jobs/",
        "detail": "https://www.deel.com/api/deel-ats/jobs/{id}/",
        "note": "Ashby underneath -- every row carries ashby_id -- but the public Ashby board returns empty, so this must target deel.com"
      },
      "careers_url": "https://www.deel.com/careers/",
      "publishes_salary": true,
      "last_verified": "2026-08-25",
      "verified_returned": 300
    }
  ]
}
```

**Field notes, each of which exists for a reason:**

| Field | Why |
|---|---|
| `ats` + `params` | **A common core with per-protocol parameters.** Greenhouse needs a token; Workday needs host, tenant and site as three separate values, because [there are two hosting styles](#) and deriving the host from the tenant silently misses employers |
| 🔴 `last_verified` | **Non-negotiable.** An employer changes ATS and the entry returns nothing — **which looks exactly like "no jobs this week"** |
| 🔴 `verified_returned` | **How many roles it returned when last checked.** *Returned 0* and *returned 214* are different health states and a date alone cannot tell them apart. 🔴 **Compare it as an order of magnitude, never for equality** — measured an hour apart, three of five entries had already moved (1347→1351, 7354→7357, 300→299). **A verifier testing equality would cry wolf on every run and be switched off within a week** |
| 🟢 `publishes_salary` | Rare and valuable. Deel publishes a band on every role, which takes PAY out of `TBC` before any call happens |
| 🔴 `careers_url` | **Always the company's own page — `stripe.com/careers/search`, never `boards.greenhouse.io/stripe`.** It is what a person actually pastes, and **it is the recovery key: when an employer switches ATS the endpoint dies and the careers page does not**, so that URL is how the replacement gets found. The ATS address belongs in `params` |

🔴 **Seeded, not comprehensive. Twenty verified entries beat five hundred guessed.** Board tokens are
frequently just the company name, which makes guessing work *often enough to be dangerous* — it produces
an entry that looks verified and is not.

---

## Where the entries come from: ask at the moment the user cares

🔴 **Do not ask users to go and compile a list. Ask once, about one employer, at the moment they are
already interested in it.**

**The trigger:** a role scores at or above the build threshold, or the user says they like one.

> *"Before I build this — can you find their own careers page and paste me the link? It takes a minute and
> it is worth more than it sounds."*

---

### 🟢 Explain why, because the reason is real and it changes behaviour

**The employer's own posting is materially better than the aggregator's copy, and this has been measured
twice:**

| | What the aggregator carried | What the employer's own site carried |
|---|---|---|
| **A professional services role** | *"Proficiency in [eight named tools]"* | 🟢 *"Proficiency in **at least one**…"* of eleven. **Two flagged capability gaps dissolved on one line** |
| | *"Consulting experience preferred"* | 🟢 *"…**or internal product delivery, or regulated environments**"* |
| | *(absent)* | 🔴 **The business driver for the role** — the strongest match in the whole posting |
| | Posted "roughly three weeks ago" | 🔴 **Three weeks older than stated** |
| **A remote SaaS role** | No salary | 🔴 **$80,000–$130,000 published — below the user's floor.** The application was never viable and the aggregator could not show it |
| | Posted "yesterday" | 🔴 **Ten weeks old** |

**The pitch to the user is not "help us build a list". It is:**

> **"Aggregators truncate, and they truncate the qualifiers — which is the half that decides whether you
> are eligible. They also re-date reposts, so a ten-week-old requisition looks like it went up yesterday.
> One link and I read the real thing. As a side effect it gets recorded, so nobody using this has to find
> it again."**

🟢 **The user benefit is immediate and personal; the registry entry is a by-product.** That ordering is the
whole design — a request framed as *"contribute to our database"* gets ignored.

---

### The original design

---

## Contributing it back: one file, and only one file

🔴 **This is the part that needs care, because the contribution flow runs from a working copy that contains
the user's private wiki.** The pre-commit hook exists for exactly this reason and must not be the only
thing standing between a helpful impulse and a published CV.

**The design, in order of strictness:**

1. 🔴 **Stage exactly one path — `tools/radar/ats_registry.json` — and refuse if anything else is staged.**
   Not "warn": refuse. `git status --porcelain` must show that file and nothing else before the flow
   proceeds.
2. 🔴 **Show the user the exact diff and get a yes**, before anything leaves the machine. It is four lines
   of JSON; there is no excuse for not showing it.
3. **Then, by what the user actually has:**

| Available | Route |
|---|---|
| `gh` CLI, authenticated | `gh repo fork` then `gh pr create` — **the only route that produces a real PR without the user understanding forks** |
| A browser and nothing else | **Open a pre-filled GitHub issue URL** with the JSON in the body. Zero git knowledge, works from a phone |
| Neither, or offline | **Print the JSON block and say where to paste it.** Still a contribution |

4. 🔴 **Never attempt to push to a repository the user does not own.** It fails, and failing at a git remote
   is exactly the moment a non-technical user concludes the whole system is broken.

🟢 **And run the same personal-data check the pre-commit hook runs**, on the file being contributed. An
employer name and a URL cannot leak anything — **but that is an argument for the check being cheap, not for
skipping it.**

---

## 🔴 Can you actually reach the listings from the careers URL? Four of five, and testing it found a bug

**Asked 2026-08-25, and worth having asked** — the recovery-key claim above was an assertion until it was
tested.

| From `careers_url` alone | |
|---|---|
| **SS&C** | 🟢 **Complete** — `myworkdaysite.com/recruiting/ssctech/SSCTechnologies` is in the page, host, tenant and site together |
| **Grant Thornton** | 🟢 **Complete** — host plus `sites/GrantThorntonIrelandExperiencedHires` |
| **JPMorganChase** | 🟢 **Complete** — host plus `sites/CX_1001` |
| **A large employer** | 🟡 **Host only.** The tenant is inferable from the host and the site still has to be probed |
| 🔴 **Deel** | 🔴 **Nothing.** No ATS marker anywhere in the HTML — **the endpoint was only ever visible in network traffic from a live browser** |

🔴 **So the recovery key works for employers who front a third-party ATS and fails for employers who proxy
their own.** That is a real limit and the schema should carry a `discovery` note for the second kind,
recording *how* the endpoint was found so nobody has to rediscover it from a network tab.

---

### 🔴 And testing it found a wrong entry, because Oracle fails open

**The Grant Thornton entry was seeded as `siteNumber: CX_1` — a 200 response returning 152 jobs. It was
wrong.**

| siteNumber | Returns | Contains their Data & AI role? |
|---|---|---|
| `CX_1` | 152 | 🔴 **No** |
| **`CX_1001`** | **55** | 🟢 **Yes — this is the experienced-hires site** |
| `GrantThorntonIrelandExperiencedHires` | 258 | *(the friendly name is not a valid siteNumber)* |
| 🔴 **`CX_9999`, pure nonsense** | **258** | **Returns 200 and the tenant's whole unfiltered list** |

🔴 **An unrecognised Oracle siteNumber does not error. It returns a plausible number.** So does the detail
endpoint — which is how the wrong value survived being used to fetch a real job successfully.

🟢 **Workday behaves the opposite way**: a wrong site 404s with an explicit `Job_Posting_Site_ID=` message.
**Two platforms, opposite behaviour on a wrong identifier, and only one of them tells you.**

**The rule this produces, and it governs the verifier below:**

> 🔴 **Verify by known-job presence, never by status code or job count.** A check that cannot fail is not a
> check — and both this registry and the ICON/aggregator work have now produced the same lesson from
> different directions.

---

### The design

🔴 **A registry without a checker rots into the silent-zero failure the `role-radar` skill already
documents** — every query returns nothing and the run reports a quiet week.

**`tools/registry_check.py`:** hit every entry, record what came back, update `last_verified` and
`verified_returned`, and **fail loudly on any entry that returned zero when it previously returned
something.**

🔴 **And check a known requisition id is present, not just that something came back.** Each entry should
carry one — the `verified_by` field — because on Oracle a wrong site returns 200 and a plausible count.
**Without that check the verifier would have confirmed the wrong Grant Thornton entry every time it ran.** Run it in CI if there is CI, and from `/career-lint` if there is not.

---

### 🔴 Read this before moving the user root — the paths that are load-bearing

**Compiled 2026-08-25 for the boundary work, from the code rather than from memory.** The move is
happening in a separate piece of work; this is the inventory it needs, and it is here because the person
doing it will be reading the entry below.

🔴 **`vault/postings/` is now load-bearing and it was not a week ago.** It is the **only durable copy of a
posting** — `raw.json` is overwritten every run with that run's new rows, so nothing else survives.
`radar.archive()` writes it, defaulting to `HERE/../../wiki/postings` with a `postings_dir` override in
the old tracked config (removed; settings now live in `vault/settings/`), and **`refresh.py`
reads it by path** when someone is about to apply. It is already on the
user's side of the line, but two tools now agree on where it is, and a third (`build-application` Step 0)
names the path in prose.

**Where a path is currently pinned, and to what:**

| | Holds | Note |
|---|---|---|
| `radar.py` | `CONFIG`, `RAW`, `SEEN`, `OUT`, and `archive()`'s default | **The four the handover asked to be told about.** Untouched this session |
| `radar/employers.py` | `employers.json` | 🔴 The private avoid list. **Never ships** |
| `doctor.py` | `sources/`, `wiki/`, `.git/`, both old config files, `employers.json`, `ats_registry.json` | **Seven paths in one file** — the most concentrated place the move will show up, and the one that will silently report `OPTIONAL` for everything if a root changes under it |
| `registry.py`, `registry_check.py`, `add_employer.py` | `ats_registry.json` | 🟢 System-side. Ships, and stays where it is |
| `export_review.py` | `vault/oversight/` | User-side |
| `verify.py`, `known.py`, `wikilinks.py`, `template_drift.py` | `--wiki`, defaulting to `wiki` | 🟢 **Already parameterised.** These need nothing |

🟢 **The pattern worth keeping**: the four that take `--wiki` are the ones that will survive the move
untouched. **Anything that computes a path from `HERE` is what has to change.**

🟡 **And one schema change, not a path**: `seen.json` records now carry `requisition` and `posted`, so a
repost can be spotted on a later run. Older records have neither and the check degrades to silence. **A
migration does not need to do anything about this** — it is additive — but a validator that rejects
unknown keys would break it.

---

---

### 🟢 The original design

**A user's idea, 2026-08-24, and it makes two existing features work better rather than adding a third.**

**The system currently evaluates every role on its own merits.** But candidates have standing positions
about employers that no scoring framework captures: **"I will not work for that company because they do
not pay for sick leave"** is not a capability score at all — it is a prior, and it should never
have to be re-derived.

**Two lists, and they do different jobs:**

| | What it does |
|---|---|
| 🔴 **Will not work for** | **Filters the radar before scoring.** An excluded employer's roles get dropped with a one-line note rather than assessed. Without it, the *assess-every-role-immediately* rule burns effort on something already decided |
| 🟢 **Would like to work for** | **Becomes the employer-board watchlist.** Greenhouse and Lever adapters watch whole boards, which gives complete and immediate coverage of an employer rather than whatever they syndicate. **That is only worth doing for employers the user actually cares about** |

**The second one is the more valuable half** and it is easy to miss. In the proving case the board
watchlist had been chosen by the agent, essentially arbitrarily. **It should be the user's list.**

#### Design points that need to be in the build

- **Each exclusion needs a reason AND a basis.** *"Their published policy says X"* and *"someone who
  worked there told me X"* are both legitimate reasons to decline an employer and **completely different
  kinds of claim.** The basis decides how durable the exclusion is.
- **Category exclusions matter more than name lists**, because a category catches employers the user has
  never heard of. Gambling, tobacco, arms, payday lending, or a documented employment-practices record.
  **Ask whether the objection is to the company or to the sector** — in the proving case a single bookmaker
  was named and it was genuinely unclear which.
- **Separate hard exclusions from "assessed and declined".** A principled exclusion is permanent; a role
  declined on commute or timing can return. **Recording both, differently, means a re-appearance is
  decided in seconds rather than researched again.**
- **Exclusions go stale.** Companies change ownership, policy and management. Date them.

#### Two refinements from first use, 2026-08-24

**1. "Watch everywhere", not "add to one adapter."** The first draft said a preferred employer joins the
Greenhouse watchlist. **That was too narrow and the user corrected it.** The point is complete coverage of
that employer, and which route achieves it varies: Greenhouse or Lever if they use one, **their own
careers API if not**, a named query as the fallback. **The list says who to watch; the adapter is an
implementation detail.**

🟢 **Worth knowing for the build: Workday careers sites are machine-readable.** Many large employers front
Workday on a custom domain, and the underlying endpoint takes a POST and returns JSON with no key:

```
POST https://<tenant>.wd1.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs
     {"appliedFacets":{},"limit":20,"offset":0,"searchText":"Dublin"}
```

**Verified working against a large financial employer.** Note the `wd1`/`wd5` numbering varies by tenant —
a `422` usually means the wrong shard, not a wrong request.

🔴 **There is a second hosting style and an adapter that assumes the first will silently miss employers:**

```
POST https://wd1.myworkdaysite.com/wday/cxs/<tenant>/<site>/jobs      # shared host
POST https://<tenant>.wd1.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs   # per-tenant subdomain
```

🟢 **Both resolve to the same API shape, so one adapter covers both — provided it takes host, tenant and
site as three separate inputs** rather than deriving the host from the tenant. **Verified against two
different employers, one on each style.**

🟢 **And there is a detail endpoint worth having**: `GET /wday/cxs/<tenant>/<site><externalPath>` returns
the full description, requisition id, posting date and — **the part the listing hides — the additional
locations.** A role advertised as one city is often open in four.

**A Workday adapter would cover a large share of enterprise employers** and is probably the highest-value
adapter still unbuilt.

✅ **Built 2026-08-25 as [`tools/radar/adapters/workday.py`](tools/radar/adapters/workday.py), with 22
tests against recorded response shapes.** Host, tenant and site are three separate config inputs, so both
hosting styles work; a `422` reports itself as a wrong shard rather than a generic failure; pagination
compares what it fetched against the API's own `total`, so `TRUNCATED` is a known gap rather than a
heuristic; and the requisition number is captured at ingest from `bulletFields`.

🟢 **The hidden-locations detail call earns its place, and it is measurable.** A listing saying
*"3 Locations"* is dropped by the location filter; expanded, the same posting keeps the city that saves
it. **Verified as an A/B against `location_ok`, not asserted** — the filter runs before any description is
read, so this is the only point at which the role can be rescued.

🟢 **Run against two live tenants the same day, one of each hosting style. It found two defects that no
recorded fixture could have**, which is the argument for doing this to every adapter:

| Found | Why a fixture could not catch it |
|---|---|
| 🔴 **The public URL differs by hosting style.** Shared-host needs a `/recruiting/<tenant>/<site>` segment the per-tenant form does not | **The fixture asserted the shape the code produced.** Both styles now verified as HTTP 200, and where the detail is fetched the employer's own `externalUrl` is used in preference to any construction |
| **Descriptions arrive with HTML entities intact**, so a company name with an ampersand in it came through as `Acme&amp;Co` | Invented fixture text had no entities in it |

🟢 **And it confirmed two design guesses cheaply.** `searchText` really does filter server-side
(352 → 127 → 0 on a nonsense term), so the query is worth sending rather than discarding as the board
adapters do. And **14 of 40 postings in one sample had hidden locations** — 35%, far more than expected,
which settles whether the extra call earns its place.

🟢 **One of those expansions is the "remote is country-scoped" defect, caught in the wild by a different
mechanism**: a posting listed as one city expanded to four entries, three of them of the form
*Remote - \<US state\>*. **State-scoped remote, invisible in the listing** — and a scope that decides
right-to-work and payroll before anything else about the role matters.

🟡 **The remaining limitation: Workday will only say "30+ Days Ago".** A role six months old and one exactly thirty days old
  produce the same string, so the derived date is a **floor**. It is rendered with a trailing `+` and the
  raw text is kept on the row — because a date that looks exact and is not is the aggregator-re-dating
  problem arrived at from the other direction.

🟢 **A contract change came with it, and it is the better design.** `fetch_body` now takes the whole row
rather than an id: a Workday posting is addressed by four values, and packing those into the id field to
fit a narrower signature is how an id stops being an id.

**2. 🔴 Exclusions have to work at division level, not just company level.**

**Found immediately in real use.** A user named a preferred employer *and* a division inside it he would
not work for. **Roughly a third of that employer's local postings turned out to belong to the excluded
division** — so a company-level filter would have surfaced them all, every run, forever.

**So the exclusion list needs entries at both levels**, and the filter has to read the division out of the
job title, since that is usually where it appears (*"Full Stack Engineer, <Division>, Vice President"*).

#### 🔴 The safety rule this needs, and it is not optional

**This list contains factual assertions about named companies, some from word of mouth.** That is entirely
legitimate as a private note and **completely unusable anywhere else.**

**It must never reach a CV, a cover letter, an oversight export, or anything a third party reads.** The
`export_review.py` allowlist already prevents this by construction — the exclusion list is not one of the
four reviewable file kinds — **but the rule should be stated explicitly rather than left to the file
filter.**

**And the agent should never suggest the user repeat it.** If asked why they are not interested in an
employer, the answer is *"it is not the right fit for me"* and nothing further. **Nothing is gained by
explaining, and a repeated second-hand allegation about a named employer is a real risk to the person
repeating it.**

---

### 🟢 The system treats every employer as a stranger, and often they are not

**Three related gaps, all surfaced in one conversation 2026-08-24.** The scoring framework and the
research step both assume no prior relationship with the employer. **In practice a candidate frequently
has one, and it is worth more than anything research can find.**

#### 1. Record the relationship, and use it

**A field on every employer page**: *worked there* · *works with them now* · *interviewed there before* ·
*knows people there* · *no relationship*.

**Why it changes things:**

- 🟢 **Pay becomes known rather than TBC.** In the proving case the user could state the employer's band
  for the grade he would target, from having worked there. **PAY is currently scored only where a band is
  published — personal knowledge of an employer's bands is a legitimate high-confidence source and the
  framework has no slot for it.**
- 🟢 **Research is partly redundant**, and the parts that remain are different. Culture, management and
  pay structure are already known; what is worth researching is what has changed since.
- 🟢 **It is the strongest possible answer to "why do you want to work here"**, and the honest one.
- 🔴 **A previous rejection is the same data structure.** The proving case included an employer the user
  interviewed with, was offered a job by, and declined over a contract term. **That belongs in the same
  field, not in a separate memory.**

#### 2. 🔴 Check for contractual restrictions on applying — nobody thinks of this

**If the user works for a supplier, consultancy, agency or outsourcer, their employer's contract with a
client may restrict them from being hired by that client.** Non-solicitation and non-hire clauses between
the parties are ordinary in vendor agreements.

**The proving case: a user who is customer-facing to a client every day, considering applying to that
client.** Their prior employment there and existing relationship make it an unusually strong application
— **and none of that matters if a clause blocks it.**

🔴 **This is discovered at offer stage or not at all**, which is the worst possible time. **A one-line
prompt when a target employer is a current client, customer or partner of the user's employer** would
catch it. **The system should flag it and say to read the contract — never assess the clause itself,
which is a solicitor's job.**

#### 3. The advertised location may not be the only option

**Large employers have satellite offices.** A role advertised for the head office may be workable from a
site much closer to the candidate — and **the posting will never say so, because it is advertising the
main location.**

**In the proving case an employer has an office in the user's own town, twenty-five miles from the
advertised location, and none of their postings mention it.**

**The scoring currently reads Lifestyle off the advertised location alone.** It should ask: *does this
employer have a site nearer than the one advertised, and can the role be worked from it?* **Treat the
answer as a question to ask, not an assumption** — but the upside is the difference between a two-hour
round trip and none.
