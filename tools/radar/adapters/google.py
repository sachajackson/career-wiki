"""Google Careers — server-rendered HTML, no API, no posting dates.

WHY THIS IS ITS OWN ADAPTER

Google runs its own careers site and no third-party ATS reaches it. The old
`careers.google.com/api/v3/search/` endpoint is gone -- it answers 404 with
`{"detail":"Not Found"}` -- and the `custom` adapter cannot help, because that
one walks JSON and there is no JSON here.

🟢 But the results page is SERVER-RENDERED, which is the unusual part and the
reason this works at all. The page ships about 1.4MB of real HTML carrying
twenty complete job cards: title, location, and the Minimum-qualifications list.
No browser, no JavaScript, and it answers this repo's own user agent rather than
demanding a browser one.

🔴 IT PUBLISHES NO POSTING DATE. Not "30+ days" like Workday -- none at all,
anywhere on the card. So `date` is empty and `HONOURS_DAYS` is False, and a
Google row can be any age. Never report one as new. This is worse than Workday's
floor, because a floor at least tells you a minimum.

WHAT IT PARSES, AND WHY THAT ANCHOR

Each card ends with an anchor carrying both the id and the human-readable title:

    href="jobs/results/<id>-<slug>?location=..."
    aria-label="Learn more about Senior Control Systems Networking Engineer"

🔴 The aria-label is used for the title rather than the slug, deliberately. The
slug is lowercased and hyphen-flattened -- `forward-deployed-engineer-iii-
generative-ai` -- and title matching runs on whole words, so a slug would work
but would read badly everywhere a human sees it.

The card is the HTML BETWEEN the previous anchor and this one, because the
anchor sits at the end of its own card. That is the one structural assumption
here, and `probe()` checks it rather than trusting it.
"""
import html
import re

from ._http import get
from . import _titles, _verdicts as V

NAME = "google"
TRUNCATED = False
HONOURS_DAYS = False   # no recency parameter, and no posting date to filter on

RESULTS = ("https://www.google.com/about/careers/applications/jobs/results/"
           "?location={loc}&page={page}")
PER_PAGE = 20

# id and human title in one match. Both are needed; a card missing either is
# skipped rather than half-filled.
CARD = re.compile(r'href="jobs/results/(\d+)-[^"]*"\s+aria-label="Learn more about ([^"]+)"')
QUALS = re.compile(r'<h4>Minimum qualifications</h4>(.*?)</div>', re.S)
# 🔴 EVERY location span, joined -- never one of them. This is the same trap the
# `custom` adapter documents for Deel, and it bit here too.
#
# A multi-site role renders as three separate spans:
#     <span>London, UK</span><span>; Dublin, Ireland</span><span>; +2 more</span>
#
# Taking the first gives "London, UK"; taking the last gives "; +2 more". Either
# way the radar's location filter -- which runs on this string, before any
# description is read -- drops a role that IS open in Dublin, and nothing says
# so. Measured before this was joined: an "Engineering Manager" fetch returned
# rows labelled Warsaw and London that the Dublin query had matched precisely
# because they are also open in Dublin.
PLACE = re.compile(r'<span[^>]*>\s*;?\s*([A-Z][^<]*?,\s*[A-Za-z][^<]*?)\s*</span>')
MORE = re.compile(r'\+\s*(\d+)\s*more')
TOTAL = re.compile(r'\bof (\d+)\s')


SCRIPTS = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
# Where the real description starts on a detail page, and where the site's own
# boilerplate begins. Everything between the two is the job.
STARTS = ("<h3>About the job", "<h3>Minimum qualifications")
ENDS = ("Google is proud to be an equal opportunity",
        "To all recruitment agencies", "Benefits at Google")
BODY_CAP = 12000


def text(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def describe(detail_html):
    """The full description from a job's own page, or "" if the shape changed.

    🔴 WHY THIS EXISTS AT ALL. The results page carries only the
    Minimum-qualifications bullets -- about 360 characters. Measured across 48
    Google roles scored from the listing alone, the highest keyword tally was 4
    against a MED threshold of 10: NOT ONE Google role could ever have tiered.
    A watched employer whose roles can only ever land in the catch-all section
    is a watch in name only.

    The detail page carries About-the-job, Responsibilities, and both
    qualification lists. Script and style blocks are stripped first, or the
    flattened text runs on into Google's inlined JavaScript.
    """
    if not detail_html:
        return ""
    clean = SCRIPTS.sub(" ", detail_html)
    start = min((clean.find(s) for s in STARTS if clean.find(s) >= 0), default=-1)
    if start < 0:
        return ""
    body = text(clean[start:start + BODY_CAP * 3])
    for end in ENDS:
        cut = body.find(end)
        if cut > 0:
            body = body[:cut]
    return body[:BODY_CAP].strip()


def parse(page_html):
    """Cards on one results page. Empty list means the page held none."""
    out, prev = [], 0
    for m in CARD.finditer(page_html):
        card, prev = page_html[prev:m.start()], m.end()
        q = QUALS.search(card)
        places, hidden = PLACE.findall(card), MORE.search(card)
        loc = "; ".join(dict.fromkeys(text(p) for p in places if text(p)))
        # "+2 more" means the card itself is hiding locations. Say so rather
        # than letting a truncated list read as the complete one.
        if hidden and loc:
            loc = f"{loc} (+{hidden.group(1)} more)"
        out.append({
            "id": f"goog-{m.group(1)}",
            "title": html.unescape(m.group(2)).strip(),
            "company": "Google",
            "loc": loc or "?",
            # 🔴 Empty on purpose. Google states no posting date; inventing
            # today's would make every role look new for ever.
            "date": "",
            "url": f"https://www.google.com/about/careers/applications/jobs/results/{m.group(1)}",
            "body": text(q.group(1)) if q else "",
            "pay": "",
            "source": NAME,
        })
    return out


def fetch(cfg, query, days):
    """`days` is ignored: there is no recency parameter and no date to apply one to."""
    conf = cfg.get("google", {})
    locations = conf.get("locations", [])
    if not locations:
        return []
    pages = int(conf.get("pages", 8))
    out, seen = [], set()
    for loc in locations:
        for page in range(1, pages + 1):
            body = get(RESULTS.format(loc=loc.replace(" ", "%20"), page=page))
            if not body:
                break
            rows = parse(body)
            if not rows:
                break
            fresh = [r for r in rows if r["id"] not in seen]
            if not fresh:
                break          # the site repeated a page rather than ending
            seen.update(r["id"] for r in fresh)
            for r in fresh:
                if not _titles.matches(query, r["title"]):
                    continue
                # Only matching rows are expanded, and _http caches within the
                # run -- so 47 queries over one board cost one fetch per role,
                # not 47.
                full = describe(get(r["url"]))
                if full:
                    r["body"] = full
                out.append(r)
            if len(rows) < PER_PAGE:
                break          # short page: that was the last one
    return out


def probe(cfg):
    conf = cfg.get("google", {})
    locations = conf.get("locations", [])
    if not locations:
        return V.NOT_CONFIGURED, ("no locations listed. This source watches one employer's own "
                                  "site, so an empty list is nobody being watched, not a failure")
    loc = locations[0]
    body = get(RESULTS.format(loc=loc.replace(" ", "%20"), page=1))
    if not body:
        return V.FAILED, f"careers page returned nothing for {loc!r}"
    rows = parse(body)
    if not rows:
        # 🔴 The failure this adapter is most likely to have, and the one that
        # looks exactly like a quiet week. Google re-renders its careers site
        # periodically; when the anchor changes shape, parse() returns [] while
        # the page still answers 200 with over a megabyte of HTML.
        return V.FAILED, (f"page answered ({len(body)} bytes) but NO job cards parsed for {loc!r}. "
                          f"The markup has almost certainly changed -- check the "
                          f"'Learn more about' anchor in adapters/google.py")
    total = TOTAL.search(body)
    n = f", {total.group(1)} open in {loc}" if total else ""
    return V.OK, f"{len(rows)} card(s) parsed on page 1{n}"
