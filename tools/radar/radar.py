#!/usr/bin/env python3
"""Role Radar — find job postings, filter them, and tier them for an agent to read.

    python3 radar.py --days 7
    python3 radar.py --score-only      # re-tier the cache without refetching
    python3 radar.py --reset           # forget what has been seen

Writes shortlist.md, raw.json and seen.json alongside this file. All three are
gitignored and regenerated; nothing here is a record of anything durable.

WHAT THIS IS NOT: the tier is a keyword tally, not a judgement, and it has no
relationship to the scoring framework's number. Its only job is to decide what
is worth an agent reading. See the failure modes in the role-radar skill --
in particular, good roles DO land in tier B, so tier B always gets read.
"""
import json, os, re, sys, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adapters import ADAPTERS                                    # noqa: E402

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


def load_config():
    if not os.path.exists(CONFIG):
        sys.exit(f"No config.json. Copy config.example.json to {CONFIG} and fill it in.")
    return json.load(open(CONFIG))


def tier_score(text):
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
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 7
    only = argv[argv.index("--adapter") + 1] if "--adapter" in argv else None
    reset, score_only = "--reset" in argv, "--score-only" in argv

    cfg = load_config()
    seen = {} if reset or not os.path.exists(SEEN) else json.load(open(SEEN))
    today = datetime.date.today().isoformat()
    dead, dupes = [], 0

    if score_only and os.path.exists(RAW):
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
    keep, dropped = [], {"loc": 0, "title": 0}
    for c in found.values():
        if not location_ok(cfg, c["loc"], c["title"]):
            dropped["loc"] += 1; continue
        if NEVER.search(c["title"]) or IC_TITLE.match(c["title"].strip()):
            dropped["title"] += 1; continue
        keep.append(c)

    # bodies, then tier
    fetched = 0
    for c in keep:
        if not c.get("body"):
            mod = ADAPTERS.get(c.get("source", ""))
            if mod and hasattr(mod, "fetch_body"):
                c["body"] = mod.fetch_body(c["id"]); fetched += 1
                time.sleep(0.4)
        c["tier_score"] = tier_score(c["title"] + " " + c.get("body", ""))
        if not c.get("pay"):
            m = MONEY.search(c["title"])
            c["pay"] = m.group(0) if m else ""
        if c["pay"]:
            c["tier_score"] += 3
    if fetched:
        print(f"  read {fetched} descriptions", file=sys.stderr)

    json.dump(found, open(RAW, "w"), indent=1)
    keep.sort(key=lambda x: (-x["tier_score"], x["date"]))
    A = [c for c in keep if c["tier_score"] >= 18]
    B = [c for c in keep if 10 <= c["tier_score"] < 18]

    with open(OUT, "w") as f:
        f.write(f"# Radar shortlist — {today} ({days}-day window)\n\n")
        f.write(f"{len(found)} fetched, {dupes} duplicates suppressed. "
                f"Dropped {dropped['loc']} on location, {dropped['title']} on title. "
                f"**Tier A {len(A)}, Tier B {len(B)}.**\n\n")
        if dead:
            f.write(f"> **FETCH FAILURES — this run is incomplete:** {dead}\n\n")
        f.write("> The score below is a keyword tally, not an assessment. **Read Tier B too** — a "
                "posting with a thin description scores low regardless of how good the role is.\n\n")
        for name, rows in (("Tier A", A), ("Tier B", B)):
            f.write(f"## {name}\n\n| Score | Posted | Company | Title | Location | Pay | Link |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for c in rows:
                f.write(f"| {c['tier_score']} | {c['date']} | {c['company'][:28]} | "
                        f"{c['title'][:62]} | {c['loc'][:22]} | {c['pay']} | [link]({c['url']}) |\n")
            f.write("\n")

    if not score_only:
        for c in found.values():
            c.pop("_k", None)
            seen[c["id"]] = {"title": c["title"], "company": c["company"], "first_seen": today}
        json.dump(seen, open(SEEN, "w"), indent=1)

    print(f"\n{len(found)} fetched | Tier A {len(A)} | Tier B {len(B)} | "
          f"failures: {dead or 'none'}\n-> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
