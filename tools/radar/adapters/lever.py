"""Lever postings — public JSON, no key.

Company handle from the careers URL: jobs.lever.co/<handle>
"""
from ._http import get_json, fetch_json
import re
from . import _titles, _verdicts as V

NAME = "lever"
TRUNCATED = False   # whole board, one call: never capped
HONOURS_DAYS = False   # whole board: everything open, at any age
POSTINGS = "https://api.lever.co/v0/postings/{handle}?mode=json"

def fetch(cfg, query, days):
    """`days` is ignored: a board returns everything currently open.

    That is the point of watching a board rather than searching. It is also
    why TRUNCATED is always False here -- there is no page budget to exhaust
    and no recency filter to hide a still-open role behind.
    """
    handles = cfg.get("lever", {}).get("companies", [])
    if not handles:
        return []
    q = query
    out = []
    for handle in handles:
        data = get_json(POSTINGS.format(handle=handle))
        if not data:
            continue
        for j in data:
            title = j.get("text", "")
            if not _titles.matches(q, title):
                continue
            body = re.sub(r"<[^>]+>", " ", j.get("descriptionPlain") or j.get("description", "") or "")
            out.append({
                "id": f"lever-{j.get('id')}",
                "title": title,
                "company": handle,
                "loc": (j.get("categories") or {}).get("location", "?"),
                "date": "",
                "url": j.get("hostedUrl", ""),
                "body": re.sub(r"\s+", " ", body),
                "pay": "",
                "source": NAME,
            })
    return out


def probe(cfg):
    tokens = cfg.get("lever", {}).get("companies", [])
    if not tokens:
        return V.NOT_CONFIGURED, ("no companies listed. This source watches named employers "
                                  "rather than searching, so an empty list is not a "
                                  "failure -- it is nobody being watched")
    good, bad = [], []
    for t in tokens:
        data, status = fetch_json(POSTINGS.format(handle=t))
        (good if status == 200 and data else bad).append(f"{t} ({status})" if status != 200 else t)
    if not good:
        return V.FAILED, f"no company slug resolved: {', '.join(bad)}. Check them at jobs.lever.co/<slug>"
    if bad:
        return V.OK, f"{len(good)}/{len(tokens)} resolve. Not resolving: {', '.join(bad)}"
    return V.OK, f"all {len(good)} resolve"
