> **Part of [Career Wiki](README.md).** What checks the output before it is sent.

# Checking the output

**The disclaimer at the top is the rule: you check everything.** This section is about what the system
does to make that job smaller, and what it deliberately does not claim to do.

Everything that writes here is a language model, **including whichever model would review its own work.**
A model that found a figure plausible enough to write finds it plausible enough to approve. So the checks
are built on the assumption that the writer cannot audit itself, and there are three of them, asking three
different questions.

| | Asks | What it is |
|---|---|---|
| **`verify.py`** | **Is it true?** | Arithmetic and string matching against your wiki. No model, no network |
| **`vault/oversight/`** | **Does it convince?** | A different vendor's model, reading only what a recruiter reads |
| **`--coverage`** | **What did you leave out?** | Your wiki and the job advert, compared against the CV |

---

### 1. The deterministic layer — `verify.py`

**No model is involved.** It reads your wiki, reads the outgoing document, and proves four things:

| Finding | What it means |
|---|---|
| 🔴 **UNSOURCED** | A figure appears in the CV and **nowhere in your wiki**. Treat it as invented until you prove otherwise |
| 🔴 **ATTRIBUTION** | A real figure is sitting on the **wrong employer**. Every sentence is true and the document still misleads. This is the error that survives every kind of review, because nothing in it reads as false |
| **UNVERIFIED** | The figure is in your wiki, but you have never confirmed it |
| **STALE** | It traces to a page whose review date has passed |

**It refuses to guess.** Attribution is read from an explicit field, never inferred from nearby text —
inference was built, tested, and produced confident nonsense, so when the data is missing the check
**reports itself as skipped** rather than quietly passing. **Read the SKIPPED lines**: a clean run with two
checks disabled means very little.

**You never run it.** A hook fires on every write or edit of a CV or cover letter, and the findings go
straight to the agent, which fixes them and triggers the check again. One rule governs the fixing, and it
matters: **an UNSOURCED figure is never resolved by adding it to the wiki.** That would launder an
invention into a source, and every future application would then treat it as evidence. It comes out of the
document, or you confirm it.

### 2. The oversight layer — a second opinion from a different AI

**Why a different one:** the point is not that another model is better. It is that its mistakes are not
*the same* mistakes. Two passes from the same model share the same blind spots.

#### How to use it

There is a folder called **`oversight`**. Open it in Gemini, ChatGPT or anything else, and say:

> **"Read OVERSIGHT.md and follow it. Review Acme R-12345."**

That is the whole procedure. The folder rebuilds itself every time a document changes, so it is never out
of date, and it contains one subfolder per application:

```
oversight/
    OVERSIGHT.md          <- the reviewer's instructions
    Acme R-12345/         posting, CV, cover letter, REVIEW-ID
    Globex R-4471/        posting, CV, cover letter, REVIEW-ID
```

#### What it gives you

Not a proofread. A structured, adversarial read in a fixed order: **fatal problems** that get an
application binned unread, **unsupported claims** with the follow-up question an interviewer would ask,
**generic lines** that would read identically on someone else's CV, **mismatches** between what the advert
asks for and what your documents lead on, **passages that read as machine-written**, and finally **the
strongest objection a hiring manager could make.** It ends with one line: `SEND`, `FIX FIRST` or
`DO NOT SEND`.

It is told not to rewrite anything, not to open with encouragement, and not to comment on whether claims
are *believable* — that is the deterministic layer's job and it is a different question from whether they
are *specific*.

#### Two rules, and neither is fussiness

> 🔴 **Open `oversight`. Never open your wiki.**
>
> Your wiki holds your salary floor, why you are leaving, and things you have said about colleagues.
> `oversight` holds only what the employer is going to receive anyway — so showing it to another company's
> AI costs you nothing at all.
>
> The brief also tells the reviewer to stay out of everything else, but **telling a model not to read
> something is not the same as it being unable to**, which is why the folder exists separately in the
> first place.

> 🔴 **Start a new chat for every review — including after you fix something.**
>
> Suppose it says a bullet is vague, you fix it, and you ask the same chat again. **It now knows what that
> bullet was meant to say, so the new version reads clearly to it — because it is completing the sentence
> from memory.** It approves something a recruiter would reject.
>
> **Its entire value is that it knows nothing about you.** Every turn of conversation spends some of that,
> which is why it also refuses explanations: *"that number is real, it's from the X project"* is context
> the recruiter will never have.

#### When it goes wrong, you are told

**No model can clear its own memory or start a new chat** — those are things only you can do. So instead
the system makes the failure visible.

Every folder carries a **`REVIEW-ID`**, a fingerprint of exactly those documents that changes the instant
any of them does. The reviewer must open its review with that line. Which means:

- **If it has already reviewed in that chat**, it finds its own earlier ID and refuses, instead of quietly
  doing a worse job.
- **If you edit anything afterwards**, hand the review back here and it gets filed — then the next time
  you touch that CV you are told by name: *your oversight review for this application was of the previous
  version, and its verdict no longer applies.*

**That second one is the failure most worth catching, because it is the comfortable one.** A genuine
verdict, from a real review, of a document you have since changed. **A pass you believe you have is more
dangerous than no pass**, because you will act on it.

### 3. Coverage — what you left out

`verify.py --coverage --posting` reads three things — your CV, your wiki and the job advert — and reports
the achievements **this employer's own language points at** that your CV does not carry.

**Most omissions are correct.** A two-page CV cannot hold everything, and it is reported separately from
the findings for that reason. The question it forces is **decision or oversight** — and the second kind is
how the best thing you have ever done stays invisible for years, because no single application happened to
ask for it and nobody ever looked at the set.

It matches words, not meaning: it cannot see that *"shipping cadence"* in an advert and *"release
management"* in your wiki are the same idea. So the agent is told to repeat the exercise itself
afterwards, with comprehension the script does not have. Anything you have marked as permanently excluded
stays excluded and is never raised.

### What none of this does

**It cannot tell you whether the document is good**, whether it is honest about things your wiki never
recorded, or whether you should send it. **A clean run means nothing was provably wrong by the checks that
ran.** Read it yourself. That is not a formality — it is the only step that actually establishes the
document is true.

---
