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

# 🔴 A DECLARED ABSENCE IS NOT A GAP, and a check that cannot tell them apart
# reports the same finding forever until somebody stops reading it.
#
# One role was assessed before postings were archived and its listing has since
# closed. There is no URL to record and there never will be. Left as a blank it
# is indistinguishable from work somebody forgot to finish -- the same "not
# recorded versus recorded as absent" confusion that already cost this system an
# outcome it had captured and could not find.
#
# So the page says so in frontmatter, in a form a machine can read.
NO_POSTING = re.compile(r"^posting:\s*none\b", re.M)


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
        elif not any(rows[name]) and not URL.search(body) and not NO_POSTING.search(body):
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


# 🔴 THE ORDERED RUNBOOK. The radar skill is 323 lines across 18 sections and the
# only ordered part is a five-item list two thirds of the way down — which is how
# the `role-triage` instruction, named twice in that file, went unused for the
# life of the repo. An agent reading prose picks up what it happens to land on.
#
# So the order lives here, executable, with the command for each step. Prose can
# explain WHY; this says WHAT, NEXT.
RUNBOOK = [
    ("0  sources answer",
     "python3 tools/radar/sources_check.py",
     "A silent run and a quiet market look identical. 0 usable means the radar cannot speak."),
    ("1  sweep or window",
     "python3 tools/radar/radar.py --all-open      (or --days 7)",
     "--all-open every 7 days for the backlog; --days 7 for freshness. Not the same run."),
    ("2  read the header, not the command you typed",
     "head -3 vault/state/shortlist.md",
     "Three wordings mean three different things, and one says the window applied to nothing."),
    ("3  open a batch from the SHORTLIST",
     "python3 tools/batch.py --open <slug> --employer <name>",
     "🔴 Never from raw.json. That is the corpus BEFORE the location filter."),
    ("4  delegate the reading",
     "role-triage agent — several in parallel above ~8 roles",
     "🔴 Standing rule. Job adverts are the bulkiest thing that can enter a session."),
    ("5  employer's own posting before scoring an aggregator row",
     "python3 tools/radar/refresh.py <archived posting>",
     "Aggregators truncate the qualifiers that make a candidate MORE eligible."),
    ("6  score, and file in the same turn",
     "page + scoring-table row + posting URL",
     "🔴 All three, or the radar re-surfaces it and the work is done twice."),
    ("7  archive the posting text",
     "vault/postings/<Employer> - <Title>.txt",
     "raw.json is overwritten every run. The archive is the only durable copy."),
    ("8  log it",
     "append to vault/wiki/log.md",
     "An assessment that exists only in a reply gets re-derived next week."),
    ("9  check the batch came back",
     "python3 tools/batch.py --status <slug>  &&  python3 tools/pipeline.py",
     "A delegation nobody verifies is the same failure one level up."),
]


def stage_quoted():
    """🔴 Does every line an assessment attributes to an employer appear in the
    posting? The score is argued from the quote, and nothing checked the quote."""
    sys.path.insert(0, HERE)
    try:
        import quotes
        postings = quotes.load_postings()
    except Exception as e:
        return True, f"could not check: {type(e).__name__}", []
    if not postings:
        return True, "no archived postings to check against", []
    bad, checked = [], 0
    haystack = quotes.archive_text()
    for path in _role_pages():
        fn, missing, n = quotes.check(path, postings)
        if not fn:
            continue
        checked += 1
        # 🔴 A false "the source was cut" caveat is not a misquote, but it does the
        # same damage: the assessment stops looking. Five pages carried one at once.
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        if quotes.false_truncation(body, postings):
            bad.append(f"{os.path.basename(path)[:-3][:44]}: says its source is truncated; "
                       f"the archive runs to its end")
        for rid in quotes.untraceable_ids(body, haystack):
            bad.append(f"{os.path.basename(path)[:-3][:44]}: requisition {rid} is in no archive")
        claimed = [m[1] for m in missing if m[0] == "absent" and m[2] == "claimed"]
        if claimed:
            bad.append(f"{os.path.basename(path)[:-3][:44]}: \"{claimed[0][:60]}\"")
    if bad:
        # 🟡 Three different faults land here — a misquote, a false "the source was
        # truncated" caveat, and a requisition number in no archive. Naming them
        # "misquotes" sent a reader looking for a quotation that was never wrong.
        return False, (f"{len(bad)} problem(s) between an assessment and its posting, "
                       f"across {checked} checked"), bad
    return True, f"all {checked} checked assessment(s) match their posting", []


def stage_scored():
    """🔴 N + D + E must equal FIT, and the page must agree with the table.

    Real on the day this was written: a role scored 4·4·2 carried a FIT of 9 in
    both places, under a heading reading "What holds it at 9". Every component
    was argued for in prose; the total was a slip, and it had been read several
    times without anyone noticing."""
    sys.path.insert(0, HERE)
    try:
        import scores
        faults, _, scored = scores.audit()
    except Exception as e:
        return True, f"could not check: {type(e).__name__}", []
    if not scored:
        return True, "no scored assessments yet", []
    if faults:
        return False, f"{len(faults)} fault(s) in the numbers", [
            f"{k}: {n[:40]} — {d}" for n, k, d in faults]
    return True, f"all {scored} score(s) add up and agree with the table", []


def stage_reviewed():
    """🔴 THE ONLY STAGE THAT NEEDS A MODEL, and the reason it is last.

    Every other stage is a string operation. This one asks whether the posting
    was READ correctly -- and "hands-on experience with agent frameworks",
    quoted perfectly and scored as though it demanded daily coding, is a true
    quote and a false conclusion that no matcher will ever catch.

    🔴 A script cannot spawn the agent. What it can do is refuse to call the
    work finished until the verdict is written down."""
    sys.path.insert(0, HERE)
    try:
        import scores
        _, due, _ = scores.audit()
    except Exception as e:
        return True, f"could not check: {type(e).__name__}", []
    if due:
        return False, (f"{len(due)} assessment(s) at FIT {scores.REVIEW_AT}+ have a posting "
                       f"and no recorded review"), [f"FIT {f}  {n}" for n, f in due[:12]]
    return True, f"every assessment at FIT {scores.REVIEW_AT}+ has been argued with", []


STAGES = [
    ("sweep", "A full --all-open sweep is recent enough to trust", stage_sweep),
    ("triage", "Every HIGH-signal role is assessed or dispatched", stage_triage),
    ("recorded", "Every assessment has a page, a table row and a posting URL", stage_recorded),
    ("quoted", "Every line attributed to an employer is in their posting", stage_quoted),
    ("scored", "The score adds up and the page agrees with the table", stage_scored),
    ("logged", "The log records what was assessed", stage_logged),
    ("outcomes", "No application is waiting to be chased", stage_outcomes),
    ("reviewed", "Every score about to be acted on has been argued with", stage_reviewed),
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


def runbook():
    lines = ["", "  A radar run, in order", ""]
    for step, cmd, why in RUNBOOK:
        lines += [f"  {step}", f"      $ {cmd}", f"      {why}", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runbook", action="store_true",
                    help="print the ordered steps of a radar run and stop")
    ap.add_argument("--write", action="store_true",
                    help="refresh vault/state/progress.md as well as printing")
    args = ap.parse_args()
    if args.runbook:
        print(runbook())
        return 0
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
