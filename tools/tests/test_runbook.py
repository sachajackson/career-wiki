"""runbook: the ordered steps of every sequence, and whether they are reachable.

🔴 Prose has no order. `role-radar/SKILL.md` is 323 lines across eighteen
sections; its only sequence was a five-item list two thirds of the way down, and
the `role-triage` delegation named twice in that same file went unused for the
life of the repo.

🔴 A runbook is still READ, so it is a guide and not a sensor. What makes the
difference is the precondition tools enforce on themselves — tested in
test_batch.py — and these checks, which keep the runbooks reachable and honest.
"""
import importlib.util, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("runbook", os.path.join(ROOT, "tools", "runbook.py"))
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)
SKILLS = os.path.join(ROOT, ".claude", "skills")


class TheRunbooks(unittest.TestCase):

    def test_every_step_carries_a_command_and_a_consequence(self):
        """A step without a consequence is a preference; one without a command
        is a wish. Neither survives contact with a long session."""
        for name, (title, steps) in rb.BOOKS.items():
            for step, cmd, why in steps:
                self.assertTrue(step.strip() and cmd.strip() and why.strip(),
                                f"{name}: incomplete step {step!r}")

    def test_each_renders_numbered_from_zero(self):
        for name in rb.BOOKS:
            text = rb.render(name)
            self.assertIn("  0  ", text, name)
            self.assertIn(", in order", text)

    def test_the_steps_that_were_actually_skipped_are_present(self):
        """Each of these was skipped for real, once, at a cost."""
        radar = rb.render("radar")
        for must in ("role-triage", "raw.json", "posting URL", "log.md"):
            self.assertIn(must, radar, f"radar runbook omits {must}")
        app = rb.render("application")
        self.assertIn("cv_docx", app)          # .docx is the portal default
        self.assertIn("Submitted YYYY-MM-DD", app)   # a date, or it can never be aged
        self.assertIn("no response", rb.render("outcome"))
        self.assertIn("settings_drift", rb.render("update"))


class TheSkillsPointAtThem(unittest.TestCase):
    """🔴 A runbook nobody reaches is prose with extra steps. Every skill that
    HAS a sequence must name the runbook in its opening lines, before the
    caveats — because the caveats are where the last one got lost."""

    ORDERED = ("role-radar", "build-application", "pre-submit", "career-init", "career-migrate")

    def test_a_skill_with_a_sequence_names_the_runbook_early(self):
        for name in self.ORDERED:
            path = os.path.join(SKILLS, name, "SKILL.md")
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as fh:
                head = "".join(fh.readlines()[:30])
            self.assertIn("runbook", head.lower(),
                          f"{name}/SKILL.md does not name a runbook in its first 30 lines")


if __name__ == "__main__":
    unittest.main(verbosity=2)
