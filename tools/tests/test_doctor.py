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
import importlib.util, io, json, os, shutil, subprocess, sys, tempfile, unittest
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
            h.write("vault/templates/sources-README.md", "# put your CV here")
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


class AMigratedWikiWithoutItsRecord(unittest.TestCase):
    """A migrated vault arrives with pages and no log and no index.

    The sorter files what it is handed, and somebody dropping their pages in
    does not include the catalogue -- or decides to start the log afresh and
    leaves the old one behind. Every operation in SCHEMA.md ends "update
    index.md, append to log.md", so without them the failure is silent: the
    record is simply not kept, and nobody notices for weeks.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        doctor.paths.use(os.path.join(self.tmp, "vault"))
        os.makedirs(doctor.paths.WIKI)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def page(self, name):
        with open(os.path.join(doctor.paths.WIKI, name), "w") as fh:
            fh.write("---\ntype: topic\n---\n")

    def test_pages_but_no_record_is_a_warning(self):
        self.page("CV.md")
        status, msg = doctor.check_wiki()
        self.assertEqual(status, doctor.WARN)
        self.assertIn("index.md", msg)
        self.assertIn("log.md", msg)

    def test_it_names_only_what_is_actually_missing(self):
        self.page("CV.md"); self.page("log.md")
        status, msg = doctor.check_wiki()
        self.assertEqual(status, doctor.WARN)
        self.assertIn("index.md", msg)
        self.assertNotIn("or log.md", msg)

    def test_an_empty_wiki_is_still_just_not_set_up_yet(self):
        """Before /career-init there is nothing to warn about, and warning then
        would train somebody to ignore the warning that matters."""
        self.assertEqual(doctor.check_wiki()[0], doctor.OPTIONAL)

    def test_a_complete_wiki_is_ok(self):
        for f in ("CV.md", "index.md", "log.md"):
            self.page(f)
        self.assertEqual(doctor.check_wiki()[0], doctor.OK)


class TheSignalCheck(unittest.TestCase):
    """🔴 The update gap, made checkable.

    The tiering vocabulary moved into the vault on 2026-08-26. An update can
    ship a system that needs a new vault file; it cannot put that file in
    somebody's vault. Without signal.json the radar still runs, still fetches,
    still writes a shortlist -- HIGH and MED are just always empty. Every role
    falls into the catch-all section, which reads as a quiet week rather than a
    broken install, and doctor reported the whole setup as fine.
    """

    GOOD = {"thresholds": {"high": 18, "med": 10},
            "positive": [{"match": "delivery", "weight": 6}],
            "negative": []}

    def test_nothing_is_wrong_when_nothing_searches_yet(self):
        """🔴 The cry-wolf case, and it fired for real. An install with no
        search.json has nothing to tier, so a missing vocabulary is not a fault
        there -- it is a step not yet reached."""
        with Home() as h:
            verdict, _ = doctor.check_signal()
            self.assertEqual(verdict, doctor.OPTIONAL)

    def test_a_missing_signal_file_is_reported(self):
        with Home() as h:
            h.write("vault/settings/search.json", {"queries": ["delivery"]})
            verdict, detail = doctor.check_signal()
            self.assertEqual(verdict, doctor.PLACEHOLDER)
            self.assertIn("quiet week", detail)

    def test_an_untouched_example_is_caught_too(self):
        """The placeholder case, which is the one that does not announce itself."""
        with Home() as h:
            h.write("vault/settings/search.json", {"queries": ["delivery"]})
            h.write("vault/settings/signal.json",
                    {"thresholds": {"high": 18, "med": 10},
                     "positive": [{"match": "<a technology central to your work>", "weight": 6}]})
            verdict, _ = doctor.check_signal()
            self.assertEqual(verdict, doctor.PLACEHOLDER)

    def test_a_real_signal_file_passes(self):
        """🔴 The false-positive case. A check that cries wolf gets switched off,
        so the working configuration is tested before the broken ones ship."""
        with Home() as h:
            h.write("vault/settings/search.json", {"queries": ["delivery"]})
            h.write("vault/settings/signal.json", self.GOOD)
            verdict, detail = doctor.check_signal()
            self.assertEqual(verdict, doctor.OK)
            self.assertIn("1 positive pattern", detail)

    def test_broken_json_says_so_rather_than_crashing(self):
        with Home() as h:
            h.write("vault/settings/search.json", {"queries": ["delivery"]})
            h.write("vault/settings/signal.json", "{not json")
            verdict, _ = doctor.check_signal()
            self.assertEqual(verdict, doctor.PLACEHOLDER)


class TheProfileCheck(unittest.TestCase):
    """🔴 A settings file nobody can discover is a default nobody chose.

    profile.json appeared in no documentation at all until 2026-08-27 -- not
    SCHEMA.md, not a skill, not doctor. Only paths.py and the one tool reading it
    knew it existed, so a fresh vault silently ran with CV spelling checks off
    and no way to annualise a contract day rate.
    """

    def test_a_missing_profile_is_reported_but_is_not_a_fault(self):
        """🟡 Most people never need it. Telling them they are broken every week
        is how a check gets ignored -- but saying nothing is how a guess stands
        in for a number only the user knows."""
        with Home() as h:
            verdict, detail = doctor.check_profile()
            self.assertEqual(verdict, doctor.OPTIONAL)
            self.assertIn("annualise", detail)

    def test_a_complete_profile_reports_both_values(self):
        with Home() as h:
            h.write("vault/settings/profile.json",
                    {"spelling": "ie-uk", "working_days_per_year": 220})
            verdict, detail = doctor.check_profile()
            self.assertEqual(verdict, doctor.OK)
            self.assertIn("220 working days", detail)
            self.assertIn("ie-uk", detail)

    def test_a_half_filled_profile_names_what_is_missing(self):
        """The likeliest real state: somebody set the spelling months ago and has
        never met a contract role."""
        with Home() as h:
            h.write("vault/settings/profile.json", {"spelling": "ie-uk"})
            verdict, detail = doctor.check_profile()
            self.assertEqual(verdict, doctor.OK)
            self.assertIn("Not set: working_days_per_year", detail)

    def test_an_implausible_day_count_is_not_accepted(self):
        """🔴 366 days is a year with no weekends. A number that cannot be right
        is worse than an absent one, because it will be used."""
        for bad in (0, 12, 366, 400, "many", None, True):
            with Home() as h:
                # spelling is set so the file is not WHOLLY placeholder -- this
                # test is about the day count alone, not the empty-file case.
                h.write("vault/settings/profile.json",
                        {"spelling": "ie-uk", "working_days_per_year": bad})
                _, detail = doctor.check_profile()
                self.assertIn("Not set:", detail, repr(bad))
                self.assertIn("working_days_per_year", detail.split("Not set:")[1], repr(bad))
                self.assertNotIn("working days", detail, repr(bad))

    def test_broken_json_says_so(self):
        with Home() as h:
            h.write("vault/settings/profile.json", "{not json")
            verdict, _ = doctor.check_profile()
            self.assertEqual(verdict, doctor.PLACEHOLDER)


class TheExamplesMustNeverLookConfigured(unittest.TestCase):
    """🔴 The whole point of this tool, generalised.

    Found by running career-init end to end on a fresh clone: a vault whose five
    settings files were copied straight from the examples and never edited got
    "OK — 1 watched, 1 avoided, 1 declined" from the watch/avoid check, on a list
    whose only entry is literally `<Employer name>`. And the profile check
    reported "220 working days" because the example shipped a REAL number rather
    than a placeholder — so a user who never edited it silently inherited another
    person's figure for the one value that has no safe default.

    `search.json` got this right and reported PLACEHOLDER. The rule was applied
    per-check, so each new settings file had to remember it independently. This
    is the version that cannot be forgotten.
    """

    EXAMPLES = os.path.join(ROOT, "templates", "settings")

    def _copied_vault(self, h):
        for f in os.listdir(self.EXAMPLES):
            if f.endswith(".example.json"):
                shutil.copy(os.path.join(self.EXAMPLES, f),
                            os.path.join(h.dir, "vault", "settings",
                                         f.replace(".example.json", ".json")))

    def test_no_check_reports_ok_on_an_untouched_example(self):
        with Home() as h:
            self._copied_vault(h)
            offenders = []
            for name, fn in doctor.CHECKS:
                # None of these read vault/settings, so a vault of untouched
                # examples tells us nothing about them. "other tools" reads
                # git state; the rest read the environment or the wiki.
                if name in ("python", "registry", "this copy", "your CV",
                            "your wiki", "other tools"):
                    continue
                try:
                    verdict, detail = fn()
                except Exception:
                    continue
                if verdict == doctor.OK:
                    offenders.append(f"{name}: {detail[:90]}")
            self.assertEqual(offenders, [],
                             "a settings file copied from its example and never edited must "
                             "never report OK — it looks configured and matches nothing")

    def test_no_example_ships_a_usable_value_for_a_personal_number(self):
        """🔴 An example may HINT at a number in its prose. It must not ship one
        as the value, or the hint becomes somebody else's answer by default."""
        with open(os.path.join(self.EXAMPLES, "profile.example.json"), encoding="utf-8") as fh:
            profile = json.load(fh)
        days = profile.get("working_days_per_year")
        self.assertFalse(isinstance(days, (int, float)) and not isinstance(days, bool),
                         "profile.example.json ships a real working_days_per_year, so a user "
                         "who never edits it inherits it silently")


class TheOracleEmployerName(unittest.TestCase):
    """🔴 A field documented as cosmetic that silently disables the exclusion list.

    `oracle.py` falls back to the site slug when `names` has no entry, so a row's
    company reads `CX_1001` rather than the employer. `employers.py` matches every
    avoid, avoid_sectors and watch rule against that field — so none of them can
    fire, and dedup can never recognise the same job arriving from LinkedIn under
    the employer's real name.

    🔴 `templates/settings/search.example.json` said `names` "only prettifies the
    site slug in the shortlist". That is why nobody set it, and why 1,308 rows in
    one vault carried a site code as their employer.
    """

    def _vault(self, oracle):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        saved = doctor.paths.VAULT
        self.addCleanup(doctor.paths.use, saved)
        os.makedirs(os.path.join(d, "settings"))
        with open(os.path.join(d, "settings", "search.json"), "w", encoding="utf-8") as fh:
            json.dump({"oracle": oracle}, fh)
        doctor.paths.use(d)
        return doctor.check_oracle_names()

    def test_a_site_with_no_name_is_reported(self):
        v, detail = self._vault({"employers": [{"host": "jpmc.fa.oraclecloud.com",
                                                "site": "CX_1001"}], "names": {}})
        self.assertEqual(v, doctor.MISSING)
        self.assertIn("CX_1001", detail)

    def test_a_named_site_passes(self):
        v, _ = self._vault({"employers": [{"host": "jpmc.fa.oraclecloud.com", "site": "CX_1001"}],
                            "names": {"CX_1001": "JPMorganChase"}})
        self.assertEqual(v, doctor.OK)

    def test_no_oracle_employers_is_OPTIONAL_not_a_fault(self):
        """🟡 Most installs never configure Oracle. Reporting that as a problem is
        how a check gets ignored."""
        v, _ = self._vault({"employers": [], "names": {}})
        self.assertEqual(v, doctor.OPTIONAL)

    def test_no_search_json_at_all_is_OPTIONAL(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        saved = doctor.paths.VAULT
        self.addCleanup(doctor.paths.use, saved)
        doctor.paths.use(d)
        self.assertEqual(doctor.check_oracle_names()[0], doctor.OPTIONAL)

    def test_the_example_no_longer_calls_names_cosmetic(self):
        """🔴 The comment IS the bug. A field described as cosmetic does not get set."""
        with open(os.path.join(ROOT, "templates", "settings",
                               "search.example.json"), encoding="utf-8") as fh:
            text = " ".join(json.load(fh)["oracle"]["_comment"])
        self.assertNotIn("only prettifies", text)
        self.assertIn("NOT cosmetic", text)


class TheUpdatableCheck(unittest.TestCase):
    """🔴 A backlog entry claimed a tuned SCHEMA.md was "silently clobbered by a
    pull". Tested on a throwaway clone rewound six commits, and it is not true —
    git aborts, loudly, and nothing is lost.

    🔴 The real failure is the opposite one and it IS quiet: the pull is step 1
    of `runbook.py update`, the four steps after it read the code already on
    disk, and every one of them passes. A user who does not read the git output
    concludes they are current when they are several versions behind.
    """

    def _repo(self, dirty):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        subprocess.run(["git", "init", "-q", d], check=True)
        for cmd in (["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", d] + cmd, check=True)
        with open(os.path.join(d, "SCHEMA.md"), "w", encoding="utf-8") as fh:
            fh.write("# schema\n")
        subprocess.run(["git", "-C", d, "add", "-A"], check=True)
        subprocess.run(["git", "-C", d, "commit", "-qm", "x"], check=True)
        if dirty:
            with open(os.path.join(d, "SCHEMA.md"), "a", encoding="utf-8") as fh:
                fh.write("\nnever call me a leader\n")
        saved = doctor.ROOT
        doctor.ROOT = d
        self.addCleanup(setattr, doctor, "ROOT", saved)
        return doctor.check_updatable()

    def test_a_clean_clone_says_a_pull_would_apply(self):
        self.assertEqual(self._repo(dirty=False)[0], doctor.OK)

    def test_a_locally_tuned_tracked_file_is_reported_before_the_pull(self):
        v, detail = self._repo(dirty=True)
        self.assertEqual(v, doctor.WARN)
        self.assertIn("SCHEMA.md", detail)
        self.assertIn("ABORT", detail)

    def test_an_untracked_file_does_not_block_and_is_not_reported(self):
        """🟡 The false-positive direction. Untracked files never block a merge,
        and reporting them would fire on every working session."""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        subprocess.run(["git", "init", "-q", d], check=True)
        for cmd in (["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", d] + cmd, check=True)
        with open(os.path.join(d, "a.md"), "w", encoding="utf-8") as fh:
            fh.write("x\n")
        subprocess.run(["git", "-C", d, "add", "-A"], check=True)
        subprocess.run(["git", "-C", d, "commit", "-qm", "x"], check=True)
        with open(os.path.join(d, "scratch.txt"), "w", encoding="utf-8") as fh:
            fh.write("working file\n")
        saved = doctor.ROOT
        doctor.ROOT = d
        self.addCleanup(setattr, doctor, "ROOT", saved)
        self.assertEqual(doctor.check_updatable()[0], doctor.OK)

    def test_a_zip_download_is_OPTIONAL_not_a_fault(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        saved = doctor.ROOT
        doctor.ROOT = d
        self.addCleanup(setattr, doctor, "ROOT", saved)
        self.assertEqual(doctor.check_updatable()[0], doctor.OPTIONAL)


class TheCompanyResearchExpiry(unittest.TestCase):
    """🔴 A company page is written once and REUSED, which makes it the artefact
    that rots invisibly. Financial results age in months; a page saying "revenue
    down 4%, no redundancies announced" is a liability six months later and
    nothing about it looks stale.

    🔴 `/career-lint` reports an EXPIRED page. It cannot report one that never
    claimed an expiry — so an undated research page is permanently fresh and
    permanently wrong. Five of seven had no `stale_after` when this was written,
    and the skill that creates them never asked for one.
    """

    def _vault(self, pages):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        saved = doctor.paths.VAULT
        self.addCleanup(doctor.paths.use, saved)
        os.makedirs(os.path.join(d, "companies"))
        for name, body in pages.items():
            with open(os.path.join(d, "companies", f"{name}.md"), "w", encoding="utf-8") as fh:
                fh.write(body)
        doctor.paths.use(d)
        return doctor.check_company_research()

    RESEARCH = ("---\ntype: entity\ntags: [career, company-research, due-diligence]\n"
                "stale_after: 2099-01-01\nstatus: active\n---\n\n# Acme\n")

    def test_a_dated_research_page_passes(self):
        self.assertEqual(self._vault({"Acme - Company Research": self.RESEARCH})[0], doctor.OK)

    def test_an_undated_research_page_is_caught(self):
        body = self.RESEARCH.replace("stale_after: 2099-01-01\n", "")
        v, detail = self._vault({"Acme - Company Research": body})
        self.assertEqual(v, doctor.MISSING)
        self.assertIn("Acme", detail)

    def test_an_expired_page_is_reported_but_not_as_missing(self):
        """🟡 Expired is a different state from never-dated: one is research that
        needs refreshing, the other is research nothing can ever chase."""
        body = self.RESEARCH.replace("2099-01-01", "2020-01-01")
        self.assertEqual(self._vault({"Acme - Company Research": body})[0], doctor.WARN)

    def test_the_users_own_employers_are_not_research_pages(self):
        """🔴 THE FALSE-POSITIVE CASE. `vault/companies/` also holds where the
        user WORKED — biography, not a dated claim about a market. Four of the
        seven pages are that, and demanding an expiry on them would be asking
        somebody to date their own career."""
        own = ("---\ntype: entity\ntags: [career, employer, acme]\nstatus: active\n---\n\n# Acme\n")
        self.assertEqual(self._vault({"Acme": own})[0], doctor.OPTIONAL)

    def test_a_vault_with_no_companies_folder_is_not_a_fault(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        saved = doctor.paths.VAULT
        self.addCleanup(doctor.paths.use, saved)
        doctor.paths.use(d)
        self.assertEqual(doctor.check_company_research()[0], doctor.OPTIONAL)
