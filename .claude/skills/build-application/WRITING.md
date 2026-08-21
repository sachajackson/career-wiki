# Writing standard

**Read this before drafting any CV, cover letter or profile. Do not work from memory of it.**

Written for a single-column, ATS-safe CV. The spelling and legal conventions below are an **Ireland/UK
profile** — see [Localising this](#localising-this) before using it elsewhere.

> **If the user has their own writing standard, theirs wins.** Ask early, keep it in the wiki, and treat
> this as the fallback.

Four parts:

1. **The prompt.** The standard itself, written as instructions.
2. **The rulebook.** The same standard with the reasoning, so it can be applied by hand when editing.
3. **The audit pass.** A second prompt that reviews finished copy against the rulebook. **Run it in a
   fresh session** — a model that just wrote the copy will defend it.
4. **Cover letters and application forms**, which the first three parts do not cover.

`tools/cv_lint.py` in this repo checks mechanically everything that can be checked mechanically. Run it
before the audit pass, not instead of it.

---

## Part 1: The prompt

Paste everything between the rules. Replace the bracketed input at the bottom.

---

You are helping me write CV copy. You are not a marketing writer and you are not producing content. You are converting facts I give you into plain, evidence-led lines that read as though I typed them myself.

### Your single hardest constraint

**Never invent a fact, a number, a tool, a job title, a date, or an outcome.** If a bullet needs a figure I have not given you, write the bullet with a placeholder in this exact form:

`[NEED: what proportion of releases this covered]`

Placeholders are the correct output. A fabricated metric is the worst possible output, because I have to defend every line of this document out loud in an interview. When in doubt, ask me rather than filling the gap.

### Character-level bans (absolute)

Use ASCII only, apart from the euro sign and any accented characters in proper nouns. Specifically, never emit:

- The em dash `—` (U+2014). Not once. Rewrite the sentence with a full stop, a colon, a comma, or brackets.
- The en dash `–` (U+2013), including in date ranges. Use a plain hyphen `-` or the word "to".
- Curly quotes `' ' " "` (U+2018, U+2019, U+201C, U+201D). Use straight `'` and `"`.
- The ellipsis character `…` (U+2026). Use three full stops if you genuinely need one, which on a CV you do not.
- Non-breaking space (U+00A0), zero-width space (U+200B), thin space (U+2009), narrow no-break space (U+202F), or any other exotic space. Plain U+0020 only.
- Decorative bullet glyphs (`▪ ‣ ◦ ●`), arrows (`→`), emoji, or icons. One bullet character throughout: `-`.
- Markdown emphasis markers (`**`, `*`, `_`) inside CV body text.

### Banned vocabulary

These words are the current signature of machine-written applications. They are flagged on sight by recruiters reading two hundred applications a week. Do not use them, and do not use close variants:

`spearheaded, leveraged, leverage, delve, delved, pivotal, intricate, intricacies, showcasing, showcased, realm, robust (of anything except an engineering system where it is the literal technical term), underscore, underscored, meticulous, meticulously, synergy, synergies, seamless, seamlessly, cutting-edge, best-in-class, world-class, tapestry, testament, foster, fostering, navigate (metaphorically), landscape (metaphorically), elevate, resonate, paramount, commendable, unwavering, holistic, myriad, plethora, streamlined (unless I used it), instrumental, orchestrated, championed, results-driven, detail-oriented, self-starter, go-getter, team player, passionate, dynamic, proven track record, hit the ground running, wearing many hats, transformative, game-changing, innovative, groundbreaking, empowered, enabled (as a verb of last resort), drove (metaphorically), spearhead, thought leadership, value-add, mission-critical (unless literally true and I said so)`

Preferred replacements are plain verbs that describe what physically happened: `built, wrote, rebuilt, migrated, cut, shipped, fixed, ran, set up, replaced, automated, negotiated, trained, taught, hired, tested, measured, moved, merged, split, deleted`.

### Banned sentence shapes

- **"Not just X, but Y."** Also "It's not X, it's Y." Never.
- **Rule of three.** Do not write lists of exactly three items unless there are exactly three things and no more. Two and four are normal in real life.
- **The participial tail.** Never end a bullet with `, resulting in X`, `, driving Y`, `, enabling Z`, `, leading to W`, `, allowing for V`. This is the single most recognisable AI bullet shape. Put the result first, or make it a second clause with a real verb.
- **Uniform bullet grammar.** Do not make every bullet start with a past-tense verb in the same slot with the same rhythm. Some bullets should open with the outcome, some with the constraint, some with the system name.
- **Uniform bullet length.** Vary deliberately. A CV where every bullet is 18 to 24 words reads as generated. Aim for a spread: some bullets 8 words, some 25. Never more than two lines on the page.
- **Colon-summary headers.** No `Project Alpha: A Case Study in Delivery`.
- **Hedged abstraction.** No `helped to`, `worked on`, `was involved in`, `contributed to`, `responsible for`. Say what I did.

### Evidence rules

Every bullet must pass all three:

1. **The swap test.** If you could replace the company name and job title and the bullet still reads fine, it is generic. Rewrite it with something only this job contained: a system name, a tool, a constraint, a volume, a deadline, a specific failure.
2. **The stranger test.** Every bullet needs at least one noun or number a stranger could not have guessed. `Improved reporting efficiency` fails. `Replaced the weekly Excel export with a Python job on cron, so the Monday report landed by 07:00 instead of mid-afternoon` passes.
3. **The interview test.** If I could not talk about this line for ninety seconds unprompted, it does not go on the CV. Flag any line you suspect fails this.

### Numbers

- Use the real number I gave you. Never round to a marketing figure.
- Odd, specific numbers read as true because they usually are. `37%` reads real. `40%` reads generated. If my real number is genuinely 40, keep 40, but never invent a round one.
- Prefer before-and-after pairs over percentages: `from 11 days to 4` beats `reduced by 64%`.
- Give scale when it is the point: number of users, size of team, transaction volume, budget, uptime.
- Currency in euro unless the role was elsewhere. No dollar signs on an Irish CV by default.
- If I have not given you a number, write `[NEED: ...]`. Do not estimate.

### Voice and register

- First person implied, pronoun dropped. `Built the pipeline`, not `I built the pipeline` and not `Responsible for building`.
- Past tense for past roles, present tense for the current role. Be consistent within each role.
- Plain, slightly flat, unimpressed by itself. Think handover note, not press release.
- Assume the reader is a busy specialist who will be annoyed by adjectives.
- Include a constraint or a difficulty where it is honest to do so. Real work has friction. Copy with no friction in it reads as invented. `Migrated to Postgres over three weekends because we could not take the downtime midweek` is more convincing than any adjective.
- No summary sentence that describes me as a type of person. The profile section states what I do, what I have worked on, and what I am looking for. Nothing about my character.

### Spelling and local conventions (Ireland/UK profile)

- Irish/British spelling throughout: `organised, analysed, prioritised, optimised, recognised, programme` (for a scheme, `program` for software), `centre, licence` (noun) / `license` (verb), `defence, catalogue, modelling, travelling, enrolment`.
- Never `-ize` endings, never `color`, `center`, `analyze`, `math`, `fall` for autumn.
- Dates as `Mar 2024 - Present` or `March 2024 to June 2025`. Never `03/04/24` (ambiguous across IE and US readers).
- Document is a **CV**, not a resume. Two pages. Third page only for academic or very senior roles.
- No photo, no date of birth, no marital status, no nationality, no PPS number, no age. The Employment Equality Acts 1998-2015 make these unnecessary and Irish employers do not expect them.
- Right to work: one line only, and only if it is not obvious. `Irish citizen` or `Stamp 4, no sponsorship required`.
- No referee contact details on the document. `References available on request` remains standard here.

### Formatting constraints (these come from the parser, not from taste)

The CV will be parsed by Workday, Greenhouse, Lever, iCIMS or similar before a human sees it. Being "human" must not mean being creative here:

- Single column. No tables, no text boxes, no sidebars, no floating frames.
- Nothing in the Word header or footer zone. Contact details go in the document body.
- Standard section headings only: `Profile`, `Skills`, `Experience`, `Education`, `Certifications`. No `My Journey`, no `What I Bring`.
- Reverse chronological.
- One system font: Arial, Calibri, Helvetica, Georgia or Garamond. 10 to 11 point.
- Export as a text-selectable PDF, or DOCX if the posting asks. Never an image PDF, never a Canva export with embedded graphics.
- Each role: job title, company, location, dates, then three to five bullets.

### Output format

Return the CV copy in plain text, section by section. Then, separately, return:

1. A list of every `[NEED: ...]` placeholder, so I can fill them.
2. Any line you think fails the interview test.
3. Anything you were tempted to write but could not because I had not given you the fact.

Do not add commentary, encouragement, or a summary of what you did.

### My input

**Target role and company:**
[paste the job posting, or the parts of it that matter]

**Raw material:**
[dump everything. Job titles, dates, tools, systems, numbers, incidents, things that went wrong, things you fixed, team sizes, volumes. Bad prose is fine. Fragments are fine. This is the only source of truth you have.]

**What I want written:**
[e.g. the Experience section for role X, or the Profile paragraph, or all of it]

---

## Part 2: The rulebook, and why each rule is there

### The thing most advice gets wrong

The em dash is the most-discussed AI tell and the least valuable one to fix on its own. Removing it changes an automated detector's score by a few points at most, because those tools weigh dozens of features and punctuation is a small contributor. What actually gets an application binned is not detected AI, it is **generic content**. A 2025 Resume Now survey found 62% of hiring managers reject AI-generated CVs that lack personalisation, while roughly 80% of recruiters say they would not reject an application simply for having been AI-assisted. The rejection trigger is emptiness, not authorship.

That said, remove the em dash anyway. It costs nothing, and the audience for a CV is a human skimming for eight seconds, not a detector. Perception is the entire game at that stage. The point is that typographic hygiene is the floor, not the ceiling.

So the guidelines above operate on three independent layers:

| Layer | What it fixes | Effort | Actual weight |
|---|---|---|---|
| Typographic | Visible artifacts: em dashes, curly quotes, exotic spaces | 5 minutes, mechanical | Low on detectors, high on human perception |
| Structural | Bullet rhythm, sentence shape, vocabulary | 30 minutes, judgement | High, and durable |
| Evidential | Specificity, numbers, constraints, named systems | Hours, and needs real recall | Decisive |

Most people spend all their effort on layer 1 and none on layer 3. That is backwards.

### The bad advice you will find everywhere, and should ignore

Search results on this topic are dominated by sites selling "humanizers". Their standard recommendation is to introduce deliberate imperfections: vary punctuation randomly, mix straight and curly quotes, add minor errors so the text has human "noise".

**Do not do this on a CV.** Typos and inconsistent punctuation are a documented rejection trigger in their own right, and inconsistent quote characters look like a botched copy-paste, which is exactly the impression you are trying to avoid. Human-ness on a CV comes from content specificity, not from manufactured sloppiness. The consistency of your punctuation is not what marks you as a machine. The interchangeability of your bullets is.

### Why the vocabulary list will decay

The banned words come from real corpus research, not folklore. Analyses of PubMed abstracts found `delve` up roughly 25-fold and `showcasing` around 9-fold after 2022, with an estimated 10% or more of 2024 abstracts showing LLM style markers. Separate work identified `pivotal, intricate, showcasing, realm` as the strongest LLM-preferred style words, and traced the effect to preference training rather than to the base models.

But there is a catch worth knowing. A 2025 arXiv study on human-LLM coevolution found that `delve` frequency **dropped sharply** in arXiv abstracts shortly after it became a public meme, while other ChatGPT-favoured words like `significant` kept climbing. Authors adapted. Models were prompted around it. Detection got harder.

The practical consequence: **a banned-word list has a shelf life of roughly a year.** Date it, and expect to refresh it. The structural rules (bullet rhythm, participial tails, the rule of three, evidential emptiness) have survived four model generations and will outlive the word list. Weight them accordingly.

### The round-number tell

This one is underrated and easy to exploit. Language models generate metrics that cluster on round values: 20%, 25%, 30%, 40%, 50%. Real operational numbers rarely land there. If your CV reads `reduced processing time by 30%` and `improved accuracy by 25%` and `cut costs by 40%`, a recruiter who reads metrics for a living gets an uneasy feeling long before they can articulate why.

Where you have the real figure, use it exactly. Where you have a before-and-after pair, use the pair instead of the percentage: `from 11 days to 4` carries the same information, is harder to fake, and invites a follow-up question you can answer.

### The participial tail

If you fix one structural habit, fix this one. The shape is:

> Implemented a new reporting framework across three business units, resulting in a 30% reduction in manual effort and improved stakeholder visibility.

Verb, object, scope, comma, present participle, outcome, and an `and` clause to round it off. Every model produces this shape by default, and it appears at a density in AI CVs that it never reaches in human ones. Two rewrites that break it:

> Cut the monthly reporting cycle from four days to one. Built the replacement in Python against the existing Oracle views, so nobody had to change their process.

> Three business units were still hand-keying the month-end pack. I automated it. [NEED: how many hours a month that saved]

Note that both are less elegant than the original. That is the point.

### Bullet length variance

Detection research converges on cadence uniformity as the most durable machine signal: sentence after sentence in the 18 to 24 word band, paragraph after paragraph. On a CV this shows up as a wall of bullets that are all exactly one and a half lines long.

Deliberately vary. A short bullet after three long ones does real work on the page as well, because it draws the eye during an eight second scan. Use that.

### What "human" cannot mean

There is genuine tension between reading as human and parsing correctly. Roughly 30% of ATS parsers fail on common layouts, and formatting problems account for around a quarter of parse failures. The parser wants: single column, standard headings, `Month YYYY` dates, nothing in headers or footers, no tables, text-selectable PDF. Greenhouse in particular is strict on date format and will often fail to extract `January 2023 to March 2025` while parsing `Jan 2023 - Mar 2025` cleanly.

So the personality goes in the sentences, never in the structure. A creatively titled section, a two-column layout, or a skills bar chart is not human, it is invisible.

### Checking what the machine actually sees

If you have Python or poppler-utils available, the fastest sanity check there is:

```bash
pdftotext -layout cv.pdf - | less
```

That is approximately what the parser receives. If your name is missing, if the columns interleave, if the dates have vanished, fix the source file before you send anything. Most people never do this, which is why they never find out why they got no callbacks.

Run `python3 tools/cv_lint.py cv.txt` on the same output to catch the character-level, vocabulary and cadence problems mechanically.

### The honest bit about risk

The failure mode that actually costs people jobs is not stylistic. Greenhouse's 2026 research found 91% of recruiters have encountered AI-assisted candidate deception, and the mechanism by which people get caught is almost always the same: a polished document making claims the candidate cannot substantiate in conversation. Every fabricated metric is a landmine you have to step around for forty-five minutes with someone whose job is to find it.

This is why the prompt in Part 1 forbids invention absolutely and emits placeholders instead. It is the difference between a tool that writes your CV and a tool that formats your evidence. Only the second one is safe.

Related, and worth stating plainly: the trick of hiding white text or prompt injections in a CV to manipulate AI screeners is now something recruiters actively check for, and being caught at it is disqualifying in a way that ordinary AI assistance is not. Do not.

---

## Part 3: The audit prompt

Run this in a **fresh chat** with no prior context. Fresh context matters, because a model that just wrote the copy will defend it.

---

You are auditing CV copy for signs that it was machine-written. You are not improving it and you are not being encouraging. Report only problems.

Check the text below and report, in this order:

**1. Character violations.** List every occurrence with its line, of: em dash (U+2014), en dash (U+2013), curly quotes (U+2018, U+2019, U+201C, U+201D), ellipsis character (U+2026), non-breaking space (U+00A0), zero-width space (U+200B), any decorative bullet glyph, any emoji.

**2. Banned vocabulary.** Any of: spearheaded, leveraged, delve, pivotal, intricate, showcasing, realm, underscore, meticulous, synergy, seamless, cutting-edge, tapestry, testament, foster, navigate (metaphorical), landscape (metaphorical), elevate, resonate, paramount, holistic, myriad, plethora, results-driven, detail-oriented, self-starter, team player, passionate, dynamic, proven track record, innovative, transformative, robust (non-technical use).

**3. Structural tells.** Flag each instance:
- "Not just X, but Y" or "It's not X, it's Y"
- Any list of exactly three items
- Any bullet ending in a participial tail (`, resulting in`, `, driving`, `, enabling`, `, leading to`, `, allowing`)
- Bullets where more than 60% start with the same grammatical pattern
- Bullet word-count spread: report min, max, mean, and standard deviation. If SD is under 4, flag it as uniform.

**4. Round-number tells.** List every percentage or metric ending in 0 or 5. For each, note that a real figure would be more convincing.

**5. Swap test failures.** For each bullet, state whether it would still read correctly with a different company and job title substituted. Any bullet that would is generic. List them.

**6. Stranger test failures.** List every bullet containing no proper noun, no tool name, no system name and no number.

**7. Spelling register.** Flag any US spelling (`-ize`, `color`, `center`, `analyze`, `organization` where `organisation` is meant).

**8. Unsupported claims.** List any statement that asserts an outcome with no mechanism attached, e.g. "improved team efficiency". These are the lines that fail in interview.

End with a single number: bullets flagged out of bullets total. No summary, no praise, no suggestions unless I ask.

**Text to audit:**
[paste]

---

## Quick reference card

Pin this to the wall.

**Never:** em dash, en dash, curly quotes, ellipsis character, exotic spaces, emoji, decorative bullets.

**Never:** spearheaded, leveraged, delve, pivotal, intricate, showcasing, realm, synergy, seamless, cutting-edge, results-driven, passionate, dynamic, proven track record.

**Never:** "not just X but Y", lists of exactly three, `, resulting in X` bullet endings, every bullet the same length.

**Always:** one unguessable noun or number per bullet, real figures rather than round ones, before-and-after pairs rather than percentages, Irish spelling, `Mar 2024 - Present` date format, single column, standard headings.

**Test:** could a stranger have written this bullet about someone else? Could you talk about it for ninety seconds?

**Before sending:** `pdftotext -layout cv.pdf -` and read what comes out.

---

---

## Part 4: Cover letters and application forms

The three parts above are about CV copy. Two other documents get written for every application and neither
follows the same rules.

### Cover letters

- **One page. Four or five paragraphs.** Never longer.
- **Open on the hardest objection, not on enthusiasm.** Whatever a sceptical reader would ask first,
  answer it in the first paragraph. Never open with "I am writing to apply for" — they know.
- **Conceding a requirement you fail is often the strongest move available**, particularly where a posting
  contradicts itself. It forces the hiring manager to decide which version of the role they are recruiting
  for, and it is the only version that survives an interview.
- **One quantified proof per paragraph at most.** A letter that is a list of numbers is a second CV.
- **Close on the work, not on availability.** "I would be glad to talk about the role" is enough.
- The character bans, banned vocabulary and banned sentence shapes above all still apply.

### Application forms

**Recruiters search structured fields, not attachment contents.** A form filled in thinly wastes the
application no matter how good the CV is.

- **Every role as a discrete entry**, including promotions as separate entries. The form has no page
  limit, and two entries show a promotion that one entry hides. Unpack any grouped "earlier career" block.
- **Description text unwrapped: one unbroken line per paragraph.** Hard line breaks survive a paste and
  look broken.
- **Use the employer's vocabulary** for the same artefact. If they call it a competency matrix and your
  wiki calls it a capability matrix, write theirs. It is what gets searched.
- **Skills tags: only what could be done today.** A tag is an unqualified claim with nowhere to put the
  qualification that would make it true. Governing a technology estate is not fluency in it.
- **Keep an explicit do-not list** of anything the cover letter concedes. A tag contradicting the letter it
  is attached to is worse than an absent tag.
- **After the CV is parsed, re-read every field.** Parsers merge consecutive roles at the same employer,
  which silently claims a current job title held years longer than it was.

---

## Localising this

Three sections above are Ireland/UK specific and need swapping for another market:

| Section | What changes elsewhere |
|---|---|
| **Spelling and local conventions** | US and Canadian markets use `-ize`, `program` for both senses, `resume` not CV, and one page rather than two below senior level |
| **Photo, DOB, nationality** | Prohibited by convention in Ireland, the UK and the US. **Expected** in much of continental Europe, and normal in parts of Asia and Latin America |
| **Currency and date format** | `Mar 2024 - Present` parses reliably in Greenhouse and is unambiguous across readers. Keep the format even where the currency changes |

**Everything else — the character bans, the vocabulary, the sentence shapes, the evidence rules, the
cadence rules — is market-independent.** Those are the parts that carry the weight.
