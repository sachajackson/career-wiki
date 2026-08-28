"""Oracle Cloud Recruiting (CX) — the other large enterprise ATS.

Public JSON, no key. Verified against three live tenants on 2026-08-25.

TWO VALUES, AND BOTH ARE IN THE CAREERS URL:

    https://<host>/hcmUI/CandidateExperience/en/sites/<site>/jobs

Unlike Workday this needs no third value. The site segment of that URL works
directly as the API's siteNumber -- confirmed against a numbered site and two
named ones. The host is taken verbatim and NOT derived: tenants appear
both with a region (<pod>.fa.us2.oraclecloud.com) and without
(<pod>.fa.oraclecloud.com), and constructing it from a pattern loses one of them.

WHAT THIS SOURCE GIVES THAT OTHERS DO NOT

  PostedDate is a real ISO date, not "30+ days ago". So the posting window is
  applied here exactly rather than approximated, and HONOURS_DAYS is True --
  see the note on it below, because "the adapter filters" and "the API filters"
  are different claims and only one of them is true.

  Id is the requisition number as the employer prints it.

  ShortDescriptionStr arrives in the listing, so a failed description fetch
  degrades to something real rather than to nothing.

🔴 AN UNRECOGNISED SITE DOES NOT FAIL. IT WIDENS. Oracle ignores a siteNumber it
does not know and answers with the tenant's default set instead, so a typo in
the site value returns MORE roles rather than none -- on a multi-brand tenant,
other people's roles under the name you gave the employer. Nothing in a single
response distinguishes that from a correct config. `sources_check.py` detects it
by asking for a deliberately nonsense site and comparing the counts.

A NOTE ON THE BACKLOG'S WRITE-UP. It records that the detail finder's values
must be quoted or the request 400s. Unquoted worked on every tenant tried here,
so that is either version-specific or was only ever true of a non-numeric id.
Quoting costs nothing and is kept -- but the claim is softened rather than
repeated, because an instruction nobody can reproduce stops being followed.
"""
import re, time, urllib.parse
from ._http import get_json, fetch_json
from . import _verdicts as V

NAME = "oracle"
TRUNCATED = False
# True, but read this: the API has no posting-window parameter. What it has is
# an exact PostedDate on every row and a newest-first sort, so the window is
# applied here, precisely, and paging stops at the first row that falls outside
# it. The result is the same as a server-side filter; the mechanism is not, and
# a reader deciding whether to trust the date needs to know which.
HONOURS_DAYS = True

LIST = ("https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
        "?onlyData=true&expand=requisitionList.secondaryLocations&finder={finder}")
DETAIL = ("https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails"
          "?expand=all&finder={finder}")
PUBLIC = "https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{jid}"

PAGE = 25


def _strip(markup):
    import html
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup or ""))).strip()


def _finder(s):
    return urllib.parse.quote(s, safe=';,="')


def _rows(payload):
    """The list response buries the rows two levels down, behind a search object."""
    items = (payload or {}).get("items") or []
    if not items:
        return [], None
    return (items[0].get("requisitionList") or []), items[0].get("TotalJobsCount")


def tenant(host):
    """The first label of the host — `jpmc.fa.oraclecloud.com` -> `jpmc`.

    🟡 Not a display name, but unlike the site slug it is UNIQUE PER TENANT, so
    two employers sharing Oracle's default site stop looking like one employer.
    """
    return (host or "").split(".")[0] or "oracle"


def employer_name(o, host, site):
    """The employer to write on a row from this tenant and site.

    🔴 THIS USED TO BE `names.get(site, site)`, AND SITE ALONE IS NOT AN IDENTITY.
    `CX_1001` is Oracle's DEFAULT site value and two shipped registry entries
    already use it, so one label was applied to two different employers and their
    roles deduped against each other as though they were one company.

    🔴 The company field is not cosmetic either — `employers.py` matches every
    avoid, avoid_sectors and watch rule against it, so while it read `CX_1001`
    none of them could fire on this adapter at all.

    🟢 Keys are tried most-specific first, and `"<host>|<site>"` is the form to
    write for a tenant on a shared site.

    🔴 A SITE-ONLY KEY STILL WORKS, and that is deliberate rather than lazy.
    Several employers have a genuinely unique site and their labels were written
    against it; requiring the compound form would leave every one of those
    lookups missing and silently revert good labels to raw slugs — the fix for
    unhelpful labels producing no labels at all.
    """
    names = o.get("names") or {}
    if names.get(f"{host}|{site}"):
        return names[f"{host}|{site}"]
    if names.get(site):
        # 🔴 Only trust a site-only label when ONE configured tenant uses that
        # site. Otherwise it is a confidently wrong employer name, which is worse
        # than a slug because it gets believed.
        hosts = {e.get("host") for e in (o.get("employers") or [])
                 if isinstance(e, dict) and e.get("site") == site and e.get("host")}
        if len(hosts) <= 1:
            return names[site]
    return tenant(host)


def fetch(cfg, query, days):
    global TRUNCATED
    TRUNCATED = False
    o = cfg.get("oracle", {})
    employers = o.get("employers", [])
    if not employers:
        return []
    pages = int(o.get("pages", 5))
    delay = float(o.get("delay", 0.3))
    cutoff = None
    if days is not None:
        import datetime
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    out = []

    for e in employers:
        host, site = e.get("host"), e.get("site")
        if not (host and site):
            print(f"  !! oracle: an employer entry needs host and site (got {e!r}) -- skipped",
                  flush=True)
            continue
        got, total, ran_out_of_window = 0, None, False

        for page in range(pages):
            f = f"findReqs;siteNumber={site},limit={PAGE},offset={page * PAGE}," \
                f"sortBy=POSTING_DATES_DESC"
            if query:
                f += f',keyword="{query}"'
            data = get_json(LIST.format(host=host, finder=_finder(f)))
            if data is None:
                TRUNCATED = True
                print(f"  !! oracle {site}: request failed", flush=True)
                break
            rows, count = _rows(data)
            if total is None:
                total = count
            if not rows:
                break

            for r in rows:
                posted = str(r.get("PostedDate") or "")[:10]
                # Newest first, so the first row outside the window means every
                # row after it is too. Stopping here is completeness, not a cap.
                if cutoff and posted and posted < cutoff:
                    ran_out_of_window = True
                    break
                loc = r.get("PrimaryLocation") or ""
                extra = [x.get("Name") for x in (r.get("secondaryLocations") or []) if x.get("Name")]
                jid = str(r.get("Id") or "")
                out.append({
                    "id": f"or-{site}-{jid}",
                    "title": (r.get("Title") or "").strip(),
                    "company": employer_name(o, host, site),
                    "loc": "; ".join([p for p in [loc] + extra if p]) or "?",
                    "date": posted,
                    "url": PUBLIC.format(host=host, site=site, jid=jid),
                    # Left empty on purpose so the runner fetches the full text.
                    # Tiering on the short description would systematically
                    # under-score this source against ones that give full text,
                    # which is the same defect as a term only some inputs earn.
                    "body": "",
                    "pay": "",
                    "source": NAME,
                    "requisition": jid,
                    "_short": _strip(r.get("ShortDescriptionStr")),
                    "_or": [host, site, jid],
                })
                got += 1

            if ran_out_of_window:
                break
            time.sleep(delay)
            if total is not None and (page + 1) * PAGE >= total:
                break

        # A window that ran out is a complete answer for that window. A page
        # budget that ran out is not, and only the second is truncation.
        if not ran_out_of_window and total is not None and got < total and cutoff is None:
            TRUNCATED = True
        elif not ran_out_of_window and total is not None and got >= PAGE * pages:
            TRUNCATED = True

        # 🔴 AN UNRECOGNISED SITE DOES NOT FAIL HERE, IT WIDENS. Oracle ignores a
        # siteNumber it does not know and answers with the whole tenant instead,
        # so a typo returns MORE roles rather than none -- on a multi-brand
        # tenant, other employers' roles under this employer's name. There is no
        # error to notice and the run looks unusually productive.
        #
        # `probe()` has caught this since 2026-08-25, but only when somebody runs
        # sources_check. A real run never asked, so the one place the answer
        # changes what you are looking at was the one place it was not checked.
        #
        # 🟢 Two counts settle it: a site value Oracle honours scopes the result,
        # a nonsense one does not. One extra request per TENANT, cached, not per
        # employer -- and it says so once rather than per page.
        if total:
            if host not in _control_cache:
                _control_cache[host] = _count(host, CONTROL_SITE)
            control, cstatus = _control_cache[host]
            if cstatus == 200 and control == total:
                print(f"  !! oracle {site}: {total} roles, and a NONSENSE site value returns the "
                      f"same {control}.\n"
                      f"  !! Oracle is probably ignoring this site and searching the whole tenant "
                      f"({tenant(host)}).\n"
                      f"  !! Harmless if that employer runs one site. Otherwise these rows may "
                      f"belong to other\n"
                      f"  !! employers on the same tenant — check the site segment of the careers "
                      f"URL.", flush=True)

    return out


def fetch_body(row):
    """Full description, degrading to the short one the listing already gave.

    Most adapters return "" when the description cannot be fetched, and a role
    then signals low for a reason that has nothing to do with the role. Here
    there is something real to fall back to, so it falls back.
    """
    stash = (row or {}).get("_or")
    if not stash:
        return (row or {}).get("_short", "")
    host, site, jid = stash
    f = _finder(f'ById;Id="{jid}",siteNumber="{site}"')
    data = get_json(DETAIL.format(host=host, finder=f))
    items = (data or {}).get("items") or []
    full = _strip(items[0].get("ExternalDescriptionStr")) if items else ""
    return full or row.get("_short", "")


# A site value no tenant will have. Its only job is to be the control below.
CONTROL_SITE = "zzNoSuchSiteZZ"
# Per-tenant, not per-employer: several employers can share one host and the
# control count is a property of the tenant. Cleared between runs by process
# lifetime, which is the right scope -- a tenant can be reconfigured.
_control_cache = {}


def _count(host, site):
    data, status = fetch_json(LIST.format(host=host, finder=_finder(
        f"findReqs;siteNumber={site},limit=1")))
    _, total = _rows(data) if data else ([], None)
    return total, status


def probe(cfg):
    employers = cfg.get("oracle", {}).get("employers", [])
    if not employers:
        return V.NOT_CONFIGURED, ("no employers listed. This watches named employers "
                                  "rather than searching, so empty is nobody watched")
    good, bad, unverified = [], [], []
    for e in employers:
        host, site = e.get("host"), e.get("site")
        if not (host and site):
            bad.append(f"{site or host or '?'} (needs host AND site)")
            continue
        data, status = _count(host, site)
        total = data
        if status != 200 or total is None:
            bad.append(f"{site} ({status})")
            continue
        # Oracle does not reject an unrecognised siteNumber. It falls back to
        # the tenant's default set, so a typo does not fail -- it QUIETLY WIDENS
        # the search to everything that tenant posts, which on a multi-brand
        # tenant is other people's roles under your employer's name. Verified:
        # on one tenant a real site scoped to 152 while a nonsense one returned
        # 258. One probe cannot see this; two can. Same trick as adzuna's
        # control country, and the same reason.
        control, cstatus = _count(host, CONTROL_SITE)
        if cstatus == 200 and control == total:
            unverified.append(site)
            good.append(f"{site} ({total} open, site value may be ignored)")
        else:
            good.append(f"{site} ({total} open)")
    # Said once, not per employer: repeated for each it becomes a wall nobody
    # reads, which for a warning is the same as not printing it.
    note = (f" ⚠ {len(unverified)} site value(s) returned the same count as a nonsense "
            f"one, so Oracle may be ignoring them and searching the whole tenant. "
            f"Harmless if that employer runs a single site; otherwise check the site "
            f"segment of the careers URL.") if unverified else ""
    if not good:
        return V.FAILED, f"none reachable: {', '.join(bad)}"
    if bad:
        return V.OK, (f"{len(good)}/{len(employers)} reachable: {', '.join(good)}. "
                      f"Not: {', '.join(bad)}.{note}")
    return V.OK, ", ".join(good) + note
