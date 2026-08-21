#!/usr/bin/env python3
"""review -- independent oversight on a finished application, by a second model.

    python3 tools/review/review.py --posting job.txt --cv cv.txt --letter letter.txt
    python3 tools/review/review.py --posting job.txt --cv cv.txt --provider openai

WHY A SECOND MODEL, AND WHY A DIFFERENT ONE

A model reviewing its own output shares its blind spots. If it found a phrasing
natural enough to write, it will find it natural enough to approve. Cross-model
review is not about one model being better; it is about the failure modes not
being correlated.

WHY IT IS BLIND TO THE WIKI -- THIS IS DELIBERATE

The reviewer sees the posting and the outgoing documents. It never sees the
wiki, and it is never given the applicant's history, salary floor, reasons for
leaving or anything else.

Two reasons, and both matter:

  1. Independence. A reviewer that has read the wiki will judge the CV against
     what it knows to be true, which is exactly the wrong test. The recruiter
     has not read the wiki either. The question is whether the document stands
     up to someone who only has the document.
  2. Data minimisation. This sends text to a third-party API. Sending only what
     a recruiter will receive anyway means a review costs no additional privacy.
     Sending the wiki would be a serious escalation for a marginal gain.

Truth-checking is not this layer's job. tools/verify.py does that
deterministically, against the wiki, without a network call.

CONFIGURE

  cp tools/review/config.example.json tools/review/config.json

and set a key for one provider. config.json is gitignored. No key, no review --
the script says so and exits rather than degrading silently.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PROMPT = """You are reviewing a job application before it is submitted. You did not write it and you \
have no stake in it. Your job is to find what is wrong with it, not to encourage.

You have the job posting and the applicant's documents. You do NOT have their history, and you should \
not ask for it: the recruiter will not have it either. Judge only what is in front of you.

Report, in this order, and omit any section with nothing in it:

1. FATAL. Anything that would get this rejected without a reply. Wrong employer named. A stated minimum \
requirement contradicted. An unanswerable claim. A formatting choice that will not survive parsing.

2. UNSUPPORTED. Every claim asserting an outcome with no mechanism, scale or constraint attached. For \
each, quote it and say what a sceptical interviewer would ask next. Be exhaustive here; this is the \
section that matters most.

3. GENERIC. Every line that would read identically on someone else's application. Apply this test to each \
bullet: could the company name and job title be swapped and the sentence still work? If yes, it is filler.

4. MISMATCH. What the posting asks for that the documents do not address, and what the documents lead on \
that the posting does not care about. Quote the posting.

5. READS AS MACHINE-WRITTEN. Uniform bullet length or rhythm, participial endings, lists of exactly three, \
vocabulary that clusters in generated text. Quote examples.

6. THE STRONGEST OBJECTION. In one paragraph: if you were the hiring manager and you were going to say no, \
what would the reason be?

Do not rewrite anything. Do not suggest improvements unless asked. Do not comment on what is good. End \
with a single line: VERDICT: SEND / FIX FIRST / DO NOT SEND.

--- JOB POSTING ---
{posting}

--- APPLICANT DOCUMENTS ---
{documents}
"""


def load(path):
    if not path:
        return None
    if not os.path.exists(path):
        sys.exit(f"not found: {path}")
    return open(path, encoding="utf-8").read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posting", required=True, help="the job posting as text")
    ap.add_argument("--cv", required=True)
    ap.add_argument("--letter")
    ap.add_argument("--answers", help="free-text form answers, if any")
    ap.add_argument("--provider", help="override the configured provider")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt and send nothing")
    args = ap.parse_args()

    cfg_path = os.path.join(HERE, "config.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    provider = args.provider or cfg.get("provider")

    docs = [("CURRICULUM VITAE", load(args.cv))]
    if args.letter:
        docs.append(("COVER LETTER", load(args.letter)))
    if args.answers:
        docs.append(("APPLICATION FORM ANSWERS", load(args.answers)))
    prompt = PROMPT.format(
        posting=load(args.posting).strip(),
        documents="\n\n".join(f"### {n}\n{t.strip()}" for n, t in docs))

    if args.dry_run:
        print(prompt)
        return

    if not provider:
        sys.exit("No provider configured. Copy config.example.json to config.json and set one.\n"
                 "Use --dry-run to see the prompt and paste it into any chat interface yourself --\n"
                 "that works just as well and costs nothing.")

    from adapters import ADAPTERS
    if provider not in ADAPTERS:
        sys.exit(f"unknown provider {provider!r}. Available: {', '.join(ADAPTERS)}")
    pcfg = cfg.get(provider, {})
    key = pcfg.get("api_key") or os.environ.get(pcfg.get("api_key_env", ""), "")
    if not key:
        sys.exit(f"No API key for {provider}. Set it in config.json or in "
                 f"${pcfg.get('api_key_env', 'THE_ENV_VAR')}.")

    print(f"reviewing with {provider} / {pcfg.get('model', 'default')}...\n", file=sys.stderr)
    out = ADAPTERS[provider].review(prompt, key, pcfg)
    print(out)
    print("\n" + "-" * 78)
    print("A second model is still probabilistic. It cannot tell you whether a claim is TRUE --\n"
          "only whether it is convincing. Run tools/verify.py for truth, and remember that the\n"
          "verdict above is an opinion from something that has never met you.")


if __name__ == "__main__":
    main()
