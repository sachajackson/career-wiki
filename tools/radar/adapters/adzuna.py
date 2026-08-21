"""Adzuna — the default. A documented, supported, free-tier API.

Register at https://developer.adzuna.com/ for an app_id and app_key.
Docs: https://developer.adzuna.com/overview
"""
import urllib.parse, re
from ._http import get_json

NAME = "adzuna"
BASE = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

def fetch(cfg, query, days):
    a = cfg.get("adzuna", {})
    if not a.get("app_id") or not a.get("app_key"):
        return []
    out, country = [], a.get("country", "gb")
    for page in range(1, int(a.get("pages", 2)) + 1):
        params = {
            "app_id": a["app_id"], "app_key": a["app_key"],
            "results_per_page": 50, "what": query,
            "where": a.get("where", ""), "max_days_old": days,
            "content-type": "application/json",
        }
        if a.get("distance"):
            params["distance"] = a["distance"]
        data = get_json(BASE.format(country=country, page=page) + "?" + urllib.parse.urlencode(params))
        if not data or not data.get("results"):
            break
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
    return out
