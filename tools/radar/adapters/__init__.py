"""Search adapters. Each exposes fetch(cfg, query, days) -> list[dict].

A posting dict is: {id, title, company, loc, date, url, body}
`body` may be empty at listing time; the runner fills it via fetch_body if the
adapter provides one.

THE `days` CONTRACT. `days` is the posting window in days, or None meaning
"everything currently open". An adapter with a recency parameter MUST OMIT that
parameter when days is None -- never substitute a large number, which asks the
source a different question and gets a differently-wrong answer.

NONE IS THE SENTINEL, AND ONLY NONE. Guard on `days is not None`, never on
`days`, or a window of 0 turns falsy and silently becomes an unfiltered sweep --
the same class of error the None handling exists to prevent, reintroduced by the
shorter spelling. 0 is a window, or a user error; it is not a request for
everything, and answering a question nobody asked is the failure mode here.

THE `HONOURS_DAYS` CONTRACT. True if the adapter applies `days` at all. Adapters
that read a whole employer board return everything currently open regardless, so
they set it False, and the runner then refuses to head the shortlist with a
window those rows do not obey. An adapter that does not declare it is treated as
NOT honouring the window: over-warning costs a line of output, under-warning
tells the reader a six-month-old posting is a week old.

THE `TRUNCATED` CONTRACT. Every adapter sets the module attribute TRUNCATED on
each call to fetch(), before returning. True means the adapter stopped because
it exhausted its own page budget or a page failed -- so the source had more to
give and this result set is not complete. False means the source itself ran out
of results, which is the only thing that proves completeness. The runner reports
truncation rather than presenting a capped set as the whole picture: sources cap
per query, so a run reporting a round number is usually reporting the cap.

Adding an adapter: write the module, expose fetch(), set TRUNCATED, add it to
ADAPTERS below.
"""
from . import adzuna, greenhouse, lever, linkedin

ADAPTERS = {
    "adzuna": adzuna,
    "greenhouse": greenhouse,
    "lever": lever,
    "linkedin": linkedin,
}
