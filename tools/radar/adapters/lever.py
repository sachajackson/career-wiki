"""Lever postings — public JSON, no key.

Company handle from the careers URL: jobs.lever.co/<handle>
"""
from ._http import get_json
import re

NAME = "lever"
POSTINGS = "https://api.lever.co/v0/postings/{handle}?mode=json"

def fetch(cfg, query, days):
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
