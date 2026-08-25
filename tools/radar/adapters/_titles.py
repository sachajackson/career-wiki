"""Does this board title plausibly answer this query?

Employer boards return EVERYTHING an employer has open -- sales, support, legal,
warehouse -- so unlike a search API they need a relevance filter of their own.
Eleven boards produced 756 roles in one country and one role worth reading.

The filter was `query.split()[0] in title`, and it was wrong in both directions
at once. The first word of "head of delivery" is "head", so it kept every Head
of Anything on the board and dropped every Delivery Manager. It matched on the
least informative word in the query.

WHAT ACTUALLY DISCRIMINATES is the domain word, not the seniority word. Boards
are full of Managers, Leads and Directors; they are not full of Delivery. So a
query is split into generic role nouns and distinctive ones, and a title has to
match something distinctive. Where a query is nothing but role nouns there is
nothing distinctive to ask for, so it falls back to requiring all of them --
which is strict, and a query of "senior manager" deserves strict.

TWO THINGS FOUND LATER, BOTH BY MEASURING A REAL BOARD RATHER THAN READING THIS

  The test was `w in title`, a raw substring. "ai" is two letters and it lives
  inside retail, training, maintenance, campaign, email, domain, chair and air.
  On a watchlist carrying fifteen AI-flavoured queries, every one of them kept
  every Retail Operations Manager on every board. Matching is on whole words now.

  "technical", "digital" and "data" were treated as distinctive and they are
  not -- they are everywhere in sales and support titles. Of 138 live rows from
  one employer, 74 survived the filter and seventeen were Account Executives:
  "Cloud Account Executive - Digital" kept by "digital transformation",
  "Technical Support Engineer" kept by three separate queries. They are generic
  now, which leaves each of those queries asking for the word that actually
  discriminates -- transformation, program, delivery.
"""
import re

STOP = {"of", "the", "a", "an", "and", "or", "for", "in", "to", "with", "at", "on"}

# Seniority and role-shape words. Present on a large share of any board, so
# matching one says almost nothing about whether the role is relevant.
GENERIC = {
    "manager", "management", "lead", "leader", "head", "director", "officer",
    "chief", "vp", "vice", "president", "executive", "senior", "snr", "sr",
    "junior", "jnr", "principal", "staff", "associate", "assistant", "specialist",
    "consultant", "analyst", "engineer", "developer", "architect", "coordinator",
    "administrator", "partner", "owner", "expert", "professional",
    # Domain-shaped but not domain-bearing. Measured, not guessed: see above.
    "technical", "digital", "data",
}


def words(text):
    return [w for w in re.findall(r"[a-z0-9+#]+", (text or "").lower()) if w not in STOP]


def matches(query, title):
    """True if the title is worth keeping for this query."""
    qs = words(query)
    if not qs:
        return True                      # no query is not a reason to drop a board
    # Whole words, not substrings. `"ai" in "retail manager"` is True and that
    # single character of laziness kept every Retail role for every AI query.
    ts = set(words(title))
    distinctive = [w for w in qs if w not in GENERIC]
    if distinctive:
        return any(w in ts for w in distinctive)
    return all(w in ts for w in qs)
