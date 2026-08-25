#!/usr/bin/env python3
"""add_employer -- add an employer to the registry, verified, and offer it upstream.

    python3 tools/add_employer.py "Stripe" https://stripe.com/careers/search
    python3 tools/add_employer.py "Stripe" https://stripe.com/careers/search --canary 6543210
    python3 tools/add_employer.py --contribute        # send what is already added

WHY THIS SHAPE

Somebody maintains this registry by hand. Every entry that arrives unverified is
a research task for them, and a maintainer who has to verify contributions stops
merging them. So this does the verification before the contribution exists:

  1. Read the employer's own careers page and work out which ATS is behind it.
  2. Call the endpoint. If it does not answer, there is nothing to contribute.
  3. Write the entry.
  4. Only then offer to send it.

A pull request that arrives already checked is a thirty-second read. That is the
whole design.

ON SENDING IT

It stages exactly one file and refuses if anything else is staged. This runs from
a working copy that also contains somebody's private wiki, and "I only meant to
commit the one file" is how that goes wrong. The check is not a formality.
"""
import argparse, json, os, re, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REGISTRY = os.path.join(HERE, "radar", "employers.json")
REL = "tools/radar/employers.json"
UPSTREAM = "sachajackson/career-wiki"

# What an ATS looks like when it is fronted by an employer's own careers page.
SNIFF = [
    ("workday", re.compile(r"([a-z0-9.-]*\.?wd\d+\.myworkday(?:jobs|site)\.com)"
                           r"(?:/(?:recruiting|wday/cxs)/([\w-]+)/([\w-]+))?", re.I)),
    ("oracle", re.compile(r"([a-z0-9-]+\.fa\.(?:[a-z0-9-]+\.)?oraclecloud\.com)"
                          r"[^\"']*?sites/([A-Za-z0-9_]+)", re.I)),
    ("greenhouse", re.compile(r"boards(?:-api)?\.greenhouse\.io/(?:v1/boards/)?([a-z0-9_-]+)", re.I)),
    ("lever", re.compile(r"jobs\.lever\.co/([a-z0-9_-]+)", re.I)),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([a-z0-9_-]+)", re.I)),
]


def get(url, timeout=30, method="GET", body=None):
    req = urllib.request.Request(url, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


WORKDAY_SITES = ["Global", "External", "Careers", "careers", "en-US", "Search",
                 "External_Career_Site", "ExternalCareerSite"]


def probe_workday_site(host, tenant):
    """Workday fails closed: a wrong Job_Posting_Site_ID 404s with a named error.

    That makes probing honest here in a way it would not be on Oracle, where a
    wrong site returns 200 and a plausible answer.
    """
    for site in WORKDAY_SITES:
        try:
            raw = get(f"https://{host}/wday/cxs/{tenant}/{site}/jobs", method="POST",
                      body={"appliedFacets": {}, "limit": 1, "offset": 0}, timeout=15)
            if json.loads(raw).get("total"):
                return site
        except Exception:
            continue
    return None


def sniff(careers_url):
    """Which ATS sits behind this careers page? Returns (ats, params) or (None, why)."""
    try:
        html = get(careers_url)
    except Exception as e:
        return None, f"could not read {careers_url}: {type(e).__name__}"
    for ats, rx in SNIFF:
        m = rx.search(html)
        if not m:
            continue
        g = [x for x in m.groups() if x]
        if ats == "workday":
            host = g[0]
            if len(g) >= 3:
                return ats, {"host": host, "tenant": g[1], "site": g[2]}
            tenant = host.split(".")[0] if not host.startswith("wd") else None
            # Workday 404s on a wrong site, so probing is safe and cheap -- unlike
            # Oracle, a wrong guess cannot come back looking like a right one.
            site = probe_workday_site(host, tenant) if tenant else None
            return ats, {"host": host, "tenant": tenant, "site": site}
        if ats == "oracle":
            # Prefer a CX_ number. A friendly site name is not a siteNumber: Oracle
            # does not recognise it and falls back to the tenant's whole unfiltered
            # list, so the entry would claim a filter it is not applying.
            host = g[0]
            cx = re.findall(r"sites/(CX_\d+)", html)
            return ats, {"host": host, "site": cx[0] if cx else g[1],
                         "_unfiltered": not cx}
        if ats == "greenhouse":
            return ats, {"token": g[0]}
        if ats == "lever":
            return ats, {"handle": g[0]}
        if ats == "ashby":
            return ats, {"slug": g[0]}
    return None, ("no ATS marker in the page. Some employers proxy their own -- open the careers page "
                  "in a browser, watch the network tab for a request returning JSON, and add the entry "
                  "by hand with \"ats\": \"custom\"")


def verify(ats, params, canary=None):
    """(count, raw) or raises. The point of the whole script."""
    if ats == "workday":
        raw = get(f"https://{params['host']}/wday/cxs/{params['tenant']}/{params['site']}/jobs",
                  method="POST", body={"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""})
        return json.loads(raw).get("total", 0), raw
    if ats == "oracle":
        raw = get(f"https://{params['host']}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
                  f"?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber={params['site']},limit=20")
        return json.loads(raw)["items"][0].get("TotalJobsCount", 0), raw
    if ats == "greenhouse":
        raw = get(f"https://boards-api.greenhouse.io/v1/boards/{params['token']}/jobs?content=true")
        return len(json.loads(raw).get("jobs", [])), raw
    if ats == "lever":
        raw = get(f"https://api.lever.co/v0/postings/{params['handle']}?mode=json")
        return len(json.loads(raw)), raw
    if ats == "custom":
        raw = get(params["list"])
        d = json.loads(raw)
        return (len(d) if isinstance(d, list) else len(d.get("jobs", d.get("results", [])))), raw
    raise ValueError(f"no verification rule for {ats!r}")


def one_file_staged():
    out = subprocess.run(["git", "-C", REPO, "status", "--porcelain"],
                         capture_output=True, text=True).stdout.strip().splitlines()
    dirty = [l[3:].strip() for l in out if l.strip()]
    return dirty == [REL], dirty


def contribute(entry_name):
    ok, dirty = one_file_staged()
    if not ok:
        print(f"REFUSED: this would send more than the registry.\n\n"
              f"  changed: {dirty or 'nothing'}\n\n"
              f"Only {REL} may go upstream. This working copy also holds a private wiki, and\n"
              f"'I only meant to commit the one file' is exactly how that goes wrong.\n"
              f"Commit or stash everything else first.", file=sys.stderr)
        return 1

    diff = subprocess.run(["git", "-C", REPO, "diff", "--", REL], capture_output=True, text=True).stdout
    print("This is everything that would be sent:\n")
    print("\n".join("  " + l for l in diff.splitlines() if l.startswith(("+", "-")) and l[1:2] != "-"))
    if input("\nSend it? [y/N] ").strip().lower() != "y":
        print("Nothing sent. The entry is still in your local registry and still works.")
        return 0

    has_gh = subprocess.run(["which", "gh"], capture_output=True).returncode == 0
    if has_gh:
        branch = "add-employer-" + re.sub(r"[^a-z0-9]+", "-", entry_name.lower()).strip("-")
        for cmd in (["git", "-C", REPO, "checkout", "-b", branch],
                    ["git", "-C", REPO, "add", REL],
                    ["git", "-C", REPO, "commit", "-m", f"registry: add {entry_name}"]):
            subprocess.run(cmd, check=False, capture_output=True)
        r = subprocess.run(["gh", "pr", "create", "--repo", UPSTREAM, "--fill",
                            "--title", f"registry: add {entry_name}"],
                           cwd=REPO, capture_output=True, text=True)
        if r.returncode == 0:
            print("\n" + r.stdout.strip())
            return 0
        print(f"\ngh could not open the PR: {r.stderr.strip()[:200]}", file=sys.stderr)

    body = urllib.parse.quote(f"Verified this endpoint. Registry entry:\n\n```json\n{diff}\n```")
    print(f"\nNo PR was opened. Paste it here instead -- it is just as useful:\n"
          f"  https://github.com/{UPSTREAM}/issues/new?title=" +
          urllib.parse.quote(f"registry: add {entry_name}") + f"&body={body}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("employer", nargs="?", help="the employer's name, as a person would write it")
    ap.add_argument("careers_url", nargs="?", help="their OWN careers page, never the ATS address")
    ap.add_argument("--canary", help="a requisition id that must appear. Required for Oracle, which "
                                     "returns 200 and a plausible count for a site that does not exist")
    ap.add_argument("--contribute", action="store_true", help="send what is already added")
    ap.add_argument("--registry", default=REGISTRY)
    args = ap.parse_args()

    if args.contribute and not args.employer:
        return contribute("an employer")
    if not (args.employer and args.careers_url):
        ap.error("give an employer name and their careers URL, or --contribute")

    for bad in ("myworkdayjobs.com", "myworkdaysite.com", "oraclecloud.com",
                "boards.greenhouse.io", "jobs.lever.co", "ashbyhq.com"):
        if bad in args.careers_url:
            sys.exit(f"That is the ATS address, not the company's careers page.\n"
                     f"Use theirs -- stripe.com/careers/search, not boards.greenhouse.io/stripe.\n"
                     f"The careers page outlives whatever ATS sits behind it, which is why it is the "
                     f"field that matters.")

    print(f"reading {args.careers_url} ...")
    ats, params = sniff(args.careers_url)
    if not ats:
        sys.exit(f"\n{params}")
    unfiltered = params.pop("_unfiltered", False)
    print(f"  looks like {ats}: {params}")
    if unfiltered:
        print("  !! that site name is not a CX_ number. Oracle does not recognise it and returns the\n"
              "     tenant's whole unfiltered list, so this entry will fetch every site they run, not\n"
              "     just the one you were looking at. Open a job and take CX_<n> from its URL if you\n"
              "     want the narrower one.", file=sys.stderr)
    if any(v is None for v in params.values()):
        sys.exit(f"\nFound {ats} but not every part of it. Fill the gaps by hand and add the entry "
                 f"to {REL} directly -- a half-guessed identifier is worse than none.")

    print("  calling it ...")
    try:
        n, raw = verify(ats, params, args.canary)
    except Exception as e:
        sys.exit(f"  the endpoint did not answer: {type(e).__name__}: {e}\n"
                 f"  Nothing to contribute until it does.")
    if not n:
        sys.exit("  it answered and returned no jobs. That is not a working entry.")
    print(f"  {n} open roles")

    if ats == "oracle" and not args.canary:
        sys.exit("\nOracle needs a --canary: an unrecognised siteNumber returns 200 and the tenant's\n"
                 "whole unfiltered list, so a count is not evidence. Open a job on their site, take the\n"
                 "requisition number from the URL, and pass it.")
    if args.canary and args.canary not in raw:
        print(f"  !! canary {args.canary} not in the first page -- checking by search is left to "
              f"registry_check.py", file=sys.stderr)

    reg = json.load(open(args.registry, encoding="utf-8"))
    if any(e["employer"].lower() == args.employer.lower() for e in reg["employers"]):
        sys.exit(f"\n{args.employer} is already in the registry.")

    import datetime
    entry = {"employer": args.employer, "ats": ats, "params": params,
             "careers_url": args.careers_url, "publishes_salary": False,
             "last_verified": datetime.date.today().isoformat(), "verified_returned": n}
    if args.canary:
        entry["canary"] = args.canary
    reg["employers"].append(entry)
    reg["employers"].sort(key=lambda e: e["employer"].lower())
    with open(args.registry, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")

    print(f"\nAdded to {REL}:\n")
    print("\n".join("  " + l for l in json.dumps(entry, indent=2).splitlines()))
    print(f"\nYour radar can watch them now: add \"{args.employer}\" to `watch` in config.json.")
    print(f"To offer it to everyone else:  python3 tools/add_employer.py --contribute")
    return 0


if __name__ == "__main__":
    import urllib.parse
    sys.exit(main())
