#!/usr/bin/env python3
"""Which applications have been submitted and never heard about again?

    python3 tools/outcomes.py

WHY THIS EXISTS, AND WHY AN INSTRUCTION WAS NOT ENOUGH

`SCHEMA.md` said "record what happened to every application". Across seven
applications and six weeks, ONE outcome was recorded. The rule was then re-shipped
as a step inside `/career-lint` -- which is still an instruction, and that skill
names it "the check most likely to be skipped, because nothing triggers it".

🔴 That is twice, and this repo's rule is that when something goes wrong twice the
fix is not a stronger warning. Every other operation here has a trigger: a
document arrives, a role is found, a document is written. **An outcome arrives in
somebody's inbox and the system never hears about it.** This is the trigger.

WHAT IT READS

Any markdown table row under `vault/wiki/` carrying a status from the closed
vocabulary. It deliberately does not know the shape of one particular table --
the same application is listed in two places with different columns, and a parser
tied to either would miss the other.

🔴 IT NEVER WRITES. An outcome is something a human knows and this tool does not.
It says which questions are owed and to whom.

THE THREE VERDICTS

    ASK        submitted more than 7 days ago, nothing recorded
    RECORD     more than 21 days. Silence IS the outcome -- write `no response`,
               because a blank field looks unasked rather than unanswered
    UNDATEABLE 🔴 submitted, and no date anywhere. Its age cannot be computed at
               all, so it can never become either of the above. This is the
               quietest failure of the three and the reason the tool reports it
               first
"""
import argparse
import datetime
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import paths  # noqa: E402

ASK_AFTER, RECORD_AFTER = 7, 21

# 🔴 A STATUS CELL, NOT A MENTION -- and this applies to BOTH halves of the
# vocabulary. The cell must BE the status once emphasis and emoji are stripped.
#
# Measured against the real vault, matching anywhere on the line went wrong in
# both directions on the same day. A loose "Submitted" matched a column header
# ("Submitted with") and a sentence about a CV that could no longer be changed.
# A loose settled-check then matched the word "closed" inside the prose of a note
# and silently swallowed a live application that was 14 days unanswered -- the
# exact case the tool exists to surface.
#
# "Rejected" alone is deliberately absent from the vocabulary: it once meant both
# "the employer turned them down" and "they chose not to apply", four days apart
# in the same table.
SETTLED_WORDS = ("rejected by employer", "withdrew", "declined", "closed",
                 "vetoed", "not applied", "no response")
TERM = re.compile(r"^(submitted|" + "|".join(SETTLED_WORDS) + r")"
                  r"(?:\s+(\d{4}-\d{2}-\d{2}))?$", re.I)
LINK = re.compile(r"\[\[([^\]|\\]+)(?:\\?\|([^\]]+))?\]\]")
NOISE = re.compile(r"[*`_]|[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]")


def plain(cell):
    return NOISE.sub("", cell).replace("\u2014", "-").strip(" -\u2013\u2014")


def statuses(cells):
    """Every cell that IS a status, as (term, date-or-None)."""
    out = []
    for c in cells:
        m = TERM.match(plain(c))
        if m:
            out.append((m.group(1).lower(), m.group(2)))
    return out


def rows(wiki):
    """(key, display name, submitted-date or None, page) per LIVE submitted row.

    Keyed on the WIKI-LINK TARGET rather than the visible text, because the same
    application is listed in several tables with different display names --
    "JPMorganChase" in one and "JPMorganChase -- Lead TPM (210768893)" in
    another. The link target is identical in both.
    """
    for page in sorted(glob.glob(os.path.join(wiki, "*.md"))):
        with open(page, encoding="utf-8") as fh:
            for line in fh:
                if not line.startswith("| ") or "---" in line:
                    continue
                found = statuses([c.strip() for c in re.split(r"(?<!\\)\|", line)])
                if not found:
                    continue
                if any(term != "submitted" for term, _ in found):
                    continue                      # already settled
                link = LINK.search(line)
                if not link:
                    continue                      # no role page: not an application row
                when = next((d for term, d in found if term == "submitted" and d), None)
                yield (link.group(1).strip().lower(),
                       (link.group(2) or link.group(1)).strip(), when,
                       os.path.basename(page))


def review(wiki, today=None):
    """(ask, record, undateable) -- each a list of (name, days_or_None, page)."""
    today = today or datetime.date.today()
    seen = {}
    for key, name, when, page in rows(wiki):
        # Keep whichever listing carries a date, so a dated row is never hidden
        # by an undated duplicate of the same application.
        if key in seen and seen[key][1] and not when:
            continue
        seen[key] = (name, when, page)
    ask, record, undateable = [], [], []
    for name, when, page in seen.values():
        if not when:
            undateable.append((name, None, page)); continue
        try:
            age = (today - datetime.date.fromisoformat(when)).days
        except ValueError:
            undateable.append((name, None, page)); continue
        if age >= RECORD_AFTER:
            record.append((name, age, page))
        elif age >= ASK_AFTER:
            ask.append((name, age, page))
    return (sorted(ask, key=lambda r: -r[1]),
            sorted(record, key=lambda r: -r[1]),
            sorted(undateable))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wiki", default=paths.WIKI)
    args = ap.parse_args()

    if not os.path.isdir(args.wiki):
        print(f"  no wiki at {args.wiki!r} — nothing to check.")
        return 0

    ask, record, undateable = review(args.wiki)

    if undateable:
        print(f"\n  🔴 SUBMITTED, NO DATE — {len(undateable)}. Their age cannot be computed, so "
              f"they will\n     never appear below however long they go unanswered.")
        for name, _, page in undateable:
            print(f"     {name}")
        print("     Add the date to the status cell — `Submitted YYYY-MM-DD`.")

    if record:
        print(f"\n  RECORD AN OUTCOME — {len(record)}, over {RECORD_AFTER} days:")
        for name, age, _ in record:
            print(f"     {age:3d} days   {name}")
        print("     Silence is data. Record `no response` rather than leaving it blank —\n"
              "     a blank field looks unasked rather than unanswered.")

    if ask:
        print(f"\n  ASK — {len(ask)}, over {ASK_AFTER} days:")
        for name, age, _ in ask:
            print(f"     {age:3d} days   {name}")
        print("     Any acknowledgement, rejection, or silence?")

    total = len(ask) + len(record) + len(undateable)
    if not total:
        print("\n  Nothing owed. Every submitted application is either recent or already "
              "answered.\n  That is not the same as every application having gone well.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
