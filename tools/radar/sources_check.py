#!/usr/bin/env python3
"""Ask every configured source whether it would actually work, before you rely on it.

    python3 tools/radar/sources_check.py

WHY THIS EXISTS. A user obtained an API key for a job board, wired it up, and
found out afterwards that the board does not cover their country at all -- it
returned 404 there while serving four other countries fine. The README had
claimed coverage it did not have. The hour went on debugging a key that was
never broken.

So this makes no search and reads no results. It asks each adapter one question:
would you work, for this config, right now -- and it insists on two distinctions
that a naive check collapses.

  NOT CONFIGURED IS NOT FAILED. Most sources here watch named employers rather
  than searching, so an empty list means nobody is being watched, which is a
  fact about the config rather than a fault in the source. Reported as a failure
  it sends someone to debug a source they never wanted.

  NO COVERAGE IS NOT A BAD KEY. Where an adapter can hit that ambiguity it
  probes a known-good control alongside the user's own country, because one
  probe genuinely cannot tell them apart -- and the answers point in opposite
  directions. One is "get a new key", the other is "no key will ever help".

WHAT IT DOES NOT DO. It cannot tell you a source has good coverage of your
country, only that it answers. Depth is a judgement and this is a connectivity
check. It also runs no searches, so it costs each source one or two requests.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adapters import ADAPTERS, SEVERITY, NOT_CONFIGURED, OK       # noqa: E402

sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import paths  # noqa: E402

CONFIG    = paths.SEARCH
EMPLOYERS = paths.EMPLOYERS

MARK = {"OK": "OK  ", "EMPTY": "??  ", "NOT CONFIGURED": "--  ",
        "NO COVERAGE": "!!  ", "BAD CREDENTIALS": "!!  ", "BLOCKED": "!!  ",
        "FAILED": "!!  "}


def load(path, what):
    if not os.path.exists(path):
        return {}, f"no {what} — copy {os.path.basename(path).replace('.json', '.example.json')}"
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except ValueError as e:
        return {}, f"{what} is not valid JSON: {e}"


def main():
    cfg, cfg_note = load(CONFIG, "config.json")
    emp, _ = load(EMPLOYERS, "employers.json")
    if cfg_note:
        print(f"  {cfg_note}\n")

    # The watchlist is folded in first, or every employer-board adapter reports
    # NOT CONFIGURED while the user is looking at a watchlist full of employers.
    if emp:
        import employers as EMP
        routed, unrouted = EMP.route(emp, cfg)
        print(f"  watchlist: {len(routed)} employer(s) routed"
              + (f", {len(unrouted)} with NO ROUTE: {', '.join(unrouted)}" if unrouted else "")
              + "\n")

    results = []
    for name in sorted(ADAPTERS):
        mod = ADAPTERS[name]
        if not hasattr(mod, "probe"):
            results.append((name, "FAILED", "no probe(); this adapter cannot be checked"))
            continue
        try:
            verdict, detail = mod.probe(cfg)
        except Exception as e:                       # a probe must never kill the run
            verdict, detail = "FAILED", f"probe raised {type(e).__name__}: {e}"
        results.append((name, verdict, detail))

    results.sort(key=lambda r: (SEVERITY.index(r[1]) if r[1] in SEVERITY else 0, r[0]))
    width = max(len(n) for n, _, _ in results)
    for name, verdict, detail in results:
        print(f"  {MARK.get(verdict, '?   ')}{name:<{width}}  {verdict:<15}  {detail}")

    usable = [r for r in results if r[1] == OK]
    unset = [r for r in results if r[1] == NOT_CONFIGURED]
    broken = [r for r in results if r[1] not in (OK, NOT_CONFIGURED)]

    print(f"\n  {len(usable)} usable, {len(unset)} not configured, {len(broken)} needing attention.")
    if not usable:
        print("  🔴 NOTHING here can return a role. A radar run would be silent, and a "
              "silent run\n     looks exactly like a quiet week.")
    print("\n  This proves each source answers. It does not prove it covers your country "
          "well —\n  that is a judgement, and this is a connectivity check.")
    return 1 if broken or not usable else 0


if __name__ == "__main__":
    sys.exit(main())
