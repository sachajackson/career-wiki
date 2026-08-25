"""Lever postings — public JSON, no key.

Company handle from the careers URL: jobs.lever.co/<handle>
"""
from ._http import get_json
import re

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
    q = query.lower()
    out = []
    for handle in handles:
        data = get_json(POSTINGS.format(handle=handle))
        if not data:
            continue
        for j in data:
            title = j.get("text", "")
            if q and q.split()[0] not in title.lower():
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
