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
    "tools/radar/config.example.json",
    "tools/radar/employers.example.json",
    "tools/radar/radar.py",
    "tools/radar/registry.py",
    "tools/registry_check.py",
    "tools/add_employer.py",
    "tools/verify.py",
    "tools/cv_lint.py",
    "tools/wikilinks.py",
    "tools/known.py",
    "tools/export_review.py",
    "oversight/OVERSIGHT.md",
    ".claude/settings.json",
    ".claude/hooks/verify-artefact.sh",
    "githooks/pre-commit",
]

# Files that must NEVER be tracked. The mirror image, and the reason the ignore
# rule that hid the registry has to stay: employers.json is one user's private
# positions on named companies, and it sits one letter from a file that ships.
MUST_NOT_SHIP = [
    "tools/radar/employers.json",
    "tools/radar/config.json",
    "tools/radar/seen.json",
    "tools/radar/raw.json",
    "tools/radar/shortlist.md",
    "tools/review/config.json",
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


class TheIgnoreRuleThatKeepsCatchingThings(unittest.TestCase):
    """`tools/radar/*.json` is correct and has now hidden two files that had to
    ship. Every carve-out is named individually, on purpose."""

    def test_each_shipped_json_under_radar_has_an_explicit_carve_out(self):
        gitignore = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
        for f in [f for f in REQUIRED if f.startswith("tools/radar/") and f.endswith(".json")]:
            self.assertIn(f"!{f}", gitignore,
                          f"{f} ships but has no `!` line -- it will be silently dropped")

    def test_the_pre_commit_hook_carves_out_the_same_files(self):
        hook = open(os.path.join(ROOT, "githooks", "pre-commit"), encoding="utf-8").read()
        for f in [f for f in REQUIRED if f.startswith("tools/radar/") and f.endswith(".json")]:
            self.assertIn(os.path.basename(f), hook,
                          f"{f} is carved out of .gitignore but the hook will still block it")


class TheRegistryIsUsable(unittest.TestCase):
    def test_it_parses_and_is_not_empty(self):
        p = os.path.join(ROOT, "tools", "radar", "ats_registry.json")
        d = json.load(open(p, encoding="utf-8"))
        self.assertGreater(len(d["employers"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
