import urllib.request, json, time

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
