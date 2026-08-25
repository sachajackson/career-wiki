"""refresh: re-read one archived posting and say what has changed.

The premise this started from turned out to be wrong, and measuring it is what
found that. The radar was said to fetch a description for everything surviving
the filter on every run. It does not: seen.json is consulted at FETCH time, so a
role found last week never reaches the description fetch again. Run the radar
twice against the same board and the second run reads zero descriptions and
produces an empty shortlist.

So the expensive pass was already bounded, and the real failure was the other
one the design warned about: NOTHING IS EVER RE-READ. A description changes
after posting -- a band added, a requirement softened, the role withdrawn -- and
none of it is ever noticed.

The second reason is stronger than the first. A listing censors the posting date
and the detail endpoint does not: one real posting's listing said "Posted 30+
Days Ago" while its detail gave a start date ten days earlier, and 9 of 20
postings from that tenant arrived capped. Age is the best ghost-job predictor,
so re-reading buys the one signal the shortlist could not see.
"""
import importlib.util, io, os, sys, tempfile, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
spec = importlib.util.spec_from_file_location("refresh", os.path.join(ROOT, "tools", "radar", "refresh.py"))
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)

WD = "https://wd1.myworkdaysite.com/recruiting/<tenant>/<site>/job/<city>/Head-of-Delivery_R-100"
ORC = "https://<pod>.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/<site>/job/336508"


def archive(url=WD, posted="2026-07-26", body="The original description. " * 30):
    return (f"<Employer> -- Head of Delivery\n"
            f"Archived 2026-08-25 by the radar\n"
            f"Posted   {posted}\n"
            f"Location <city>\n"
            f"Pay      not stated\n"
            f"Source   {url}\n" + "=" * 72 + f"\n\n{body}\n")


class UrlsBackIntoCoordinates(unittest.TestCase):
    """Both Workday hosting styles and Oracle, from the public URL alone.

    The archive keeps a URL, not adapter coordinates -- raw.json is regenerated
    every run and holds only that run's new roles, so by the time anyone wants
    to re-read, the row is gone.
    """

    def test_the_shared_host_workday_form(self):
        ats, row = refresh.coords(WD)
        self.assertEqual(ats, "workday")
        self.assertEqual(row["_wd"][:3], ["wd1.myworkdaysite.com", "<tenant>", "<site>"])

    def test_the_per_tenant_workday_form(self):
        ats, row = refresh.coords(
            "https://<tenant>.wd1.myworkdayjobs.com/Global/job/<city>/Head_R-1")
        self.assertEqual(ats, "workday")
        self.assertEqual(row["_wd"][1:3], ["<tenant>", "Global"])

    def test_oracle(self):
        ats, row = refresh.coords(ORC)
        self.assertEqual(ats, "oracle")
        self.assertEqual(row["_or"][1:], ["<site>", "336508"])

    def test_an_aggregator_url_says_so_rather_than_guessing(self):
        ats, why = refresh.coords("https://www.linkedin.com/jobs/view/123/")
        self.assertIsNone(ats)
        self.assertIn("can re-read", why)

    def test_the_requisition_comes_off_the_url_and_is_never_faked(self):
        """Passing a placeholder would silently disable the missing-requisition
        check and report a clean result it never ran."""
        self.assertEqual(refresh.requisition(WD), "R-100")
        self.assertEqual(refresh.requisition(ORC), "336508")
        self.assertEqual(refresh.requisition("https://www.linkedin.com/jobs/view/1/"), "")


class WhatChanged(unittest.TestCase):

    def test_an_unreadable_posting_is_the_loudest_finding(self):
        """Filled, withdrawn or moved -- and applying from the archived copy
        after that is the failure worth preventing."""
        notes = refresh.compare(refresh.parse_archive(archive()), "", "")
        self.assertIn("GONE", notes[0])

    def test_an_unchanged_posting_says_so_plainly(self):
        a = refresh.parse_archive(archive())
        notes = refresh.compare(a, a["body"], "2026-07-26")
        self.assertIn("unchanged", notes[0])

    def test_whitespace_is_not_a_change(self):
        """Re-fetched HTML re-wraps. Reporting that as a change is the noise
        that gets a check switched off."""
        a = refresh.parse_archive(archive())
        notes = refresh.compare(a, a["body"].replace(" ", "\n  "), "2026-07-26")
        self.assertIn("unchanged", notes[0])

    def test_a_changed_description_reports_the_direction(self):
        a = refresh.parse_archive(archive())
        notes = refresh.compare(a, a["body"] + " And a new paragraph.", "2026-07-26")
        self.assertIn("CHANGED", notes[0])
        self.assertIn("+", notes[0])

    def test_a_salary_appearing_is_called_out(self):
        """The design's own example of a description changing after posting."""
        a = refresh.parse_archive(archive())
        notes = refresh.compare(a, a["body"] + " Salary £95,000.", "2026-07-26")
        self.assertTrue(any("salary figure has appeared" in n for n in notes))

    def test_a_salary_disappearing_is_called_out_too(self):
        a = refresh.parse_archive(archive(body="Pay is £95,000 a year. " * 20))
        notes = refresh.compare(a, "Pay is competitive. " * 20, "2026-07-26")
        self.assertTrue(any("has gone" in n for n in notes))


class TheCensoredDate(unittest.TestCase):
    """The stronger of the two reasons to re-read.

    A listing that stops counting at 30 days and a detail endpoint that does not
    are the same source disagreeing with itself, and the shortlist only ever saw
    the censored half.
    """

    def test_an_older_true_date_is_reported_as_a_correction(self):
        a = refresh.parse_archive(archive(posted="2026-07-26"))
        notes = refresh.compare(a, a["body"], "2026-07-16")
        self.assertTrue(any("POSTED 2026-07-16" in n for n in notes))
        self.assertTrue(any("older than" in n for n in notes))
        self.assertTrue(any("censor" in n for n in notes))

    def test_a_newer_date_is_reported_without_the_censorship_claim(self):
        """A repost genuinely has a newer date. Calling that censorship would
        be asserting something that is not true of it."""
        a = refresh.parse_archive(archive(posted="2026-07-16"))
        notes = refresh.compare(a, a["body"], "2026-08-20")
        self.assertTrue(any("2026-08-20" in n for n in notes))
        self.assertFalse(any("censor" in n for n in notes))

    def test_the_same_date_is_not_mentioned_at_all(self):
        a = refresh.parse_archive(archive(posted="2026-07-26"))
        notes = refresh.compare(a, a["body"], "2026-07-26")
        self.assertFalse(any("POSTED" in n for n in notes))


class TheLegitimacyRecompute(unittest.TestCase):
    """Re-reading recomputes the legitimacy line, and must do it on real inputs.

    Passing a placeholder requisition silently disables the missing-requisition
    check and reports a clean result it never ran -- which is the same shape as
    every other "looks configured and does nothing" defect in this repo.
    """

    def _refresh_with(self, url, posted="2026-08-20"):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "one.txt")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(archive(url=url))
        saved = refresh.live
        refresh.live = lambda ats, row: ("The description. " * 40, posted)
        try:
            return refresh.refresh(p)[1]
        finally:
            refresh.live = saved

    def test_a_url_with_no_requisition_is_flagged_not_excused(self):
        notes = self._refresh_with(
            "https://wd1.myworkdaysite.com/recruiting/<tenant>/<site>/job/<city>/Head-of-Delivery")
        self.assertTrue(any("no requisition number" in n for n in notes), notes)

    def test_a_url_carrying_one_is_not_flagged(self):
        notes = self._refresh_with(WD)
        self.assertFalse(any("no requisition number" in n for n in notes), notes)

    def test_the_recompute_uses_the_detail_date_not_the_archived_one(self):
        """The archived date is the censored one. Recomputing against it would
        reproduce exactly the blindness this tool exists to fix."""
        notes = self._refresh_with(WD, posted="2025-01-01")
        self.assertTrue(any("open a long time" in n for n in notes), notes)


class TheArchiveIsEvidence(unittest.TestCase):

    def test_re_reading_never_touches_the_archived_file(self):
        """It is the only record of what the assessment was based on, and a
        later fetch can return an edited posting -- or a 404 page, which would
        replace the evidence with nothing."""
        d = tempfile.mkdtemp()
        p = os.path.join(d, "one.txt")
        text = archive(url="https://www.linkedin.com/jobs/view/1/")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        refresh.refresh(p)
        with open(p, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), text)

    def test_the_report_says_the_archive_was_not_updated(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "one.txt"), "w", encoding="utf-8") as fh:
            fh.write(archive(url="https://www.linkedin.com/jobs/view/1/"))
        argv = sys.argv
        sys.argv = ["refresh", "--all", d]
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                refresh.main()
        finally:
            sys.argv = argv
        self.assertIn("archive is NOT updated", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
