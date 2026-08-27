#!/usr/bin/env python3
"""The arithmetic of a score, and which scores nobody has argued with.

    python3 tools/scores.py            # every fault, and what is due review
    python3 tools/scores.py --due      # just the review queue, one per line

WHAT THIS CATCHES, AND THE MUCH LARGER THING IT DOES NOT

🟢 Three faults, all computable, all silent, and one of them was real on the day
this was written -- a role scored 4·4·2 carried a FIT of 9, on the page and in
the table, under a heading reading "What holds it at 9". Every component was
argued for in prose. The total was a slip, and it had been read several times.

  ARITHMETIC   N + D + E must equal FIT.
  RANGE        Components are out of 5, FIT out of 15, LIFE and SEC out of 5.
  AGREEMENT    A role page carries its own score block AND a row in the scoring
               table. Two copies of a number drift, and the table is what gets
               read when roles are compared.

🔴 WHAT IT CANNOT DO, and the reason the `role-review` agent exists: it checks
that the numbers are consistent with EACH OTHER. It has no way to check them
against the posting. A role read wrongly and scored 3·3·3 is perfectly
consistent, and wrong, and this tool will call it clean.

  quotes.py    proves a sentence was IN the posting
  this         proves the numbers hang together
  role-review  proves the sentence was READ correctly -- the only one of the
               three that cannot be a string operation, and the only one that
               needs a model

THE REVIEW QUEUE

🔴 A script cannot spawn an agent, which is how `.claude/agents/role-triage.md`
came to exist for the life of this repo and never once run. What a script CAN do
is make the delegation checkable -- the batch.py pattern. So this answers one
question with a list: WHICH SCORES ARE ABOUT TO BE ACTED ON AND HAVE NEVER BEEN
ARGUED WITH?

A page is due review when its FIT is at or above REVIEW_AT, an archived posting
exists to review it against, and no `**Review YYYY-MM-DD — ...**` line is on it.

🟡 Below REVIEW_AT nothing is queued, deliberately. Reviewing 106 assessments
costs more than the decisions it would change, and a queue nobody can finish is
a queue nobody starts.
"""
import argparse
import glob
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import paths  # noqa: E402

_spec = importlib.util.spec_from_file_location("quotes", os.path.join(HERE, "quotes.py"))
quotes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(quotes)

REVIEW_AT = 10

# `4·4·2`, in a page's score block or a table cell, with or without emphasis.
NDE = re.compile(r"(?<![\d·])(\d)\s*·\s*(\d)\s*·\s*(\d)(?![\d·])")
REVIEWED = re.compile(r"^\*\*Review\s+(\d{4}-\d{2}-\d{2})\s*[—-]\s*([A-Z][A-Z -]+)", re.M)
LINK = re.compile(r"^\|\s*\[\[([^\]\\|]+)")
HEADER = re.compile(r"^\|\s*Role\s*\|")
# 🔴 THE BUG THAT MADE THIS TOOL'S FIRST RUN REPORT 17 FAULTS WHERE THERE WAS 1.
# This vault's own convention puts a status marker INSIDE a score cell -- the real
# cell reads `🔴 **7**`, not `7`. A regex anchored on a digit matched nothing there,
# the parser walked on to the next numeric-looking column, and read SEC as FIT.
# Every "arithmetic" fault it reported was the number 4 from the wrong column.
DECOR = re.compile(r"[*_`]|[\U0001F300-\U0001FAFF\u2190-\u21FF\u2600-\u27BF\uFE0F]")
LEADING_NUM = re.compile(r"^\s*(\d{1,2})\s*(?:/\s*\d{1,2})?\s*(?:$|[—\-])")


def undecorate(cell):
    return DECOR.sub("", cell).strip()


def score_in(cell):
    """The number a score cell carries, or None.

    🟡 Anchored at the START and allowed to be followed by an em-dash, because
    a LIFE cell legitimately carries its reason: `🔴 **1** — "primarily in the
    office"`. Requiring the whole cell to be a number drops those; searching
    anywhere in it picks a number out of the reason.
    """
    found = LEADING_NUM.match(undecorate(cell))
    return int(found.group(1)) if found else None


def _cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def table_rows():
    """{page name: (nde, fit)} — by COLUMN NAME, never by walking for something
    that looks like a number. The header is right there; use it."""
    out = {}
    try:
        with open(os.path.join(paths.WIKI, "Role Scoring Framework.md"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return out
    cols = {}
    for line in text.split("\n"):
        if HEADER.match(line):
            cols = {undecorate(c).upper(): i for i, c in enumerate(_cells(line))}
            continue
        link = LINK.match(line)
        if not link or "FIT" not in cols:
            continue
        cells = _cells(line)

        def at(name):
            i = cols.get(name)
            return cells[i] if i is not None and i < len(cells) else ""

        found = NDE.search(undecorate(at("N·D·E")))
        out[link.group(1).strip()] = (tuple(int(g) for g in found.groups()) if found else None,
                                      score_in(at("FIT")))
    return out


def _page_dim(text, name):
    """A page's own score block: `| 🟢 **FIT** | **12/15** |`.

    🔴 The marker goes in front of the LABEL as often as the value, so the label
    is undecorated too. Anchoring on `| **FIT**` missed every page that flagged
    its own score, which is disproportionately the interesting ones.
    """
    for line in text.split("\n"):
        cells = _cells(line)
        if len(cells) >= 3 and undecorate(cells[1]).upper() == name:
            return score_in(cells[2])
    return None


def page_own(text):
    """(nde, fit) from the page's OWN vertical score block, or (None, None).

    🔴 A cluster page has no vertical block -- it is a TABLE OF SEVERAL ROLES,
    each with its own N·D·E and FIT on one line. Reading the first `·` on the
    page and the first FIT-shaped number gave a pair belonging to two different
    roles, and reported three clean cluster pages as faulty.
    """
    nde = None
    for line in text.split("\n"):
        cells = _cells(line)
        if len(cells) >= 3 and undecorate(cells[1]).upper() == "N·D·E":
            found = NDE.search(undecorate(cells[2]))
            nde = tuple(int(g) for g in found.groups()) if found else None
            break
    return nde, _page_dim(text, "FIT")


def inline_pairs(text):
    """[(nde, fit)] for every line carrying BOTH -- one row per role on a
    cluster page. Each is checked on its own; none is compared to the table,
    because the table's row for a cluster is one of the roles inside it."""
    out = []
    for line in text.split("\n"):
        cells = [undecorate(c) for c in _cells(line)]
        for i, c in enumerate(cells[:-1]):
            found = NDE.fullmatch(c.replace(" ", ""))
            if not found:
                continue
            fit = score_in(cells[i + 1])
            if fit is not None:
                out.append((tuple(int(g) for g in found.groups()), fit))
    return out


def audit():
    """([faults], [due review], scored) — everything computed from the vault.

    🔴 `scored` is returned because zero is not the same as clean. A vault with
    no scored assessments passes every check in here, and reporting that as OK
    is the "looks configured and matches nothing" failure this repo tests for.
    """
    rows = table_rows()
    postings = quotes.load_postings()
    faults, due, scored = [], [], 0
    for path in sorted(glob.glob(os.path.join(paths.ROLES, "*.md"))):
        name = os.path.basename(path)[:-3]
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue
        page_nde, page_fit = page_own(text)
        row_nde, row_fit = rows.get(name, (None, None))

        nde = page_nde or row_nde
        fit = page_fit if page_fit is not None else row_fit
        if nde or fit is not None:
            scored += 1

        # The page's own score, plus every row of a cluster page's table.
        for a, f in ([(page_nde, page_fit)] if page_nde and page_fit is not None
                     else []) + inline_pairs(text):
            if sum(a) != f:
                faults.append((name, "arithmetic",
                               f"{'·'.join(str(n) for n in a)} = {sum(a)}, but FIT reads {f}"))
        if not page_nde and nde and fit is not None and sum(nde) != fit:
            faults.append((name, "arithmetic",
                           f"{'·'.join(str(n) for n in nde)} = {sum(nde)}, but FIT reads {fit}"))
        if fit is not None and not 0 <= fit <= 15:
            faults.append((name, "range", f"FIT {fit} is outside 0–15"))
        for dim in ("LIFE", "SEC"):
            v = _page_dim(text, dim)
            if v is not None and not 0 <= v <= 5:
                faults.append((name, "range", f"{dim} {v} is outside 0–5"))
        # 🔴 Two copies of one number drift, and the table is the copy that gets
        # read when roles are compared against each other.
        if page_fit is not None and row_fit is not None and page_fit != row_fit:
            faults.append((name, "agreement",
                           f"the page says FIT {page_fit}, the table says {row_fit}"))
        if page_nde and row_nde and page_nde != row_nde:
            faults.append((name, "agreement",
                           f"the page says {'·'.join(map(str, page_nde))}, "
                           f"the table says {'·'.join(map(str, row_nde))}"))

        if fit is not None and fit >= REVIEW_AT and not REVIEWED.search(text):
            # No archived posting means no review is possible, not that one is owed.
            if quotes.postings_for(text, postings):
                due.append((name, fit))
    due.sort(key=lambda r: -r[1])
    return faults, due, scored


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--due", action="store_true", help="just the review queue")
    args = ap.parse_args()
    faults, due, scored = audit()

    if args.due:
        for name, fit in due:
            print(f"{fit:2d}  {name}")
        return 0

    print()
    if not scored:
        print("  no scored assessments yet — nothing to check.\n")
        return 0
    if faults:
        print(f"  🔴 {len(faults)} fault(s) in the numbers:\n")
        for name, kind, detail in faults:
            print(f"     {kind:10} {name[:46]:46} {detail}")
    else:
        print("  🟢 the numbers hang together — arithmetic, range and page/table agreement.")
    print(f"\n  🔴 That is consistency, NOT correctness. A role read wrongly and scored"
          f"\n     consistently passes every check above. Only reading the posting settles it.\n")

    if due:
        print(f"  {len(due)} assessment(s) at FIT {REVIEW_AT}+ have an archived posting "
              f"and no recorded review:\n")
        for name, fit in due:
            print(f"     FIT {fit:2d}   {name}")
        print(f"\n  🔴 Hand these to the `role-review` agent — several in parallel above ~6 —"
              f"\n     then add its one-line verdict to each page. Nothing else records it.\n")
    else:
        print("  🟢 every assessment at FIT %d+ with an archived posting has been "
              "reviewed.\n" % REVIEW_AT)
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main())
