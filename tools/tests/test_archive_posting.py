"""archive_posting: the tool that exists because a fact was read and never written.

🔴 WHAT IT COST. A requisition number, a street address and a posting date were
read off JPMorgan's own site on 2026-08-18, used to score a role, printed on a CV
and a covering letter, and never written down anywhere. `raw.json` regenerates on
every run, so within a week they existed in exactly one place: a role page citing
a source nobody could open. Every one turned out to be correct -- which is not the
point. Nothing could establish that at the moment it mattered.

🟢 WHAT THE FIRST RUN FOUND, on four sibling requisitions:

  - one page's Oracle link pointed at a DIFFERENT job, in Asset Management, at
    390 Madison Ave, New York. Applying through it would have applied to it
  - one role was at 1 Georges Dock, not Capital Dock as the page had assumed
    from a sibling requisition
  - two postings were materially older than the aggregator claimed -- one said
    13 August where the employer said 22 July
  - two pages held the SAME requisition, scored FIT 9 and FIT 13
"""
import importlib.util
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "archive_posting", os.path.join(ROOT, "tools", "radar", "archive_posting.py"))
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)

ITEM = {
    "Title": "Lead Technical Program Manager",
    "Category": "Technical Program Delivery",
    "ExternalPostedStartDate": "2026-07-17T08:31:26+00:00",
    "ExternalDescriptionStr": "<p>Shape the future of product delivery.</p>",
    "CorporateDescriptionStr": "<p>About the firm.</p>",
    "workLocation": [{"LocationName": "33416-Capital Dock",
                      "AddressLine1": "200 Capital Dock, 79 Sir John Rogerson's Quay",
                      "TownOrCity": "Dublin", "PostalCode": "D02 RK57"}],
}
URL = "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210768893/"


class TheURL(unittest.TestCase):

    def test_it_reads_host_site_and_requisition(self):
        self.assertEqual(ap.ORACLE_URL.search(URL).groups(),
                         ("jpmc.fa.oraclecloud.com", "CX_1001", "210768893"))

    def test_a_share_query_string_does_not_break_it(self):
        """The URL a user pastes comes off a Share button and carries utm tags."""
        self.assertEqual(
            ap.ORACLE_URL.search(URL + "?utm_medium=jobshare&utm_source=External+Job+Share").group(3),
            "210768893")

    def test_a_non_oracle_url_does_not_match(self):
        """🟡 The false-positive direction. A LinkedIn link must be refused, not
        silently fetched against the wrong host."""
        self.assertIsNone(ap.ORACLE_URL.search("https://www.linkedin.com/jobs/view/4442433978/"))


class TheArchive(unittest.TestCase):

    def render(self, item=None):
        return ap.render(item or ITEM, URL, "210768893", "2026-08-27")[0]

    def test_it_carries_the_three_facts_an_aggregator_does_not(self):
        """🔴 The requisition id, the employer's own posted date, and the street
        address. Each of the three was wrong or missing somewhere on the first run."""
        text = self.render()
        for fact in ("210768893", "2026-07-17", "200 Capital Dock", "33416-Capital Dock", "D02 RK57"):
            self.assertIn(fact, text, fact)

    def test_it_says_the_source_is_the_employer_not_a_board(self):
        """Every other archive header in this vault carries a Legitimacy line, and
        the whole value of this one is that the date is not a board's guess."""
        text = self.render()
        self.assertIn("employer's own", text)
        self.assertIn("Source   " + URL, text)

    def test_the_html_is_stripped(self):
        self.assertNotIn("<p>", self.render())

    def test_a_posting_with_no_work_location_still_renders(self):
        """🔴 A remote or multi-site requisition returns an empty workLocation, and
        a crash there loses the whole archive over a missing address."""
        item = dict(ITEM, workLocation=[], PrimaryLocation="Dublin, Ireland")
        text = ap.render(item, URL, "210768893", "2026-08-27")[0]
        self.assertIn("Dublin, Ireland", text)

    def test_a_posting_with_no_date_says_so_rather_than_guessing(self):
        item = dict(ITEM, ExternalPostedStartDate=None)
        self.assertIn("Posted   not stated", ap.render(item, URL, "1", "2026-08-27")[0])


class TheFilename(unittest.TestCase):

    def test_a_slash_in_a_title_cannot_escape_the_postings_folder(self):
        """🔴 Titles carry slashes — "Applied AI / ML Lead". Unsanitised, that is a
        path separator and the archive lands somewhere else entirely."""
        self.assertNotIn("/", ap._safe("Applied AI / ML Lead Software Engineer"))

    def test_it_keeps_the_characters_a_real_title_needs(self):
        """🟡 The false-positive direction: sanitising must not mangle ordinary
        titles into something unrecognisable."""
        self.assertEqual(ap._safe("Director, Services Operations (AI) & Delivery"),
                         "Director, Services Operations (AI) & Delivery")


if __name__ == "__main__":
    unittest.main(verbosity=2)
