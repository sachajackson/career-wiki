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
from . import _titles, _verdicts as V

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

PAGE = 20              # the API's own per-request ceiling: 50 and 100 both 400
# Safety ceiling on the whole-board read, in pages. 300 is 6,000 roles, which is
# far above any board seen so far -- State Street, the largest, is 1,377. It
# exists so a pathological board cannot run forever, not as a filter, and
# TRUNCATED says so when it bites.
BOARD_PAGES = 300
HIDDEN = re.compile(r"^\s*(\d+)\s+locations?\b|\band\s+(\d+)\s+more\b", re.I)
AGO = re.compile(r"posted\s+(\d+)\+?\s+days?\s+ago", re.I)
# Workday stops counting here. An age of exactly this is a floor whether or not
# the page bothered to print the "+".
DISPLAY_CAP_DAYS = 30
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
        n = int(a.group(1))
        # 30 is Workday's display CEILING, and it does not always print the "+".
        # Verified across two live tenants: 13 distinct "posted" strings, the
        # highest number 30, appearing as bare "Posted 30 Days Ago", and nothing
        # above it. So a "+" is not the signal -- reaching the cap is. Trusting
        # the "+" alone reads a year-old requisition as exactly thirty days old,
        # on the source where age is hardest to see and matters most.
        floor = "+" in posted_on or n >= DISPLAY_CAP_DAYS
        return ((datetime.date.today() - datetime.timedelta(days=n)).isoformat(), floor)
    return "", False


def _strip(markup):
    """Tags out, then entities. A description arrives holding &amp; and &nbsp;."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup or ""))).strip()


def _public(host, tenant, site, path):
    tmpl = PUBLIC_TENANT if host.lower().startswith(tenant.lower() + ".") else PUBLIC_SHARED
    return tmpl.format(host=host, tenant=tenant, site=site, path=path)


def _detail(host, tenant, site, path, delay=0.0):
    d = get_json(DETAIL.format(host=host, tenant=tenant, site=site, path=path), delay=delay)
    return (d or {}).get("jobPostingInfo") or {}


def _board(url, pages, delay):
    """Every posting on one board, once. Returns (rows, truncated).

    🔴 WHY THE WHOLE BOARD, RATHER THAN THE SERVER'S OWN SEARCH

    Workday HAS a real server-side search and this adapter used it for a year.
    Measured on State Street, 2026-08-25: the board holds **1,377 roles, and
    `searchText: "Engineering Manager"` returns 611 of them.** 44% of the board
    for one query, 682 for "Delivery". It is a loose match across several
    fields, ranked -- not a filter.

    So the old shape asked for 41 queries x 5 pages = 205 requests and saw the
    first 100 rows of each 611-row ranked set: **about 7% of the board per
    query, and largely the same highly-ranked rows every time.** That is why a
    run fetched 781 Workday rows and found 27 new ones.

    The whole board is 69 pages. **Fewer requests than the old shape, and it is
    complete rather than a ranked slice** -- and because the request body no
    longer varies by query, the cache in _http serves every query after the
    first without touching the network.

    🟡 WHAT IS GIVEN UP, STATED PLAINLY. The server matched description text;
    `_titles.matches` reads titles only, as it does for every other board
    adapter. A role whose title does not carry the domain word is now dropped
    where Workday might have surfaced it. **Against that, 93% of the board was
    previously never fetched at all**, so this is more coverage and a stricter
    filter, not a trade of like for like.
    """
    rows, truncated, total = [], False, None
    for page in range(pages):
        # The delay is passed to the transport rather than taken here, so a
        # page served from the cache costs nothing. Sleeping after a cache hit
        # is being polite to a server nobody contacted.
        data, status = post_json(url, {"appliedFacets": {}, "limit": PAGE,
                                       "offset": page * PAGE, "searchText": ""},
                                 delay=delay)
        if data is None:
            return rows, True, status
        if total is None:
            total = data.get("total")
        got = data.get("jobPostings") or []
        if not got:
            break
        rows.extend(got)
        if total is not None and len(rows) >= total:
            break
    else:
        truncated = total is None or len(rows) < total
    if total is not None and len(rows) < total:
        truncated = True
    return rows, truncated, None


def fetch(cfg, query, days):
    """`days` is ignored -- see HONOURS_DAYS. Workday has no recency filter.

    The board is read once per run and filtered here. See `_board` for why, and
    for what that costs.
    """
    global TRUNCATED
    TRUNCATED = False
    w = cfg.get("workday", {})
    employers = w.get("employers", [])
    if not employers:
        return []
    # `pages` used to mean pages PER QUERY. Reusing it for the board read would
    # turn the common `pages: 5` into "the first 100 roles of the board" -- a
    # silent 93% loss on State Street, and exactly the kind of quiet regression
    # a renamed meaning causes. So it is ignored here, and said out loud.
    pages = int(w.get("board_pages", BOARD_PAGES))
    delay = float(w.get("delay", 0.3))
    out = []

    for e in employers:
        host, tenant, site = e.get("host"), e.get("tenant"), e.get("site")
        if not (host and tenant and site):
            print(f"  !! workday: an employer entry needs host, tenant and site "
                  f"(got {e!r}) -- skipped", flush=True)
            continue
        url = LIST.format(host=host, tenant=tenant, site=site)
        board, truncated, status = _board(url, pages, delay)
        if truncated:
            TRUNCATED = True
        if status is not None:
            if status == 422:
                print(f"  !! workday {tenant}: 422 -- the tenant is probably on a "
                      f"different wd shard. Try wd3/wd5 in host, not a new request.",
                      flush=True)
            else:
                print(f"  !! workday {tenant}: HTTP {status}", flush=True)

        for j in board:
            if not _titles.matches(query, j.get("title") or ""):
                continue
            path = j.get("externalPath") or ""
            loc = (j.get("locationsText") or "").strip()
            posted = j.get("postedOn") or ""
            date, floor = _date(posted)
            # bulletFields is where Workday puts the requisition number --
            # the thing an application folder has to be named for and that
            # no aggregator carries.
            req = next((b for b in (j.get("bulletFields") or []) if b), "")
            body, url_row = "", _public(host, tenant, site, path)

            # Only pay for the detail call when the listing admits it is
            # hiding something, and only for rows this query actually kept.
            if path and HIDDEN.search(loc):
                info = _detail(host, tenant, site, path, delay)
                extra = [x for x in (info.get("additionalLocations") or []) if x]
                primary = info.get("location") or ""
                if primary or extra:
                    loc = "; ".join([p for p in [primary] + extra if p])
                body = _strip(info.get("jobDescription"))
                req = info.get("jobReqId") or info.get("id") or req
                if info.get("startDate"):
                    date, floor = str(info["startDate"])[:10], False
                # The employer's own link, rather than one this reconstructed.
                url_row = info.get("externalUrl") or url_row

            out.append({
                "id": f"wd-{tenant}-{req or path.rsplit('_', 1)[-1] or len(out)}",
                "title": (j.get("title") or "").strip(),
                "company": w.get("names", {}).get(tenant, tenant),
                "loc": loc or "?",
                "date": date,
                "url": url_row,
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


def probe(cfg):
    employers = cfg.get("workday", {}).get("employers", [])
    if not employers:
        return V.NOT_CONFIGURED, ("no employers listed. This watches named employers "
                                  "rather than searching, so empty is nobody watched")
    good, bad, shard = [], [], []
    for e in employers:
        host, tenant, site = e.get("host"), e.get("tenant"), e.get("site")
        if not (host and tenant and site):
            bad.append(f"{e.get('tenant') or '?'} (needs host, tenant AND site)")
            continue
        data, status = post_json(LIST.format(host=host, tenant=tenant, site=site),
                                 {"appliedFacets": {}, "limit": 1, "offset": 0,
                                  "searchText": ""})
        if status == 200 and data is not None:
            good.append(f"{tenant} ({data.get('total', '?')} open)")
        elif status == 422:
            # Named separately because it is a diagnosis, not a failure: the
            # request was right and the tenant is on another shard.
            shard.append(tenant); bad.append(f"{tenant} (422)")
        else:
            bad.append(f"{tenant} ({status})")
    hint = (f" — 422 means the wrong wd shard, not a bad request: try wd3/wd5 in "
            f"host for {', '.join(shard)}") if shard else ""
    if not good:
        return V.FAILED, f"none reachable: {', '.join(bad)}{hint}"
    if bad:
        return V.OK, f"{len(good)}/{len(employers)} reachable: {', '.join(good)}. Not: {', '.join(bad)}{hint}"
    return V.OK, ", ".join(good)
