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
    {"employer": "Stateline Capital", "ats": "workday", "careers_url": "https://x",
     "params": {"host": "h", "tenant": "t", "site": "Global"}},
    {"employer": "Widget Advisory Ireland", "ats": "oracle", "careers_url": "https://y",
     "params": {"host": "gh", "site": "CX_1001"}},
    {"employer": "Stripe", "ats": "greenhouse", "careers_url": "https://z", "params": {"token": "stripe"}},
    {"employer": "Deel", "ats": "custom", "careers_url": "https://d", "params": {"list": "https://d/api"}},
    # An ATS nothing speaks. Deel used to play this part and now has an adapter,
    # which is why the branch needs a stand-in rather than being deleted with it.
    {"employer": "Obscure GmbH", "ats": "bespoke_thing", "careers_url": "https://o", "params": {}},
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
        cfg, rep = run(["Stateline Capital"])
        self.assertEqual(rep["Stateline Capital"][0], "RESOLVED")
        self.assertEqual(cfg["workday"]["employers"],
                         [{"host": "h", "tenant": "t", "site": "Global"}])

    def test_a_greenhouse_employer_becomes_a_bare_token(self):
        cfg, _ = run(["Stripe"])
        self.assertEqual(cfg["greenhouse"]["boards"], ["stripe"])

    def test_matching_is_case_insensitive_and_forgiving(self):
        _, rep = run(["  widget advisory ireland  "])
        self.assertEqual(rep["Widget Advisory Ireland"][0], "RESOLVED")

    def test_it_reports_the_canonical_name_and_says_what_was_typed(self):
        """Substring matching is where a wrong resolution would hide, so show it."""
        _, rep = run(["Widget Advisory"])
        status, msg = rep["Widget Advisory Ireland"]
        self.assertEqual(status, "RESOLVED")
        self.assertIn("matched on 'Widget Advisory'", msg)


class NothingIsDroppedSilently(unittest.TestCase):
    def test_it_labels_the_rows_with_the_employer_not_the_slug(self):
        """The registry knows the employer is called "Stateline Capital"; the ATS
        calls the tenant "statestreet". Adapters label every row with whatever
        the source says, so without this the shortlist shows slugs -- which
        reads badly, defeats cross-source dedup (one source says "Citi", the
        other "citi", so one role appears twice), and silently breaks an avoid
        entry written with the real name.

        workday and oracle already read an optional `names` map whose stated
        purpose is exactly this. Nothing was filling it in."""
        cfg, _ = registry.resolve({"watch": ["Stateline Capital", "Widget Advisory Ireland"]}, REG)
        self.assertEqual(cfg["workday"]["names"].get("t"), "Stateline Capital")
        self.assertEqual(cfg["oracle"]["names"].get("CX_1001"), "Widget Advisory Ireland")

    def test_a_hand_written_name_is_not_overwritten(self):
        """The map is the user's file. Filling a gap is help; changing what
        somebody typed is not."""
        cfg = {"watch": ["Stateline Capital"], "workday": {"names": {"t": "My Own Label"}}}
        cfg, _ = registry.resolve(cfg, REG)
        self.assertEqual(cfg["workday"]["names"]["t"], "My Own Label")

    def test_two_employers_sharing_a_slug_are_both_left_unlabelled(self):
        """Oracle's default site identifier is the same string for many
        tenants -- two shipped entries really do both use CX_1001. The map is
        keyed on the slug, so labelling both would print one employer's name on
        the other's rows.

        A slug is unhelpful. A confidently wrong employer name is worse, and it
        would be believed. So a collision removes the label rather than picking
        a winner, and says so."""
        reg = {"employers": [
            {"employer": "First Bank", "ats": "oracle", "careers_url": "https://a",
             "params": {"host": "a", "site": "CX_1001"}},
            {"employer": "Second Bank", "ats": "oracle", "careers_url": "https://b",
             "params": {"host": "b", "site": "CX_1001"}}]}
        cfg, rep = registry.resolve({"watch": ["First Bank", "Second Bank"]}, reg)
        self.assertNotIn("CX_1001", cfg["oracle"].get("names", {}))
        self.assertTrue(any("NEITHER is labelled" in r[2] for r in rep), rep)
        self.assertEqual(len(rep), 2, "still one report line per watched name")

    def test_an_unknown_name_is_reported(self):
        _, rep = run(["Acme Corp"])
        self.assertEqual(rep["Acme Corp"][0], "NOT IN REGISTRY")

    def test_an_ats_with_no_adapter_is_reported_with_the_careers_url(self):
        """Saying so beats searching four of five employers quietly."""
        _, rep = run(["Obscure GmbH"])
        status, msg = rep["Obscure GmbH"]
        self.assertEqual(status, "NO ADAPTER")
        self.assertIn("https://o", msg)

    def test_a_bespoke_api_resolves_now_that_custom_exists(self):
        cfg, rep = run(["Deel"])
        self.assertEqual(rep["Deel"][0], "RESOLVED")
        self.assertEqual(cfg["custom"]["employers"][0]["employer"], "Deel")

    def test_an_incomplete_registry_entry_is_reported_not_half_used(self):
        _, rep = run(["Halfling Ltd"])
        self.assertEqual(rep["Halfling Ltd"][0], "INCOMPLETE")

    def test_the_report_counts_what_will_not_be_searched(self):
        _, report = registry.resolve({"watch": ["Obscure GmbH", "Acme Corp", "Stripe"]}, REG)
        out = registry.format_report(report)
        self.assertIn("2 watched employer(s) will NOT be searched", out)


class Ambiguity(unittest.TestCase):
    def test_two_matches_refuses_rather_than_guessing(self):
        """Guessing would watch the wrong employer, and the user would see a quiet week."""
        _, rep = run(["State"])
        status, msg = rep["State"]
        self.assertEqual(status, "AMBIGUOUS")
        self.assertIn("Stateline Capital", msg)
        self.assertIn("Statesman Bank", msg)

    def test_an_exact_name_beats_a_substring_collision(self):
        _, rep = run(["Stateline Capital"])
        self.assertEqual(rep["Stateline Capital"][0], "RESOLVED")


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


class Listing(unittest.TestCase):
    """Wanting to know who is on the list should not cost fifteen requests to
    other people's servers, which is what registry_check does."""

    def test_it_names_every_employer_without_calling_anything(self):
        out = registry.listing(REG)
        for e in REG["employers"]:
            self.assertIn(e["employer"], out)

    def test_an_empty_registry_says_so_rather_than_printing_a_header(self):
        self.assertIn("empty", registry.listing({"employers": []}))

    def test_it_says_how_to_add_one(self):
        self.assertIn("add_employer.py", registry.listing(REG))


class AgainstTheRealRegistry(unittest.TestCase):
    def test_every_shipped_entry_either_resolves_or_says_why(self):
        real = registry.load_registry()
        names = [e["employer"] for e in real["employers"]]
        _, report = registry.resolve({"watch": names}, real)
        self.assertEqual(len(report), len(names), "every watched name must produce a line")
        for name, status, msg in report:
            self.assertEqual(status, "RESOLVED",
                             f"{name}: {status} {msg} -- every shipped entry should now resolve")


if __name__ == "__main__":
    unittest.main(verbosity=2)
