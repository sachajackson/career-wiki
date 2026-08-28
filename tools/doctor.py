#!/usr/bin/env python3
"""Is this set up, and what will silently do nothing if it is not?

    python3 tools/doctor.py

WHY. Setting this up means three config files copied from examples, a git
setting, a CV in a folder, and up to two API keys. Nothing answered "am I ready"
-- `sources_check.py` answers a third of it and only about job sources.

THE FAILURE THIS IS REALLY FOR. A config copied from the example and never
filled in **looks configured and returns nothing.** `templates/settings/search.example.json` says
so in its own first line: leave the angle-bracket values as they are and the
location filter matches nothing, so the radar finds no roles and reports a quiet
week. A missing file announces itself. A file full of placeholders does not, and
that is the one worth a check.

WHAT IT WILL NOT DO. It makes no network calls, so it is fast, works offline,
and cannot tell you an endpoint answers -- `sources_check.py` does that and says
so. And OPTIONAL never means broken: most of this is optional, and reporting an
unconfigured thing as a fault sends people to fix something they never wanted.
"""
import glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Seven paths were pinned in this file, which made it the place a vault move
# would break most quietly: a check reading the wrong path reports OPTIONAL, not
# an error. They now come from one module.
sys.path.insert(0, os.path.join(HERE, "lib"))
import paths  # noqa: E402
ROOT = os.path.dirname(HERE)

OK, MISSING, PLACEHOLDER, OPTIONAL, WARN = "OK", "MISSING", "PLACEHOLDER", "OPTIONAL", "WARN"
MARK = {OK: "OK  ", MISSING: "!!  ", PLACEHOLDER: "!!  ", OPTIONAL: "--  ", WARN: "??  "}
# Worst first, so the report leads with what needs doing.
ORDER = [MISSING, PLACEHOLDER, WARN, OPTIONAL, OK]

MIN_PYTHON = (3, 8)


def placeholders(value):
    """Angle-bracket values left as shipped. Recursive: they nest in the examples."""
    found = []
    if isinstance(value, str):
        if value.startswith("<") and value.endswith(">"):
            found.append(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            if not k.startswith("_"):
                found += placeholders(v)
    elif isinstance(value, list):
        for v in value:
            found += placeholders(v)
    return found


def check_python():
    v = sys.version_info
    if (v.major, v.minor) < MIN_PYTHON:
        return MISSING, (f"Python {v.major}.{v.minor}; this needs "
                         f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer")
    return OK, f"Python {v.major}.{v.minor}.{v.micro}, no packages to install"


def check_git():
    """A ZIP download works, but it can never be updated. Worth knowing early."""
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        return WARN, ("not a git clone — everything works, but you will never get an "
                      "update. Re-clone with git when convenient")
    try:
        hooks = subprocess.run(["git", "-C", ROOT, "config", "core.hooksPath"],
                               capture_output=True, text=True).stdout.strip()
    except Exception:
        return WARN, "git is not on PATH"
    if hooks != "githooks":
        return WARN, ("the commit guard is not installed. It normally installs itself at the "
                      "start of a session — if you are not using an agent here, run "
                      "`git config core.hooksPath githooks` yourself. It is what refuses "
                      "personal material even against `git add -f`")
    return OK, "clone, with the commit guard installed"


def check_updatable():
    """🔴 Will the next `git pull` actually apply, or abort?

    A backlog entry claimed a tuned `SCHEMA.md` or `.claude/skills/` file was
    "silently clobbered by a pull". **Tested on a throwaway clone rewound six
    commits, and it is not true** — git refuses, loudly:

        error: Your local changes to the following files would be overwritten
        by merge: SCHEMA.md ... Aborting

    🟢 Nothing is lost. 🔴 But nothing is UPDATED either, and that failure is
    quiet in the way that matters: the pull is one step of `runbook.py update`,
    the four steps after it read the code that is already there, and every one
    of them then passes. A user who does not read the git output concludes they
    are current when they are several versions behind.

    So this reports it BEFORE the pull, and names the files to deal with.
    🟡 It makes no network call and cannot say whether an update exists — only
    whether one could land.
    """
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        return OPTIONAL, "not a git clone — reported by the copy check above"
    try:
        r = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True, timeout=20)
    except Exception as e:
        return WARN, f"could not ask git: {type(e).__name__}"
    if r.returncode != 0:
        return WARN, "git could not report the working tree"
    # 🟢 Only TRACKED, MODIFIED files block a merge. Untracked ones are excluded
    # above, and everything under vault/ is ignored, so a user's own data cannot
    # trigger this — which is the point of the boundary.
    changed = [ln[3:].strip() for ln in r.stdout.splitlines() if ln[:2].strip()]
    if not changed:
        return OK, "a `git pull` would apply cleanly"
    shown = ", ".join(changed[:3]) + (f" and {len(changed) - 3} more" if len(changed) > 3 else "")
    return WARN, (f"{len(changed)} tracked file(s) modified locally, so `git pull` will ABORT "
                  f"rather than update: {shown}. Commit or stash them, then pull")


# Files that SHIP. Everything here reaches a stranger who clones the repo.
_SHIPPED = ("templates", "tools", "docs", ".claude", "githooks")
_SHIPPED_FILES = ("README.md", "SCHEMA.md", "AGENTS.md", "BACKLOG.md", "PRIVACY.md")


def _generic_vocabulary():
    """Every string the shipped EXAMPLES already use.

    🟢 The neat part: if a value appears in a template, it is generic by
    definition — the suite proves those are placeholders or listed identifiers.
    So this needs no stoplist of common words and cannot drift from one.
    """
    out = set()
    for f in glob.glob(os.path.join(ROOT, "templates", "settings", "*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue
        out |= {w for w in re.findall(r"[A-Za-z][A-Za-z .-]{2,}", text)}
    return {w.strip().lower() for w in out}


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


REGISTRY = "tools/radar/ats_registry.json"


def check_settings_not_shipped():
    """🔴 Do the employers on YOUR lists appear in files that ship?

    `templates/settings/search.example.json` once shipped with one user's real commuting geography,
    home county included, in a public repo under their own name. **Nobody wrote
    that file — it was a working config with `.example` in the name**, which is
    how almost every example file in every project gets made.

    🟡 The suite proves the shipped examples are placeholders, and that is the
    generic half. **It cannot do this half**: a public repo must not carry a
    denylist of its author's private details, so the comparison has to happen
    where the private data already is. That is here.

    🔴 SCOPED TO EMPLOYER NAMES ON PURPOSE, and the first draft was not. Scanning
    every settings value found 229 "leaks" — because a signal vocabulary is
    generic by design and the docs legitimately discuss the same words. **A check
    that reports 229 findings on a healthy repo is one nobody reads.** Who you
    watch and who you refuse to work for is the part that is genuinely yours.

    🟡 `tools/radar/ats_registry.json` is excluded: it maps employers to their ATS
    and is contributed back deliberately — a public fact about a company, not a
    fact about you.

    🟢 WARN, never MISSING. Several of these are legitimate and only you can
    say which, so it names files and stops.
    """
    in_registry = []
    reg = os.path.join(paths.SETTINGS, "employers.json")
    if not os.path.exists(reg):
        return OPTIONAL, "no employers.json — nothing of yours to leak"
    try:
        with open(reg, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return OPTIONAL, "employers.json unreadable — reported by the settings check"
    names, stack = set(), [doc]
    while stack:
        v = stack.pop()
        if isinstance(v, dict):
            stack += [x for k, x in v.items() if not str(k).startswith("_")]
        elif isinstance(v, list):
            stack += list(v)
        elif isinstance(v, str):
            t = v.strip()
            # A name, not a date, a reason, or a tag.
            if 4 <= len(t) <= 40 and not re.fullmatch(r"[\d-]+", t) and " " not in t[:2] \
                    and not t.endswith(".") and t[:1].isupper():
                names.add(t)
    if not names:
        return OPTIONAL, "no employer names recorded"
    try:
        tracked = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True,
                                 text=True, timeout=30).stdout.split("\n")
    except Exception:
        return OPTIONAL, "git could not list tracked files"
    hits = []
    for rel in tracked:
        if not rel or rel.endswith((".png", ".pdf", ".docx", ".pyc")):
            continue
        if rel == REGISTRY:
            # 🟡 Excluded, and SAID rather than skipped. Mapping an employer to
            # their ATS is a public fact about a company, and the registry is
            # contributed back on purpose -- but its COMPOSITION still reflects
            # who one person looked up, and a silent exclusion hides that.
            reg_body = _read(os.path.join(ROOT, rel))
            in_registry = [n for n in names
                           if re.search(r"\b" + re.escape(n) + r"\b", reg_body)]
            continue
        full = os.path.join(ROOT, rel)
        if not os.path.isfile(full):
            continue
        try:
            with open(full, encoding="utf-8", errors="ignore") as fh:
                body = fh.read()
        except OSError:
            continue
        for n in names:
            if re.search(r"\b" + re.escape(n) + r"\b", body):
                hits.append(f"{rel}: {n!r}")
    note = (f"; {len(in_registry)} also named in the shipped ATS registry, which is a public fact "
            f"about a company but whose CONTENTS still say who you looked up" if in_registry else "")
    if hits:
        where = "; ".join(sorted(set(hits))[:3])
        return WARN, (f"{len(set(hits))} appearance(s) of an employer from your own lists in "
                      f"TRACKED files: {where}. Some may be legitimate — **read each one** "
                      f"before deciding{note}")
    return OK, f"none of your {len(names)} listed employer(s) appear in tracked files{note}"


def check_gaps():
    """🔴 Are the wiki's closed questions findable, and do any pages reopen them?

    `not recorded` and `recorded as not held` look identical to a search and mean
    opposite things. A capability was put to the user three days after the wiki
    had closed it in two places with the words "stop asking", because searching
    for EVIDENCE of it found none.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    try:
        import gaps as _g
        rows = _g.gaps()
    except Exception as e:
        return WARN, f"could not check: {type(e).__name__}: {e}"
    if not rows:
        return OPTIONAL, "no standing-gaps table yet — nothing has been closed"
    unfindable = [r["gap"] for r in rows if not _g.RESOLVED.search(r["status"])]
    risky = [(r["gap"], p) for r in rows for p, _ in _g.undistinguished(r)]
    if unfindable or risky:
        bits = []
        if unfindable:
            bits.append(f"{len(unfindable)} gap(s) have no resolution word in their status")
        if risky:
            bits.append(f"{len(risky)} declared near-miss page(s) carry no distinction")
        return MISSING, "; ".join(bits) + ". Run `python3 tools/gaps.py`"
    pressing = [r["gap"] for r in rows if _g.demands(r["where"]) >= 3]
    note = (f"; {len(pressing)} demanded 3+ times and worth deciding once" if pressing else "")
    return OK, f"all {len(rows)} closed question(s) findable, no page reopens one{note}"


def check_sources():
    d = paths.SOURCES
    files = [f for f in os.listdir(d) if not f.startswith(".") and f != "README.md"] \
        if os.path.isdir(d) else []
    if not files:
        return MISSING, ("vault/sources/ has no CV in it. /career-init stops without one, and "
                         "a messy CV is more useful than a tidy one")
    return OK, f"{len(files)} file(s) — {', '.join(sorted(files)[:3])}"


def check_wiki():
    d = paths.WIKI
    pages = [f for f in os.listdir(d) if f.endswith(".md")] if os.path.isdir(d) else []
    if not pages:
        return OPTIONAL, "no wiki yet. Run /career-init — that is the next step, not a fault"
    # 🔴 A migrated vault arrives with pages and neither of these, because the
    # sorter files what it is given and a drop of somebody's pages does not
    # include them. Every operation in SCHEMA.md ends "update index.md, append
    # to log.md", so a wiki without them fails quietly: the agent writes an
    # entry to a file nobody made, or does not write one at all.
    missing = [f for f in ("index.md", "log.md") if f not in pages]
    if missing:
        return WARN, (f"{len(pages)} page(s), but no {' or '.join(missing)}. "
                      f"Copy templates/{missing[0]} into vault/wiki/ — every operation "
                      f"ends by writing to these, so without them the record is not kept")
    return OK, (f"{len(pages)} page(s). After any tool update run template_drift.py for "
                f"these and settings_drift.py for vault/settings/")


def _config(path, name, what):
    if not os.path.exists(path):
        ex = os.path.join("templates", "settings",
                          os.path.basename(path).replace(".json", ".example.json"))
        return OPTIONAL, f"no {name}. Copy {ex} into vault/settings/ and fill it in — {what}"
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except ValueError as e:
        return MISSING, f"{name} is not valid JSON: {e}"
    left = placeholders(cfg)
    if left:
        return PLACEHOLDER, (f"{name} still has {len(left)} example value(s) in it — "
                             f"{', '.join(sorted(set(left))[:3])}. **It looks configured and "
                             f"will match nothing**")
    return OK, None, cfg


def check_radar_config():
    r = _config(paths.SEARCH, "settings/search.json",
                "without it only the employer-board adapters run")
    if r[0] != OK:
        return r[0], r[1]
    cfg = r[2]
    if not cfg.get("queries"):
        return PLACEHOLDER, "no queries listed, so the radar has nothing to search for"
    watch = len(cfg.get("watch", []))
    return OK, (f"{len(cfg['queries'])} quer{'y' if len(cfg['queries']) == 1 else 'ies'}"
                + (f", {watch} watched employer(s) by name" if watch else "")
                + ". Run sources_check.py to see whether they answer")


def check_quotes():
    """🔴 Does an assessment quote something the posting does not contain?

    `verify.py` protects an outgoing CV against the wiki. Nothing protected the
    wiki's own role pages, which are model-written and rest entirely on
    quotation -- every score here is argued from a line lifted out of an advert.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    try:
        import quotes
        postings = quotes.load_postings()
        if not postings:
            return OPTIONAL, "no archived postings yet — nothing to check assessments against"
        import glob as _g
        bad = 0
        checked = 0
        for path in _g.glob(os.path.join(paths.ROLES, "*.md")):
            fn, missing, n = quotes.check(path, postings)
            if not fn:
                continue
            checked += 1
            if [m for m in missing if m[0] == "absent" and m[2] == "claimed"]:
                bad += 1
    except Exception as e:
        return WARN, f"could not check: {type(e).__name__}: {e}"
    if bad:
        return MISSING, (f"{bad} of {checked} assessment(s) quote the employer on something the "
                         f"posting does not say. Run `python3 tools/quotes.py`")
    return OK, (f"{checked} assessment(s) checked; every line attributed to an employer is in "
                f"their posting")


def check_scores():
    """🔴 Do the numbers hang together, and has anybody argued with them?

    Two copies of every score exist -- the role page and the scoring table --
    and they drift. One page had been rescored 13 -> 12 and said so in as many
    words while its table row still read 13, which is the copy that gets read
    when roles are compared against each other.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    try:
        import scores
        faults, due, scored = scores.audit()
    except Exception as e:
        return WARN, f"could not check: {type(e).__name__}: {e}"
    if not scored:
        return OPTIONAL, "no scored assessments yet — nothing to check"
    if faults:
        return MISSING, (f"{len(faults)} fault(s) in the score arithmetic or between a page "
                         f"and its table row. Run `python3 tools/scores.py`")
    # 🔴 The review BACKLOG is deliberately not a finding here. doctor reports
    # whether the system is configured; a queue of unargued-with assessments is
    # outstanding work, and `pipeline.py` already owns it as its own stage.
    # Reporting it in both places made doctor exit non-zero on a healthy install
    # and broke four tests that were right to fail.
    note = f"; {len(due)} at FIT {scores.REVIEW_AT}+ await `role-review` (see pipeline)" if due else ""
    return OK, f"all {scored} score(s) add up and agree with the table{note}"


def check_oracle_names():
    """🔴 An Oracle site configured with no employer name silently disables the
    exclusion list for that whole adapter.

    `oracle.py` falls back to the site slug when `names` has no entry, so a row's
    company field reads `CX_1001` rather than the employer. `employers.py` matches
    every avoid, avoid_sectors and watch rule against that field -- so none of them
    can ever fire, and dedup can never recognise the same job arriving from
    LinkedIn under the employer's real name.

    🔴 It was documented as cosmetic. `templates/settings/search.example.json` said `names` "only
    prettifies the site slug in the shortlist", which is why nobody set it, and
    1,308 rows in one vault carried a site code as their employer.
    """
    if not os.path.exists(paths.SEARCH):
        return OPTIONAL, "no search.json — the radar runs on employer boards only"
    try:
        with open(paths.SEARCH, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except (OSError, ValueError):
        return OPTIONAL, "search.json unreadable — reported by the search check"
    oracle = cfg.get("oracle") or {}
    sites = [e for e in (oracle.get("employers") or []) if isinstance(e, dict)]
    if not sites:
        return OPTIONAL, "no Oracle employers configured"
    # 🟢 Ask the adapter rather than reimplementing its key order. A site-only
    # label is still valid where one tenant uses that site, and a second
    # implementation of that rule would drift from the first.
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "radar"))
    try:
        from adapters import oracle as _ora
    except Exception as e:
        return WARN, f"could not load the Oracle adapter: {type(e).__name__}: {e}"
    unnamed = []
    for e in sites:
        host, site = e.get("host") or "", e.get("site") or ""
        if not site:
            continue
        if _ora.employer_name(oracle, host, site) == _ora.tenant(host):
            unnamed.append(f"{_ora.tenant(host)}/{site}")
    if unnamed:
        return MISSING, (f"{len(unnamed)} Oracle tenant(s) resolve to no employer name: "
                         f"{', '.join(unnamed[:3])}. Their rows carry the tenant slug, so "
                         f"avoid/watch rules never match them. Key on \"<host>|<site>\" when two "
                         f"tenants share a site")
    return OK, f"all {len(sites)} Oracle tenant(s) resolve to an employer name"


def check_foreign_state():
    """🔴 What another tool left beside the code, naming the user's files.

    `.obsidian/` sat at the repository root, untracked but not ignored, and its
    workspace.json named vault settings and wiki pages by path. One `git add -A`
    would have published that list to a public remote.

    Advisory here and hard-failing in pre-commit, which is the right split: this
    runs every session and is a property of the working tree, not of a commit.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    try:
        import foreign_state
        found = foreign_state.scan(os.path.dirname(here))
    except Exception as e:
        return WARN, f"could not check: {type(e).__name__}: {e}"
    if not found:
        return OK, ("nothing untracked names a file under vault/. "
                    "Editors and sync tools drop state beside a repo and it is not ignored by default")
    names = ", ".join(p for p, _ in found[:3])
    return MISSING, (f"{len(found)} untracked, un-ignored file(s) name a file under vault/: "
                     f"{names}. **Untracked is not ignored — one `git add -A` publishes them.** "
                     f"Run `python3 tools/foreign_state.py` for detail")


def check_profile():
    """🟡 OPTIONAL, and reported anyway — because both defaults are silent.

    Missing `spelling` means the CV linter checks no locale, which is correct
    (enforcing one nobody declared was the original bug) but invisible. Missing
    `working_days_per_year` means nothing can annualise a contract day rate, and
    the failure there is worse than silence: an agent guessed 250 and reported a
    €700-750/day contract as €175-190k when at the user's own 220 it is
    €154-165k. Fourteen percent high, on the number that decides whether a
    contract clears their floor.

    So this never fails a run -- most people never need it -- but it says what is
    not set rather than letting a guess stand in.
    """
    if not os.path.exists(paths.PROFILE):
        return OPTIONAL, ("no settings/profile.json. CV spelling checks are off, and nothing can "
                          "annualise a contract day rate — copy templates/settings/"
                          "profile.example.json if either matters")
    try:
        with open(paths.PROFILE, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except ValueError as e:
        return PLACEHOLDER, f"settings/profile.json is not valid JSON: {e}"
    have, missing = [], []
    spelling = str(cfg.get("spelling", "")).lower()
    (have if spelling in ("ie-uk", "us", "off") else missing).append(
        f"spelling={spelling}" if spelling in ("ie-uk", "us", "off") else "spelling")
    days = cfg.get("working_days_per_year")
    # 🔴 261 is every weekday in a year with no leave taken at all, so anything
    # above it is not a working year. The first version of this bound allowed
    # 366 -- a year with no weekends in it -- which a test caught.
    if isinstance(days, (int, float)) and not isinstance(days, bool) and 100 < days <= 261:
        have.append(f"{int(days)} working days")
    else:
        missing.append("working_days_per_year")
    # 🔴 An ABSENT profile is OPTIONAL — most people never need one. A profile
    # that exists with nothing usable in it was copied from the example and never
    # edited, which is a different thing and the one worth saying out loud.
    if not have:
        return PLACEHOLDER, ("settings/profile.json holds only example values, so it is doing "
                             "nothing: CV spelling checks are off and no day rate can be "
                             "annualised. 🔴 working_days_per_year has no safe default — ask")
    return OK, ", ".join(have) + (f". Not set: {', '.join(missing)}" if missing else "")


def check_signal():
    """🔴 A vault without this file gets a completely clean bill of health while
    the radar tiers every role LOW.

    The tiering vocabulary moved into the vault on 2026-08-26, correctly -- it
    was one user's preferences sitting in shared code. But an update that adds a
    required vault file cannot add it to a vault, and nothing here noticed the
    absence. The radar still runs, still fetches, still writes a shortlist; HIGH
    and MED are simply always empty and every role lands in the catch-all
    section. That reads as a thin week, not as a broken install.
    """
    # 🔴 Scoped to a configured radar, and that scoping is the check working.
    # The first version fired on an install with no search.json at all -- nothing
    # searches there, so nothing needs a vocabulary, and calling that "needs
    # attention" is how a check earns its way into being ignored.
    if not os.path.exists(paths.SEARCH):
        return OPTIONAL, ("no vocabulary, and nothing searches yet either. It matters once "
                          "settings/search.json exists")
    if not os.path.exists(paths.SIGNAL):
        return PLACEHOLDER, ("settings/signal.json is missing, so nothing can ever signal "
                             "HIGH or MED — the radar still runs and every role lands in "
                             "the catch-all section, which looks like a quiet week. Copy "
                             "templates/settings/signal.example.json and edit it")
    try:
        with open(paths.SIGNAL, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except ValueError as e:
        return PLACEHOLDER, f"settings/signal.json is not valid JSON: {e}"
    pos = [w for w in cfg.get("positive", []) if not str(w.get("match", "")).startswith("<")]
    if not pos:
        return PLACEHOLDER, ("settings/signal.json has no positive patterns filled in. Copied "
                             "from the example and never edited looks exactly like configured")
    hi = cfg.get("thresholds", {}).get("high")
    return OK, (f"{len(pos)} positive pattern(s)"
                + (f", HIGH at {hi}" if hi is not None else "")
                + ". Tuning it changes what reaches you — nothing else does")


def check_employers():
    p = paths.EMPLOYERS
    if not os.path.exists(p):
        return OPTIONAL, ("no watch/avoid list. Optional — without it nothing is filtered "
                          "before scoring and no employer is watched by name")
    try:
        with open(p, encoding="utf-8") as fh:
            e = json.load(fh)
    except ValueError as ex:
        return MISSING, f"employers.json is not valid JSON: {ex}"
    # 🔴 The example's only watch entry is literally `<Employer name>`, and without
    # this the check reported "1 watched, 1 avoided, 1 declined" on it. A watch
    # list of placeholders watches nobody, and says nothing while doing it.
    left = placeholders(e)
    if left:
        return PLACEHOLDER, (f"employers.json still has {len(left)} example value(s) in it — "
                             f"{', '.join(left[:3])}. **Nobody is actually being watched**")
    return OK, (f"{len(e.get('watch', []))} watched, {len(e.get('avoid', []))} avoided, "
                f"{len(e.get('declined', []))} declined")


def check_oversight():
    p = paths.REVIEW
    if not os.path.exists(p):
        return OPTIONAL, ("no reviewer configured. 🟢 `review.py --dry-run` prints the prompt "
                          "to paste into any other vendor's chat window, which costs nothing "
                          "and works as well — the key is only for automating it")
    try:
        with open(p, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except ValueError as e:
        return MISSING, f"settings/review.json is not valid JSON: {e}"
    provider = cfg.get("provider")
    if not provider:
        return PLACEHOLDER, "no provider set"
    env = (cfg.get(provider) or {}).get("api_key_env", "")
    if env and not os.environ.get(env):
        return MISSING, f"provider is {provider!r} but ${env} is not set in this shell"
    return OK, (f"{provider}. 🔴 It must not be the vendor whose model wrote the documents — "
                f"review.py refuses if `authored_by` matches")


def check_registry():
    p = os.path.join(HERE, "radar", "ats_registry.json")
    if not os.path.exists(p):
        return MISSING, ("ats_registry.json is not here. It ships with the repo, so a copy "
                         "without it is incomplete — re-clone")
    try:
        with open(p, encoding="utf-8") as fh:
            reg = json.load(fh)
    except ValueError as e:
        return MISSING, f"ats_registry.json is not valid JSON: {e}"
    return OK, f"{len(reg.get('employers', []))} employer(s), shared and shipped"


CHECKS = [
    ("python", check_python),
    ("this copy", check_git),
    ("updatable", check_updatable),
    ("other tools", check_foreign_state),
    ("quotes", check_quotes),
    ("scores", check_scores),
    ("oracle names", check_oracle_names),
    ("settings leak", check_settings_not_shipped),
    ("closed questions", check_gaps),
    ("registry", check_registry),
    ("your CV", check_sources),
    ("your wiki", check_wiki),
    ("job search", check_radar_config),
    ("signal", check_signal),
    ("profile", check_profile),
    ("watch/avoid", check_employers),
    ("oversight", check_oversight),
]


def main():
    results = []
    for name, fn in CHECKS:
        try:
            verdict, detail = fn()[:2]
        except Exception as e:                    # a check must never be the thing that breaks
            verdict, detail = WARN, f"check raised {type(e).__name__}: {e}"
        results.append((name, verdict, detail))

    results.sort(key=lambda r: (ORDER.index(r[1]) if r[1] in ORDER else 0, r[0]))
    width = max(len(n) for n, _, _ in results)
    for name, verdict, detail in results:
        print(f"  {MARK.get(verdict, '?   ')}{name:<{width}}  {verdict:<11}  {detail}")

    blocking = [r for r in results if r[1] in (MISSING, PLACEHOLDER)]
    print(f"\n  {len([r for r in results if r[1] == OK])} ready, "
          f"{len([r for r in results if r[1] == OPTIONAL])} not set up (fine), "
          f"{len(blocking)} needing attention.")
    if any(r[1] == PLACEHOLDER for r in results):
        print("  🔴 A config left on its example values LOOKS configured and matches nothing.\n"
              "     That is a quiet week that never happened.")
    print("\n  This reads files. It makes no network calls, so it cannot tell you a source\n"
          "  answers — `python3 tools/radar/sources_check.py` does that.")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
