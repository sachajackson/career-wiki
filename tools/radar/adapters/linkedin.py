"""LinkedIn guest endpoint.

*** OFF BY DEFAULT. READ THIS BEFORE ENABLING. ***

This uses an undocumented endpoint that backs LinkedIn's logged-out job widget.
It is not a public API. Three things follow:

  1. Automated access is against LinkedIn's terms of service. Enabling this is
     your decision, made knowingly.
  2. It is undocumented, so it can change or start refusing without notice.
     When it does, this adapter returns nothing and the runner will say so.
  3. It is rate-limited by politeness only. The delay below is deliberate.
     Do not lower it.

Prefer the adzuna adapter. It is documented, supported, and will not disappear.
"""
import urllib.parse, re, html, time
from ._http import get

NAME = "linkedin"
SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

def fetch(cfg, query, days):
    c = cfg.get("linkedin", {})
    if not c.get("enabled"):
        return []
    where = c.get("location", "")
    out = []
    for start in range(0, int(c.get("pages", 4)) * 10, 10):
        url = SEARCH + "?" + urllib.parse.urlencode(
            {"keywords": query, "location": where, "f_TPR": f"r{days*86400}", "start": start})
        h = get(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en"})
        if h is None:
            break
        cards = _parse(h)
        if not cards:
            break
        out.extend(cards)
        time.sleep(float(c.get("delay", 0.8)))
    return out

def fetch_body(job_id):
    """Descriptions are not in the listing response; one extra call each."""
    h = get(DETAIL + job_id.replace("li-", ""), headers={"User-Agent": BROWSER_UA})
    if not h:
        return ""
    m = re.search(r"show-more-less-html__markup(.*?)</div>", h, re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", m.group(1)))) if m else ""

def _parse(h):
    out = []
    for c in h.split("<li>"):
        m = re.search(r'href="(https://[a-z]{2}\.linkedin\.com/jobs/view/[^"?]+)', c)
        if not m:
            continue
        jid = m.group(1).rsplit("-", 1)[-1]
        if not jid.isdigit():
            continue
        t = re.search(r'base-search-card__title"[^>]*>\s*(.*?)\s*</h3>', c, re.S)
        co = re.search(r'base-search-card__subtitle".*?>\s*([^<]+?)\s*</a>', c, re.S)
        lo = re.search(r'job-search-card__location"[^>]*>\s*(.*?)\s*</span>', c, re.S)
        dt = re.search(r'datetime="([\d-]+)"', c)
        if not t:
            continue
        clean = lambda x: html.unescape(re.sub("<[^>]+>", "", x)).strip() if x else ""
        out.append({"id": f"li-{jid}", "title": clean(t.group(1)),
                    "company": clean(co.group(1)) if co else "?",
                    "loc": clean(lo.group(1)) if lo else "?",
                    "date": dt.group(1) if dt else "", "body": "", "pay": "",
                    "url": f"https://www.linkedin.com/jobs/view/{jid}/", "source": NAME})
    return out
