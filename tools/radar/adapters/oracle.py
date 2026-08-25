"""Oracle Cloud Recruiting (CX) — the other large enterprise ATS.

Public JSON, no key. Verified against three live tenants on 2026-08-25.

TWO VALUES, AND BOTH ARE IN THE CAREERS URL:

    https://<host>/hcmUI/CandidateExperience/en/sites/<site>/jobs

Unlike Workday this needs no third value. The site segment of that URL works
directly as the API's siteNumber -- confirmed against a numbered site and two
named ones. The host is taken verbatim and NOT derived: tenants appear
both with a region (<pod>.fa.us2.oraclecloud.com) and without
(<pod>.fa.oraclecloud.com), and constructing it from a pattern loses one of them.

WHAT THIS SOURCE GIVES THAT OTHERS DO NOT

  PostedDate is a real ISO date, not "30+ days ago". So the posting window is
  applied here exactly rather than approximated, and HONOURS_DAYS is True --
  see the note on it below, because "the adapter filters" and "the API filters"
  are different claims and only one of them is true.

  Id is the requisition number as the employer prints it.

  ShortDescriptionStr arrives in the listing, so a failed description fetch
  degrades to something real rather than to nothing.

A NOTE ON THE BACKLOG'S WRITE-UP. It records that the detail finder's values
must be quoted or the request 400s. Unquoted worked on every tenant tried here,
so that is either version-specific or was only ever true of a non-numeric id.
Quoting costs nothing and is kept -- but the claim is softened rather than
repeated, because an instruction nobody can reproduce stops being followed.
"""
import re, time, urllib.parse
from ._http import get_json

NAME = "oracle"
TRUNCATED = False
# True, but read this: the API has no posting-window parameter. What it has is
# an exact PostedDate on every row and a newest-first sort, so the window is
# applied here, precisely, and paging stops at the first row that falls outside
# it. The result is the same as a server-side filter; the mechanism is not, and
# a reader deciding whether to trust the date needs to know which.
HONOURS_DAYS = True

LIST = ("https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
        "?onlyData=true&expand=requisitionList.secondaryLocations&finder={finder}")
DETAIL = ("https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails"
          "?expand=all&finder={finder}")
PUBLIC = "https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{jid}"

PAGE = 25


def _strip(markup):
    import html
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup or ""))).strip()


def _finder(s):
    return urllib.parse.quote(s, safe=';,="')


def _rows(payload):
    """The list response buries the rows two levels down, behind a search object."""
    items = (payload or {}).get("items") or []
    if not items:
        return [], None
    return (items[0].get("requisitionList") or []), items[0].get("TotalJobsCount")


def fetch(cfg, query, days):
    global TRUNCATED
    TRUNCATED = False
    o = cfg.get("oracle", {})
    employers = o.get("employers", [])
    if not employers:
        return []
    pages = int(o.get("pages", 5))
    delay = float(o.get("delay", 0.3))
    cutoff = None
    if days is not None:
        import datetime
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    out = []

    for e in employers:
        host, site = e.get("host"), e.get("site")
        if not (host and site):
            print(f"  !! oracle: an employer entry needs host and site (got {e!r}) -- skipped",
                  flush=True)
            continue
        got, total, ran_out_of_window = 0, None, False

        for page in range(pages):
            f = f"findReqs;siteNumber={site},limit={PAGE},offset={page * PAGE}," \
                f"sortBy=POSTING_DATES_DESC"
            if query:
                f += f',keyword="{query}"'
            data = get_json(LIST.format(host=host, finder=_finder(f)))
            if data is None:
                TRUNCATED = True
                print(f"  !! oracle {site}: request failed", flush=True)
                break
            rows, count = _rows(data)
            if total is None:
                total = count
            if not rows:
                break

            for r in rows:
                posted = str(r.get("PostedDate") or "")[:10]
                # Newest first, so the first row outside the window means every
                # row after it is too. Stopping here is completeness, not a cap.
                if cutoff and posted and posted < cutoff:
                    ran_out_of_window = True
                    break
                loc = r.get("PrimaryLocation") or ""
                extra = [x.get("Name") for x in (r.get("secondaryLocations") or []) if x.get("Name")]
                jid = str(r.get("Id") or "")
                out.append({
                    "id": f"or-{site}-{jid}",
                    "title": (r.get("Title") or "").strip(),
                    "company": o.get("names", {}).get(site, site),
                    "loc": "; ".join([p for p in [loc] + extra if p]) or "?",
                    "date": posted,
                    "url": PUBLIC.format(host=host, site=site, jid=jid),
                    # Left empty on purpose so the runner fetches the full text.
                    # Tiering on the short description would systematically
                    # under-score this source against ones that give full text,
                    # which is the same defect as a term only some inputs earn.
                    "body": "",
                    "pay": "",
                    "source": NAME,
                    "requisition": jid,
                    "_short": _strip(r.get("ShortDescriptionStr")),
                    "_or": [host, site, jid],
                })
                got += 1

            if ran_out_of_window:
                break
            time.sleep(delay)
            if total is not None and (page + 1) * PAGE >= total:
                break

        # A window that ran out is a complete answer for that window. A page
        # budget that ran out is not, and only the second is truncation.
        if not ran_out_of_window and total is not None and got < total and cutoff is None:
            TRUNCATED = True
        elif not ran_out_of_window and total is not None and got >= PAGE * pages:
            TRUNCATED = True

    return out


def fetch_body(row):
    """Full description, degrading to the short one the listing already gave.

    Most adapters return "" when the description cannot be fetched, and a role
    then signals low for a reason that has nothing to do with the role. Here
    there is something real to fall back to, so it falls back.
    """
    stash = (row or {}).get("_or")
    if not stash:
        return (row or {}).get("_short", "")
    host, site, jid = stash
    f = _finder(f'ById;Id="{jid}",siteNumber="{site}"')
    data = get_json(DETAIL.format(host=host, finder=f))
    items = (data or {}).get("items") or []
    full = _strip(items[0].get("ExternalDescriptionStr")) if items else ""
    return full or row.get("_short", "")
