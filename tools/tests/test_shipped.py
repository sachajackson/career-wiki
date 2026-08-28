"""Does a clone actually contain what the tools need?

THE FAILURE THIS EXISTS FOR

Twice in two days a file was written, used, tested and pushed -- and was never
in the repository. Both times an ignore rule matched it, `git add -A` skipped it
without a word, and the working tree looked perfect. The tools worked for the
person who wrote them and were broken for everyone else.

WHY THE EXISTING CHECKS ALL MISSED IT

  - The test suite reads the working tree, where the file exists.
  - `git status --porcelain` was clean: the file was not unexpectedly staged,
    it was expectedly absent, and those look identical.
  - CONTRIBUTING already said to check status before pushing. That instruction
    was followed and the bug went through it, because it asks whether anything
    UNEXPECTED is there, never whether something EXPECTED is missing.

So the only check that catches this is one that asks git what a clone would get,
rather than asking the filesystem what this machine has.
"""
import json, os, re, subprocess, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def tracked():
    """Split on newlines, not whitespace: this repo has filenames with spaces in
    them and .split() turned `templates/Role Scoring Framework.md` into three."""
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, text=True).stdout
    return {p for p in out.split("\0") if p}


# Files the tools open by name. If one of these is not tracked, a clone is broken
# in a way no test reading the working tree can see.
REQUIRED = [
    "tools/radar/ats_registry.json",
    "tools/lib/paths.py",
    "templates/settings/review.example.json",
    "AGENTS.md",
    "SCHEMA.md",
    "templates/settings/search.example.json",
    "templates/settings/employers.example.json",
    "tools/radar/radar.py",
    "tools/radar/registry.py",
    "tools/registry_check.py",
    "tools/add_employer.py",
    "tools/verify.py",
    "tools/cv_lint.py",
    "tools/wikilinks.py",
    "tools/known.py",
    "tools/export_review.py",
    "templates/OVERSIGHT.md",
    ".claude/settings.json",
    ".claude/hooks/verify-artefact.sh",
    "githooks/pre-commit",
    "githooks/pre-push",
]

# Files that must NEVER be tracked. The mirror image, and the reason the ignore
# rule that hid the registry has to stay: employers.json is one user's private
# positions on named companies, and it sits one letter from a file that ships.
MUST_NOT_SHIP = [
    "vault/settings/employers.json",
    "vault/settings/search.json",
    "vault/state/seen.json",
    "vault/state/raw.json",
    "vault/state/shortlist.md",
    "vault/settings/review.json",
]


class WhatACloneGets(unittest.TestCase):
    def test_every_file_the_tools_need_is_tracked(self):
        t = tracked()
        missing = [f for f in REQUIRED if f not in t]
        self.assertEqual(missing, [], f"a clone would not contain: {missing}")

    def test_nothing_private_is_tracked(self):
        t = tracked()
        leaked = [f for f in MUST_NOT_SHIP if f in t]
        self.assertEqual(leaked, [], f"these must never ship: {leaked}")

    def test_every_adapter_is_tracked(self):
        """A module in ADAPTERS but not in the repo breaks the import on a clone."""
        t = tracked()
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
        from adapters import ADAPTERS
        for name in ADAPTERS:
            self.assertIn(f"tools/radar/adapters/{name}.py", t, f"{name} adapter is not tracked")

    def test_every_test_file_is_tracked(self):
        """An untracked test is a check that only ever runs for its author."""
        t = tracked()
        here = os.path.dirname(os.path.abspath(__file__))
        for f in os.listdir(here):
            if f.startswith("test_") and f.endswith(".py"):
                self.assertIn(f"tools/tests/{f}", t, f"{f} is not tracked")


# The two tests that lived here asserted every shipped .json under tools/radar
# had a carve-out in .gitignore and another in the pre-commit hook. They were
# correct, and they were guarding a list that had to be maintained by hand --
# which had already failed twice. The boundary replaced the list, so the tests
# were replaced by the property they were approximating. See test_boundary.py.


class TheRegistryIsUsable(unittest.TestCase):
    def test_it_parses_and_is_not_empty(self):
        p = os.path.join(ROOT, "tools", "radar", "ats_registry.json")
        d = json.load(open(p, encoding="utf-8"))
        self.assertGreater(len(d["employers"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TheTwoWaysIn(unittest.TestCase):
    """A migrating user running /career-init gets templates written over pages
    they already have and an hour of questions they have already answered.
    Nothing said so until 2026-08-25, and career-init's own check was whether
    sources/ had a CV -- which a migrating vault also does."""

    def test_both_entry_points_exist(self):
        for skill in ("career-init", "career-migrate"):
            self.assertIn(f".claude/skills/{skill}/SKILL.md", tracked())

    def test_init_sends_a_populated_vault_to_migrate(self):
        p = os.path.join(ROOT, ".claude", "skills", "career-init", "SKILL.md")
        with open(p, encoding="utf-8") as fh:
            head = fh.read(2500)
        self.assertIn("/career-migrate", head,
                      "career-init must turn away a vault that already has pages")

    def test_migrate_does_not_send_them_back(self):
        """The loop that would make both useless."""
        p = os.path.join(ROOT, ".claude", "skills", "career-migrate", "SKILL.md")
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("Do not run `/career-init`", text)


class TheDocsAreAMapNotAPile(unittest.TestCase):
    """README was 1034 lines with eight top-level sections, and the scoring one
    described a model that had been replaced. Length is how a document rots:
    nobody re-reads the middle of it."""

    # docs/ holds the guides a person reads. The root keeps only what a
    # convention or a tool looks for there: README and LICENSE (GitHub),
    # AGENTS.md and CLAUDE.md (agent entry points), SCHEMA.md as AGENTS' one
    # companion, CONTRIBUTING.md (GitHub links it from the PR form), PRIVACY.md
    # because it is the one document a user must not have to hunt for, and
    # BACKLOG.md because it is a working record rather than documentation.
    GUIDES = ("docs/FOR-RECRUITERS", "docs/CHECKING", "docs/INSTALL",
              "docs/JOB-SEARCH", "docs/SCORING", "docs/DISCLAIMER", "docs/LESSONS")
    ROOTED = ("PRIVACY", "CONTRIBUTING", "BACKLOG", "SCHEMA", "AGENTS")
    PAGES = GUIDES + ROOTED

    def readme(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            return fh.read()

    def test_every_page_is_reachable_from_the_readme(self):
        """A split-out page nobody links to is worse than a long README: the
        content is still there and now nobody finds it."""
        text = self.readme()
        for page in self.PAGES:
            self.assertIn(f"({page}.md)", text, f"{page}.md is orphaned")

    def test_every_guide_points_back(self):
        for page in self.GUIDES:
            with open(os.path.join(ROOT, f"{page}.md"), encoding="utf-8") as fh:
                self.assertIn("README.md", fh.read(2000), f"{page}.md has no way back")

    def test_the_root_holds_only_what_something_looks_for_there(self):
        """Fourteen markdown files at the root is a pile. The ones that stay are
        the ones a convention or a tool expects at the top level -- move any of
        them and something silently stops finding it."""
        import glob
        at_root = {os.path.basename(p)[:-3] for p in glob.glob(os.path.join(ROOT, "*.md"))}
        self.assertEqual(at_root, {"README", "CLAUDE"} | set(self.ROOTED),
                         "a guide belongs in docs/, or the reason it does not belongs in this test")

    def test_the_readme_stays_short_enough_to_be_read(self):
        n = len(self.readme().splitlines())
        self.assertLess(n, 400, f"README is {n} lines — split something out")

    def test_no_document_describes_the_replaced_scoring_model(self):
        """FIT/LIFE/SEC/REQS replaced a single score out of 20 on 2026-08-25,
        and README described the old one for weeks afterwards."""
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "vault", "tests")]
            for f in files:
                # 🟢 BACKLOG.md was exempt here too, for the same expired
                # reason. It is future work now, and future work has no
                # business describing a scoring model replaced in August.
                if not f.endswith(".md"):
                    continue
                path = os.path.join(base, f)
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                rel = os.path.relpath(path, ROOT)
                for line in text.splitlines():
                    if re.search(r"\bWANT\b", line):
                        self.fail(f"{rel}: WANT was replaced by LIFE and SEC — {line.strip()[:70]}")
