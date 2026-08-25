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
import json, os, re, sys, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adapters import ADAPTERS                                    # noqa: E402
import employers as EMP                                          # noqa: E402

CONFIG = os.path.join(HERE, "config.json")
RAW    = os.path.join(HERE, "raw.json")
SEEN   = os.path.join(HERE, "seen.json")
OUT    = os.path.join(HERE, "shortlist.md")

# Titles that resolve to an individual-contributor role. Matched against the
# WHOLE title, anchored -- "Senior Developer" is out, but "Director of
# Engineering, Developer Experience" is not. A substring match here silently
# discarded a genuinely strong role during development.
IC_TITLE = re.compile(
    r"^(senior |staff |principal |lead |sr\.? |junior |graduate |trainee )*"
    r"(software |backend |frontend |full.?stack |ai |ml |data |cloud |platform )*"
    r"(developer|engineer|scientist|analyst|consultant|architect|intern)s?"
    r"(\s*[-,(].*)?$", re.I)
NEVER = re.compile(r"\b(mechanical|electrical|civil|hvac|nurse|clinical|quantity surveyor|"
                   r"site engineer|apprentice|sales representative|recruiter)\b", re.I)
MONEY = re.compile(r"(€|£|\$)\s?\d[\d,.]*\s?k?|\b\d{2,3}\s?k\b", re.I)

# Tiering vocabulary. Positive terms describe the work; negative terms are
# domains that recur in listings and are reliably wrong. Tune in config later.
POS = [(r"generative ai|agentic|llm|large language model", 4),
       (r"human.in.the.loop|guardrail|ai governance|responsible ai", 4),
       (r"not a hands-on coding role|not a traditional engineering management", 6),
       (r"software development l(ife)?cycle|sdlc|release management|change management", 3),
       (r"legacy|modernis|moderniz|technical debt|re-?platform", 3),
       (r"regulated|financial services|bank|payments|insurance", 3),
       (r"portfolio|roadmap|prioritis|prioritiz|capacity planning", 2),
       (r"adoption|upskill|enablement", 2),
       (r"managers? (who )?report|leaders? report|manage managers", 3),
       (r"mentor|coach|career development|graduate", 2),
       (r"stakeholder|executive|senior leadership", 1)]
NEG = [(r"hands.on (coding|engineering|development)|write code daily", -5),
       (r"data cent(re|er)|network engineering|telecom|fibre", -6),
       (r"supply chain|logistics|warehouse|shop floor", -5),
       (r"pre.?sales|quota|revenue target|billable", -3),
       (r"on.?call 24|24x7|weekend rota", -4),
       (r"\b(4|5) days? (per week )?(in|from) (the )?office", -3)]

# The two cut-points of the keyword tally. Above HIGH_AT is worth reading first;
# above MED_AT is worth reading. Below that the posting is not surfaced at all.
HIGH_AT, MED_AT = 18, 10


def signal(tally):
    """Render the keyword tally as HIGH / MED / LOW, deliberately not a number.

    This column used to print the raw tally under the heading "Score", and a
    radar output of 21 was duly reported to a user as a framework score -- which
    is impossible, since that scale stops at 15. The user caught it. A warning
    was added and the confusion recurred anyway.

    A word cannot be mistaken for a score out of 15 even by accident, and that is
    the entire reason this is not a number. The tally survives in raw.json for
    tuning; it does not reach anything a human reads.
    """
    return "HIGH" if tally >= HIGH_AT else "MED" if tally >= MED_AT else "LOW"


def load_config():
    if not os.path.exists(CONFIG):
        sys.exit(f"No config.json. Copy config.example.json to {CONFIG} and fill it in.")
    return json.load(open(CONFIG))


def tally_of(text):
    t = re.sub(r"\s+", " ", (text or "").lower())
    return sum(w for rx, w in POS + NEG if re.search(rx, t))


def location_ok(cfg, loc, title):
    where = f"{loc} {title}".lower()
    L = cfg.get("location", {})
    if any(b in where for b in L.get("bad", [])) and "remote" not in where:
        return False
    if any(e in where for e in L.get("edge", [])):
        return False
    ok = L.get("ok", [])
    return (not ok) or any(o in where for o in ok)


def main():
    argv = sys.argv
    # --all-open means "no recency filter at all". It beats --days if both are
    # given, because it is the more explicit of the two.
    all_open = "--all-open" in argv
    days = None if all_open else (
        int(argv[argv.index("--days") + 1]) if "--days" in argv else 7)
    only = argv[argv.index("--adapter") + 1] if "--adapter" in argv else None
    reset = "--reset" in argv
    retier = "--retier" in argv or "--score-only" in argv   # old name still works

    cfg = load_config()
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
        for name in names:
            mod, got = ADAPTERS[name], 0
            for q in cfg.get("queries", []):
                try:
                    rows = mod.fetch(cfg, q, days)
                except Exception as e:
                    dead.append(f"{name}/{q}: {type(e).__name__}"); continue
                # The adapter tells us whether it stopped because the source ran
                # dry or because it ran out of its own page budget. Only the
                # first proves the result set is complete.
                if getattr(mod, "TRUNCATED", False):
                    capped.append(f"{name}/{q}")
                for r in rows:
                    key = re.sub(r"\W+", "", r["title"].lower())[:40] + "|" + r["loc"].lower()[:12]
                    if r["id"] in found or r["id"] in seen or any(
                            f["_k"] == key for f in found.values()):
                        dupes += 1; continue
                    r["_k"], r["q"] = key, q
                    found[r["id"]] = r
                    got += 1
            print(f"  {name:12} +{got}", file=sys.stderr)
        if not found and not dead:
            print("\n  !! Every adapter returned zero and none reported an error.\n"
                  "  !! Treat this as a possible breakage, NOT a quiet week.", file=sys.stderr)

    # filter
    keep, dropped = [], {"loc": 0, "title": 0, "avoid": 0}
    for c in found.values():
        if not location_ok(cfg, c["loc"], c["title"]):
            dropped["loc"] += 1; continue
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
        if c["pay"]:
            c["tally"] += 3
        c["signal"] = signal(c["tally"])
    if fetched:
        print(f"  read {fetched} descriptions", file=sys.stderr)

    for c in [c for c in keep if c.get("_drop")]:
        dropped["avoid"] += 1
        skipped.append(f"{c['title'][:60]} — {c['_drop']}")
    keep = [c for c in keep if not c.get("_drop")]

    json.dump(found, open(RAW, "w"), indent=1)
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

    with open(OUT, "w") as f:
        f.write(f"# Radar shortlist — {today} ({window})\n\n")
        f.write(f"{len(found)} fetched, {dupes} duplicates suppressed. "
                f"Dropped {dropped['loc']} on location, {dropped['title']} on title"
                + (f", {dropped['avoid']} on the avoid list" if dropped["avoid"] else "")
                + f". **HIGH {len(high)}, MED {len(med)}.**\n\n")
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
                    "that adapter in `config.json`, or narrow the query. A run that reports a "
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
                who = c["company"][:28] + (" †" if c.get("_note") else "")
                f.write(f"| {c['signal']} | {posted} | {who} | "
                        f"{c['title'][:62]} | {c['loc'][:22]} | {c['pay']} | [link]({c['url']}) |\n")
            notes = sorted({c["_note"] for c in rows if c.get("_note")})
            for n in notes:
                f.write(f"\n† {n}\n")
            f.write("\n")

    if not retier:
        for c in found.values():
            c.pop("_k", None)
            seen[c["id"]] = {"title": c["title"], "company": c["company"], "first_seen": today}
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
