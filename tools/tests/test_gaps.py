"""gaps: the questions the wiki has already closed, and the pages that reopen them.

🔴 TWO DEFECTS, ONE MECHANISM. `not recorded` and `recorded as not held` look
identical to a search and mean opposite things. A capability was put to the user
three days after the wiki had closed it in two places, with the words "stop
asking" — because searching for EVIDENCE of it found none, which reads as
"unknown" rather than "confirmed absent".

🔴 And the near miss is worse than the miss. The user said he had never
commercialised internal tooling; the wiki holds pages about years spent selling
custom software to enterprise clients. Adjacent, and different — that software
was built to sell from the outset. Unmarked, a later pass either re-asks or
writes the stretched claim into an application.

🔴 THE TOOL GUESSED WHICH PAGES RESEMBLED A GAP, TWICE, AND BOTH WERE UNUSABLE:

    terms from the gap's TITLE     missed the only case it was built for --
                                   the page never says "commercialising"
    terms from the gap's STATUS    25 pages, because a few common words
                                   co-occur everywhere

🟢 So the table declares them. Deciding a page resembles a gap is the judgement a
person has to make; the check enforces the half that follows.
"""
import importlib.util
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("gaps", os.path.join(ROOT, "tools", "gaps.py"))
gaps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gaps)

TABLE = """# Framework

### 🔴 The standing gaps — check these at assessment

| Gap | Status | Where it has been named |
|---|---|---|
| 🔴 **Commercialising internal tooling** | **Confirmed absent 2026-08-24.** | Acme, Beta · **Looks like: [[Story]]** |
| 🔴 **Widget ownership** | **No evidence.** | Acme, Beta, Widget Corp |
"""


class Vault:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.dir, "wiki"))
        self._saved = gaps.paths.VAULT
        gaps.paths.use(self.dir)
        self.write("Role Scoring Framework", TABLE)
        return self

    def write(self, name, body):
        with open(os.path.join(self.dir, "wiki", f"{name}.md"), "w", encoding="utf-8") as fh:
            fh.write(body)

    def __exit__(self, *a):
        gaps.paths.use(self._saved)
        shutil.rmtree(self.dir, ignore_errors=True)


class TheTable(unittest.TestCase):

    def test_it_reads_the_closed_questions(self):
        with Vault():
            self.assertEqual([g["gap"] for g in gaps.gaps()],
                             ["Commercialising internal tooling", "Widget ownership"])

    def test_a_declared_near_miss_is_read_as_a_page_not_as_prose(self):
        with Vault():
            self.assertEqual(gaps.gaps()[0]["looks_like"], ["Story"])

    def test_the_declaration_is_not_counted_as_a_posting_that_demanded_it(self):
        """🔴 The two columns share a cell. Counting the near-miss link as a
        demand would push a gap over the three-posting threshold on the strength
        of somebody documenting it."""
        with Vault():
            self.assertEqual(gaps.demands(gaps.gaps()[0]["where"]), 2)
            self.assertEqual(gaps.demands(gaps.gaps()[1]["where"]), 3)


class TheNearMiss(unittest.TestCase):

    def test_a_declared_page_with_no_distinction_is_reported(self):
        with Vault() as v:
            v.write("Story", "# Story\n\nHe sold custom software to enterprise clients.\n")
            self.assertEqual([p for p, _ in gaps.undistinguished(gaps.gaps()[0])], ["Story"])

    def test_a_page_that_carries_the_distinction_passes(self):
        with Vault() as v:
            v.write("Story", "# Story\n\nHe sold custom software.\n\n"
                             "> **Adjacent, and different:** it was built to sell from the outset.\n")
            self.assertEqual(gaps.undistinguished(gaps.gaps()[0]), [])

    def test_a_declared_page_that_does_not_exist_is_reported_not_ignored(self):
        """🔴 A typo in the column would otherwise silently mean 'nothing to
        check', which is the same shape as the defect this tool exists for."""
        with Vault():
            self.assertEqual([w for _, w in gaps.undistinguished(gaps.gaps()[0])], ["no such page"])

    def test_a_gap_declaring_nothing_reports_nothing(self):
        """🟡 The false-positive direction. Most gaps have no near miss, and a
        tool that invented one for each would be the two designs this replaced."""
        with Vault():
            self.assertEqual(gaps.undistinguished(gaps.gaps()[1]), [])


class TheResolutionMustBeFindable(unittest.TestCase):
    """🟢 A resolution is phrased as a NEGATION, which is exactly what an
    evidence search misses. A status without one is unfindable by anybody looking
    for the answer rather than for the evidence."""

    def test_a_negation_counts_as_findable(self):
        for status in ("Confirmed absent 2026-08-24.", "No evidence.", "He does not hold one.",
                       "Resolved — stop asking."):
            self.assertTrue(gaps.RESOLVED.search(status), status)

    def test_a_status_with_no_resolution_word_is_not_findable(self):
        self.assertIsNone(gaps.RESOLVED.search("Under discussion with the user."))


if __name__ == "__main__":
    unittest.main(verbosity=2)
