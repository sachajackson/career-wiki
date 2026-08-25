#!/usr/bin/env python3
"""What has the template gained that this vault never got?

    python3 tools/template_drift.py --wiki wiki

WHY THIS EXISTS. `/career-init` copies `templates/` into `wiki/` ONCE, and
nothing ever revisits it. `sync-to-vault.sh` deliberately refuses to touch
`wiki/`, because that directory is the person and not the tool. So the tool
improves and the vault does not, silently, for as long as somebody keeps using
it.

That is not hypothetical. On 2026-08-25 the framework template gained a standing
gaps table, a known locations table, a baseline row, an internal-move row and a
seven-value outcome vocabulary. `CLAUDE.md` -- which IS synced -- was updated to
instruct the agent to use all five. Every vault created before that morning has
an agent looking for tables that are not there.

WHAT IT REPORTS, AND WHAT IT WILL NOT DO

It reports three things: sections a template has and a page does not, sections
whose table the page is missing, and rows the template SHIPS FILLED IN that the
page has not got. The third matters more than it sounds -- the baseline row and
the internal-move row both live inside a table every vault already had, so a
section-level check walks straight past them.

It NEVER WRITES. Merging a new section into a page that already holds a real
person's history is a judgement: where it goes, what carries over, whether an
existing note belongs under it. The agent owns wiki pages and can do that. A
script that rewrote them would be editing the one thing in this repo it does not
own, and a bad merge there costs somebody their notes.

It also cannot tell you a section is UP TO DATE -- only that it is present. A
template section whose contents changed reads as fine here.
"""
import argparse, difflib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(os.path.dirname(HERE), "templates")

# Pages only. cv.html and the example JSON are not wiki pages.
SKIP = {"application.example.json", "cv.html"}
HEADING = re.compile(r"^(#{2,4})\s+(.*)$", re.M)
NOISE = re.compile(r"[^a-z0-9 ]+")
# Close enough that a reworded heading is recognised, far enough that two
# genuinely different sections are not confused for one another.
SAME = 0.75


def subject(heading):
    return " ".join(NOISE.sub(" ", heading.lower()).split())


def same(a, b):
    """Is this the same section, allowing for the agent's own phrasing?

    Ratio alone is too strict when a heading GAINS words -- "standing gaps"
    against "standing gaps (capabilities)" scores 0.67 and would be reported as
    missing. That is the false positive that gets a check switched off, so
    containment counts too, with a length floor so short headings do not match
    each other by accident.
    """
    if difflib.SequenceMatcher(None, a, b).ratio() >= SAME:
        return True
    return len(a) >= 8 and len(b) >= 8 and (a in b or b in a)


def sections(text):
    """-> [(subject, heading, body)] for every ## / ### / #### in the file."""
    out, parts = [], HEADING.split(text)
    for i in range(1, len(parts), 3):
        heading, body = parts[i + 1].strip(), parts[i + 2]
        out.append((subject(heading), heading, body))
    return out


def has_table(body):
    return bool(re.search(r"^\|.*\|\s*$", body, re.M))


def seeded_rows(body):
    """Table rows the template SHIPS FILLED IN, by their first cell.

    A blank row is a place to write; a filled one is content the page is
    supposed to carry. The framework's scoring table seeds two -- the current
    job and the internal move -- and both are rows that `CLAUDE.md` instructs
    the agent to score. Ship the empty table, and ship the row that is not empty.
    """
    out = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.fullmatch(r"\|[\s|:-]+\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # An empty first cell is a legend row or a blank one -- a place to write
        # rather than content to carry. Dropped here so the caller does not have
        # to know that; it was guarded in both places, which reads as two rules.
        if cells and cells[0]:
            out.append(cells[0])
    return out


def compare(template_text, page_text):
    """-> (missing_sections, tableless_sections, missing_rows)."""
    theirs = sections(page_text)
    missing, tableless, rows = [], [], []
    for subj, heading, body in sections(template_text):
        if not subj:
            continue
        best = next((b2 for s2, _, b2 in theirs if same(subj, s2)), None)
        if best is None:
            missing.append(heading)
            continue
        if has_table(body) and not has_table(best):
            # The rule that produced this check in the first place: a section
            # heading with no table under it is a place to write nothing.
            tableless.append(heading)
            continue
        # A section can be present, with its table, and still be missing a row
        # the template seeds. That is how the baseline and internal-move rows
        # would have gone unnoticed: they live inside a table a vault already had.
        got = [subject(c) for c in seeded_rows(best)]
        for cell in seeded_rows(body):
            want = subject(cell)
            if want and not any(same(want, g) for g in got):
                rows.append((heading, cell))
    return missing, tableless, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wiki", default="wiki")
    ap.add_argument("--templates", default=TEMPLATES)
    args = ap.parse_args()

    if not os.path.isdir(args.wiki):
        print(f"  no vault at {args.wiki!r} — nothing to compare.")
        return 0
    pages = [f for f in os.listdir(args.wiki) if f.endswith(".md")]
    if not pages:
        print(f"  {args.wiki}/ has no pages yet. Run /career-init first — this checks a "
              f"vault that exists\n  against the templates it was built from, and an empty "
              f"vault is not out of date.")
        return 0

    checked, missing_n, tableless_n, rows_n, absent = 0, 0, 0, 0, []
    for name in sorted(os.listdir(args.templates)):
        if name in SKIP or not name.endswith(".md"):
            continue
        page = os.path.join(args.wiki, name)
        if not os.path.exists(page):
            absent.append(name)
            continue
        checked += 1
        with open(os.path.join(args.templates, name), encoding="utf-8") as fh:
            tpl = fh.read()
        with open(page, encoding="utf-8") as fh:
            got = fh.read()
        missing, tableless, rows = compare(tpl, got)
        if missing or tableless or rows:
            print(f"\n  {page}")
            for h in missing:
                print(f"    !! section the template has and this page does not: {h}")
            for h in tableless:
                print(f"    ?? section present, but the table under it is not:  {h}")
            for h, cell in rows:
                print(f"    ?? row missing from \"{h}\": {cell}")
        missing_n += len(missing)
        tableless_n += len(tableless)
        rows_n += len(rows)

    if absent:
        print(f"\n  Pages the templates define and this vault has none of: {', '.join(absent)}")

    print(f"\n  {checked} page(s) checked, {missing_n} section(s) missing, "
          f"{tableless_n} table(s) missing, {rows_n} seeded row(s) missing.")
    if missing_n or tableless_n or rows_n or absent:
        print("\n  These are NOT errors. The tool moved on and the vault did not, which is what\n"
              "  happens to every vault eventually. Add them where they belong — the agent owns\n"
              "  these pages, and a section carries content that a script cannot place for it.")
    else:
        print("  Nothing missing. That means the STRUCTURE matches; it does not mean a section's\n"
              "  contents are current.")
    return 1 if (missing_n or tableless_n or rows_n or absent) else 0


if __name__ == "__main__":
    sys.exit(main())
