"""custom: employers who run their own job API.

The test that matters most here is the location one. Deel carries both
`location_name` -- the first of thirty countries, "Israel" -- and
`all_locations`. Mapping the obvious-looking field would filter out every Deel
role for a user eligible for all of them, and nothing would say so.
"""
import importlib.util, json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
from adapters import custom, ADAPTERS                                  # noqa: E402
from adapters import _verdicts as V                                    # noqa: E402

DEEL_MAP = {"id": "attributes.ashby_id", "title": "attributes.title",
            "loc": "attributes.all_locations", "date": "attributes.ashby_published_date",
            "pay": "attributes.compensation_tier_summary", "url": "attributes.slug",
            "body": "attributes.full_job_description"}

ROW = {"id": 0, "attributes": {
    "ashby_id": "abc-123", "title": "Senior Team Lead, AI Engineering",
    "location_name": "Israel",
    "all_locations": ["Israel", "Portugal", "Ireland", "Germany"],
    "ashby_published_date": "2026-07-23T12:46:07.533Z",
    "compensation_tier_summary": "$85,000 - $180,000 USD",
    "slug": "/careers/position/?ashby_jid=abc-123",
    "full_job_description": ""}}

CFG = {"custom": {"employers": [{"employer": "Deel", "params": {
    "list": "https://example.test/jobs/", "detail": "https://example.test/jobs/{id}/",
    "url_prefix": "https://example.test", "map": DEEL_MAP}}]}}


class Stub:
    """Replaces the network for the whole module."""

    def __init__(self, payload):
        self.payload, self.calls = payload, []

    def __call__(self, url, *a, **k):
        self.calls.append(url)
        return self.payload(url) if callable(self.payload) else self.payload


class Digging(unittest.TestCase):
    def test_a_dotted_path(self):
        self.assertEqual(custom.dig(ROW, "attributes.title"), "Senior Team Lead, AI Engineering")

    def test_a_missing_path_is_empty_not_an_error(self):
        self.assertEqual(custom.dig(ROW, "attributes.nope.deeper"), "")

    def test_a_list_is_joined_rather_than_truncated(self):
        self.assertEqual(custom.dig(ROW, "attributes.all_locations"),
                         "Israel, Portugal, Ireland, Germany")

    def test_a_list_of_objects_is_flattened(self):
        row = {"l": [{"location": "Ireland"}, {"location": "Spain"}]}
        self.assertEqual(custom.dig(row, "l"), "Ireland, Spain")


class Fetching(unittest.TestCase):
    def setUp(self):
        self._get = custom.get_json
        self.addCleanup(lambda: setattr(custom, "get_json", self._get))

    def test_every_location_reaches_the_runner(self):
        """The whole point. location_name would say Israel and lose the role."""
        custom.get_json = Stub([ROW])
        row = custom.fetch(CFG, "", None)[0]
        self.assertIn("Ireland", row["loc"])
        self.assertNotEqual(row["loc"], "Israel")

    def test_the_row_matches_what_the_runner_expects(self):
        custom.get_json = Stub([ROW])
        r = custom.fetch(CFG, "", None)[0]
        self.assertEqual(r["title"], "Senior Team Lead, AI Engineering")
        self.assertEqual(r["company"], "Deel")
        self.assertEqual(r["date"], "2026-07-23")
        self.assertEqual(r["pay"], "$85,000 - $180,000 USD")
        self.assertEqual(r["source"], "custom")
        self.assertTrue(r["id"].startswith("custom:"))

    def test_a_relative_url_gets_the_prefix(self):
        custom.get_json = Stub([ROW])
        self.assertEqual(custom.fetch(CFG, "", None)[0]["url"],
                         "https://example.test/careers/position/?ashby_jid=abc-123")

    def test_a_failed_request_is_truncation_not_an_empty_board(self):
        custom.get_json = Stub(None)
        self.assertEqual(custom.fetch(CFG, "", None), [])
        self.assertTrue(custom.TRUNCATED)

    def test_nobody_configured_is_not_an_error(self):
        self.assertEqual(custom.fetch({}, "", None), [])

    def test_it_finds_the_rows_however_the_api_wraps_them(self):
        for payload in ([ROW], {"jobs": [ROW]}, {"results": [ROW]}, {"data": [ROW]}):
            custom.get_json = Stub(payload)
            self.assertEqual(len(custom.fetch(CFG, "", None)), 1, payload)


class Bodies(unittest.TestCase):
    def setUp(self):
        self._get = custom.get_json
        self.addCleanup(lambda: setattr(custom, "get_json", self._get))

    def test_a_detail_response_that_unwraps_what_the_list_wrapped(self):
        """Deel returns attributes.full_job_description in the listing and
        full_job_description on its own in the detail. One mapping, both shapes."""
        custom.get_json = Stub(lambda url: [ROW] if url.endswith("jobs/")
                               else {"full_job_description": "<p>Own the <b>vision</b></p>"})
        row = custom.fetch(CFG, "", None)[0]
        self.assertEqual(custom.fetch_body(row), "Own the vision")

    def test_a_row_from_another_adapter_is_ignored(self):
        self.assertEqual(custom.fetch_body({"id": "linkedin:1"}), "")


class Probing(unittest.TestCase):
    def setUp(self):
        self._get = custom.get_json
        self.addCleanup(lambda: setattr(custom, "get_json", self._get))

    def test_nobody_watched_is_not_configured_rather_than_failed(self):
        self.assertEqual(custom.probe({})[0], V.NOT_CONFIGURED)

    def test_an_answering_board_is_ok_with_a_count(self):
        custom.get_json = Stub([ROW])
        status, msg = custom.probe(CFG)
        self.assertEqual(status, V.OK)
        self.assertIn("Deel (1 open)", msg)

    def test_a_board_that_answers_with_nothing_fails(self):
        custom.get_json = Stub([])
        self.assertEqual(custom.probe(CFG)[0], V.FAILED)


class Wiring(unittest.TestCase):
    def test_it_is_registered(self):
        self.assertIs(ADAPTERS.get("custom"), custom)

    def test_the_shipped_deel_entry_maps_all_locations_not_the_first_one(self):
        reg = json.load(open(os.path.join(ROOT, "tools", "radar", "ats_registry.json"), encoding="utf-8"))
        deel = [e for e in reg["employers"] if e["employer"] == "Deel"][0]
        self.assertEqual(deel["params"]["map"]["loc"], "attributes.all_locations")

    def test_the_resolver_expands_a_custom_employer(self):
        from registry import resolve
        cfg, report = resolve({"watch": ["Deel"]})
        self.assertEqual([r[1] for r in report], ["RESOLVED"])
        self.assertEqual(cfg["custom"]["employers"][0]["employer"], "Deel")


if __name__ == "__main__":
    unittest.main(verbosity=2)
