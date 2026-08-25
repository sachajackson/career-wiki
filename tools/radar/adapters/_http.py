import urllib.request, urllib.error, json, time

UA = "career-wiki/0.1 (+https://github.com/)"

def get(url, headers=None, tries=3, timeout=30):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(2 * (i + 1))

def get_json(url, headers=None):
    raw = get(url, headers)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None

def post_json(url, payload, headers=None, timeout=30):
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
    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception:
        return None, None
    try:
        return json.loads(raw), 200
    except ValueError:
        return None, 200
