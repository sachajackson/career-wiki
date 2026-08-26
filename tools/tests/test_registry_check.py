"""registry_check: does it catch a dead endpoint without crying wolf?

The two rules under test were bought with real mistakes. An entry was seeded
from a 200 response and a plausible count, and pointed at the wrong site. And
the first version of the canary check scanned one page of a 7,357-job board,
which reported a healthy entry as broken on its very first run.
"""
import importlib.util, json, os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RC = os.path.join(ROOT, "tools", "registry_check.py")

spec = importlib.util.spec_from_file_location("registry_check", RC)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)


def entry(**kw):
    e = {"employer": "Acme", "ats": "custom", "params": {"list": "https://x/"},
         "careers_url": "https://acme.example/careers", "verified_returned": 100}
    e.update(kw)
    return e


class Verdicts(unittest.TestCase):
    """fetch() and find_canary() are stubbed: this tests the judgement, not the network."""

    def setUp(self):
        self._fetch, self._canary = rc.fetch, rc.find_canary
        self.addCleanup(lambda: setattr(rc, "fetch", self._fetch))
        self.addCleanup(lambda: setattr(rc, "find_canary", self._canary))

    def stub(self, count=None, raw="{}", canary_found=True, boom=None):
        def f(e, ep):
            if boom:
                raise boom
            return count, raw
        rc.fetch = f
        rc.find_canary = lambda e, c: canary_found

    def test_a_healthy_entry_passes(self):
        self.stub(count=100)
        self.assertEqual(rc.check(entry(), {})[0], "OK")

    def test_churn_is_not_a_failure(self):
        """Three of five real entries moved within an hour of being recorded."""
        self.stub(count=104)
        self.assertEqual(rc.check(entry(verified_returned=100), {})[0], "OK")

    def test_a_large_fall_is_a_collapse(self):
        self.stub(count=3)
        v, _, msg = rc.check(entry(verified_returned=100), {})
        self.assertEqual(v, "COLLAPSED!")
        self.assertIn("churn", msg)

    def test_zero_is_always_a_failure(self):
        """An endpoint answering with nothing looks exactly like a quiet week."""
        self.stub(count=0)
        self.assertEqual(rc.check(entry(), {})[0], "EMPTY!")

    def test_an_unreachable_endpoint_fails(self):
        self.stub(boom=OSError("connection refused"))
        v, _, msg = rc.check(entry(), {})
        self.assertEqual(v, "UNREACHABLE!")
        self.assertIn("OSError", msg)

    def test_a_missing_canary_asks_a_human_rather_than_failing(self):
        """It cannot tell a wrong endpoint from a filled vacancy, and must not guess."""
        self.stub(count=100, canary_found=False)
        v, _, msg = rc.check(entry(canary="115289"), {})
        self.assertEqual(v, "CANARY GONE")
        self.assertFalse(v.endswith("!"))
        self.assertIn("or that job closed", msg)

    def test_an_oracle_entry_without_a_canary_is_unproven(self):
        """Oracle returns 200 and a plausible count for a site that does not exist."""
        self.stub(count=152)
        v, _, msg = rc.check(entry(ats="oracle", params={"host": "h", "site": "CX_1"}), {})
        self.assertEqual(v, "UNPROVEN")
        self.assertIn("not evidence", msg)

    def test_a_workday_entry_without_a_canary_is_fine(self):
        """Workday 404s on a wrong site, so a 200 is already proof."""
        self.stub(count=1347)
        v, _, _ = rc.check(entry(ats="workday", params={"host": "h", "tenant": "t", "site": "Global"}), {})
        self.assertEqual(v, "OK")


class TransientFailures(unittest.TestCase):
    """A connection reset is not a dead endpoint. One real employer reported
    UNREACHABLE! on a reset and answered fine a second later."""

    def test_it_retries_before_calling_an_endpoint_dead(self):
        calls = []
        real = rc.urllib.request.urlopen

        class Fake:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"[]"

        def flaky(req, timeout=None):
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionResetError(54, "Connection reset by peer")
            return Fake()

        rc.urllib.request.urlopen = flaky
        self.addCleanup(lambda: setattr(rc.urllib.request, "urlopen", real))
        waits = []
        real_sleep, rc.time.sleep = rc.time.sleep, waits.append
        self.addCleanup(lambda: setattr(rc.time, "sleep", real_sleep))
        self.assertEqual(rc.call("https://x/"), "[]")
        self.assertEqual(len(calls), 3)
        # The waiting is the point, not just the re-calling: hammering a host
        # that just reset the connection is how a checker gets itself blocked.
        # Asserted here because the two subprocess tests below now run with the
        # backoff at zero, so nothing else proves it happens at all.
        self.assertEqual(len(waits), 2)
        # Strictly increasing, not merely sorted: [1.5, 1.5] is sorted and is a
        # flat retry, which is what hammers a host that has just reset on you.
        self.assertTrue(all(b > a for a, b in zip(waits, waits[1:])),
                        f"the backoff must grow, not repeat: {waits}")
        self.assertTrue(all(w > 0 for w in waits), "a backoff of zero is not a backoff")


class TheBackoffIsOverridable(unittest.TestCase):
    """Only so the subprocess tests can turn it off, and that has to keep working.

    Without it those two tests cost 4.5s each and the suite went from under a
    second to twelve. A slow suite gets run less often, and CONTRIBUTING tells
    every contributor to run it before every push -- so the speed is not a
    convenience, it is whether the one control this repo trusts gets used.
    """

    def _backoff_with(self, value):
        env = dict(os.environ)
        env.pop("REGISTRY_CHECK_BACKOFF", None)
        if value is not None:
            env["REGISTRY_CHECK_BACKOFF"] = value
        r = subprocess.run(
            [sys.executable, "-c",
             "import importlib.util,sys;"
             f"s=importlib.util.spec_from_file_location('rc', {RC!r});"
             "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(m.BACKOFF)"],
            capture_output=True, text=True, env=env)
        return float(r.stdout.strip())

    def test_the_environment_can_switch_it_off(self):
        self.assertEqual(self._backoff_with("0"), 0.0)

    def test_and_the_default_is_a_real_wait(self):
        """Zero must never become the shipped default: retrying instantly is how
        a checker gets itself blocked by the host it just upset."""
        self.assertGreater(self._backoff_with(None), 0)


class TheRealRegistry(unittest.TestCase):
    def test_it_parses_and_every_entry_has_what_the_checker_needs(self):
        reg = json.load(open(os.path.join(ROOT, "tools", "radar", "ats_registry.json"), encoding="utf-8"))
        for e in reg["employers"]:
            self.assertTrue(e.get("careers_url", "").startswith("http"), e["employer"])
            self.assertIn(e["ats"], ("workday", "oracle", "greenhouse", "lever", "custom", "google"), e["employer"])
            self.assertIsInstance(e.get("verified_returned"), int, e["employer"])
            if e["ats"] == "oracle":
                self.assertTrue(e.get("canary"), f"{e['employer']}: oracle fails open, so it needs a canary")

    def test_careers_url_is_the_company_not_the_ats(self):
        """The careers page is the recovery key. An ATS link expires exactly when it is needed."""
        reg = json.load(open(os.path.join(ROOT, "tools", "radar", "ats_registry.json"), encoding="utf-8"))
        for e in reg["employers"]:
            for ats_host in ("myworkdayjobs.com", "myworkdaysite.com", "oraclecloud.com",
                             "boards.greenhouse.io", "jobs.lever.co"):
                self.assertNotIn(ats_host, e["careers_url"],
                                 f"{e['employer']}: careers_url points at the ATS, not the company")


# These two drive the checker as a subprocess against a dead port on purpose, so
# they cannot stub time.sleep the way the in-process test above does. At the real
# backoff they cost 4.5s each -- more than the rest of the suite put together.
NO_BACKOFF = dict(os.environ, REGISTRY_CHECK_BACKOFF="0")


class CommandLine(unittest.TestCase):
    def test_it_does_not_rewrite_the_registry_unless_asked(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        path = os.path.join(d, "ats_registry.json")
        reg = {"version": 1, "_endpoints": {}, "employers": [entry(params={"list": "https://127.0.0.1:9/"})]}
        with open(path, "w") as fh:
            json.dump(reg, fh)
        before = open(path).read()
        subprocess.run([sys.executable, RC, "--registry", path],
                       capture_output=True, text=True, env=NO_BACKOFF)
        self.assertEqual(open(path).read(), before)

    def test_a_failure_exits_one_so_it_can_gate(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        path = os.path.join(d, "ats_registry.json")
        with open(path, "w") as fh:
            json.dump({"version": 1, "_endpoints": {},
                       "employers": [entry(params={"list": "https://127.0.0.1:9/unreachable"})]}, fh)
        r = subprocess.run([sys.executable, RC, "--registry", path],
                           capture_output=True, text=True, env=NO_BACKOFF)
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNREACHABLE!", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
