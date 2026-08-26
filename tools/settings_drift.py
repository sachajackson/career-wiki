#!/usr/bin/env python3
"""What has the system started reading that this vault never got?

    python3 tools/settings_drift.py

WHY THIS EXISTS. `git pull` is the update mechanism and it works: the vault is
gitignored, so an update replaces the system and cannot touch a file under
`vault/`. That is the whole boundary and it is the right one.

But it has a corollary nobody had checked. An update can ship a system that NEEDS
a new vault file, and it cannot put that file in anybody's vault.

That is not hypothetical. On 2026-08-26 the radar's tiering vocabulary moved out
of `radar.py` and into `vault/settings/signal.json` -- correctly, it was one
user's preferences sitting in shared code. Anybody who pulled that change got the
new radar and not the file it reads. Nothing errored. The radar still ran, still
fetched, still wrote a shortlist; HIGH and MED were simply always empty and every
role landed in the catch-all section. A broken install that reads as a quiet week
is the worst failure this system can have.

`doctor.py` now names that one file, because a human wrote that check by hand.
This is the general version, so the next required setting does not need somebody
to remember.

WHAT IT COMPARES

`templates/settings/*.example.json` against `vault/settings/*.json`, by KEY and
never by value. Your queries, your employers and your vocabulary are yours; only
the shape is the system's.

- It recurses into objects and treats LISTS AS OPAQUE. A list in these files is
  always data -- queries, boards, employers, weighted patterns -- and never
  schema. Comparing list contents would report a user's own search terms as
  drift.

- 🔴 It ignores every key beginning with `_`, at any depth, and that single rule
  is what makes the check usable. These files carry `_comment`, `_README`,
  `_needs_you` and `_queries_provenance` blocks that explain themselves in
  prose, and both sides accumulate their own. Measured before this rule existed:
  a completely healthy, current vault produced five findings and ALL FIVE were
  underscore keys. A check that reports five faults on a correct vault is a check
  that gets switched off in a week.

WHAT IT WILL NOT DO

It never writes. These are the user's settings and a script that edited them
would be changing the one thing in this repo it does not own.

It does not judge values. A key present but still holding `<your city>` is
`doctor.py`'s finding, not this one -- that tool already knows the difference
between missing, placeholder and optional, and says which.

🔴 A settings file the vault does not have AT ALL is reported but is NOT a
failure, and that asymmetry is deliberate. Most of these are optional: somebody
who never wants oversight should not be told they are out of date every week for
the rest of the year. Adopting a file is a choice; keeping an adopted file
current is not.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import paths  # noqa: E402
TEMPLATES = os.path.join(os.path.dirname(HERE), "templates", "settings")
SUFFIX = ".example.json"


def shape(obj, prefix=""):
    """Every key path in an object, ignoring prose and treating lists as values.

    See the module docstring: the underscore rule is the whole difference
    between a check people run and a check people mute.
    """
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            out.add(prefix + k)
            out |= shape(v, prefix + k + ".")
    return out


def outermost(keys):
    """Drop any key whose parent is already in the set.

    🔴 Volume is the other way a check cries wolf. A vault predating the LinkedIn
    adapter is missing one block, but the naive comparison reports `linkedin`
    plus `linkedin.enabled`, `.location`, `.pages` and `.delay` -- five findings
    for one decision. Measured on a vault two updates behind: 16 missing keys
    collapse to 6 actual gaps. Nobody reads a list that pads itself.
    """
    keys = set(keys)
    return sorted(k for k in keys
                  if not any(k.rsplit(".", i)[0] in keys
                             for i in range(1, k.count(".") + 1)))


def compare(example, actual):
    """(keys the system reads and this vault has not got, keys it no longer reads)."""
    want, got = shape(example), shape(actual)
    return outermost(want - got), outermost(got - want)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--settings", default=paths.SETTINGS)
    ap.add_argument("--templates", default=TEMPLATES)
    args = ap.parse_args()

    if not os.path.isdir(args.templates):
        print(f"  no templates at {args.templates!r} — nothing to compare against.")
        return 0
    if not os.path.isdir(args.settings):
        print(f"  no settings at {args.settings!r}. Nothing is configured yet, which is not\n"
              f"  drift — run `python3 tools/doctor.py` to see what is worth setting up.")
        return 0

    examples = sorted(f for f in os.listdir(args.templates) if f.endswith(SUFFIX))
    checked, missing_n, unknown_n = 0, 0, 0
    absent, unreadable, untemplated = [], [], []

    for name in examples:
        want = name[: -len(SUFFIX)] + ".json"
        live = os.path.join(args.settings, want)
        if not os.path.exists(live):
            absent.append(want)
            continue
        try:
            example, actual = load(os.path.join(args.templates, name)), load(live)
        except ValueError as e:
            unreadable.append((want, e))
            continue
        checked += 1
        missing, unknown = compare(example, actual)
        if missing or unknown:
            print(f"\n  {live}")
            for k in missing:
                print(f"    !! the system reads this and your file has not got it: {k}")
            for k in unknown:
                print(f"    ?? nothing reads this any more, or it is your own:     {k}")
        missing_n += len(missing)
        unknown_n += len(unknown)

    templated = {n[: -len(SUFFIX)] + ".json" for n in examples}
    if os.path.isdir(args.settings):
        untemplated = sorted(f for f in os.listdir(args.settings)
                             if f.endswith(".json") and f not in templated)

    for name, e in unreadable:
        print(f"\n  !! {name} is not valid JSON and was not compared: {e}")

    if absent:
        print(f"\n  Settings the system ships an example for, and this vault has no copy of:"
              f"\n    {', '.join(absent)}"
              f"\n  Not a fault on its own — most are optional. `python3 tools/doctor.py` says"
              f"\n  which of them would silently do nothing for you.")

    if untemplated:
        print(f"\n  ?? Settings files with no example beside them: {', '.join(untemplated)}"
              f"\n  Either yours, or the system gained a setting and shipped no template for it —"
              f"\n  in which case nobody cloning this repo can discover the file exists.")

    print(f"\n  {checked} file(s) compared, {missing_n} key(s) missing, "
          f"{unknown_n} unrecognised.")
    if missing_n:
        print("\n  The missing ones are the update you have not taken. Copy the key across from\n"
              "  templates/settings/ and fill in YOUR value — never the example's, which is a\n"
              "  placeholder and matches nothing.")
    elif not unknown_n:
        print("  Nothing missing. That means the SHAPE matches; it does not mean a value is\n"
              "  right, current, or filled in — `python3 tools/doctor.py` answers that.")
    return 1 if missing_n else 0


if __name__ == "__main__":
    sys.exit(main())
