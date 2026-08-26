#!/usr/bin/env python3
"""The /market-standards skill, and the gates that read its output.

Four things are tested and each one has already gone wrong somewhere in this
repository, which is why they are checks and not prose in the skill.
"""
import glob, os, re, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "lib"))
import paths  # noqa: E402

SKILL = os.path.join(ROOT, ".claude", "skills", "market-standards", "SKILL.md")
GATED = ("build-application", "profile-refresh", "pre-submit")


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


class TheSkillShips(unittest.TestCase):
    def test_it_exists_and_declares_itself(self):
        t = read(SKILL)
        self.assertIn("name: market-standards", t)
        self.assertIn("description:", t)


class TheKnownFalseClaimsSurvive(unittest.TestCase):
    """Each of these costs a research run to rediscover, and a tidy-up edit
    would drop them silently. The point of the list is that it persists."""

    CLAIMS = [
        ("75%", "Preptel"),            # the auto-rejection figure and its dead source
        ("5×", "ranking factors"),     # LinkedIn headline weighting
        ("Posting weekly", "search"),  # feed reach conflated with search ranking
        ("7.4-second", "30 recruiters"),
    ]

    def test_every_debunked_claim_is_still_named_with_its_reason(self):
        t = read(SKILL)
        for claim, reason in self.CLAIMS:
            self.assertIn(claim, t, f"{claim!r} was dropped from the skill")
            self.assertIn(reason, t, f"{claim!r} is named but its reason {reason!r} is gone")

    def test_the_privacy_rule_survives(self):
        """The natural way to write a personalised query is to personalise it
        with personal data. That instruction must not be edited away."""
        t = read(SKILL)
        self.assertRegex(t, r"[Nn]ever.{0,60}search quer|Never put the user into a search query")
        self.assertIn("Research the category", t)


class TheGateDoesNotBlock(unittest.TestCase):
    """🔴 The one that matters. A skill that refuses to work until research has
    run is a skill people route around, so the gate must offer, state its
    fallback assumption, and continue."""

    def skills(self):
        for name in GATED:
            yield name, read(os.path.join(ROOT, ".claude", "skills", name, "SKILL.md"))

    def test_every_gated_skill_mentions_the_research_skill(self):
        for name, t in self.skills():
            self.assertIn("market-standards", t, f"{name} has no gate")

    def test_no_gate_hard_blocks(self):
        for name, t in self.skills():
            self.assertRegex(t, r"PROCEED|[Pp]roceed",
                             f"{name} does not say to proceed when the user declines")
            self.assertRegex(t, r"[Nn]ever hard-block|do not hard-block",
                             f"{name} does not forbid hard-blocking")

    def test_every_gate_states_a_fallback_assumption(self):
        """Declining must produce a named assumption, not silence."""
        for name, t in self.skills():
            self.assertRegex(t, r"assumption", f"{name} does not name a fallback assumption")


class ThePagesIfPresentAreWellFormed(unittest.TestCase):
    """The pages live in a vault that is not committed, so this asserts nothing
    when they are absent and everything when they are there."""

    NAMES = ("CV Layout and ATS Standards", "Cover Letter Standards",
             "LinkedIn Profile Standards")

    def found(self):
        wiki = os.path.join(paths.VAULT, "wiki")
        if not os.path.isdir(wiki):
            return []
        out = [p for p in glob.glob(os.path.join(wiki, "*Standards*.md"))]
        return out

    def test_each_page_carries_frontmatter_and_a_staleness_date(self):
        for p in self.found():
            t = read(p)
            self.assertTrue(t.startswith("---"), f"{os.path.basename(p)}: no frontmatter")
            self.assertIn("type: synthesis", t, os.path.basename(p))
            self.assertIn("section: career", t, os.path.basename(p))
            self.assertRegex(t, r"stale_after:\s*\d{4}-\d{2}-\d{2}",
                             f"{os.path.basename(p)}: no stale_after — it would never expire")

    def test_each_page_hedges_its_confidence(self):
        """Evidence quality differs enormously across the four topics. A page
        that sounds equally certain about all of them is lying about one."""
        for p in self.found():
            t = read(p).lower()
            self.assertRegex(t, r"confidence|could be wrong",
                             f"{os.path.basename(p)}: no confidence marking")


if __name__ == "__main__":
    unittest.main(verbosity=2)
