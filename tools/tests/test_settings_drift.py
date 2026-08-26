"""settings_drift: what has the system started reading that this vault never got?

🔴 THE INCIDENT THIS GENERALISES. `git pull` updates the system and cannot touch
`vault/` -- that is the boundary and it is correct. The corollary nobody checked
is that an update can ship a system needing a vault file it has no way to
deliver. When the radar's tiering vocabulary moved into vault/settings/signal.json
on 2026-08-26, anybody who pulled got the new radar and not the file it reads.
Nothing errored: HIGH and MED were simply always empty, which reads as a quiet
week rather than a broken install.

Most of the tests below are false-positive tests, because that is the whole risk
here. A drift check that reports faults on a correct vault gets muted, and then
it is worth less than nothing -- it looks like coverage.
"""
import importlib.util, io, json, os, shutil, sys, tempfile, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SD = os.path.join(ROOT, "tools", "settings_drift.py")
spec = importlib.util.spec_from_file_location("settings_drift", SD)
drift = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drift)

TEMPLATES = os.path.join(ROOT, "templates", "settings")


class Vault:
    """A settings directory, written from whatever the test hands it."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        return self

    def write(self, name, obj):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
            fh.write(obj if isinstance(obj, str) else json.dumps(obj))

    def copy_example(self, stem):
        shutil.copy(os.path.join(TEMPLATES, stem + ".example.json"),
                    os.path.join(self.dir, stem + ".json"))

    def run(self, templates=TEMPLATES):
        buf = io.StringIO()
        argv = sys.argv
        sys.argv = ["settings_drift.py", "--settings", self.dir, "--templates", templates]
        try:
            with redirect_stdout(buf):
                code = drift.main()
        finally:
            sys.argv = argv
        return code, buf.getvalue()

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)


class TheFalsePositiveCases(unittest.TestCase):
    """🔴 Tested before the catching cases, deliberately.

    The first version of this check reported five findings against a completely
    healthy, current vault -- every one of them a `_comment` or `_README` block.
    A check like that is switched off within a week, and the repo has the rule
    because it has happened here before.
    """

    def test_a_vault_copied_from_the_shipped_examples_is_clean(self):
        """The strongest version: use the REAL templates, not a fixture.

        This is what a brand-new user has five minutes after cloning, and it must
        come back with nothing to do.
        """
        with Vault() as v:
            for f in os.listdir(TEMPLATES):
                if f.endswith(drift.SUFFIX):
                    v.copy_example(f[: -len(drift.SUFFIX)])
            code, out = v.run()
            self.assertEqual(code, 0, out)
            self.assertIn("0 key(s) missing", out)

    def test_prose_keys_are_ignored_in_both_directions(self):
        """These files explain themselves in `_comment` and `_needs_you` blocks
        and both sides accumulate their own. Comparing them is pure noise."""
        example = {"queries": [], "_comment": ["a"], "_shipped_note": ["b"]}
        actual = {"queries": ["mine"], "_README": ["c"], "_provenance": ["d"]}
        self.assertEqual(drift.compare(example, actual), ([], []))

    def test_nested_prose_is_ignored_too(self):
        """The real vault carried `thresholds._comment`, which a top-level-only
        rule would have reported."""
        self.assertEqual(
            drift.compare({"thresholds": {"high": 1, "_comment": ["why"]}},
                          {"thresholds": {"high": 18}}),
            ([], []))

    def test_list_contents_are_never_compared(self):
        """A list in these files is always data -- queries, boards, weighted
        patterns. Comparing them would report a user's own search terms as
        drift, which is both wrong and a privacy-shaped mistake."""
        example = {"queries": ["<a job title you would take>"],
                   "positive": [{"match": "<a technology>", "weight": 6}]}
        actual = {"queries": ["Head of Delivery", "AI Governance"],
                  "positive": [{"match": "delivery", "weight": 6},
                               {"match": "governance", "weight": 4}]}
        self.assertEqual(drift.compare(example, actual), ([], []))

    def test_an_unrecognised_key_does_not_fail_the_run(self):
        """It might be theirs. Report it, do not fail on it -- the exit code is
        reserved for 'the system reads something you have not got'."""
        with Vault() as v:
            v.write("search.json", {"queries": [], "my_own_note": "keep"})
            code, out = v.run(templates=self._templates({"search": {"queries": []}}))
            self.assertEqual(code, 0)
            self.assertIn("my_own_note", out)

    def test_a_settings_file_the_vault_never_adopted_is_not_a_failure(self):
        """🔴 The asymmetry that keeps this runnable. Most settings are optional.
        Somebody who never wants oversight should not be told they are out of
        date every week for the rest of the year."""
        with Vault() as v:
            code, out = v.run()
            self.assertEqual(code, 0, out)
            self.assertIn("Not a fault on its own", out)

    def _templates(self, spec):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        for stem, obj in spec.items():
            with open(os.path.join(d, stem + drift.SUFFIX), "w", encoding="utf-8") as fh:
                json.dump(obj, fh)
        return d


class TheCatchingCases(unittest.TestCase):

    def test_the_signal_incident_is_caught(self):
        """The actual event, replayed: a vault whose vocabulary predates the
        thresholds and exclusions the current radar reads."""
        old = {"positive": [{"match": "delivery", "weight": 6}], "negative": []}
        with open(os.path.join(TEMPLATES, "signal.example.json"), encoding="utf-8") as fh:
            example = json.load(fh)
        missing, _ = drift.compare(example, old)
        self.assertIn("thresholds", missing)

    def test_a_missing_key_fails_the_run(self):
        with Vault() as v:
            v.write("search.json", {"queries": []})
            code, out = v.run(templates=self._t({"search": {"queries": [], "linkedin": {}}}))
            self.assertEqual(code, 1)
            self.assertIn("linkedin", out)

    def test_only_the_outermost_missing_key_is_reported(self):
        """🔴 Volume is the other way a check cries wolf.

        A vault predating the LinkedIn adapter is missing ONE block, but the
        naive comparison reports the parent plus every child -- five findings
        for one decision. Measured on a vault two updates behind: 16 raw
        differences, 6 actual gaps.
        """
        example = {"linkedin": {"enabled": True, "location": "", "pages": 4, "delay": 1}}
        missing, _ = drift.compare(example, {})
        self.assertEqual(missing, ["linkedin"])

    def test_a_child_alone_is_still_reported(self):
        """The collapse must not swallow a real finding: the parent is present,
        so the missing child is the whole gap."""
        example = {"location": {"ok": [], "bad": [], "edge": []}}
        missing, _ = drift.compare(example, {"location": {"ok": ["Ireland"]}})
        self.assertEqual(missing, ["location.bad", "location.edge"])

    def test_a_key_nothing_reads_any_more_is_surfaced(self):
        """A renamed setting leaves the old one behind, still looking configured
        and doing nothing at all."""
        _, unknown = drift.compare({"queries": []}, {"queries": [], "min_salary": 90000})
        self.assertEqual(unknown, ["min_salary"])

    def test_a_settings_file_with_no_example_is_named(self):
        """Found a real one on the day it was written: profile.json shipped
        without a template, so nobody cloning could discover it existed."""
        with Vault() as v:
            v.write("invented.json", {"a": 1})
            code, out = v.run(templates=self._t({"search": {"queries": []}}))
            self.assertIn("invented.json", out)

    def test_broken_json_is_reported_rather_than_crashing(self):
        with Vault() as v:
            v.write("search.json", "{not json")
            code, out = v.run(templates=self._t({"search": {"queries": []}}))
            self.assertIn("not valid JSON", out)

    def test_an_empty_vault_is_not_drift(self):
        d = tempfile.mkdtemp()
        shutil.rmtree(d)
        argv = sys.argv
        sys.argv = ["settings_drift.py", "--settings", d]
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = drift.main()
        finally:
            sys.argv = argv
        self.assertEqual(code, 0)
        self.assertIn("not\n  drift", buf.getvalue())

    def _t(self, spec):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        for stem, obj in spec.items():
            with open(os.path.join(d, stem + drift.SUFFIX), "w", encoding="utf-8") as fh:
                json.dump(obj, fh)
        return d


class TheShippedExamples(unittest.TestCase):
    """The check is only as good as the templates it reads."""

    def test_every_example_parses(self):
        for f in sorted(os.listdir(TEMPLATES)):
            if f.endswith(drift.SUFFIX):
                with open(os.path.join(TEMPLATES, f), encoding="utf-8") as fh:
                    json.load(fh)

    def test_every_settings_path_the_system_knows_has_an_example(self):
        """🔴 The gap this tool found in its first run.

        paths.py names five settings files. If one ships no example, a user
        cannot discover it exists -- and the tool that reads it silently falls
        back to a default nobody chose.
        """
        sys.path.insert(0, os.path.join(ROOT, "tools", "lib"))
        import paths
        shipped = {f[: -len(drift.SUFFIX)] for f in os.listdir(TEMPLATES)
                   if f.endswith(drift.SUFFIX)}
        for attr in ("SEARCH", "EMPLOYERS", "PROFILE", "REVIEW", "SIGNAL"):
            stem = os.path.basename(getattr(paths, attr))[: -len(".json")]
            self.assertIn(stem, shipped,
                          f"paths.{attr} has no templates/settings/{stem}.example.json, "
                          f"so nobody cloning this repo can discover the setting exists")


if __name__ == "__main__":
    unittest.main(verbosity=2)
