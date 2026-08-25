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


class TheRealRegistry(unittest.TestCase):
    def test_it_parses_and_every_entry_has_what_the_checker_needs(self):
        reg = json.load(open(os.path.join(ROOT, "tools", "radar", "employers.json"), encoding="utf-8"))
        for e in reg["employers"]:
            self.assertTrue(e.get("careers_url", "").startswith("http"), e["employer"])
            self.assertIn(e["ats"], ("workday", "oracle", "greenhouse", "lever", "custom"), e["employer"])
            self.assertIsInstance(e.get("verified_returned"), int, e["employer"])
            if e["ats"] == "oracle":
                self.assertTrue(e.get("canary"), f"{e['employer']}: oracle fails open, so it needs a canary")

    def test_careers_url_is_the_company_not_the_ats(self):
        """The careers page is the recovery key. An ATS link expires exactly when it is needed."""
        reg = json.load(open(os.path.join(ROOT, "tools", "radar", "employers.json"), encoding="utf-8"))
        for e in reg["employers"]:
            for ats_host in ("myworkdayjobs.com", "myworkdaysite.com", "oraclecloud.com",
                             "boards.greenhouse.io", "jobs.lever.co"):
                self.assertNotIn(ats_host, e["careers_url"],
                                 f"{e['employer']}: careers_url points at the ATS, not the company")


class CommandLine(unittest.TestCase):
    def test_it_does_not_rewrite_the_registry_unless_asked(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        path = os.path.join(d, "employers.json")
        reg = {"version": 1, "_endpoints": {}, "employers": [entry(params={"list": "https://127.0.0.1:9/"})]}
        with open(path, "w") as fh:
            json.dump(reg, fh)
        before = open(path).read()
        subprocess.run([sys.executable, RC, "--registry", path], capture_output=True, text=True)
        self.assertEqual(open(path).read(), before)

    def test_a_failure_exits_one_so_it_can_gate(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        path = os.path.join(d, "employers.json")
        with open(path, "w") as fh:
            json.dump({"version": 1, "_endpoints": {},
                       "employers": [entry(params={"list": "https://127.0.0.1:9/unreachable"})]}, fh)
        r = subprocess.run([sys.executable, RC, "--registry", path], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNREACHABLE!", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
