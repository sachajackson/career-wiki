"""doctor: am I set up, and what will silently do nothing if I am not?

Setting this up means three config files copied from examples, a git setting, a
CV in a folder and up to two API keys. Nothing answered "am I ready" --
sources_check.py answers a third of it, and only about job sources.

The failure it is really for: a config copied from the example and never filled
in LOOKS CONFIGURED AND RETURNS NOTHING. search.example.json says so in its own
first line -- leave the angle-bracket values and the location filter matches
nothing. Run for real with an untouched example config, the radar reports
"3 fetched, HIGH 0, MED 0" and exits successfully. That is a quiet week that
never happened, and a missing file would have been louder than a filled one.

The other distinction, which this repo has now got wrong in four places:
OPTIONAL is not MISSING. Most of this is optional, and reporting an unconfigured
thing as a fault sends someone to fix what they never wanted.
"""
import importlib.util, io, json, os, shutil, sys, tempfile, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC = os.path.join(ROOT, "tools", "doctor.py")
spec = importlib.util.spec_from_file_location("doctor", DOC)
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class Home:
    """A fake install: sources/, wiki/, tools/radar/, tools/review/."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        for d in ("vault/sources", "vault/wiki", "vault/settings", "tools/radar", "tools/review"):
            os.makedirs(os.path.join(self.dir, d))
        self.write("tools/radar/ats_registry.json", {"version": 1, "employers": [{}, {}]})
        self._saved = (doctor.ROOT, doctor.HERE, doctor.paths.VAULT)
        doctor.ROOT, doctor.HERE = self.dir, os.path.join(self.dir, "tools")
        # One re-root instead of patching every path doctor happens to read.
        doctor.paths.use(os.path.join(self.dir, "vault"))
        return self

    def write(self, rel, obj):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(obj if isinstance(obj, str) else json.dumps(obj))

    def run(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = doctor.main()
        return code, buf.getvalue()

    def __exit__(self, *a):
        doctor.ROOT, doctor.HERE = self._saved[0], self._saved[1]
        doctor.paths.use(self._saved[2])
        shutil.rmtree(self.dir, ignore_errors=True)


class ThePlaceholderCase(unittest.TestCase):
    """The one worth having. A missing file announces itself; a file full of
    example values does not, and behaves like a working one that finds nothing."""

    def test_an_untouched_example_config_is_caught(self):
        with Home() as h:
            h.write("vault/settings/search.json",
                    {"queries": ["<a job title you would take>"],
                     "location": {"ok": ["<your city>"], "bad": []}})
            verdict, detail = doctor.check_radar_config()
            self.assertEqual(verdict, doctor.PLACEHOLDER)
            self.assertIn("looks configured", detail)

    def test_a_filled_config_is_ready(self):
        with Home() as h:
            h.write("vault/settings/search.json",
                    {"queries": ["head of delivery"], "location": {"ok": ["<city>".strip("<>")]}})
            self.assertEqual(doctor.check_radar_config()[0], doctor.OK)

    def test_comment_keys_are_not_mistaken_for_placeholders(self):
        """Every example file documents itself in _comment blocks full of
        angle brackets. Flagging those would make the check unusable."""
        with Home() as h:
            h.write("vault/settings/search.json",
                    {"_comment": ["copy this to <somewhere>", "set <your city>"],
                     "queries": ["delivery manager"], "location": {"ok": ["dublin"]}})
            self.assertEqual(doctor.check_radar_config()[0], doctor.OK)

    def test_placeholders_are_found_however_deep_they_sit(self):
        self.assertEqual(doctor.placeholders({"a": {"b": [{"c": "<x>"}]}}), ["<x>"])
        self.assertEqual(doctor.placeholders({"_comment": "<x>"}), [])

    def test_a_config_with_no_queries_searches_for_nothing(self):
        with Home() as h:
            h.write("vault/settings/search.json", {"queries": [], "location": {}})
            verdict, detail = doctor.check_radar_config()
            self.assertEqual(verdict, doctor.PLACEHOLDER)
            self.assertIn("nothing to search for", detail)


class OptionalIsNotMissing(unittest.TestCase):
    """Got wrong in four places in this repo already. An unconfigured thing has
    not been tried; reporting it broken sends people to fix what they never
    wanted, and reporting it fine claims coverage that does not exist."""

    def test_no_radar_config_is_optional(self):
        with Home():
            self.assertEqual(doctor.check_radar_config()[0], doctor.OPTIONAL)

    def test_no_watch_list_is_optional(self):
        with Home():
            self.assertEqual(doctor.check_employers()[0], doctor.OPTIONAL)

    def test_no_wiki_yet_is_the_next_step_not_a_fault(self):
        with Home():
            verdict, detail = doctor.check_wiki()
            self.assertEqual(verdict, doctor.OPTIONAL)
            self.assertIn("career-init", detail)

    def test_no_reviewer_names_the_free_way_round_it(self):
        """The oversight layer needs a second vendor's paid key. Most users will
        skip the review entirely unless told the dry-run path works as well."""
        with Home():
            verdict, detail = doctor.check_oversight()
            self.assertEqual(verdict, doctor.OPTIONAL)
            self.assertIn("--dry-run", detail)

    def test_but_a_broken_config_is_not_optional(self):
        with Home() as h:
            h.write("vault/settings/search.json", "{not json")
            self.assertEqual(doctor.check_radar_config()[0], doctor.MISSING)


class ThingsThatReallyAreMissing(unittest.TestCase):

    def test_no_cv_stops_career_init(self):
        with Home():
            verdict, detail = doctor.check_sources()
            self.assertEqual(verdict, doctor.MISSING)
            self.assertIn("career-init", detail)

    def test_a_readme_in_sources_is_not_a_cv(self):
        with Home() as h:
            h.write("vault/sources/README.md", "# put your CV here")
            self.assertEqual(doctor.check_sources()[0], doctor.MISSING)

    def test_a_provider_whose_key_is_not_in_the_shell(self):
        with Home() as h:
            h.write("vault/settings/review.json",
                    {"provider": "openai", "openai": {"api_key_env": "NOT_SET_ANYWHERE_XYZ"}})
            verdict, detail = doctor.check_oversight()
            self.assertEqual(verdict, doctor.MISSING)
            self.assertIn("NOT_SET_ANYWHERE_XYZ", detail)

    def test_a_copy_without_the_registry_is_incomplete(self):
        with Home() as h:
            os.remove(os.path.join(h.dir, "tools/radar/ats_registry.json"))
            verdict, detail = doctor.check_registry()
            self.assertEqual(verdict, doctor.MISSING)
            self.assertIn("re-clone", detail)


class TheReport(unittest.TestCase):

    def test_it_leads_with_what_needs_doing(self):
        with Home() as h:
            h.write("vault/settings/search.json", {"queries": ["<a title>"], "location": {}})
            code, out = h.run()
            self.assertLess(out.index("PLACEHOLDER"), out.index("OPTIONAL"))
            # Deliberately a pair where alphabetical order DISAGREES with
            # severity: "your CV" is missing and sorts last by name, "python" is
            # fine and sorts early. Sorted by name this assertion passes while
            # the report buries the only thing that needs doing.
            self.assertLess(out.index("your CV"), out.index("python"),
                            "the report is not leading with what needs attention")
            self.assertEqual(code, 1)

    def test_only_optional_findings_still_exit_zero(self):
        """Nothing here is wrong. Exiting 1 would make this unusable in a gate."""
        with Home() as h:
            h.write("vault/sources/CV.pdf", "x")
            code, out = h.run()
            self.assertEqual(code, 0, out)

    def test_a_check_that_raises_does_not_kill_the_report(self):
        with Home() as h:
            h.write("vault/sources/CV.pdf", "x")
            def boom():
                raise RuntimeError("x")
            saved = doctor.CHECKS
            doctor.CHECKS = [("boom", boom)] + list(saved)
            try:
                code, out = h.run()
            finally:
                doctor.CHECKS = saved
            self.assertIn("check raised RuntimeError", out)
            self.assertIn("python", out)

    def test_it_says_what_it_cannot_tell_you(self):
        """It reads files. Implying it proved a source answers would be the
        README line that started sources_check, said again."""
        with Home() as h:
            h.write("vault/sources/CV.pdf", "x")
            _, out = h.run()
            self.assertIn("no network calls", out)
            self.assertIn("sources_check.py", out)


class ItStaysOffline(unittest.TestCase):
    def test_it_imports_nothing_that_could_make_a_request(self):
        """Offline is a promise in the docstring, and a promise that can be
        checked should be checked. It is also what keeps it fast."""
        with open(DOC, encoding="utf-8") as fh:
            body = fh.read()
        for banned in ("urllib", "http.client", "requests", "socket"):
            self.assertNotIn(banned, body, f"doctor.py should not touch {banned}")


if __name__ == "__main__":
    unittest.main()
