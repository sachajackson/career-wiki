#!/usr/bin/env python3
"""Does every line an assessment quotes actually appear in the posting?

    python3 tools/quotes.py                       # every role page with an archived posting
    python3 tools/quotes.py --page "<name>"       # one of them

WHY THIS EXISTS — THE ASYMMETRY IT CLOSES

`verify.py` checks an outgoing CV against the wiki, because a model wrote the CV
and a model reviewing its own work shares its failure modes. That protection stops
at the wiki's edge.

🔴 But the wiki's role pages are ALSO model-written, and they rest on quotation.
Every score in this system is argued from a line lifted out of a posting — *"50%
of capacity to active coding"*, *"managing Architecture teams"*, *"Remote,
Ireland"*. **The score is only as good as the quote, and nothing checked the
quote.**

That matters more than it sounds, because the error propagates: a misquote sets a
score, the score enters the shortlist, the shortlist decides where an evening
goes, and the CV is then written to argue against a requirement that may not
exist. **By the time anybody reads the real posting again, the decision is made.**

WHAT IT COMPARES

The quoted passages on a role page against `vault/postings/<the archived text>`.
It is string matching, not judgement — the same reason `verify.py` is not a model.

🔴 STATUS 2026-08-27: ADVISORY. NOT WIRED INTO `doctor.py` OR `pipeline.py`, and
deliberately so.

Against the live vault it reports 28 of 56 pages as quoting something absent, and
that rate is too high to gate on. It has already been narrowed four times — a
blockquote prefix leaking into every multi-line quote (69/71 failing), fuzzy
filename matching pairing Guidewire's page with Yuno's posting, a URL regex that
found no URLs on the very pages it was written to check, and a similarity ratio
that could not see an elision (49 failing).

🟢 Each narrowing was a real bug in the check, and each was found by running it
rather than reasoning about it. It has also found two genuine faults: a posting
reading "manage i.t. related risks" quoted as "manage IT related risks", and
"Set safe-AI standards FOR AGENTIC SYSTEMS:" quoted with those three words
silently dropped.

🔴 WHAT IS LEFT, and it is why this does not gate anything yet: the remaining 28
are not diagnosed. Some will be genuine, some will be pages quoting an employer's
own posting while only the aggregator's copy was archived, and some will be
postings that changed between archiving and reading. **Until that is separated, a
gate here would fail honest work half the time, and a check that does that gets
switched off.** See `BACKLOG.md`.

🔴 WHAT IT CANNOT DO EVEN WHEN FINISHED, and the limit is real: it proves a sentence was in the
posting. It cannot prove the sentence was READ correctly. "Hands-on experience
with X" quoted accurately and then scored as though it demanded daily coding is a
true quote and a false conclusion, and only a reader catches that.
"""
import argparse
import difflib
import glob
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import paths  # noqa: E402

# A quoted passage: markdown emphasis around straight or curly double quotes.
QUOTED = re.compile(r'[*_]*["“]([^"”]{25,})["”][*_]*')
# 🔴 Fragments shorter than this match by accident. Measured: 25 characters is
# where coincidental matches stop and real quotations start.
MIN_FRAGMENT = 25
# Ellipsis joins two separate parts of a posting into one quotation, so each side
# is checked independently. Writing a quote that way is correct and common.
ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…|\[\.\.\.\])\s*")


def flatten(text):
    """Whitespace, emphasis and smart punctuation removed, for comparison only."""
    text = html.unescape(text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"[*_`]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


# 🔴 A blockquote's "> " prefix leaked into extracted quotations and made every
# multi-line quote fail. Most role pages quote inside a blockquote, so the first
# run reported 69 of 71 pages as misquoting — a check nobody would run twice.
BLOCKQUOTE = re.compile(r"^\s*>\s?", re.M)


def quotations(page_text):
    """Every quoted fragment worth checking, ellipsis-split."""
    page_text = BLOCKQUOTE.sub("", page_text)
    # 🔴 A role page quotes the USER as well as the posting -- "Sacha said he is
    # getting quite hands-on with building AI" is a quotation, and it is correctly
    # not in the advert. Lines that attribute a quote to a person are skipped.
    page_text = "\n".join(l for l in page_text.split("\n")
                          if not re.search(r"\bSacha\b|\bhe said\b|at .{0,20}request", l, re.I))
    out = []
    for whole in QUOTED.findall(page_text):
        # Prose that happens to contain quotation marks is not a quotation. A
        # wiki link or a table pipe inside the span means the regex ran past the
        # end of the quote and swallowed the sentence after it.
        if "[[" in whole or "|" in whole or "](" in whole:
            continue
        for part in ELLIPSIS.split(whole):
            part = flatten(part)
            if len(part) >= MIN_FRAGMENT:
                out.append(part)
    return out


# 🔴 Match on the POSTING ID, not the URL string. Role pages write the same
# posting five ways -- a markdown link, a bare host, a backticked path with no
# scheme at all -- and a regex requiring "https://" found none of them on the very
# page it was written to check.
POSTING_ID = re.compile(r"(?:jobs/view/|/job/|gh_jid=|ashby_jid=)([A-Za-z0-9-]{4,})")


def ids_in(text):
    return set(POSTING_ID.findall(text))


def postings_for(page_text, postings):
    """The archived posting THIS page is about — matched on the posting URL.

    🔴 The first version fuzzy-matched filenames at a 0.55 cutoff and paired
    "Guidewire Engineering Manager JDP AI Integration" with
    "Yuno - Engineering Manager - Payments Integrations". Every quote on that page
    then failed, and 63 of 71 pages reported as misquoting — a check that would
    have been switched off within a day, and whose failures were all its own.

    🟢 Every archived posting carries `Source <url>` in its header, and every role
    page records the same URL. That is an exact key, and it needs no guessing.
    """
    # 🟢 A cluster page covers many roles and quotes all of them, so its quotes are
    # checked against every posting it names, not the first.
    return [postings[i] for i in sorted(ids_in(page_text)) if i in postings]


def load_postings():
    out = {}
    for f in glob.glob(os.path.join(paths.POSTINGS, "*")):
        if not os.path.isfile(f):
            continue
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                body = fh.read()
        except OSError:
            continue
        for i in ids_in(body[:800]):                  # the archive header
            out[i] = (os.path.basename(f), flatten(body))
    return out


def check(page_path, postings):
    """(posting name or None, [quotes that are not in it], total checked)."""
    with open(page_path, encoding="utf-8") as fh:
        page = fh.read()
    quotes = quotations(page)
    if not quotes:
        return None, [], 0
    matched = postings_for(page, postings)
    if not matched:
        return None, [], len(quotes)
    filename = matched[0][0] + (f" +{len(matched)-1} more" if len(matched) > 1 else "")
    body = " \n ".join(b for _, b in matched)
    missing = []
    body_words = re.findall(r"[a-z0-9']+", body)
    for q in quotes:
        if q in body:
            continue
        # 🔴 The distinction that makes this usable. A quotation that is CLOSE to
        # something in the posting was paraphrased inside quotation marks — a real
        # fault, and a small one. A quotation matching nothing is a sentence that
        # was not there, which is the failure that matters.
        missing.append((_classify(q, body_words), q, ""))
    return filename, missing, len(quotes)


def _classify(quote, body_words):
    """'elided' if every word appears in order; 'absent' if not.

    🔴 A similarity RATIO cannot see an elision, and elision is by far the
    commonest fault. Dropping three words from the middle of a long quotation
    barely moves a ratio yet changes the string entirely, so 49 of 56 pages
    reported as fabricating when almost none were.

    The right test is a SUBSEQUENCE: do the quote's words all appear in the
    posting, in order? If yes the sentence was there and was tightened without
    marking the cut — a real fault, and a small one. If no, the sentence was not
    there, which is the failure that matters.
    """
    words = [w for w in re.findall(r"[a-z0-9']+", quote) if w]
    if not words:
        return "absent"
    i = 0
    for w in body_words:
        if w == words[i]:
            i += 1
            if i == len(words):
                return "elided"
    return "absent"


def _windows(body, size):
    """Overlapping slices of the posting, for near-match comparison.

    🔴 The window is WIDER than the quote on purpose. The commonest fault by far
    is not fabrication but elision -- tightening a quotation by dropping a few
    words without marking the cut. "Set safe-AI standards: prompt injection..."
    against a posting reading "Set safe-AI standards FOR AGENTIC SYSTEMS: prompt
    injection...". A same-length window can never match that, so every elision
    read as an invention and 48 of 56 pages reported as fabricating.
    """
    span = int(size * 1.7) + 30
    step = max(size // 3, 25)
    return [body[i:i + span] for i in range(0, max(len(body) - size, 1), step)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--page", help="check one role page by name")
    args = ap.parse_args()

    postings = load_postings()
    if not postings:
        print(f"  no archived postings in {paths.POSTINGS} — nothing to check against.")
        return 0

    pages = sorted(glob.glob(os.path.join(paths.ROLES, "*.md")))
    if args.page:
        pages = [p for p in pages if args.page.lower() in os.path.basename(p).lower()]
        if not pages:
            print(f"  no role page matching {args.page!r}")
            return 1

    checked = unmatched = bad = quotes_total = paraphrased = 0
    for path in pages:
        filename, missing, n = check(path, postings)
        quotes_total += n
        if not n:
            continue
        if filename is None:
            unmatched += 1
            continue
        checked += 1
        absent = [m for m in missing if m[0] == "absent"]
        near = [m for m in missing if m[0] == "elided"]
        if absent:
            bad += 1
            print(f"\n  🔴 {os.path.basename(path)[:-3]}  —  against {filename}")
            for _, q, _ in absent[:3]:
                print(f"       NOT IN THE POSTING: \"{q[:100]}\"")
            if len(absent) > 3:
                print(f"       …and {len(absent) - 3} more")
        if near:
            paraphrased += len(near)

    print(f"\n  {checked} page(s) checked against an archived posting, {quotes_total} quotation(s).")
    if unmatched:
        print(f"  {unmatched} page(s) had no archived posting to check against — "
              f"not a fault, but not checked either.")
    if paraphrased:
        print(f"  🟡 {paraphrased} quotation(s) were TIGHTENED — every word is in the posting, in "
              f"order,\n     but words were dropped without an ellipsis. A small fault, and the "
              f"commonest one.")
    if bad:
        print(f"\n  🔴 {bad} page(s) quote something the posting does not contain.\n"
              f"  A score argued from a line that is not there rests on nothing, and the error\n"
              f"  travels: into the shortlist, into where an evening goes, into the CV.\n"
              f"  🟡 Check the wording before assuming the worst — an accurate quote of an EARLIER\n"
              f"     version of a posting will also fail here, and that is worth knowing too.")
    else:
        print("  🟢 Every quotation appears in its posting. That proves the sentence was there.\n"
              "     It does not prove it was read correctly — only a reader catches that.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
