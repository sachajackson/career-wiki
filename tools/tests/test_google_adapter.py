"""google: an employer whose careers site is HTML, and who publishes no dates.

Every fixture below is trimmed from the real page fetched on 2026-08-26. The
markup is Google's and will change; when it does, `probe()` is what says so, and
`test_a_page_that_answers_but_parses_nothing_is_a_loud_failure` is the check that
keeps that promise.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar"))
from adapters import google  # noqa: E402

# One card, single location. Real markup, shortened.
ONE = (
    '<div class="Xsxa1e"><h4>Minimum qualifications</h4><ul>'
    "<li>Bachelor's degree or equivalent practical experience.</li>"
    "<li>5 years of experience managing engineering teams.</li></ul></div>"
    '<span>place</span><span class="r0wTof">Dublin, Ireland</span>'
    '<a class="WpHeLc" href="jobs/results/12345678901234567-engineering-manager-site-reliability'
    '?location=Dublin+Ireland" aria-label="Learn more about Engineering Manager, Site Reliability'
    ' Engineering, Alphanet SRE"></a>'
)

# 🔴 The regression fixture. Three spans, and Dublin is the middle one.
MULTI = (
    '<div class="Xsxa1e"><h4>Minimum qualifications</h4><ul><li>Experience.</li></ul></div>'
    '<span class="r0wTof">London, UK</span><span class="r0wTof">; Dublin, Ireland</span>'
    '<span class="BVHzed">; +2 more</span>'
    '<a href="jobs/results/78474146920440518-senior-control-systems-networking-engineer'
    '?location=Dublin+Ireland" aria-label="Learn more about Senior Control Systems Networking'
    ' Engineer, Data Center Technology Systems"></a>'
)

PAGE = f'<!doctype html><html><body><p>1 - 20 of 112 </p>{ONE}{MULTI}</body></html>'
CFG = {"google": {"locations": ["Dublin Ireland"], "pages": 3}}


class Stub:
    """Replaces the adapter's HTTP call for the duration of a test."""

    def __init__(self, pages):
        self.pages, self.urls = pages, []

    def __call__(self, url, *a, **k):
        if "page=" not in url:          # a detail fetch, not a results page
            return DETAIL
        self.urls.append(url)
        i = int(url.split("page=")[1]) - 1
        return self.pages[i] if i < len(self.pages) else ""


class TheParser(unittest.TestCase):

    def test_it_reads_id_title_location_and_body(self):
        rows = google.parse(PAGE)
        self.assertEqual(len(rows), 2)
        r = rows[0]
        self.assertEqual(r["id"], "goog-12345678901234567")
        self.assertEqual(r["company"], "Google")
        self.assertEqual(r["loc"], "Dublin, Ireland")
        self.assertIn("managing engineering teams", r["body"])
        self.assertIn("12345678901234567", r["url"])

    def test_the_title_comes_from_the_aria_label_not_the_slug(self):
        """The slug is lowercased and hyphen-flattened. It would match, and it
        would read badly everywhere a human sees it."""
        self.assertEqual(google.parse(PAGE)[0]["title"],
                         "Engineering Manager, Site Reliability Engineering, Alphanet SRE")

    def test_every_location_is_kept_not_just_one(self):
        """🔴 THE REGRESSION, and it was real before it was a test.

        A multi-site role renders London first, Dublin second, "+2 more" third.
        The first version of this adapter took the last span and produced rows
        labelled "Warsaw, Poland" and "London, UK" for roles the DUBLIN query had
        matched -- because they are also open in Dublin.

        The radar's location filter runs on this string BEFORE any description is
        read, so either end of the list drops a commutable role and nothing says
        so. Same trap the custom adapter documents for Deel's all_locations.
        """
        loc = google.parse(MULTI)[0]["loc"]
        self.assertIn("Dublin, Ireland", loc)
        self.assertIn("London, UK", loc)

    def test_hidden_locations_are_declared(self):
        """"+2 more" means the card is truncating. A truncated list that reads as
        a complete one is how a role gets judged on a place it is not in."""
        self.assertIn("+2 more", google.parse(MULTI)[0]["loc"])

    def test_no_date_is_invented(self):
        """🔴 Google publishes no posting date anywhere on the card.

        Stamping today's would make every Google role look new for ever, and the
        radar reads a date to decide whether something is worth chasing. Empty is
        the honest answer, and it is why HONOURS_DAYS is False.
        """
        for r in google.parse(PAGE):
            self.assertEqual(r["date"], "")
        self.assertFalse(google.HONOURS_DAYS)

    def test_markup_with_no_cards_yields_nothing_rather_than_guessing(self):
        self.assertEqual(google.parse("<html><body>no jobs here</body></html>"), [])


DETAIL = (
    '<html><body><script>var junk="Minimum qualifications";</script>'
    '<div><h3>Minimum qualifications:</h3><ul><li>Five years leading teams.</li></ul></div>'
    '<div class="aG5W3"><h3>About the job</h3><p>You will lead a squad of AI engineers who bridge '
    'the gap between AI products and production-grade reality.</p></div>'
    '<div class="BDNOWe"><h3>Responsibilities</h3><ul><li>Establish code standards.</li></ul></div>'
    '<footer>Google is proud to be an equal opportunity workplace. Boilerplate follows.</footer>'
    '</body></html>'
)


class TheDescription(unittest.TestCase):
    """🔴 Why the adapter fetches a second page per role.

    The results page carries only the Minimum-qualifications bullets -- about
    360 characters. Measured across 48 Google roles scored from the listing
    alone, the HIGHEST keyword tally was 4, against a MED threshold of 10. Not
    one Google role could ever have tiered, so a watched employer's roles would
    land only in the catch-all section for ever: a watch in name only.
    """

    def test_it_takes_the_whole_description_not_just_the_qualifications(self):
        body = google.describe(DETAIL)
        self.assertIn("bridge the gap", body)
        self.assertIn("Establish code standards", body)
        self.assertIn("Five years leading teams", body)

    def test_scripts_are_stripped_before_flattening(self):
        """Google inlines a lot of JavaScript. Flattening without stripping it
        first runs the description straight on into minified code, which then
        gets keyword-tallied as if it were prose."""
        self.assertNotIn("var junk", google.describe(DETAIL))

    def test_the_site_boilerplate_is_cut(self):
        self.assertNotIn("equal opportunity", google.describe(DETAIL))

    def test_an_unrecognised_page_yields_nothing_rather_than_garbage(self):
        """Returning "" leaves the listing body in place. Returning half a page
        of navigation would quietly inflate the tally instead."""
        self.assertEqual(google.describe("<html><body>Something else</body></html>"), "")
        self.assertEqual(google.describe(""), "")


class TheFetch(unittest.TestCase):

    def setUp(self):
        self._get = google.get
        self.addCleanup(lambda: setattr(google, "get", self._get))

    def test_it_filters_on_title_like_the_other_board_adapters(self):
        google.get = Stub([PAGE])
        self.assertEqual(len(google.fetch(CFG, "Engineering Manager", 7)), 1)
        self.assertEqual(google.fetch(CFG, "Veterinary Nurse", 7), [])

    def test_it_stops_on_a_short_page_instead_of_paging_forever(self):
        stub = Stub([PAGE])
        google.get = stub
        google.fetch(CFG, "Engineering Manager", 7)
        self.assertEqual(len(stub.urls), 1, "a short page means the board ended")

    def test_a_repeated_page_ends_the_walk(self):
        """Some paginated sites answer the same rows past the end. Without this
        the adapter would spin to its page cap collecting duplicates."""
        full = PAGE.replace("</body>", ONE.replace("12345678901234567", "999") * 18 + "</body>")
        stub = Stub([full, full])
        google.get = stub
        google.fetch(CFG, "Engineering Manager", 7)
        self.assertLessEqual(len(stub.urls), 2)

    def test_no_locations_configured_fetches_nothing(self):
        google.get = Stub([PAGE])
        self.assertEqual(google.fetch({"google": {}}, "Engineering Manager", 7), [])


class TheProbe(unittest.TestCase):

    def setUp(self):
        self._get = google.get
        self.addCleanup(lambda: setattr(google, "get", self._get))

    def test_an_unconfigured_source_is_not_a_failure(self):
        verdict, _ = google.probe({"google": {}})
        self.assertEqual(verdict, google.V.NOT_CONFIGURED)

    def test_a_working_page_reports_the_open_count(self):
        google.get = Stub([PAGE])
        verdict, detail = google.probe(CFG)
        self.assertEqual(verdict, google.V.OK)
        self.assertIn("112", detail)

    def test_a_page_that_answers_but_parses_nothing_is_a_loud_failure(self):
        """🔴 The failure this adapter is most likely to have, and it looks
        exactly like a quiet week.

        Google re-renders its careers site periodically. When the anchor changes
        shape the page still answers 200 with over a megabyte of HTML and the
        parser returns nothing. A silent zero here is indistinguishable from
        "Google is not hiring in Dublin", which is the worst failure this system
        can have.
        """
        google.get = Stub(["<html>" + "x" * 5000 + "</html>"])
        verdict, detail = google.probe(CFG)
        self.assertEqual(verdict, google.V.FAILED)
        self.assertIn("NO job cards parsed", detail)
        self.assertIn("google.py", detail)

    def test_an_unreachable_page_says_so(self):
        google.get = lambda *a, **k: ""
        verdict, _ = google.probe(CFG)
        self.assertEqual(verdict, google.V.FAILED)


class TheRegistration(unittest.TestCase):

    def test_it_is_wired_into_the_adapter_list(self):
        from adapters import ADAPTERS
        self.assertIs(ADAPTERS["google"], google)

    def test_the_registry_routes_the_employer_name(self):
        """The watch list says WHO to watch; the registry decides which adapter
        reaches them. Without an entry, "Google" reports as unroutable."""
        import json
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(here, "radar", "ats_registry.json"), encoding="utf-8") as fh:
            reg = json.load(fh)
        entry = [e for e in reg["employers"] if e["employer"] == "Google"]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["ats"], "google")


if __name__ == "__main__":
    unittest.main(verbosity=2)
