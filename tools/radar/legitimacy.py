"""Is this posting a real, open vacancy — reported separately, never as a score.

Between a fifth and a third of live listings are estimated to be ghost jobs; one
count puts 27% of LinkedIn listings in that bracket, 40% of hiring managers admit
to posting one in the past year, and BLS openings against hires works out at
roughly one in three never producing a hire.

🔴 THE DESIGN DECISION, AND IT IS THE WHOLE POINT: THIS NEVER TOUCHES THE SCORE.

A fake posting is not a low-scoring role. It is not a role. Folding this into a
fit number would let a strong-but-fake posting outrank a real mediocre one, and
would make a scam read as a mediocre opportunity. Same principle as splitting one
total into FIT, LIFE and SEC: things that are not the same question do not go in
the same number.

So this emits CONCERNS, and deliberately not a percentage. A percentage is a
score by another name, and it would be averaged, compared and ranked within a
week. A role can be worth applying to at poor odds of being real -- that is the
user's call, and a number invites the tool to make it for them.

WHAT IT USES, all of it already fetched and none of it costing a request:

  The employer's own posting date. Age is the single best ghost-job predictor,
  and an aggregator showed a ten-week-old requisition as "posted yesterday" in
  real use -- which is why only a date from the employer's own API is trusted
  for this, and an aggregator's date is reported as unconfirmed rather than used.

  A requisition number missing on an employer whose ATS issues them.

  The same requisition number posted before, from seen.json.

WHAT IT DOES NOT DO. It never calls anything, so it cannot tell you a posting is
still live -- `build-application` Step 0 already confirms that at the point it
matters, which is when somebody is about to spend an evening on it.
"""
import datetime, re

# Heuristics, not derived constants: there is no published cut-off at which a
# posting becomes a ghost job. These are the points at which age is worth
# mentioning and worth leading with. Age is a reason to ask, never an answer.
AGEING_DAYS = 45
LONG_OPEN_DAYS = 90

# Sources that ARE the employer's own system. A date from one of these is the
# employer's own; a date from anything else is that site's idea of the date.
# 🟡 google is here for correctness rather than effect: it IS the employer's
# own site, but it publishes no date at all, so there is never a date to
# attribute. The ageing checks simply do not fire on a Google row.
EMPLOYER_OWN = {"workday", "oracle", "greenhouse", "lever", "custom", "google"}
# Of those, the ones that issue a requisition number on every posting, so a
# posting without one is odd rather than merely unrecorded.
ISSUES_REQUISITION = {"workday", "oracle"}


def _age(posted, today):
    try:
        return (today - datetime.date.fromisoformat(str(posted)[:10])).days
    except (ValueError, TypeError):
        return None


def concerns(row, history=None, today=None):
    """-> list of one-line concerns. Empty means nothing looked wrong.

    Empty is NOT a clean bill of health and the caller must not present it as
    one: most of what makes a posting fake is invisible from the posting.
    """
    today = today or datetime.date.today()
    out = []
    source = (row.get("source") or "").lower()
    own = source in EMPLOYER_OWN

    days = _age(row.get("date"), today)
    whose = "the employer's own" if own else f"{source or 'the source'}'s"
    unconfirmed = "" if own else " — unconfirmed, aggregators re-date reposts"
    if row.get("date_is_floor"):
        # A floor is its own finding and must not be compared against the
        # thresholds below. Workday stops counting at 30, so a year-old
        # requisition and a thirty-day-old one are the same string -- measuring
        # that against a 45-day threshold means the check can NEVER fire on the
        # source where age is hardest to see. The refusal to say is the signal.
        out.append(f"age unknown: {whose} date stops at {days} days, so this could be "
                   f"far older{unconfirmed}")
    elif days is not None and days >= AGEING_DAYS:
        band = "open a long time" if days >= LONG_OPEN_DAYS else "ageing"
        out.append(f"{band}: {days} days old by {whose} date{unconfirmed}")

    if source in ISSUES_REQUISITION and not str(row.get("requisition") or "").strip():
        out.append(f"no requisition number, though {source} issues one on every posting")

    rep = _reposts(row, history or {})
    if rep:
        first, n = rep
        out.append(f"requisition {row['requisition']} has been seen before"
                   + (f" ({n} times)" if n > 1 else "")
                   + f", first on {first} — repeat reposting is a ghost-job signal")
    return out


def _reposts(row, history):
    """Matched on requisition number ONLY, and that is deliberate.

    Matching on company and title instead would fire on an employer legitimately
    running the same role in four cities, which is common and would make this
    cry wolf. A check that cries wolf gets switched off, and this one is worth
    keeping. Requisition numbers are exact; a false positive needs the employer
    to reuse one.
    """
    req = str(row.get("requisition") or "").strip()
    if not req:
        return None
    seen_dates = [v.get("posted") for k, v in history.items()
                  if k != row.get("id") and str(v.get("requisition") or "").strip() == req]
    seen_dates = sorted(d for d in seen_dates if d)
    if not seen_dates:
        return None
    return seen_dates[0], len(seen_dates)


def provenance(row):
    """One line on where this came from, which is not a concern in itself.

    Reported apart from concerns on purpose. A LinkedIn posting is not suspect
    for being on LinkedIn -- most of the corpus is -- and flagging every one
    would be the noise that gets the whole block ignored. What is true is that
    nothing has confirmed it against the employer, and unconfirmed is its own
    state, distinct from checked-and-fine.
    """
    source = (row.get("source") or "").lower()
    if source in EMPLOYER_OWN:
        return f"from {source}, the employer's own system"
    return (f"from {source or 'an unknown source'} — an aggregator. Not confirmed against "
            f"the employer's own site, and the date is theirs rather than the employer's")


def line(row, history=None, today=None):
    """The single line that goes on a role page and in the shortlist."""
    c = concerns(row, history, today)
    if not c:
        return f"Legitimacy: nothing flagged. {provenance(row)}"
    head = f"Legitimacy: {len(c)} concern{'s' if len(c) > 1 else ''}"
    return f"{head} — " + "; ".join(c) + f". {provenance(row)}"
