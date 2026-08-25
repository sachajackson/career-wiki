"""sources_check: would this source work, before anyone relies on it.

Built for a failure that cost a real user an hour. They obtained an API key,
wired it up, and found out afterwards that the board does not cover their
country at all -- 404 there while serving four others. The hour went on
debugging a key that was never broken.

So the tests that matter here are the ones about telling apart things a naive
check collapses:

  NOT CONFIGURED is not FAILED -- an adapter nobody set up has not been tried.
  NO COVERAGE is not BAD CREDENTIALS -- and one probe cannot tell them apart,
  which is why the adapters that can hit that ambiguity probe a known-good
  control as well.

The Oracle case is the same shape found a second time, from the other end: an
unrecognised site does not fail, it silently WIDENS to the whole tenant, so a
typo returns more roles rather than none.
"""
import importlib.util, io, os, sys, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RADAR = os.path.join(ROOT, "tools", "radar")
sys.path.insert(0, RADAR)
from adapters import adzuna, greenhouse, lever, linkedin, oracle, workday   # noqa: E402
from adapters import _verdicts as V                                          # noqa: E402

spec = importlib.util.spec_from_file_location("sources_check",
                                              os.path.join(RADAR, "sources_check.py"))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


class NotConfiguredIsNotFailed(unittest.TestCase):
    """The distinction the whole report is built on.

    Reported as broken it sends someone to debug a source they never wanted;
    reported as fine it claims coverage that does not exist.
    """

    def test_every_adapter_says_so_rather_than_failing(self):
        for mod in (adzuna, greenhouse, lever, linkedin, oracle, workday):
            verdict, detail = mod.probe({})
            self.assertEqual(verdict, V.NOT_CONFIGURED, mod.NAME)
            self.assertTrue(detail, mod.NAME)

    def test_a_placeholder_country_is_unset_not_broken(self):
        """A fresh clone's config is full of <angle brackets>."""
        v, _ = adzuna.probe({"adzuna": {"app_id": "a", "app_key": "b",
                                        "country": "<iso-2, e.g. gb>"}})
        self.assertEqual(v, V.NOT_CONFIGURED)

    def test_linkedin_being_off_is_a_decision_not_a_fault(self):
        v, d = linkedin.probe({"linkedin": {"enabled": False}})
        self.assertEqual(v, V.NOT_CONFIGURED)
        self.assertIn("your call", d)


class NoCoverageIsNotABadKey(unittest.TestCase):
    """The original incident, and the reason for the control probe."""

    def setUp(self):
        self.cfg = {"adzuna": {"app_id": "a", "app_key": "b", "country": "ie"}}

    def _codes(self, mine, control):
        seen = {}
        def fake(url, headers=None, timeout=30):
            code = control if f"/{adzuna.CONTROL}/" in url else mine
            seen[url] = code
            return ({"results": []} if code == 200 else None), code
        adzuna.fetch_json = fake
        return seen

    def test_a_404_against_a_working_control_is_the_country(self):
        self._codes(mine=404, control=200)
        v, d = adzuna.probe(self.cfg)
        self.assertEqual(v, V.NO_COVERAGE)
        self.assertIn("does not cover", d)
        self.assertIn("Your key is fine", d)

    def test_a_401_is_the_key_and_needs_no_control_at_all(self):
        self._codes(mine=401, control=200)
        v, d = adzuna.probe(self.cfg)
        self.assertEqual(v, V.BAD_CREDENTIALS)
        self.assertIn("not the country", d)

    def test_a_control_that_also_refuses_means_the_key(self):
        """404 on yours AND 403 on a country it definitely serves."""
        self._codes(mine=404, control=403)
        v, d = adzuna.probe(self.cfg)
        self.assertEqual(v, V.BAD_CREDENTIALS)
        self.assertIn("it is the key", d)

    def test_both_unreachable_is_neither_diagnosis(self):
        """Refusing to guess is the point. The API may simply be down."""
        self._codes(mine=None, control=None)
        v, d = adzuna.probe(self.cfg)
        self.assertEqual(v, V.FAILED)
        self.assertIn("may be down", d)

    def test_a_working_country_needs_no_control_request(self):
        seen = self._codes(mine=200, control=200)
        v, _ = adzuna.probe(self.cfg)
        self.assertEqual(v, V.OK)
        self.assertEqual(len(seen), 1)


class OracleWidensRatherThanFailing(unittest.TestCase):
    """An unrecognised site returns MORE roles, not none. Verified live.

    On one tenant a real site scoped to 152 while a nonsense one returned 258.
    Nothing in a single response tells those apart.
    """

    def _counts(self, real, control):
        def fake(url, headers=None):
            n = control if oracle.CONTROL_SITE in url else real
            return {"items": [{"TotalJobsCount": n, "requisitionList": []}]}, 200
        oracle.fetch_json = fake

    def test_a_site_that_matches_the_nonsense_control_is_flagged(self):
        self._counts(real=258, control=258)
        v, d = oracle.probe({"oracle": {"employers": [{"host": "h", "site": "<site>"}]}})
        self.assertEqual(v, V.OK)
        self.assertIn("may be ignored", d)
        self.assertIn("whole tenant", d)

    def test_a_site_that_scopes_differently_is_not_flagged(self):
        self._counts(real=152, control=258)
        v, d = oracle.probe({"oracle": {"employers": [{"host": "h", "site": "<site>"}]}})
        self.assertEqual(v, V.OK)
        self.assertNotIn("may be ignored", d)

    def test_the_warning_is_said_once_not_per_employer(self):
        """Repeated per employer it becomes a wall, which for a warning is the
        same as not printing it at all."""
        self._counts(real=258, control=258)
        _, d = oracle.probe({"oracle": {"employers": [
            {"host": "h", "site": "<a>"}, {"host": "h", "site": "<b>"},
            {"host": "h", "site": "<c>"}]}})
        self.assertEqual(d.count("whole tenant"), 1)
        self.assertIn("3 site value(s)", d)

    def test_an_entry_missing_a_value_is_named_not_silently_skipped(self):
        self._counts(real=1, control=2)
        v, d = oracle.probe({"oracle": {"employers": [{"host": "h"}]}})
        self.assertEqual(v, V.FAILED)
        self.assertIn("needs host AND site", d)


class WorkdayDiagnoses(unittest.TestCase):
    def test_a_422_is_reported_as_a_shard_not_as_a_bad_request(self):
        """The request was right. Reported generically it sends someone to
        rewrite a request that was correct all along."""
        workday.post_json = lambda url, payload, headers=None, timeout=30: (None, 422)
        v, d = workday.probe({"workday": {"employers": [
            {"host": "h", "tenant": "<tenant>", "site": "s"}]}})
        self.assertEqual(v, V.FAILED)
        self.assertIn("wrong wd shard", d)
        self.assertIn("wd3/wd5", d)

    def test_a_partial_entry_says_which_values_are_needed(self):
        workday.post_json = lambda url, payload, headers=None, timeout=30: ({"total": 1}, 200)
        v, d = workday.probe({"workday": {"employers": [
            {"host": "h", "tenant": "<a>", "site": "s"}, {"tenant": "<b>"}]}})
        self.assertEqual(v, V.OK)
        self.assertIn("host, tenant AND site", d)
        self.assertIn("1/2", d)


class Boards(unittest.TestCase):
    def test_a_partial_failure_names_the_ones_that_did_not_resolve(self):
        greenhouse.fetch_json = lambda url, headers=None: (
            ({"jobs": []}, 200) if "good" in url else (None, 404))
        v, d = greenhouse.probe({"greenhouse": {"boards": ["good", "<bad>"]}})
        self.assertEqual(v, V.OK)
        self.assertIn("1/2", d)
        self.assertIn("<bad> (404)", d)

    def test_none_resolving_is_a_failure_with_somewhere_to_look(self):
        lever.fetch_json = lambda url, headers=None: (None, 404)
        v, d = lever.probe({"lever": {"companies": ["<a>"]}})
        self.assertEqual(v, V.FAILED)
        self.assertIn("jobs.lever.co", d)


class TheReport(unittest.TestCase):
    def _run(self, adapters, cfg=None, emp=None):
        old = (sc.ADAPTERS, sc.load)
        sc.ADAPTERS = adapters
        sc.load = lambda p, w: ((cfg or {}) if "config" in p else (emp or {}), None)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = sc.main()
        finally:
            sc.ADAPTERS, sc.load = old
        return code, buf.getvalue()

    def test_it_leads_with_what_needs_attention(self):
        class M:
            def __init__(self, v): self.v = v
            def probe(self, cfg): return self.v, "d"
        code, out = self._run({"aaa_ok": M(V.OK), "zzz_bad": M(V.BAD_CREDENTIALS)})
        self.assertLess(out.index("zzz_bad"), out.index("aaa_ok"))
        self.assertEqual(code, 1)

    def test_a_probe_that_raises_does_not_kill_the_report(self):
        """One broken adapter must not hide the state of the other five."""
        class Boom:
            def probe(self, cfg): raise RuntimeError("x")
        class Fine:
            def probe(self, cfg): return V.OK, "d"
        code, out = self._run({"boom": Boom(), "fine": Fine()})
        self.assertIn("probe raised RuntimeError", out)
        self.assertIn("fine", out)

    def test_nothing_usable_is_called_out_loudly(self):
        """A silent radar run looks exactly like a quiet week."""
        class M:
            def probe(self, cfg): return V.NOT_CONFIGURED, "d"
        code, out = self._run({"a": M()})
        self.assertIn("NOTHING here can return a role", out)
        self.assertEqual(code, 1)

    def test_the_watchlist_is_folded_in_before_anything_is_probed(self):
        """Otherwise every board adapter reports NOT CONFIGURED while the user
        is looking at a watchlist full of employers."""
        seen = {}
        class M:
            def probe(self, cfg): seen.update(cfg); return V.OK, "d"
        _, out = self._run({"greenhouse": M()}, cfg={},
                           emp={"watch": [{"employer": "<A>", "greenhouse": "tok"}]})
        self.assertEqual(seen.get("greenhouse", {}).get("boards"), ["tok"])
        self.assertIn("1 employer(s) routed", out)

    def test_an_unroutable_watch_entry_is_surfaced_here_too(self):
        class M:
            def probe(self, cfg): return V.OK, "d"
        _, out = self._run({"a": M()}, emp={"watch": [{"employer": "<A>"}]})
        self.assertIn("NO ROUTE", out)
        self.assertIn("<A>", out)

    def test_an_adapter_with_no_probe_is_reported_not_skipped(self):
        class M: pass
        _, out = self._run({"mute": M()})
        self.assertIn("cannot be checked", out)


if __name__ == "__main__":
    unittest.main()
