#!/usr/bin/env python3
"""registry -- turn `"watch": ["State Street"]` into the config the adapters expect.

The registry (employers.json) knows which ATS an employer uses and under what
identifier. The adapters know how to speak each ATS. Nothing joined the two, so
a user had to know that watching Stripe means writing a Greenhouse board token,
and that watching State Street means writing a host, a tenant and a site.

    "watch": ["State Street", "Grant Thornton Ireland", "Stripe"]

becomes

    "workday":    {"employers": [{"host": ..., "tenant": ..., "site": ...}]}
    "oracle":     {"employers": [{"host": ..., "site": ...}]}
    "greenhouse": {"boards": ["stripe"]}

THE RULE THIS IS BUILT AROUND

Every watched name produces a line in the report, including the ones that could
not be resolved. An employer silently dropped because nobody wrote an adapter
for its ATS is the same failure as a search window that quietly only covered a
week: the run succeeds, the roles are missing, and nothing says so.

It merges with hand-written config rather than replacing it, and deduplicates,
so watching an employer somebody already listed by hand does not fetch twice.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(HERE, "employers.json")

# ats -> (config key, list key, which params the adapter needs)
SHAPES = {
    "workday":    ("workday", "employers", ("host", "tenant", "site")),
    "oracle":     ("oracle", "employers", ("host", "site")),
    "greenhouse": ("greenhouse", "boards", ("token",)),
    "lever":      ("lever", "companies", ("handle",)),
}


def load_registry(path=REGISTRY):
    if not os.path.exists(path):
        return {"employers": []}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def match(name, employers):
    """Exact match wins. Otherwise substring, and two matches is an error.

    Guessing between two employers would silently watch the wrong one, and the
    user would never see it -- they would just see a quiet week.
    """
    lo = name.strip().lower()
    exact = [e for e in employers if e["employer"].lower() == lo]
    if exact:
        return exact[0], None
    part = [e for e in employers if lo in e["employer"].lower()]
    if len(part) == 1:
        return part[0], None
    if len(part) > 1:
        return None, "AMBIGUOUS"
    return None, "NOT IN REGISTRY"


def resolve(config, registry=None):
    """(config, report). config is modified in place and also returned."""
    registry = registry if registry is not None else load_registry()
    employers = registry.get("employers", [])
    report = []

    for name in config.get("watch", []):
        if not isinstance(name, str) or name.startswith("_") or not name.strip():
            continue                      # people leave comments in arrays; do not resolve them
        entry, problem = match(name, employers)
        if problem == "AMBIGUOUS":
            hits = [e["employer"] for e in employers if name.strip().lower() in e["employer"].lower()]
            report.append((name, "AMBIGUOUS", f"matches {hits} -- name it exactly"))
            continue
        if problem:
            report.append((name, "NOT IN REGISTRY",
                           "no entry. Find their careers page, add one, and everyone else gets it too"))
            continue

        shape = SHAPES.get(entry["ats"])
        if not shape:
            report.append((entry["employer"], "NO ADAPTER",
                           f"the registry has it ({entry['ats']}) but no adapter speaks that. "
                           f"{entry['careers_url']}"))
            continue

        key, listkey, fields = shape
        params = entry.get("params", {})
        missing = [f for f in fields if not params.get(f)]
        if missing:
            report.append((entry["employer"], "INCOMPLETE",
                           f"registry entry is missing {missing} for {entry['ats']}"))
            continue

        bucket = config.setdefault(key, {}).setdefault(listkey, [])
        value = params[fields[0]] if len(fields) == 1 else {f: params[f] for f in fields}
        # Say what it matched when that is not what was typed. Substring matching
        # is where a wrong resolution would hide, so it is shown rather than
        # assumed to be obvious.
        via = "" if name.strip().lower() == entry["employer"].lower() else f" (matched on {name.strip()!r})"
        if value in bucket:
            report.append((entry["employer"], "ALREADY LISTED",
                           f"already in {key}.{listkey} by hand -- not added twice{via}"))
        else:
            bucket.append(value)
            report.append((entry["employer"], "RESOLVED", f"-> {key}.{listkey}{via}"))

    return config, report


def format_report(report):
    if not report:
        return ""
    lines = ["  watchlist:"]
    for name, status, msg in report:
        lines.append(f"    [{status:14}] {name:26} {msg}")
    unresolved = [r for r in report if r[1] != "RESOLVED" and r[1] != "ALREADY LISTED"]
    if unresolved:
        lines.append(f"    !! {len(unresolved)} watched employer(s) will NOT be searched this run.")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    cfg_path = os.path.join(HERE, "config.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {"watch": sys.argv[1:]}
    _, rep = resolve(cfg)
    print(format_report(rep) or "  nothing in `watch`")
