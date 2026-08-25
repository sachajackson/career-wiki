"""Search adapters. Each exposes fetch(cfg, query, days) -> list[dict].

A posting dict is: {id, title, company, loc, date, url, body}
`body` may be empty at listing time; the runner fills it via fetch_body if the
adapter provides one. fetch_body takes the WHOLE ROW, not an id: some sources
address a posting by more than one value -- Workday needs host, tenant, site and
path -- and packing those into the id field to fit a narrower signature is how an
id stops being an id. An adapter may stash what it needs on the row under a
leading-underscore key.

THE `days` CONTRACT. `days` is the posting window in days, or None meaning
"everything currently open". An adapter with a recency parameter MUST OMIT that
parameter when days is None -- never substitute a large number, which asks the
source a different question and gets a differently-wrong answer.

NONE IS THE SENTINEL, AND ONLY NONE. Guard on `days is not None`, never on
`days`, or a window of 0 turns falsy and silently becomes an unfiltered sweep --
the same class of error the None handling exists to prevent, reintroduced by the
shorter spelling. 0 is a window, or a user error; it is not a request for
everything, and answering a question nobody asked is the failure mode here.

AN EARLY STOP DOES NOT MEAN THE SAME THING IN EVERY ADAPTER. For most, stopping
before the end means the source had more to give -- truncation. For one that
sorts newest-first and holds an exact posting date, stopping at the window edge
means the opposite: everything in the window was seen. Set TRUNCATED from WHY
the loop ended, never from whether it ended early.

THE `HONOURS_DAYS` CONTRACT. True if the adapter applies `days` at all. Adapters
that read a whole employer board return everything currently open regardless, so
they set it False. An adapter with no window parameter may still set it True if
it filters exactly itself -- but say so in the module, because "the API filters"
and "the adapter filters" are different claims and only one can be checked
against the source. Adapters and the runner then refuses to head the shortlist with a
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

THE `probe` CONTRACT. Each adapter exposes probe(cfg) -> (verdict, detail),
answering "would this source work for this user, right now" WITHOUT running a
search. `sources_check.py` calls it.

Two of the verdicts exist because collapsing them is the failure this was built
for, and both are the same mistake in different clothes:

  NOT CONFIGURED is not FAILED. An adapter nobody set up has not been tried.
  Reporting it as broken sends someone to debug a source they never wanted, and
  reporting it as fine claims coverage that does not exist.

  NO COVERAGE is not BAD CREDENTIALS. A job API returning 404 for one country
  while serving others is telling you it does not cover that country -- not
  that your key is wrong. An adapter that can be wrong about this must probe a
  KNOWN-GOOD control alongside the user's own country, because one probe cannot
  tell the two apart and guessing cost a real user an hour.

Adding an adapter: write the module, expose fetch(), set TRUNCATED and
HONOURS_DAYS, expose probe(), add it to ADAPTERS below.
"""
from ._verdicts import (OK, EMPTY, NOT_CONFIGURED, NO_COVERAGE,      # noqa: F401
                        BAD_CREDENTIALS, BLOCKED, FAILED, SEVERITY)

from . import adzuna, custom, greenhouse, lever, linkedin, oracle, workday  # noqa: E402

ADAPTERS = {
    "adzuna": adzuna,
    "custom": custom,
    "greenhouse": greenhouse,
    "lever": lever,
    "linkedin": linkedin,
    "oracle": oracle,
    "workday": workday,
}
