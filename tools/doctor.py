#!/usr/bin/env python3
"""Is this set up, and what will silently do nothing if it is not?

    python3 tools/doctor.py

WHY. Setting this up means three config files copied from examples, a git
setting, a CV in a folder, and up to two API keys. Nothing answered "am I ready"
-- `sources_check.py` answers a third of it and only about job sources.

THE FAILURE THIS IS REALLY FOR. A config copied from the example and never
filled in **looks configured and returns nothing.** `search.example.json` says
so in its own first line: leave the angle-bracket values as they are and the
location filter matches nothing, so the radar finds no roles and reports a quiet
week. A missing file announces itself. A file full of placeholders does not, and
that is the one worth a check.

WHAT IT WILL NOT DO. It makes no network calls, so it is fast, works offline,
and cannot tell you an endpoint answers -- `sources_check.py` does that and says
so. And OPTIONAL never means broken: most of this is optional, and reporting an
unconfigured thing as a fault sends people to fix something they never wanted.
"""
import json, os, subprocess, sys

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


def check_sources():
    d = paths.SOURCES
    files = [f for f in os.listdir(d) if not f.startswith(".") and f != "README.md"] \
        if os.path.isdir(d) else []
    if not files:
        return MISSING, ("sources/ has no CV in it. /career-init stops without one, and "
                         "a messy CV is more useful than a tidy one")
    return OK, f"{len(files)} file(s) — {', '.join(sorted(files)[:3])}"


def check_wiki():
    d = paths.WIKI
    pages = [f for f in os.listdir(d) if f.endswith(".md")] if os.path.isdir(d) else []
    if not pages:
        return OPTIONAL, "no wiki yet. Run /career-init — that is the next step, not a fault"
    return OK, f"{len(pages)} page(s). Run template_drift.py after any tool update"


def _config(path, name, what):
    if not os.path.exists(path):
        return OPTIONAL, f"no {name}. Copy {os.path.basename(path).replace('.json', '.example.json')} and fill it in — {what}"
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
    r = _config(paths.SEARCH, "radar config.json",
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
        return MISSING, f"review config.json is not valid JSON: {e}"
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
    ("registry", check_registry),
    ("your CV", check_sources),
    ("your wiki", check_wiki),
    ("job search", check_radar_config),
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
