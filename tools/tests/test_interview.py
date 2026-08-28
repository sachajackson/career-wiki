"""interview: the skill everything else is downstream of, and nothing checked it.

🔴 It calls itself "the most valuable thing in the repo" and had **zero tests and
zero log entries**. Writing the first one found its opening instruction broken:

    python3 tools/known.py "<the thing>" --wiki wiki   ->  known: no wiki at wiki

**That command is the duplicate-question guard.** It is the first thing the skill
tells you to run, before the first question and before any question you are
unsure about, because "a question the user has already answered tells them the
system does not retain what they say, which is the one thing it exists to do".

🔴 It had been returning nothing since `wiki/` moved to `vault/wiki/`, and the
same literal was in FOUR skills and `SCHEMA.md` — the identical fault found in
`verify-artefact.sh` the same day. Every one of those tools defaults its wiki
argument to `paths.WIKI`; every one of those commands overrode a correct default
with a path that had moved.

🟡 A skill is prose read by an agent, so none of this asserts behaviour. What it
asserts is that **the commands the skill tells a reader to run actually run**,
and that the rules other skills depend on are still in it.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL = os.path.join(ROOT, ".claude", "skills", "interview", "SKILL.md")


def body():
    with open(SKILL, encoding="utf-8") as fh:
        return fh.read()


def commands(text):
    """Every `python3 tools/...` line inside a fenced block."""
    out = []
    for block in re.findall(r"```(?:bash|sh)?\n(.*?)```", text, re.S):
        out += [l.strip() for l in block.split("\n") if l.strip().startswith("python3 tools/")]
    return out


class TheCommandsItTellsYouToRun(unittest.TestCase):

    def test_it_shows_at_least_one(self):
        self.assertTrue(commands(body()), "the skill shows no runnable command at all")

    def test_every_tool_it_names_exists(self):
        for cmd in commands(body()):
            tool = re.search(r"(tools/[\w/]+\.py)", cmd).group(1)
            self.assertTrue(os.path.exists(os.path.join(ROOT, tool)), f"{tool} does not exist")

    def test_no_command_names_a_folder_that_moved(self):
        """🔴 THE BUG. `--wiki wiki` when the wiki is `vault/wiki`. The tools all
        default correctly; the documented command overrode the default."""
        for cmd in commands(body()):
            self.assertNotIn("--wiki wiki", cmd)
            self.assertFalse(re.search(r"\.py\s+wiki\b", cmd), cmd)

    def test_the_duplicate_question_guard_actually_answers(self):
        """🔴 Runs it. It returned `no wiki at wiki` for as long as the literal
        was there — so the guard was documented, instructed in bold, and dead.

        🟡 Against a vault built here, never the user's. The first version ran it
        in the repo root and `test_boundary` failed it for exactly that: a suite
        that reads the author's vault passes for the author and nobody else.
        """
        cmd = next((c for c in commands(body()) if "known.py" in c), None)
        self.assertIsNotNone(cmd, "the skill no longer names the duplicate-question guard")
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        os.makedirs(os.path.join(tmp, "wiki"))
        with open(os.path.join(tmp, "wiki", "Scope.md"), "w", encoding="utf-8") as fh:
            fh.write("---\ntype: topic\nverified: 2026-08-01\n---\n\n"
                     "# Scope\n\n**RESOLVED 2026-08-01: he holds no widget budget.**\n")
        runnable = cmd.replace('"<the thing>"', '"widget budget"')
        r = subprocess.run(runnable, shell=True, cwd=ROOT, timeout=60,
                           capture_output=True, text=True,
                           env=dict(os.environ, CAREER_VAULT=tmp))
        self.assertNotIn("no wiki at", r.stdout + r.stderr,
                         "the guard is pointed at a folder that does not exist")
        self.assertIn("known:", r.stdout, "the guard produced no verdict")


class TheRulesOtherThingsDependOn(unittest.TestCase):
    """Each of these is referenced elsewhere in the system, so removing it from
    here breaks something that is not here."""

    def test_it_still_says_to_check_before_asking(self):
        self.assertIn("known.py", body())
        self.assertRegex(body(), r"SETTLED|PRESENT")

    def test_it_still_files_before_the_next_round(self):
        """`career-init` step 3 says "file the answers before moving on. Do not
        stack rounds", and points here for the rounds themselves."""
        self.assertRegex(body(), r"After each round")
        self.assertIn("log.md", body())

    def test_the_standing_backlog_section_is_named_exactly(self):
        """🔴 `Operating Model.md` carries an `## Interview backlog` heading and
        this skill is what writes it. A rename here orphans it silently."""
        self.assertIn("## Interview backlog", body())
        self.assertIn("Operating Model.md", body())

    def test_rounds_are_bounded(self):
        """Not one at a time — that is an interrogation. Not twenty — a form."""
        self.assertRegex(body(), r"six to eight")


class ItShipsLikeTheOthers(unittest.TestCase):

    def test_it_has_frontmatter_with_a_name_and_a_description(self):
        head = re.match(r"^---\n(.*?)\n---", body(), re.S)
        self.assertIsNotNone(head, "no frontmatter")
        self.assertRegex(head.group(1), r"(?m)^name:\s*interview\s*$")
        self.assertRegex(head.group(1), r"description:\s*\S")

    def test_it_is_tracked(self):
        out = subprocess.run(["git", "-C", ROOT, "ls-files", ".claude/skills/interview/SKILL.md"],
                             capture_output=True, text=True).stdout
        self.assertIn("SKILL.md", out, "the skill is not tracked, so a clone does not get it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
