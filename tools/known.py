#!/usr/bin/env python3
"""known -- does the wiki already know this, and did it already decide it does not?

    python3 tools/known.py "budget"
    python3 tools/known.py "work pattern" --wiki wiki

WHY THIS EXISTS

Searching for evidence of X and finding nothing returns the same empty result
whether X was never investigated, or was investigated and found not to hold.
Those mean opposite things. One is a question worth asking. The other is a
settled fact, and asking it again wastes the user's time and costs credibility.

In real use this was got wrong three times in a single session:

  "Does he have budget ownership?"   -- resolved six days earlier, with the
                                        words "stop asking" on the page.
  "Your work pattern isn't recorded" -- it was, and had been for three weeks.
  "No outcome has ever been logged"  -- one had, under a different heading.

Every one of those was in the wiki. None was found, because the search looked
for the assertion and the answer was written as a negation.

WHAT IT DOES

Finds every line mentioning the term and sorts them into two piles: lines that
assert something, and lines that carry a resolution or a negation. Then it
gives a three-way verdict instead of a two-way one:

  SETTLED        the wiki records a decision on this. DO NOT ASK. Read the
                 lines -- the answer is one of them, and it may be yes or no.
  PRESENT        the wiki has material. Do not write "not recorded".
  NEGATIVE ONLY  every mention is a negative. Treat as an established absence.
  NOT FOUND      genuinely nothing. Now it is safe to ask, and to file the answer.

The question this answers is not "is it true" -- that needs judgement. It is
"should I ask the user about this", which is decidable, and which is the
question that was got wrong.

WHAT IT CANNOT DO

Judge. It matches words, so it will call a sentence a negation because of where
"never" sits in it. THE VERDICT IS A SUMMARY AND THE LINES ARE THE EVIDENCE --
read them. A tool that is trusted without being read is a worse failure than
the one it replaced.
"""
import argparse, glob, os, re, sys
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import paths  # noqa: E402

# Phrases that mark a line as a settled negative rather than an open question.
# Deliberately broad: a false CONFIRMED ABSENT costs one read of the lines,
# a false NOT FOUND costs the user being asked something they already answered.
RESOLVED = [
    r"stop asking", r"already (answered|resolved|recorded|established)",
    r"confirmed absent", r"resolved[: ]", r"\bsettled\b", r"asked and answered",
]
NEGATIVE = [
    r"\bnever\b", r"\bnone\b", r"\bno evidence\b", r"\bnot recorded\b",
    r"does not\b", r"do not\b", r"did not\b", r"has not\b", r"have not\b",
    r"\bcannot\b", r"\bwithout\b", r"\babsent\b", r"\bgap\b", r"\bunevidenced\b",
    r"\bnot? (a )?(budget|evidence|experience)\b",
]
STRIKETHROUGH = re.compile(r"~~.*?~~")
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def stems(term):
    """'work pattern' also matches 'work patterns'. Crude and deliberate."""
    t = term.strip().lower()
    out = {t}
    if not t.endswith("s"):
        out.add(t + "s")
    elif len(t) > 3:
        out.add(t[:-1])
    return out


def classify(line):
    low = line.lower()
    if any(re.search(p, low) for p in RESOLVED):
        return "resolved"
    if STRIKETHROUGH.search(line):
        return "resolved"          # struck through means dealt with
    if any(re.search(p, low) for p in NEGATIVE):
        return "negative"
    return "assertion"


def search(wiki, term):
    hits = {"resolved": [], "negative": [], "assertion": []}
    pats = stems(term)
    for path in sorted(glob.glob(os.path.join(wiki, "**", "*.md"), recursive=True)):
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except Exception:
            continue
        body = FRONTMATTER.sub("", text)
        for n, line in enumerate(body.splitlines(), 1):
            low = line.lower()
            if any(p in low for p in pats):
                rel = os.path.relpath(path, wiki)
                hits[classify(line)].append((rel, n, line.strip()))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("term", help="what you are about to assert is missing, or ask the user about")
    ap.add_argument("--wiki", default=paths.WIKI)
    ap.add_argument("--all", action="store_true", help="print every matching line, not a sample")
    args = ap.parse_args()
    if not os.path.isdir(args.wiki):
        sys.exit(f"known: no wiki at {args.wiki}")

    h = search(args.wiki, args.term)
    settled = h["resolved"] + h["negative"]

    if h["resolved"]:
        verdict, advice = "SETTLED", (
            "The wiki records a decision on this. DO NOT ASK THE USER.\n"
            "  Read the RESOLVED lines below -- the answer is one of them, and it may be yes or no.\n"
            "  Cite it. Do not re-open a question the wiki has closed.")
    elif h["negative"] and not h["assertion"]:
        verdict, advice = "NEGATIVE ONLY", (
            "Every mention is a negative. Treat this as an established absence, not an open question.\n"
            "  It is a scored input. Read the lines before writing anything about it.")
    elif h["assertion"] or h["negative"]:
        verdict, advice = "PRESENT", (
            "The wiki has material on this. Use it. DO NOT WRITE 'not recorded'.\n"
            "  If some mentions are negative, the fact is qualified rather than simple -- read both.")
    else:
        verdict, advice = "NOT FOUND", (
            "Nothing at all. It is now safe to ask the user -- and to file the answer when it comes.")

    print(f"known: {args.term!r} -> {verdict}")
    print(f"  {advice}\n")
    print(f"  {len(h['resolved'])} resolved, {len(h['negative'])} negative, "
          f"{len(h['assertion'])} assertion(s)\n")

    for label, rows in (("RESOLVED", h["resolved"]), ("NEGATIVE", h["negative"]),
                        ("ASSERTION", h["assertion"])):
        if not rows:
            continue
        shown = rows if args.all else rows[:6]
        print(f"  {label}")
        for rel, n, line in shown:
            print(f"    {rel}:{n}  {line[:150]}")
        if len(rows) > len(shown):
            print(f"    ... and {len(rows) - len(shown)} more (--all)")
        print()

    print("  The verdict is a summary. THE LINES ARE THE EVIDENCE -- read them before acting.")
    sys.exit(0)


if __name__ == "__main__":
    main()
