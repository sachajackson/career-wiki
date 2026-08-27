#!/usr/bin/env python3
"""Fetch a posting from the EMPLOYER's own site and archive it.

    python3 tools/radar/archive_posting.py <careers URL> [<careers URL> ...]

WHY THIS IS NOT refresh.py

`refresh.py` re-READS an archive and says what changed. 🔴 **It never writes,
deliberately** — an archived posting is evidence of what an assessment was
actually based on, and overwriting it with today's text destroys that.

🔴 This is the other half, and its absence cost a week. A requisition number, a
street address and a posting date were read off JPMorgan's own site on
2026-08-18, used to score a role, printed on a CV and a covering letter, and
**never written down anywhere.** By the time anything looked, `raw.json` had been
regenerated and the facts existed in exactly one place: a role page that cited a
source nobody could open. Every one of them turned out to be right, which is not
the point — **nothing could establish that at the moment it mattered.**

🟢 Runbook step 7 is *archive the posting text*. This is the command for it when
the employer runs Oracle Cloud Recruiting, which is most large enterprises.

WHAT IT REFUSES TO DO

**It will not overwrite an existing archive.** Same doctrine as `refresh.py`: a
later fetch can return an edited posting or a 404 page, and replacing evidence
with nothing is worse than having none. Delete the file by hand if you mean it.

WHY THE EMPLOYER'S COPY IS WORTH THE TROUBLE

An aggregator gives you its own guess at the posting date and nothing else. The
employer's record carries **the requisition id, the exact posted date, and the
street address of the work location** — and on the first role this was run
against, the employer's date was 17 July where LinkedIn said 8 August. **41 days
old rather than 19**, which is the single best ghost-job signal there is.
"""
import argparse
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import paths  # noqa: E402
from adapters import oracle  # noqa: E402

# https://<host>/hcmUI/CandidateExperience/en/sites/<site>/job/<id>/
ORACLE_URL = re.compile(r"https?://([^/]+)/hcmUI/CandidateExperience/[^/]+/sites/([^/]+)/job/(\d+)")
SAFE = re.compile(r"[^A-Za-z0-9 &.,()'-]+")


def _safe(name):
    return SAFE.sub(" ", name).strip()[:90]


def fetch(host, site, jid):
    """The employer's own record for one requisition, or None."""
    finder = oracle._finder(f'ById;Id="{jid}",siteNumber="{site}"')
    data = oracle.get_json(oracle.DETAIL.format(host=host, finder=finder))
    items = (data or {}).get("items") or []
    return items[0] if items else None


def render(item, url, jid, today):
    body = oracle._strip(item.get("ExternalDescriptionStr") or "")
    corp = oracle._strip(item.get("CorporateDescriptionStr") or "")
    loc = (item.get("workLocation") or [{}])[0]
    where = ", ".join(x for x in (loc.get("AddressLine1"), loc.get("TownOrCity"),
                                  loc.get("PostalCode")) if x) or item.get("PrimaryLocation", "")
    posted = str(item.get("ExternalPostedStartDate") or "")[:10] or "not stated"
    head = [f"{item.get('Title', 'Untitled')}",
            f"Archived {today} from the employer's own Oracle Recruiting site",
            f"Posted   {posted}",
            f"Location {where}"]
    if loc.get("LocationName"):
        head.append(f"Site     {loc['LocationName']}")
    head += [f"Job ID   {jid}",
             f"Category {item.get('Category', '')}",
             "Pay      not stated",
             f"Source   {url}",
             "Legitimacy: this IS the employer's own site, not an aggregator. The posted date and the",
             "address are the employer's own fields rather than a board's guess.",
             "=" * 72, ""]
    out = "\n".join(head) + "\n" + body
    if corp:
        out += "\n\n--- Corporate description ---\n\n" + corp
    return out + "\n", posted, where


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("urls", nargs="+", help="employer careers URLs")
    ap.add_argument("--employer", help="name for the archive filename; taken from the host otherwise")
    args = ap.parse_args()
    today = datetime.date.today().isoformat()
    os.makedirs(paths.POSTINGS, exist_ok=True)
    failed = 0

    for url in args.urls:
        m = ORACLE_URL.search(url)
        if not m:
            print(f"  🔴 not an Oracle careers URL, skipped: {url[:70]}")
            failed += 1
            continue
        host, site, jid = m.groups()
        employer = args.employer or host.split(".")[0].upper()
        item = fetch(host, site, jid)
        if not item:
            # 🔴 A closed or withdrawn requisition returns no items. That is a
            # finding about the role, not an error -- say so rather than exiting.
            print(f"  🔴 {jid}: the employer returned nothing. Withdrawn, filled, or the id is wrong")
            failed += 1
            continue
        text, posted, where = render(item, url, jid, today)
        name = f"{employer} - {_safe(item.get('Title', jid))} (employer site, req {jid}).txt"
        dest = os.path.join(paths.POSTINGS, name)
        if os.path.exists(dest):
            print(f"  🟡 already archived, left alone: {name[:64]}")
            continue
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(text)
        age = ""
        try:
            age = f"  ({(datetime.date.today() - datetime.date.fromisoformat(posted)).days} days old)"
        except ValueError:
            pass
        print(f"  🟢 {item.get('Title', '')[:46]:46} posted {posted}{age}")
        print(f"     {where[:70]}")
        print(f"     -> {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
