#!/usr/bin/env python3
"""registry_check -- is every employer endpoint in the registry still real?

    python3 tools/registry_check.py
    python3 tools/registry_check.py --update      # write today's counts back
    python3 tools/registry_check.py --only Deel

WHY THIS EXISTS

An employer changes ATS and their entry starts returning nothing. That looks
exactly like a quiet week, which is the worst failure a job search can have:
the tool reports success and the user concludes the market is dead.

WHAT IT LEARNED FROM BEING WRONG ONCE

Two rules here were bought with a real mistake. The Grant Thornton entry was
seeded from a 200 response and a count of 152 -- and pointed at the wrong site,
which does not contain their postings at all.

  1. VERIFY BY KNOWN-JOB PRESENCE, NOT BY STATUS CODE OR COUNT. Oracle returns
     200 and the tenant's whole unfiltered list for a siteNumber that does not
     exist. So does its detail endpoint. A check that cannot fail is not a check.

  2. COMPARE COUNTS AS AN ORDER OF MAGNITUDE, NEVER FOR EQUALITY. Measured an
     hour apart, three of five entries had already moved. A checker that fires
     on churn gets switched off within a week, and then it is not a checker.

WHAT IT DELIBERATELY DOES NOT DO

Decide whether a missing canary means a broken endpoint or a filled vacancy. It
cannot know, so it reports and leaves the judgement. Guessing would make the
output confident and sometimes wrong, which is worse than making someone look.
"""
import argparse, json, os, sys, time, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(HERE, "radar", "ats_registry.json")
COLLAPSE = 4          # "now < previous/4" is a collapse; anything less is churn


# Seconds between retries, times the attempt number. Overridable ONLY so the
# tests that drive this file as a subprocess can set it to 0 -- they point it at
# a dead port on purpose, and at the real backoff two of them cost 4.5s each and
# made the whole suite twelve times slower than the second CONTRIBUTING promises.
# A slow suite gets run less often, and the suite is this repo's one control that
# has never failed. Retries still happen at zero; only the waiting goes.
BACKOFF = float(os.environ.get("REGISTRY_CHECK_BACKOFF", "1.5"))


def call(url, method="GET", body=None, timeout=30, tries=3):
    """Retries, because a transient reset is not a dead endpoint.

    Found the hard way: seeding fifteen employers, one reported UNREACHABLE! on a
    connection reset and answered fine three times in a row a second later. A
    checker that calls a working endpoint dead is the cry-wolf failure this whole
    file exists to avoid.
    """
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url, method=method,
                data=json.dumps(body).encode() if body is not None else None,
                headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json",
                         "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            last = e
            if attempt + 1 < tries:
                time.sleep(BACKOFF * (attempt + 1))
    raise last


def fetch(entry, endpoints):
    """Returns (count, raw_json_text). Raises on anything unreachable."""
    p, ats = entry["params"], entry["ats"]
    if ats == "workday":
        raw = call(f"https://{p['host']}/wday/cxs/{p['tenant']}/{p['site']}/jobs",
                   "POST", {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""})
        return json.loads(raw).get("total", 0), raw
    if ats == "oracle":
        raw = call(f"https://{p['host']}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
                   f"?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber={p['site']},limit=200")
        return json.loads(raw)["items"][0].get("TotalJobsCount", 0), raw
    if ats == "greenhouse":
        raw = call(f"https://boards-api.greenhouse.io/v1/boards/{p['token']}/jobs?content=true")
        return len(json.loads(raw).get("jobs", [])), raw
    if ats == "lever":
        raw = call(f"https://api.lever.co/v0/postings/{p['handle']}?mode=json")
        return len(json.loads(raw)), raw
    if ats == "custom":
        raw = call(p["list"])
        d = json.loads(raw)
        return (len(d) if isinstance(d, list) else len(d.get("jobs", d.get("results", [])))), raw
    raise ValueError(f"no rule for ats {ats!r}")


def find_canary(entry, canary):
    """Ask the source for the canary specifically.

    Scanning the first page was tried and produced an immediate false alarm: a
    board with 7,357 jobs does not carry a given requisition in its first 200,
    so a healthy entry reported CANARY GONE. A targeted query is both correct
    and cheaper, and a false alarm on the first run is how a checker earns the
    reputation that gets it ignored.
    """
    p, ats = entry["params"], entry["ats"]
    try:
        if ats == "oracle":
            raw = call(f"https://{p['host']}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
                       f"?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber={p['site']},"
                       f"keyword={canary},limit=5")
        elif ats == "workday":
            raw = call(f"https://{p['host']}/wday/cxs/{p['tenant']}/{p['site']}/jobs", "POST",
                       {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": canary})
        else:
            raw = fetch(entry, {})[1]          # small boards: the full list is the search
    except Exception:
        return False
    return canary in raw


def check(entry, endpoints):
    """(verdict, count, message). Verdicts ending in ! are failures."""
    was = entry.get("verified_returned")
    try:
        n, raw = fetch(entry, endpoints)
    except Exception as e:
        return "UNREACHABLE!", None, f"{type(e).__name__}: {e}"

    if n == 0:
        return "EMPTY!", 0, "the endpoint answered and returned no jobs at all"
    if was and n * COLLAPSE < was:
        return "COLLAPSED!", n, f"was {was}, now {n} -- too large a fall to be churn"

    canary = entry.get("canary")
    if canary and not find_canary(entry, canary):
        # Cannot distinguish a wrong endpoint from a filled vacancy, and says so.
        return "CANARY GONE", n, (
            f"{n} jobs, but requisition {canary} is not among them. Either the endpoint is "
            f"wrong or that job closed -- open the careers page and check before trusting this entry")
    if not canary and entry["ats"] == "oracle":
        return "UNPROVEN", n, (
            f"{n} jobs, but no canary. Oracle returns 200 and a plausible count for a site that "
            f"does not exist, so this number is not evidence. Add one")
    drift = f" (was {was})" if was and was != n else ""
    return "OK", n, f"{n} jobs{drift}" + (f", canary {canary} present" if canary else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--only", help="check one employer by name (substring, case-insensitive)")
    ap.add_argument("--update", action="store_true",
                    help="write today's counts and date back into the registry. Off by default: a "
                         "check that silently rewrites what it is checking is hard to trust")
    args = ap.parse_args()

    if not os.path.exists(args.registry):
        sys.exit(f"registry_check: no registry at {args.registry}")
    reg = json.load(open(args.registry, encoding="utf-8"))
    entries = reg["employers"]
    if args.only:
        entries = [e for e in entries if args.only.lower() in e["employer"].lower()]
        if not entries:
            sys.exit(f"registry_check: nothing matching {args.only!r}")

    today = datetime.date.today().isoformat()
    bad = look = 0
    print(f"registry_check: {len(entries)} employer(s)\n")
    for e in entries:
        verdict, n, msg = check(e, reg.get("_endpoints", {}))
        print(f"  [{verdict:12}] {e['employer']:26} {msg}")
        if verdict.endswith("!"):
            bad += 1
        elif verdict != "OK":
            look += 1
        elif args.update and n:
            e["verified_returned"] = n
            e["last_verified"] = today

    if args.update:
        with open(args.registry, "w", encoding="utf-8") as fh:
            json.dump(reg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\n  updated counts and dates for the entries that passed")

    print()
    if bad:
        print(f"{bad} entry/entries FAILED. Until they are fixed the radar is silently missing "
              f"those employers.\nStart from careers_url -- an employer's own careers page outlives "
              f"whatever ATS sits behind it.")
    if look:
        print(f"{look} entry/entries need a human to look. Not failures -- the tool cannot tell a "
              f"wrong endpoint from a closed vacancy, and will not pretend to.")
    if not bad and not look:
        print("Every endpoint answered, and every canary was where it should be.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
