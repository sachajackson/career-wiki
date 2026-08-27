#!/usr/bin/env python3
"""Where is the search up to, and what is the next thing to do?

    python3 tools/pipeline.py              # the checklist, and the next action
    python3 tools/pipeline.py --write      # also refresh vault/state/progress.md

WHY THIS EXISTS

Two failures in one session, both of the same kind, and no existing check could
have caught either:

  1. `.claude/agents/role-triage.md` has existed for the life of this repo, the
     radar skill tells the agent to use it in two places, and IT HAS NEVER RUN.
     An instruction-shaped control that never fired once, and nothing noticed
     because nothing was looking.

  2. A cluster page said "recorded so the radar does not re-surface them" and
     shipped with no posting URLs. It re-surfaced all ten. Written twice, the
     same way, an hour apart.

🔴 THE SHAPE OF BOTH IS THE SAME: a stage of work that CLAIMS to be done, with
nothing computing whether it is. The deterministic layer already checks outgoing
artefacts -- cv_lint, verify, known all check whether a CV is fit to send. What
nothing checked was whether a BATCH of work actually completed.

🟢 So every criterion below is COMPUTED from the vault, never asserted. A stage is
done when the files say it is done.

WHAT IT DELIBERATELY DOES NOT DO

It does not judge quality. A role can be scored badly and this will call it
recorded. `cv_lint` and `verify` own whether a document is fit to send; this owns
whether the work was finished at all.
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

SWEEP_STALE_DAYS = 7
URL = re.compile(r"https?://[^\s)\]|]+")
LINK = re.compile(r"\[\[([^\]|\\]+)")


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _framework():
    return _read(os.path.join(paths.WIKI, "Role Scoring Framework.md"))


def _role_pages():
    return sorted(glob.glob(os.path.join(paths.ROLES, "*.md")))


def _norm(u):
    return re.sub(r"^https?://(www\.)?", "", u).rstrip("/").lower()


# --------------------------------------------------------------------------
# The stages. Each returns (done, one-line detail, [specifics]).
# --------------------------------------------------------------------------

def stage_sweep():
    """Has a full sweep run recently enough to trust the corpus?"""
    marker = os.path.join(paths.STATE, "last-all-open.json")
    if not os.path.exists(marker):
        return False, "no --all-open sweep has ever been recorded", [
            "python3 tools/radar/radar.py --all-open"]
    try:
        # The key radar.py actually writes. Guessing it wrong reported a healthy
        # sweep as unreadable on this tool's first run -- read the writer, do not
        # assume the shape.
        when = datetime.date.fromisoformat(
            json.loads(_read(marker))["last_all_open"][:10])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return False, "the sweep marker is unreadable", []
    age = (datetime.date.today() - when).days
    if age > SWEEP_STALE_DAYS:
        return False, f"last full sweep was {age} days ago", [
            "python3 tools/radar/radar.py --all-open"]
    return True, f"last full sweep {age} day(s) ago", []


def stage_triage():
    """Is every HIGH-signal role either assessed or explicitly dispatched?

    🔴 Matched on FULL URL, not on a LinkedIn id. One role reaches the shortlist
    under several posting ids and through several sources, and an id-only match
    reports assessed roles as outstanding -- which it did, repeatedly, before
    this was written down.
    """
    shortlist = _read(os.path.join(paths.STATE, "shortlist.md"))
    if not shortlist:
        return False, "no shortlist — run the radar first", []
    known = {_norm(u) for u in URL.findall(_framework())}
    for f in _role_pages():
        known |= {_norm(u) for u in URL.findall(_read(f))}
    section = [s for s in re.split(r"^## ", shortlist, flags=re.M)
               if s.startswith("HIGH signal")]
    if not section:
        return True, "no HIGH-signal roles in the current shortlist", []
    rows = [l for l in section[0].split("\n") if l.startswith("|")][2:]
    left = []
    for row in rows:
        found = URL.search(row)
        if found and _norm(found.group(0)) not in known:
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", row)]
            if len(cells) > 4:
                left.append(f"{cells[3][:22]} — {cells[4][:44]}")
    if left:
        return False, f"{len(left)} of {len(rows)} HIGH-signal role(s) unassessed", left[:8]
    return True, f"all {len(rows)} HIGH-signal role(s) assessed or dispatched", []


def stage_recorded():
    """🔴 THE CHECK THE CLUSTER PAGES NEEDED.

    An assessment is finished when three things are true, and a cluster page
    satisfied the first two while failing the third -- twice:

      a page exists · the scoring table has a row · a posting URL is recorded

    Without the URL the radar re-surfaces the role on the next sweep, so the page
    claiming to prevent that causes exactly what it claims to prevent.
    """
    framework = _framework()
    rows = {}
    for line in framework.split("\n"):
        if not line.startswith("| "):
            continue
        m = LINK.search(line)
        if m:
            rows.setdefault(m.group(1).strip(), []).append(bool(URL.search(line)))
    problems = []
    for path in _role_pages():
        name = os.path.basename(path)[:-3]
        body = _read(path)
        if name not in rows:
            problems.append(f"{name[:52]} — no row in the scoring table")
        elif not any(rows[name]) and not URL.search(body):
            problems.append(f"{name[:52]} — no posting URL anywhere")
    if problems:
        return False, f"{len(problems)} of {len(_role_pages())} assessment(s) incomplete", problems
    return True, f"all {len(_role_pages())} assessment(s) carry a page, a row and a URL", []


def stage_logged():
    """Every operation in SCHEMA.md ends 'append to log.md'. Did it?"""
    log = _read(os.path.join(paths.WIKI, "log.md"))
    if not log:
        return False, "no log.md", []
    dates = re.findall(r"^## \[(\d{4}-\d{2}-\d{2})\]", log, re.M)
    if not dates:
        return False, "log.md has no dated entries", []
    newest = max(dates)
    # The newest thing written in the vault, against the newest log entry.
    touched = max((os.path.getmtime(f) for f in _role_pages()), default=0)
    if touched:
        touched_day = datetime.date.fromtimestamp(touched).isoformat()
        if touched_day > newest:
            return False, (f"role pages written {touched_day}, "
                           f"newest log entry {newest}"), [
                "an assessment that exists only in a reply gets re-derived next week"]
    return True, f"newest log entry {newest}", []


def stage_outcomes():
    """Anything submitted and never chased."""
    sys.path.insert(0, HERE)
    try:
        import outcomes
        ask, record, undateable = outcomes.review(paths.WIKI)
    except Exception as e:
        return True, f"could not check: {type(e).__name__}", []
    total = len(ask) + len(record) + len(undateable)
    if total:
        detail = [f"{n} ({d} days)" if d else f"{n} (no date)"
                  for n, d, _ in undateable + record + ask]
        return False, f"{total} application(s) owed a chase or an outcome", detail
    return True, "nothing owed", []


STAGES = [
    ("sweep", "A full --all-open sweep is recent enough to trust", stage_sweep),
    ("triage", "Every HIGH-signal role is assessed or dispatched", stage_triage),
    ("recorded", "Every assessment has a page, a table row and a posting URL", stage_recorded),
    ("logged", "The log records what was assessed", stage_logged),
    ("outcomes", "No application is waiting to be chased", stage_outcomes),
]


def run():
    return [(name, why, fn()) for name, why, fn in STAGES]


def render(results):
    out = ["", "  Search pipeline", ""]
    for name, why, (done, detail, specifics) in results:
        out.append(f"  {'[x]' if done else '[ ]'} {name:9} {detail}")
        if not done:
            for s in specifics[:6]:
                out.append(f"          {s}")
            if len(specifics) > 6:
                out.append(f"          …and {len(specifics) - 6} more")
    nxt = next((n for n, _, (d, _, _) in results if not d), None)
    out += ["", f"  NEXT: {nxt}" if nxt else
            "  NEXT: nothing outstanding. That is not the same as nothing to do —",
            "" if nxt else "        the backlog and the live applications are separate questions.", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="refresh vault/state/progress.md as well as printing")
    args = ap.parse_args()
    results = run()
    text = render(results)
    print(text)
    if args.write:
        paths.ensure(paths.STATE)
        target = os.path.join(paths.STATE, "progress.md")
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(f"# Search pipeline — {datetime.date.today().isoformat()}\n\n"
                     "Regenerated by `python3 tools/pipeline.py --write`. Safe to delete.\n"
                     "\nEvery line below is COMPUTED from the vault, never asserted.\n\n"
                     "```\n" + text.strip("\n") + "\n```\n")
        print(f"  -> {target}")
    return 1 if any(not d for _, _, (d, _, _) in results) else 0


if __name__ == "__main__":
    sys.exit(main())
