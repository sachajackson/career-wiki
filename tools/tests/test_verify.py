"""verify: the deterministic layer, which is the one check that is not a model.

Two of these guard failures that were found in real use and fixed: figures
were being sourced from the CV being checked (a fabrication that "existed in
the wiki" because it existed in the document), and employer attribution was
being inferred from nearby prose, which passed everything.
"""
import importlib.util, os, subprocess, sys, tempfile, textwrap, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFY = os.path.join(ROOT, "tools", "verify.py")

spec = importlib.util.spec_from_file_location("verify", VERIFY)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def page(employer=None, verified=True, stale=None, body="", type_="achievement", title="P"):
    fm = [f"type: {type_}", f"title: {title}"]
    if employer:
        fm.append(f"employer: {employer}")
    if stale:
        fm.append(f"stale_after: {stale}")
    if verified:
        fm.append('verified:\n  - { by: "human:test", at: 2026-01-01T00:00:00Z }')
    return "---\n" + "\n".join(fm) + "\n---\n\n" + body + "\n"


class Wiki:
    """A throwaway wiki on disk. Built in code so there are no fixture files to rot."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        self.wiki = os.path.join(self.dir, "wiki")
        os.makedirs(self.wiki)
        return self

    def add(self, name, text):
        path = os.path.join(self.wiki, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def run(self, doc, *args):
        d = os.path.join(self.dir, "doc.txt")
        with open(d, "w", encoding="utf-8") as fh:
            fh.write(doc)
        p = subprocess.run([sys.executable, VERIFY, d, "--wiki", self.wiki, *args],
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def __exit__(self, *a):
        import shutil; shutil.rmtree(self.dir, ignore_errors=True)


class Normalisation(unittest.TestCase):
    """50,000 and 50k and 50000 are the same claim and must compare equal."""

    def test_thousands_separator(self):
        self.assertEqual(verify.norm("50,000"), verify.norm("50000"))

    def test_k_suffix(self):
        self.assertEqual(verify.norm("50k"), verify.norm("50000"))

    def test_currency_is_stripped(self):
        self.assertEqual(verify.norm("€94,000"), verify.norm("94000"))

    def test_a_percentage_and_a_count_are_not_the_same_claim(self):
        """'100% of fixes within SLA' and 'over 100 staff' used to collide,
        producing a confident ATTRIBUTION finding against a correct document."""
        self.assertNotEqual(verify.norm("100%"), verify.norm("100"))

    def test_a_multiplier_and_a_count_are_not_the_same_claim(self):
        self.assertNotEqual(verify.norm("3x"), verify.norm("3"))

    def test_the_same_percentage_written_differently_still_matches(self):
        self.assertEqual(verify.norm("63%"), verify.norm("63 %"))


class WhatCountsAsAFigure(unittest.TestCase):
    def test_small_bare_integers_are_ignored(self):
        """'3 teams' is not a provenance risk and flagging it would drown the signal."""
        self.assertEqual(verify.NUM.findall("led 3 teams across 2 sites"), [])

    def test_percentages_money_and_large_counts_are_caught(self):
        for s in ("37%", "€94,000", "1,200", "50000", "3x", "50-70"):
            self.assertTrue(verify.NUM.search(s), s)


class Frontmatter(unittest.TestCase):
    def test_reads_employer_and_verified(self):
        fm, _ = verify.parse_frontmatter(page(employer="Acme Corp"))
        self.assertEqual(fm["employer"], "Acme Corp")
        self.assertTrue(fm["verified"])

    def test_no_frontmatter_is_not_a_wiki_page(self):
        fm, _ = verify.parse_frontmatter("# Just a heading\n")
        self.assertEqual(fm, {})

    def test_exclude_from_cv(self):
        fm, _ = verify.parse_frontmatter(
            "---\ntype: achievement\nexclude_from_cv: true\n---\n\nbody\n")
        self.assertTrue(fm["exclude"])


class Provenance(unittest.TestCase):
    def test_a_figure_absent_from_the_wiki_is_unsourced(self):
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", body="Cut planning from 11 days to 4."))
            code, out = w.run("Cut cost by 63% at Acme Corp.\nme@example.com\n")
            self.assertIn("UNSOURCED", out)
            self.assertEqual(code, 1)

    def test_a_sourced_figure_passes(self):
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", body="Cut cost by 63% over two quarters."))
            code, out = w.run("Cut cost by 63%.\nme@example.com\n")
            self.assertNotIn("UNSOURCED", out)
            self.assertEqual(code, 0, out)

    def test_years_are_not_treated_as_figures(self):
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", body="Joined in 2015."))
            _, out = w.run("Head of Delivery, 2019 to 2024.\nme@example.com\n")
            self.assertNotIn("UNSOURCED", out)


class CircularSourcing(unittest.TestCase):
    """The check exists to catch fabricated figures. If the document being
    checked is itself indexed as a source, a fabrication proves itself."""

    def test_an_application_folder_under_the_wiki_is_not_a_source(self):
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", body="Cut planning from 11 days to 4."))
            w.add("applications/Acme R1/cv.md",
                  page(employer="Acme Corp", body="Cut cost by 63%."))
            _, out = w.run("Cut cost by 63% at Acme Corp.\nme@example.com\n")
            self.assertIn("UNSOURCED", out)


class Attribution(unittest.TestCase):
    def test_a_figure_under_the_wrong_employer_is_caught(self):
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", body="Ran 50,000 executions a month."))
            doc = ("Head of Delivery, Beta Ltd\nRan 50,000 executions a month.\n"
                   "Engineer, Acme Corp\nOther work.\nme@example.com\n")
            _, out = w.run(doc, "--employers", "Acme Corp,Beta Ltd")
            self.assertIn("ATTRIBUTION", out)

    def test_the_right_employer_passes(self):
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", body="Ran 50,000 executions a month."))
            doc = ("Engineer, Acme Corp\nRan 50,000 executions a month.\nme@example.com\n")
            _, out = w.run(doc, "--employers", "Acme Corp,Beta Ltd")
            self.assertNotIn("ATTRIBUTION", out)

    def test_it_says_so_loudly_when_it_cannot_run(self):
        """Silence would read as a pass. This is the check that catches a real
        achievement attached to the wrong job."""
        with Wiki() as w:
            w.add("A.md", page(employer=None, body="Ran 50,000 executions a month."))
            _, out = w.run("Ran 50,000 executions a month.\nme@example.com\n",
                           "--employers", "Acme Corp")
            self.assertIn("[SKIPPED] attribution", out)


class PerApplicationRules(unittest.TestCase):
    def test_a_banned_term_is_caught(self):
        with Wiki() as w:
            w.add("A.md", page(body="Nothing numeric here."))
            _, out = w.run("Strong React experience.\nme@example.com\n", "--ban", "react")
            self.assertIn("BANNED", out)

    def test_uk_spelling_convention(self):
        with Wiki() as w:
            w.add("A.md", page(body="Nothing numeric."))
            _, out = w.run("Ran the program.\nme@example.com\n", "--spelling", "uk")
            self.assertIn("SPELLING", out)

    def test_the_employer_must_be_named_in_the_document(self):
        with Wiki() as w:
            w.add("A.md", page(body="Nothing numeric."))
            _, out = w.run("Dear hiring manager.\nme@example.com\n", "--employer", "Acme Corp")
            self.assertIn("EMPLOYER", out)

    def test_missing_email_is_caught(self):
        with Wiki() as w:
            w.add("A.md", page(body="Nothing numeric."))
            _, out = w.run("A document with no way to reply to it.\n")
            self.assertIn("CONTACT", out)


class Staleness(unittest.TestCase):
    def test_an_expired_page_flags_its_figures(self):
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", stale="2020-01-01",
                               body="Ran 50,000 executions a month."))
            _, out = w.run("Ran 50,000 executions a month.\nme@example.com\n")
            self.assertIn("STALE", out)


class MachineReadable(unittest.TestCase):
    def test_json_output_is_parseable(self):
        import json
        with Wiki() as w:
            w.add("A.md", page(employer="Acme Corp", body="Cut cost by 63%."))
            _, out = w.run("Cut cost by 63%.\nme@example.com\n", "--json")
            data = json.loads(out)
            self.assertIn("findings", data)
            self.assertTrue(data["clean"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
