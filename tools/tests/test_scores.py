"""scores: the arithmetic of a score, and the four ways checking it cried wolf.

🔴 THE POINT OF THIS FILE. On its first run this tool reported 17 faults where
there was 1. Every false one came from the same class of mistake: assuming a
score cell contains a bare number.

This vault's own convention puts a status marker in it. The real cell reads
`🔴 **7**`, and the label beside it reads `🟢 **FIT**`. A parser anchored on a
digit matched neither, walked on to the next numeric-looking column, and read
SEC as FIT -- which is why every spurious fault reported the number 4.

A check that reports 17 faults on a healthy vault gets switched off in a week,
so most of what follows is the false-positive case, not the true one.
"""
import importlib.util
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("scores", os.path.join(ROOT, "tools", "scores.py"))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

HEAD = "| Role | N·D·E | **FIT** | **LIFE** | **SEC** | REQS | PAY | **Status** | Posting | Note |\n|---|---|---|---|---|---|---|---|---|---|\n"


class Vault:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        for d in ("wiki", "roles", "postings"):
            os.makedirs(os.path.join(self.dir, d))
        self._saved = sc.paths.VAULT
        sc.paths.use(self.dir)
        sc.quotes.paths.use(self.dir)
        self.table([])
        return self

    def table(self, rows):
        self._w("wiki/Role Scoring Framework.md", "# Framework\n\n" + HEAD + "\n".join(rows) + "\n")

    def role(self, name, body):
        self._w(f"roles/{name}.md", body)

    def posting(self, name, body="Some posting text.\nhttps://www.linkedin.com/jobs/view/4456075351/\n"):
        self._w(f"postings/{name}.txt", body)

    def _w(self, rel, text):
        with open(os.path.join(self.dir, rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def __exit__(self, *a):
        sc.paths.use(self._saved)
        sc.quotes.paths.use(self._saved)
        shutil.rmtree(self.dir, ignore_errors=True)


def block(nde, fit, life=3, sec=3, extra=""):
    return (f"# A role\n\n| | |\n|---|---|\n| **N·D·E** | **{nde}** |\n"
            f"| **FIT** | **{fit}/15** |\n| **LIFE** | **{life}** |\n| **SEC** | **{sec}** |\n{extra}")


class TheArithmetic(unittest.TestCase):
    """🟢 The true positive, and it was real: a role scored 4·4·2 carried a FIT
    of 9 on the page, in the table, and under a heading reading 'What holds it
    at 9'. Every component was argued for in prose; the total was a slip."""

    def test_a_total_that_does_not_add_up_is_caught(self):
        with Vault() as v:
            v.role("Acme", block("4·4·2", 9))
            faults, _, _ = sc.audit()
            self.assertEqual(len(faults), 1)
            self.assertIn("= 10, but FIT reads 9", faults[0][2])

    def test_a_correct_total_is_not(self):
        with Vault() as v:
            v.role("Acme", block("4·4·2", 10))
            self.assertEqual(sc.audit()[0], [])


class TheMarkersInsideCells(unittest.TestCase):
    """🔴 ALL FOURTEEN of the first run's spurious faults were this."""

    def test_a_marker_before_the_value_does_not_break_it(self):
        with Vault() as v:
            v.role("Acme", "# A role\n\n| | |\n|---|---|\n| **N·D·E** | **3·2·2** |\n"
                           "| **FIT** | 🔴 **7/15** |\n")
            self.assertEqual(sc.audit()[0], [])

    def test_a_marker_before_the_LABEL_does_not_break_it_either(self):
        """The marker goes in front of the label as often as the value, and the
        pages that flag their own score are disproportionately the interesting
        ones -- so missing them misses the roles that matter most."""
        with Vault() as v:
            v.role("Acme", "# A role\n\n| | |\n|---|---|\n| **N·D·E** | **5·3·4** |\n"
                           "| 🟢 **FIT** | **12/15** |\n")
            self.assertEqual(sc.audit()[0], [])

    def test_a_LIFE_cell_carrying_its_reason_still_parses(self):
        """`🔴 **1** — "primarily in the office"`. Requiring the whole cell to be
        a number drops these; searching anywhere in it picks a number out of the
        quoted reason. The number is at the START."""
        with Vault() as v:
            v.role("Acme", block("3·2·2", 7, life='🔴 **1** — *"**primarily in the office**"*'))
            self.assertEqual(sc.audit()[0], [])
            self.assertEqual(sc._page_dim(open(os.path.join(v.dir, "roles/Acme.md"),
                                               encoding="utf-8").read(), "LIFE"), 1)


class TheClusterPages(unittest.TestCase):
    """🔴 Three spurious faults. A cluster page is a TABLE OF SEVERAL ROLES, each
    with its own N·D·E and FIT on one line. Taking the first `·` on the page and
    the first FIT-shaped number pairs two different roles' scores."""

    CLUSTER = ("# Three roles\n\n| Role | N·D·E | FIT | LIFE |\n|---|---|---|---|\n"
               "| **Alexion** — a role | **4·3·4** | **11** | 🔴 **1–2** |\n"
               "| **JPMorganChase** — another | **4·2·4** | **10** | 🟡 TBC |\n"
               "| **PwC** — a third | **3·2·3** | **8** | 🔴 **2** |\n")

    def test_a_cluster_page_whose_rows_all_add_up_is_clean(self):
        with Vault() as v:
            v.role("Cluster", self.CLUSTER)
            self.assertEqual(sc.audit()[0], [])

    def test_a_single_bad_row_inside_a_cluster_is_still_caught(self):
        with Vault() as v:
            v.role("Cluster", self.CLUSTER.replace("| **4·2·4** | **10** |", "| **4·2·4** | **9** |"))
            faults, _, _ = sc.audit()
            self.assertEqual(len(faults), 1)
            self.assertIn("= 10, but FIT reads 9", faults[0][2])

    def test_a_cluster_is_never_compared_against_its_table_row(self):
        """The table's row for a cluster is one of the roles inside it, so
        page-versus-table agreement is meaningless there."""
        with Vault() as v:
            v.role("Cluster", self.CLUSTER)
            v.table(["| [[Cluster\\|X]] — three roles | 4·3·4 | **11** | 1 | 2 |"])
            self.assertEqual(sc.audit()[0], [])


class TheAgreement(unittest.TestCase):
    """🟢 The other true positive, also real: one page had been rescored 13 -> 12
    and said so in as many words, while its table row still carried the old
    number. The table is the copy that gets read when roles are compared."""

    def test_a_page_and_table_that_disagree_on_FIT_are_caught(self):
        with Vault() as v:
            v.role("Acme", block("5·3·4", 12))
            v.table(["| [[Acme\\|X]] — a role | 5·3·5 | **13** | 2 | 2 |"])
            kinds = {k for _, k, _ in sc.audit()[0]}
            self.assertEqual(kinds, {"agreement"})

    def test_a_page_and_table_that_agree_are_clean(self):
        with Vault() as v:
            v.role("Acme", block("5·3·4", 12))
            v.table(["| [[Acme\\|X]] — a role | 5·3·4 | **12** | 2 | 2 |"])
            self.assertEqual(sc.audit()[0], [])

    def test_columns_are_found_by_NAME_not_by_position(self):
        """🔴 The parser walked columns looking for something number-shaped and
        read SEC as FIT. The header is right there."""
        with Vault() as v:
            v.table(["| [[Acme\\|X]] — a role | 5·3·4 | 🔴 **12** | 🔴 **1** — *\"office\"* | **4** |"])
            self.assertEqual(sc.table_rows()["Acme"], ((5, 3, 4), 12))


class TheReviewQueue(unittest.TestCase):
    """🔴 A script cannot spawn an agent -- which is how role-triage existed for
    the life of the repo and never ran. What it CAN do is make the delegation
    checkable."""

    def high(self, v, name="Acme"):
        v.role(name, block("5·5·4", 14) + "\nhttps://www.linkedin.com/jobs/view/4456075351/\n")
        v.posting(name)

    def test_a_high_score_with_a_posting_and_no_review_is_queued(self):
        with Vault() as v:
            self.high(v)
            self.assertEqual(sc.audit()[1], [("Acme", 14)])

    def test_a_recorded_review_takes_it_off_the_queue(self):
        with Vault() as v:
            self.high(v)
            v.role("Acme", block("5·5·4", 14) + "\nhttps://www.linkedin.com/jobs/view/4456075351/\n"
                   "\n**Review 2026-08-27 — SOUND.** Tested the seniority claim hardest.\n")
            self.assertEqual(sc.audit()[1], [])

    def test_a_review_line_is_not_required_to_be_a_blockquote(self):
        """🔴 In this vault a blockquote means THE EMPLOYER SAID THIS, and
        quotes.py gates on it. A verdict written as one would be checked against
        the posting and fail, correctly."""
        with Vault() as v:
            self.high(v)
            text = open(os.path.join(v.dir, "roles/Acme.md"), encoding="utf-8").read()
            self.assertIsNone(sc.REVIEWED.search("> **Review 2026-08-27 — SOUND.** no.\n"))
            self.assertIsNotNone(sc.REVIEWED.search("**Review 2026-08-27 — SOUND.** yes.\n"))
            del text

    def test_no_archived_posting_means_no_review_is_possible_not_that_one_is_owed(self):
        """A queue full of things nobody can do is a queue nobody starts."""
        with Vault() as v:
            v.role("Acme", block("5·5·4", 14))
            self.assertEqual(sc.audit()[1], [])

    def test_a_low_score_is_not_queued(self):
        """🟡 Deliberate. Reviewing every assessment costs more than the
        decisions it would change."""
        with Vault() as v:
            v.role("Acme", block("2·2·1", 5) + "\nhttps://www.linkedin.com/jobs/view/4456075351/\n")
            v.posting("Acme")
            self.assertEqual(sc.audit()[1], [])


class TheHonestLimit(unittest.TestCase):

    def test_it_says_consistency_is_not_correctness(self):
        """🔴 A role read wrongly and scored consistently passes every check in
        this file. If the output ever stops saying so, the tool starts being
        read as a verdict on the assessment, which it cannot be."""
        flat = " ".join(sc.__doc__.split())
        self.assertIn("no way to check them against the posting", flat)
        self.assertIn("this tool will call it clean", flat)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TheRowsTheCheckCouldNotSee(unittest.TestCase):
    """🔴 A 19% blind spot in a check that reported completeness.

    LINK anchored `[[` directly after the pipe. This vault decorates the first
    cell as readily as the score cells — `| 🟢 [[…`, `| **[[…`, `| ~~[[…` — so
    the parser saw 78 of 96 rows and said "all scores agree with the table"
    about the 78. The 18 it could not see included four submitted applications
    and both internal moves.
    """

    def test_a_status_marker_before_the_link_does_not_hide_the_row(self):
        with Vault() as v:
            v.role("Acme", block("4·4·2", 9))
            v.table(["| 🟢 [[Acme\\|X]] — a role | 4·4·2 | **10** | 3 | 3 |"])
            kinds = {k for _, k, _ in sc.audit()[0]}
            self.assertIn("agreement", kinds, "the decorated row was not seen at all")

    def test_bold_around_the_link_does_not_either(self):
        with Vault() as v:
            v.table(["| **[[Acme\\|X]]** — a role | 5·4·5 | **14** | 2 | 4 |"])
            self.assertEqual(sc.table_rows().get("Acme"), ((5, 4, 5), 14))

    def test_a_struck_row_is_still_parsed_rather_than_skipped(self):
        """🟡 A merged or withdrawn row still holds a score, and silently not
        reading it is what this test exists to stop. Deciding whether to ACT on
        it is a separate question from being able to see it."""
        with Vault() as v:
            v.table(["| ~~[[Acme\\|X]] — a role~~ | ~~4·2·3~~ | ~~**9**~~ | — | — |"])
            self.assertIn("Acme", sc.table_rows())

    def test_a_row_that_is_not_a_role_does_not_become_a_phantom_score(self):
        """🟡 The false-positive direction. A looser regex also matches rows in
        the comparison tables — `| **[[Compensation\\|€17,000 unvested equity]]**
        | Forfeited | Retained |`. It must parse to no score, not a wrong one."""
        with Vault() as v:
            v.table(["| **[[Compensation\\|equity]]** | Forfeited | **Retained** |"])
            self.assertEqual(sc.table_rows().get("Compensation"), (None, None))
            self.assertEqual(sc.audit()[0], [])
