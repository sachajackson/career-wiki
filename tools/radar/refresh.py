#!/usr/bin/env python3
"""Re-read one archived posting and say what has changed since it was assessed.

    python3 tools/radar/refresh.py wiki/postings/"<file>.txt"
    python3 tools/radar/refresh.py --all wiki/postings

WHY THIS AND NOT A CHEAPER RADAR LOOP. The radar was already bounded to the
delta and nobody had measured it: seen.json is consulted at fetch time, so a
role found last week never reaches the description fetch again. Run the radar
twice against the same board and the second run reads zero descriptions --
measured, not argued.

So the failure here is the OTHER one: nothing is ever re-read. A description
changes after posting -- a band added, a requirement softened, the role quietly
withdrawn -- and none of that is ever noticed. Cheap pass over everything,
expensive pass over what the user is about to act on. This is the expensive
pass, and it is invoked deliberately rather than run on a schedule, which is
what keeps it bounded.

THE SECOND REASON, WHICH IS STRONGER THAN THE FIRST. A listing censors the
posting date and the detail endpoint does not. One real posting's listing said
"Posted 30+ Days Ago" while its detail gave a start date 78 days back. Age is
the single best ghost-job predictor, so re-reading buys the one signal the
shortlist could not see.

IT NEVER WRITES TO THE ARCHIVE. An archived posting is evidence of what was read
at the time. Overwriting it with today's text would destroy the only record of
what the assessment was actually based on -- and a later fetch can return an
edited posting or a 404 page, which would replace the evidence with nothing.
"""
import argparse, datetime, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adapters import oracle, workday                             # noqa: E402
from adapters._http import get_json                              # noqa: E402
import legitimacy as LEGIT                                       # noqa: E402

# Public posting URLs, back into the coordinates an adapter needs. Order matters:
# the shared-host Workday form also matches the per-tenant pattern.
WD_SHARED = re.compile(r"^https://([^/]+)/recruiting/([^/]+)/([^/]+)(/job/.+)$")
ORACLE = re.compile(r"^https://([^/]+)/hcmUI/CandidateExperience/[^/]+/sites/([^/]+)/job/([^/?#]+)")
WD_TENANT = re.compile(r"^https://(([^./]+)\.[^/]+)/([^/]+)(/job/.+)$")

MONEY = re.compile(r"(€|£|\$)\s?\d[\d,.]*\s?k?", re.I)


def coords(url):
    """-> (ats, row) an adapter can re-read, or (None, why)."""
    m = WD_SHARED.match(url or "")
    if m:
        return "workday", {"_wd": [m.group(1), m.group(2), m.group(3), m.group(4)]}
    m = ORACLE.match(url or "")
    if m:
        return "oracle", {"_or": [m.group(1), m.group(2), m.group(3)]}
    m = WD_TENANT.match(url or "")
    if m:
        return "workday", {"_wd": [m.group(1), m.group(2), m.group(3), m.group(4)]}
    return None, "not an employer ATS URL this can re-read (aggregator, or an ATS with no adapter)"


def requisition(url):
    """The requisition number, off the URL. Both ATSs put it there.

    Workday ends a job path with the requisition, in three shapes seen live:
    _R-000000, _R000000, and _R000000-1 where one requisition is posted in two
    places. Oracle's job id IS the requisition.
    """
    m = ORACLE.match(url or "")
    if m:
        return m.group(3)
    m = re.search(r"_([A-Za-z]*-?\d[\w-]*)$", url or "")
    return m.group(1) if m else ""


def parse_archive(text):
    """The header archive() writes, back into fields."""
    head, _, body = text.partition("=" * 72)
    out = {"body": body.strip()}
    for key, field in (("Posted", "date"), ("Source", "url"), ("Archived", "archived")):
        m = re.search(rf"^{key}\s+(.+)$", head, re.M)
        if m:
            out[field] = m.group(1).strip()
    if out.get("archived"):
        out["archived"] = out["archived"].split()[0]
    if out.get("date"):
        out["date"] = out["date"].split()[0]
    return out


def live(ats, row):
    """-> (body, posted_iso). Empty body means the posting could not be read."""
    if ats == "workday":
        host, tenant, site, path = row["_wd"]
        info = workday._detail(host, tenant, site, path)
        return workday._strip(info.get("jobDescription")), str(info.get("startDate") or "")[:10]
    host, site, jid = row["_or"]
    body = oracle.fetch_body(row)
    f = oracle._finder(f'ById;Id="{jid}",siteNumber="{site}"')
    d = get_json(oracle.DETAIL.format(host=host, finder=f)) or {}
    items = d.get("items") or [{}]
    return body, str(items[0].get("ExternalPostedStartDate") or "")[:10]


def norm(t):
    return re.sub(r"\s+", " ", (t or "")).strip()


def compare(archived, now_body, now_date):
    """What changed, in the terms someone about to apply would care about."""
    notes = []
    if not now_body:
        return ["🔴 GONE — the posting could not be read. It may have been filled, "
                "withdrawn, or moved. Do not apply from the archived copy without checking"]
    a, b = norm(archived.get("body")), norm(now_body)
    if a != b:
        delta = len(b) - len(a)
        notes.append(f"CHANGED — the description differs ({delta:+d} characters)")
        had, has = bool(MONEY.search(a)), bool(MONEY.search(b))
        if has and not had:
            notes.append("🟢 a salary figure has appeared that was not there when this was assessed")
        elif had and not has:
            notes.append("🟡 a salary figure that was there when this was assessed has gone")
    else:
        notes.append("unchanged since it was archived")

    was = archived.get("date")
    if now_date and was and now_date != was:
        try:
            older = datetime.date.fromisoformat(now_date) < datetime.date.fromisoformat(was)
        except ValueError:
            older = False
        notes.append(f"🔴 POSTED {now_date}, not {was} — {'older than' if older else 'different from'} "
                     f"what the listing said. Listings censor the date; the detail endpoint does not"
                     if older else f"posting date now reads {now_date}, was {was}")
    return notes


def refresh(path):
    with open(path, encoding="utf-8") as fh:
        arch = parse_archive(fh.read())
    ats, row = coords(arch.get("url"))
    name = os.path.basename(path)
    if ats is None:
        return name, ["-- " + row]
    body, posted = live(ats, row)
    notes = compare(arch, body, posted)
    if body:
        # Recomputed against the date the DETAIL gave, which is the whole point:
        # the concern that matters is the one true now, and the listing's date
        # was the censored one. The requisition comes off the URL rather than
        # being faked -- passing a placeholder would silently disable the
        # missing-requisition check and report a clean result it never ran.
        notes += ["legitimacy now: " + "; ".join(
            LEGIT.concerns({"date": posted or arch.get("date"), "source": ats,
                            "requisition": requisition(arch.get("url")),
                            "date_is_floor": False}) or ["nothing flagged"])]
    return name, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", help="an archived posting, or a directory with --all")
    ap.add_argument("--all", action="store_true", help="re-read every posting in a directory")
    args = ap.parse_args()

    paths = ([os.path.join(args.target, f) for f in sorted(os.listdir(args.target))
              if f.endswith(".txt")] if args.all else [args.target])
    if not paths:
        print("  nothing to re-read.")
        return 0
    changed = 0
    for p in paths:
        name, notes = refresh(p)
        print(f"\n  {name}")
        for n in notes:
            print(f"    {n}")
        if any(w in n for n in notes for w in ("GONE", "CHANGED", "POSTED")):
            changed += 1
    print(f"\n  {len(paths)} re-read, {changed} with something to look at.")
    print("  The archive is NOT updated. It is evidence of what the assessment was based on,\n"
          "  and today's text is a different document.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
