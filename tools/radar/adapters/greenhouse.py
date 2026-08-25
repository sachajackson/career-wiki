"""Greenhouse job boards — public JSON, no key, explicitly documented.

Best used to watch a list of target employers rather than to search broadly.
Find a board token in the careers URL: boards.greenhouse.io/<token>
"""
from ._http import get_json, fetch_json
import re
from . import _verdicts as V

NAME = "greenhouse"
TRUNCATED = False   # whole board, one call: never capped
HONOURS_DAYS = False   # whole board: everything open, at any age
BOARD = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

def fetch(cfg, query, days):
    """`days` is ignored: a board returns everything currently open.

    That is the point of watching a board rather than searching. It is also
    why TRUNCATED is always False here -- there is no page budget to exhaust
    and no recency filter to hide a still-open role behind.
    """
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


def probe(cfg):
    tokens = cfg.get("greenhouse", {}).get("boards", [])
    if not tokens:
        return V.NOT_CONFIGURED, ("no boards listed. This source watches named employers "
                                  "rather than searching, so an empty list is not a "
                                  "failure -- it is nobody being watched")
    good, bad = [], []
    for t in tokens:
        data, status = fetch_json(BOARD.format(token=t))
        (good if status == 200 and data else bad).append(f"{t} ({status})" if status != 200 else t)
    if not good:
        return V.FAILED, f"no board token resolved: {', '.join(bad)}. Check them at boards.greenhouse.io/<token>"
    if bad:
        return V.OK, f"{len(good)}/{len(tokens)} resolve. Not resolving: {', '.join(bad)}"
    return V.OK, f"all {len(good)} resolve"
