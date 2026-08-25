"""workday: the adapter for the API behind a large share of enterprise careers.

Recorded response shapes, no network. The endpoints were verified against two
real employers when they were written up; what is tested here is that this
adapter reads them correctly and fails usefully when it cannot.

Three of these encode a failure the write-up warned about specifically:
deriving the host from the tenant silently loses every employer on the other
hosting style; a 422 is a wrong shard rather than a bad request, and reporting
it as a generic failure sends someone to rewrite a request that was fine; and a
listing that says "4 Locations" hides the one city that would have kept the role
in the search.
"""
import datetime, importlib.util, io, os, sys, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
from adapters import workday                                      # noqa: E402

TODAY = datetime.date.today()


def listing(rows, total=None):
    return {"total": total if total is not None else len(rows), "jobPostings": rows}


def row(title="Head of Delivery", loc="<city>", posted="Posted 5 Days Ago",
        path="/job/<city>/Head-of-Delivery_R-100", req="R-100"):
    return {"title": title, "locationsText": loc, "postedOn": posted,
            "externalPath": path, "bulletFields": [req]}


def cfg(**kw):
    e = {"host": "acme.wd1.myworkdayjobs.com", "tenant": "acme", "site": "External"}
    e.update(kw.pop("employer", {}))
    base = {"workday": {"employers": [e], "delay": 0, "pages": 5}}
    base["workday"].update(kw)
    return base


class Recorder:
    """Stands in for the network. Records what was asked for."""

    def __init__(self, pages=None, detail=None, status=200):
        self.pages, self.detail, self.status = pages or [], detail or {}, status
        self.posts, self.gets = [], []

    def post_json(self, url, payload, headers=None, timeout=30):
        self.posts.append((url, payload))
        if self.status != 200:
            return None, self.status
        i = payload["offset"] // workday.PAGE
        return (self.pages[i] if i < len(self.pages) else listing([])), 200

    def get_json(self, url, headers=None):
        self.gets.append(url)
        return self.detail

    def install(self):
        workday.post_json, workday.get_json = self.post_json, self.get_json
        return self


def run(conf, rec, query="delivery"):
    rec.install()
    buf = io.StringIO()
    with redirect_stdout(buf):
        out = workday.fetch(conf, query, None)
    return out, buf.getvalue()


class TheTwoHostingStyles(unittest.TestCase):
    """Deriving the host from the tenant covers one style and loses the other.

    It loses it quietly: the employer simply never appears in a run. Which is
    why host, tenant and site are three separate config inputs.
    """

    def test_the_per_tenant_subdomain_style(self):
        rec = Recorder([listing([row()])])
        run(cfg(), rec)
        self.assertEqual(rec.posts[0][0],
                         "https://acme.wd1.myworkdayjobs.com/wday/cxs/acme/External/jobs")

    def test_the_shared_host_style_is_not_derived_from_the_tenant(self):
        rec = Recorder([listing([row()])])
        run(cfg(employer={"host": "wd1.myworkdaysite.com"}), rec)
        self.assertEqual(rec.posts[0][0],
                         "https://wd1.myworkdaysite.com/wday/cxs/acme/External/jobs")

    def test_an_incomplete_employer_entry_is_skipped_and_said_so(self):
        rec = Recorder([listing([row()])])
        out, said = run(cfg(employer={"site": None}), rec)
        self.assertEqual(out, [])
        self.assertIn("host, tenant and site", said)
        self.assertEqual(rec.posts, [])

    def test_the_query_is_used_because_workday_really_searches(self):
        rec = Recorder([listing([row()])])
        run(cfg(), rec, query="head of delivery")
        self.assertEqual(rec.posts[0][1]["searchText"], "head of delivery")


class TheShard(unittest.TestCase):
    def test_a_422_names_the_shard_rather_than_the_request(self):
        """422 means the tenant is on wd3 or wd5, not that the body is wrong.

        Reported as a generic failure it sends someone to rewrite a request
        that was correct all along.
        """
        rec = Recorder(status=422)
        out, said = run(cfg(), rec)
        self.assertEqual(out, [])
        self.assertIn("different wd shard", said)
        self.assertTrue(workday.TRUNCATED)

    def test_another_status_is_reported_plainly(self):
        rec = Recorder(status=503)
        _, said = run(cfg(), rec)
        self.assertIn("503", said)
        self.assertNotIn("shard", said)


class HiddenLocations(unittest.TestCase):
    """The runner filters on location BEFORE it reads any description.

    So a role open in the user's city but advertised under one they exclude is
    dropped and never looked at again. When the listing admits it is hiding
    locations, the detail is worth the extra call.
    """

    def test_n_locations_triggers_the_detail_call_and_expands_them(self):
        rec = Recorder([listing([row(loc="4 Locations")])],
                       detail={"jobPostingInfo": {
                           "location": "<city-a>",
                           "additionalLocations": ["<city-b>", "<city-c>"],
                           "jobDescription": "<p>Runs delivery.</p>",
                           "jobReqId": "R-777", "startDate": "2026-07-04"}})
        out, _ = run(cfg(), rec)
        self.assertEqual(len(rec.gets), 1)
        self.assertEqual(out[0]["loc"], "<city-a>; <city-b>; <city-c>")
        self.assertEqual(out[0]["requisition"], "R-777")
        self.assertEqual(out[0]["body"], "Runs delivery.")

    def test_and_so_does_the_other_phrasing(self):
        rec = Recorder([listing([row(loc="<city> and 3 more")])],
                       detail={"jobPostingInfo": {"location": "<city>",
                                                  "additionalLocations": ["<city-b>"]}})
        out, _ = run(cfg(), rec)
        self.assertEqual(len(rec.gets), 1)
        self.assertEqual(out[0]["loc"], "<city>; <city-b>")

    def test_a_plain_location_costs_no_extra_request(self):
        """Expanding every posting would triple the request count for nothing."""
        rec = Recorder([listing([row(loc="<city>")])])
        out, _ = run(cfg(), rec)
        self.assertEqual(rec.gets, [])
        self.assertEqual(out[0]["loc"], "<city>")


class Dates(unittest.TestCase):
    def test_relative_dates_become_real_ones(self):
        self.assertEqual(workday._date("Posted Today"), (TODAY.isoformat(), False))
        self.assertEqual(workday._date("Posted 5 Days Ago"),
                         ((TODAY - datetime.timedelta(days=5)).isoformat(), False))

    def test_thirty_plus_is_a_floor_and_is_marked_as_one(self):
        """"Posted 30+ Days Ago" is the same string for a role six months old.

        A date derived from it looks exact and is not, which is the
        aggregator-re-dating problem in a new coat. The raw text is kept beside
        it so nothing downstream has to trust the derived value.
        """
        iso, floor = workday._date("Posted 30+ Days Ago")
        self.assertEqual(iso, (TODAY - datetime.timedelta(days=30)).isoformat())
        self.assertTrue(floor)

    def test_the_raw_text_survives_onto_the_row(self):
        rec = Recorder([listing([row(posted="Posted 30+ Days Ago")])])
        out, _ = run(cfg(), rec)
        self.assertEqual(out[0]["posted_text"], "Posted 30+ Days Ago")
        self.assertTrue(out[0]["date_is_floor"])

    def test_an_exact_start_date_from_the_detail_beats_the_derived_one(self):
        rec = Recorder([listing([row(loc="2 Locations", posted="Posted 30+ Days Ago")])],
                       detail={"jobPostingInfo": {"location": "<city>",
                                                  "startDate": "2026-01-09"}})
        out, _ = run(cfg(), rec)
        self.assertEqual(out[0]["date"], "2026-01-09")
        self.assertFalse(out[0]["date_is_floor"])

    def test_an_unparseable_string_is_blank_rather_than_invented(self):
        self.assertEqual(workday._date("Posted recently"), ("", False))
        self.assertEqual(workday._date(""), ("", False))


class Pagination(unittest.TestCase):
    def test_it_stops_when_it_has_everything_and_says_so(self):
        rec = Recorder([listing([row(req=f"R-{i}") for i in range(20)], total=25),
                        listing([row(req=f"R-{i}") for i in range(20, 25)], total=25)])
        out, _ = run(cfg(), rec)
        self.assertEqual(len(out), 25)
        self.assertEqual(len(rec.posts), 2)
        self.assertFalse(workday.TRUNCATED)

    def test_running_out_of_page_budget_is_truncation_and_workday_knows_the_total(self):
        """Not a guess here: the API returns the true total, so the gap is known."""
        rec = Recorder([listing([row(req=f"R-{i}") for i in range(20)], total=500)])
        run(cfg(pages=1), rec)
        self.assertTrue(workday.TRUNCATED)

    def test_an_empty_page_ends_it_without_claiming_truncation(self):
        rec = Recorder([listing([row()], total=1)])
        run(cfg(), rec)
        self.assertFalse(workday.TRUNCATED)


class Robustness(unittest.TestCase):
    def test_an_unrecognised_shape_yields_a_thin_row_not_a_traceback(self):
        """A tenant returning something this has not seen must not kill the run."""
        rec = Recorder([listing([{}])])
        out, _ = run(cfg(), rec)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["title"], "")
        self.assertEqual(out[0]["loc"], "?")
        self.assertEqual(out[0]["source"], "workday")

    def test_no_employers_configured_is_silence_not_an_error(self):
        self.assertEqual(workday.fetch({"workday": {"employers": []}}, "q", None), [])
        self.assertEqual(workday.fetch({}, "q", None), [])

    def test_it_declares_that_it_ignores_the_window(self):
        """No recency parameter exists, so claiming a window would be a lie."""
        self.assertFalse(workday.HONOURS_DAYS)


class FetchBody(unittest.TestCase):
    def test_it_takes_the_row_because_a_posting_needs_four_values(self):
        rec = Recorder(detail={"jobPostingInfo": {"jobDescription": "<b>Text.</b>"}}).install()
        r = {"_wd": ["h", "t", "s", "/job/x"]}
        self.assertEqual(workday.fetch_body(r), "Text.")
        self.assertEqual(rec.gets, ["https://h/wday/cxs/t/s/job/x"])

    def test_a_row_without_the_stash_returns_empty_rather_than_raising(self):
        self.assertEqual(workday.fetch_body({}), "")
        self.assertEqual(workday.fetch_body(None), "")


if __name__ == "__main__":
    unittest.main()
