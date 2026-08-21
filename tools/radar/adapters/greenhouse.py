"""Greenhouse job boards — public JSON, no key, explicitly documented.

Best used to watch a list of target employers rather than to search broadly.
Find a board token in the careers URL: boards.greenhouse.io/<token>
"""
from ._http import get_json
import re

NAME = "greenhouse"
BOARD = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

def fetch(cfg, query, days):
    tokens = cfg.get("greenhouse", {}).get("boards", [])
    if not tokens:
        return []
    q = query.lower()
    out = []
    for token in tokens:
        data = get_json(BOARD.format(token=token))
        if not data:
            continue
        for j in data.get("jobs", []):
            title = j.get("title", "")
            if q and q.split()[0] not in title.lower():
                continue
            body = re.sub(r"<[^>]+>", " ", j.get("content", "") or "")
            out.append({
                "id": f"gh-{j.get('id')}",
                "title": title,
                "company": token,
                "loc": (j.get("location") or {}).get("name", "?"),
                "date": (j.get("updated_at") or "")[:10],
                "url": j.get("absolute_url", ""),
                "body": re.sub(r"\s+", " ", body),
                "pay": "",
                "source": NAME,
            })
    return out
