"""outcomes: which applications were submitted and never heard about again?

🔴 THE INSTRUCTION FAILED TWICE BEFORE THIS EXISTED. `SCHEMA.md` said "record
what happened to every application" -- across seven applications and six weeks,
one outcome was recorded. It was re-shipped as a step inside `/career-lint`,
which is still an instruction, and that skill calls it "the check most likely to
be skipped, because nothing triggers it".

Nothing inside the system happens when an employer replies, or fails to. Every
other operation has a trigger; an outcome arrives in somebody's inbox. This is
the trigger.

Most of the tests below are false-positive tests. Both of the ones marked as
"found for real" were hit on the first run against a live vault -- in opposite
directions, in the same file, within a minute of each other.
"""
import datetime
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("outcomes", os.path.join(ROOT, "tools", "outcomes.py"))
oc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oc)

TODAY = datetime.date(2026, 8, 27)
HEAD = "| Role | Status |\n|---|---|\n"


class Wiki:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        return self

    def page(self, name, body):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
            fh.write(body)

    def review(self):
        return oc.review(self.dir, today=TODAY)

    def run(self):
        buf, argv = io.StringIO(), sys.argv
        sys.argv = ["outcomes.py", "--wiki", self.dir]
        try:
            with redirect_stdout(buf):
                code = oc.main()
        finally:
            sys.argv = argv
        return code, buf.getvalue()

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)


class TheFalsePositives(unittest.TestCase):
    """🔴 Tested first, because a check that nags about settled applications is
    one that gets muted -- and muting this one restores the original failure."""

    def test_a_recent_submission_says_nothing(self):
        with Wiki() as w:
            w.page("t.md", HEAD + "| [[Role A\\|A]] | 🟢 **Submitted 2026-08-24** |\n")
            self.assertEqual(w.review(), ([], [], []))
            code, out = w.run()
            self.assertEqual(code, 0)
            self.assertIn("Nothing owed", out)

    def test_a_column_header_is_not_a_status(self):
        """Found for real: a table header reading "Submitted with" was counted as
        an application awaiting a reply."""
        with Wiki() as w:
            w.page("t.md", "| Role | Submitted with | Next |\n|---|---|---|\n")
            self.assertEqual(w.review(), ([], [], []))

    def test_prose_mentioning_the_word_is_not_a_status(self):
        """Found for real, on a CV page: "**Submitted — cannot be changed**" was
        about a document, not an application, and the application it sat beside
        had already been rejected."""
        with Wiki() as w:
            w.page("CV.md", HEAD + "| [[Role A\\|A]] | **Submitted — cannot be changed** |\n")
            self.assertEqual(w.review(), ([], [], []))

    def test_a_settled_application_is_never_chased(self):
        for settled in ("🔴 **Rejected by employer 2026-08-22**", "**Withdrew**",
                        "🔴 **Declined 2026-08-24**", "**Closed**", "🔴 **Vetoed**"):
            with Wiki() as w:
                w.page("t.md", HEAD + f"| [[Role A\\|A]] | Submitted 2026-01-01 | {settled} |\n")
                self.assertEqual(w.review(), ([], [], []), settled)

    def test_a_row_with_no_role_page_behind_it_is_not_an_application(self):
        with Wiki() as w:
            w.page("t.md", HEAD + "| Some note | Submitted 2026-01-01 |\n")
            self.assertEqual(w.review(), ([], [], []))


class TheCatchingCases(unittest.TestCase):

    def test_over_seven_days_is_asked_about(self):
        with Wiki() as w:
            w.page("t.md", HEAD + "| [[Osborne Role\\|Osborne]] | 🟢 **Submitted 2026-08-13** |\n")
            ask, record, undateable = w.review()
            self.assertEqual([(n, d) for n, d, _ in ask], [("Osborne", 14)])
            self.assertEqual((record, undateable), ([], []))

    def test_a_note_containing_a_vocabulary_word_does_not_settle_a_live_row(self):
        """🔴 FOUND FOR REAL, and it is the worse of the two directions.

        The word "closed" appeared in the prose of a note -- "the posting closed
        before..." -- on a row whose status cell said Submitted. Matching the
        vocabulary anywhere on the line swallowed a live application that was 14
        days unanswered: the exact case this tool exists to surface, hidden by
        the tool itself.
        """
        with Wiki() as w:
            w.page("t.md", HEAD + "| [[Osborne Role\\|Osborne]] | 🟢 **Submitted 2026-08-13** | "
                                  "the earlier posting closed before applying, and they declined "
                                  "to say why |\n")
            ask, _, _ = w.review()
            self.assertEqual([n for n, _, _ in ask], ["Osborne"])

    def test_over_twenty_one_days_becomes_record_an_outcome(self):
        with Wiki() as w:
            w.page("t.md", HEAD + "| [[Role A\\|A]] | **Submitted 2026-07-20** |\n")
            ask, record, _ = w.review()
            self.assertEqual(ask, [])
            self.assertEqual([n for n, _, _ in record], ["A"])
            _, out = w.run()
            self.assertIn("no response", out)

    def test_a_submitted_row_with_no_date_is_reported_separately(self):
        """🔴 The quietest failure. Without a date the application can never
        cross either threshold, so it would never be chased however long it went
        unanswered -- and the table looks complete."""
        with Wiki() as w:
            w.page("t.md", HEAD + "| [[JPMC Role\\|JPMorganChase]] | 🟢 **Submitted** |\n")
            ask, record, undateable = w.review()
            self.assertEqual((ask, record), ([], []))
            self.assertEqual([n for n, _, _ in undateable], ["JPMorganChase"])
            code, out = w.run()
            self.assertEqual(code, 1)
            self.assertIn("NO DATE", out)

    def test_one_application_in_two_tables_is_counted_once(self):
        """The same application is listed under different display names. The
        wiki-link TARGET is what is stable between them."""
        with Wiki() as w:
            w.page("a.md", HEAD + "| [[Stripe TPM Role\\|Stripe]] | 🟢 **Submitted 2026-08-01** |\n")
            w.page("b.md", HEAD + "| [[Stripe TPM Role\\|Stripe — TPM (Risk)]] | 🟢 **Submitted** |\n")
            ask, record, undateable = w.review()
            self.assertEqual(undateable, [], "the undated duplicate hid the dated row")
            self.assertEqual(len(record), 1)

    def test_a_malformed_date_does_not_crash_the_run(self):
        with Wiki() as w:
            w.page("t.md", HEAD + "| [[Role A\\|A]] | Submitted 2026-13-45 |\n")
            code, _ = w.run()
            self.assertEqual(code, 1)


class TheRealVault(unittest.TestCase):

    def test_it_runs_against_whatever_is_there(self):
        """No assertion on the contents -- this vault is the user's and changes
        daily. It must not crash, and must not report a wiki that has no pages."""
        with Wiki() as w:
            code, out = w.run()
            self.assertIn(code, (0, 1))
            self.assertTrue(out.strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
