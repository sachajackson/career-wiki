> **Part of [Career Wiki](../README.md).** What it cannot do, and what it will not do.

> # ⚠️ Read this before you use anything here
>
> **This system is built on large language models. They produce fluent, confident, plausible text, and
> some of it will be wrong.** That is not a defect awaiting a fix — it is how the technology works. A
> model can invent a number, attach a real achievement to the wrong job, misread a date, misstate a
> qualification, or write a sentence you cannot support, and it will do all of that in the same assured
> tone as everything it gets right.
>
> ### You must read and verify every single output, in full, before it leaves your hands
>
> **Every CV, cover letter, profile, form answer and assessment this produces is a draft for you to
> check.** Not a finished document. Read it line by line against what you actually know to be true:
> dates, job titles, employers, figures, technologies, qualifications, and which role each achievement
> belongs to. **If you cannot personally stand over a sentence in an interview, take it out.**
>
> ### You are solely responsible for what you submit
>
> **The person whose name is on the application is accountable for its contents.** Not this software, not
> its authors, not the model provider. If something inaccurate reaches an employer, that is your
> submission and your consequence.
>
> **Those consequences are real.** An unsupportable claim can lose you an application, an offer, or a job
> after you have started. In many places a material misstatement in a job application is grounds for
> summary dismissal, and depending on the claim and the jurisdiction it can amount to fraud or
> misrepresentation with legal consequences beyond employment. **Answers about right to work, visa status,
> sponsorship, qualifications and professional registration are legally significant. Verify them
> yourself.**
>
> ### The checks in this repo reduce risk. They do not remove it
>
> There is a deterministic verifier, a lint pass and an independent review layer, and they exist precisely
> because model output cannot be trusted unexamined. **They are not a guarantee.** A clean run means
> *nothing was provably wrong by the checks that ran* — it does not mean the document is accurate, and it
> never means you can skip reading it.
>
> ### No warranty, no liability, no advice
>
> **This software is provided "as is", without warranty of any kind**, express or implied, per the MIT
> licence in `LICENSE`. **The authors and contributors accept no liability for any loss or damage arising
> from its use**, including lost opportunities, withdrawn offers, terminated employment, reputational harm
> or any other consequence, however caused.
>
> **Nothing here is legal, immigration, employment, financial or career advice.** It is not a substitute
> for a solicitor, an employment adviser, an immigration adviser or a qualified professional. If a
> question is genuinely legal — redundancy rights, notice, discrimination, visa eligibility, contractual
> obligations — take it to someone qualified.
>
> **Third parties are outside anyone's control here.** Job boards, applicant tracking systems, employers
> and any other AI vendor you choose to use have their own terms, their own data practices and their own
> behaviour. **Read their terms. Using the optional job-search or review integrations is your decision and
> your responsibility.**
>
> ### Using it means you accept all of the above
>
> **If you are not willing to check the output yourself, do not use this.** An unchecked AI-written CV is
> worse than no CV, because it is confident, specific and wrong in ways you will be asked about out loud.

---

# Honest limits

🔴 **The most important one first: it cannot tell you whether what it wrote is true.** The deterministic
layer proves every figure traces back to your wiki. **Nothing proves your wiki is right.** Only you can do
that, and no amount of checking below substitutes for reading the document before you send it.

- **It cannot update your LinkedIn or Indeed profile.** Those require logging in. It writes the text and
  you paste it.
- **It cannot apply for jobs.** It builds the pack and prepares the form answers. You submit.
- **Salary is usually missing** from listings. Unknown is recorded as unknown, and you are told to ask on
  the first call rather than guess.
- **The search ranking is triage, not judgement.** A keyword tally decides what is worth reading, nothing
  more. Good roles do land low in it, which is why the shortlist gets read rather than trusted.
- **It cannot make anything private from the model.** Claude Code runs locally, but it sends the contents
  of the files it reads to Anthropic's API to answer anything. **Local storage is not concealment** — see
  [`PRIVACY.md`](../PRIVACY.md).
- **It will not invent anything.** No metric, title or achievement you did not provide. Ask it to
  embellish and it will decline and explain why the claim would not survive a follow-up question.
- **It is not a lawyer, a doctor or an HR professional.** Redundancy rights, notice periods and
  discrimination get flagged as questions for a professional.
- 🔴 **It does not know whether a posting is real.** Ghost listings, roles already filled internally and
  agency reposts of the same job all reach the shortlist. Legitimacy signals are *reported*, never scored.

---

## Things it will decline to do

**These are not gaps. They are the reason the output survives an interview.**

| | |
|---|---|
| **Invent a figure, title or achievement** | Nothing reaches a document that you did not provide |
| **Embellish a real one** | Ask, and it will say so plainly and explain why an inflated claim does not survive a follow-up question at senior level |
| **Re-suggest something you excluded** | A page you marked as off the CV stays off it until *you* raise it again |
| **Record an identifiable colleague** | Never, in any form, in a personnel or redundancy context — and never as positioning material |
| **Send a document it has not checked** | `verify.py` and `cv_lint.py` run before release. A clean run means *nothing was provably wrong by the checks that ran* — it is not approval |

---

## Known gaps

**[`BACKLOG.md`](../BACKLOG.md) records what does not work yet, what has gone wrong once, and what was
deliberately not done.** Worth reading before you rely on something: the largest gap is that **the system
stops at the submit button** — interview preparation, offers and negotiation are not covered.
