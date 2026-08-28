"""radar: surfacing one job that arrived from two sources, and never merging it.

🔴 WHAT HAPPENED. `same_role()` runs only against roles found in the SAME run,
and `seen` is consulted by a source-prefixed id. So one Acme Bank requisition
reached a vault as `li-4453618843` on 2026-08-26 and `or-210778716` on 2026-08-27,
was assessed twice, scored 9 and 13, and both rows sat in the scoring table until
someone re-fetched the employer's own copy and noticed.

🔴 WHY IT IS SURFACED AND NOT MERGED. Merging is the cheaper change. Measured on
6,534 real sightings before building: 318 (employer, title) pairs repeat and one
of them EIGHTEEN TIMES — eighteen real vacancies at one employer separated only
by location. Merging on title deletes seventeen jobs and reports nothing, which
radar.py already names as its worst possible failure.

🔴 AND WHY LOCATION IS REQUIRED ON BOTH SIDES. Replaying the same corpus:
treating a missing location as agreement fires on 7.6% of sightings; requiring
one on both sides fires on 0.0%. Every one of those 494 was the same artefact —
not one record in `seen` carried a location, because nothing stored it.
"""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
sys.path.insert(0, os.path.join(ROOT, "tools", "lib"))
spec = importlib.util.spec_from_file_location("radar", os.path.join(ROOT, "tools", "radar", "radar.py"))
radar = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(radar)
except SystemExit:                                    # argparse on import
    pass

SEEN = {"li-4453618843": {"title": "Director of Software Engineering",
                          "company": "Acme Bank",
                          "loc": "Dublin, County Dublin, Ireland",
                          "first_seen": "2026-08-26"}}


def row(**kw):
    base = {"id": "or-210778716", "title": "Director of Software Engineering",
            "company": "Acme Bank", "loc": "Dublin, Ireland"}
    base.update(kw)
    return base


class TheRealCase(unittest.TestCase):

    def test_the_same_job_from_two_sources_is_flagged(self):
        hits = radar.duplicate_candidates(row(), SEEN)
        self.assertEqual([h[0] for h in hits], ["li-4453618843"])

    def test_the_location_written_two_ways_still_matches(self):
        """🟢 SUBSET, not equality. "Dublin, Ireland" folds into "Dublin, County
        Dublin, Ireland" the same way same_role() folds them."""
        self.assertTrue(radar.duplicate_candidates(row(loc="Dublin"), SEEN))

    def test_a_requisition_number_in_the_title_does_not_hide_it(self):
        self.assertTrue(radar.duplicate_candidates(
            row(title="Director of Software Engineering R-281578"), SEEN))


class TheThingsItMustNotDo(unittest.TestCase):
    """🔴 Every test here is a real vacancy that must survive."""

    def test_a_different_city_is_two_roles(self):
        """The eighteen-vacancies case. Same employer, same title, different
        place — and location is the only thing that says so."""
        self.assertEqual(radar.duplicate_candidates(row(loc="New York, NY"), SEEN), [])

    def test_lyon_and_nice_do_not_match_on_france(self):
        """🔴 Token INTERSECTION would merge them, because every location in a
        country carries the country's name. The same bug same_role() documents."""
        seen = {"li-1": dict(SEEN["li-4453618843"], loc="Lyon, France")}
        self.assertEqual(radar.duplicate_candidates(row(loc="Nice, France"), seen), [])

    def test_a_different_employer_is_not_a_duplicate(self):
        self.assertEqual(radar.duplicate_candidates(row(company="Northwind"), SEEN), [])

    def test_a_different_title_is_not_a_duplicate(self):
        self.assertEqual(radar.duplicate_candidates(row(title="Product Delivery Manager"), SEEN), [])

    def test_a_role_does_not_match_itself(self):
        self.assertEqual(radar.duplicate_candidates(row(id="li-4453618843"), SEEN), [])


class TheQuietDayOne(unittest.TestCase):
    """🔴 A section that fires on 7.6% of a sweep is a section nobody reads."""

    def test_an_old_record_with_no_location_does_not_participate(self):
        old = {"li-1": {"title": "Director of Software Engineering",
                        "company": "Acme Bank", "first_seen": "2026-08-26"}}
        self.assertEqual(radar.duplicate_candidates(row(), old), [])

    def test_a_new_row_with_no_location_does_not_either(self):
        self.assertEqual(radar.duplicate_candidates(row(loc=""), SEEN), [])

    def test_a_row_with_no_employer_does_not_match_everything(self):
        """🔴 Empty normalises to empty, and without this an unnamed agency row
        would pair with every other unnamed row in the corpus."""
        blank = {"li-1": {"title": "", "company": "", "loc": "Dublin", "first_seen": "x"}}
        self.assertEqual(radar.duplicate_candidates(row(company="", title=""), blank), [])


class TheRecordThatMakesItPossible(unittest.TestCase):

    def test_radar_stores_the_location_it_needs_next_run(self):
        """🔴 The field whose absence made this undetectable. Not one of 6,534
        records carried it."""
        with open(os.path.join(ROOT, "tools", "radar", "radar.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn('"loc": c.get("loc", "")', src)

    def test_the_shortlist_says_nothing_was_dropped(self):
        """🔴 The whole promise of this section. If the wording ever stops saying
        so, a reader will assume the radar removed something."""
        with open(os.path.join(ROOT, "tools", "radar", "radar.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("Nothing has been dropped and nothing has been merged", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
