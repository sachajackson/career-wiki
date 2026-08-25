"""legitimacy: is this a real vacancy — reported apart from the score, always.

Between a fifth and a third of live listings are estimated to be ghost jobs. The
design decision under test is that none of this touches the fit score: a fake
posting is not a low-scoring role, it is not a role, and folding it into a number
would let a strong-but-fake posting outrank a real mediocre one.

The case that mattered most was found by measuring rather than reasoning. The
first version compared every posting's age against a 45-day threshold. Workday
STOPS COUNTING AT 30 -- and prints bare "Posted 30 Days Ago" as often as it
prints "30+" -- so a year-old requisition and a thirty-day-old one arrive as the
same string, and the threshold could never fire on the source where age is
hardest to see. Verified across two live tenants: 13 distinct posted strings,
highest number 30, nothing above it.

The other thing measured before shipping was the false-positive rate, because a
check that cries wolf gets switched off. On 240 live postings it flags 7% of
Workday and 0% of Oracle, and every one of those is the source refusing to say
how old the posting is.
"""
import datetime, importlib.util, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
import legitimacy as L                                            # noqa: E402

TODAY = datetime.date(2026, 8, 25)


def ago(n):
    return (TODAY - datetime.timedelta(days=n)).isoformat()


def row(**kw):
    r = {"id": "x1", "title": "Head of Delivery", "company": "<Employer>",
         "source": "oracle", "requisition": "R-100", "date": ago(3)}
    r.update(kw)
    return r


class NothingWrongLooksLikeNothingWrong(unittest.TestCase):
    """Measured first, because a check that cries wolf gets switched off."""

    def test_a_fresh_posting_from_an_employers_own_ats_is_clean(self):
        self.assertEqual(L.concerns(row(), today=TODAY), [])

    def test_an_aggregator_posting_is_not_suspect_for_being_one(self):
        """Most of the corpus is LinkedIn. Flagging every one is the noise that
        gets the whole block ignored -- provenance is reported separately."""
        self.assertEqual(L.concerns(row(source="linkedin", requisition=""), today=TODAY), [])
        self.assertIn("aggregator", L.provenance(row(source="linkedin")))

    def test_a_board_without_requisition_numbers_is_not_flagged_for_lacking_one(self):
        """Greenhouse and Lever do not issue them, so absence says nothing."""
        for src in ("greenhouse", "lever", "custom"):
            self.assertEqual(L.concerns(row(source=src, requisition=""), today=TODAY), [], src)

    def test_just_under_the_threshold_says_nothing(self):
        self.assertEqual(L.concerns(row(date=ago(L.AGEING_DAYS - 1)), today=TODAY), [])


class TheCappedDate(unittest.TestCase):
    """The defect measuring found, and the reason this is not a threshold check.

    Workday stops counting at 30. Compared against a 45-day threshold the check
    can never fire there -- on the source where the posting could be a year old
    and nothing on the page would say so.
    """

    def test_a_floor_date_is_a_finding_even_though_it_is_under_the_threshold(self):
        r = row(source="workday", date=ago(30), date_is_floor=True)
        self.assertLess(30, L.AGEING_DAYS)          # would never trip the threshold
        c = L.concerns(r, today=TODAY)
        self.assertEqual(len(c), 1)
        self.assertIn("age unknown", c[0])
        self.assertIn("could be far older", c[0])

    def test_a_floor_is_never_reported_as_a_measured_age(self):
        """"30 days old" and "at least 30 days old" are different claims, and
        the first one is the aggregator re-dating problem in our own output."""
        c = L.concerns(row(source="workday", date=ago(30), date_is_floor=True), today=TODAY)
        self.assertNotIn("30 days old", c[0])


class ThingsWorthSaying(unittest.TestCase):

    def test_an_ageing_posting(self):
        c = L.concerns(row(date=ago(60)), today=TODAY)
        self.assertEqual(len(c), 1)
        self.assertIn("ageing", c[0])
        self.assertIn("60 days", c[0])

    def test_a_posting_open_a_long_time_is_said_more_strongly(self):
        c = L.concerns(row(date=ago(L.LONG_OPEN_DAYS + 5)), today=TODAY)
        self.assertIn("open a long time", c[0])

    def test_an_aggregators_date_is_marked_unconfirmed(self):
        """An aggregator showed a ten-week-old requisition as posted yesterday."""
        c = L.concerns(row(source="linkedin", requisition="", date=ago(60)), today=TODAY)
        self.assertIn("unconfirmed", c[0])
        self.assertNotIn("unconfirmed", L.concerns(row(date=ago(60)), today=TODAY)[0])

    def test_a_missing_requisition_where_the_ats_issues_one(self):
        for src in ("workday", "oracle"):
            c = L.concerns(row(source=src, requisition=""), today=TODAY)
            self.assertEqual(len(c), 1, src)
            self.assertIn("no requisition number", c[0])


class Reposts(unittest.TestCase):
    """Matched on requisition number only, and deliberately not on title.

    An employer legitimately running the same role in four cities would fire a
    title match every time, which is the false positive that would get this
    switched off. A requisition number is exact.
    """

    def test_the_same_requisition_seen_before(self):
        history = {"old": {"requisition": "R-100", "posted": "2026-03-01"}}
        c = L.concerns(row(), history, today=TODAY)
        self.assertEqual(len(c), 1)
        self.assertIn("seen before", c[0])
        self.assertIn("2026-03-01", c[0])

    def test_the_same_role_in_four_cities_is_not_a_repost(self):
        history = {f"c{i}": {"requisition": f"R-20{i}", "posted": "2026-03-01",
                             "title": "Head of Delivery", "company": "<Employer>"}
                   for i in range(4)}
        self.assertEqual(L.concerns(row(), history, today=TODAY), [])

    def test_its_own_record_is_not_a_previous_posting(self):
        history = {"x1": {"requisition": "R-100", "posted": "2026-03-01"}}
        self.assertEqual(L.concerns(row(id="x1"), history, today=TODAY), [])

    def test_a_history_without_the_new_fields_degrades_quietly(self):
        """seen.json entries written before this shipped have no requisition."""
        history = {"old": {"title": "Head of Delivery", "company": "<Employer>",
                           "first_seen": "2026-01-01"}}
        self.assertEqual(L.concerns(row(), history, today=TODAY), [])


class ItNeverBecomesAScore(unittest.TestCase):
    """The whole design decision, pinned. A percentage is a score by another
    name and would be averaged, compared and ranked within a week."""

    def test_the_line_carries_no_percentage_or_ratio(self):
        for r in (row(), row(date=ago(200)), row(source="workday", date=ago(30),
                                                 date_is_floor=True)):
            out = L.line(r, today=TODAY)
            self.assertNotIn("%", out)
            self.assertNotRegex(out, r"\b\d+\s*/\s*\d+\b")
            self.assertNotRegex(out, r"(?i)\b(score|rating|confidence)\b")

    def test_a_clean_result_is_not_presented_as_verified(self):
        """Most of what makes a posting fake is invisible from the posting."""
        out = L.line(row(), today=TODAY)
        self.assertIn("nothing flagged", out)
        self.assertNotRegex(out, r"(?i)\b(genuine|verified|legitimate|real)\b")

    def test_the_line_counts_concerns_and_names_them(self):
        out = L.line(row(source="workday", requisition="", date=ago(120)), today=TODAY)
        self.assertIn("2 concerns", out)
        self.assertIn("no requisition number", out)


if __name__ == "__main__":
    unittest.main()
