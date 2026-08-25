"""Workday CXS — the endpoint behind a large share of enterprise careers sites.

Public, no key, returns JSON. Many big employers front Workday on their own
domain, so a careers page that looks bespoke is often this API underneath.

Verified against two live tenants on 2026-08-25, one of each hosting style.
Every field read is still guarded, because a tenant that returns a shape this
has not seen should yield a thin row, not a traceback that kills the run.

The live run found two things a recorded fixture could not have: the public URL
differs between the two hosting styles, and descriptions arrive with their HTML
entities intact. Both are pinned by tests now.

TWO HOSTING STYLES, AND AN ADAPTER THAT ASSUMES ONE SILENTLY MISSES EMPLOYERS:

    POST https://<tenant>.wd1.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs
    POST https://wd1.myworkdaysite.com/wday/cxs/<tenant>/<site>/jobs

Same API either way, which is why host, tenant and site are three separate
config inputs. Deriving the host from the tenant covers the first style and
loses the second, and loses it quietly -- the employer simply never appears.

THE SHARD NUMBER VARIES. wd1, wd3, wd5. A 422 means the tenant is on a
different shard, NOT that the request is malformed, and this adapter says so
rather than reporting a generic failure.

WHAT THE LISTING HIDES. A posting open in four cities is advertised as one, and
the listing writes "4 Locations" where the city should be. That matters here
more than anywhere else, because the runner filters on location BEFORE it reads
any description -- so a role that is open in the user's city, advertised under a
city they have excluded, is dropped and never looked at again. When the listing
says it is hiding locations, this fetches the detail and expands them.
"""
import datetime, html, re, time
from ._http import get_json, post_json

NAME = "workday"
TRUNCATED = False
HONOURS_DAYS = False   # no recency parameter: returns everything currently open

LIST   = "https://{host}/wday/cxs/{tenant}/{site}/jobs"
DETAIL = "https://{host}/wday/cxs/{tenant}/{site}{path}"
# The public URL differs by hosting style, and this was got wrong until a live
# run caught it. Verified against one employer of each style:
#   per-tenant   https://<tenant>.wd1.myworkdayjobs.com/<site>/job/...
#   shared host  https://wd1.myworkdaysite.com/recruiting/<tenant>/<site>/job/...
# The detail response carries the authoritative externalUrl, so where the detail
# is fetched at all that is used in preference to either of these.
PUBLIC_TENANT = "https://{host}/{site}{path}"
PUBLIC_SHARED = "https://{host}/recruiting/{tenant}/{site}{path}"

PAGE = 20              # the API's own per-request ceiling
HIDDEN = re.compile(r"^\s*(\d+)\s+locations?\b|\band\s+(\d+)\s+more\b", re.I)
AGO = re.compile(r"posted\s+(\d+)\+?\s+days?\s+ago", re.I)
TODAY = re.compile(r"posted\s+(today|yesterday)", re.I)


def _date(posted_on):
    """Turn "Posted 5 Days Ago" into a date. Returns (iso, is_floor).

    Workday writes "Posted 30+ Days Ago" for anything older than a month, so the
    date derived from it is a FLOOR, not the posting date -- a role six months
    old and one exactly thirty days old produce the same string. The caller
    keeps the raw text alongside, because a date that looks exact and is not is
    the aggregator re-dating problem in a new coat.
    """
    if not posted_on:
        return "", False
    t = TODAY.search(posted_on)
    if t:
        d = 0 if t.group(1).lower() == "today" else 1
        return (datetime.date.today() - datetime.timedelta(days=d)).isoformat(), False
    a = AGO.search(posted_on)
    if a:
        floor = "+" in posted_on
        return ((datetime.date.today() - datetime.timedelta(days=int(a.group(1)))).isoformat(),
                floor)
    return "", False


def _strip(markup):
    """Tags out, then entities. A description arrives holding &amp; and &nbsp;."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup or ""))).strip()


def _public(host, tenant, site, path):
    tmpl = PUBLIC_TENANT if host.lower().startswith(tenant.lower() + ".") else PUBLIC_SHARED
    return tmpl.format(host=host, tenant=tenant, site=site, path=path)


def _detail(host, tenant, site, path):
    d = get_json(DETAIL.format(host=host, tenant=tenant, site=site, path=path))
    return (d or {}).get("jobPostingInfo") or {}


def fetch(cfg, query, days):
    """`days` is ignored -- see HONOURS_DAYS. Workday has no recency filter.

    It does have a real server-side search, so unlike a plain board adapter the
    query is used rather than thrown away.
    """
    global TRUNCATED
    TRUNCATED = False
    w = cfg.get("workday", {})
    employers = w.get("employers", [])
    if not employers:
        return []
    pages = int(w.get("pages", 5))
    delay = float(w.get("delay", 0.3))
    out = []

    for e in employers:
        host, tenant, site = e.get("host"), e.get("tenant"), e.get("site")
        if not (host and tenant and site):
            print(f"  !! workday: an employer entry needs host, tenant and site "
                  f"(got {e!r}) -- skipped", flush=True)
            continue
        url = LIST.format(host=host, tenant=tenant, site=site)
        got, total = 0, None

        for page in range(pages):
            data, status = post_json(url, {"appliedFacets": {}, "limit": PAGE,
                                           "offset": page * PAGE, "searchText": query})
            if data is None:
                TRUNCATED = True
                if status == 422:
                    print(f"  !! workday {tenant}: 422 -- the tenant is probably on a "
                          f"different wd shard. Try wd3/wd5 in host, not a new request.",
                          flush=True)
                elif status:
                    print(f"  !! workday {tenant}: HTTP {status}", flush=True)
                break

            if total is None:
                total = data.get("total")
            rows = data.get("jobPostings") or []
            if not rows:
                break

            for j in rows:
                path = j.get("externalPath") or ""
                loc = (j.get("locationsText") or "").strip()
                posted = j.get("postedOn") or ""
                date, floor = _date(posted)
                # bulletFields is where Workday puts the requisition number --
                # the thing an application folder has to be named for and that
                # no aggregator carries.
                req = next((b for b in (j.get("bulletFields") or []) if b), "")
                body, url = "", _public(host, tenant, site, path)

                # Only pay for the detail call when the listing admits it is
                # hiding something. Expanding every posting would triple the
                # request count for a field most of them do not have.
                if path and HIDDEN.search(loc):
                    info = _detail(host, tenant, site, path)
                    extra = [x for x in (info.get("additionalLocations") or []) if x]
                    primary = info.get("location") or ""
                    if primary or extra:
                        loc = "; ".join([p for p in [primary] + extra if p])
                    body = _strip(info.get("jobDescription"))
                    req = info.get("jobReqId") or info.get("id") or req
                    if info.get("startDate"):
                        date, floor = str(info["startDate"])[:10], False
                    # The employer's own link, rather than one this reconstructed.
                    url = info.get("externalUrl") or url
                    time.sleep(delay)

                out.append({
                    "id": f"wd-{tenant}-{req or path.rsplit('_', 1)[-1] or len(out)}",
                    "title": (j.get("title") or "").strip(),
                    "company": w.get("names", {}).get(tenant, tenant),
                    "loc": loc or "?",
                    "date": date,
                    "url": url,
                    "body": body,
                    "pay": "",
                    "source": NAME,
                    # Kept so nothing downstream has to trust a derived date, and
                    # so the requisition survives into the role page.
                    "requisition": req,
                    "posted_text": posted,
                    "date_is_floor": floor,
                    "_wd": [host, tenant, site, path],
                })
                got += 1

            time.sleep(delay)
            if total is not None and (page + 1) * PAGE >= total:
                break

        # One place, and not a guess: Workday returns the true total, so a gap
        # between what was asked for and what exists IS the cap being the
        # constraint. Whether the loop ended on budget or on an empty page is
        # not a distinction worth two branches -- it was tried, and the second
        # branch made a test pass while testing nothing.
        if total is not None and got < total:
            TRUNCATED = True

    return out


def fetch_body(row):
    """Descriptions are not in the listing; one extra call each.

    Takes the whole row rather than an id because a Workday posting is addressed
    by four values, and smuggling a URL through an id field to get round that is
    how an id stops being an id.
    """
    wd = (row or {}).get("_wd")
    if not wd:
        return ""
    host, tenant, site, path = wd
    return _strip(_detail(host, tenant, site, path).get("jobDescription"))
