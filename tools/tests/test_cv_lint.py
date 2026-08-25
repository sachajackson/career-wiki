"""cv_lint: does the mechanical layer actually catch what it claims to?

Three of these encode bugs that were live in the shipped version:
empty input reported "clean", bullets with no words crashed, and one word
could produce two identical findings.
"""
import subprocess, sys, os, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LINT = os.path.join(ROOT, "tools", "cv_lint.py")


def run(text):
    p = subprocess.run([sys.executable, LINT, "-"], input=text,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# Invented, and it has to stay realistic: this fixture exists to prove a
# well-written document passes, and the cadence and opening-word checks only
# mean something against prose that reads like prose. What it must NOT be is
# anyone's actual history -- no employer, no dates, no place, and figures that
# appear nowhere else in this repo.
CLEAN = ("Rebuilt the deployment pipeline, taking a fortnightly cycle to three days.\n"
         "- Ran a group of five across two offices and one time zone difference.\n"
         "- Brought the open defect count down by a third over two quarters, then held it.\n"
         "- Ran the migration.\n"
         "- Took the on-call rota from a single name to a rota of five, which ended "
         "the single point of failure nobody wanted to name.\n"
         "me@example.com\n")


class CleanInput(unittest.TestCase):
    def test_a_clean_document_passes(self):
        code, out = run(CLEAN)
        self.assertEqual(code, 0, out)
        self.assertIn("clean on the mechanical checks", out)


class RefusesToPassOnNothing(unittest.TestCase):
    """A checker that reports clean when it checked nothing is worse than none."""

    def test_empty_input_is_an_error_not_a_pass(self):
        code, out = run("")
        self.assertEqual(code, 1)
        self.assertIn("empty", out.lower())
        self.assertNotIn("clean on the mechanical checks", out)

    def test_whitespace_only_is_also_an_error(self):
        code, out = run("   \n\n\t\n")
        self.assertEqual(code, 1)
        self.assertIn("empty", out.lower())


class Characters(unittest.TestCase):
    def test_em_dash(self):
        self.assertIn("em dash", run("Ran delivery — across two teams.\n")[1])

    def test_curly_quotes(self):
        self.assertIn("curly quote", run("The “platform” team.\n")[1])

    def test_non_breaking_space(self):
        self.assertIn("non-breaking space", run("Ran delivery.\n")[1])

    def test_currency_symbols_are_allowed(self):
        self.assertNotIn("non-ascii", run("Budget of €12,400 and £9,100.\n")[1])

    def test_accented_letters_in_names_are_allowed(self):
        self.assertNotIn("non-ascii", run("Worked with Siobhán on the migration.\n")[1])


class Vocabulary(unittest.TestCase):
    def test_banned_word(self):
        self.assertIn("banned word", run("Spearheaded the migration.\n")[1])

    def test_hedge(self):
        self.assertIn("hedge", run("Was involved in the migration.\n")[1])

    def test_participial_tail(self):
        self.assertIn("participial tail", run("Ran it, resulting in faster delivery.\n")[1])

    def test_not_just_x_but_y(self):
        self.assertIn("banned shape", run("Not just a rebuild but a rethink.\n")[1])


class Numbers(unittest.TestCase):
    def test_round_percentage_is_flagged(self):
        self.assertIn("round-number tell", run("Cut cost by 40%.\n")[1])

    def test_an_odd_percentage_is_not(self):
        self.assertNotIn("round-number tell", run("Cut cost by 37%.\n")[1])


class Spelling(unittest.TestCase):
    def test_us_spelling_flagged(self):
        self.assertIn("US spelling", run("Optimize the pipeline.\n")[1])

    def test_short_ize_words_are_not_false_positives(self):
        out = run("The size of the prize.\n")[1]
        self.assertNotIn("US spelling", out)

    def test_one_word_produces_one_finding(self):
        """Two patterns matched 'organization' and both reported it."""
        out = run("The organization grew.\n")[1]
        self.assertEqual(out.count("US spelling"), 1, out)


class Cadence(unittest.TestCase):
    def test_uniform_bullet_length_is_flagged(self):
        same = "- Delivered the programme on time and to the agreed budget again\n" * 5
        self.assertIn("UNIFORM CADENCE", run(same)[1])

    def test_uniform_openings_flagged(self):
        text = ("- Managed the release process end to end for the platform\n"
                "- Managed a team of nine\n"
                "- Managed the vendor relationship through two renewals and a change of account team\n"
                "- Managed the migration\n")
        self.assertIn("uniform openings", run(text)[1])

    def test_bullets_with_no_words_do_not_crash(self):
        """This raised IndexError on Counter.most_common of an empty counter."""
        code, out = run("-\n-\n-\n-\n")
        self.assertNotIn("Traceback", out)
        self.assertIn(code, (0, 1))


class ExitStatus(unittest.TestCase):
    def test_findings_exit_one_so_it_can_gate_a_build(self):
        self.assertEqual(run("Spearheaded it.\n")[0], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
