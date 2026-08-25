"""oracle: the other large enterprise ATS, and the one with real dates.

Recorded response shapes, no network. Verified against three live tenants when
it was written -- a numbered site, a named site, and a host with no region in
it -- and the shapes here are what those returned.

The case worth understanding before changing anything: this source has no
posting-window parameter, but it does give an exact PostedDate on every row and
sorts newest first. So the window is applied in the adapter and paging stops at
the first row outside it. That makes HONOURS_DAYS true and it makes stopping
early COMPLETENESS rather than a cap -- which is the opposite of what stopping
early means everywhere else in this package, and is why it is pinned here.
"""
import datetime, importlib.util, io, os, sys, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
from adapters import oracle                                       # noqa: E402

TODAY = datetime.date.today()


def ago(n):
    return (TODAY - datetime.timedelta(days=n)).isoformat()


def req(jid="R100", title="Head of Delivery", posted=None, loc="<city>, <country>",
        secondary=None, short="A short description."):
    return {"Id": jid, "Title": title, "PostedDate": posted or ago(1),
            "PrimaryLocation": loc, "ShortDescriptionStr": short,
            "secondaryLocations": [{"Name": n} for n in (secondary or [])]}


def listing(rows, total=None):
    return {"items": [{"TotalJobsCount": total if total is not None else len(rows),
                       "requisitionList": rows}]}


def cfg(employer=None, **kw):
    e = employer or {"host": "<pod>.fa.us2.oraclecloud.com", "site": "<site>"}
    base = {"oracle": {"employers": [e], "pages": 5, "delay": 0}}
    base["oracle"].update(kw)
    return base


class Recorder:
    def __init__(self, pages=None, detail=None):
        self.pages, self.detail, self.urls = pages or [], detail, []

    def get_json(self, url, headers=None):
        self.urls.append(url)
        if "RequisitionDetails" in url:
            return self.detail
        i = len([u for u in self.urls if "RequisitionDetails" not in u]) - 1
        return self.pages[i] if i < len(self.pages) else listing([])

    def install(self):
        oracle.get_json = self.get_json
        return self


def run(conf, rec, query="delivery", days=None):
    rec.install()
    buf = io.StringIO()
    with redirect_stdout(buf):
        out = oracle.fetch(conf, query, days)
    return out, buf.getvalue()


class TwoValuesBothFromTheUrl(unittest.TestCase):
    """Unlike Workday this needs no third value, and the host is not derived."""

    def test_the_site_segment_of_the_url_is_the_api_site_number(self):
        rec = Recorder([listing([req()])])
        run(cfg(), rec)
        self.assertIn("siteNumber=%3Csite%3E", rec.urls[0])

    def test_a_host_with_no_region_is_taken_verbatim(self):
        """Tenants appear with and without a region. Constructing it loses one."""
        rec = Recorder([listing([req()])])
        run(cfg(employer={"host": "<pod>.fa.oraclecloud.com", "site": "<site>"}), rec)
        self.assertTrue(rec.urls[0].startswith("https://<pod>.fa.oraclecloud.com/hcmRestApi/"))

    def test_an_incomplete_entry_is_skipped_and_said_so(self):
        rec = Recorder([listing([req()])])
        out, said = run(cfg(employer={"host": "<pod>.fa.us2.oraclecloud.com"}), rec)
        self.assertEqual(out, [])
        self.assertIn("host and site", said)
        self.assertEqual(rec.urls, [])

    def test_the_query_reaches_the_keyword_parameter(self):
        rec = Recorder([listing([req()])])
        run(cfg(), rec, query="head of delivery")
        self.assertIn("keyword", rec.urls[0])

    def test_the_public_url_points_at_the_candidate_site_not_the_api(self):
        rec = Recorder([listing([req(jid="R900")])])
        out, _ = run(cfg(), rec)
        self.assertEqual(
            out[0]["url"],
            "https://<pod>.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/<site>/job/R900")


class TheWindow(unittest.TestCase):
    """The window is exact here, because the date is."""

    def test_rows_outside_the_window_are_dropped(self):
        rec = Recorder([listing([req(jid="new", posted=ago(2)),
                                 req(jid="old", posted=ago(40))], total=2)])
        out, _ = run(cfg(), rec, days=7)
        self.assertEqual([r["requisition"] for r in out], ["new"])

    def test_stopping_at_the_window_edge_is_completeness_not_a_cap(self):
        """Newest first, so the first row outside it means every later one is.

        Everywhere else in this package an early stop means the source had more
        to give. Here it means the opposite, and reporting truncation would send
        the reader looking for roles that do not exist.
        """
        rec = Recorder([listing([req(jid="a", posted=ago(1)),
                                 req(jid="b", posted=ago(90))], total=5000)])
        run(cfg(), rec, days=7)
        self.assertFalse(oracle.TRUNCATED)

    def test_running_out_of_page_budget_inside_the_window_is_truncation(self):
        rows = [req(jid=f"r{i}", posted=ago(1)) for i in range(25)]
        rec = Recorder([listing(rows, total=5000), listing(rows, total=5000)])
        run(cfg(pages=2), rec, days=7)
        self.assertTrue(oracle.TRUNCATED)

    def test_no_window_means_no_date_filtering_at_all(self):
        rec = Recorder([listing([req(jid="ancient", posted="2019-01-01")], total=1)])
        out, _ = run(cfg(), rec, days=None)
        self.assertEqual(len(out), 1)

    def test_a_failed_request_is_truncation_and_says_so(self):
        rec = Recorder([None])
        out, said = run(cfg(), rec)
        self.assertEqual(out, [])
        self.assertTrue(oracle.TRUNCATED)
        self.assertIn("request failed", said)


class Fields(unittest.TestCase):
    def test_the_rows_are_two_levels_down_behind_a_search_object(self):
        rec = Recorder([listing([req(title="Head of Delivery")])])
        out, _ = run(cfg(), rec)
        self.assertEqual(out[0]["title"], "Head of Delivery")

    def test_the_id_is_the_requisition_number_the_employer_prints(self):
        rec = Recorder([listing([req(jid="R-4412")])])
        out, _ = run(cfg(), rec)
        self.assertEqual(out[0]["requisition"], "R-4412")

    def test_secondary_locations_are_appended_to_the_primary(self):
        rec = Recorder([listing([req(loc="<city-a>", secondary=["<city-b>", "<city-c>"])])])
        out, _ = run(cfg(), rec)
        self.assertEqual(out[0]["loc"], "<city-a>; <city-b>; <city-c>")

    def test_the_date_is_used_as_given_with_no_derivation(self):
        """No "30+ days ago" here, so no floor and no dagger."""
        rec = Recorder([listing([req(posted="2026-07-04")])])
        out, _ = run(cfg(), rec)
        self.assertEqual(out[0]["date"], "2026-07-04")
        self.assertFalse(out[0].get("date_is_floor"))

    def test_an_unrecognised_shape_yields_a_thin_row_not_a_traceback(self):
        rec = Recorder([listing([{}])])
        out, _ = run(cfg(), rec)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["loc"], "?")

    def test_no_employers_configured_is_silence_not_an_error(self):
        self.assertEqual(oracle.fetch({"oracle": {"employers": []}}, "q", None), [])
        self.assertEqual(oracle.fetch({}, "q", None), [])


class Descriptions(unittest.TestCase):
    def test_body_is_left_empty_so_the_runner_fetches_the_full_text(self):
        """Tiering on the short description would under-score this source.

        Every other source gets its full description read before it is tiered.
        Scoring one of them on a summary is the same defect as a scoring term
        that only some inputs can earn.
        """
        rec = Recorder([listing([req(short="A summary.")])])
        out, _ = run(cfg(), rec)
        self.assertEqual(out[0]["body"], "")
        self.assertEqual(out[0]["_short"], "A summary.")

    def test_fetch_body_returns_the_full_description(self):
        rec = Recorder([listing([req()])],
                       detail={"items": [{"ExternalDescriptionStr":
                                          "<p>Runs delivery &amp; more</p>"}]})
        out, _ = run(cfg(), rec)
        self.assertEqual(oracle.fetch_body(out[0]), "Runs delivery & more")

    def test_it_degrades_to_the_short_description_rather_than_to_nothing(self):
        """A failed fetch elsewhere makes a good role signal low for no reason.

        Here the listing already handed over something real, so it is used.
        """
        rec = Recorder([listing([req(short="The summary.")])], detail=None)
        out, _ = run(cfg(), rec)
        self.assertEqual(oracle.fetch_body(out[0]), "The summary.")
        self.assertEqual(oracle.fetch_body({"_short": "only this"}), "only this")

    def test_the_detail_finder_quotes_its_values(self):
        """The write-up says unquoted 400s. It did not, on any tenant tried.

        Quoting costs nothing and is kept, so this pins the behaviour rather
        than the claim.
        """
        rec = Recorder([listing([req(jid="R1")])],
                       detail={"items": [{"ExternalDescriptionStr": "x"}]})
        out, _ = run(cfg(), rec)
        oracle.fetch_body(out[0])
        # The quotes are in the safe set on purpose: percent-encoded they are
        # not quotes any more, and quoting is the whole point of keeping them.
        self.assertIn('Id="R1"', rec.urls[-1])


if __name__ == "__main__":
    unittest.main()
