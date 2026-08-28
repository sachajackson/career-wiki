#!/usr/bin/env python3
"""The questions the wiki has already closed, and the pages that will reopen them.

    python3 tools/gaps.py

TWO DEFECTS, ONE MECHANISM

🔴 **`not recorded` and `recorded as not held` look identical to a search, and
mean opposite things.** Searching for evidence of a capability and finding none
returns "unknown"; the wiki had already produced "confirmed absent". One is a
question, the other is a scored fact that should have lowered a score.

It cost a real question: a capability was put to the user three days after the
wiki had closed it **in two places, with the words "stop asking"**.

🔴 **And the near-miss is worse than the miss.** The user said he had never
commercialised internal tooling. The wiki holds a page about six years spent
selling custom software to enterprise clients — **adjacent, and different**: that
software was built to sell from the outset. On a keyword search the page reads as
a flat contradiction, so a later pass will either re-ask, or write the stretched
claim into an application where it dies at the first follow-up.

🟢 **So the distinction has to live WHERE THE NEXT SEARCH LANDS**, not only on the
page where the question arose. That is the thing this checks.

WHAT IT CANNOT DO

🔴 It cannot stop an agent asking a closed question — that is a runtime
behaviour and no script can force one. What it can do is make the closure
FINDABLE, count how often each gap has been demanded, and name the pages that
still read as contradictions.
"""
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import paths  # noqa: E402

FRAMEWORK = "Role Scoring Framework.md"
SECTION = re.compile(r"^#+\s*.*standing gaps", re.I)
ROW = re.compile(r"^\|\s*(?:🔴|🟡|🟢)?\s*\*\*(?P<gap>[^*]+)\*\*\s*\|(?P<status>[^|]*)\|(?P<where>[^|]*)\|")
# 🟢 The answer to a closed question is phrased as a NEGATION, which is exactly
# what an evidence search misses. A row without one of these is not findable by
# anybody looking for the resolution rather than the evidence.
RESOLVED = re.compile(r"confirmed absent|absent|no evidence|none|does not|do not ask|stop asking|"
                      r"resolved|never", re.I)
# A page that has been told how it differs from a gap it resembles.
DISTINCTION = re.compile(r"does not apply|adjacent|not the same|different thing|"
                         r"is not what|standing gap|Budget and Commercial Scope", re.I)
# A page that has been told how it differs from a gap it resembles.
DISTINCTION = re.compile(r"does not apply|adjacent, and different|not the same|different thing|"
                         r"standing gap|near miss|near-miss", re.I)
# The declared near-miss column: `Looks like: [[Page]], [[Other]]`
LOOKS_LIKE = re.compile(r"looks like:\s*(.+)$", re.I)
WIKILINK = re.compile(r"\[\[([^\]|]+)")


def _table(text):
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if SECTION.match(l)), None)
    if start is None:
        return []
    out = []
    for l in lines[start:]:
        if l.startswith("#") and out:
            break
        m = ROW.match(l)
        if m:
            row = {k: m.group(k).strip() for k in ("gap", "status", "where")}
            rest = l[m.end():]
            found = LOOKS_LIKE.search(row["where"] + " " + rest)
            row["looks_like"] = WIKILINK.findall(found.group(1)) if found else []
            out.append(row)
    return out


def gaps():
    try:
        with open(os.path.join(paths.WIKI, FRAMEWORK), encoding="utf-8") as fh:
            return _table(fh.read())
    except OSError:
        return []


def demands(where):
    """How many postings have asked for this. Three is a decision, not a coincidence."""
    where = LOOKS_LIKE.split(where)[0]
    # 🟡 The split leaves the markdown that introduced the declaration behind —
    # `Acme, Beta · **` — and a fragment of asterisks was counted as a third
    # posting, which is the threshold that turns a coincidence into a question.
    parts = [re.sub(r"[^\w &-]", "", w).strip() for w in re.split(r"[,·]", where)]
    return len([w for w in parts if re.search(r"[A-Za-z0-9]", w)])


def undistinguished(row):
    """Declared near-miss pages that still say nothing about the difference.

    🔴 THE TOOL GUESSED THIS FOR TWO VERSIONS AND BOTH WERE UNUSABLE. Deriving
    terms from the gap's title missed the only case it was built for -- the page
    says "sold software as a business owner", never "commercialising internal
    tooling" -- and deriving them from the status found 25 pages, because a
    handful of common words co-occur everywhere.

    🟢 So the table DECLARES them: `Looks like: [[Page]]`. That is not a
    shortcut. Deciding a page resembles a gap is exactly the judgement a person
    has to make, and the column is where they record having made it -- while
    the check enforces the half that follows automatically.
    """
    out = []
    for page in row.get("looks_like", []):
        f = os.path.join(paths.WIKI, f"{page}.md")
        if not os.path.exists(f):
            out.append((page, "no such page"))
            continue
        with open(f, encoding="utf-8") as fh:
            if not DISTINCTION.search(fh.read()):
                out.append((page, "no distinction written on it"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true", help="only what needs attention")
    args = ap.parse_args()
    rows = gaps()
    if not rows:
        print("\n  no standing-gaps table found — nothing has been closed yet.\n")
        return 0

    print(f"\n  {len(rows)} closed question(s). 🔴 Do not re-ask any of these.\n")
    unfindable, risky, pressing = [], [], []
    for g in rows:
        n = demands(g["where"])
        flag = "🔴" if n >= 3 else "  "
        if not args.quiet:
            print(f"  {flag} {g['gap'][:44]:44} demanded by {n}")
        if not RESOLVED.search(g["status"]):
            unfindable.append(g["gap"])
        if n >= 3:
            pressing.append((g["gap"], n))
        for page, why in undistinguished(g):
            risky.append((g["gap"], page, why))

    if unfindable:
        print(f"\n  🔴 {len(unfindable)} gap(s) have no resolution WORD in their status:")
        for g in unfindable:
            print(f"       {g[:60]}")
        print("     A resolution is phrased as a negation, and that is exactly what an\n"
              "     evidence search misses. Without one, this row is unfindable.")
    if risky:
        print(f"\n  🔴 {len(risky)} declared near-miss page(s) carry no distinction:")
        for g, page, why in risky:
            print(f"       {page[:38]:38} declared like {g[:26]:26} — {why}")
        print("     🟡 Adjacent is not the same as contradictory — but the distinction has to be\n"
              "     WRITTEN ON THAT PAGE, because that is where the next search lands.")
    if pressing:
        print(f"\n  🟡 {len(pressing)} gap(s) demanded three times or more:")
        for g, n in pressing:
            print(f"       {g[:44]:44} {n} postings")
        print("     Two is a coincidence. Three is a question to put to the user ONCE —\n"
              "     is this worth going and acquiring? — rather than conceded in every letter.")
    if not (unfindable or risky):
        print("\n  🟢 every closed question is findable, and no page contradicts one.")
    print()
    return 1 if (unfindable or risky) else 0


if __name__ == "__main__":
    sys.exit(main())
