#!/usr/bin/env python3
"""Prepare a batch of roles for triage, and check the results came back.

    python3 tools/batch.py --open <slug> --employer JPMorganChase --limit 20
    python3 tools/batch.py --status <slug>
    python3 tools/batch.py --list

WHAT THIS DOES AND DOES NOT DO

🔴 It cannot spawn agents. Delegation is a runtime decision and no script can
force one — which is exactly how `.claude/agents/role-triage.md` came to exist
for the life of this repo, be named twice in the radar skill, and never once run.

🟢 What a script CAN do is make the delegation checkable. This writes the batch
to disk with every role's posting URL, and then answers one question with a
number: **how many of these have been assessed since?** A delegation nobody
verifies is the same failure one level up.

WHY THE URL IS THE KEY, AND WHY IT IS NORMALISED

An assessment is only finished when the posting URL is recorded somewhere — a
role page or the scoring table. Without it the radar re-surfaces the role on the
next sweep, which is what happened to two cluster pages written an hour apart.

🔴 And the URL is matched normalised, never by id. One role reaches the shortlist
through several sources under several URLs; matching on a LinkedIn id reported
assessed roles as outstanding, repeatedly, in one session.

WHERE IT KEEPS THINGS

`vault/state/batches/<slug>.json` — regenerable, and safe to delete. It records
what was handed out, never what was concluded: the conclusions live on role pages
and in the scoring table, which is where every other tool looks for them.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import paths  # noqa: E402

URL = re.compile(r"https?://[^\s)\]|]+")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")


def _dir():
    return os.path.join(paths.STATE, "batches")


def _path(slug):
    return os.path.join(_dir(), f"{slug}.json")


def norm(u):
    """Compare postings the way the rest of the toolchain does."""
    return re.sub(r"^https?://(www\.)?", "", u or "").rstrip("/").lower()


def assessed_urls():
    """Every posting URL recorded anywhere an assessment lives."""
    text = ""
    fw = os.path.join(paths.WIKI, "Role Scoring Framework.md")
    for f in [fw] + sorted(glob.glob(os.path.join(paths.ROLES, "*.md"))):
        try:
            with open(f, encoding="utf-8") as fh:
                text += fh.read()
        except OSError:
            pass
    return {norm(u) for u in URL.findall(text)}


def corpus():
    """Roles that PASSED the filters — read from the shortlist, never raw.json.

    🔴 THIS FUNCTION READ raw.json ON ITS FIRST DRAFT AND THAT WAS WRONG.

    `raw.json` is the corpus BEFORE the location filter. Building a batch from it
    produced seventeen JPMorganChase roles in Mumbai, Hyderabad, Glasgow, Jersey
    City, Columbus, Palo Alto, Plano and Bengaluru — and they were handed to three
    triage agents as "Dublin roles". All three flagged it independently.

    The radar was right the whole time: 20 such roles were fetched, 3 were in
    Ireland, and the shortlist contains exactly those 3. `Dropped 4734 on
    location` is the filter doing its job.

    🟢 So a batch is built from the SHORTLIST, which is the filtered output, and
    bodies are looked up in raw.json by URL afterwards. Bypassing a filter to get
    at a richer source is how a filter comes to be bypassed permanently.
    """
    shortlist = ""
    try:
        with open(os.path.join(paths.STATE, "shortlist.md"), encoding="utf-8") as fh:
            shortlist = fh.read()
    except OSError:
        return []
    bodies = {}
    try:
        with open(os.path.join(paths.STATE, "raw.json"), encoding="utf-8") as fh:
            for v in json.load(fh).values():
                if isinstance(v, dict) and v.get("url"):
                    bodies[norm(v["url"])] = v
    except (OSError, ValueError):
        pass
    out = []
    for line in shortlist.split("\n"):
        if not line.startswith("| ") or "---" in line:
            continue
        found = URL.search(line)
        if not found:
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)]
        if len(cells) < 6:
            continue
        cached = bodies.get(norm(found.group(0)), {})
        # The shortlist's own columns differ between its sections, so the cached
        # row is preferred where it exists and the table is the fallback.
        out.append({"title": cached.get("title") or cells[4],
                    "company": cached.get("company") or cells[3],
                    "url": found.group(0),
                    "loc": cached.get("loc") or cells[5],
                    "date": cached.get("date", ""),
                    "tally": cached.get("tally")})
    return out


def open_batch(slug, employer=None, title=None, limit=40):
    """Everything matching, minus what is already assessed."""
    done = assessed_urls()
    rows = []
    for v in corpus():
        if employer and employer.lower() not in (v.get("company", "") or "").lower():
            continue
        if title and title.lower() not in (v.get("title", "") or "").lower():
            continue
        if norm(v.get("url")) in done:
            continue
        rows.append({"title": v.get("title", ""), "company": v.get("company", ""),
                     "url": v.get("url", ""), "loc": v.get("loc", ""),
                     "date": v.get("date", ""), "tally": v.get("tally")})
    rows.sort(key=lambda r: r["title"])
    rows = rows[:limit]
    os.makedirs(_dir(), exist_ok=True)
    payload = {"slug": slug, "opened": datetime.date.today().isoformat(),
               "employer": employer, "title_filter": title, "roles": rows}
    with open(_path(slug), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    return payload


def status(slug):
    """(payload, [assessed], [outstanding]) — computed, never stored."""
    try:
        with open(_path(slug), encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, ValueError):
        return None, [], []
    done = assessed_urls()
    a = [r for r in payload["roles"] if norm(r["url"]) in done]
    o = [r for r in payload["roles"] if norm(r["url"]) not in done]
    return payload, a, o


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--open", metavar="SLUG", help="create a batch")
    ap.add_argument("--status", metavar="SLUG", help="how much of a batch came back")
    ap.add_argument("--list", action="store_true", help="every batch and its progress")
    ap.add_argument("--employer")
    ap.add_argument("--title", help="substring the role title must contain")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    if args.open:
        if not SLUG.match(args.open):
            print("  slug must be lowercase letters, digits and hyphens")
            return 1
        # 🔴 THE GUARDRAIL, not the reminder. A runbook is read; a precondition is
        # enforced. Opening a batch is step 3 and it cannot precede step 1, so
        # this refuses rather than warning -- a warning is a thing you scroll past.
        sys.path.insert(0, HERE)
        try:
            import pipeline
            fresh, why, fix = pipeline.stage_sweep()
        except Exception:
            fresh, why, fix = True, "", []
        if not fresh:
            print(f"\n  🔴 REFUSED: {why}.\n"
                  f"  A batch built on a stale corpus hands out roles that may already be filled,\n"
                  f"  and misses everything opened since.\n"
                  + (f"\n  Run this first:\n     {fix[0]}\n" if fix else "")
                  + "\n  Then open the batch again. `python3 tools/runbook.py radar` has the order.\n")
            return 1
        p = open_batch(args.open, args.employer, args.title, args.limit)
        print(f"\n  batch '{p['slug']}': {len(p['roles'])} role(s) not yet assessed")
        for r in p["roles"]:
            print(f"     {r['title'][:58]:58} {r['url'][-24:]}")
        print(f"\n  -> {_path(args.open)}"
              f"\n  🔴 Hand these to the role-triage agent — several in parallel for a batch this"
              f"\n     size — then `--status {args.open}` to check they actually came back.")
        return 0

    if args.status:
        payload, a, o = status(args.status)
        if payload is None:
            print(f"  no batch called {args.status!r}")
            return 1
        total = len(payload["roles"])
        print(f"\n  batch '{args.status}', opened {payload['opened']}: "
              f"{len(a)}/{total} assessed")
        for r in o:
            print(f"     [ ] {r['title'][:58]}")
        if not o:
            print("  🟢 Every role in this batch has a posting URL recorded against an "
                  "assessment.\n     That means it was FINISHED, not that it was finished well.")
        return 1 if o else 0

    if args.list:
        os.makedirs(_dir(), exist_ok=True)
        found = sorted(glob.glob(os.path.join(_dir(), "*.json")))
        if not found:
            print("  no batches open.")
            return 0
        for f in found:
            slug = os.path.basename(f)[:-5]
            payload, a, o = status(slug)
            print(f"  {slug:24} {len(a):3d}/{len(payload['roles']):3d} assessed"
                  f"   opened {payload['opened']}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
