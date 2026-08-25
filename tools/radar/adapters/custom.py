"""custom -- employers who run their own job API instead of a third-party ATS.

Deel is the first. There will be more: an employer large enough to build its own
careers site often proxies its ATS behind it, and then none of the four standard
adapters can reach them. Without this they resolve from the registry and are
then reported as unsearchable, which is honest and useless.

HOW IT IS GENERIC

The adapter knows how to walk JSON. The registry says where this employer's
fields live, as dotted paths:

    "params": {
      "list": "https://www.deel.com/api/deel-ats/jobs/",
      "detail": "https://www.deel.com/api/deel-ats/jobs/{id}/",
      "map": {"id": "attributes.ashby_id", "title": "attributes.title", ...}
    }

THE FIELD THAT MATTERS MOST IS THE LOCATION, AND IT IS THE EASY ONE TO GET WRONG

Deel carries both `location_name` -- the FIRST location, "Israel" -- and
`all_locations`, the full list of thirty countries including Ireland. Mapping the
obvious-looking field would have every Deel role filtered out on location by a
user who is eligible for all of them, and nothing would say so. A list is joined
rather than taking its first element, deliberately.
"""
from ._http import get_json
from . import _verdicts as V

NAME = "custom"
TRUNCATED = False
HONOURS_DAYS = False   # one call returns the whole board; no recency parameter


def dig(row, path):
    """'attributes.all_locations' -> the value. Lists are joined, not truncated."""
    cur = row
    for part in (path or "").split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return ""
        if cur is None:
            return ""
    if isinstance(cur, list):
        parts = [str(x.get("location", x)) if isinstance(x, dict) else str(x) for x in cur]
        return ", ".join(p for p in parts if p)
    return str(cur) if cur is not None else ""


def rows_of(data, root):
    if root:
        return dig(data, root) if isinstance(dig(data, root), list) else (data.get(root) or [])
    if isinstance(data, list):
        return data
    for k in ("jobs", "results", "data", "items"):
        if isinstance(data.get(k), list):
            return data[k]
    return []


def _one(emp):
    """(rows, params) for one employer entry, or (None, params) if unreachable."""
    p = emp.get("params", emp)
    data = get_json(p["list"])
    if data is None:
        return None, p
    return rows_of(data, p.get("root")), p


def fetch(cfg, query, days):
    """`days` is ignored -- see HONOURS_DAYS. A bespoke board returns everything open.

    `query` is ignored too: these APIs rarely offer server-side search, and
    filtering here would hide roles the runner's own title matching would keep.
    """
    global TRUNCATED
    TRUNCATED = False
    employers = cfg.get("custom", {}).get("employers", [])
    if not employers:
        return []

    out = []
    for emp in employers:
        rows, p = _one(emp)
        if rows is None:
            TRUNCATED = True          # the request failed; what was behind it is unknown
            continue
        m = p.get("map", {})
        prefix = p.get("url_prefix", "")
        for r in rows:
            url = dig(r, m.get("url", ""))
            if url and prefix and url.startswith("/"):
                url = prefix + url
            out.append({
                "id": f"{NAME}:{dig(r, m.get('id', ''))}",
                "title": dig(r, m.get("title", "")),
                "company": emp.get("employer", p.get("employer", "")),
                # Every location, joined. Taking the first would drop a role the
                # user is eligible for and say nothing about it.
                "loc": dig(r, m.get("loc", "")),
                "date": dig(r, m.get("date", ""))[:10],
                "url": url,
                "pay": dig(r, m.get("pay", "")),
                "body": dig(r, m.get("body", "")),
                "source": NAME,
                "_custom": (p, dig(r, m.get("id", ""))),
            })
    return out


def fetch_body(row):
    """Descriptions are usually absent from a list response; one call each.

    Takes the row rather than an id because the detail URL is per-employer, and
    the id alone cannot say which employer it belongs to.
    """
    c = (row or {}).get("_custom")
    if not c:
        return ""
    p, jid = c
    tmpl = p.get("detail")
    if not (tmpl and jid):
        return ""
    data = get_json(tmpl.replace("{id}", str(jid)))
    if data is None:
        return ""
    path = p.get("map", {}).get("body", "")
    body = dig(data, path)
    if not body and "." in path:
        # A detail response often returns unwrapped what the list response wraps.
        # Deel does exactly this: attributes.full_job_description in the listing,
        # full_job_description on its own in the detail. Try the leaf before
        # giving up, rather than making the registry carry two paths for one field.
        body = dig(data, path.split(".")[-1])
    import re, html
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()


def probe(cfg):
    employers = cfg.get("custom", {}).get("employers", [])
    if not employers:
        return V.NOT_CONFIGURED, ("no employers listed. This watches named employers rather than "
                                  "searching, so empty is nobody watched")
    good, bad = [], []
    for emp in employers:
        name = emp.get("employer", "?")
        p = emp.get("params", emp)
        if not p.get("list"):
            bad.append(f"{name} (no list URL)")
            continue
        rows, _ = _one(emp)
        if rows is None:
            bad.append(f"{name} (did not answer)")
        elif not rows:
            bad.append(f"{name} (answered with nothing)")
        else:
            good.append(f"{name} ({len(rows)} open)")
    if bad and not good:
        return V.FAILED, "; ".join(bad)
    if bad:
        return V.OK, f"{'; '.join(good)} -- but {'; '.join(bad)}"
    return V.OK, "; ".join(good)
