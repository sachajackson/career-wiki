"""LinkedIn guest endpoint.

🔴 IT GETS THE USER'S OWN IP BLOCKED. Reported 2026-08-28, after a run: LinkedIn
then refused that user's normal browsing from the same address.

That is a different class of cost from every other caveat in this file, and it
is worth stating plainly rather than as a footnote:

  - A run is up to 47 queries x `pages` requests. At pages=10 that is ~470
    automated requests from one address in a few minutes.
  - The person running it NEEDS LinkedIn for the job search itself -- their
    profile, recruiter contact, and many applications start there.
  - So the tool damages the thing it exists to serve. **A source that costs the
    user access to that source is not a source, it is a trade**, and it has to
    be a decision rather than a default.

🟢 WHAT IT UNIQUELY BUYS, MEASURED, so the trade can be judged rather than
argued: of the role pages in one real vault, five cite a LinkedIn URL and no
other, and they are AGENCY postings -- the employer is withheld, so there is no
board to watch and no other route exists. Everything else LinkedIn found was
also reachable from an employer's own ATS.

🟡 THE DESIGNED ALTERNATIVE IS ALREADY WRITTEN DOWN. `role-radar` says of
bot-protected sources: "use their own saved-search email alerts and paste
anything interesting in for scoring." **That applies here exactly**, and it is
the standing backlog item *Email alerts as a universal source*, which this
finding promotes from a good idea to the answer to a live problem.


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
from . import _verdicts as V

NAME = "linkedin"
TRUNCATED = False
HONOURS_DAYS = True   # search endpoint: takes a recency filter
SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

def fetch(cfg, query, days):
    """days=None omits f_TPR entirely, which returns everything still open.

    MEASURED 2026-08-26, and the number this docstring used to carry was wrong.

    It said the endpoint caps a query at roughly 100 results whatever the
    window. It does not. One broad query, 7-day window, one country:

        pages=4  ->  40 rows, truncated      pages=40 -> 400 rows, truncated
        pages=16 -> 160 rows, truncated      pages=80 -> 710 rows, RAN DRY

    So the binding limit is `pages` -- our own budget, ten results a page --
    and not the source. That matters because "capped" in the runner's output
    means OUR budget ran out, which reads as "the source stopped answering"
    and is a different thing entirely.

    Unfiltered is still not a superset of windowed: a fixed page budget spread
    across months is sparser than the same budget over one week, so both runs
    are still needed. The trade is real; it is just OUR cap being traded, and
    it is a setting rather than a fact about LinkedIn.

    Two things before raising it. The tail is mixed rather than junk -- one
    query's rows past 260 held both an unrelated Compliance Manager and a
    precisely on-target senior role -- so depth does buy real roles. And
    LinkedIn rows never pass through _titles.matches, unlike the board
    adapters, so that noise reaches scoring unfiltered.
    """
    global TRUNCATED
    TRUNCATED = False
    c = cfg.get("linkedin", {})
    if not c.get("enabled"):
        return []
    where = c.get("location", "")
    out = []
    for start in range(0, int(c.get("pages", 4)) * 10, 10):
        params = {"keywords": query, "location": where, "start": start}
        if days is not None:          # 0 is a window, not a request for everything
            params["f_TPR"] = f"r{days * 86400}"
        url = SEARCH + "?" + urllib.parse.urlencode(params)
        h = get(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en"})
        if h is None:
            TRUNCATED = True        # a page failed; no idea what was behind it
            break
        cards = _parse(h)
        if not cards:
            break                   # the source ran dry -- this set IS complete
        out.extend(cards)
        time.sleep(float(c.get("delay", 0.8)))
    else:
        TRUNCATED = True            # page budget exhausted, not the source
    return out

def fetch_body(row):
    """Descriptions are not in the listing response; one extra call each."""
    h = get(DETAIL + str(row.get("id", "")).replace("li-", ""),
            headers={"User-Agent": BROWSER_UA})
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


def probe(cfg):
    c = cfg.get("linkedin", {})
    if not c.get("enabled"):
        # Off by default is a decision, not a fault. Saying FAILED here would
        # nag a user into enabling something they read about and declined.
        return V.NOT_CONFIGURED, "off by default, and enabling it is your call — see the module docstring"
    url = SEARCH + "?" + urllib.parse.urlencode(
        {"keywords": "manager", "location": c.get("location", ""), "start": 0})
    h = get(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en"})
    if h is None:
        return V.BLOCKED, ("the guest endpoint refused us. Undocumented and rate-limited; "
                           "it can start refusing without notice")
    n = len(_parse(h))
    if not n:
        return V.EMPTY, ("responded but parsed zero cards. Either the location matches "
                         "nothing or the page markup changed — check before trusting a "
                         "quiet run")
    return V.OK, f"{n} cards parsed from the first page"
