"""Adzuna — a documented, supported, free-tier API.

Register at https://developer.adzuna.com/ for an app_id and app_key.
Docs: https://developer.adzuna.com/overview

*** COVERAGE IS NOT GLOBAL. CHECK YOUR COUNTRY FIRST. ***

Tested 2026-08-23 with a valid key: gb, us, nl and de all return results.
`ie` returns 404 -- Adzuna does not cover Ireland. A 404 here means the
country is unsupported, NOT that the key is wrong, and the difference costs an
hour if you assume the latter.

    curl "https://api.adzuna.com/v1/api/jobs/<cc>/search/1?app_id=X&app_key=Y&results_per_page=1"

Run that before wiring anything up.
"""
import urllib.parse, re
from . import _verdicts as V
from ._http import get_json, fetch_json

NAME = "adzuna"
TRUNCATED = False
HONOURS_DAYS = True   # search API: takes a recency filter
BASE = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

def fetch(cfg, query, days):
    """days=None omits max_days_old, which returns everything still open."""
    global TRUNCATED
    TRUNCATED = False
    a = cfg.get("adzuna", {})
    if not a.get("app_id") or not a.get("app_key"):
        return []
    out, country = [], a.get("country", "gb")
    for page in range(1, int(a.get("pages", 2)) + 1):
        params = {
            "app_id": a["app_id"], "app_key": a["app_key"],
            "results_per_page": 50, "what": query,
            "where": a.get("where", ""),
            "content-type": "application/json",
        }
        if days is not None:          # 0 is a window, not a request for everything
            params["max_days_old"] = days
        if a.get("distance"):
            params["distance"] = a["distance"]
        data = get_json(BASE.format(country=country, page=page) + "?" + urllib.parse.urlencode(params))
        if data is None:
            TRUNCATED = True        # request failed; the rest is unknown
            break
        if not data.get("results"):
            break                   # the source ran dry -- this set IS complete
        for r in data["results"]:
            sal = ""
            lo, hi = r.get("salary_min"), r.get("salary_max")
            if lo and hi:
                sal = f"{int(lo):,}-{int(hi):,}" if lo != hi else f"{int(lo):,}"
            out.append({
                "id": f"adzuna-{r.get('id')}",
                "title": r.get("title", "").strip(),
                "company": (r.get("company") or {}).get("display_name", "?"),
                "loc": (r.get("location") or {}).get("display_name", "?"),
                "date": (r.get("created") or "")[:10],
                "url": r.get("redirect_url", ""),
                # Adzuna returns a truncated description; enough to triage on.
                "body": re.sub(r"\s+", " ", r.get("description", "")),
                "pay": sal,
                "source": NAME,
            })
    else:
        TRUNCATED = True            # page budget exhausted, not the source
    return out


# A country the API is known to serve. Its only job is to be the control in the
# probe below: without it, "404 for your country" and "your key is wrong" look
# identical, and a real user spent an hour on the wrong one of those.
CONTROL = "gb"


def _ping(a, country):
    params = {"app_id": a.get("app_id", ""), "app_key": a.get("app_key", ""),
              "results_per_page": 1, "content-type": "application/json"}
    return fetch_json(BASE.format(country=country, page=1) + "?" +
                      urllib.parse.urlencode(params))


def probe(cfg):
    a = cfg.get("adzuna", {})
    country = a.get("country", "")
    if not a.get("app_id") or not a.get("app_key"):
        return V.NOT_CONFIGURED, "no app_id/app_key. Free key: developer.adzuna.com"
    if not country or country.startswith("<"):
        return V.NOT_CONFIGURED, "country is unset or still a placeholder"

    data, status = _ping(a, country)
    if status == 200 and data is not None:
        return V.OK, f"{country} returns results"
    if status in (401, 403):
        return V.BAD_CREDENTIALS, f"{country} -> {status}. The key is wrong, not the country"

    # Ambiguous so far, so ask the control. This is the whole point of the probe.
    _, control = _ping(a, CONTROL)
    if status == 404 and control == 200:
        return (V.NO_COVERAGE,
                f"{country} -> 404 while {CONTROL} -> 200. Adzuna does not cover "
                f"{country}. Your key is fine; nothing you can do to this config "
                f"will fix it")
    if control in (401, 403):
        return V.BAD_CREDENTIALS, f"{CONTROL} -> {control} too, so it is the key"
    if control == 200:
        return V.FAILED, f"{country} -> {status} while {CONTROL} works. Not a key problem"
    return V.FAILED, f"{country} -> {status}, {CONTROL} -> {control}. Adzuna may be down"
