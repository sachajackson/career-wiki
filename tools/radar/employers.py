"""The user's standing positions on employers: who to watch, and who to skip.

*** THIS FILE'S DATA NEVER LEAVES THE MACHINE. ***

employers.json holds factual assertions about named companies, some of them
second-hand -- "someone who worked there told me they do not pay for sick
leave". That is entirely legitimate as a private note and completely unusable
anywhere else. It must never reach a CV, a cover letter, an oversight export or
anything a third party reads. export_review.py cannot carry it: that copies four
named kinds of file and this is not one of them. The rule is written here as
well, because a control nobody can see is a control nobody maintains.

And an agent must never suggest the user repeat any of it. Asked why they are
not interested in an employer, the answer is "it is not the right fit for me"
and nothing further. Nothing is gained by explaining, and repeating a
second-hand allegation about a named company is a real risk to the person
repeating it.

WHY TWO LISTS, DOING DIFFERENT JOBS

  watch   Complete coverage of an employer, rather than whatever they choose to
          syndicate to a job board. The list says WHO to watch; which adapter
          reaches them is an implementation detail, and one employer may need a
          different route from the next.

  avoid   Filters the radar BEFORE scoring. Without it, the rule that every role
          found must be assessed in the same turn burns effort on a question
          that was settled months ago.

AND WHY "AVOID" IS NOT THE SAME AS "DECLINED"

A principled exclusion is permanent. A role turned down over a commute or a
start date can come back, and treating the two the same either loses a real
option or re-opens a closed one. So declined entries annotate; they do not
filter.
"""
import datetime, json, os, re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import paths  # noqa: E402

FILE = paths.EMPLOYERS

# Legal-form suffixes carry no identity: "Acme" and "Acme Group plc" are one
# employer, and a user writing the short form should not silently miss the long.
SUFFIX = re.compile(r"\b(ltd|limited|plc|inc|incorporated|llc|llp|corp|corporation|"
                    r"gmbh|s\.?a\.?|nv|bv|ag|group|holdings|international|global)\b", re.I)
# Below this, a substring match starts hitting words inside unrelated names.
MIN_NAME = 4


def norm(s):
    s = SUFFIX.sub(" ", (s or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def load(path=None):
    p = path or FILE
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _names_match(rule_name, company):
    """Substring either way, on normalised names, with a floor on length.

    Either way round because a listing writes the employer inconsistently: the
    same company appears as itself, as its parent, and as a division of itself.
    """
    a, b = norm(rule_name), norm(company)
    if not a or not b or len(a) < MIN_NAME:
        return False
    if a in b or b in a:
        return True
    # And again with the spaces gone. norm() collapses whitespace but keeps it,
    # so "State Street" never matched "statestreet" -- and adapters label a row
    # with whatever the SOURCE calls the employer, which for an ATS is the
    # tenant slug, and a tenant slug has no spaces in it. A real avoid entry
    # naming a two-word employer therefore matched nothing: configured,
    # reported as configured, filtering nothing. The same gap made one employer
    # have to be listed under two spellings by hand.
    #
    # The floor still applies. Removing spaces creates new adjacencies, so this
    # is deliberately the second attempt rather than a replacement for the
    # first: it can only add matches, never change one that already held.
    a2, b2 = a.replace(" ", ""), b.replace(" ", "")
    if len(a2) < MIN_NAME:
        return False
    return a2 in b2 or b2 in a2


def route(emp, cfg):
    """Fold the watch list into the adapter configs. Returns (routed, unrouted).

    This is the half of the design that is easy to get wrong. The first draft
    said a preferred employer joins the Greenhouse watchlist -- too narrow. The
    point is complete coverage of that employer, and the route varies: their ATS
    if they have one this can read, a named query if not.
    """
    routed, unrouted = [], []
    for e in emp.get("watch", []):
        name = e.get("employer") or "?"
        hit = False
        wd = e.get("workday")
        if wd and wd.get("host") and wd.get("tenant") and wd.get("site"):
            cfg.setdefault("workday", {}).setdefault("employers", []).append(dict(wd))
            cfg["workday"].setdefault("names", {})[wd["tenant"]] = name
            hit = True
        orc = e.get("oracle")
        if orc and orc.get("host") and orc.get("site"):
            cfg.setdefault("oracle", {}).setdefault("employers", []).append(dict(orc))
            cfg["oracle"].setdefault("names", {})[orc["site"]] = name
            hit = True
        if e.get("greenhouse"):
            cfg.setdefault("greenhouse", {}).setdefault("boards", []).append(e["greenhouse"])
            hit = True
        if e.get("lever"):
            cfg.setdefault("lever", {}).setdefault("companies", []).append(e["lever"])
            hit = True
        if e.get("query"):
            # The fallback, and the weakest route: a search term rather than the
            # employer's own board, so it sees only what they syndicate.
            cfg.setdefault("queries", []).append(e["query"])
            hit = True
        (routed if hit else unrouted).append(name)
    return routed, unrouted


def contradictions(emp):
    """An employer on both lists. Silence here would let either one win."""
    watched = [e.get("employer", "") for e in emp.get("watch", [])]
    out = []
    for a in emp.get("avoid", []):
        for w in watched:
            if _names_match(a.get("employer", ""), w):
                out.append(w)
    return sorted(set(out))


def excluded(row, emp):
    """One line saying why this row is out, or None. Name and division only.

    Sector matching is deliberately not done here: at this point in the run
    there is no description to match against, and a sector cannot be judged
    from a job title. See excluded_by_sector.
    """
    company, title = row.get("company", ""), row.get("title", "")
    for a in emp.get("avoid", []):
        name = a.get("employer", "")
        divisions = a.get("divisions") or []
        if not _names_match(name, company):
            # 🔴 A DIVISION OFTEN POSTS UNDER ITS OWN NAME, and checking the
            # parent's name first made the exclusion unreachable when it does.
            #
            # State Street is watched and its Charles River division excluded.
            # That was verified against State Street's own Workday board, where
            # the company field says "State Street" and the division is in the
            # title -- and it worked. LinkedIn labels the same roles "Charles
            # River Development", so the parent never matched, the division check
            # never ran, and 16 rows reached a shortlist. One was "Technical
            # Delivery Manager", which matches the user's query list exactly and
            # is the role the exclusion was written to stop.
            #
            # The exclusion looked correct because it WAS correct, on the one
            # source it had been tested against.
            hit = next((d for d in divisions if d and _names_match(d, company)), None)
            if not hit:
                continue
            return f"{name}: {hit} division excluded"
        if not divisions:
            return f"{name}: on the avoid list"
        # A whole employer can be fine and one division inside it not. Found in
        # real use: roughly a third of one employer's local postings belonged to
        # a division the user had ruled out, so a company-level filter would
        # have surfaced every one of them, every run, forever.
        hay = f"{title} {company}".lower()
        for d in divisions:
            if d and d.lower() in hay:
                return f"{name}: {d} division excluded"
    for e in emp.get("watch", []):
        if not _names_match(e.get("employer", ""), company):
            continue
        hay = f"{title} {company}".lower()
        for d in e.get("avoid_divisions") or []:
            if d and d.lower() in hay:
                return f"{e.get('employer')}: {d} division excluded"
    return None


def _word(kw):
    """Whole-word match, but only where a word boundary can exist.

    `\b` sits between a word character and a non-word one, so anchoring a
    keyword that begins or ends with punctuation asks for a boundary that is
    never there and the keyword silently never matches. Silent is the problem:
    the user believes a sector is filtered and it is not.
    """
    kw = kw.lower()
    left = r"\b" if kw[:1].isalnum() else ""
    right = r"\b" if kw[-1:].isalnum() else ""
    return left + re.escape(kw) + right


def excluded_by_sector(row, emp):
    """Run this AFTER descriptions are fetched, not before.

    A category exclusion is the half that catches employers the user has never
    heard of, which is exactly why it cannot work off a company name. With the
    description it is a usable net; without one it is close to useless, and
    saying so is better than a filter that quietly does nothing.
    """
    hay = f"{row.get('company','')} {row.get('title','')} {row.get('body','')}".lower()
    for s in emp.get("avoid_sectors", []):
        for kw in s.get("match") or []:
            if kw and re.search(_word(kw), hay):
                return f"{s.get('sector', 'sector')}: matched {kw!r}"
    return None


def declined_note(row, emp):
    """Not a filter. A role turned down on timing or commute can come back."""
    for d in emp.get("declined", []):
        if _names_match(d.get("employer", ""), row.get("company", "")):
            return f"{d.get('employer')} — declined {d.get('on','?')}: {d.get('reason','no reason recorded')}"
    return None


def stale(emp, months=24, today=None):
    """Exclusions go stale. Companies change ownership, policy and management.

    An undated entry is reported too: it cannot be aged, which is a reason to
    look at it rather than a reason to trust it.
    """
    today = today or datetime.date.today()
    cutoff = today - datetime.timedelta(days=int(months * 30.44))
    out = []
    for a in emp.get("avoid", []) + emp.get("avoid_sectors", []):
        who = a.get("employer") or a.get("sector") or "?"
        since = a.get("since")
        if not since:
            out.append(f"{who} (undated)")
            continue
        try:
            if datetime.date.fromisoformat(str(since)[:10]) < cutoff:
                out.append(f"{who} (since {since})")
        except ValueError:
            out.append(f"{who} (unreadable date {since!r})")
    return out


def basis_gaps(emp):
    """An exclusion without a basis cannot be re-judged later.

    "Their published policy says X" and "someone who worked there told me X" are
    both legitimate reasons to decline an employer and completely different
    kinds of claim. The basis is what decides how durable the exclusion is, so
    an entry missing one is a note rather than a position.
    """
    return [a.get("employer", "?") for a in emp.get("avoid", [])
            if not a.get("basis") or not a.get("reason")]
