#!/usr/bin/env python3
"""verify -- the deterministic layer. Checks an outgoing document against the wiki.

    python3 tools/verify.py "applications/Acme R123/cv.txt" --wiki wiki
    pdftotext -layout cv.pdf - | python3 tools/verify.py - --wiki wiki --ban react,graphql

WHY THIS EXISTS

Everything else in this repo is probabilistic. A model wrote the CV, and a model
checking a model shares its failure modes -- if it hallucinated a number while
writing, it will find that number plausible while reviewing.

So the last check on the way out is not a model. It is arithmetic and string
matching against the wiki, which is the source of truth. It cannot judge whether
a bullet is any good. It can prove that every number in the document exists in
the wiki, sits on the same employer it sits on in the wiki, and has been
confirmed by a human. That is the class of error that survives review and gets
found in an interview instead.

WHAT IT CANNOT DO

Judgement. Tone, angle, whether the CV answers the posting, whether a bullet is
worth its space. Use the audit prompt and a human for those. A clean run here
means "nothing provably wrong", not "good".

Exit status is 1 if anything is flagged, so it can gate a build.
"""
import argparse, os, re, sys, glob, datetime
from collections import defaultdict

# A number worth tracing: percentages, money, counts of 3+ digits or with
# separators, before-and-after ranges, and multipliers. Deliberately ignores
# small bare integers -- "3 teams" is not a provenance risk.
NUM = re.compile(r"""
    (?:[€£$]\s?\d[\d,.]*\s?[kKmM]?)      | # money
    (?:\d[\d,]*\s?%)                     | # percentage
    (?:\d+\s?-\s?\d+)                    | # range, e.g. 50-70
    (?:\d+(?:\.\d+)?\s?[xX]\b)           | # multiplier
    (?:\d{1,3}(?:,\d{3})+)               | # 1,200 / 50,000
    (?:\b\d{3,}\b)                         # 240, 20000
""", re.X)

YEARS = re.compile(r"\b(19|20)\d{2}\b")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def norm(n):
    """50,000 / 50000 / 50k all compare equal."""
    s = n.lower().replace(",", "").replace(" ", "").lstrip("€£$")
    m = re.match(r"^(\d+(?:\.\d+)?)k$", s)
    if m:
        return str(int(float(m.group(1)) * 1000))
    s = s.rstrip("%x")
    return s.rstrip(".0") if "." in s else s


def parse_frontmatter(text):
    m = FRONTMATTER.match(text)
    if not m:
        return {}, text
    fm, body = m.group(1), text[m.end():]
    out = {"verified": "verified:" in fm, "status": None, "stale_after": None, "employer": None,
           "type": None, "title": None, "exclude": False}
    for k in ("type", "title"):
        m2 = re.search(rf"^{k}:\s*(.+?)\s*$", fm, re.M)
        if m2:
            out[k] = m2.group(1).strip().strip('"\'')
    if re.search(r"^exclude_from_cv:\s*true", fm, re.M | re.I):
        out["exclude"] = True
    e = re.search(r"^employer:\s*(.+?)\s*$", fm, re.M)
    if e:
        out["employer"] = e.group(1).strip().strip('"\'')
    s = re.search(r"^status:\s*(\S+)", fm, re.M)
    if s:
        out["status"] = s.group(1)
    d = re.search(r"^stale_after:\s*([\d-]+)", fm, re.M)
    if d:
        out["stale_after"] = d.group(1)
    return out, body


def load_wiki(wiki_dir, employers):
    """Returns (figure index, page records). A page record is what --coverage reads."""
    index = defaultdict(list)
    records = []
    pages = 0
    for path in glob.glob(os.path.join(wiki_dir, "**", "*.md"), recursive=True):
        if os.path.basename(path) in ("log.md", "index.md"):
            continue
        try:
            raw = open(path, encoding="utf-8").read()
        except Exception:
            continue
        pages += 1
        fm, body = parse_frontmatter(raw)
        lines = body.splitlines()
        for i, line in enumerate(lines):
            for m in NUM.finditer(line):
                index[norm(m.group(0))].append({
                    "page": os.path.relpath(path, wiki_dir),
                    "verified": fm.get("verified", False),
                    "stale_after": fm.get("stale_after"),
                    # Explicit only. Proximity in prose was tried and produced
                    # confident nonsense: a discursive page mentions four
                    # employers within six lines of any number, so every
                    # attribution "passed". Silence beats a false pass.
                    "employer": fm.get("employer"),
                })
        figs = [m.group(0) for line in lines for m in NUM.finditer(line)
                if not YEARS.fullmatch(m.group(0).strip())]
        if figs or fm.get("type") == "achievement":
            records.append({
                "page": os.path.relpath(path, wiki_dir),
                "title": fm.get("title") or os.path.basename(path)[:-3],
                "type": fm.get("type"),
                "employer": fm.get("employer"),
                "verified": fm.get("verified", False),
                "stale_after": fm.get("stale_after"),
                "exclude": fm.get("exclude", False),
                "figures": figs,
            })
    return index, pages, records


def employers_from_list(arg):
    """Employers come from the caller, never from guessing.

    An earlier version inferred company names from the wiki with a regex and
    produced 'Cross', 'Hands' and 'Per' alongside the real ones, which made the
    attribution check worse than useless -- it fired on noise and stayed silent
    on the case it exists for. A deterministic layer that guesses is not a
    deterministic layer. If the list is not supplied, the check is skipped and
    says so.
    """
    return [e.strip() for e in arg.split(",") if e.strip()] if arg else []


def sections(doc_text, employers):
    """Split the outgoing document into (employer_context, text) blocks."""
    lines = doc_text.splitlines()
    marks = []
    for i, line in enumerate(lines):
        hit = [e for e in employers if e.lower() in line.lower()]
        if hit and len(line) < 160:
            marks.append((i, hit[0]))
    if not marks:
        return [(None, doc_text)]
    out = []
    for idx, (start, emp) in enumerate(marks):
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(lines)
        out.append((emp, "\n".join(lines[start:end])))
    if marks[0][0] > 0:
        out.insert(0, (None, "\n".join(lines[:marks[0][0]])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("document", help="outgoing text, or - for stdin")
    ap.add_argument("--wiki", default="wiki")
    ap.add_argument("--ban", default="", help="comma-separated terms that must not appear")
    ap.add_argument("--spelling", choices=["uk", "us"], help="employer's convention for program(me)")
    ap.add_argument("--coverage", action="store_true",
                    help="also list wiki achievements absent from this document. Not errors -- a "
                         "two-page CV cannot carry everything. It asks whether the omission was a "
                         "decision or an oversight")
    ap.add_argument("--employer", help="employer this application is for")
    ap.add_argument("--employers", default="",
                    help="comma-separated list of the applicant's past employers, exactly as they "
                         "appear in the wiki. Required for the attribution check")
    args = ap.parse_args()

    doc = sys.stdin.read() if args.document == "-" else open(args.document, encoding="utf-8").read()
    if not os.path.isdir(args.wiki):
        sys.exit(f"no wiki at {args.wiki}")

    employers = employers_from_list(args.employers)
    index, pages, records = load_wiki(args.wiki, employers)
    any_verified = any(h["verified"] for hits in index.values() for h in hits)
    any_employer = any(h["employer"] for hits in index.values() for h in hits)
    today = datetime.date.today().isoformat()
    F = []                                    # (severity, message)

    # ---- 1. provenance, attribution, verification -------------------------
    for emp, block in sections(doc, employers):
        for m in NUM.finditer(block):
            raw, key = m.group(0), norm(m.group(0))
            if YEARS.fullmatch(raw.strip()):
                continue
            hits = index.get(key, [])
            if not hits:
                F.append(("UNSOURCED", f"{raw!r} appears in the document but nowhere in the wiki"))
                continue
            if any_verified and not any(h["verified"] for h in hits):
                F.append(("UNVERIFIED", f"{raw!r} is in the wiki but no page carrying it is human-verified "
                                        f"({hits[0]['page']})"))
            owners = {h["employer"] for h in hits if h["employer"]}
            if emp and owners and emp not in owners:
                F.append(("ATTRIBUTION", f"{raw!r} sits under {emp!r} in this document, but the wiki "
                                         f"attributes it to {sorted(owners)}"))
            for h in hits:
                if h["stale_after"] and h["stale_after"] < today:
                    F.append(("STALE", f"{raw!r} traces to {h['page']}, whose stale_after "
                                       f"({h['stale_after']}) has passed"))
                    break

    # ---- 2. per-application do-not list -----------------------------------
    for term in [t.strip().lower() for t in args.ban.split(",") if t.strip()]:
        if re.search(r"\b" + re.escape(term) + r"\b", doc, re.I):
            F.append(("BANNED", f"{term!r} appears, but it is on this application's do-not list"))

    # ---- 3. employer spelling ---------------------------------------------
    if args.spelling == "us" and re.search(r"\bprogramme", doc, re.I):
        F.append(("SPELLING", "'programme' appears, but this employer uses US spelling"))
    if args.spelling == "uk" and re.search(r"\bprogram\b", doc, re.I):
        F.append(("SPELLING", "'program' appears, but this employer uses UK spelling"))

    # ---- 4. wrong employer named ------------------------------------------
    if args.employer:
        if args.employer.lower() not in doc.lower():
            F.append(("EMPLOYER", f"{args.employer!r} is not named anywhere in this document"))
        for other in employers:
            if other.lower() != args.employer.lower() and re.search(
                    r"(join|joining|work(ing)? (for|at)|apply(ing)? to)\s+" + re.escape(other), doc, re.I):
                F.append(("EMPLOYER", f"reads as addressed to {other!r}, not {args.employer!r}"))

    # ---- 5. contact block --------------------------------------------------
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", doc):
        F.append(("CONTACT", "no email address found"))
    if re.search(r"linkedin\.com", doc, re.I) and not re.search(r"https?://(www\.)?linkedin\.com", doc, re.I):
        F.append(("CONTACT", "LinkedIn appears without a full https:// URL; some forms reject a bare handle"))

    # ---- report ------------------------------------------------------------
    order = ["UNSOURCED", "ATTRIBUTION", "BANNED", "EMPLOYER", "UNVERIFIED", "STALE", "SPELLING", "CONTACT"]
    F.sort(key=lambda x: order.index(x[0]) if x[0] in order else 99)
    seen, uniq = set(), []
    for sev, msg in F:
        if (sev, msg) not in seen:
            seen.add((sev, msg)); uniq.append((sev, msg))

    print(f"verify: {len(uniq)} finding(s) against {pages} wiki pages, "
          f"{len(index)} distinct figures indexed\n")
    if not employers:
        print("  [SKIPPED] attribution -- pass --employers so the document can be split by role.\n")
    elif not any_employer:
        print("  [SKIPPED] attribution -- no wiki page carries an `employer:` field, so there is\n"
              "            nothing to check a figure's owner against. Add `employer:` to the\n"
              "            frontmatter of pages that carry a number. THIS IS THE CHECK THAT\n"
              "            CATCHES A FIGURE ATTACHED TO THE WRONG ROLE, and it is off.\n")
    if not any_verified:
        print("  [SKIPPED] verification -- no page in this wiki carries a `verified:` field, so\n"
              "            human-confirmed and inferred claims cannot be told apart.\n")
    for sev, msg in uniq:
        print(f"  [{sev}] {msg}")
    if not uniq:
        print("  nothing provably wrong.")
    if args.coverage:
        doc_figs = {norm(m.group(0)) for m in NUM.finditer(doc)}
        missing = []
        for r in records:
            if r["exclude"] or r["stale_after"] and r["stale_after"] < today:
                continue
            if r["figures"] and any(norm(f) in doc_figs for f in r["figures"]):
                continue
            if not r["figures"] and r["type"] != "achievement":
                continue
            score = (2 if r["verified"] else 0) + (1 if r["figures"] else 0)
            missing.append((score, r))
        missing.sort(key=lambda x: -x[0])
        excluded = [r for r in records if r["exclude"]]
        print("\n" + "-" * 78)
        print(f"COVERAGE -- {len(missing)} wiki item(s) not represented in this document\n")
        if not missing:
            print("  every eligible achievement in the wiki appears here.")
        for score, r in missing[:20]:
            mark = "verified" if r["verified"] else "unverified"
            emp = f", {r['employer']}" if r["employer"] else ""
            figs = f"  [{', '.join(r['figures'][:3])}]" if r["figures"] else ""
            print(f"  - {r['title']} ({mark}{emp}){figs}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
        if excluded:
            print(f"\n  {len(excluded)} page(s) skipped as exclude_from_cv. Those stay excluded.")
        print("\n  These are NOT findings. A two-page CV cannot carry everything, and leaving\n"
              "  something out is usually correct. The question is whether each omission was a\n"
              "  decision or an oversight -- the second kind is how good material stays invisible\n"
              "  for years. Coverage does not affect the exit status.")

    print("\nDeterministic checks only. This proves nothing about whether the document is any"
          "\ngood -- only that its figures trace to the wiki, sit on the right employer, and"
          "\nhave been confirmed by a human. Judgement is still a separate pass.")
    sys.exit(1 if uniq else 0)


if __name__ == "__main__":
    main()
