"""registry.resolve: naming an employer instead of knowing their ATS.

The rule under test is that nothing is dropped silently. An employer watched but
not searched -- because nobody wrote an adapter for its ATS, or the name was
misspelt -- is the same failure as a search window that quietly covered a week:
the run succeeds, the roles are missing, and nothing says so.
"""
import importlib.util, json, os, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("registry", os.path.join(ROOT, "tools", "radar", "registry.py"))
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)

REG = {"employers": [
    {"employer": "State Street", "ats": "workday", "careers_url": "https://x",
     "params": {"host": "h", "tenant": "t", "site": "Global"}},
    {"employer": "Grant Thornton Ireland", "ats": "oracle", "careers_url": "https://y",
     "params": {"host": "gh", "site": "CX_1001"}},
    {"employer": "Stripe", "ats": "greenhouse", "careers_url": "https://z", "params": {"token": "stripe"}},
    {"employer": "Deel", "ats": "custom", "careers_url": "https://d", "params": {"list": "https://d/api"}},
    {"employer": "Statesman Bank", "ats": "lever", "careers_url": "https://s", "params": {"handle": "sb"}},
    {"employer": "Halfling Ltd", "ats": "workday", "careers_url": "https://hl", "params": {"host": "h"}},
]}


def run(watch, config=None):
    cfg = config or {}
    cfg["watch"] = watch
    cfg, report = registry.resolve(cfg, REG)
    return cfg, {name: (status, msg) for name, status, msg in report}


class Resolving(unittest.TestCase):
    def test_a_workday_employer_becomes_host_tenant_site(self):
        cfg, rep = run(["State Street"])
        self.assertEqual(rep["State Street"][0], "RESOLVED")
        self.assertEqual(cfg["workday"]["employers"],
                         [{"host": "h", "tenant": "t", "site": "Global"}])

    def test_a_greenhouse_employer_becomes_a_bare_token(self):
        cfg, _ = run(["Stripe"])
        self.assertEqual(cfg["greenhouse"]["boards"], ["stripe"])

    def test_matching_is_case_insensitive_and_forgiving(self):
        _, rep = run(["  grant thornton ireland  "])
        self.assertEqual(rep["Grant Thornton Ireland"][0], "RESOLVED")

    def test_it_reports_the_canonical_name_and_says_what_was_typed(self):
        """Substring matching is where a wrong resolution would hide, so show it."""
        _, rep = run(["Grant Thornton"])
        status, msg = rep["Grant Thornton Ireland"]
        self.assertEqual(status, "RESOLVED")
        self.assertIn("matched on 'Grant Thornton'", msg)


class NothingIsDroppedSilently(unittest.TestCase):
    def test_an_unknown_name_is_reported(self):
        _, rep = run(["Acme Corp"])
        self.assertEqual(rep["Acme Corp"][0], "NOT IN REGISTRY")

    def test_an_ats_with_no_adapter_is_reported_with_the_careers_url(self):
        """Deel proxies its own ATS. Saying so beats searching four of five employers quietly."""
        _, rep = run(["Deel"])
        status, msg = rep["Deel"]
        self.assertEqual(status, "NO ADAPTER")
        self.assertIn("https://d", msg)

    def test_an_incomplete_registry_entry_is_reported_not_half_used(self):
        _, rep = run(["Halfling Ltd"])
        self.assertEqual(rep["Halfling Ltd"][0], "INCOMPLETE")

    def test_the_report_counts_what_will_not_be_searched(self):
        _, report = registry.resolve({"watch": ["Deel", "Acme Corp", "Stripe"]}, REG)
        out = registry.format_report(report)
        self.assertIn("2 watched employer(s) will NOT be searched", out)


class Ambiguity(unittest.TestCase):
    def test_two_matches_refuses_rather_than_guessing(self):
        """Guessing would watch the wrong employer, and the user would see a quiet week."""
        _, rep = run(["State"])
        status, msg = rep["State"]
        self.assertEqual(status, "AMBIGUOUS")
        self.assertIn("State Street", msg)
        self.assertIn("Statesman Bank", msg)

    def test_an_exact_name_beats_a_substring_collision(self):
        _, rep = run(["State Street"])
        self.assertEqual(rep["State Street"][0], "RESOLVED")


class HandWrittenConfigSurvives(unittest.TestCase):
    def test_it_merges_rather_than_replacing(self):
        cfg, _ = run(["Stripe"], {"greenhouse": {"boards": ["monzo"]}})
        self.assertEqual(cfg["greenhouse"]["boards"], ["monzo", "stripe"])

    def test_an_employer_already_listed_by_hand_is_not_added_twice(self):
        cfg, rep = run(["Stripe"], {"greenhouse": {"boards": ["stripe"]}})
        self.assertEqual(rep["Stripe"][0], "ALREADY LISTED")
        self.assertEqual(cfg["greenhouse"]["boards"], ["stripe"])

    def test_comments_left_in_the_array_are_not_resolved_as_employers(self):
        _, rep = run(["_comment: name employers here", "Stripe"])
        self.assertNotIn("_comment: name employers here", rep)
        self.assertEqual(rep["Stripe"][0], "RESOLVED")


class AgainstTheRealRegistry(unittest.TestCase):
    def test_every_shipped_entry_either_resolves_or_says_why(self):
        real = registry.load_registry()
        names = [e["employer"] for e in real["employers"]]
        _, report = registry.resolve({"watch": names}, real)
        self.assertEqual(len(report), len(names), "every watched name must produce a line")
        for name, status, msg in report:
            self.assertIn(status, ("RESOLVED", "NO ADAPTER"), f"{name}: {status} {msg}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
