"""cv_lint: does the mechanical layer actually catch what it claims to?

Three of these encode bugs that were live in the shipped version:
empty input reported "clean", bullets with no words crashed, and one word
could produce two identical findings.
"""
import importlib.util, json, re, shutil, subprocess, sys, os, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LINT = os.path.join(ROOT, "tools", "cv_lint.py")

_spec = importlib.util.spec_from_file_location("cv_lint", LINT)
cv_lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cv_lint)


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
    """🔴 Spelling is a LOCALE, and a locale belongs to the user.

    These patterns ran unconditionally until 2026-08-26, so a US candidate
    writing a correct US resume got a finding for every "optimize" and "center"
    and a non-zero exit, with no flag to turn it off."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.p = os.path.join(self.tmp, "profile.json")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rules(self, cfg):
        if cfg is not None:
            with open(self.p, "w") as fh:
                json.dump(cfg, fh)
        return cv_lint.spelling_rules(self.p)

    def test_no_profile_enforces_nothing(self):
        """🔴 THE ONE THAT MATTERS. Absent means off, never means one market."""
        pats, locale = cv_lint.spelling_rules(os.path.join(self.tmp, "absent.json"))
        self.assertEqual(pats, [])
        self.assertIsNone(locale)

    def test_an_unknown_locale_enforces_nothing(self):
        pats, locale = self.rules({"spelling": "klingon"})
        self.assertEqual(pats, [])
        self.assertIsNone(locale)

    def test_the_two_locales_are_mirror_images(self):
        """A US resume must not be corrected toward British spelling, and the
        reverse. Each locale flags the OTHER one's forms."""
        ie, _ = self.rules({"spelling": "ie-uk"})
        us, _ = self.rules({"spelling": "us"})
        self.assertTrue(any(re.search(r, "we optimize the center") for r in ie))
        self.assertFalse(any(re.search(r, "we optimise the centre") for r in ie))
        self.assertTrue(any(re.search(r, "we optimise the centre") for r in us))
        self.assertFalse(any(re.search(r, "we optimize the center") for r in us))

    def test_short_words_are_not_false_positives(self):
        """🔴 'size', 'wise' and 'rise' end in -ise and are not British spelling."""
        us, _ = self.rules({"spelling": "us"})
        out = run("The size of the prize. Rise and advise wisely.\n")[1]
        self.assertNotIn("spelling", out)


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


class ThirdPerson(unittest.TestCase):
    """Six CVs carried these and five went to employers before anybody looked."""

    def test_he_is_flagged(self):
        out = run("The estate is still in production, inside the function he now leads.\n")[1]
        self.assertIn("THIRD PERSON", out)

    def test_his_is_flagged(self):
        self.assertIn("THIRD PERSON", run("Six of his fifteen work on AI.\n")[1])

    def test_him_is_flagged(self):
        out = run("Delivers through functions that do not report to him.\n")[1]
        self.assertIn("THIRD PERSON", out)

    def test_she_and_her_are_flagged(self):
        self.assertIn("THIRD PERSON", run("The lifecycle she designed.\n")[1])
        self.assertIn("THIRD PERSON", run("Grew her function from 5 to 20.\n")[1])

    def test_they_them_their_are_NOT_flagged(self):
        """The false-positive case, and the reason the check is singular-only.

        In a CV these point at an employer, a client or a team, not at the
        subject. A check that fires here fires on nearly every real document,
        and that is how a good check gets switched off."""
        text = ("The product owner sits inside the client, and works with them, their\n"
                "operations teams and their management on intake, priority and release.\n")
        self.assertNotIn("THIRD PERSON", run(text)[1])

    def test_the_and_other_embedded_matches_are_not_flagged(self):
        """'there', 'the', 'usher', 'this', 'other' each contain a pronoun as a
        substring -- her, he, she, his, her. Word boundaries must hold."""
        text = "There the usher moved this other file across the shared platform.\n"
        out = run(text)[1]
        self.assertEqual(out.count("THIRD PERSON"), 0, out)

    def test_a_clean_cv_stays_clean(self):
        """Every cover letter in the vault scored zero. So must this."""
        self.assertNotIn("THIRD PERSON", run(CLEAN)[1])


class ExitStatus(unittest.TestCase):
    def test_findings_exit_one_so_it_can_gate_a_build(self):
        self.assertEqual(run("Spearheaded it.\n")[0], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
