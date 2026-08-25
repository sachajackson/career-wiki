"""known: the three-way answer to "does the wiki already know this?"

Every case here is drawn from a real failure. An agent searched for evidence of
a fact, found none, and told the user it was not recorded -- three times in one
session, and every time the answer was in the wiki, written as a negation or
under a heading the search did not match.

The fixtures are deliberately about "the applicant" and nobody in particular.
known.py matches on the shape of a sentence -- "resolved:", "never", "no budget"
-- and never on its subject, so a placeholder subject tests exactly as hard as a
real one and cannot be read back as somebody's actual situation.
"""
import importlib.util, os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWN = os.path.join(ROOT, "tools", "known.py")

spec = importlib.util.spec_from_file_location("known", KNOWN)
known = importlib.util.module_from_spec(spec)
spec.loader.exec_module(known)

FM = "---\ntype: topic\ntitle: P\n---\n\n"


class Wiki:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        return self

    def add(self, name, body):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
            fh.write(FM + body + "\n")

    def verdict(self, term):
        p = subprocess.run([sys.executable, KNOWN, term, "--wiki", self.dir],
                           capture_output=True, text=True)
        return p.stdout.split("-> ")[1].split("\n")[0].strip(), p.stdout

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)


class TheThreeRealFailures(unittest.TestCase):
    def test_stop_asking_is_settled(self):
        """The page said 'stop asking'. It was asked again six days later."""
        with Wiki() as w:
            w.add("A.md", "Two consequences: **stop asking**, and treat budget ownership as a gap.")
            self.assertEqual(w.verdict("budget")[0], "SETTLED")

    def test_a_recorded_fact_is_present_not_missing(self):
        """'Your work pattern isn't recorded' -- it had been for three weeks."""
        with Wiki() as w:
            w.add("A.md", "Confirmed by the applicant: hybrid at first, fully remote since.")
            self.assertEqual(w.verdict("fully remote")[0], "PRESENT")

    def test_a_fact_filed_under_another_word_is_still_found(self):
        """The outcome was logged under a different prefix, so a search missed it."""
        with Wiki() as w:
            w.add("log.md", "## [2026-08-22] data | the rejection came four days after submitting")
            self.assertEqual(w.verdict("rejection")[0], "PRESENT")


class Verdicts(unittest.TestCase):
    def test_nothing_at_all_is_safe_to_ask(self):
        with Wiki() as w:
            w.add("A.md", "Nothing relevant here.")
            self.assertEqual(w.verdict("scuba diving")[0], "NOT FOUND")

    def test_only_negatives_is_an_established_absence(self):
        with Wiki() as w:
            w.add("A.md", "The applicant has never held a professional certification in this.")
            self.assertEqual(w.verdict("certification")[0], "NEGATIVE ONLY")

    def test_struck_through_counts_as_settled(self):
        with Wiki() as w:
            w.add("A.md", "- ~~Does the applicant own a budget?~~ No.")
            self.assertEqual(w.verdict("budget")[0], "SETTLED")

    def test_settled_beats_present_when_both_appear(self):
        """A decision outranks loose mentions -- otherwise chatter buries the answer."""
        with Wiki() as w:
            w.add("A.md", "The budget was discussed at length and it came up again.")
            w.add("B.md", "Resolved: the applicant holds no budget.")
            self.assertEqual(w.verdict("budget")[0], "SETTLED")


class Matching(unittest.TestCase):
    def test_plurals_match(self):
        with Wiki() as w:
            w.add("A.md", "Managing delivery risks, dependencies and budgets.")
            self.assertEqual(w.verdict("budget")[0], "PRESENT")

    def test_case_insensitive(self):
        with Wiki() as w:
            w.add("A.md", "BUDGET ownership sits with the director.")
            self.assertEqual(w.verdict("budget")[0], "PRESENT")

    def test_frontmatter_is_not_searched(self):
        """A tag is not a statement, and matching one would report false presence."""
        with Wiki() as w:
            with open(os.path.join(w.dir, "A.md"), "w", encoding="utf-8") as fh:
                fh.write("---\ntype: topic\ntags: [budget]\n---\n\nNothing about it in the body.\n")
            self.assertEqual(w.verdict("budget")[0], "NOT FOUND")


class TheOutputIsTheEvidence(unittest.TestCase):
    def test_it_prints_the_lines_it_judged_on(self):
        """The verdict is a summary. If the lines are not shown it cannot be checked."""
        with Wiki() as w:
            w.add("A.md", "Resolved: the applicant holds no budget, so the figure does not exist.")
            _, out = w.verdict("budget")
            self.assertIn("the applicant holds no budget", out)
            self.assertIn("THE LINES ARE THE EVIDENCE", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
