"""radar: the window that hid 51 open roles, and the column that read as a score.

Both cases here are ones that actually happened.

The radar defaulted to a seven-day posting window with no way to ask for
everything currently open, so still-open roles posted earlier were never looked
at. The highest-scoring unapplied role in one user's table had been posted
fourteen days before the run; the radar never saw it and the user found it by
hand. Fifty-one roles above the read-threshold appeared the first time the
filter came off.

And the shortlist printed the raw keyword tally under a column headed "Score".
A radar output of 21 was reported to a user as though it were a framework score
of 21 -- impossible, since that scale stops at 15. A warning was added to the
output and the confusion recurred anyway, which is why the column is now a word:
HIGH cannot be mistaken for a score out of 15 even by accident.
"""
import contextlib, importlib.util, io, json, os, re, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RADAR_DIR = os.path.join(ROOT, "tools", "radar")

sys.path.insert(0, RADAR_DIR)
spec = importlib.util.spec_from_file_location("radar", os.path.join(RADAR_DIR, "radar.py"))
radar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)

from adapters import adzuna, greenhouse, lever, linkedin      # noqa: E402


class FakeAdapter:
    """Stands in for a module: fetch(), TRUNCATED, HONOURS_DAYS."""

    def __init__(self, rows, truncated=False, honours_days=True, bodies=False):
        self.rows, self.TRUNCATED, self.calls = rows, truncated, []
        self.HONOURS_DAYS = honours_days
        self.bodies = []
        if bodies:
            self.fetch_body = self._body

    def _body(self, row):
        self.bodies.append(row["id"])
        return "regulated bank portfolio roadmap mentor stakeholder adoption"

    def fetch(self, cfg, query, days):
        self.calls.append(days)
        return [dict(r) for r in self.rows]


def posting(**kw):
    r = {"id": "x1", "title": "Head of Delivery", "company": "Acme", "loc": "<city>",
         "date": "2026-08-01", "url": "http://e.g/1", "body": "", "pay": "",
         "source": "fake"}
    r.update(kw)
    return r


class Run:
    """Run radar.main() against a temp dir with a stubbed adapter."""

    def __init__(self, argv, adapters, config=None, employers=None):
        self.argv, self.adapters, self.employers = argv, adapters, employers or {}
        self.config = config or {"queries": ["delivery"], "location": {}}

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        self._saved = {k: getattr(radar, k) for k in ("CONFIG", "RAW", "SEEN", "OUT", "ADAPTERS")}
        self._argv = sys.argv
        radar.CONFIG = os.path.join(self.dir, "config.json")
        radar.RAW = os.path.join(self.dir, "raw.json")
        radar.SEEN = os.path.join(self.dir, "seen.json")
        radar.OUT = os.path.join(self.dir, "shortlist.md")
        radar.ADAPTERS = self.adapters
        self._load = radar.EMP.load
        radar.EMP.load = lambda *a, **k: self.employers
        with open(radar.CONFIG, "w") as fh:
            json.dump(self.config, fh)
        sys.argv = ["radar.py"] + self.argv
        with contextlib.redirect_stderr(io.StringIO()) as err:
            radar.main()
        self.err = err.getvalue()
        with open(radar.OUT) as fh:
            self.out = fh.read()
        return self

    def __exit__(self, *a):
        sys.argv = self._argv
        radar.EMP.load = self._load
        for k, v in self._saved.items():
            setattr(radar, k, v)
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)


# --------------------------------------------------------------------------
# The window
# --------------------------------------------------------------------------

class TheWindow(unittest.TestCase):

    def test_default_is_still_a_seven_day_window(self):
        """Frequent windowed runs stay the default: dense coverage of a week."""
        fake = FakeAdapter([posting()])
        with Run([], {"fake": fake}) as r:
            self.assertEqual(fake.calls, [7])
            self.assertIn("7-day window", r.out)

    def test_all_open_asks_the_adapter_for_everything(self):
        """The fix for the defect: None means no recency filter at all.

        Not a big number -- None. A large --days asks the source a different
        question and gets a differently-wrong answer.
        """
        fake = FakeAdapter([posting()])
        with Run(["--all-open"], {"fake": fake}) as r:
            self.assertEqual(fake.calls, [None])
            self.assertIn("all open postings", r.out)

    def test_all_open_beats_days_when_both_are_given(self):
        fake = FakeAdapter([posting()])
        with Run(["--days", "30", "--all-open"], {"fake": fake}):
            self.assertEqual(fake.calls, [None])

    def test_all_open_says_it_is_a_backlog_not_a_shortlist(self):
        """An unfiltered sweep surfaces dozens at once.

        The assess-every-role-immediately rule does not survive a fifty-one item
        catch-up, so the output has to say which kind of run this was.
        """
        fake = FakeAdapter([posting()])
        with Run(["--all-open"], {"fake": fake}) as r:
            self.assertIn("backlog sweep", r.out)
        with Run([], {"fake": FakeAdapter([posting()])}) as r:
            self.assertNotIn("backlog sweep", r.out)

    def test_a_window_of_zero_is_not_a_request_for_everything(self):
        """`if days:` made 0 falsy, so --days 0 silently became an unfiltered sweep.

        None is the sentinel and only None. 0 is a window, or a user error --
        either way it is not a request for every open role, and answering a
        question nobody asked is the exact failure the None handling exists to
        prevent. Reintroduced once by the shorter spelling of the guard.
        """
        seen = []
        linkedin.get = lambda url, headers=None: seen.append(url) or ""
        linkedin.fetch({"linkedin": {"enabled": True, "pages": 1, "delay": 0}}, "q", 0)
        self.assertIn("f_TPR", seen[0])

        seen.clear()
        adzuna.get_json = lambda url, headers=None: seen.append(url) or {"results": []}
        adzuna.fetch({"adzuna": {"app_id": "a", "app_key": "b", "pages": 1}}, "q", 0)
        self.assertIn("max_days_old=0", seen[0])

    def test_the_runner_passes_zero_through_rather_than_reinterpreting_it(self):
        fake = FakeAdapter([posting()])
        with Run(["--days", "0"], {"fake": fake}):
            self.assertEqual(fake.calls, [0])

    def test_linkedin_omits_the_recency_parameter_when_days_is_none(self):
        seen = []
        linkedin.get = lambda url, headers=None: seen.append(url) or ""
        cfg = {"linkedin": {"enabled": True, "pages": 1, "delay": 0}}
        linkedin.fetch(cfg, "delivery", None)
        self.assertNotIn("f_TPR", seen[0])
        seen.clear()
        linkedin.fetch(cfg, "delivery", 7)
        self.assertIn("f_TPR=r604800", seen[0])

    def test_adzuna_omits_max_days_old_when_days_is_none(self):
        seen = []
        adzuna.get_json = lambda url, headers=None: seen.append(url) or {"results": []}
        cfg = {"adzuna": {"app_id": "a", "app_key": "b", "pages": 1}}
        adzuna.fetch(cfg, "delivery", None)
        self.assertNotIn("max_days_old", seen[0])
        seen.clear()
        adzuna.fetch(cfg, "delivery", 7)
        self.assertIn("max_days_old=7", seen[0])

    def test_board_adapters_ignore_days_entirely(self):
        """A board returns everything open, so the defect never applied to them."""
        payload = [{"id": 1, "title": "Delivery Lead", "content": "x",
                    "location": {"name": "<city>"}, "updated_at": "2026-08-01",
                    "absolute_url": "u"}]
        greenhouse.get_json = lambda url, headers=None: {"jobs": payload}
        self.assertEqual(len(greenhouse.fetch({"greenhouse": {"boards": ["t"]}}, "delivery", 7)),
                         len(greenhouse.fetch({"greenhouse": {"boards": ["t"]}}, "delivery", None)))
        self.assertFalse(greenhouse.TRUNCATED)
        self.assertFalse(lever.TRUNCATED)


class TheHeader(unittest.TestCase):
    """A shortlist headed "7-day window" that contains board rows is lying.

    Board adapters return everything currently open at any age, so a file mixing
    them with a windowed search can carry six-month-old postings under a header
    claiming a week. The header is the only thing telling a reader how old these
    can be.
    """

    def test_a_windowed_search_alone_still_claims_the_window(self):
        with Run([], {"fake": FakeAdapter([posting()])}) as r:
            self.assertIn("(7-day window)", r.out)
            self.assertNotIn("does not apply to every source", r.out)

    def test_board_rows_qualify_the_header_and_name_the_boards(self):
        board = FakeAdapter([posting(id="b", source="board")], honours_days=False)
        search = FakeAdapter([posting(id="s", title="Head of Delivery Ops", source="search")])
        with Run([], {"search": search, "board": board}) as r:
            self.assertIn("7-day window on searched sources", r.out)
            self.assertIn("does not apply to every source", r.out)
            self.assertIn("board", r.out)

    def test_boards_alone_do_not_claim_a_window_at_all(self):
        """--adapter greenhouse --days 7 applied the window to nothing."""
        board = FakeAdapter([posting(source="board")], honours_days=False)
        with Run([], {"board": board}) as r:
            self.assertIn("applied to nothing", r.out)
            self.assertNotIn("(7-day window)", r.out)

    def test_all_open_needs_no_qualifier_because_nothing_claims_a_window(self):
        board = FakeAdapter([posting(source="board")], honours_days=False)
        with Run(["--all-open"], {"board": board}) as r:
            self.assertIn("all open postings", r.out)
            self.assertNotIn("does not apply to every source", r.out)

    def test_an_adapter_that_forgets_to_declare_is_treated_as_a_board(self):
        """Over-warning costs a line; under-warning ages a posting by months."""
        class Undeclared(FakeAdapter):
            pass
        mute = Undeclared([posting(source="mute")])
        del mute.HONOURS_DAYS
        with Run([], {"mute": mute}) as r:
            self.assertIn("applied to nothing", r.out)


class TheAvoidList(unittest.TestCase):
    """Exclusions filter BEFORE scoring, which is the whole point of them.

    Without that, the rule that every role found gets assessed in the same turn
    spends effort on a question settled months ago.
    """

    def test_an_avoided_employer_never_costs_a_description_fetch(self):
        """The ordering IS the feature, so it is pinned rather than assumed."""
        fake = FakeAdapter([posting(id="a", company="<Employer A>"),
                            posting(id="b", company="<Employer B>",
                                    title="Head of Delivery Ops")], bodies=True)
        with Run([], {"fake": fake},
                 employers={"avoid": [{"employer": "<Employer A>"}]}) as r:
            self.assertEqual(fake.bodies, ["b"])          # a was never fetched
            self.assertIn("1 on the avoid list", r.out)

    def test_it_says_what_it_skipped_and_why(self):
        """A silent exclusion is indistinguishable from a source finding nothing."""
        fake = FakeAdapter([posting(company="<Employer A>")])
        with Run([], {"fake": fake},
                 employers={"avoid": [{"employer": "<Employer A>"}]}) as r:
            self.assertIn("Skipped — already decided", r.out)
            self.assertIn("<Employer A>", r.out)

    def test_a_sector_is_judged_after_the_description_arrives(self):
        """A category catches employers never heard of, so a name is not enough."""
        fake = FakeAdapter([posting(id="a", company="<Employer Z>")], bodies=True)
        with Run([], {"fake": fake},
                 employers={"avoid_sectors": [{"sector": "<sector>",
                                               "match": ["regulated"]}]}) as r:
            self.assertEqual(fake.bodies, ["a"])          # fetched, THEN judged
            self.assertIn("1 on the avoid list", r.out)
            self.assertIn("<sector>", r.out)

    def test_a_declined_employer_is_marked_not_dropped(self):
        """A role turned down on a commute can legitimately come back."""
        body = "regulated bank portfolio roadmap adoption upskill mentor stakeholder"
        fake = FakeAdapter([posting(company="<Employer A>", body=body)])
        with Run([], {"fake": fake},
                 employers={"declined": [{"employer": "<Employer A>", "reason": "commute",
                                          "on": "2026-01-04"}]}) as r:
            self.assertIn("<Employer A> †", r.out)
            self.assertIn("declined 2026-01-04: commute", r.out)
            self.assertNotIn("on the avoid list", r.out)

    def test_a_watch_entry_with_no_route_is_reported_as_not_watched(self):
        fake = FakeAdapter([posting()])
        with Run([], {"fake": fake},
                 employers={"watch": [{"employer": "<Employer A>"}]}) as r:
            self.assertIn("no route", r.out)
            self.assertIn("<Employer A>", r.out)

    def test_an_employer_on_both_lists_is_flagged_rather_than_resolved(self):
        """Whichever list won would be an accident of ordering."""
        fake = FakeAdapter([posting()])
        with Run([], {"fake": fake},
                 employers={"watch": [{"employer": "<Employer A>", "query": "x"}],
                            "avoid": [{"employer": "<Employer A>"}]}) as r:
            self.assertIn("watch list AND the avoid list", r.out)

    def test_no_employers_file_changes_nothing(self):
        fake = FakeAdapter([posting()])
        with Run([], {"fake": fake}) as r:
            self.assertNotIn("avoid list", r.out)
            self.assertNotIn("Skipped", r.out)


# --------------------------------------------------------------------------
# The cap
# --------------------------------------------------------------------------

class TheCap(unittest.TestCase):
    """Where a source caps results, the cap is the real constraint.

    A run reporting a round number is usually reporting the cap rather than the
    match count, and presenting that as the complete set of open roles is the
    same silent-truncation failure as the seven-day window.
    """

    def test_exhausting_the_page_budget_is_truncation(self):
        page = '<li><a href="https://xx.linkedin.com/jobs/view/a-123"></a>' \
               '<h3 class="base-search-card__title">Head of Delivery</h3>'
        linkedin.get = lambda url, headers=None: page
        linkedin.fetch({"linkedin": {"enabled": True, "pages": 2, "delay": 0}}, "q", 7)
        self.assertTrue(linkedin.TRUNCATED)

    def test_an_empty_page_proves_the_set_is_complete(self):
        linkedin.get = lambda url, headers=None: "<html></html>"
        linkedin.fetch({"linkedin": {"enabled": True, "pages": 2, "delay": 0}}, "q", 7)
        self.assertFalse(linkedin.TRUNCATED)

    def test_a_failed_page_counts_as_truncation_not_completeness(self):
        """A page that failed is unknown, and unknown is reported, not assumed empty."""
        linkedin.get = lambda url, headers=None: None
        linkedin.fetch({"linkedin": {"enabled": True, "pages": 2, "delay": 0}}, "q", 7)
        self.assertTrue(linkedin.TRUNCATED)

    def test_adzuna_distinguishes_a_dry_source_from_a_failed_request(self):
        adzuna.get_json = lambda url, headers=None: {"results": []}
        adzuna.fetch({"adzuna": {"app_id": "a", "app_key": "b", "pages": 2}}, "q", 7)
        self.assertFalse(adzuna.TRUNCATED)
        adzuna.get_json = lambda url, headers=None: None
        adzuna.fetch({"adzuna": {"app_id": "a", "app_key": "b", "pages": 2}}, "q", 7)
        self.assertTrue(adzuna.TRUNCATED)

    def test_the_shortlist_says_when_it_is_not_the_whole_picture(self):
        fake = FakeAdapter([posting()], truncated=True)
        with Run([], {"fake": fake}) as r:
            self.assertIn("NOT THE COMPLETE SET", r.out)
            self.assertIn("NOT the complete set", r.err)   # and on the console
        with Run([], {"fake": FakeAdapter([posting()])}) as r:
            self.assertNotIn("NOT THE COMPLETE SET", r.out)


# --------------------------------------------------------------------------
# The column
# --------------------------------------------------------------------------

class TheSignal(unittest.TestCase):

    def test_signal_is_a_word_at_every_boundary(self):
        self.assertEqual(radar.signal(radar.HIGH_AT), "HIGH")
        self.assertEqual(radar.signal(radar.HIGH_AT - 1), "MED")
        self.assertEqual(radar.signal(radar.MED_AT), "MED")
        self.assertEqual(radar.signal(radar.MED_AT - 1), "LOW")
        self.assertEqual(radar.signal(-30), "LOW")
        self.assertEqual(radar.signal(999), "HIGH")

    def test_the_shortlist_never_prints_a_bare_number_as_a_verdict(self):
        """The regression test for the actual incident.

        A tally of 21 printed under a column headed "Score" was read as a
        framework score of 21. Nothing a human reads may carry the tally.
        """
        rows = [posting(id="a", title="Head of AI Delivery",
                        body="generative ai agentic llm ai governance guardrail "
                             "regulated bank legacy modernisation sdlc"),
                posting(id="b", title="Delivery Manager", body="stakeholder mentor adoption")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            self.assertNotIn("| Score |", r.out)
            self.assertNotRegex(r.out, r"(?i)\|\s*score\s*\|")
            self.assertIn("| SIGNAL |", r.out)
            for line in r.out.splitlines():
                if line.startswith("| ") and not line.startswith("| SIGNAL"):
                    first = line.split("|")[1].strip()
                    self.assertFalse(re.fullmatch(r"-?\d+", first),
                                     f"a bare number is back in the verdict column: {line}")

    def test_high_and_med_both_appear_and_med_is_never_dropped(self):
        """Good roles land in MED, so MED is always written out.

        A title-thin posting signals low regardless of how good the role is,
        which is why the lower band is printed rather than filtered away.
        """
        rows = [posting(id="a", title="Head of AI Delivery",
                        body="generative ai agentic llm ai governance guardrail "
                             "regulated bank legacy modernisation sdlc release "
                             "management mentor stakeholder"),
                posting(id="b", title="Delivery Manager",
                        body="stakeholder mentor adoption upskill portfolio roadmap "
                             "regulated insurance")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            self.assertIn("## HIGH signal", r.out)
            self.assertIn("## MED signal", r.out)
            self.assertIn("| HIGH |", r.out)
            self.assertIn("| MED |", r.out)

    def test_the_tally_survives_in_the_cache_for_tuning(self):
        """raw.json is disposable and machine-read, so the number is fine there."""
        with Run([], {"fake": FakeAdapter([posting()])}) as r:
            cached = json.load(open(radar.RAW))
            row = list(cached.values())[0]
            self.assertIsInstance(row["tally"], int)
            self.assertEqual(row["signal"], radar.signal(row["tally"]))

    def test_a_floor_date_is_marked_so_an_old_role_cannot_look_fresh(self):
        """Some sources only say "30+ days ago", which is a floor, not a date.

        A six-week-old senior requisition may already be at offer stage, so the
        posting date is read as a prioritisation input. Printing a floor bare
        makes an ageing role look fresh -- the same harm as an aggregator
        re-dating a repost, arrived at from the other direction.
        """
        body = "regulated bank portfolio roadmap adoption upskill mentor stakeholder"
        rows = [posting(id="a", date="2026-07-26", date_is_floor=True, body=body),
                posting(id="b", title="Delivery Lead", date="2026-08-20", body=body)]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            self.assertIn("| 2026-07-26+ |", r.out)
            self.assertIn("| 2026-08-20 |", r.out)
            self.assertNotIn("| 2026-08-20+ |", r.out)

    def test_the_output_still_disclaims_what_signal_is(self):
        with Run([], {"fake": FakeAdapter([posting()])}) as r:
            self.assertIn("not an assessment", r.out)
            self.assertIn("Read MED too", r.out)


if __name__ == "__main__":
    unittest.main()
