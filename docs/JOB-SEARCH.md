> **Part of [Career Wiki](../README.md).** Configuring the search, once installed.

# Setting up job search

Search runs through adapters in `tools/radar/adapters/`. Copy `templates/settings/search.example.json` to `vault/settings/search.json` and
fill in what you have. Nothing under `vault/` is ever committed, so your settings stay on your machine.

| Adapter | What it needs | Notes |
|---|---|---|
| **adzuna** | A free API key from [developer.adzuna.com](https://developer.adzuna.com/) | Documented and supported. 🔴 **Check your country is covered before relying on it** — GB, US, NL, DE and others work; **Ireland is not covered and returns 404** |
| **greenhouse** | Employer board names | Public data, no key. Best for watching specific target employers |
| **lever** | Employer handles | Public data, no key. Same idea |
| **oracle** | Host and site, both read off the employer's careers URL | Public data, no key. The other large enterprise ATS. **Gives an exact posting date**, the requisition number, and a description in the listing itself. Verified against three live employers |
| **workday** | Host, tenant and site, read off the employer's careers URL | Public data, no key. **A large share of big employers run Workday**, including where the careers site looks bespoke. Returns the requisition number and the real posting date, and expands roles advertised in one city that are open in several. Verified against two live employers, one of each hosting style |
| **linkedin** | Nothing | **Off by default.** Uses an undocumented endpoint, is against LinkedIn's terms of service, and will break without warning. Enable knowingly or not at all |

You also set your location rules in the same file: which places are acceptable, which are not, and which
are borderline.

### 🟢 Name employers, not endpoints

**You should not have to know that watching Stripe means writing a Greenhouse board token and watching
one large employer means writing a host, a tenant and a site.** So you do not:

```json
"watch": ["Northwind Traders", "Statesman Bank"]
```

**A shipped registry — [`tools/radar/ats_registry.json`](../tools/radar/ats_registry.json) — knows which ATS each
employer uses**, and the endpoint is looked up at run time. **Fifteen employers, around 13,000 live roles,
every entry verified by calling it.**

**To see who is on it:**

```bash
python3 tools/radar/registry.py --list
```

Names, ATS, how many roles each had when last checked, and which employers publish a salary band. **It
reads the file and calls nothing**, so it costs nothing to look.

🔴 **Anything it cannot resolve is reported at the start of the run, by name.** An employer you thought you
were watching, quietly not searched, looks exactly like a quiet week — which is the worst thing a job
search tool can do to you.

**Adding one is a line:**

```bash
python3 tools/add_employer.py "Monzo" https://monzo.com/careers
```

It reads their careers page, works out which ATS is behind it, **calls the endpoint to prove it works**,
and writes the entry. If the page is JavaScript-rendered it tries the company name as a board token and
**asks you to confirm before trusting it** — a guess that verifies is still a guess.

🟢 **Then `--contribute` offers it upstream**, staging that one file and refusing if anything else in your
working copy has changed. **Everyone who adds an employer saves everyone else finding it.** It is the only
file here that is the same for everybody.

**And because endpoints die quietly:**

```bash
python3 tools/registry_check.py
```

**Every entry, called.** It fails on an endpoint that has gone empty, and **asks you to look** when a known
requisition has vanished — because it cannot tell a moved endpoint from a filled vacancy and does not
pretend to.

### Check the sources actually work — before you invest in any of them

```bash
python3 tools/radar/sources_check.py
```

**This exists because of a wasted hour.** Someone got an API key for a job board, wired it up, and only
then discovered the board does not cover their country at all — it returned "not found" there while
serving four other countries perfectly well. The hour went on debugging a key that was never broken.

So the check asks each source one question — *would you work, for this config, right now* — and it is
careful about two answers that look the same and mean opposite things. **"Not configured" is not
"broken"**: most of these sources watch employers you name, so an empty list means nobody is being
watched, which is a fact about your setup rather than a fault. And **"does not cover your country" is not
"your key is wrong"** — which cannot be told apart from a single request, so where it matters the check
also asks about a country the source is known to serve, and compares.

It runs no searches and reads no results, so it costs a request or two per source. It will tell you a
source answers; it cannot tell you it has *good* coverage where you live. That part is a judgement.

### Employers you want watched, and employers you do not

Copy `templates/settings/employers.example.json` to `vault/settings/employers.json` — it is optional, and without it nothing changes.

**Two lists doing different jobs.** The **watch** list gives you complete coverage of an employer rather
than whatever they choose to syndicate to job boards; you name the employer and give it whichever route
reaches them, and if there is no route the run tells you they are not being watched rather than quietly
implying they are. The **avoid** list filters before anything is scored, so an employer you ruled out
months ago costs nothing — and it works at division level too, because a company you would happily join
can contain a part of it you would not.

**Two smaller distinctions that turn out to matter.** An exclusion carries a *reason* and a *basis* —
"their published policy says so" and "someone who worked there told me" are both fair reasons and very
different kinds of claim, and the basis is what lets you re-judge it later. And a role you assessed and
turned down is **not** the same as an employer you rule out on principle: the first can come back, so it
marks the row with a dagger instead of hiding it.

🔴 **This file stays on your machine.** It names companies and says why you will not work for them, some
of it second-hand. It is gitignored, it is outside what the oversight export can carry, and the agent is
told never to suggest you repeat any of it. If anyone asks, "it is not the right fit for me" is the whole
answer.

**One thing worth knowing about Workday**, because it is the difference between a source that works and
one that silently misses employers: **host, tenant and site are three separate values and you cannot work
one out from another.** There are two hosting styles — `<tenant>.wd1.myworkdayjobs.com` and the shared
`wd1.myworkdaysite.com` — and all three values are visible in the employer's own careers URL. If a
configured employer returns a `422`, that means the tenant sits on a different shard: try `wd3` or `wd5`
in the host rather than changing anything else. The adapter says so when it happens.

**Oracle Cloud Recruiting needs two values, not three**, and both sit in the careers URL:
`https://<host>/hcmUI/CandidateExperience/en/sites/<site>/jobs`. Take them verbatim — some tenants carry a
region in the host and some do not, so there is no pattern to derive it from.

🟢 **And if an employer's careers site clearly is not Workday, check anyway.** Big employers often put a
different front end over a Workday back end, and the *Apply* links give it away — search the page source
for `myworkdayjobs` or `myworkdaysite`, and the host, tenant and site are all in the link.

---
