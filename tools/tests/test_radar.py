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
import contextlib, datetime, pathlib, importlib.util, io, json, os, re, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RADAR_DIR = os.path.join(ROOT, "tools", "radar")
RADAR = os.path.join(RADAR_DIR, "radar.py")

sys.path.insert(0, RADAR_DIR)
spec = importlib.util.spec_from_file_location("radar", os.path.join(RADAR_DIR, "radar.py"))
radar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)

from adapters import adzuna, greenhouse, lever, linkedin      # noqa: E402
from adapters import _titles                                  # noqa: E402


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


# 🔴 THE SUITE MUST NOT READ THE USER'S VAULT.
#
# When the tiering vocabulary moved to vault/settings/signal.json on 2026-08-26,
# radar's POS/NEG/HIGH_AT/MED_AT became module constants loaded AT IMPORT from
# whatever vault happened to be present. On the author's machine that file exists
# and the suite passed. On a fresh clone -- or any vault without it -- five tests
# failed, because nothing could ever score HIGH.
#
# Found by simulating exactly that: clone, rewind, populate a vault, git pull.
# A test that reads the user's configuration is not testing the code.
TEST_SIGNAL = {
    # Tuned to the fixtures below, and the fixtures are the specification:
    # a bare "Head of Delivery" must NOT tier (that is the pay-promotion test),
    # a role with governance/AI vocabulary must reach HIGH, and a people-and-
    # portfolio role must land in MED and stay there.
    "thresholds": {"high": 20, "med": 12},
    "positive": [
        {"match": "generative ai", "weight": 6}, {"match": "agentic", "weight": 6},
        {"match": "llm", "weight": 6}, {"match": "ai governance", "weight": 6},
        {"match": "guardrail", "weight": 6}, {"match": "legacy modernisation", "weight": 6},
        {"match": "sdlc", "weight": 4}, {"match": "release management", "weight": 4},
        {"match": "portfolio", "weight": 2}, {"match": "roadmap", "weight": 2},
        {"match": "stakeholder", "weight": 2}, {"match": "mentor", "weight": 2},
        {"match": "adoption", "weight": 2}, {"match": "upskill", "weight": 2},
        {"match": "regulated", "weight": 2},
    ],
    "negative": [{"match": "warehouse", "weight": -6}, {"match": "forklift", "weight": -6}],
    "exclude_titles": {"words": ["mechanical", "nurse"]},
    "individual_contributor_titles": {
        "seniority": ["senior", "staff", "principal", "lead", "junior", "graduate"],
        "domains": ["software", "data", "cloud", "platform"],
        "nouns": ["developer", "engineer", "scientist", "analyst", "architect", "intern"]},
}

# Installed at IMPORT, not per-Run, because several tests read radar.HIGH_AT and
# call radar.tally_of() directly. Those are the ones that failed on a clone.
(radar.POS, radar.NEG, radar.NEVER, radar.IC_TITLE,
 radar.HIGH_AT, radar.MED_AT) = radar.build_signal(TEST_SIGNAL)


class Run:
    """Run radar.main() against a temp dir with a stubbed adapter."""

    def __init__(self, argv, adapters, config=None, employers=None, signal=None):
        self.argv, self.adapters, self.employers = argv, adapters, employers or {}
        self.config = config or {"queries": ["delivery"], "location": {}}
        self.signal = TEST_SIGNAL if signal is None else signal

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        self._saved = {k: getattr(radar, k) for k in
                       ("CONFIG", "RAW", "SEEN", "OUT", "ADAPTERS",
                        "POS", "NEG", "NEVER", "IC_TITLE", "HIGH_AT", "MED_AT")}
        (radar.POS, radar.NEG, radar.NEVER, radar.IC_TITLE,
         radar.HIGH_AT, radar.MED_AT) = radar.build_signal(self.signal)
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


class TheDayRate(unittest.TestCase):
    """🔴 A day rate read as a salary is a role thrown away.

    Sacha asked on 2026-08-26 to be shown high-FIT contract roles even at SEC 1
    or 2, because the rate can make the trade worth it. That makes the RATE the
    deciding number -- and the pay regex could not see one.

    `(€|£|$)\s?\d[\d,.]*\s?k?` searching the title alone turns
    "€400-650/day" into "€400". Against a €130k floor that reads as
    catastrophic, when it is in fact roughly €150k gross before the pension,
    leave and continuity gap. The one number that decides a contract was being
    rendered as its own opposite.
    """

    def test_a_day_rate_keeps_its_unit(self):
        for text, want in (
            ("AI Delivery Lead - Finance €400-650/day", "€400-650/day"),
            ("Delivery Lead (€550 per day)", "€550 per day"),
            ("Contract PM £700/day", "£700/day"),
            ("Programme Manager - 650 p/d", "650 p/d"),
        ):
            self.assertEqual(radar.pay_in(text), want, text)

    def test_an_annual_salary_is_not_labelled_a_rate(self):
        """🔴 The false-positive case, tested before the feature ships.

        Mislabelling €149k as a day rate would be the same error in the other
        direction, and there are far more salaries than rates in the corpus.
        """
        for text in ("Head of AI - 120k", "TPM €149,800 - €224,800", "Director $180k"):
            got = radar.pay_in(text)
            self.assertTrue(got, text)
            self.assertNotIn("day", got.lower())
            self.assertNotIn("p/d", got.lower())

    def test_a_lunch_allowance_is_not_a_day_rate(self):
        """🔴 THE CRY-WOLF CASE, and it fired on the first real run.

        Searching the body for a rate found this, in a Sprout Social advert for a
        Senior Applied AI/ML Scientist:

            "Dublin Office Perks: A €18 daily lunch stipend (via Deliveroo)"

        and rendered the role's Pay as "€18 daily". Benefits sections are full of
        per-day numbers -- lunch, travel, internet -- and every one of them sits
        beside the word "daily" or "per day".

        Two guards, because either alone leaks: a magnitude floor, since no
        director-level contract in this market pays under €150 a day, and an
        allowance-word veto for the ones that clear it.
        """
        for text in ("A €18 daily lunch stipend (via Deliveroo)",
                     "€25 per day meal allowance",
                     "a €200 per day travel expenses cap",
                     "€12 a day for lunch"):
            self.assertEqual(radar.pay_in(text), "", text)

    def test_a_real_rate_still_survives_both_guards(self):
        """The other half of the same test: guards that block the real thing are
        worse than no guards, because a contract without its rate is unscoreable."""
        for text, want in (("€400-650/day", "€400-650/day"),
                           ("£700/day", "£700/day"),
                           ("650 p/d", "650 p/d"),
                           ("€550 per day", "€550 per day")):
            self.assertEqual(radar.pay_in(text), want, text)

    def test_the_body_is_searched_when_the_title_says_nothing(self):
        """Rates live in the advert far more often than in the title, and a
        contract without its rate is not assessable at all."""
        rows = [posting(title="AI Delivery Lead", pay="",
                        body="12 month contract, €400-650/day depending on experience. "
                             "delivery portfolio roadmap stakeholder mentor adoption upskill")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            self.assertIn("€400-650/day", r.out)

    def test_company_money_in_the_body_is_never_read_as_pay(self):
        """🔴 The second thing shipping the body search broke.

        Adverts are full of money that is not the salary. Real matches from one
        run: "$1.1 trillion in assets under management" became a pay of "$1.1",
        and "grown products from $0 to $200M in revenue" became "$0".

        So the body is searched for a RATE only. A salary still comes from the
        title, where a number next to a job title is the job's number. There is
        no equivalent guarantee anywhere in the body prose.
        """
        rows = [posting(title="Head of Delivery", pay="",
                        body="Our $1.1 trillion in assets under management. We grew from $0 to "
                             "$200M in revenue. delivery portfolio roadmap stakeholder mentor "
                             "adoption upskill")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            self.assertNotIn("$1.1", r.out)
            self.assertNotIn("| $0 |", r.out)

    def test_a_rate_in_the_body_never_overrides_one_the_source_gave(self):
        rows = [posting(title="AI Delivery Lead", pay="€700/day",
                        body="was previously €300/day. delivery portfolio roadmap stakeholder "
                             "mentor adoption upskill")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            self.assertIn("€700/day", r.out)
            self.assertNotIn("€300/day", r.out)


class TheTableSurvivesItsOwnContent(unittest.TestCase):
    """🔴 A pipe in a job title silently breaks the row it is in.

    Found 2026-08-26 while counting how many roles were left to score. 43 rows
    of one sweep carried a `|` in the title or the company:

        | Barden | B Corp | Privacy & AI Counsel | ...
        | Archer Recruitment | Engineering Manager - .NET / C# | Build & Lead...

    Markdown reads that pipe as a column break, so the row renders with its
    columns shifted: the title lands under Company and the link ends up in the
    wrong cell entirely. 🔴 The row still looks like a row, which is why it
    lasted -- the same failure had just been found by hand in the scoring table.

    Recruiters and job boards put pipes in titles routinely. This is not an
    exotic input.
    """

    def test_a_pipe_in_a_title_does_not_add_a_column(self):
        rows = [posting(title="Engineering Manager | Build & Lead a New Team",
                        company="Barden | B Corp", loc="Dublin | Hybrid",
                        body="delivery portfolio roadmap stakeholder mentor adoption upskill")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            for line in r.out.splitlines():
                if line.startswith("| ") and "---" not in line and "SIGNAL" not in line \
                        and not line.startswith("| Company"):
                    cells = re.split(r"(?<!\\)\|", line)
                    self.assertIn(len(cells) - 2, (5, 7),
                                  f"a pipe in the content added a column: {line!r}")

    def test_the_title_is_still_readable_after_escaping(self):
        """Escaping must not eat the text -- the point is to keep it."""
        rows = [posting(title="Engineering Manager | Build a Team",
                        body="delivery portfolio roadmap stakeholder mentor adoption upskill")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            self.assertIn("Engineering Manager", r.out)
            self.assertIn("Build a Team", r.out)

    def test_a_newline_in_a_field_cannot_split_a_row(self):
        """The other way one row becomes two."""
        rows = [posting(company="Acme\nCorp", title="Head of Delivery",
                        body="delivery portfolio roadmap stakeholder mentor adoption upskill")]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            body = r.out.split("## HIGH signal")[1]
            for line in body.splitlines():
                self.assertFalse(line.strip() and not line.startswith(("|", "#", ">", "-")),
                                 f"a newline split a row: {line!r}")


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


class RemoteIsCountryScoped(unittest.TestCase):
    """"Remote" almost always means remote WITHIN somewhere, and the suffix is
    the whole meaning. Read as "anywhere", a search widens into roles the
    applicant cannot legally take -- right to work, tax residency and payroll
    entity all sit behind that word and none appear in a listing.
    """

    CFG = {"location": {"ok": ["<home>", "remote"], "bad": ["<far>"], "edge": ["<maybe>"]}}

    def test_the_scope_is_parsed_off_every_common_phrasing(self):
        for text, scope in [("Remote - <far>", "<far>"), ("Remote, <far>", "<far>"),
                            ("<home> (Remote)", "<home>"), ("Fully Remote - <far>", "<far>"),
                            ("Remote", ""), ("100% Remote", "")]:
            is_remote, got = radar.parse_location(text)
            self.assertTrue(is_remote, text)
            self.assertEqual(got, scope, text)

    def test_a_plain_location_is_not_remote(self):
        self.assertEqual(radar.parse_location("<home>"), (False, "<home>"))

    def test_the_ok_list_is_matched_case_insensitively(self):
        """THE FALSE-POSITIVE CASE, and it silenced a whole run.

        The haystack was lowercased and the needle was not, so a capitalised
        entry matched nothing. templates/settings/search.example.json both
        promises "matched case-insensitively" and ships placeholders -- <your
        city>, <your country> -- which anybody fills in capitalised, because
        that is how places are spelled. One real run fetched 4,815 roles and
        dropped every single one of them on location.

        Placeholders here rather than real place names, per this file's own
        convention: the config values ARE somebody's geography."""
        cfg = {"location": {"ok": ["<Home>"], "bad": [], "edge": []}}
        for loc in ("<city>  <home>", "<home> - <city>", "<city>, <HOME>"):
            self.assertTrue(radar.assess_location(cfg, loc, "Delivery Manager")[0], loc)

    def test_the_exclusion_lists_are_matched_case_insensitively(self):
        """The same bug on bad/edge, and this direction is the dangerous one.

        A capitalised `ok` entry keeps nothing, which at least shows up as an
        empty run. A capitalised `bad` entry EXCLUDES nothing -- so a role
        somewhere ruled out as uncommutable sails through and gets scored, and
        nothing anywhere reports that the filter did not fire."""
        cfg = {"location": {"ok": [], "bad": ["<Far>"], "edge": []}}
        self.assertFalse(radar.assess_location(cfg, "<far>, <country>", "Delivery Manager")[0])
        cfg = {"location": {"ok": [], "bad": [], "edge": ["<Maybe>"]}}
        self.assertFalse(radar.assess_location(cfg, "<MAYBE>", "Delivery Manager")[0])

    def test_case_insensitivity_does_not_become_match_everything(self):
        """The fix must not buy the empty run back by keeping the whole board."""
        cfg = {"location": {"ok": ["<Home>"], "bad": [], "edge": []}}
        for loc in ("<elsewhere>, <far>", "<other city> <far region>"):
            self.assertFalse(radar.assess_location(cfg, loc, "Delivery Manager")[0], loc)

    def test_remote_no_longer_waives_an_exclusion(self):
        """The defect. Any "remote" anywhere skipped the exclusion list, so a
        role advertised as remote WITHIN an excluded place survived a filter
        that existed to exclude that place."""
        self.assertEqual(radar.assess_location(self.CFG, "Remote - <far>", "Head of Delivery"),
                         (False, False))

    def test_the_word_in_the_title_cannot_waive_one_either(self):
        """It read location out of the title too, so a title containing the word
        exempted a role sitting squarely in an excluded city."""
        keep, _ = radar.assess_location(self.CFG, "<far>", "Remote Delivery Lead")
        self.assertFalse(keep)

    def test_an_excluded_city_named_only_in_the_title_still_drops_the_role(self):
        """Location fields are employer-entered and often wrong; the title
        frequently names the real city. The title may not EXCUSE a role from
        the exclusion list, but it can still put it on one."""
        # The location must be acceptable, or the row is dropped by the ok list
        # instead and the test proves nothing about the title.
        keep, _ = radar.assess_location(self.CFG, "<home>", "Delivery Manager, <far>")
        self.assertFalse(keep)
        self.assertTrue(radar.assess_location(self.CFG, "<home>", "Delivery Manager")[0])

    def test_unqualified_remote_is_unknown_even_with_no_ok_list_configured(self):
        """The no-filter path is the one a fresh config takes, so it needs the
        same honesty as the filtered one."""
        self.assertEqual(radar.assess_location({"location": {}}, "Remote", "Head of Delivery"),
                         (True, True))
        self.assertEqual(radar.assess_location({"location": {}}, "Remote - <home>", "x"),
                         (True, False))

    def test_a_remote_role_scoped_to_an_acceptable_place_is_kept_plainly(self):
        self.assertEqual(radar.assess_location(self.CFG, "Remote - <home>", "Head of Delivery"),
                         (True, False))

    def test_an_unqualified_remote_role_is_kept_but_marked_unknown(self):
        """Not dropped -- that loses real roles. Not trusted either: it is kept
        on the strength of a word, and the word does not say where."""
        self.assertEqual(radar.assess_location(self.CFG, "Remote", "Head of Delivery"),
                         (True, True))

    def test_an_edge_location_still_excludes_a_remote_role(self):
        keep, _ = radar.assess_location(self.CFG, "Remote - <maybe>", "Head of Delivery")
        self.assertFalse(keep)

    def test_the_shortlist_says_scope_tbc_rather_than_implying_anywhere(self):
        body = "regulated bank portfolio roadmap adoption upskill mentor stakeholder"
        rows = [posting(id="a", loc="Remote", body=body),
                posting(id="b", loc="Remote - <home>", title="Delivery Lead", body=body)]
        with Run([], {"fake": FakeAdapter(rows)}, config={"queries": ["d"],
                 "location": {"ok": ["<home>", "remote"]}}) as r:
            self.assertIn("Remote (scope TBC)", r.out)
            self.assertNotIn("Remote - <home> (scope TBC)", r.out)


class TheTieringVocabularyIsTheUsersNotTheRepos(unittest.TestCase):
    """🔴 A +6 for "not a hands-on coding role", a -6 for data centres, a -3 for
    four office days. Every one is a statement about ONE PERSON, and all of them
    shipped in tools/radar/radar.py to everyone who cloned the repo until
    2026-08-26. A florist got a scale built for a delivery director."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.f = os.path.join(self.tmp, "signal.json")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, cfg):
        with open(self.f, "w") as fh:
            json.dump(cfg, fh)
        return radar.build_signal(radar._load_signal(self.f))

    def test_no_file_means_no_tiering_and_no_exclusions(self):
        """🔴 THE ONE THAT MATTERS. A missing config must never hide a role, and
        must never fall back to somebody else's vocabulary."""
        pos, neg, never, ic, high, med = radar.build_signal(radar._load_signal(
            os.path.join(self.tmp, "absent.json")))
        self.assertEqual(pos, [])
        self.assertEqual(neg, [])
        self.assertFalse(never.search("Nurse Manager"))
        self.assertFalse(ic.match("Senior Software Engineer"))
        self.assertGreater(high, 10 ** 6, "an absent config must tier nothing as HIGH")

    def test_the_repo_ships_none_of_the_vocabulary(self):
        """The point of the move. radar.py must not carry anybody's preferences."""
        src = pathlib.Path(radar.__file__).read_text()
        for leaked in ("not a hands-on coding role", "data cent", "quantity surveyor",
                       "financial services", "weekend rota"):
            self.assertNotIn(leaked, src, f"{leaked!r} is still hardcoded in radar.py")

    def test_placeholders_are_ignored_rather_than_matched(self):
        """A template copied and not filled in must do nothing, not match '<'."""
        pos, neg, never, ic, _, _ = self.write({
            "positive": [{"match": "<a technology>", "weight": 4}],
            "exclude_titles": {"words": ["<a trade>"]},
            "individual_contributor_titles": {"nouns": ["<noun>"]}})
        self.assertEqual(pos, [])
        self.assertFalse(never.search("a trade"))
        self.assertFalse(ic.match("noun"))

    def test_a_broken_regex_is_skipped_not_fatal(self):
        pos, _, _, _, _, _ = self.write({"positive": [
            {"match": "unclosed (group", "weight": 3}, {"match": "valid", "weight": 2}]})
        self.assertEqual(pos, [("valid", 2)])

    def test_seniority_prefixes_apply_to_the_whole_group(self):
        """🔴 The bug this rewrite introduced and a check caught. Written as
        `(senior|staff|lead )*` the space binds only to the LAST alternative, so
        "Senior Software Engineer" passes a filter written to catch exactly it."""
        _, _, _, ic, _, _ = self.write({"individual_contributor_titles": {
            "seniority": ["senior", "staff", "lead"],
            "domains": ["software", "data"], "nouns": ["engineer", "scientist"]}})
        for t in ("Senior Software Engineer", "Staff Data Scientist", "Engineer"):
            self.assertTrue(ic.match(t), t)
        for t in ("Director of Engineering", "Engineering Manager", "Head of Delivery"):
            self.assertFalse(ic.match(t), t)

    def test_an_empty_ic_list_hides_nothing(self):
        """🔴 If the user IS an individual contributor, this must be inert."""
        _, _, _, ic, _, _ = self.write({"individual_contributor_titles": {"nouns": []}})
        for t in ("Senior Software Engineer", "Data Scientist", "Developer"):
            self.assertFalse(ic.match(t), t)


class NothingThatPassesTheFiltersIsHidden(unittest.TestCase):
    """🔴 The tally was a GATE and it should only ever have been a hint.

    Measured on one real run: 1,931 roles passed location and the avoid list,
    then fell below the tally threshold and were never shown. Three of the four
    roles the user had ALREADY APPLIED FOR were in that pile, scoring 6, 8 and
    10 on a scale where 18 means "read this first"."""

    def rows(self, n):
        return [{"id": f"i{i}", "title": t, "company": co, "loc": "<city>",
                 "url": f"http://e.g/{i}", "date": "2026-08-01", "source": "fake",
                 "body": body}
                for i, (co, t, body) in enumerate(n)]

    def test_a_low_scoring_role_is_listed_rather_than_dropped(self):
        rows = self.rows([("Acme", "Head of Delivery", "nothing matching any query at all")])
        with Run([], {"fake": FakeAdapter(rows)},
                 config={"queries": ["delivery"], "location": {"ok": ["<city>"]}}) as r:
            self.assertIn("Everything else that passed the filters", r.out)
            self.assertIn("Head of Delivery", r.out)

    def test_the_header_counts_everything_that_survived(self):
        rows = self.rows([("Acme", "Head of Delivery", "x"), ("Beta", "Delivery Lead", "y")])
        with Run([], {"fake": FakeAdapter(rows)},
                 config={"queries": ["delivery"], "location": {"ok": ["<city>"]}}) as r:
            self.assertIn("2 passed the filters", r.out)
            self.assertIn("below the tally threshold", r.out)

    def test_the_section_says_it_is_not_a_ranking(self):
        """🔴 Sorting by tally is what made a keyword count look like a ranking.
        The section must say so, or the next reader infers one anyway."""
        rows = self.rows([("Acme", "Head of Delivery", "x")])
        with Run([], {"fake": FakeAdapter(rows)},
                 config={"queries": ["delivery"], "location": {"ok": ["<city>"]}}) as r:
            self.assertIn("Sorted by employer", r.out)
            self.assertRegex(r.out, r"no ranking|not a lower tier|Not a lower tier")

    def test_it_is_sorted_by_employer_not_by_tally(self):
        rows = self.rows([("Zeta", "Delivery Lead", "delivery " * 30),
                          ("Alpha", "Head of Delivery", "x")])
        with Run([], {"fake": FakeAdapter(rows)},
                 config={"queries": ["delivery"], "location": {"ok": ["<city>"]}}) as r:
            tail = r.out.split("Everything else that passed the filters")[-1]
            if "Alpha" in tail and "Zeta" in tail:
                self.assertLess(tail.index("Alpha"), tail.index("Zeta"),
                                "the section is not in employer order")


class RetierDoesNotLieAboutTheWindow(unittest.TestCase):
    """🔴 docs/LESSONS.md: "a header that describes a run must be true of every
    row under it." --retier took the window from the command line rather than
    from the corpus, so re-scoring an --all-open corpus produced a file headed
    "7-day window" over rows that could be months old."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_an_all_open_corpus_remembers_it_has_no_window(self):
        radar.record_window(None, state_dir=self.tmp)
        self.assertIsNone(radar.recorded_window(state_dir=self.tmp))

    def test_a_windowed_corpus_remembers_its_window(self):
        radar.record_window(7, state_dir=self.tmp)
        self.assertEqual(radar.recorded_window(state_dir=self.tmp), 7)

    def test_an_unrecorded_corpus_is_false_not_none(self):
        """🔴 None is a REAL stored value meaning --all-open. Conflating the two
        would make an old corpus silently claim to be an unfiltered sweep."""
        self.assertIs(radar.recorded_window(state_dir=self.tmp), False)

    def test_a_corrupt_marker_falls_back_rather_than_crashing(self):
        with open(os.path.join(self.tmp, radar.WINDOW_MARKER), "w") as fh:
            fh.write("{}")
        self.assertIs(radar.recorded_window(state_dir=self.tmp), False)


class TheAllOpenSweepIsNotForgotten(unittest.TestCase):
    """🔴 An instruction that has failed twice becomes a check.

    The skill has a section headed "Run both, and know which one you ran". It
    was missed anyway on the first real use: four runs, every one windowed, and
    two roles the user had ALREADY APPLIED FOR were invisible because they were
    posted more than a week before the run."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_never_swept_says_so_loudly(self):
        self.assertIsNone(radar.sweep_age_days(state_dir=self.tmp))
        self.assertIn("NO --all-open SWEEP HAS EVER RUN", radar.sweep_warning(None))

    def test_a_stale_sweep_warns_with_its_age(self):
        w = radar.sweep_warning(30)
        self.assertIn("30 DAYS AGO", w)
        self.assertIn("--all-open", w)

    def test_a_recent_sweep_is_silent(self):
        """🔴 THE FALSE-POSITIVE CASE. A warning on every run is a warning
        nobody reads, and this one prints above the results where it is most
        tempting to start ignoring."""
        for age in (0, 1, 6, 7):
            self.assertIsNone(radar.sweep_warning(age), f"warned at {age} days")

    def test_recording_a_sweep_clears_the_warning(self):
        today = datetime.date(2026, 8, 26)
        radar.record_sweep(today, state_dir=self.tmp)
        self.assertEqual(radar.sweep_age_days(today, state_dir=self.tmp), 0)
        self.assertEqual(radar.sweep_age_days(datetime.date(2026, 9, 30), state_dir=self.tmp), 35)
        self.assertIsNone(radar.sweep_warning(radar.sweep_age_days(today, state_dir=self.tmp)))

    def test_a_corrupt_marker_warns_rather_than_crashing(self):
        """state/ is regenerable and hand-deletable. A broken marker must fail
        toward the warning, never toward silence."""
        with open(os.path.join(self.tmp, radar.SWEEP_MARKER), "w") as fh:
            fh.write("not json")
        self.assertIsNone(radar.sweep_age_days(state_dir=self.tmp))


class Dedup(unittest.TestCase):
    """One role reaching the runner from two sources must collapse to one row.

    The key was normalised_title[:40] + the RAW first twelve characters of the
    location, and the company was not in it at all. Three sources write one
    city three ways -- "Lyon, Rhône, France", "Lyon  France",
    "France - Lyon" -- so the titles normalised identically and those twelve
    characters were the whole difference. Eighteen duplicate pairs in a
    187-row shortlist."""

    def r(self, title, company, loc):
        return {"title": title, "company": company, "loc": loc}

    def test_one_city_written_three_ways_is_one_role(self):
        a = self.r("Director, Services Operations AI Governance", "Citi",
                   "Lyon, Rhône, France")
        b = self.r("Director, Services Operations AI Governance", "Citi", "Lyon  France")
        c = self.r("Director, Services Operations AI Governance", "Citi", "France - Lyon")
        self.assertTrue(radar.same_role(a, b))
        self.assertTrue(radar.same_role(b, c))
        self.assertTrue(radar.same_role(a, c))

    def test_the_company_case_no_longer_matters(self):
        """A board adapter labels rows with its own token."""
        a = self.r("Senior Sales Operations Analyst", "MongoDB", "Lyon, France")
        b = self.r("Senior Sales Operations Analyst", "mongodb", "Lyon, France")
        self.assertTrue(radar.same_role(a, b))

    def test_two_cities_in_one_country_are_two_roles(self):
        """🔴 THE FALSE-POSITIVE CASE, and the one that decided the design.

        Plain token overlap looks right and is wrong: every location in one
        country shares the country name, so "Lyon, France" and "Nice,
        France" intersect on 'france' and one real role vanishes. A
        disappearing role is the worst failure this tool has, because nothing
        reports it. Subset, not intersection."""
        a = self.r("Delivery Manager", "Acme", "Lyon, France")
        b = self.r("Delivery Manager", "Acme", "Nice, France")
        self.assertFalse(radar.same_role(a, b))
        c = self.r("Delivery Manager", "Acme", "Lyon, Rhône, France")
        d = self.r("Delivery Manager", "Acme", "Nice, Alpes-Maritimes, France")
        self.assertFalse(radar.same_role(c, d))

    def test_the_same_title_at_two_employers_is_two_roles(self):
        a = self.r("Engineering Manager", "Acme", "Lyon, France")
        b = self.r("Engineering Manager", "Beta Corp", "Lyon, France")
        self.assertFalse(radar.same_role(a, b))

    def test_a_narrower_location_folds_into_a_wider_one(self):
        a = self.r("Engineering Manager", "Acme", "San Francisco, CA")
        b = self.r("Engineering Manager", "Acme", "San Francisco")
        self.assertTrue(radar.same_role(a, b))

    def test_an_unknown_location_does_not_split_a_role(self):
        a = self.r("Engineering Manager", "Acme", "")
        b = self.r("Engineering Manager", "Acme", "Lyon, France")
        self.assertTrue(radar.same_role(a, b))

    def test_an_abbreviated_country_folds_into_the_written_one(self):
        """Found by hand, not by the checker. One employer posted the same role
        as "Lyon, FRA" and "Lyon, Rhone, France" and the subset rule kept them
        apart, because "fra" is not "france"."""
        a = self.r("Senior Director of Engineering", "Acme", "Lyon, FRA")
        b = self.r("Senior Director of Engineering", "Acme", "Lyon, Rhone, France")
        self.assertTrue(radar.same_role(a, b))

    def test_a_two_letter_token_never_prefix_matches(self):
        """🔴 THE FALSE-POSITIVE CASE, and it is why there is a length floor.

        "Ontario, CA" is Ontario, California. "Ontario, Canada" is a different
        continent. Allow a two-letter token to prefix-match and those two
        become one role, and the one that vanishes is never reported. Every
        two-letter state and country code is this trap: CA, IN, ID, LA, MO."""
        a = self.r("Delivery Manager", "Acme", "Ontario, CA")
        b = self.r("Delivery Manager", "Acme", "Ontario, Canada")
        self.assertFalse(radar.same_role(a, b))
        c = self.r("Delivery Manager", "Acme", "Lyon, IN")
        d = self.r("Delivery Manager", "Acme", "Lyon, Indiana")
        self.assertFalse(radar.same_role(c, d))

    def test_prefix_matching_does_not_merge_two_real_places(self):
        a = self.r("Delivery Manager", "Acme", "Lyon, France")
        b = self.r("Delivery Manager", "Acme", "Nice, France")
        self.assertFalse(radar.same_role(a, b))

    def test_different_titles_never_merge(self):
        a = self.r("Engineering Manager", "Acme", "Lyon, France")
        b = self.r("Delivery Manager", "Acme", "Lyon, France")
        self.assertFalse(radar.same_role(a, b))


class BoardTitleFilter(unittest.TestCase):
    """A board returns everything an employer has open, so it needs its own
    relevance filter. This one matched the FIRST word of the query.
    """

    def test_it_no_longer_matches_on_the_least_informative_word(self):
        """"head of delivery" matched on "head": every Head of Anything kept,
        every Delivery Manager dropped. Wrong in both directions at once."""
        self.assertTrue(_titles.matches("head of delivery", "Delivery Manager"))
        self.assertFalse(_titles.matches("head of delivery", "Head of Legal"))

    def test_it_discriminates_on_the_domain_word_not_the_seniority_word(self):
        """Boards are full of Managers. They are not full of Delivery."""
        self.assertTrue(_titles.matches("delivery manager", "Service Delivery Manager"))
        self.assertFalse(_titles.matches("delivery manager", "Account Manager"))

    def test_a_short_query_word_does_not_match_inside_a_longer_one(self):
        """THE FALSE-POSITIVE CASE, and the one that mattered most.

        The match was `w in title`, a raw substring test. "ai" is two letters
        and it lives inside retail, training, maintenance, campaign, email,
        domain, chair and air. With fifteen AI-flavoured queries on a real
        watchlist, every AI query kept every Retail Operations Manager on
        every board."""
        for junk in ("Retail Operations Manager", "Maintenance Technician",
                     "Training Coordinator", "Campaign Manager",
                     "Email Marketing Specialist", "Domain Administrator",
                     "Chair of the Board", "Air Traffic Analyst"):
            self.assertFalse(_titles.matches("head of ai", junk), junk)

    def test_it_still_matches_the_word_it_is_actually_looking_for(self):
        """The fix must not buy precision by breaking recall."""
        for real in ("Head of AI", "Director, AI Platform Engineering",
                     "Senior Team Lead, AI Engineering", "Applied AI Product Manager",
                     "AI/ML Programme Lead"):
            self.assertTrue(_titles.matches("head of ai", real), real)

    def test_technical_digital_and_data_are_not_distinctive(self):
        """Measured against a real board: 74 of 138 rows survived the filter and
        seventeen were Account Executives. "Cloud Account Executive - Digital"
        was kept by "digital transformation"; "Technical Support Engineer" by
        three separate queries. These words are everywhere in sales and support
        titles, so they discriminate nothing."""
        self.assertFalse(_titles.matches("digital transformation",
                                         "Cloud Account Executive - Digital, Northern Europe"))
        self.assertFalse(_titles.matches("technical program manager",
                                         "Technical Support Engineer - German or French"))
        self.assertFalse(_titles.matches("data and ai", "Account Executive, SMB Data Cloud"))

    def test_those_queries_still_find_what_they_are_for(self):
        self.assertTrue(_titles.matches("digital transformation",
                                        "Head of Digital Transformation"))
        self.assertTrue(_titles.matches("technical program manager",
                                        "Lead Technical Program Manager"))
        self.assertTrue(_titles.matches("data and ai",
                                        "Associate Director, Data & AI Internal Product Team"))

    def test_an_all_generic_query_falls_back_to_requiring_every_word(self):
        """Nothing distinctive to ask for, so ask for all of it. "senior
        manager" deserves strict -- loose, it would return the whole board."""
        self.assertTrue(_titles.matches("senior manager", "Senior Manager, Tax"))
        self.assertFalse(_titles.matches("senior manager", "Senior Accountant"))
        self.assertFalse(_titles.matches("senior manager", "Category Manager"))

    def test_stopwords_are_not_evidence(self):
        self.assertFalse(_titles.matches("head of delivery", "Director of Legal"))

    def test_an_empty_query_keeps_the_board(self):
        """No query is not a reason to drop an employer being watched."""
        self.assertTrue(_titles.matches("", "Anything At All"))
        self.assertTrue(_titles.matches("of the", "Anything At All"))

    def test_the_adapters_actually_use_it(self):
        payload = [{"id": 1, "title": "Delivery Manager", "content": "x",
                    "location": {"name": "<city>"}, "updated_at": "2026-08-01",
                    "absolute_url": "u"},
                   {"id": 2, "title": "Head of Legal", "content": "x",
                    "location": {"name": "<city>"}, "updated_at": "2026-08-01",
                    "absolute_url": "u"}]
        greenhouse.get_json = lambda url, headers=None: {"jobs": payload}
        got = greenhouse.fetch({"greenhouse": {"boards": ["t"]}}, "head of delivery", None)
        self.assertEqual([g["title"] for g in got], ["Delivery Manager"])


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

    def test_a_visible_salary_does_not_change_the_signal(self):
        """The tally counts what the role is about. Salary is not that.

        Only one adapter returns a structured salary field, so a bonus for
        having one was largely a measurement of WHICH SOURCE FOUND THE ROLE --
        the same role fetched two ways scored two different ways. A scoring term
        only some inputs can earn measures the input pipeline.
        """
        body = "regulated bank portfolio roadmap adoption upskill mentor stakeholder"
        rows = [posting(id="paid", title="Head of Delivery €120k", body=body),
                posting(id="quiet", title="Head of Delivery Ops", body=body)]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            cached = json.load(open(radar.RAW))
            self.assertEqual(cached["paid"]["tally"], cached["quiet"]["tally"])
            self.assertEqual(cached["paid"]["signal"], cached["quiet"]["signal"])

    def test_a_structured_salary_from_the_adapter_does_not_either(self):
        """Adzuna supplies pay as a field; the boards supply nothing."""
        body = "regulated bank portfolio roadmap adoption upskill mentor stakeholder"
        rows = [posting(id="a", body=body, pay="90,000-110,000"),
                posting(id="b", title="Head of Delivery Ops", body=body)]
        with Run([], {"fake": FakeAdapter(rows)}) as r:
            cached = json.load(open(radar.RAW))
            self.assertEqual(cached["a"]["tally"], cached["b"]["tally"])

    def test_the_salary_still_reaches_the_pay_column(self):
        """Removing the bonus must not remove the information.

        The column says the actual figure, which is more than three anonymous
        points ever did.
        """
        body = "regulated bank portfolio roadmap adoption upskill mentor stakeholder"
        with Run([], {"fake": FakeAdapter([posting(title="Head of Delivery €120k",
                                                  body=body)])}) as r:
            self.assertIn("| €120k |", r.out)

    def test_pay_can_no_longer_promote_a_role_across_a_band(self):
        """The concrete harm: 3 points is a third of the gap between bands.

        A role sitting just under a cut-point used to cross it because its title
        happened to mention money, or because it arrived via the one adapter
        that reports salary.
        """
        just_under = "stakeholder mentor coach adoption upskill portfolio"
        self.assertLess(radar.tally_of(just_under), radar.MED_AT)
        self.assertGreaterEqual(radar.tally_of(just_under) + 3, radar.MED_AT)
        with Run([], {"fake": FakeAdapter([posting(title="Head of Delivery €120k",
                                                  body=just_under)])}) as r:
            self.assertNotIn("| MED |", r.out)
            self.assertNotIn("| HIGH |", r.out)

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


class FlagsAreCheckedNotSniffed(unittest.TestCase):
    """`"--adapter" in sys.argv` had three failure modes and every one was
    silent: an unknown flag ignored, an unknown adapter name yielding an empty
    fetch -- the "silent zero" the skill warns about, reachable by one typo --
    and a missing --days value crashing on an IndexError."""

    def test_help_works_before_the_config_exists(self):
        """The first thing anybody types. A tool that will not describe itself
        until it is configured is one nobody gets as far as configuring."""
        r = subprocess.run([sys.executable, RADAR, "--help"], capture_output=True, text=True,
                           env=dict(os.environ, CAREER_VAULT="/nonexistent-vault"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--adapter", r.stdout)

    def test_an_unknown_adapter_is_refused_by_name(self):
        r = subprocess.run([sys.executable, RADAR, "--adapter", "greanhouse"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("invalid choice", r.stderr)

    def test_an_unknown_flag_is_refused(self):
        r = subprocess.run([sys.executable, RADAR, "--adaptor", "greenhouse"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)

    def test_days_needs_a_number(self):
        r = subprocess.run([sys.executable, RADAR, "--days", "soon"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)

    def test_the_old_flag_name_still_works(self):
        self.assertTrue(radar.parse(["--retier"]).score_only)
        self.assertTrue(radar.parse(["--score-only"]).score_only)

    def test_all_open_beats_days(self):
        a = radar.parse(["--days", "3", "--all-open"])
        self.assertTrue(a.all_open)
