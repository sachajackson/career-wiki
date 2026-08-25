"""HTTP, plus the two things a job-board run needs from it: a within-run
response cache, and enough thread safety to fetch boards concurrently.

🔴 WHY THE CACHE EXISTS, AND WHY IT IS THE BIGGER HALF OF THE SPEEDUP

A whole-board adapter returns everything open and then filters by query
in-process. So a 41-query config asks Greenhouse for the SAME six board URLs
forty-one times: 246 identical requests where six would do. Workday, Lever and
the custom adapter have the same shape. That is most of a twenty-minute run,
and it was measured -- 87 new roles arrived alongside 17,350 suppressed
duplicates, which is the same board rows coming back over and over.

**A board does not change during a run**, so a response is reusable for the
lifetime of the process and no longer. There is no on-disk cache and there
should not be: a stale board read from yesterday would report a filled role as
open, which is the one failure this whole tool exists to avoid.

🔴 THE POLITENESS DELAY LIVES HERE, NOT IN THE ADAPTERS, and that is not tidying.
An adapter that sleeps after every page sleeps after the pages the cache served
too -- 69 cached pages at 0.3s is twenty seconds of waiting for a server nobody
contacted, once per query, and on a 41-query config that is thirteen minutes of
pure sleep. The delay exists to be polite to a server. A cache hit touches no
server, so it earns no delay.

🔴 FAILURES ARE NEVER CACHED. A transient timeout cached for the rest of the run
turns one flaky request into a whole board reported as empty -- a silent zero,
which is worse than being slow.
"""
import json
import threading
import time
import urllib.error
import urllib.request

UA = "career-wiki/0.1 (+https://github.com/)"

_LOCK = threading.Lock()
_CACHE = {}
_ENABLED = False
_HITS = _MISSES = 0


def enable_cache(on=True):
    """Off by default so importing this module changes nothing. radar.py turns
    it on for the length of a run; a test that wants the old behaviour does not
    have to know it exists."""
    global _ENABLED
    with _LOCK:
        _ENABLED = on
        _CACHE.clear()


def cache_stats():
    with _LOCK:
        return {"hits": _HITS, "misses": _MISSES, "entries": len(_CACHE)}


def _cached(key):
    global _HITS, _MISSES
    if not _ENABLED:
        return None, False
    with _LOCK:
        if key in _CACHE:
            _HITS += 1
            return _CACHE[key], True
        _MISSES += 1
    return None, False


def _store(key, value):
    if not _ENABLED:
        return
    with _LOCK:
        _CACHE[key] = value

def get(url, headers=None, tries=3, timeout=30):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    key = ("GET", url, tuple(sorted(h.items())))
    hit, found = _cached(key)
    if found:
        return hit
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            body = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
            _store(key, body)
            return body
        except Exception:
            if i == tries - 1:
                return None          # not cached: see the module docstring
            time.sleep(2 * (i + 1))

def get_json(url, headers=None, delay=0.0):
    return fetch_json(url, headers, delay=delay)[0]


def fetch_json(url, headers=None, timeout=30, delay=0.0):
    """GET JSON and report the status alongside it. Returns (data, status).

    get_json collapses every failure to None, which is fine when all you can do
    is skip the row. It is not fine when the status IS the answer: a 404 from a
    job API means that country is not covered, and a 401 means the key is wrong.
    Told apart they are two different jobs for the user; collapsed together they
    cost an hour of looking in the wrong place. status is None when nothing came
    back at all.
    """
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    key = ("GETJ", url, tuple(sorted(h.items())))
    hit, found = _cached(key)
    if found:
        return hit
    try:
        req = urllib.request.Request(url, headers=h)
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception:
        return None, None
    try:
        out = (json.loads(raw), 200)
    except ValueError:
        return None, 200
    _store(key, out)
    if delay:
        time.sleep(delay)     # only ever after a real request. See the docstring
    return out

def post_json(url, payload, headers=None, timeout=30, delay=0.0):
    """POST JSON, get JSON back. Returns (data, status).

    Unlike get_json this reports the HTTP status, because for at least one API
    the status IS the diagnosis: a Workday 422 means the tenant is on a
    different wd shard, not that the request was malformed, and an adapter that
    only sees None spends an hour looking in the wrong place. status is None
    when the request never got a response at all.
    """
    h = {"User-Agent": UA, "Content-Type": "application/json",
         "Accept": "application/json"}
    if headers:
        h.update(headers)
    body = json.dumps(payload).encode("utf-8")
    # The payload is part of the identity: Workday pages by POST body, so two
    # calls to one URL with different offsets are different requests.
    key = ("POST", url, tuple(sorted(h.items())), body)
    hit, found = _cached(key)
    if found:
        return hit
    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception:
        return None, None
    try:
        out = (json.loads(raw), 200)
    except ValueError:
        return None, 200
    _store(key, out)
    if delay:
        time.sleep(delay)     # only ever after a real request. See the docstring
    return out
