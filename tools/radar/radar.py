#!/usr/bin/env python3
"""Role Radar — find job postings, filter them, and tier them for an agent to read.

    python3 radar.py --days 7          # dense recent coverage
    python3 radar.py --all-open        # sparse sweep of everything still open
    python3 radar.py --retier          # re-tier the cache without refetching
    python3 radar.py --reset           # forget what has been seen

Writes shortlist.md, raw.json and seen.json alongside this file. All three are
gitignored and regenerated; nothing here is a record of anything durable.

WHAT THIS IS NOT: SIGNAL is a keyword tally rendered as a word, not a judgement,
and it has no relationship to the scoring framework's number. Its only job is to
decide what is worth an agent reading. See the failure modes in the role-radar
skill -- in particular, good roles DO land in MED, so MED always gets read.

--all-open IS NOT A SUPERSET OF --days. Sources cap results per query regardless
of the window, so a windowed run and an unfiltered run are a trade, not a
ladder: 100 results from one week, or 100 results across three months. Both are
needed -- frequent windowed runs for freshness, a periodic unfiltered sweep for
the standing backlog of still-open roles. Dedup handles the overlap.
"""
import argparse, datetime, json, os, re, sys, time
import concurrent.futures as cf
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adapters import ADAPTERS                                    # noqa: E402
from adapters import _http as HTTP                               # noqa: E402
import employers as EMP                                          # noqa: E402
import legitimacy as LEGIT                                       # noqa: E402

# Paths come from one place, so moving the vault touches one file. Before this
# they were pinned here, in employers.py, and seven times in doctor.py -- and
# missing one is silent: a tool reading a path nobody writes to reports "nothing
# here" rather than "I am looking in the wrong place".
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import paths  # noqa: E402

CONFIG = paths.SEARCH
RAW    = paths.RAW
SEEN   = paths.SEEN
OUT    = paths.SHORTLIST

# Titles that resolve to an individual-contributor role. Matched against the
# WHOLE title, anchored -- "Senior Developer" is out, but "Director of
# Engineering, Developer Experience" is not. A substring match here silently
# discarded a genuinely strong role during development.
# ---------------------------------------------------------------------------
# THE TIERING VOCABULARY IS THE USER'S, AND IT LIVES IN THEIR VAULT.
#
# Until 2026-08-26 one person's vocabulary was hardcoded here: a large positive
# weight for a phrase that pre-answered their main objection, a large negative one
# for an adjacent industry whose listings kept matching their words, and a penalty
# for a commuting pattern they would not accept. Every one of those is a statement
# about ONE PERSON -- their preference, their exclusions, their journey to work --
# and all of it shipped to everyone who cloned the repo. Somebody in an unrelated
# trade got a scale built for a delivery director, and somebody working IN that
# penalised industry got a heavy negative for their own career.
#
# (Worded carefully: the test that keeps this file clean searches for those very
# terms, and a comment naming them would fail it. That has now happened three
# times in this repo -- see the commit guard's own postmortems.)
#
# AGENTS.md: "everything about, belonging to, or specific to the user lives under
# vault/". test_boundary.py could not catch this, because it checks that no FILE
# under vault/ is tracked -- not that no user-specific CONTENT sits in tools/.
# Same shape as the .obsidian/ gap: the guard covered the form, not the substance.
#
# THE DEFAULT IS EMPTY, AND THAT IS DELIBERATE. With no signal.json the radar
# tiers nothing, excludes nothing on title, and lists everything that passed the
# real filters. Shipping somebody else's vocabulary as a fallback would put the
# problem straight back.
# ---------------------------------------------------------------------------

MONEY = re.compile(r"(€|£|\$)\s?\d[\d,.]*\s?k?|\b\d{2,3}\s?k\b", re.I)

_NOTHING = re.compile(r"(?!x)x")          # matches nothing, ever


def _load_signal(path=None):
    try:
        with open(path or paths.SIGNAL, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def build_signal(cfg):
    """(POS, NEG, NEVER, IC_TITLE, HIGH_AT, MED_AT) from the user's settings.

    Absent or unreadable -> no tiering and no title exclusions. A missing config
    must never silently hide a role.
    """
    def pairs(key):
        out = []
        for row in cfg.get(key) or []:
            m = row.get("match") if isinstance(row, dict) else (row[0] if row else None)
            w = row.get("weight") if isinstance(row, dict) else (row[1] if len(row) > 1 else 0)
            if not m or str(m).startswith("<"):     # unreplaced placeholder
                continue
            try:
                re.compile(m)
            except re.error:
                print(f"  !! signal.json: {key} pattern is not valid regex, skipped: {m!r}",
                      file=sys.stderr)
                continue
            out.append((m, int(w)))
        return out

    words = [w for w in ((cfg.get("exclude_titles") or {}).get("words") or [])
             if w and not str(w).startswith("<")]
    never = re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.I) \
        if words else _NOTHING

    ic = cfg.get("individual_contributor_titles") or {}
    nouns = [n for n in (ic.get("nouns") or []) if n and not str(n).startswith("<")]
    if nouns:
        # The whitespace belongs to the GROUP, not to the last alternative in it.
        # `(senior|staff|lead )*` only ever matched "lead " -- so "Senior Software
        # Engineer" sailed through a filter written to catch exactly that.
        def grp(words):
            return "(?:(?:" + "|".join(re.escape(w) for w in words) + r")\s+)*" if words else ""
        ic_re = re.compile("^" + grp(ic.get("seniority") or []) + grp(ic.get("domains") or [])
                           + "(?:" + "|".join(re.escape(n) for n in nouns) + r")s?"
                           r"(?:\s*[-,(].*)?$", re.I)
    else:
        ic_re = _NOTHING

    th = cfg.get("thresholds") or {}
    return pairs("positive"), pairs("negative"), never, ic_re, \
        int(th.get("high", 10 ** 9)), int(th.get("med", 10 ** 9))


POS, NEG, NEVER, IC_TITLE, HIGH_AT, MED_AT = build_signal(_load_signal())


def signal(tally):
    """Render the keyword tally as HIGH / MED / LOW, deliberately not a number.

    This column used to print the raw tally under the heading "Score", and a
    radar output of 21 was duly reported to a user as a framework score -- which
    is impossible, since that scale stops at 15. The user caught it. A warning
    was added and the confusion recurred anyway.

    A word cannot be mistaken for a score out of 15 even by accident, and that is
    the entire reason this is not a number. The tally survives in raw.json for
    tuning; it does not reach anything a human reads.

    THE TALLY COUNTS WHAT THE ROLE IS ABOUT, AND NOTHING ELSE. A visible salary
    used to add 3 to it. Only one adapter returns a structured salary field, so
    that bonus was largely a measurement of WHICH SOURCE FOUND THE ROLE -- the
    same role fetched two ways scored two different ways. Three points is a
    third of the distance between the cut-points below, enough to promote a role
    across a band on the strength of the route it arrived by. A scoring term
    only some inputs can earn is a measurement of the input pipeline.
    """
    return "HIGH" if tally >= HIGH_AT else "MED" if tally >= MED_AT else "LOW"


def archive(rows, cfg, history=None):
    """Save the description of every shortlisted role, before raw.json is overwritten.

    A posting is the source document behind the score, the requirement tally, the
    angle a CV takes and the stories chosen for an interview -- and it is the only
    input in this system guaranteed to be deleted. Usually at the point it becomes
    most useful: after the employer has finished hiring and is about to interview.

    Measured rather than assumed: in one real vault, five of forty-one assessed
    roles already had unreachable postings, including the role a full application
    pack had been built for and the role the user had been rejected from. Nothing
    was left to read for the post-mortem.

    SHORTLISTED, NOT EVERYTHING FETCHED. The shortlist is by definition what is
    worth an agent reading, and the standing rule is that everything on it gets
    assessed in the same turn -- so shortlisted and assessed are the same set.
    Archiving all 130-odd fetched descriptions would keep mostly roles nobody
    ever looked at.

    It never overwrites. An archived posting is evidence of what was read at the
    time, and a later fetch of the same URL can return an edited posting -- or a
    404 page, which would replace the evidence with nothing.
    """
    where = cfg.get("postings_dir") or paths.POSTINGS
    where = os.path.abspath(where)
    try:
        os.makedirs(where, exist_ok=True)
    except OSError as e:
        print(f"  !! could not archive postings to {where}: {e}", file=sys.stderr)
        return 0, 0
    saved = skipped = 0
    for c in rows:
        body = (c.get("body") or "").strip()
        if len(body) < 400:          # nothing worth keeping; the listing had no description
            continue
        name = re.sub(r"[^\w &.-]", "", f"{c['company']} - {c['title']}").strip()[:90]
        path = os.path.join(where, name + ".txt")
        if os.path.exists(path):
            skipped += 1
            continue
        posted = c["date"] + (" (floor -- source would only say 30+ days)" if c.get("date_is_floor") else "")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{c['company']} -- {c['title']}\n"
                    f"Archived {datetime.date.today().isoformat()} by the radar\n"
                    f"Posted   {posted}\n"
                    f"Location {c['loc']}\n"
                    f"Pay      {c.get('pay') or 'not stated'}\n"
                    f"Source   {c['url']}\n"
                    f"{LEGIT.line(c, history)}\n"
                    f"{'=' * 72}\n\n{body}\n")
        saved += 1
    return saved, skipped


def load_config():
    if not os.path.exists(CONFIG):
        sys.exit(f"No search settings. Copy templates/settings/search.example.json to {CONFIG} and fill it in.")
    cfg = json.load(open(CONFIG))
    # `watch` names employers; ats_registry.json knows which ATS each uses. Expand
    # one into the other, and print what could not be expanded -- an employer
    # silently dropped for want of an adapter looks exactly like a quiet week.
    if cfg.get("watch"):
        from registry import resolve, format_report
        cfg, report = resolve(cfg)
        out = format_report(report)
        if out:
            print(out, file=sys.stderr)
    return cfg


def tally_of(text):
    t = re.sub(r"\s+", " ", (text or "").lower())
    return sum(w for rx, w in POS + NEG if re.search(rx, t))


REMOTE = re.compile(r"\b(fully\s+|100%\s+|partially\s+)?remote(ly)?\b", re.I)
EDGES = r"^[\s\-–—,:;()/|]+|[\s\-–—,:;()/|]+$"


def _norm(s):
    return re.sub(r"\W+", "", (s or "").lower())


def _loc_tokens(loc):
    return {w for w in re.split(r"\W+", (loc or "").lower()) if w}


def same_role(a, b):
    """Are these two rows the same posting reaching us from two places?

    Title and employer must match. The location decides the rest, and HOW it
    decides is the whole design.

    The old key was normalised_title[:40] plus the RAW first twelve characters
    of the location, with the employer left out entirely. One city arrives
    written three ways -- "Lyon, Rhône, France", "Lyon  France",
    "France - Lyon" -- so identical titles produced three different keys and
    one role appeared three times.

    🔴 Token INTERSECTION is the obvious repair and it is wrong. Every location
    in a country carries the country's name, so "Lyon, France" and "Nice,
    France" intersect on "france" and one real role silently disappears --
    the worst failure this tool has, because nothing reports it.

    So: SUBSET. One location's tokens must contain the other's. That folds
    "San Francisco" into "San Francisco, CA" and the three Lyon spellings
    into one, while leaving Lyon and Nice as the two different roles they
    are. An empty location is unknown rather than different, and does not
    split a role that is otherwise identical.
    """
    if _norm(a.get("title")) != _norm(b.get("title")):
        return False
    if _norm(a.get("company")) != _norm(b.get("company")):
        return False
    la, lb = _loc_tokens(a.get("loc")), _loc_tokens(b.get("loc"))
    if not la or not lb:
        return True
    return _within(la, lb) or _within(lb, la)


MIN_PREFIX = 3


def _same_token(x, y):
    """Equal, or one is a prefix of the other and the shorter is long enough.

    The prefix half exists because a country gets abbreviated: one employer
    posted the same role as "Lyon, FRA" and as "Lyon, Rhone, France",
    and a strict subset kept them apart because "fra" is not "france". Found by hand, which is the point of writing it down.

    🔴 MIN_PREFIX is the whole safety of this. "Ontario, CA" is Ontario,
    California; "Ontario, Canada" is a different continent. Let a two-letter
    token prefix-match and those become one role, and the one that disappears
    is never reported. Every two-letter state and country code is that trap --
    CA, IN, ID, LA, MO -- so two characters never match anything but themselves.
    """
    if x == y:
        return True
    lo, hi = (x, y) if len(x) < len(y) else (y, x)
    return len(lo) >= MIN_PREFIX and hi.startswith(lo)


def _within(small, big):
    return all(any(_same_token(s, b) for b in big) for s in small)


def parse_location(loc):
    """Split a location string into (is_remote, scope). The scope is the point.

    "Remote" is country-scoped almost everywhere -- Remote - UK, Remote - Texas,
    Remote, Australia -- and the suffix is the whole meaning. Read as though the
    word alone meant "anywhere", a search widens into roles the applicant cannot
    legally take: right to work, tax residency and payroll entity all sit behind
    that word and none of them appear in a listing.

    An unqualified "Remote" returns an empty scope, which means UNKNOWN and not
    global. Usually it means remote within whatever country the requisition was
    raised in.
    """
    s = (loc or "").strip()
    if not REMOTE.search(s):
        return False, s
    scope = REMOTE.sub(" ", s)
    scope = re.sub(r"\(\s*\)", " ", scope)          # "Dublin (Remote)" -> "Dublin"
    scope = re.sub(EDGES, "", re.sub(r"\s{2,}", " ", scope)).strip()
    return True, scope


def assess_location(cfg, loc, title):
    """-> (keep, scope_unknown). Exclusions are never waived by the word remote.

    They used to be: any occurrence of "remote" -- in the location OR THE TITLE
    -- skipped the exclusion list entirely, so "Remote - London" survived a
    filter that excluded London. That is exactly backwards. A role advertised as
    remote *within* an excluded geography is still in that geography, and it is
    the case the word was supposed to help with.

    The title is still read for exclusions as well as for matches, because
    location fields are employer-entered and often wrong while the title
    frequently names the real city. What the title may no longer do is EXCUSE a
    role from the exclusion list, which is the only thing it was doing before.
    """
    L = cfg.get("location", {})
    is_remote, scope = parse_location(loc)

    # Exclusions are judged on where the role actually is. For a remote role
    # that is its scope; for an unqualified remote role there is nothing to
    # judge, and inventing a geography is what the old code effectively did.
    place = scope if is_remote else (loc or "")
    against = f"{place} {title}".lower()
    # .lower() BOTH SIDES. The haystack was lowercased and the needle was not,
    # so a capitalised entry matched nothing -- and
    # templates/settings/search.example.json both
    # promises "matched case-insensitively" and ships placeholders (<your city>,
    # <your country>) that anybody fills in capitalised, because that is how
    # places are spelled. One real run fetched 4,815 roles and dropped every one
    # of them on location. The exclusion lists had the same bug pointing the
    # other way, which is worse: a capitalised `bad` entry excluded NOTHING, so
    # a role somewhere ruled out as uncommutable sailed through and got scored
    # with nothing anywhere reporting that the filter had not fired.
    if any(b and b.lower() in against for b in L.get("bad", [])):
        return False, False
    if any(e and e.lower() in against for e in L.get("edge", [])):
        return False, False

    ok = L.get("ok", [])
    if not ok:
        return True, is_remote and not scope
    if any(o and o.lower() in f"{loc} {title}".lower() for o in ok):
        # An unqualified remote role kept only because "remote" is on the ok
        # list is kept on TRUST, not on evidence. Flagged so nobody reports it
        # as a role in the user's country without checking the requisition.
        return True, is_remote and not scope
    return False, False


def parse(argv=None):
    """Flags, checked rather than sniffed.

    🔴 This was `"--adapter" in sys.argv` and friends, which has three failure
    modes and every one of them is silent:

      --adaptor greenhouse   an unknown flag is ignored, so the run does
                             something other than what was asked, and says
                             nothing about it
      --adapter greanhouse   an unknown adapter name yields an empty fetch --
                             which is EXACTLY the "silent zero" the role-radar
                             skill warns about, reachable by one typo
      --days                 a missing or non-numeric value crashes on an
                             IndexError instead of saying what was wrong

    `--help` also has to work before the config exists. It is the first thing
    anybody types, and a tool that will not describe itself until it is
    configured is a tool nobody gets as far as configuring.
    """
    ap = argparse.ArgumentParser(
        prog="radar.py", description="Find roles, score them, and report only what is new.")
    ap.add_argument("--days", type=int, default=7, metavar="N",
                    help="posting window in days (default: 7)")
    ap.add_argument("--all-open", action="store_true",
                    help="no recency filter at all. Beats --days, being the more explicit of the two")
    ap.add_argument("--adapter", choices=sorted(ADAPTERS), metavar="NAME",
                    help=f"restrict to one source: {', '.join(sorted(ADAPTERS))}")
    ap.add_argument("--reset", action="store_true", help="forget everything seen before")
    ap.add_argument("--score-only", "--retier", dest="score_only", action="store_true",
                    help="re-score the cached corpus without re-fetching")
    return ap.parse_args(argv)


# --- fetching -------------------------------------------------------------


def fetch_all(cfg, names, queries, days, dead, capped, report=None):
    """Every (adapter, query) pair. Returns {(name, q): rows}.

    ONE THREAD PER ADAPTER, each working its own query list in order.

    🔴 The obvious shape -- a thread pool over all (adapter, query) pairs, with a
    lock per adapter -- was built first and measured, and it is worse than
    serial. `map` dispatches in order, the pairs are grouped by adapter, so the
    whole pool fills with units belonging to ONE adapter and every worker but
    one blocks on that adapter's lock. Effective concurrency of about 1, plus
    the overhead. Interleaving the pairs would paper over it; one thread per
    adapter removes the lock entirely, which is the honest fix.

    The lock was never conservatism. TRUNCATED is a module attribute set during
    fetch() and read straight after, so two concurrent calls into one module
    would each read the other's answer -- and reporting a capped result set as
    complete is the exact failure TRUNCATED exists to prevent. One thread per
    adapter satisfies that by construction.

    Parallelism across adapters is the smaller half of the win anyway. The cache
    in _http is the larger: a whole-board adapter asked for the same board once
    per query, and now asks once per run.
    """
    out = {}
    if not names or not queries:
        return out

    def work(name):
        mod, rows_by_q, errors, caps = ADAPTERS[name], {}, [], []
        for q in queries:
            try:
                rows_by_q[q] = mod.fetch(cfg, q, days)
                if getattr(mod, "TRUNCATED", False):
                    caps.append(f"{name}/{q}")
            except Exception as e:
                errors.append(f"{name}/{q}: {type(e).__name__}")
        return name, rows_by_q, errors, caps

    with cf.ThreadPoolExecutor(max_workers=min(len(names), 8)) as pool:
        futures = {pool.submit(work, n): n for n in names}
        for fut in cf.as_completed(futures):
            name, rows_by_q, errors, caps = fut.result()
            for q, rows in rows_by_q.items():
                out[(name, q)] = rows
            dead.extend(errors)
            capped.extend(caps)
            # 🔴 Printed as each adapter lands rather than at the end. A run that
            # prints nothing for twenty minutes is indistinguishable from a hung
            # one, and the first version of this was silent for its whole
            # duration -- which is worse than the slowness it was fixing.
            if report:
                report(name, sum(len(r) for r in rows_by_q.values()), len(errors))

    # 🔴 Sorted into the DECLARED order -- adapter, then query -- never the order
    # the threads finished in. Dedupe keeps the first row it sees, so a
    # nondeterministic merge would attribute a role to whichever query won the
    # race and quietly reshuffle the shortlist between two runs that found
    # exactly the same jobs.
    capped.sort(key=lambda c: (names.index(c.split("/")[0]), c))
    dead.sort(key=lambda d: (names.index(d.split("/")[0]), d))
    # Rebuilt in declared order rather than left in finishing order. The caller
    # already iterates by name and query, so this changes no behaviour today --
    # which is the point: a guarantee that only holds because the caller happens
    # to do the right thing is one the next caller forgets.
    return {(n, q): out[(n, q)] for n in names for q in queries if (n, q) in out}


WINDOW_MARKER = "corpus-window.json"
SWEEP_MARKER = "last-all-open.json"


def record_window(days, state_dir=None):
    """Remember what window the CACHED CORPUS was fetched with.

    --retier re-scores raw.json without re-fetching, and it took `days` from the
    command line -- so re-tiering an --all-open corpus produced a file headed
    "7-day window" over rows that could be months old. docs/LESSONS.md already
    carries the rule this broke: a header that describes a run must be true of
    every row under it.
    """
    paths.ensure(state_dir or paths.STATE)
    with open(os.path.join(state_dir or paths.STATE, WINDOW_MARKER), "w", encoding="utf-8") as fh:
        json.dump({"days": days}, fh)


def recorded_window(state_dir=None):
    """The window the corpus was fetched with, or False if unrecorded.

    False rather than None: None is a legitimate stored value meaning --all-open.
    """
    try:
        with open(os.path.join(state_dir or paths.STATE, WINDOW_MARKER), encoding="utf-8") as fh:
            return json.load(fh)["days"]
    except (OSError, ValueError, KeyError):
        return False
SWEEP_STALE_DAYS = 7


def _sweep_path(state_dir=None):
    # state_dir is a PARAMETER, not a monkeypatched global. The first version of
    # this patched paths.STATE in setUp, another test relocated paths mid-run,
    # and the restore wrote a marker into the real vault -- which then silenced
    # the very warning these tests exist to prove. A test that writes to the
    # user's vault is a boundary violation as well as a flaky test.
    return os.path.join(state_dir or paths.STATE, SWEEP_MARKER)


def sweep_age_days(today=None, state_dir=None):
    """Days since the last --all-open sweep, or None if there has never been one.

    `today` is injectable because Date.now()-style calls make a test unrunnable.
    """
    try:
        with open(_sweep_path(state_dir), encoding="utf-8") as fh:
            last = json.load(fh)["last_all_open"]
    except (OSError, ValueError, KeyError):
        return None
    today = today or datetime.date.today()
    return (today - datetime.date.fromisoformat(last)).days


def record_sweep(today=None, state_dir=None):
    paths.ensure(state_dir or paths.STATE)
    with open(_sweep_path(state_dir), "w", encoding="utf-8") as fh:
        json.dump({"last_all_open": (today or datetime.date.today()).isoformat()}, fh)


def sweep_warning(age):
    """The line to print, or None. A windowed run cannot see an older posting.

    WHY THIS IS A CHECK AND NOT A LINE IN THE SKILL. The skill already says to
    run both, in a section headed "Run both, and know which one you ran", and
    says a year went by with only the windowed run before anybody noticed. It
    was then missed again on the first real use of this tool: four runs, all
    windowed, and two roles the user had actually APPLIED FOR were invisible
    because they were posted more than a week before the run.

    An instruction that has now failed twice is not an instruction problem.
    """
    if age is None:
        return ("  !! NO --all-open SWEEP HAS EVER RUN. A windowed run cannot see a role posted\n"
                "     before the window, however open it still is. Run:  radar.py --all-open")
    if age > SWEEP_STALE_DAYS:
        return (f"  !! LAST --all-open SWEEP WAS {age} DAYS AGO. Everything posted before this run's\n"
                f"     window has been invisible since. Run:  radar.py --all-open")
    return None


def cell(value):
    """Make a value safe to put in a markdown table cell.

    🔴 A `|` in a job title breaks the row it sits in, and job titles carry them
    constantly -- "Engineering Manager | Build & Lead a New Team", "Barden | B
    Corp". Markdown reads the pipe as a column break, so the row renders with
    every value shifted one cell left and the link in the wrong column.

    Found while counting how many roles were left to score: 43 rows of one
    sweep carried a pipe, and every one of them rendered with its columns
    shifted -- the link landing in the Posted column. The row still looks like a
    row, which is why it survived. The same failure had just been found by hand
    in the scoring table, which is the argument for fixing it in the writer
    rather than in the file.

    Newlines do the same thing more violently, turning one row into two.
    """
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def main(argv=None):
    args = parse(argv)
    all_open = args.all_open
    days = None if all_open else args.days
    only = args.adapter
    reset = args.reset
    retier = args.score_only

    if retier:
        # The corpus was fetched by an earlier run; its window is that run's, not
        # this command's. Unrecorded (an old corpus) leaves `days` alone and the
        # header says what it always said.
        remembered = recorded_window()
        if remembered is not False:
            days = remembered
    if all_open:
        record_sweep()
    else:
        warn = sweep_warning(sweep_age_days())
        if warn:
            print(warn, file=sys.stderr)

    cfg = load_config()
    HTTP.enable_cache()   # a board does not change during a run. See adapters/_http.py
    # The watch list is folded into the adapter configs before anything runs, so
    # that "watch this employer" is a fact about the employer rather than an
    # entry in whichever adapter someone happened to think of.
    emp = EMP.load()
    routed, unrouted = EMP.route(emp, cfg) if emp else ([], [])
    clash = EMP.contradictions(emp) if emp else []

    seen = {} if reset or not os.path.exists(SEEN) else json.load(open(SEEN))
    today = datetime.date.today().isoformat()
    dead, capped, dupes = [], [], 0
    skipped = []

    if retier and os.path.exists(RAW):
        found = json.load(open(RAW))
    else:
        found = {}
        names = [only] if only else [n for n in ADAPTERS
                                     if cfg.get(n, {}).get("enabled", n != "linkedin")]
        started = time.time()
        def landed(name, rows, errs):
            note = f", {errs} query/queries failed" if errs else ""
            print(f"  {name:12} fetched {rows} row(s){note}", file=sys.stderr)

        results = fetch_all(cfg, names, cfg.get("queries", []), days, dead, capped, landed)
        # 🔴 Merged in the declared order -- adapter, then query -- and NOT in
        # the order the threads happened to finish. Dedupe keeps the first row
        # it sees, so a nondeterministic merge would attribute a role to
        # whichever query won the race and quietly reshuffle the shortlist
        # between two runs that found exactly the same jobs.
        for name in names:
            got = 0
            for q in cfg.get("queries", []):
                for r in results.get((name, q), []):
                    if r["id"] in found or r["id"] in seen or any(
                            same_role(r, f) for f in found.values()):
                        dupes += 1; continue
                    r["q"] = q
                    found[r["id"]] = r
                    got += 1
            print(f"  {name:12} +{got}", file=sys.stderr)
        st = HTTP.cache_stats()
        print(f"  {'':12}  {time.time() - started:.0f}s, {st['misses']} request(s), "
              f"{st['hits']} served from the within-run cache", file=sys.stderr)
        if not found and not dead:
            print("\n  !! Every adapter returned zero and none reported an error.\n"
                  "  !! Treat this as a possible breakage, NOT a quiet week.", file=sys.stderr)

    # filter
    keep, dropped = [], {"loc": 0, "title": 0, "avoid": 0}
    for c in found.values():
        keep_it, scope_unknown = assess_location(cfg, c["loc"], c["title"])
        if not keep_it:
            dropped["loc"] += 1; continue
        c["loc_tbc"] = scope_unknown
        if NEVER.search(c["title"]) or IC_TITLE.match(c["title"].strip()):
            dropped["title"] += 1; continue
        # Before the description is fetched, so an employer already ruled out
        # costs nothing. This is the point of the list: without it the
        # assess-every-role-immediately rule spends effort on settled questions.
        why = EMP.excluded(c, emp) if emp else None
        if why:
            dropped["avoid"] += 1; skipped.append(f"{c['title'][:60]} — {why}"); continue
        keep.append(c)

    # bodies, then tier
    fetched = 0
    for c in keep:
        if not c.get("body"):
            mod = ADAPTERS.get(c.get("source", ""))
            if mod and hasattr(mod, "fetch_body"):
                c["body"] = mod.fetch_body(c); fetched += 1
                time.sleep(0.4)
        # Sector exclusions run here rather than above, because a category is
        # what catches employers the user has never heard of and that cannot be
        # judged from a company name.
        why = EMP.excluded_by_sector(c, emp) if emp else None
        if why:
            c["_drop"] = why; continue
        c["_note"] = EMP.declined_note(c, emp) if emp else None
        c["tally"] = tally_of(c["title"] + " " + c.get("body", ""))
        if not c.get("pay"):
            m = MONEY.search(c["title"])
            c["pay"] = m.group(0) if m else ""
        # A visible salary used to add 3 to the tally. It does not any more --
        # see signal(). The Pay column already tells a reader everything the
        # bonus was trying to say, and tells them the figure rather than three
        # anonymous points.
        c["signal"] = signal(c["tally"])
    if fetched:
        print(f"  read {fetched} descriptions", file=sys.stderr)

    for c in [c for c in keep if c.get("_drop")]:
        dropped["avoid"] += 1
        skipped.append(f"{c['title'][:60]} — {c['_drop']}")
    keep = [c for c in keep if not c.get("_drop")]

    paths.ensure(paths.STATE)
    json.dump(found, open(RAW, "w"), indent=1)
    if not retier:
        record_window(days)
    keep.sort(key=lambda x: (-x["tally"], x["date"]))
    high = [c for c in keep if c["signal"] == "HIGH"]
    med  = [c for c in keep if c["signal"] == "MED"]

    # The window applies only to sources that were asked for one. A board adapter
    # returns everything currently open at any age, so a file carrying board rows
    # cannot claim a window -- and this header is the only thing telling a reader
    # how old the postings below can be. Derived from the rows rather than from
    # which adapters ran, so it stays true under --retier as well.
    srcs = sorted({c.get("source", "") for c in keep})
    boards   = [n for n in srcs if not getattr(ADAPTERS.get(n), "HONOURS_DAYS", False)]
    windowed = [n for n in srcs if getattr(ADAPTERS.get(n), "HONOURS_DAYS", False)]

    if days is None:
        window = "all open postings"
    elif not srcs or not boards:
        window = f"{days}-day window"
    elif not windowed:
        window = f"watched boards only — everything open, the {days}-day window applied to nothing"
    else:
        window = f"{days}-day window on searched sources"

    paths.ensure(paths.STATE)
    with open(OUT, "w") as f:
        f.write(f"# Radar shortlist — {today} ({window})\n\n")
        f.write(f"{len(found)} fetched, {dupes} duplicates suppressed. "
                f"Dropped {dropped['loc']} on location, {dropped['title']} on title"
                + (f", {dropped['avoid']} on the avoid list" if dropped["avoid"] else "")
                + f". **{len(keep)} passed the filters: HIGH {len(high)}, MED {len(med)}, "
                f"{len(keep) - len(high) - len(med)} below the tally threshold and listed in "
                f"full below.**\n\n")
        if routed or unrouted:
            f.write(f"> Watching {len(routed)} employer(s) directly"
                    + (f". 🔴 **{len(unrouted)} on the watch list have no route and were NOT "
                       f"watched — saying otherwise would be false:** {', '.join(unrouted)}"
                       if unrouted else ".") + "\n\n")
        if clash:
            f.write(f"> 🔴 **On the watch list AND the avoid list: {', '.join(clash)}.** "
                    "Whichever wins is an accident. Resolve it in `employers.json`.\n\n")
        if days is not None and boards:
            f.write("> **The window does not apply to every source in this file.** "
                    f"{', '.join(boards)} return{'s' if len(boards) == 1 else ''} whole boards — "
                    f"everything currently open, at any "
                    f"age — so a row below can be far older than {days} days. "
                    + (f"Only {', '.join(windowed)} was asked for the last {days} days.\n\n"
                       if windowed else
                       f"Nothing here was asked for the last {days} days.\n\n"))
        if dead:
            f.write(f"> **FETCH FAILURES — this run is incomplete:** {dead}\n\n")
        if capped:
            one = len(capped) == 1
            f.write(f"> **NOT THE COMPLETE SET — {len(capped)} quer{'y' if one else 'ies'} hit "
                    f"the source's cap rather than running out of results, so there is more "
                    f"behind {'it' if one else 'them'}.** Raise `pages` for "
                    "that adapter in `vault/settings/search.json`, or narrow the query. A run that reports a "
                    "round number is usually reporting the cap, not the match count.\n>\n"
                    f"> {', '.join(capped[:12])}"
                    f"{f' … and {len(capped) - 12} more' if len(capped) > 12 else ''}\n\n")
        if days is None:
            f.write("> **This is a backlog sweep, not a weekly shortlist.** An unfiltered run "
                    "surfaces every still-open role at once, which can be dozens. Triage the "
                    "batch with the `role-triage` agent rather than assessing each in turn.\n\n")
        f.write("> SIGNAL is a keyword tally, not an assessment, and it is unrelated to the "
                "Role Scoring Framework's score. **Read MED too** — a posting with a thin "
                "description signals low regardless of how good the role is.\n\n")
        # The per-row SIGNAL repeats its section heading on purpose: these rows
        # get lifted out of the file and pasted elsewhere, and a row has to carry
        # its own label once it is separated from the heading above it.
        # Its own block, deliberately. A fake posting is not a low-scoring role,
        # it is not a role -- folding this into SIGNAL would let a strong-but-fake
        # posting outrank a real mediocre one. Only roles with something to say
        # appear: between a fifth and a third of listings are ghost jobs, but
        # listing every clean role here would bury the few that are not.
        flagged = [(c, LEGIT.concerns(c, seen)) for c in high + med]
        flagged = [(c, w) for c, w in flagged if w]
        if flagged:
            f.write(f"## Legitimacy — {len(flagged)} posting(s) worth a second look\n\n")
            f.write("> **Not a score, and it does not change one.** A role can be worth "
                    "applying to at poor odds of being real; that is the user's call. "
                    "**And nothing listed here is proof** — most of what makes a posting "
                    "fake is invisible from the posting.\n\n")
            for c, w in flagged:
                f.write(f"- **{c['company'][:28]} — {c['title'][:60]}**: {'; '.join(w)}\n")
            f.write("\n")

        # Dropped, not hidden. An exclusion the user cannot see is
        # indistinguishable from a source that found nothing, and the two mean
        # opposite things.
        if skipped:
            f.write(f"## Skipped — already decided ({len(skipped)})\n\n")
            for line in skipped[:25]:
                f.write(f"- {line}\n")
            if len(skipped) > 25:
                f.write(f"- … and {len(skipped) - 25} more\n")
            f.write("\n")

        for name, rows in (("HIGH signal", high), ("MED signal", med)):
            f.write(f"## {name}\n\n| SIGNAL | Posted | Company | Title | Location | Pay | Link |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for c in rows:
                # A "+" means the source would only say "30+ days ago", so the
                # date is a floor: the posting is AT LEAST this old and may be
                # far older. Showing it bare would make an ageing requisition
                # look fresh, which is the one thing a posting date is read for.
                posted = c["date"] + ("+" if c.get("date_is_floor") else "")
                # A dagger means this employer has been assessed and turned
                # down before -- a note, never a filter, because a role declined
                # on a commute or a start date can legitimately come back.
                who = cell(c["company"])[:28] + (" †" if c.get("_note") else "")
                # "Remote" with no country after it is unknown, not global.
                where = cell(c["loc"])[:22] + (" (scope TBC)" if c.get("loc_tbc") else "")
                f.write(f"| {c['signal']} | {posted} | {who} | "
                        f"{cell(c['title'])[:62]} | {where} | {cell(c['pay'])} | [link]({c['url']}) |\n")
            notes = sorted({c["_note"] for c in rows if c.get("_note")})
            for n in notes:
                f.write(f"\n† {n}\n")
            f.write("\n")

        # EVERYTHING ELSE. Not a courtesy -- the tier was hiding real roles.
        #
        # Measured on one run: 1,931 roles passed location and the avoid list and
        # were then dropped below the tally threshold and never shown. Among them
        # were THREE of the four roles this user had already applied for, scoring
        # 6, 8 and 10 on a scale where 18 means "read this first". The tally
        # measures the advert: one contract advertised by three agencies scored
        # 14, 14 and 9, and the third was invisible.
        #
        # Sorted by EMPLOYER, never by tally. Sorting by tally is what made a
        # keyword count look like a ranking, and reading in that order is reading
        # in copywriting order.
        rest = [c for c in keep if c["signal"] == "LOW"]
        if rest:
            f.write(f"## Everything else that passed the filters ({len(rest)})\n\n")
            f.write("> 🔴 **Not a lower tier of quality. A lower tally.** These cleared every "
                    "filter above, then scored below the keyword threshold — which measures "
                    "how closely the advert's wording matches the queries, not whether the job "
                    "suits. **Roles this user actually applied for have scored 6, 8 and 10 "
                    "here.**\n>\n"
                    "> **Sorted by employer, deliberately.** There is no ranking in this "
                    "section and none should be inferred. **Skim the titles.**\n\n")
            f.write("| Company | Title | Location | Posted | Link |\n|---|---|---|---|---|\n")
            for c in sorted(rest, key=lambda x: (x["company"].lower(), x["title"].lower())):
                posted = c["date"] + ("+" if c.get("date_is_floor") else "")
                where = cell(c["loc"])[:22] + (" (scope TBC)" if c.get("loc_tbc") else "")
                f.write(f"| {cell(c['company'])[:26]} | {cell(c['title'])[:64]} | {where} | "
                        f"{posted} | [link]({c['url']}) |\n")
            f.write("\n")

    # Before seen.json is updated and raw.json is overwritten on the next run.
    saved, skipped = archive(high + med, cfg, seen)
    if saved or skipped:
        print(f"  archived {saved} posting(s)" + (f", {skipped} already held" if skipped else ""),
              file=sys.stderr)

    if not retier:
        for c in found.values():
            # `_k` used to be popped here. There is no longer a cached key to
            # strip: same_role() compares the rows themselves.
            # requisition and posted are here so a REPOST can be spotted next run:
            # the same requisition number reappearing under a new id with a newer
            # date. Records written before this shipped have neither, and the
            # check degrades to silence rather than to a false positive.
            rec = {"title": c["title"], "company": c["company"], "first_seen": today}
            if c.get("requisition"):
                rec["requisition"] = c["requisition"]
            if c.get("date"):
                rec["posted"] = c["date"]
            seen[c["id"]] = rec
        json.dump(seen, open(SEEN, "w"), indent=1)

    print(f"\n{len(found)} fetched | HIGH {len(high)} | MED {len(med)} | "
          f"failures: {dead or 'none'}", file=sys.stderr)
    if emp:
        for who in EMP.stale(emp):
            print(f"  ?  avoid list: {who} — companies change ownership and policy. "
                  f"Still true?", file=sys.stderr)
        for who in EMP.basis_gaps(emp):
            print(f"  ?  avoid list: {who} has no reason or no basis recorded, so it "
                  f"cannot be re-judged later", file=sys.stderr)
    if unrouted:
        print(f"  !! watch list: no route for {', '.join(unrouted)} — NOT watched",
              file=sys.stderr)
    if capped:
        print(f"  !! {len(capped)} query/queries hit the source cap -- this is NOT the "
              f"complete set of open roles.", file=sys.stderr)
    print(f"-> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
