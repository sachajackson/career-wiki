"""The within-run cache, and the concurrency it makes safe.

WHY THIS FILE EXISTS

A whole-board adapter returns everything open and filters by query in-process,
so a 41-query config asked Greenhouse for the same six board URLs forty-one
times. 246 identical requests where six would do, and the same shape in Workday,
Lever and custom. Measured: 87 new roles arriving alongside 17,350 suppressed
duplicates, and twenty minutes of wall clock against eight seconds of CPU.

The tests that matter here are the refusals -- what must NOT be cached, and what
must NOT be reordered.
"""
import importlib.util, os, threading, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheCache(unittest.TestCase):
    def setUp(self):
        self.http = load("_http", "tools/radar/adapters/_http.py")
        self.calls = []

    def stub(self, *responses):
        """Replace the network. Each call returns the next response; a response
        of None means the request failed."""
        it = iter(responses)

        class Resp:
            def __init__(self, body): self.body = body
            def read(self): return self.body.encode()

        def urlopen(req, timeout=None):
            self.calls.append(req.full_url)
            nxt = next(it)
            if nxt is None:
                raise OSError("boom")
            return Resp(nxt)
        self.http.urllib.request.urlopen = urlopen

    def test_off_by_default_so_importing_changes_nothing(self):
        self.stub("a", "b")
        self.assertEqual(self.http.get("http://x/1"), "a")
        self.assertEqual(self.http.get("http://x/1"), "b")
        self.assertEqual(len(self.calls), 2)

    def test_the_same_url_is_fetched_once_per_run(self):
        self.http.enable_cache()
        self.stub("board", "board-again")
        for _ in range(41):
            self.assertEqual(self.http.get("http://x/board"), "board")
        self.assertEqual(len(self.calls), 1, "the board was re-fetched")
        self.assertEqual(self.http.cache_stats()["hits"], 40)

    def test_a_failure_is_never_cached(self):
        """🔴 The one that matters. A transient timeout cached for the rest of
        the run turns one flaky request into a whole board reported as empty --
        a silent zero, which is worse than being slow."""
        self.http.enable_cache()
        self.stub(None, None, None, "board")     # three tries fail, then success
        self.assertIsNone(self.http.get("http://x/b", tries=3, timeout=0))
        self.assertEqual(self.http.get("http://x/b"), "board")

    def test_a_post_body_is_part_of_the_identity(self):
        """Workday pages by POST body, so two calls to one URL with different
        offsets are different requests. Keying on the URL alone would serve
        page 1 as every page."""
        self.http.enable_cache()
        bodies = []

        class Resp:
            def __init__(self, b): self.b = b
            def read(self): return self.b

        def urlopen(req, timeout=None):
            bodies.append(req.data)
            return Resp(b'{"n": %d}' % len(bodies))
        self.http.urllib.request.urlopen = urlopen
        a, _ = self.http.post_json("http://x/j", {"offset": 0})
        b, _ = self.http.post_json("http://x/j", {"offset": 20})
        c, _ = self.http.post_json("http://x/j", {"offset": 0})
        self.assertNotEqual(a, b, "two offsets collapsed into one response")
        self.assertEqual(a, c)
        self.assertEqual(len(bodies), 2)

    def test_a_cache_hit_costs_no_politeness_delay(self):
        """🔴 The bug this exists for. The adapter slept after every page,
        including the pages the cache served -- 69 cached pages at 0.3s is
        twenty seconds of waiting for a server nobody contacted, once per query,
        and on a 41-query config that is thirteen minutes of pure sleep."""
        import time as _t
        self.http.enable_cache()

        class Resp:
            @staticmethod
            def read(): return b'{"ok": 1}'

        self.http.urllib.request.urlopen = lambda req, timeout=None: Resp()
        first = _t.time()
        self.http.get_json("http://x/board", delay=0.2)
        self.assertGreaterEqual(_t.time() - first, 0.2, "a real request skipped its delay")
        second = _t.time()
        for _ in range(20):
            self.http.get_json("http://x/board", delay=0.2)
        self.assertLess(_t.time() - second, 0.2, "cached responses slept anyway")

    def test_enabling_it_clears_what_a_previous_run_held(self):
        """There is deliberately no on-disk cache. A board read yesterday would
        report a filled role as open, which is the failure the tool exists to
        avoid."""
        self.http.enable_cache()
        self.stub("first", "second")
        self.http.get("http://x/1")
        self.http.enable_cache()
        self.assertEqual(self.http.get("http://x/1"), "second")

    def test_concurrent_readers_do_not_lose_entries(self):
        self.http.enable_cache()
        lock = threading.Lock()

        class Resp:
            def __init__(self, b): self.b = b
            def read(self): return self.b.encode()

        def urlopen(req, timeout=None):
            with lock:
                self.calls.append(req.full_url)
            return Resp("ok")
        self.http.urllib.request.urlopen = urlopen
        threads = [threading.Thread(target=self.http.get, args=(f"http://x/{i % 4}",))
                   for i in range(40)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertLessEqual(len(set(self.calls)), 4)


class TheFetchOrder(unittest.TestCase):
    """Threads finish in whatever order the network allows. The merge must not."""

    def setUp(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
        self.radar = load("radar", "tools/radar/radar.py")

    def test_results_merge_in_the_declared_order_not_the_finishing_order(self):
        """Dedupe keeps the first row it sees, so a nondeterministic merge would
        attribute a role to whichever query won the race and reshuffle the
        shortlist between two runs that found exactly the same jobs."""
        import random, time as _t

        class Mod:
            TRUNCATED = False
            @staticmethod
            def fetch(cfg, q, days):
                _t.sleep(random.random() / 100)
                return [{"id": f"{q}-1", "title": q, "loc": "Dublin"}]

        self.radar.ADAPTERS = {"a": Mod, "b": Mod}
        queries = [f"q{i}" for i in range(8)]
        first = self.radar.fetch_all({}, ["a", "b"], queries, 7, [], [])
        second = self.radar.fetch_all({}, ["a", "b"], queries, 7, [], [])
        self.assertEqual(list(first), list(second))
        self.assertEqual(len(first), 16)

    def test_one_adapter_failing_does_not_lose_the_others(self):
        class Good:
            TRUNCATED = False
            @staticmethod
            def fetch(cfg, q, days): return [{"id": q}]

        class Bad:
            TRUNCATED = False
            @staticmethod
            def fetch(cfg, q, days): raise RuntimeError("down")

        self.radar.ADAPTERS = {"good": Good, "bad": Bad}
        dead, capped = [], []
        out = self.radar.fetch_all({}, ["good", "bad"], ["q1", "q2"], 7, dead, capped)
        self.assertEqual(len(out), 2)
        self.assertEqual(len(dead), 2)
        self.assertTrue(all(d.startswith("bad/") for d in dead))

    def test_adapters_run_concurrently_with_each_other(self):
        """The first shape -- a pool over all (adapter, query) pairs with a lock
        per adapter -- had an effective concurrency of about 1, because `map`
        dispatches in order and the pairs are grouped by adapter, so the pool
        filled with units that all blocked on one lock."""
        import time as _t
        started = _t.time()

        class Slow:
            TRUNCATED = False
            @staticmethod
            def fetch(cfg, q, days):
                _t.sleep(0.05)
                return []

        self.radar.ADAPTERS = {n: Slow for n in "abcdef"}
        self.radar.fetch_all({}, list("abcdef"), ["q1", "q2"], 7, [], [])
        # Serial would be 6 * 2 * 0.05 = 0.6s. Six lanes should be near 0.1s.
        self.assertLess(_t.time() - started, 0.4, "the adapters did not run in parallel")

    def test_each_adapter_is_serialised_with_itself(self):
        """Forced by the TRUNCATED contract, not by caution."""
        import threading as _th
        inside = []

        class Mod:
            TRUNCATED = False
            @staticmethod
            def fetch(cfg, q, days):
                inside.append(_th.current_thread().name)
                return []

        self.radar.ADAPTERS = {"m": Mod}
        self.radar.fetch_all({}, ["m"], [f"q{i}" for i in range(6)], 7, [], [])
        self.assertEqual(len(set(inside)), 1, "one adapter was entered from two threads")

    def test_progress_is_reported_as_each_adapter_lands(self):
        """A run that prints nothing for twenty minutes is indistinguishable
        from a hung one. The first version of this was silent throughout."""
        class Mod:
            TRUNCATED = False
            @staticmethod
            def fetch(cfg, q, days): return [{"id": q}]

        self.radar.ADAPTERS = {"a": Mod, "b": Mod}
        seen = []
        self.radar.fetch_all({}, ["a", "b"], ["q1"], 7, [], [], lambda *a: seen.append(a))
        self.assertEqual(sorted(s[0] for s in seen), ["a", "b"])

    def test_truncation_is_attributed_to_the_right_unit(self):
        """🔴 TRUNCATED is a module attribute read after the call returns, so
        two concurrent calls into one module would each read the other's answer,
        and reporting a capped result set as complete is the failure TRUNCATED
        exists for."""
        class Mod:
            TRUNCATED = False
            @staticmethod
            def fetch(cfg, q, days):
                Mod.TRUNCATED = (q == "capped")
                return []

        self.radar.ADAPTERS = {"m": Mod}
        capped = []
        self.radar.fetch_all({}, ["m"], ["fine", "capped", "also fine"], 7, [], capped)
        self.assertEqual(capped, ["m/capped"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
