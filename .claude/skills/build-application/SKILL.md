---
name: build-application
description: Build a bespoke CV, cover letter and ATS field pack for one specific role. Use when the user decides to apply for something.
---

# build-application

One role, one pack. **There is no master CV and there should not be one** — each CV is assembled on demand
from the wiki, which is the persistent raw material. A master CV is a document that is wrong for every
application instead of right for one.

## Step 0 — is the posting still open?

**Check before building anything.** Roles close. Twenty minutes of work on a dead requisition is twenty
minutes gone, and it happens more often than it should.

If a fetch fails, say what failed rather than concluding. **A 403 is not evidence of closure**, and a
careers site that will not render for an automated browser tells you nothing about the role. If you cannot
resolve it, ask the user to check while logged in.

🟢 **If the posting was archived by the radar, re-read it — this is the moment the expensive pass is
for:**

```bash
python3 tools/radar/refresh.py "vault/postings/<Employer> - <Title>.txt"
```

**The radar is bounded to the delta and never re-reads anything**, so the text and the date behind an
assessment are however old the assessment is. Re-reading answers three things at once:

| | |
|---|---|
| **Still readable?** | `GONE` means filled, withdrawn or moved. **Do not build from the archived copy without checking** |
| **Has the description moved?** | A band added, a requirement softened. **A salary appearing is called out by name** — it changes the PAY row and the screening-call question |
| 🔴 **How old is it really?** | **A listing censors the posting date and the detail endpoint does not.** One real posting's listing said *"30+ days"* while its detail said ten days earlier, and **9 of 20 postings from that employer arrived capped.** Age is the best ghost-job signal and the shortlist could not see it |

🟡 **It never updates the archive.** That file is the evidence of what the assessment was based on, and
today's text is a different document — **note what changed on the role page instead.**

## Step 0.4 — research the employer, and the division separately

🔴 **Before writing anything, and before the route decision.** The posting tells you what the employer
says about itself. It does not tell you that they cut 500 roles last year, agreed to buy 1,200 people
three weeks ago, or pay below market — **all of which were true of one employer whose posting mentioned
none of it.**

**Research the company and the division as separate questions.** A group can be in decline while the
division hiring is the growth engine, or the reverse. **Applicants also apply to the same employer more
than once**, so a company page is written once and reused; division findings are per division.

**It must run while it can still change the decision** — which means before the pack, not after. **Skip it
for roles below the build threshold**; the assessment has already rejected those.

**Cover**: financial trend and profitability, revenue by division, whether the core business is
structurally threatened and how they are responding, what the division actually is and how it performs,
acquisitions, restructuring and headcount, leadership changes, employee reviews on management and job
security, the pay signal, and what the local office actually is.

🟢 **Two habits worth having.** **Read the transaction, not the statement** — what a company has done with
money is more reliable than what its CEO says about the market. And **find out what the local office
actually is**; a question about an office is often really a question about an acquisition.

**If the research changes the score, say so and rescore before continuing.**

### 🟢 Two more sections on every company page, because both get asked in every process

**Both are cheap once the research exists, and neither can be written without it.**

**1. "Why do you want to work for X?" — draft three answers, use one.**

🔴 **The constraint is what makes it hard.** They cannot say salary, security or location — usually the
three things actually driving the decision. **So the answer must be specific, checkable, and true of that
employer alone.**

> 🔴 **The test: could this sentence be said about a different company?** If yes, it is flattery, and it is
> what the other forty candidates wrote. *"I admire your commitment to innovation"* is the failure mode.

**What works:** name something **specific and non-obvious from the research** — it proves they looked
without announcing that they looked; **connect it to something they have actually done**, with a number;
**end on what they want from the employer**, not what they admire about them; and **concede something**
where it is true, which is what makes the rest credible.

**Draft three. Keep the other two for the second interviewer asking the same question.**

**2. The employer's values or behaviours, with three examples each.**

**Most large firms publish them, and in a values-led organisation the competency questions come straight
from that list.** Find them, then map **three stories per value from the user's own record.**

🔴 **Three, not one** — the same story cannot be reused across two interviewers, and **the third forces a
search of the wiki rather than reaching for the obvious.**

🔴 **Record them as raw material, not as finished answers.** In the room they need situation, action and
outcome. **The value is what is being scored; the story is what is remembered.**

🟢 **Prefer the awkward examples.** *"I brought the vendor in because my team did not have the expertise"*
is a better collaboration answer than any success story, and *"testing is not my strength"* is a better
one on candour than a testimonial. **Values questions reward candour that costs something.**

## Step 0.5 — how are they applying? Decide the route before writing anything

**The route matters more than the document, and it is decided once, before any work.**

### Is there a warm route in?

🟢 **A referral is the highest-leverage thing available before submitting, and it costs one message.**
Referred candidates are read by a human rather than filtered, and at many employers referrals are a
formal, incentivised programme. **Ask, every time:**

> *"Do you know anyone at this company, or anyone who would know someone? A former colleague, someone in
> your network, an alum of somewhere you worked?"*

If yes, **the sequence changes**: they ask the contact first, and apply through the referral route rather
than the public one. Applying cold and *then* asking for a referral is much weaker — some systems will not
attach a referral to an existing application at all.

**If the answer is no, say so and move on.** Do not turn this into a networking project.

### Agency, or direct?

🔴 **The trap that quietly kills applications: duplicate submission.** If a recruitment agency has already
sent their CV to this employer, a direct application creates two records. Employers routinely reject both
rather than adjudicate a fee dispute, and nobody explains why.

**So ask before applying:**

| Question | If yes |
|---|---|
| Has any agency sent your CV to this employer, for any role, in the last 6-12 months? | **Check with the agency before applying directly** |
| Is this posting itself from an agency? | The employer is often unnamed. **Ask which employer before they submit you** — that is the applicant's call to make, not the agency's |
| Are they working with a recruiter on this? | **Never let an agency send a CV without explicit per-employer permission.** Give it role by role, never as a blanket |

**Record the answer on the role page.** Six weeks later nobody remembers which agency was told what.

### Same employer, more than one role?

Applying for several roles at one employer at the same time reads as unfocused and can weaken all of them.
**Two or three closely related roles is normal; a scattergun across a careers site is not.** If they are
already in a live process there, applying for a second role usually goes through the recruiter they are
already speaking to, not through the front door again.

## Step 1 — read the posting properly, then write it down

🔴 **Fetch the employer's own posting. Never assess from the aggregator's copy.**

**Aggregators truncate, and the truncation is asymmetric** — it removes qualifiers, alternatives and
context, **which are the parts that tend to make a candidate more eligible.** In real use, reading the
employer's own version of a posting that had already been assessed:

| The aggregator carried | The employer actually wrote |
|---|---|
| *"Proficiency in [eight named tools]"* | *"Proficiency in **at least one**..."* — of eleven |
| *"Consulting experience preferred"* | *"...**or internal product delivery, or regulated environments**"* |
| *(absent)* | **The business driver for the role** — the single strongest match in the posting |
| A posting date | **Three weeks later than the real one** |

**Two flagged capability gaps dissolved on one line of the employer's own text.** A system reading
aggregators **systematically under-scores its own user**, invisibly, because the truncated version reads
perfectly coherently.

🟢 **Most large employers expose the posting as JSON**, which is faster and carries fields the rendered
page hides — the real posting date, the requisition number, secondary locations, study level:

| ATS | Endpoint |
|---|---|
| **Workday** | `POST https://<host>/wday/cxs/<tenant>/<site>/jobs` — **two hosting styles**: `<tenant>.wd<N>.myworkdayjobs.com` and the shared `wd<N>.myworkdaysite.com/recruiting/<tenant>/<site>`. **Take host, tenant and site as three inputs.** Detail: `GET /wday/cxs/<tenant>/<site><externalPath>` |
| **Oracle Cloud** | `GET /hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&finder=ById;Id="<jobId>",siteNumber="CX_1"` — **the quotes are required** |
| **Greenhouse** | `GET /v1/boards/<token>/jobs?content=true` |
| **Lever** | `GET /v0/postings/<company>?mode=json` |

🔴 **Trust the employer's posting date over the aggregator's.** Aggregators re-date reposts, so an ageing
requisition looks fresh — **and a six-week-old senior role may already be at offer stage**, which is a
prioritisation input.

Create a role page in `wiki/roles/`. Capture the **requisition number and posting URL** — both are often
only on the employer's own site, and the aggregator listing will vanish.

🔴 **And save the posting text itself to `vault/postings/<Employer>.txt`.** The URL is not enough: postings
are deleted, and **in one real vault five of forty-one had already gone, including the role a pack had been
built for and the role the user was rejected from.** See [[SCHEMA.md]]. **The requisition number is also
what makes an output filename unique.**

Then work out what they are actually anxious about. A job description is a wish list; the role exists
because something is going wrong. Name it, then check what the wiki has against it.

**Score it** on the framework and place it in the table.

🟢 **And count the requirements while the posting is open.** List the employer's named requirements, mark
each **🟢 cleared / 🟡 partial / 🔴 gap**, and put the tally on the role page. **It is the evidence behind
the DELIVER score, it is checkable line by line, and it is the raw material for the cover letter's
concession** — which is the paragraph that has to exist anyway.

🔴 **If the tally lands far from the DELIVER score already given, one of them is wrong. Find out which
before writing anything.**

### 🟢 Cite what answers each one — a tally is a number, a citation is evidence

**Every 🟢 gets the page and the specific claim that answers it. Every 🟡 gets what is there and what is
missing. Every 🔴 gets nothing, and that is the point.**

| Their requirement | | What answers it |
|---|---|---|
| *"8+ years leading engineering teams"* | 🟢 | [[Operating Model]] — six direct reports including managers, function of fifteen |
| *"Managing delivery risks, dependencies, budgets"* | 🟡 | [[Operating Model]] — five of the six. **Budget ownership is a confirmed gap** |
| *"Turn internal products into market-facing IP"* | 🔴 | — |

**Three reasons this is worth the extra column, and the third is the one that pays:**

1. **It makes the tally auditable.** *"Nine of twelve"* is a claim. *"Nine of twelve, and here is which
   page carries each"* is a working.
2. 🔴 **It catches a cleared requirement with nothing behind it.** A requirement marked 🟢 that cannot name
   a page **is not cleared, it is assumed** — and that assumption reaches the CV as a sentence nobody can
   support.
3. 🟢 **It is the interview prep, already written.** Every 🟢 with a citation is a question they may ask and
   the specific answer to it. **The row is the flashcard.**

**Where a citation would be a wiki page carrying no `employer:` field, name the achievement page instead**
— those exist precisely so a figure has an owner, and a citation to a discursive page is a citation to four
employers at once.

## Step 2 — pick the angle

**The angle is the whole job.** Ten CVs built from identical material should open in ten different places.
If two of them open the same way, one is not tailored.

Ask: what is the first bullet of the current role? That single choice is the application's argument.

| If the posting is about | Lead on |
|---|---|
| Scale and portfolio | What they own and how big it is |
| Process and control | Decision rights — what they personally sign off |
| People | Team shape, retention, who they have grown |
| Building | What they made themselves, and what it returned |
| Teaching or enablement | What they can transmit, not what they own |

## Step 2.5 — check what you are about to leave out

```bash
python3 tools/verify.py <a recent CV>.txt --wiki wiki --coverage --posting <this posting>.txt
```

**Run this while choosing the angle, not after writing.** With `--posting` it reads three things — the
document, the wiki and the job spec — and reports **wiki achievements that this employer's own language
points at and the document does not carry.** Without `--posting` it is only a list of everything absent,
which is mostly noise.

🔴 **The script matches words; you match meaning.** It cannot tell that *"shipping cadence"* in the
posting and *"release management"* in the wiki are the same idea. **So read its output, then do the same
pass yourself against the requirements it missed** — you have all three documents and it only has string
matching. Its job is to catch the blunt case, which is common: the posting names something four times, the
wiki has real evidence for it, and the CV never mentions it.

**Most omissions are correct** — the angle decides what belongs, and a CV that included everything would
be a list. But read the verified items in that list once and ask, for each: *was leaving this out a
decision?*

🔴 **The failure this exists to prevent**: strong material sitting in the wiki, never appearing on any CV,
because no single application ever happened to call for it and nobody looked at the set. That is how the
best thing someone has done stays invisible for years.

## Step 3 — write it

🔴 **Read `WRITING.md` in this skill's folder first.** It carries the content rules, the cadence rules
that decide whether a document reads as generated, the banned constructions, and the pre-release
checklist. **Do not draft from memory of it — open it.**

**Ask once, early, whether the user has their own writing standard.** If they do, theirs wins and
`WRITING.md` is the fallback. Keep it in the wiki so it survives the session.

## Step 4 — the cover letter answers the hardest question first

Whatever a sceptical reader would object to, open on it. Do not bury it.

**Conceding a named requirement you fail is often the strongest move available**, especially where the
posting contradicts itself — a "reasonable technical fluency" overview against a hard skills list in the
minimums. Naming the gap forces the hiring manager to decide which role they are recruiting for, which is
the question that decides the application anyway. It is also the only version that survives an interview.

## Step 5 — the ATS pack

**Recruiters search structured fields, not attachment contents.** A form filled in thinly wastes the
application. Produce a paste-ready file, `<Employer> <Req> - ATS Notes.md`, with:

- **Every role as a discrete entry**, including promotions as separate entries — the form has no page
  limit, and two entries show a promotion that one entry hides
- **Description text unwrapped** — one unbroken line per paragraph. Hard line breaks survive a paste and
  look broken
- **The employer's spelling**, and the keyword cluster this specific role screens on
- **Skills tags: only things the user could do today.** A structured tag is an unqualified claim with
  nowhere to put the qualification that would make it true. Governing an estate is not fluency in it
- **An explicit do-not list** of anything the cover letter concedes. A tag contradicting the letter it is
  attached to is worse than an absent tag
- **A pre-submit checklist**, including: re-read every auto-parsed field, and check the current role did
  not merge with a previous one when the CV was parsed

## Step 5.5 — the form's own questions

**Step 5 covers the fields that describe their history. This covers the questions the form asks them**,
which is where applications are lost silently.

### Knockout questions — get these exactly right

🔴 **These are machine-scored and a wrong answer is an automatic rejection no human ever sees.**

Right to work, sponsorship, notice period, willingness to relocate, salary expectation, security
clearance, driving licence, professional registration.

**Take them from `Standing Answers.md`**, which holds the settled versions. Two rules:

- **Answer exactly what is asked.** Sponsorship questions in particular are often phrased so the
  safe-sounding answer is the wrong one. **Read the question twice.**
- **If the phrasing genuinely does not fit their situation**, choose the literally true answer and address
  the nuance in the cover letter. **Never guess, and never soften.**

### Free-text supplementary questions

Many forms ask "why do you want to work here?" or "describe a time when…" in a box with a character limit.
**These are read**, often before the CV, and they are usually answered badly because the applicant has
already spent their effort on the attachment.

- **Do not paste the cover letter in.** It answers a different question and the reader can tell.
- **Respect the character limit**, and check it — some count spaces, some truncate silently mid-word.
- **One concrete example beats three claims.** These boxes are where the stranger test matters most.
- **Draft them in the ATS pack file**, unwrapped and paste-ready, not into the browser where a session
  timeout loses them.

### Voluntary disclosure

Diversity, ethnicity, disability, veteran status. **Genuinely optional, separated from the hiring
decision, and the applicant's business alone.** Note that the section exists so it is not a surprise, and
say nothing about how to answer it.

**One thing worth flagging, once**: if they need an adjustment for the process itself — extra time, a
different format, accessibility at interview — **that is a separate request to the recruiter, not this
section**, and it is normal to make it.

## Step 5.9 — create `application.json` before writing any artefact

**Do this first, or the deterministic layer cannot run on anything you write.** Copy
`templates/application.example.json` into the application folder as `application.json`:

```json
{ "employer": "Acme Corp", "requisition": "R-12345", "posting": "posting.txt",
  "past_employers": ["...", "..."], "do_not_claim": ["react", "graphql"], "spelling": "uk" }
```

**Save the posting as `posting.txt` beside it** — coverage needs it to rank what is missing by what this
employer actually asked for, and the role page needs it anyway.

**Also copy `templates/OVERSIGHT.md` into the folder.** It is the brief an independent reviewer reads,
and it travels with the application so the review can happen in any tool later without reconstructing the
instructions.

**`do_not_claim` is whatever the cover letter concedes.** A CV claiming what the letter concedes is worse
than either document alone.

## Step 6 — produce the actual document

**Write the CV as HTML using `templates/cv.html`**, then have the user print it to PDF from their browser
(Cmd/Ctrl+P → Save as PDF). The template carries print CSS with correct margins and page control.

**This route is deliberate.** It needs nothing installed, works identically on macOS, Windows and Linux,
and gives full typographic control. Generating .docx requires a library and converting it requires an
office suite — both are platform-specific and both fail on someone else's machine.

**If the employer's form demands .docx specifically**, say so and let the user decide: many accept PDF,
and a PDF parses more predictably in an ATS than a .docx built by a library.

Open the HTML yourself to check it before handing it over. **Confirm the page count rather than assuming
it** — a CV that silently runs to three pages is a real failure.

## Step 6.2 — the interview pack, written now rather than the night before

🔴 **The application is not the deliverable. Getting the job is.** A pack that stops at the cover letter
leaves the hardest part to be done under time pressure, from memory, weeks later — **and by then the
reasoning that produced the angle is gone.**

**Write it while the posting is open and the research is fresh. It costs twenty minutes now and hours
later.**

### Four STAR stories, chosen against this employer

**Not a generic set. Pick from the wiki against what this posting actually asks for**, and take the
[REQS tally](#-cite-what-answers-each-one--a-tally-is-a-number-a-citation-is-evidence) as the shortlist —
**every 🟢 with a citation is a question they may ask and the page that answers it.**

| | |
|---|---|
| **Situation** | Enough to make the stakes legible, and no more |
| **Task** | What was actually on them, stated narrowly. **Claiming the whole programme when they owned one part is where these stories fail under a follow-up** |
| **Action** | 🔴 **What *they* did, first person, singular.** *"We"* is the tell that the story belongs to somebody else |
| **Result** | The number, and **where it came from** |
| 🟢 **Reflection** | **What they would do differently.** The half most candidates skip, and the half that separates a rehearsed anecdote from someone who has thought about it |

🟢 **Prefer the awkward ones.** A story that starts with something going wrong and ends with it being fixed
beats a success story, because **interviewers ask for failures and get polished successes, and they notice.**

🔴 **One story per requirement, not one story reused.** If the same incident answers three of their asks,
it will be told three times to three interviewers who compare notes.

### The gap answer, drafted before it is needed

**The 🔴 rows in the REQS tally are what they will probe.** For each one, write the honest answer now:
**what is true, what is not, and what the nearest real thing is.**

🟢 **The shape that works is the one the cover letter already uses**: concede it plainly, name the closest
adjacent experience, and say what would be learned. **An answer improvised in the room becomes a defence;
an answer prepared becomes a position.**

### Questions to ask them, from the research

**Pull them from the role page's own open questions.** They are already written, they are specific to this
employer, and **the ones generated by [employer research](#step-04--research-the-employer-and-the-division-separately)
are the ones that mark out a candidate who did the work.**

🔴 **Order them by what would change the decision**, not by what sounds impressive. **The pay question and
the work-pattern question go first, on the first call**, however uncomfortable — see the standing answers.

### 🟡 The negotiation position, drafted only if the role clears the bar

**Do not write this for every application.** Draft it when the role is one they would actually take —
**the same threshold that governs whether the employer gets researched at all.** Below that it is work
spent on a decision already made.

**When it is drafted, it needs four things from the wiki, not from imagination:**

| | |
|---|---|
| **The floor, and what it is for** | A number tied to an obligation behaves differently from a preference, and **starting salary dominates progression** |
| 🔴 **What leaving costs** | Unvested equity, notice, a vesting date that makes one month expensive and the next one cheap. **This is the number most people discover after accepting** |
| **What is published** | Their band, if there is one. **Ask base, bonus and pension separately** — a single "package" figure hides which part is guaranteed |
| **The order** | Their band before any number of the applicant's. 🔴 **Never volunteer what they are paid now** — in some jurisdictions asking is restricted, and everywhere it anchors the offer to the past rather than to the market |

🔴 **Never invent a competing offer.** It is the most common piece of negotiation advice on the internet
and it is checkable, career-ending, and unnecessary — **a floor with a reason behind it does the same work
and is true.**

## Step 6.5 — hand them the reviewer folder, by name

**The export is built automatically** — the hook refreshes it on every write, so it always exists and is
never stale. **You do not need to run it, and neither does the user.**

🔴 **But you must tell them where it is, in plain words, when you deliver the pack.** Something like:

> *If you want a second opinion from a different AI, open the `oversight` folder — it has all your
> applications in it — and say "read OVERSIGHT.md and follow it. Review \<Employer Requisition\>". Open
> that folder, not your wiki.*

**Name the application in the sentence.** The folder holds every application they have built; the brief
makes the reviewer ask which one if not told, but telling it saves a round trip.

🔴 **And tell them to start a new chat every time** — including after a revision, which is the case people
get wrong. A reviewer that saw the first draft knows what a vague bullet was meant to say and reads the
replacement as clear. **It approves what a recruiter would reject.** The brief makes it refuse, but the
refusal only fires if the model notices; the reliable fix is a fresh conversation.

**Why this sentence matters more than it looks.** A non-technical user who wants a second opinion and has
not been given a path will point the other tool at whatever they can find — which is the application
folder, which sits inside the wiki, one level from their salary floor and their notes about colleagues.
**Naming the safe folder is the whole intervention.** They will not run a script first, and they should
not have to.

## Step 7 — the pre-release check

**Two passes, and they catch different things.** `tools/cv_lint.py` checks how it reads — characters,
vocabulary, cadence. `tools/verify.py` checks whether it is *true*.

🔴 **`verify.py` runs automatically on every write** via the hook, and its findings land in your context
whether you asked for them or not. **Fix them by the rules in `SCHEMA.md`, and after three failed rounds
stop and ask the user rather than continuing to satisfy the checker.** `cv_lint.py` is the one you have to
remember to run.


**Two passes, and they catch different things.**

**Mechanical first:**

```bash
pdftotext -layout "cv.pdf" - | python3 tools/cv_lint.py -
```

🔴 **Run it on the cover letter too, not just the CV:**

```bash
pdftotext -layout "cover letter.pdf" - | python3 tools/cv_lint.py -
```

**This step used to lint the CV alone**, which is how seven CVs shipped carrying twenty-five third-person
pronouns. The letters happened to be clean; nothing was checking them.

That checks characters, banned vocabulary, participial tails, round-number tells, US spelling, bullet
cadence and **third person**, and it exits non-zero if anything is flagged. **Run it against the extracted PDF text, not the
source** — that is approximately what an applicant tracking system receives, and if the name is missing or
the dates have vanished, fix the source file before sending anything.

**Then judgement**, using Part 3 of `WRITING.md` — the audit prompt. **Run it in a fresh session.** A model
that just wrote the copy will defend it. It covers the things no script can check: the swap test, the
stranger test, the interview test, and whether every number sits on the right role.

Then file a **Deliverables** table on the role page linking every file, update `log.md`, and hand them
over. **Deliverables get no frontmatter and are not listed in `index.md`** — they are point-in-time
artefacts, not knowledge.
