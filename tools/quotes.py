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

🟢 STATUS 2026-08-27: GATING. Wired into `doctor.py` and `pipeline.py`.

It reported 69 of 71 pages on its first run and now reports none, and every step
of that was a bug in the CHECK, found by running it rather than reasoning about
it:

  69 of 71   a blockquote's "> " prefix leaked into every multi-line quotation
  63 of 71   fuzzy filename matching paired Guidewire's page with Yuno's posting
   5 of  6   a URL regex requiring "https://" found no URLs on the pages it checked
  49 of 56   a similarity ratio cannot see an ELISION, the commonest fault by far
  28 of 56   the regex paired one quotation's closing mark with the next one's
             opening mark and returned whole paragraphs of our own commentary
   2 of 45   two genuine faults, both fixed
   0 of 45   quoting an employer's typo faithfully with [sic] broke the match

🔴 THE NARROWING THAT MADE IT WORK is two tiers, because an emphasised quotation
here is used for four different things and only one is the employer: a line from
the posting, something the USER said, a finding of our own, a question from an
application form. A BLOCKQUOTE is unambiguous -- it is this vault's convention
for THIS IS WHAT THE POSTING SAYS -- so a blockquote miss GATES, and an inline
miss is reported and never gated on. Blockquote-only was tried and checked 17
quotations out of 323; everything-inline reported 14 pages, mostly our own words.

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

# 🔴 EMPHASIS IS REQUIRED, and that is what tells a quotation from prose.
#
# The first version accepted any span between two double quotes. Markdown prose
# uses quote marks constantly, so the regex paired the closing quote of one
# quotation with the opening quote of the next and swallowed everything between
# -- returning whole paragraphs of commentary as "quotations the posting does not
# contain". Of 92 such reports, most were this.
#
# Every real quotation in this vault is written the same way: emphasised, either
# inline as *"..."* or inside a blockquote. Requiring the emphasis marker costs
# nothing and removes the entire class.
QUOTED = re.compile(r'[*_]{1,3}["“]([^"”\n]{25,}?)["”][*_]{1,3}')
# 🔴 Fragments shorter than this match by accident. Measured: 25 characters is
# where coincidental matches stop and real quotations start.
MIN_FRAGMENT = 25
# Ellipsis joins two separate parts of a posting into one quotation, so each side
# is checked independently. Writing a quote that way is correct and common.
ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…|\[\.\.\.\])\s*")


# 🔴 Editorial insertions are part of quoting properly, not a corruption of it.
# "[sic]" marks an employer's own typo faithfully; "[emphasis added]" marks our
# own formatting. Both belong INSIDE the quotation marks and neither is in the
# posting, so both must be removed before comparing — otherwise quoting correctly
# is what makes the check fail.
EDITORIAL = re.compile(r"\[(?:sic|emphasis added|our emphasis|…|\.\.\.)\]", re.I)


def flatten(text):
    """Whitespace, emphasis, editorial marks and smart punctuation removed."""
    text = EDITORIAL.sub(" ", text)
    text = html.unescape(text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"[*_`]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


# 🔴 A blockquote's "> " prefix leaked into extracted quotations and made every
# multi-line quote fail. Most role pages quote inside a blockquote, so the first
# run reported 69 of 71 pages as misquoting — a check nobody would run twice.
BLOCKQUOTE = re.compile(r"^\s*>\s?")


def quotations(page_text):
    """[(strength, fragment)] — 'claimed' in a blockquote, 'inline' otherwise.

    🔴 TWO TIERS, because an emphasised quotation in this vault is used for four
    different things and only one of them can be checked against an advert: a line
    from the posting, a sentence the USER said, a finding of the assessment's own,
    and a question from an application form. The last three are CORRECTLY absent
    from the employer's text.

    🟢 A blockquote is unambiguous — it is this vault's convention for THIS IS WHAT
    THE POSTING SAYS. So a blockquote miss is a claim about the employer that does
    not hold, and it gates. An inline miss is advisory, because "the ceiling is
    disciplinary" and "their office seems to be in a block of apartments" are
    quotations of nobody but us.

    Measured: blockquote-only checked 17 quotations and missed almost everything;
    everything-inline reported 14 pages, mostly our own words. Two tiers keeps the
    coverage and gates only on the claim.
    """
    out = []
    for line in page_text.split("\n"):
        claimed = bool(BLOCKQUOTE.match(line))
        body = BLOCKQUOTE.sub("", line)
        # A line attributing a quotation to a person is not about the posting.
        if re.search(r"\bSacha\b|\bhe said\b|at .{0,20}request", body, re.I):
            continue
        for whole in QUOTED.findall(body):
            if "[[" in whole or "|" in whole or "](" in whole:
                continue
            for part in ELLIPSIS.split(whole):
                part = flatten(part)
                if len(part) >= MIN_FRAGMENT:
                    out.append(("claimed" if claimed else "inline", part))
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


# 🔴 An assessment that says its source was cut stops looking, and the caveat is
# never revisited. Found on five pages at once, every one of them false -- and on
# the two highest-scoring roles in the vault it is why LIFE, PAY and REQS were all
# left unanswered for a week while the posting stated every one of them.
TRUNCATED = re.compile(r"truncat", re.I)
# A posting that reaches any of these reached its end. An aggregator cut lands
# mid-body, long before the legal boilerplate.
# 🔴 Widened twice. The first list was written from two employers' footers and
# missed Toast (which closes on a Massachusetts lie-detector statute) and Pfizer
# (candidate AI-use guidelines, then a job-family tag). A posting's end matter is
# legal boilerplate, and every employer picks a different clause -- so match the
# CATEGORY, not the phrasings that happened to be in front of me.
COMPLETE = re.compile(r"EEO|Equal Opportunit|Salary Range|Know Your Rights|Recruitment Agenc|"
                      r"requisition|protected veteran|without regard to (race|sex)|"
                      r"reasonable accommodation|lie detector|criminal penalties|"
                      r"Total Rewards|Diversity, Equity", re.I)


# 🔴 THE FIRST VERSION OF THIS CHECK FIRED ON ITS OWN FIXES. Correcting a page
# means writing the word "truncated" on it -- "the truncation caveat here was
# wrong" -- so all five pages still reported after three had been repaired. A
# check that cannot tell a claim from its retraction reports its own successes as
# failures, and gets switched off the same day.
RETRACTED = re.compile(r"not truncated|wrong|is false|is complete|COMPLETE|corrected|checked \d{4}-", re.I)


# 🔴 A REQUISITION NUMBER IS THE ONE FACT THAT LEAVES THE VAULT. It goes in the
# filename of the CV, in the covering letter, and into the portal field. Two of
# the three stated in this vault traced to nothing archived -- and one of those
# two is printed on four documents already sent to the employer.
#
# 🟡 It does not mean the number is wrong. Both were read off the employer's own
# site at the time. It means NOTHING CAN CHECK THEM, because the page they were
# read from was never archived -- runbook step 7, skipped.
REQ_CELL = re.compile(
    r"\|\s*\**(?:Job identification|Job ID|Job number|Requisition(?: number| ID)?)\**\s*"
    r"\|\s*\**([A-Za-z0-9][A-Za-z0-9_-]{3,})\**\s*\|", re.I)


def untraceable_ids(page_text, archive_text):
    """[requisition ids] stated on a page and found in no archived posting."""
    return [m.group(1) for m in REQ_CELL.finditer(page_text)
            if m.group(1) not in archive_text]


def archive_text():
    """Every archived posting concatenated — the haystack for untraceable_ids."""
    out = []
    for f in sorted(glob.glob(os.path.join(paths.POSTINGS, "*"))):
        if not os.path.isfile(f):
            continue
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                out.append(fh.read())
        except OSError:
            pass
    return "\n".join(out)


def false_truncation(page_text, postings):
    """True when a page claims a cut source and the archive runs to its end.

    🟡 Deliberately one-directional. A page that says nothing about its source is
    not reported -- silence is the normal case, and flagging it would put every
    assessment in the list. Only an explicit claim that turns out to be wrong.
    """
    # 🔴 PARAGRAPHS, NOT LINES. Markdown here wraps at ~100 characters, so the
    # claim and its retraction routinely land on different lines -- "the
    # truncation caveat that stood here was simply / wrong". Line-by-line, the
    # first half fires and the second half is never seen.
    paras = re.split(r"\n\s*\n", page_text)
    claims = [pa for pa in paras
              if TRUNCATED.search(pa) and not RETRACTED.search(pa)]
    if not claims:
        return False
    bodies = postings_for(page_text, postings)
    # postings_for yields (filename, body) pairs, not bare text.
    return bool(bodies) and any(COMPLETE.search(b) for _, b in bodies)


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
            # 🔴 TWO ARCHIVES ROUTINELY SHARE ONE ID -- the radar's clean capture
            # and a raw page scrape of the same URL. This was a plain assignment,
            # so whichever glob happened to return LAST won, unsorted. For Pfizer
            # that was a scrape ending at LinkedIn's sign-in wall, which beat the
            # complete capture ending at the employer's own footer.
            #
            # 🟢 Keep the longer body. It is the cruder rule and the right one: a
            # truncated capture is always shorter than the posting it truncates,
            # and every check downstream -- quotations, truncation claims -- is
            # better served by more of the employer's text.
            flat = flatten(body)
            if i not in out or len(flat) > len(out[i][1]):
                out[i] = (os.path.basename(f), flat)
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
    for tier, q in quotes:
        if q in body:
            continue
        # 🔴 The distinction that makes this usable. A quotation that is CLOSE to
        # something in the posting was paraphrased inside quotation marks — a real
        # fault, and a small one. A quotation matching nothing is a sentence that
        # was not there, which is the failure that matters.
        missing.append((_classify(q, body_words), q, tier))
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

    checked = unmatched = bad = quotes_total = paraphrased = advisory = 0
    stale = []
    haystack = archive_text()
    untraceable = []
    for path in pages:
        filename, missing, n = check(path, postings)
        quotes_total += n
        if not n:
            continue
        if filename is None:
            unmatched += 1
            continue
        checked += 1
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        if false_truncation(body, postings):
            stale.append(os.path.basename(path)[:-3])
        for rid in untraceable_ids(body, haystack):
            untraceable.append((os.path.basename(path)[:-3], rid))
        absent = [m for m in missing if m[0] == "absent" and m[2] == "claimed"]
        soft = [m for m in missing if m[0] == "absent" and m[2] == "inline"]
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
        advisory += len(soft)

    print(f"\n  {checked} page(s) checked against an archived posting, {quotes_total} quotation(s).")
    if unmatched:
        print(f"  {unmatched} page(s) had no archived posting to check against — "
              f"not a fault, but not checked either.")
    if advisory:
        print(f"  🟡 {advisory} inline quotation(s) are not in the posting. Most will be the user's own\n"
              f"     words or a finding of ours rather than the employer's — reported, never gated on.")
    if paraphrased:
        print(f"  🟡 {paraphrased} quotation(s) were TIGHTENED — every word is in the posting, in "
              f"order,\n     but words were dropped without an ellipsis. A small fault, and the "
              f"commonest one.")
    if stale:
        print(f"\n  🔴 {len(stale)} page(s) say their source was TRUNCATED, and the archive runs to its "
              f"end:\n" + "".join(f"       {n[:60]}\n" for n in stale) +
              f"  🔴 The caveat is load-bearing. On the two highest-scoring roles in this vault it is\n"
              f"     why LIFE, PAY and REQS were all left unanswered for a week — while the posting\n"
              f"     stated every one of them, salary band included.")
    if untraceable:
        print(f"\n  🔴 {len(untraceable)} stated requisition number(s) appear in NO archived posting:")
        for n, rid in untraceable:
            print(f"       {rid:14} {n[:52]}")
        print(f"  🟡 That does not make them wrong — they were read off the employer's site at the\n"
              f"     time. It means nothing can check them, because the page was never archived.\n"
              f"  🔴 A requisition number is the one fact that LEAVES the vault: the CV filename,\n"
              f"     the covering letter, the portal field. Re-fetch before the next contact.")
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
